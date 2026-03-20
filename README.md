# Political Transparency Evaluator 🔍

A minimal viable product (MVP) web application that evaluates the transparency of political parties and their candidates in Peru by checking their negative mentions in credible news sources.

## Features
- **Data Scraper**: Extracts candidates and parties. Uses resilient fallback datasets to avoid crashes if the JNE portal structure changes.
- **Search Analyzer**: Searches DuckDuckGo for top negative indicators (corrupción, delito, etc.) on trusted domains (El Comercio, La República, etc.).
- **Scoring System**: Deduct points based on severe keywords AND the volume of negative news.
- **FastAPI Backend**: Delivers JSON payloads with scores, article links, and transparency records.
- **Vanilla Frontend**: Clean, responsive UI built without node dependencies.

## Prerequisites
- Python 3.9+

## Installation
1. Clone the repository and navigate to the project directory:
   ```bash
   cd NOSEPORQUIENVOTAR
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Initialize the database and prepare the data:
   **Step A: Initialize the database**
   ```bash
   python -m backend.database
   ```
   **Step B: Run the scraper**
   ```bash
   python -m backend.scraper
   ```
   **Step C: Analyze the candidates (this fetches the news)**
   ```bash
   python -m backend.analyzer
   ```

## Running the Application
Start the FastAPI server:
```bash
uvicorn backend.main:app --reload
```

Then, open your browser and navigate to:
**http://127.0.0.1:8000**
