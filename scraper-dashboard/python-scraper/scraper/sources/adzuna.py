from datetime import datetime, timezone
from urllib.parse import urlsplit, urlunsplit

from scraper.fetching.adzuna_client import search_jobs
from scraper.models.job import RawJob
from scraper.sources.base import JobSourceAdapter


class AdzunaAdapter(JobSourceAdapter):
    source_slug = "adzuna"

    def discover(self, max_pages: int = 5) -> list[dict]:
        all_items: list[dict] = []
        seen_ids: set[str] = set()

        for page in range(1, max_pages + 1):
            try:
                response = search_jobs(page=page)
            except Exception as err:
                print(f"Error fetching page {page}: {err}")
                break

            results = response.get("results", [])
            if not results:
                break

            new_in_page = 0
            for item in results:
                ext_id = self.source_external_id(item)
                if ext_id and ext_id not in seen_ids:
                    seen_ids.add(ext_id)
                    all_items.append(item)
                    new_in_page += 1
                elif not ext_id:
                    all_items.append(item)
                    new_in_page += 1

            if new_in_page == 0:
                break

        return all_items

    def fetch(self, item: dict) -> dict:
        return item

    def parse(self, item: dict) -> RawJob:
        return RawJob(
            source=self.source_slug,
            source_url=item.get("redirect_url", ""),
            external_id=self.source_external_id(item),
            title=item.get("title", ""),
            company=(item.get("company") or {}).get("display_name", ""),
            description=item.get("description", ""),
            location=(item.get("location") or {}).get("display_name", ""),
            location_area=(item.get("location") or {}).get("area", []),
            published_at=item.get("created"),
            fetched_at=datetime.now(timezone.utc).isoformat(),
        )

    def canonicalize_url(self, url: str) -> str:
        p = urlsplit(str(url))
        return urlunsplit((p.scheme, p.netloc, p.path, "", ""))

    def source_external_id(self, raw_job: dict) -> str | None:
        job_id = raw_job.get("id")
        return str(job_id) if job_id is not None else None


if __name__ == "__main__":
    from scraper.normalization.job_normalizer import normalize_job

    adapter = AdzunaAdapter()
    items = adapter.discover()
    print(f"Jobs found: {len(items)}")

    for item in items:
        raw = adapter.parse(adapter.fetch(item))
        job = normalize_job(raw)
        print(
            f"{job.title} | {job.company!r} | {job.city} / {job.state} | "
            f"{job.published_at} | {job.seniority} | {job.work_mode} | {job.technologies}"
        )