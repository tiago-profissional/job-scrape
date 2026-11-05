import time
import httpx

BASE_URL = "https://portal.api.gupy.io/api/v1/jobs"


def search_gupy_jobs(
    job_name: str = "desenvolvedor",
    limit: int = 10,
    offset: int = 0,
    max_retries: int = 3,
    backoff_factor: float = 1.0,
) -> dict:
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "application/json, text/plain, */*",
        "Referer": "https://portal.gupy.io/",
        "Origin": "https://portal.gupy.io",
    }
    params = {
        "jobName": job_name,
        "limit": limit,
        "offset": offset,
    }

    for attempt in range(1, max_retries + 1):
        try:
            response = httpx.get(BASE_URL, params=params, headers=headers, timeout=10.0)
            response.raise_for_status()
            return response.json()
        except (httpx.HTTPStatusError, httpx.RequestError) as err:
            status_code = getattr(getattr(err, "response", None), "status_code", None)
            if attempt < max_retries and (
                status_code in (429, 500, 502, 503, 504)
                or isinstance(err, httpx.RequestError)
            ):
                time.sleep(backoff_factor * (2 ** (attempt - 1)))
                continue
            raise err