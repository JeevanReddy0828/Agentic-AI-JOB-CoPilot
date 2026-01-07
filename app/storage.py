import sqlite3
from pathlib import Path
from typing import Any, Dict, Optional, List
import json
import uuid
from datetime import datetime

DB_PATH = Path("data/copilot.db")

def init_db():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("""
        CREATE TABLE IF NOT EXISTS jobs (
            job_id TEXT PRIMARY KEY,
            job_url TEXT,
            company TEXT,
            role TEXT,
            jd_text TEXT,
            created_at TEXT
        )
        """)
        conn.execute("""
        CREATE TABLE IF NOT EXISTS artifacts (
            run_id TEXT PRIMARY KEY,
            job_id TEXT,
            created_at TEXT,
            payload_json TEXT,
            FOREIGN KEY(job_id) REFERENCES jobs(job_id)
        )
        """)
        conn.commit()

def _now() -> str:
    return datetime.utcnow().isoformat()

def upsert_job(job_url: Optional[str], company: Optional[str], role: Optional[str], jd_text: str) -> str:
    job_id = str(uuid.uuid5(uuid.NAMESPACE_URL, job_url)) if job_url else str(uuid.uuid4())
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("""
        INSERT INTO jobs (job_id, job_url, company, role, jd_text, created_at)
        VALUES (?, ?, ?, ?, ?, ?)
        ON CONFLICT(job_id) DO UPDATE SET
            job_url=excluded.job_url,
            company=excluded.company,
            role=excluded.role,
            jd_text=excluded.jd_text
        """, (job_id, job_url, company, role, jd_text, _now()))
        conn.commit()
    return job_id

def save_artifact(job_id: str, payload: Dict[str, Any]) -> str:
    run_id = str(uuid.uuid4())
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute(
            "INSERT INTO artifacts (run_id, job_id, created_at, payload_json) VALUES (?, ?, ?, ?)",
            (run_id, job_id, _now(), json.dumps(payload)),
        )
        conn.commit()
    return run_id

def load_run(run_id: str) -> Optional[Dict[str, Any]]:
    with sqlite3.connect(DB_PATH) as conn:
        cur = conn.execute("SELECT payload_json FROM artifacts WHERE run_id=?", (run_id,))
        row = cur.fetchone()
        if not row:
            return None
        return json.loads(row[0])

def list_runs_for_job(job_id: str) -> List[Dict[str, Any]]:
    with sqlite3.connect(DB_PATH) as conn:
        cur = conn.execute("""
            SELECT run_id, created_at
            FROM artifacts
            WHERE job_id=?
            ORDER BY created_at DESC
        """, (job_id,))
        return [{"run_id": r[0], "created_at": r[1]} for r in cur.fetchall()]
