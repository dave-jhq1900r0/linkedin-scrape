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


def crawl(keywords: str, location: str, max_jobs: int, delay_range: tuple[float, float], output_format: str, out_file: Path):
    client = GuestClient()
    seen_ids = set()
    total_saved = 0
    start = 0
    batch_size = 25

    db_conn = None
    json_fh = None

    if output_format == "sqlite":
        db_conn = init_db(out_file)
    else:
        out_file.parent.mkdir(parents=True, exist_ok=True)
        json_fh = open(out_file, "a", encoding="utf-8")

    try:
        while total_saved < max_jobs:
            print(f"fetching batch at offset {start}...")
            html = client.get_search_page(keywords=keywords, location=location, start=start)
            if not html:
                print("empty page or search limit hit, stopping.")
                break

            cards = parse_job_cards(html)
            if not cards:
                print("no more cards returned.")
                break

            new_cards = [c for c in cards if c["job_id"] not in seen_ids]
            if not new_cards:
                # pagination returned duplicates or ended
                break

            for card in new_cards:
                seen_ids.add(card["job_id"])
                time.sleep(random.uniform(delay_range[0], delay_range[1]))

                detail_html = client.get_job_detail(card["job_id"])
                detail_info = parse_job_detail(detail_html)

                full_record = dict(card)
                full_record.update(detail_info)

                if db_conn:
                    save_sqlite(db_conn, full_record)
                elif json_fh:
                    json_fh.write(json.dumps(full_record, ensure_ascii=False) + "\n")
                    json_fh.flush()

                total_saved += 1
                print(f"[{total_saved}/{max_jobs}] saved: {card['title']} @ {card['company']}")

                if total_saved >= max_jobs:
                    break

            start += batch_size
            # FIXME: linkedin starts serving weird 400s past offset 900 on guest searches
            time.sleep(random.uniform(1.5, 3.0))

    finally:
        client.close()
        if db_conn:
            db_conn.close()
        if json_fh:
            json_fh.close()


def main():
    parser = argparse.ArgumentParser(description="Scrape LinkedIn job postings without login")
    parser.add_argument("-k", "--keywords", required=True, help="Job search terms")
    parser.add_argument("-l", "--location", default="United States", help="Target location string")
    parser.add_argument("-n", "--count", type=int, default=50, help="Target job count")
    parser.add_argument("-o", "--output", default="jobs.sqlite", help="Output destination file")
    parser.add_argument("--format", choices=["sqlite", "jsonl"], default="sqlite", help="Output format")
    parser.add_argument("--min-delay", type=float, default=1.2, help="Minimum pause between detail requests")
    parser.add_argument("--max-delay", type=float, default=2.8, help="Maximum pause between detail requests")

    args = parser.parse_args()

    dest_path = Path(args.output)
    try:
        crawl(
            keywords=args.keywords,
            location=args.location,
            max_jobs=args.count,
            delay_range=(args.min_delay, args.max_delay),
            output_format=args.format,
            out_file=dest_path
        )
    except KeyboardInterrupt:
        print("\ncanceled by user, exiting.")
        sys.exit(0)


if __name__ == "__main__":
    main()
