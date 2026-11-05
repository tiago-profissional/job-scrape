import hashlib
import unicodedata
from datetime import datetime
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit


def normalize_key_part(text: str | None) -> str:
    """Clean text for comparison only (never shown to users)."""
    if not text:
        return ""

    decomposed = unicodedata.normalize("NFKD", text.lower())

    without_accents = "".join(
        c for c in decomposed if not unicodedata.combining(c)
    )

    return " ".join(without_accents.split())


TRACKING_PARAMS = {"gclid", "fbclid", "msclkid"}


def _is_tracking(name: str) -> bool:
    name = name.lower()
    return name.startswith("utm_") or name in TRACKING_PARAMS


def strip_tracking_params(url: str) -> str:
    """Remove tracking params (utm_*, gclid...) and keep the meaningful ones."""
    parts = urlsplit(url)
    kept = [
        (k, v)
        for k, v in parse_qsl(parts.query, keep_blank_values=True)
        if not _is_tracking(k)
    ]
    return urlunsplit(
        (parts.scheme, parts.netloc, parts.path, urlencode(kept), parts.fragment)
    )


def canonical_url(url: str | None) -> str:
    """One standard form per job URL, used only for comparison."""
    if url is None:
        return ""
    url = str(url).strip()
    if not url:
        return ""

    parts = urlsplit(strip_tracking_params(url.strip()))
    path = parts.path.rstrip("/") or "/"
    query = urlencode(sorted(parse_qsl(parts.query, keep_blank_values=True)))
    return urlunsplit(
        (parts.scheme.lower(), parts.netloc.lower(), path, query, "")
    )


def source_id_key(job) -> tuple[str, str] | None:
    source = (job.source or "").strip().lower()
    external_id = "" if job.external_id is None else str(job.external_id).strip()
    if not source or not external_id:
        return None
    return (source, external_id)


def canonical_url_key(job) -> str | None:
    return canonical_url(job.source_url) or None


def content_key(job) -> tuple[str, str, str, str] | None:
    company = normalize_key_part(job.company)
    title = normalize_key_part(job.title)
    if not company or not title:
        return None
    return (
        company,
        title,
        normalize_key_part(job.city),
        normalize_key_part(job.state),
    )


def content_hash(job) -> str:
    parts = [
        normalize_key_part(job.title),
        normalize_key_part(job.company),
        normalize_key_part(job.description),
        normalize_key_part(job.city),
        normalize_key_part(job.state),
    ]
    return hashlib.sha256("\x1f".join(parts).encode("utf-8")).hexdigest()


def find_duplicate(job, existing_jobs):
    job_src_id = source_id_key(job)
    job_url_key = canonical_url_key(job)
    job_content = content_key(job)

    if job_src_id is not None:
        for existing in existing_jobs:
            if source_id_key(existing) == job_src_id:
                return existing

    if job_url_key is not None:
        for existing in existing_jobs:
            if canonical_url_key(existing) == job_url_key:
                return existing

    if job_content is not None:
        for existing in existing_jobs:
            if content_key(existing) == job_content:
                return existing

    return None


UPDATABLE_FIELDS = ("title", "company", "description", "city", "state", "fetched_at")


def merge_jobs(
    existing_jobs: list,
    new_jobs: list,
    seen_at: datetime | str | None = None,
) -> dict[str, int]:
    counts = {"added": 0, "updated": 0, "unchanged": 0}

    for new_job in new_jobs:
        dup = find_duplicate(new_job, existing_jobs)
        if dup is None:
            if seen_at is not None:
                new_job.first_seen_at = seen_at
                new_job.last_seen_at = seen_at
            existing_jobs.append(new_job)
            counts["added"] += 1
        else:
            if seen_at is not None:
                dup.last_seen_at = seen_at

            new_h = getattr(new_job, "content_hash", None) or content_hash(new_job)
            old_h = getattr(dup, "content_hash", None) or content_hash(dup)

            if new_h == old_h:
                counts["unchanged"] += 1
            else:
                for field in UPDATABLE_FIELDS:
                    setattr(dup, field, getattr(new_job, field))
                counts["updated"] += 1

    return counts