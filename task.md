# Political Transparency Web Application

## 1. Project Setup
- [ ] Create project folder structure
- [ ] Define requirements.txt (fastapi, uvicorn, requests, beautifulsoup4, duckduckgo-search)

## 2. Database & Models
- [ ] Set up SQLite using standard `sqlite3` or simple ORM
- [ ] Create `parties` table (id, name, logo_url, score)
- [ ] Create `candidates` table (id, name, party_id, score)
- [ ] Create `score_reasons` table (id, candidate_id, reason, deduction) to show transparency

## 3. Data Scraper
- [ ] Script to fetch data from `votoinformado.jne.gob.pe`
- [ ] Extract candidate name, party, and logo
- [ ] Safe execution (try/except) so it doesn't crash on failure
- [ ] Save to database

## 4. Search & Analysis Engine
- [ ] Implement DuckDuckGo search using candidate name + party name/region
- [ ] Filter search results to only include credible news sources
- [ ] Keyword analysis ("corrupción", "delito", "investigado", "denuncia", "violencia", "sentenciado")
- [ ] Record reasons for score deductions
- [ ] Keep score 100 if no results found

## 5. FastAPI Backend
- [ ] Implement `GET /parties` endpoint
- [ ] Implement `GET /ranking` endpoint
- [ ] Implement `GET /candidates` endpoint

## 6. Frontend
- [ ] Create `index.html`, `style.css`, `script.js`
- [ ] Fetch data from backend
- [ ] Render tables, color codes (green/red), and optional candidate view

## 7. Documentation
- [ ] Generate `README.md` with instructions
