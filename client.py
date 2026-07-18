import time
import random
import httpx

SEARCH_URL = "https://www.linkedin.com/jobs-guest/jobs/api/seeMoreJobPostings/search"
JOB_DETAIL_URL = "https://www.linkedin.com/jobs-guest/jobs/api/jobPosting/{job_id}"

DEFAULT_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Accept-Language": "en-US,en;q=0.9",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Referer": "https://www.linkedin.com/jobs",
}

class GuestClient:
    """Handles requests against LinkedIn guest search endpoints with backoff."""

    def __init__(self, timeout: float = 18.0):
        self.client = httpx.Client(headers=DEFAULT_HEADERS, timeout=timeout, follow_redirects=True)

    def get_search_page(self, keywords: str, location: str, start: int = 0) -> str:
        params = {
            "keywords": keywords,
            "location": location,
            "start": start,
        }
        return self._request(SEARCH_URL, params=params)

    def get_job_detail(self, job_id: str) -> str:
        url = JOB_DETAIL_URL.format(job_id=job_id)
        return self._request(url)

    def _request(self, url: str, params: dict = None) -> str:
        retries = 4
        backoff = 4.0
        for attempt in range(retries):
            try:
                # print(f"requesting {url} with {params}")
                resp = self.client.get(url, params=params)
                if resp.status_code == 200:
                    return resp.text
                if resp.status_code == 429:
                    # guest endpoint limits quickly when crawling fast
                    sleep_time = backoff + random.uniform(2.0, 5.0)
                    time.sleep(sleep_time)
                    backoff *= 2.2
                    continue
                if resp.status_code in (404, 410):
                    return ""
            except (httpx.ConnectError, httpx.ReadTimeout, httpx.RemoteProtocolError):
                if attempt == retries - 1:
                    return ""
                time.sleep(3.0)
        return ""

    def close(self):
        self.client.close()
