import os
import json
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

def analyze_journal_text(text: str) -> dict:
    prompt = f"""
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
    
    try:
        response = model.generate_content(prompt)
        text_response = response.text.strip()
        if text_response.startswith('```json'):
            text_response = text_response[7:]
        if text_response.endswith('```'):
            text_response = text_response[:-3]
        result = json.loads(text_response.strip())
        return result
    except Exception as e:
        print(f"Error calling Gemini: {e}")
        # Default fallback if there's an API error or key isn't set up yet
        return {
            "emotion": "unknown",
            "keywords": ["nature", "journal"],
            "summary": "AI analysis unavailable."
        }
