import time
import httpx

BASE_URL = "https://www.arbeitnow.com/api/job-board-api"


def search_arbeitnow_jobs(page: int = 1, max_retries: int = 3) -> dict:
    params = {"page": page}
    for attempt in range(1, max_retries + 1):
        try:
            response = httpx.get(BASE_URL, params=params, timeout=10.0)
            response.raise_for_status()
            return response.json()
        except (httpx.HTTPStatusError, httpx.RequestError) as err:
            if attempt < max_retries:
                time.sleep(1.0)
                continue
            raise err