# Implementation Plan: Political Transparency Evaluator

## Goal Description
Build a simple web application (MVP) to evaluate the transparency of political parties in Peru. It consists of a data scraper that fetches candidate information from a JNE portal, a search analyzer that scores candidates based on negative news mentions, a FastAPI backend to serve the data via SQLite, and a vanilla JS/CSS frontend to display the rankings.

## Proposed Changes

### Project Structure
```text
NOSEPORQUIENVOTAR/
├── backend/
│   ├── database.py       # SQLite connection and table initialization
│   ├── main.py           # FastAPI application and endpoints
│   ├── scraper.py        # Logic to scrape JNE portal
│   └── analyzer.py       # Logic to search DuckDuckGo and calculate scores
├── frontend/
│   ├── index.html        # Main dashboard
│   ├── style.css         # Styling (green/red theme)
│   └── script.js         # API polling and rendering logic
└── requirements.txt      # Python dependencies
```

### Database Schema (SQLite)
- `parties`: `id` (PK, text/int), `name` (text), `logo_url` (text), `score` (float)
- `candidates`: `id` (PK, int), `name` (text), `party_id` (FK), `score` (int)

### Data Processing Pipeline
1. **Scraping**: Fetches the party and candidate list. Given the nature of Peruvian government sites, it might be an SPA. If so, we might need to find the API endpoint it uses.
2. **Analysis**: Uses `duckduckgo-search` to fetch the top text snippets for a query like `"{candidate_name}" corrupción`. Reduces the candidate's initial score of 100 based on keyword occurrences.
3. **Aggregation**: Party score becomes the average of its candidates' scores.

### Backend Endpoints
- `GET /parties`: Returns all parties with their scores.
- `GET /ranking`: Returns parties sorted by score descending.
- `GET /candidates?party_id=X`: Returns candidates for a specific party.

## Verification Plan
### Automated Tests
- N/A for this MVP, but we will test the API manually via Swagger UI (`/docs`).
### Manual Verification
- Run the scraper script and ensure DB populates.
- Run the analyzer script and ensure scores are updated correctly.
- Serve the backend, open the frontend in a browser, and verify UI components load correctly.
