import time
import httpx

BASE_URL = "https://remotive.com/api/remote-jobs"


def search_remotive_jobs(
    category: str = "software-dev",
    limit: int = 15,
    max_retries: int = 3,
    backoff_factor: float = 1.0,
) -> dict:
    params = {
        "category": category,
        "limit": limit,
    }

    for attempt in range(1, max_retries + 1):
        try:
            response = httpx.get(BASE_URL, params=params, timeout=10.0)
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