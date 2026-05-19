import sqlite3
from datetime import datetime

DB_PATH = "consultations.db"

def init_db():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS consultations (
            thread_id     TEXT PRIMARY KEY,
            patient_case  TEXT,
            final_report  TEXT,
            created_at    TEXT
        )
    """)
    conn.commit()
    conn.close()

def save_report(thread_id: str, patient_case: str, final_report: str):
    conn = sqlite3.connect(DB_PATH)
    conn.execute(
        "INSERT OR REPLACE INTO consultations VALUES (?, ?, ?, ?)",
        (thread_id, patient_case, final_report, datetime.now().isoformat())
    )
    conn.commit()
    conn.close()

def get_all_reports():
    conn = sqlite3.connect(DB_PATH)
    rows = conn.execute(
        "SELECT thread_id, patient_case, created_at FROM consultations ORDER BY created_at DESC"
    ).fetchall()
    conn.close()
    return rows

def get_report(thread_id: str):
    conn = sqlite3.connect(DB_PATH)
    row = conn.execute(
        "SELECT final_report FROM consultations WHERE thread_id = ?", (thread_id,)
    ).fetchone()
    conn.close()
    return row[0] if row else None