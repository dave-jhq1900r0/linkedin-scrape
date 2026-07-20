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


