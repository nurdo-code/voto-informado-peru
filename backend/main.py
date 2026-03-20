from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Optional
import sqlite3
import os

app = FastAPI(title="Political Transparency Evaluator")

# Allow CORS for development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

DB_PATH = os.path.join(os.path.dirname(__file__), "transparency.db")

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

@app.get("/parties")
def get_parties():
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM parties ORDER BY name")
    parties = [dict(row) for row in c.fetchall()]
    conn.close()
    return parties

@app.get("/ranking")
def get_ranking():
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("SELECT id, name, logo_url, score FROM parties ORDER BY score DESC")
    ranking = [dict(row) for row in c.fetchall()]
    conn.close()
    return ranking

@app.get("/candidates")
def get_candidates(party_id: Optional[int] = None):
    conn = get_db_connection()
    c = conn.cursor()
    if party_id:
        c.execute("SELECT * FROM candidates WHERE party_id = ? ORDER BY score DESC", (party_id,))
    else:
        c.execute("SELECT * FROM candidates ORDER BY score DESC")
    
    rows = [dict(row) for row in c.fetchall()]
    conn.close()

    # Group candidates by 'cargo'
    grouped_candidates = {}
    for row in rows:
        cargo = row.get("cargo", "Otros")
        if cargo not in grouped_candidates:
            grouped_candidates[cargo] = []
        grouped_candidates[cargo].append(row)

    return grouped_candidates

@app.get("/candidate/{id}/articles")
def get_candidate_articles(id: int):
    conn = get_db_connection()
    c = conn.cursor()
    
    # Verify candidate exists
    c.execute("SELECT name, score, news_count FROM candidates WHERE id = ?", (id,))
    candidate = c.fetchone()
    if not candidate:
        conn.close()
        raise HTTPException(status_code=404, detail="Candidate not found")
        
    c.execute("SELECT title, url, source, keyword_detected FROM articles WHERE candidate_id = ?", (id,))
    articles = [dict(row) for row in c.fetchall()]
    
    # Also fetch the score reasons for transparency
    c.execute("SELECT reason, deduction FROM score_reasons WHERE candidate_id = ?", (id,))
    reasons = [dict(row) for row in c.fetchall()]
    
    conn.close()
    
    return {
        "candidate": dict(candidate),
        "articles": articles,
        "reasons": reasons
    }

# Mount static files (frontend) at root
frontend_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "frontend")
if os.path.exists(frontend_path):
    app.mount("/", StaticFiles(directory=frontend_path, html=True), name="frontend")
