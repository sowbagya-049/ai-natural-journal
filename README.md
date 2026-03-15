# AI Journal System

A full-stack application that allows users to write journal entries after nature sessions and get AI-driven emotional insights using the Google Gemini API.

## Features

- **Write Journal Entries:** Log your thoughts and the natural ambience (forest, ocean, rain, etc.)
- **View Past Entries:** See all your previous logs organized neatly.
- **AI Analysis:** Click "Analyze" on any entry to extract the primary emotion, keywords, and a short summary using **Google Gemini 1.5 Flash**.
- **Insights Dashboard:** View aggregated stats including total entries, most common emotion, top ambience, and recent keywords.

## Tech Stack

- **Frontend:** React (powered by Vite) + Vanilla CSS (Modern glassmorphism UI)
- **Backend:** Python + FastAPI
- **Database:** SQLite (via SQLAlchemy)
- **AI Integration:** Google Generative AI SDK (Gemini API)

## Project Structure

```
ai-journal-system/
├── backend/
│   ├── database.py       # SQLite connection & session
│   ├── llm_service.py    # Gemini API wrapper
│   ├── main.py           # FastAPI endpoints
│   ├── models.py         # SQLAlchemy and Pydantic schemas
│   └── requirements.txt  # Python dependencies
├── frontend/             # Vite + React app
│   ├── src/
│   │   ├── components/   # UI generic components
│   │   ├── App.jsx       # Main layout and state
│   │   └── index.css     # Global styles
│   └── package.json
├── README.md             # This file
└── ARCHITECTURE.md       # Architectural scaling answers
```

## How to Run

### 1. Backend Setup

1. Navigate to the backend folder:
   ```bash
   cd backend
   ```
2. Create and activate a virtual environment (optional but recommended):
   ```bash
   python -m venv venv
   # On Windows: venv\Scripts\activate
   # On Mac/Linux: source venv/bin/activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Set up your `.env` file or environment variable with your Gemini API Key in the `backend/` directory:
   ```
   GEMINI_API_KEY=your_google_gemini_api_key_here
   ```
5. Run the server:
   ```bash
   uvicorn main:app --reload
   ```
   *The API will be available at `http://localhost:8000`.*

### 2. Frontend Setup

1. Open a new terminal and navigate to the frontend folder:
   ```bash
   cd frontend
   ```
2. Install dependencies:
   ```bash
   npm install
   ```
3. Start the development server:
   ```bash
   npm run dev
   ```
4. Open the displayed local URL (typically `http://localhost:5173`) in your browser.

## API Endpoints

### `POST /api/journal`
Creates a new journal entry.
**Body:** `{ "userId": "string", "ambience": "string", "text": "string" }`

### `GET /api/journal/{userId}`
Gets all journal entries for a specific user.

### `POST /api/journal/analyze`
Sends the text to the Gemini API and returns insights.
**Body:** `{ "text": "string" }`
**Returns:** `{ "emotion": "string", "keywords": [...], "summary": "string" }`

### `GET /api/journal/insights/{userId}`
Returns aggregated statistics for the user's dashboard.
