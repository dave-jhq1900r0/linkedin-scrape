# linkedin-guest-scraper

I needed a way to pull public job postings and full descriptions from LinkedIn without maintaining throwaway accounts or spinning up headless Chrome. This talks directly to LinkedIn's public guest endpoints (`seeMoreJobPostings` and `jobPosting/{id}`) using httpx and parses the html with selectolax.

## Setup

I run this on Windows with Python 3.11, but any recent 3.x should work.

```cmd
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

## Usage

Search for postings and dump them directly into a JSON Lines file:

```cmd
python scrape.py --keywords "python developer" --location "United States" --limit 50 --out jobs.jsonl
```

If you omit `--limit`, it keeps paginating until LinkedIn stops returning results or hits a 429.

Options:
- `-k`, `--keywords`: search query text
- `-l`, `--location`: location filter (city, state, country, or "Remote")
- `-n`, `--limit`: max number of jobs to fetch
- `-o`, `--out`: path to output JSONL file

Keep the requests reasonably spaced out or LinkedIn will throw 429s within a couple minutes.
