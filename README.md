# linkedin-guest-scraper

I needed a way to pull public job postings and full descriptions from LinkedIn without maintaining throwaway accounts or spinning up headless Chrome. This talks directly to LinkedIn's public guest endpoints (`seeMoreJobPostings` and `jobPosting/{id}`) using httpx and parses the html with selectolax.

It writes either to a SQLite database or JSON Lines. Existing jobs in SQLite get updated on collision so you can run it on a schedule without duplicating rows.

## Setup

I run this on Windows with Python 3.11, but any recent 3.x should work.

```cmd
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

## Usage

Save to SQLite:

```cmd
python scrape.py -k "data engineer" -l "Remote" --db jobs.db --limit 100
```

Save to JSON Lines:

```cmd
python scrape.py -k "python developer" -l "United States" -o jobs.jsonl
```

Through an upstream proxy:

```cmd
python scrape.py -k "devops" -l "Austin, TX" --db jobs.db --proxy http://127.0.0.1:8888
```

### Options

- `-k`, `--keywords`: search terms (quotes needed if multiple words)
- `-l`, `--location`: city, state, country, or "Remote"
- `-n`, `--limit`: max total jobs to scrape (default is no limit, runs until no more pages)
- `--db`: SQLite output file (creates table `jobs` if it doesn't exist)
- `-o`, `--out`: JSONL output file (you must provide either `--db` or `-o`)
- `--delay`: pause in seconds between requests (default is 2.5). Don't set this under 1.5 if you're not using proxies, guest endpoints will ban your IP for an hour.
- `--proxy`: proxy url passed straight to httpx (http or https)

### Database schema

The SQLite table looks like:

```sql
CREATE TABLE IF NOT EXISTS jobs (
    job_id TEXT PRIMARY KEY,
    title TEXT,
    company TEXT,
    location TEXT,
    posted_date TEXT,
    apply_url TEXT,
    description_html TEXT,
    description_text TEXT,
    seniority TEXT,
    employment_type TEXT,
    job_function TEXT,
    industries TEXT,
    scraped_at TEXT
);
```

<!-- generated: 2026-09-22 -->
