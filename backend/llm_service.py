import os
import json
import hashlib
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

# We expect GEMINI_API_KEY to be in the environment (.env)
genai.configure(api_key=os.environ.get("GEMINI_API_KEY", ""))

# Create the model
generation_config = {
  "temperature": 0.1,
  "top_p": 0.95,
  "top_k": 40,
  "max_output_tokens": 1024,
  "response_mime_type": "application/json",
}

model = genai.GenerativeModel(
  model_name="gemini-2.5-flash",
  generation_config=generation_config,
)

# ── In-memory cache ──────────────────────────────────────────────────────────
# Key: SHA-256 hash of the journal text  Value: analysis dict
_analysis_cache: dict[str, dict] = {}


def _cache_key(text: str) -> str:
    return hashlib.sha256(text.encode()).hexdigest()


def _build_prompt(text: str) -> str:
    return f"""
    Analyze the following journal entry written by a user after a nature session.
    Extract the primary emotion, key concepts/keywords (max 3), and a short summary.
    
    Journal Entry: "{text}"
    
    Respond STRICTLY with a valid JSON object matching this schema:
    {{
      "emotion": "string (single word representing primary emotion)",
      "keywords": ["array of", "string", "keywords"],
      "summary": "string (one short sentence summary)"
    }}
    """


def analyze_journal_text(text: str) -> dict:
    """Analyze journal text using Gemini. Results are cached by content hash."""
    key = _cache_key(text)
    if key in _analysis_cache:
        print("Cache hit — returning cached analysis.")
        return _analysis_cache[key]

    try:
        response = model.generate_content(_build_prompt(text))
        text_response = response.text.strip()
        if text_response.startswith('```json'):
            text_response = text_response[7:]
        if text_response.endswith('```'):
            text_response = text_response[:-3]
        result = json.loads(text_response.strip())
        _analysis_cache[key] = result          # store in cache
        return result
    except Exception as e:
        print(f"Error calling Gemini: {e}")
        # Default fallback if there's an API error or key isn't set up yet
        return {
            "emotion": "unknown",
            "keywords": ["nature", "journal"],
            "summary": "AI analysis unavailable."
        }


async def analyze_journal_stream(text: str):
    """
    Async generator that streams the Gemini response token-by-token.
    Yields Server-Sent Events (SSE) formatted strings.
    Results are NOT cached here — the caller should cache the assembled result.
    """
    key = _cache_key(text)

    # If already cached, stream the cached JSON instantly as a single chunk
    if key in _analysis_cache:
        print("Cache hit — streaming cached analysis.")
        cached = json.dumps(_analysis_cache[key])
        yield f"data: {cached}\n\n"
        yield "data: [DONE]\n\n"
        return

    # Use streaming generation (response_mime_type must be plain text for streaming)
    stream_model = genai.GenerativeModel(
        model_name="gemini-2.5-flash",
        generation_config={
            "temperature": 0.1,
            "top_p": 0.95,
            "top_k": 40,
            "max_output_tokens": 1024,
        },
    )

    prompt = _build_prompt(text)
    full_text = ""
    try:
        response = stream_model.generate_content(prompt, stream=True)
        for chunk in response:
            token = chunk.text if chunk.text else ""
            if token:
                full_text += token
                yield f"data: {json.dumps({'chunk': token})}\n\n"

        # Try to parse and cache the assembled response
        clean = full_text.strip()
        if clean.startswith('```json'):
            clean = clean[7:]
        if clean.endswith('```'):
            clean = clean[:-3]
        try:
            result = json.loads(clean.strip())
            _analysis_cache[key] = result
        except Exception:
            pass  # Partial parse failure is fine; cache only valid JSON

        yield "data: [DONE]\n\n"
    except Exception as e:
        print(f"Streaming error: {e}")
        yield f"data: {json.dumps({'error': str(e)})}\n\n"
        yield "data: [DONE]\n\n"
