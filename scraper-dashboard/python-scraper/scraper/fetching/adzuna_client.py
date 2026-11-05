import json
import os
import time
from pathlib import Path

import httpx
from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parents[2]
load_dotenv(ROOT.parent / ".env")

BASE_URL = "https://api.adzuna.com/v1/api/jobs/br/search"


def search_jobs(
    what: str = "desenvolvedor",
    where: str = "Ceará",
    page: int = 1,
    results_per_page: int = 5,
    max_days_old: int = 30,
    max_retries: int = 3,
    backoff_factor: float = 1.0,
) -> dict:
    app_id = os.getenv("ADZUNA_APP_ID")
    app_key = os.getenv("ADZUNA_APP_KEY")
    if not app_id or not app_key:
        raise ValueError("ADZUNA_APP_ID or ADZUNA_APP_KEY is not set.")

    params = {
        "app_id": app_id,
        "app_key": app_key,
        "results_per_page": results_per_page,
        "what": what,
        "where": where,
        "max_days_old": max_days_old,
        "sort_by": "date",
    }
    
    url = f"{BASE_URL}/{page}"
    
    for attempt in range(1, max_retries + 1):
        try:
            response = httpx.get(url, params=params, timeout=10.0)
            response.raise_for_status()
            return response.json()
        except (httpx.HTTPStatusError, httpx.RequestError) as err:
            status_code = getattr(getattr(err, "response", None), "status_code", None)
            if attempt < max_retries and (status_code in (429, 500, 502, 503, 504) or isinstance(err, httpx.RequestError)):
                sleep_time = backoff_factor * (2 ** (attempt - 1))
                time.sleep(sleep_time)
                continue
            raise err


if __name__ == "__main__":
    data = search_jobs()
    print("Jobs returned from Adzuna API:", len(data["results"]))

    output_path = ROOT / "data" / "raw" / "adzuna_jobs.json"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as file:
        json.dump(data, file, ensure_ascii=False, indent=4)
    print(f"Raw response saved to {output_path}")