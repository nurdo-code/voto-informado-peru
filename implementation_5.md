# Implementation Plan: Political Transparency Evaluator

## Goal Description
Build a simple web application (MVP) to evaluate the transparency of political parties in Peru. It consists of a data scraper that fetches candidate information, a search analyzer that scores candidates based on negative news mentions and article counts, a FastAPI backend to serve the data via SQLite, and a vanilla JS/CSS frontend to display the rankings and news articles per candidate.

## Proposed Changes

### Project Structure
```text
NOSEPORQUIENVOTAR/
├── backend/
│   ├── database.py       # SQLite connection and table initialization
│   ├── main.py           # FastAPI application and endpoints
│   ├── scraper.py        # Logic to scrape JNE portal
│   └── analyzer.py       # Logic to search DuckDuckGo, store articles, calculate scores
├── frontend/
│   ├── index.html        # Main dashboard
│   ├── style.css         # Styling (green/red theme)
│   └── script.js         # API polling and rendering logic
└── requirements.txt      # Python dependencies
```

### Database Schema (SQLite)
- [parties](file:///c:/Users/ASUS/Desktop/NOSEPORQUIENVOTAR/backend/main.py#26-34): [id](file:///c:/Users/ASUS/Desktop/NOSEPORQUIENVOTAR/backend/main.py#44-55) (PK, int), `name` (text), `logo_url` (text), `score` (float)
- [candidates](file:///c:/Users/ASUS/Desktop/NOSEPORQUIENVOTAR/backend/main.py#44-55): [id](file:///c:/Users/ASUS/Desktop/NOSEPORQUIENVOTAR/backend/main.py#44-55) (PK, int), `name` (text), `party_id` (FK), `cargo` (text), `score` (int), `news_count` (int)
- `score_reasons`: [id](file:///c:/Users/ASUS/Desktop/NOSEPORQUIENVOTAR/backend/main.py#44-55) (PK, int), `candidate_id` (FK), `reason` (text), `deduction` (int)
- [articles](file:///c:/Users/ASUS/Desktop/NOSEPORQUIENVOTAR/backend/main.py#56-82): [id](file:///c:/Users/ASUS/Desktop/NOSEPORQUIENVOTAR/backend/main.py#44-55) (PK, int), `candidate_id` (FK), `title` (text), `url` (text), [source](file:///c:/Users/ASUS/Desktop/NOSEPORQUIENVOTAR/backend/analyzer.py#19-24) (text), `keyword_detected` (text)

### Data Processing Pipeline
1. **Scraping**: Fetches the party and candidate list via real JNE API endpoints. Extracts actual candidates and their `cargo` (e.g. Presidente, Senador, etc.).
2. **Analysis**: Uses `duckduckgo-search` to fetch the top text snippets. 
   - **Query**: `"{candidate_name}" AND ("corrupción" OR "investigación" OR "denuncia" OR "fiscalía" OR "acoso" OR "violación" OR "delito" OR "lavado de activos")`. The party name is omitted to widen results.
   - **Filter & Store**: Consider results from any Peruvian news source or without strict domain filtering if returning zero results. Extract title, url, source domain. Handle DuckDuckGo rate limiting via sleeps or User-Agent rotation. If error occurs, log it without modifying the score.
3. **Aggregation**: Party score becomes the average of its candidates' scores.

### Backend Endpoints
- `GET /parties`: Returns all parties with their scores.
- `GET /ranking`: Returns parties sorted by score descending.
- `GET /candidates?party_id=X`: Returns candidates for a specific party.
- `GET /candidate/{id}/articles`: Returns stored articles (title, url, source) for a specific candidate.

## Verification Plan
### Automated Tests
- N/A for this MVP, but we will test the API manually via Swagger UI (`/docs`).
### Manual Verification
- Run the scraper script and ensure DB populates.
- Run the analyzer script and verify that articles are stored without duplicates.
- Verify that candidate scores correctly reflect both keyword penalties and article count penalties.
- Serve the backend, open the frontend in a browser, and verify UI components load correctly, including the new candidate view showing linked articles.
