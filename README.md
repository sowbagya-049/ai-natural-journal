# AI Journal System

A full-stack application that allows users to write journal entries after nature sessions and get AI-driven emotional insights using the Google Gemini API.

## Features

- **Write Journal Entries:** Log your thoughts and the natural ambience (forest, ocean, rain, etc.)
- **View Past Entries:** See all your previous logs organized neatly.
- **AI Analysis:** Click "Analyze" on any entry to extract the primary emotion, keywords, and a short summary using **Google Gemini 2.5 Flash**.
- **Insights Dashboard:** View aggregated stats including total entries, most common emotion, top ambience, and recent keywords.
- **Streaming Analysis:** Real-time token streaming via SSE (`/api/journal/analyze/stream`)
- **Caching:** Analysis results are cached in-memory (SHA-256 keyed) to avoid redundant LLM calls.
- **Rate Limiting:** All endpoints are protected by `slowapi` (10 req/min on analyze, 60 req/min global).

## Tech Stack

- **Frontend:** React (Vite) + Vanilla CSS (Glassmorphism UI)
- **Backend:** Python + FastAPI + slowapi + sse-starlette
- **Database:** SQLite (via SQLAlchemy)
- **AI:** Google Generative AI SDK (Gemini 2.5 Flash)
- **Container:** Docker + Docker Compose

## Project Structure

```
ai-journal-system/
├── backend/
│   ├── database.py       # SQLite connection & session
│   ├── llm_service.py    # Gemini API wrapper (caching + streaming)
│   ├── main.py           # FastAPI endpoints + rate limiting
│   ├── models.py         # SQLAlchemy and Pydantic schemas
│   ├── requirements.txt  # Python dependencies
│   └── Dockerfile
├── frontend/             # Vite + React app
│   ├── src/
│   │   ├── components/   # UI generic components
│   │   ├── App.jsx       # Main layout and state
│   │   └── index.css     # Global styles
│   ├── package.json
│   └── Dockerfile
├── docker-compose.yml
├── .env.example
├── README.md
└── ARCHITECTURE.md
```

## How to Run

### Option A — Docker (recommended)

```bash
# 1. Copy env file and add your key
cp .env.example .env
# Edit .env → set GEMINI_API_KEY=your_key_here

# 2. Build and start all services
docker compose up --build

# App: http://localhost
# API: http://localhost:8000
# Docs: http://localhost:8000/docs
```

### Option B — Local Development

#### 1. Backend Setup

```bash
cd backend
python -m venv venv
# Windows:
venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate

pip install -r requirements.txt
```

Create `backend/.env`:
```
GEMINI_API_KEY=your_google_gemini_api_key_here
```

```bash
uvicorn main:app --reload
# API at http://localhost:8000
```

#### 2. Frontend Setup

```bash
cd frontend
npm install
npm run dev
# App at http://localhost:5173
```

## API Endpoints

| Method | Endpoint | Description | Rate Limit |
|--------|----------|-------------|------------|
| `POST` | `/api/journal` | Create a new journal entry | 30/min |
| `GET`  | `/api/journal/{userId}` | Get all entries for a user | 60/min |
| `POST` | `/api/journal/analyze` | Analyze entry with Gemini (cached) | 10/min |
| `POST` | `/api/journal/analyze/stream` | Stream analysis as SSE tokens | 10/min |
| `GET`  | `/api/journal/insights/{userId}` | Aggregated user stats | 30/min |

### Streaming Example (JavaScript)

```js
const response = await fetch('/api/journal/analyze/stream', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ text: 'Today I walked through the misty forest...' })
});
const reader = response.body.getReader();
const decoder = new TextDecoder();
while (true) {
  const { done, value } = await reader.read();
  if (done) break;
  console.log(decoder.decode(value)); // SSE chunks
}
```

## Deployment

- **Frontend:** Deploy `frontend/` to **Vercel** (set `VITE_API_URL` to your backend URL)
- **Backend:** Deploy `backend/` to **Render** (set `GEMINI_API_KEY` env var in Render dashboard)
