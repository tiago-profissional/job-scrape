from datetime import datetime, timezone
from urllib.parse import urlsplit, urlunsplit

from scraper.fetching.arbeitnow_client import search_arbeitnow_jobs
from scraper.models.job import RawJob
from scraper.sources.base import JobSourceAdapter


class ArbeitnowAdapter(JobSourceAdapter):
    source_slug = "arbeitnow"

    def discover(self, page: int = 1) -> list[dict]:
        try:
            data = search_arbeitnow_jobs(page=page)
            return data.get("data", [])
        except Exception as err:
            print(f"Error fetching Arbeitnow jobs: {err}")
            return []

    def fetch(self, item: dict) -> dict:
        return item

    def parse(self, item: dict) -> RawJob:
        created_at = item.get("created_at")
        published_at_str = str(created_at) if created_at is not None else None

        return RawJob(
            source=self.source_slug,
            source_url=item.get("url", ""),
            external_id=self.source_external_id(item),
            title=item.get("title", ""),
            company=item.get("company_name", ""),
            description=item.get("description", ""),
            location=item.get("location", "Remote"),
            location_area=[],
            published_at=published_at_str,
            fetched_at=datetime.now(timezone.utc).isoformat(),
        )

    def canonicalize_url(self, url: str) -> str:
        p = urlsplit(str(url))
        return urlunsplit((p.scheme, p.netloc, p.path, "", ""))

    def source_external_id(self, raw_job: dict) -> str | None:
        job_id = raw_job.get("slug")
        return str(job_id) if job_id is not None else None