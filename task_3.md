# Political Transparency Web Application

## 1. Project Setup
- [ ] Create project folder structure
- [ ] Define requirements.txt (fastapi, uvicorn, requests, beautifulsoup4, duckduckgo-search)

## 2. Database & Models
- [ ] Set up SQLite
- [ ] Create `parties` table (id, name, logo_url, score)
- [ ] Create `candidates` table (id, name, party_id, score, news_count)
- [ ] Create `score_reasons` table (id, candidate_id, reason, deduction)
- [ ] Create `articles` table (id, candidate_id, title, url, source, keyword_detected)

## 3. Data Scraper
- [ ] Script to fetch data from `votoinformado.jne.gob.pe`
- [ ] Extract candidate name, party, and logo
- [ ] Safe execution (try/except) so it doesn't crash on failure
- [ ] Save to database

## 4. Search & Analysis Engine
- [ ] Implement DuckDuckGo search using `"{candidate_name}" "{party_name}" {keyword}`
- [ ] Filter search results to only include trusted news domains
- [ ] Extract title, url, source domain (no full scraping)
- [ ] Store up to 5-10 articles per candidate (avoid duplicate URLs)
- [ ] Apply keyword penalties ("corrupción", "investigado", etc.)
- [ ] Apply article count penalties (1-2: -5, 3-5: -10, 6+: -20)
- [ ] Keep score 100 if no results found

## 5. FastAPI Backend
- [ ] Implement `GET /parties` endpoint
- [ ] Implement `GET /ranking` endpoint
- [ ] Implement `GET /candidates` endpoint
- [ ] Implement `GET /candidate/{id}/articles` endpoint

## 6. Frontend
- [ ] Create `index.html`, `style.css`, `script.js`
- [ ] Fetch data from backend and render parties and ranking
- [ ] Show `news_count` next to candidate name, color-coded (green=0, red=many)
- [ ] Implement Candidate View displaying their articles with clickable titles and sources

## 7. Documentation
- [ ] Generate instructions to run locally
