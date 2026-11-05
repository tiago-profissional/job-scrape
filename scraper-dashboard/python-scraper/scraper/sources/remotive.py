from datetime import datetime, timezone
from urllib.parse import urlsplit, urlunsplit

from scraper.fetching.remotive_client import search_remotive_jobs
from scraper.models.job import RawJob
from scraper.sources.base import JobSourceAdapter


class RemotiveAdapter(JobSourceAdapter):
    source_slug = "remotive"

    def discover(self, limit: int = 15) -> list[dict]:
        try:
            response = search_remotive_jobs(limit=limit)
            return response.get("jobs", [])
        except Exception as err:
            print(f"Error fetching Remotive jobs: {err}")
            return []

    def fetch(self, item: dict) -> dict:
        return item

    def parse(self, item: dict) -> RawJob:
        return RawJob(
            source=self.source_slug,
            source_url=item.get("url", ""),
            external_id=self.source_external_id(item),
            title=item.get("title", ""),
            company=item.get("company_name", ""),
            description=item.get("description", ""),
            location=item.get("candidate_required_location", "Remote"),
            location_area=[],
            published_at=item.get("publication_date"),
            fetched_at=datetime.now(timezone.utc).isoformat(),
        )

    def canonicalize_url(self, url: str) -> str:
        p = urlsplit(str(url))
        return urlunsplit((p.scheme, p.netloc, p.path, "", ""))

    def source_external_id(self, raw_job: dict) -> str | None:
        job_id = raw_job.get("id")
        return str(job_id) if job_id is not None else None