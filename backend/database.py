import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "transparency.db")

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    c = conn.cursor()

    # Create tables
    c.executescript("""
        CREATE TABLE IF NOT EXISTS parties (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL,
            logo_url TEXT,
            score REAL DEFAULT 0.0
        );

        CREATE TABLE IF NOT EXISTS candidates (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            party_id INTEGER NOT NULL,
            cargo TEXT NOT NULL,
            score INTEGER DEFAULT 100,
            news_count INTEGER DEFAULT 0,
            FOREIGN KEY (party_id) REFERENCES parties (id)
        );

        CREATE TABLE IF NOT EXISTS score_reasons (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            candidate_id INTEGER NOT NULL,
            reason TEXT NOT NULL,
            deduction INTEGER NOT NULL,
            FOREIGN KEY (candidate_id) REFERENCES candidates (id)
        );

        CREATE TABLE IF NOT EXISTS articles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            candidate_id INTEGER NOT NULL,
            title TEXT NOT NULL,
            url TEXT NOT NULL,
            source TEXT NOT NULL,
            keyword_detected TEXT,
            UNIQUE(candidate_id, url),
            FOREIGN KEY (candidate_id) REFERENCES candidates (id)
        );
    """)

    conn.commit()
    conn.close()

if __name__ == "__main__":
    init_db()
    print(f"Database initialized at {DB_PATH}")
