"""
Database Connection and Schema Initializer for SQLite.
Ensures ACID-compliant storage with relational foreign keys and indices.
"""

import sqlite3
from typing import Optional
from pathlib import Path
from config import DATABASE_PATH


def get_db_connection(db_path: Optional[Path] = None) -> sqlite3.Connection:
    """
    Returns a configured SQLite connection with foreign keys enabled and row factory.
    """
    path = db_path or DATABASE_PATH
    path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(path))
    conn.execute("PRAGMA foreign_keys = ON;")
    conn.row_factory = sqlite3.Row
    return conn


def init_db(db_path: Optional[Path] = None) -> None:
    """
    Initializes database tables, indices, and constraints.
    """
    conn = get_db_connection(db_path)
    cursor = conn.cursor()

    # 1. Normalized Scholarships Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS scholarships (
        id TEXT PRIMARY KEY,
        scholarship_name TEXT NOT NULL,
        provider TEXT NOT NULL,
        provider_type TEXT NOT NULL,
        official_source_url TEXT NOT NULL,
        application_url TEXT NOT NULL,
        amount_benefit TEXT NOT NULL,
        amount_value_inr REAL,
        academic_requirements TEXT NOT NULL,
        course_level TEXT NOT NULL,
        income_criteria TEXT NOT NULL,
        income_limit_inr REAL,
        age_criteria TEXT NOT NULL,
        gender_criteria TEXT NOT NULL,
        category_criteria TEXT NOT NULL,
        domicile_state TEXT NOT NULL,
        institution_requirements TEXT NOT NULL,
        opening_date TEXT NOT NULL,
        closing_date TEXT NOT NULL,
        documents_required TEXT NOT NULL,
        selection_process TEXT NOT NULL,
        renewal_requirements TEXT NOT NULL,
        status TEXT NOT NULL,
        confidence_score REAL NOT NULL,
        verification_status TEXT NOT NULL,
        score_breakdown TEXT,
        last_verified_at TEXT NOT NULL,
        created_at TEXT NOT NULL,
        updated_at TEXT NOT NULL
    );
    """)

    # 2. Field-Level Traceable Evidence Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS scholarship_evidence (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        scholarship_id TEXT NOT NULL,
        field_name TEXT NOT NULL,
        extracted_value TEXT NOT NULL,
        source_url TEXT NOT NULL,
        evidence_text TEXT NOT NULL,
        match_score REAL NOT NULL,
        verified_at TEXT NOT NULL,
        FOREIGN KEY (scholarship_id) REFERENCES scholarships (id) ON DELETE CASCADE
    );
    """)

    # 3. Change Detection & Audit History Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS scholarship_history (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        scholarship_id TEXT NOT NULL,
        field_name TEXT NOT NULL,
        old_value TEXT NOT NULL,
        new_value TEXT NOT NULL,
        detected_at TEXT NOT NULL,
        source_url TEXT NOT NULL,
        evidence_text TEXT NOT NULL,
        run_id TEXT NOT NULL,
        FOREIGN KEY (scholarship_id) REFERENCES scholarships (id) ON DELETE CASCADE
    );
    """)

    # 4. Crawl Runs Execution History Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS crawl_runs (
        run_id TEXT PRIMARY KEY,
        run_type TEXT NOT NULL,
        started_at TEXT NOT NULL,
        completed_at TEXT,
        total_discovered INTEGER DEFAULT 0,
        total_verified INTEGER DEFAULT 0,
        total_review_required INTEGER DEFAULT 0,
        total_changes_detected INTEGER DEFAULT 0,
        total_expired_detected INTEGER DEFAULT 0,
        log_summary TEXT
    );
    """)

    # 5. Discovery Seeds Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS discovery_seeds (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        url TEXT UNIQUE NOT NULL,
        name TEXT NOT NULL,
        provider_type TEXT NOT NULL,
        discovered_at TEXT NOT NULL,
        status TEXT NOT NULL
    );
    """)

    # Indices for high-frequency queries
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_scholarships_status ON scholarships(status);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_scholarships_confidence ON scholarships(confidence_score);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_scholarships_provider ON scholarships(provider_type);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_evidence_scholarship ON scholarship_evidence(scholarship_id);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_history_scholarship ON scholarship_history(scholarship_id);")

    conn.commit()
    conn.close()
