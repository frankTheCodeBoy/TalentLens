import sqlite3

DB_PATH = "resume_analysis.db"


def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS analyses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            filename TEXT,
            category TEXT,
            confidence REAL,
            skills TEXT,
            suggestion TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
        """
    )
    conn.commit()
    conn.close()


def save_analysis(filename, category, confidence, skills, suggestion):
    init_db()
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        """
        INSERT INTO analyses
        (filename, category, confidence, skills, suggestion)
        VALUES (?, ?, ?, ?, ?)
        """,
        (
            filename,
            category,
            confidence,
            ", ".join(skills),
            suggestion,
        ),
    )
    conn.commit()
    conn.close()


def get_history():
    init_db()
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM analyses ORDER BY timestamp DESC")
    rows = cursor.fetchall()
    conn.close()
    return rows
