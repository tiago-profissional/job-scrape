"""Step 11: save raw payloads and normalized jobs as JSON.

UTF-8, readable, atomic writes, and a file we can't read is never overwritten.
"""
import hashlib
import json
import os
import tempfile
from datetime import datetime, timezone
from pathlib import Path

from scraper.deduplication.deduplicator import merge_jobs

DATA_DIR = Path(__file__).resolve().parents[2] / "data"
RAW_JOBS_PATH = DATA_DIR / "raw" / "jobs.json"
PROCESSED_JOBS_PATH = DATA_DIR / "processed" / "jobs.json"


class StorageError(Exception):
    """The JSON file exists but can't be trusted (corrupt or wrong shape)."""


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def read_json_list(path) -> list:
    path = Path(path)

    if not path.exists():
        return []

    content = path.read_text(encoding="utf-8")

    if not content.strip():
        return []

    try:
        data = json.loads(content)
    except json.JSONDecodeError as exc:
        raise StorageError(f"JSON inválido no arquivo: {path}") from exc

    if not isinstance(data, list):
        raise StorageError(f"O JSON no arquivo {path} não é uma lista.")

    return data


def write_json_list(path, items: list) -> None:
    """Write a list as readable UTF-8 JSON, atomically.

    - creates missing parent folders
    - accents stay readable, indent=2, "\\n" line endings, final newline
    - writes to a temp file in the SAME folder, then os.replace over the real file
    - on any failure: old file untouched, no temp file left, exception re-raised
    - the temp file is read back before replacing the real one
    """
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)

    temp_path = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="w",
            encoding="utf-8",
            newline="\n",
            dir=path.parent,
            delete=False,
        ) as temp_file:
            temp_path = Path(temp_file.name)
            json.dump(items, temp_file, ensure_ascii=False, indent=2)
            temp_file.write("\n")

        with open(temp_path, "r", encoding="utf-8") as file:
            json.load(file)

        os.replace(temp_path, path)
    except Exception:
        if temp_path is not None:
            try:
                temp_path.unlink(missing_ok=True)
            except OSError:
                pass
        raise


def load_jobs(path, model) -> list:
    return [model.model_validate(item) for item in read_json_list(path)]


def save_jobs(path, jobs: list) -> None:
    write_json_list(path, [job.model_dump(mode="json") for job in jobs])


def persist_jobs(path, jobs: list, model, seen_at=None) -> dict[str, int]:
    """Load saved jobs, merge the new ones, save. Safe to run many times."""
    seen_at = seen_at or utc_now()
    existing = load_jobs(path, model)
    counts = merge_jobs(existing, jobs, seen_at=seen_at)
    save_jobs(path, existing)
    return counts


def _stamp(value) -> str:
    return value if isinstance(value, str) else value.isoformat()


def persist_raw(path, source: str, items: list[dict], seen_at=None, id_key="id") -> dict[str, int]:
    """Keep the original payloads, one record per (source, external_id)."""
    stamp = _stamp(seen_at or utc_now())
    source = source.strip().lower()
    records = read_json_list(path)
    by_key = {(r["source"], r["external_id"]): r for r in records}
    counts = {"added": 0, "updated": 0, "unchanged": 0}

    for item in items:
        raw_id = item.get(id_key)
        if raw_id is None:  # no id: fall back to a hash of the payload
            blob = json.dumps(item, sort_keys=True, ensure_ascii=False)
            external_id = "sha256:" + hashlib.sha256(blob.encode("utf-8")).hexdigest()
        else:
            external_id = str(raw_id).strip()

        saved = by_key.get((source, external_id))
        if saved is None:
            record = {
                "source": source,
                "external_id": external_id,
                "first_seen_at": stamp,
                "last_seen_at": stamp,
                "fetched_at": stamp,
                "payload": item,
            }
            records.append(record)
            by_key[(source, external_id)] = record
            counts["added"] += 1
            continue

        saved["last_seen_at"] = stamp
        if saved["payload"] == item:
            counts["unchanged"] += 1
        else:
            saved["payload"] = item
            saved["fetched_at"] = stamp
            counts["updated"] += 1

    write_json_list(path, records)
    return counts