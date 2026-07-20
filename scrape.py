import argparse
import json
import random
import sqlite3
import sys
import time
from pathlib import Path

from client import GuestClient
from parser import parse_job_cards, parse_job_detail


def init_db(db_path: Path):
    conn = sqlite3.connect(db_path)
    with conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS jobs (
                job_id TEXT PRIMARY KEY,
                title TEXT,
                company TEXT,
                location TEXT,
                posted_date TEXT,
                url TEXT,
                seniority_level TEXT,
                employment_type TEXT,
                job_function TEXT,
                industries TEXT,
                description TEXT,
                fetched_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
    return conn


def save_sqlite(conn, record: dict):
    sql = """
        INSERT INTO jobs (job_id, title, company, location, posted_date, url, seniority_level, employment_type, job_function, industries, description)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(job_id) DO UPDATE SET
            title=excluded.title,
            company=excluded.company,
            location=excluded.location,
            posted_date=excluded.posted_date,
            url=excluded.url,
            seniority_level=excluded.seniority_level,
            employment_type=excluded.employment_type,
            job_function=excluded.job_function,
            industries=excluded.industries,
            description=excluded.description
    """
    with conn:
        conn.execute(sql, (
            record["job_id"],
            record.get("title", ""),
            record.get("company", ""),
            record.get("location", ""),
            record.get("posted_date", ""),
            record.get("url", ""),
            record.get("seniority_level", ""),
            record.get("employment_type", ""),
            record.get("job_function", ""),
            record.get("industries", ""),
            record.get("description", ""),
        ))


