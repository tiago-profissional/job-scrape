import json
from datetime import datetime, timezone

import pytest

from scraper.models.job import NormalizedJob
from scraper.storage.json_store import (
    StorageError,
    load_jobs,
    persist_jobs,
    persist_raw,
    read_json_list,
    write_json_list,
)

T1 = datetime(2026, 10, 27, 10, 0, tzinfo=timezone.utc)
T2 = datetime(2026, 10, 28, 9, 0, tzinfo=timezone.utc)


def make_job(
    external_id="1",
    title="Desenvolvedor Python",
    description="Vaga para trabalhar com APIs REST.",
    fetched_at=T1,
):
    return NormalizedJob(
        source="adzuna",
        source_url=f"https://www.adzuna.com.br/details/{external_id}?utm_source=email",
        external_id=external_id,
        title=title,
        company="Empresa X",
        description=description,
        city="Fortaleza",
        state="Ceará",
        fetched_at=fetched_at,
    )


def make_batch():
    return [
        make_job("1", title="Desenvolvedor Python"),
        make_job("2", title="Desenvolvedor Java"),
        make_job("3", title="Desenvolvedor Go"),
    ]


# ---------- read / write ----------


def test_write_then_read_gives_the_same_items(tmp_path):
    path = tmp_path / "jobs.json"
    items = [{"id": 1, "title": "Dev"}, {"id": 2, "title": "QA"}]
    write_json_list(path, items)
    assert read_json_list(path) == items


def test_file_is_utf8_readable_and_indented(tmp_path):
    path = tmp_path / "jobs.json"
    write_json_list(path, [{"title": "Estagiário em Ação"}])
    text = path.read_text(encoding="utf-8")
    assert "Estagiário em Ação" in text
    assert "\\u00e1" not in text
    assert "\n  " in text


def test_missing_file_returns_empty_list(tmp_path):
    assert read_json_list(tmp_path / "nope.json") == []


def test_empty_file_returns_empty_list(tmp_path):
    path = tmp_path / "jobs.json"
    path.write_text("  \n", encoding="utf-8")
    assert read_json_list(path) == []


def test_creates_missing_folders(tmp_path):
    path = tmp_path / "data" / "processed" / "jobs.json"
    write_json_list(path, [])
    assert path.exists()


def test_non_list_json_raises(tmp_path):
    path = tmp_path / "jobs.json"
    path.write_text('{"a": 1}', encoding="utf-8")
    with pytest.raises(StorageError):
        read_json_list(path)


def test_failed_write_keeps_old_file_and_leaves_no_temp_files(tmp_path):
    path = tmp_path / "jobs.json"
    write_json_list(path, [{"id": 1}])
    with pytest.raises(TypeError):
        write_json_list(path, [object()])
    assert read_json_list(path) == [{"id": 1}]
    assert [p.name for p in tmp_path.iterdir()] == ["jobs.json"]


# ---------- processed jobs ----------


def test_first_run_adds_jobs_and_stamps_dates(tmp_path):
    path = tmp_path / "jobs.json"
    counts = persist_jobs(path, make_batch(), NormalizedJob, seen_at=T1)
    saved = load_jobs(path, NormalizedJob)
    assert counts == {"added": 3, "updated": 0, "unchanged": 0}
    assert len(saved) == 3
    assert all(job.first_seen_at == T1 and job.last_seen_at == T1 for job in saved)


def test_running_twice_does_not_duplicate_or_lose_data(tmp_path):
    path = tmp_path / "jobs.json"
    persist_jobs(path, make_batch(), NormalizedJob, seen_at=T1)
    # second run: brand-new objects, like a real second execution
    second = persist_jobs(path, make_batch(), NormalizedJob, seen_at=T2)
    saved = load_jobs(path, NormalizedJob)
    assert second == {"added": 0, "updated": 0, "unchanged": 3}
    assert len(saved) == 3
    assert all(job.first_seen_at == T1 for job in saved)
    assert all(job.last_seen_at == T2 for job in saved)
    assert all(job.fetched_at == T1 for job in saved)


def test_previous_jobs_are_kept_when_they_are_not_in_the_new_batch(tmp_path):
    path = tmp_path / "jobs.json"
    persist_jobs(path, [make_job("1"), make_job("2", title="Desenvolvedor Java")], NormalizedJob, seen_at=T1)
    persist_jobs(path, [make_job("3", title="Desenvolvedor Go")], NormalizedJob, seen_at=T2)
    saved = load_jobs(path, NormalizedJob)
    assert sorted(job.external_id for job in saved) == ["1", "2", "3"]
    old = next(job for job in saved if job.external_id == "1")
    assert old.last_seen_at == T1


def test_changed_job_is_updated_not_duplicated(tmp_path):
    path = tmp_path / "jobs.json"
    persist_jobs(path, [make_job("1")], NormalizedJob, seen_at=T1)
    changed = make_job("1", description="Nova descrição, agora com GraphQL.", fetched_at=T2)
    counts = persist_jobs(path, [changed], NormalizedJob, seen_at=T2)
    saved = load_jobs(path, NormalizedJob)
    assert counts == {"added": 0, "updated": 1, "unchanged": 0}
    assert len(saved) == 1
    assert saved[0].description == "Nova descrição, agora com GraphQL."
    assert saved[0].first_seen_at == T1
    assert saved[0].last_seen_at == T2
    assert saved[0].fetched_at == T2


def test_saved_file_keeps_accents_and_url(tmp_path):
    path = tmp_path / "jobs.json"
    persist_jobs(path, [make_job("1")], NormalizedJob, seen_at=T1)
    assert "Ceará" in path.read_text(encoding="utf-8")
    saved = load_jobs(path, NormalizedJob)
    assert str(saved[0].source_url).startswith("https://www.adzuna.com.br/details/1")


def test_corrupt_file_is_not_overwritten(tmp_path):
    path = tmp_path / "jobs.json"
    path.write_text("{not json", encoding="utf-8")
    with pytest.raises(StorageError):
        persist_jobs(path, make_batch(), NormalizedJob, seen_at=T1)
    assert path.read_text(encoding="utf-8") == "{not json"


# ---------- raw payloads ----------


def adzuna_items():
    return [
        {"id": "100", "title": "Estagiário Python", "description": "Vaga 1"},
        {"id": 200, "title": "Desenvolvedor Java", "description": "Vaga 2"},
    ]


def test_raw_first_run_adds_records_with_dates(tmp_path):
    path = tmp_path / "raw.json"
    counts = persist_raw(path, "Adzuna", adzuna_items(), seen_at=T1)
    records = read_json_list(path)
    assert counts == {"added": 2, "updated": 0, "unchanged": 0}
    assert [r["external_id"] for r in records] == ["100", "200"]
    assert all(r["source"] == "adzuna" for r in records)
    assert all(r["first_seen_at"] == r["last_seen_at"] == r["fetched_at"] for r in records)
    assert "Estagiário" in path.read_text(encoding="utf-8")


def test_raw_running_twice_does_not_duplicate(tmp_path):
    path = tmp_path / "raw.json"
    persist_raw(path, "adzuna", adzuna_items(), seen_at=T1)
    second = persist_raw(path, "adzuna", adzuna_items(), seen_at=T2)
    records = read_json_list(path)
    assert second == {"added": 0, "updated": 0, "unchanged": 2}
    assert len(records) == 2
    assert records[0]["first_seen_at"] == T1.isoformat()
    assert records[0]["last_seen_at"] == T2.isoformat()
    assert records[0]["fetched_at"] == T1.isoformat()


def test_raw_changed_payload_is_updated(tmp_path):
    path = tmp_path / "raw.json"
    persist_raw(path, "adzuna", adzuna_items(), seen_at=T1)
    items = adzuna_items()
    items[0]["description"] = "Vaga 1 atualizada"
    counts = persist_raw(path, "adzuna", items, seen_at=T2)
    records = read_json_list(path)
    assert counts == {"added": 0, "updated": 1, "unchanged": 1}
    assert records[0]["payload"]["description"] == "Vaga 1 atualizada"
    assert records[0]["fetched_at"] == T2.isoformat()
    assert records[0]["first_seen_at"] == T1.isoformat()


def test_raw_keeps_old_records_missing_from_new_batch(tmp_path):
    path = tmp_path / "raw.json"
    persist_raw(path, "adzuna", adzuna_items(), seen_at=T1)
    persist_raw(path, "adzuna", [{"id": "300", "title": "Novo"}], seen_at=T2)
    assert [r["external_id"] for r in read_json_list(path)] == ["100", "200", "300"]


def test_raw_item_without_id_is_still_deduplicated(tmp_path):
    path = tmp_path / "raw.json"
    item = {"title": "Sem id", "description": "x"}
    persist_raw(path, "adzuna", [item], seen_at=T1)
    second = persist_raw(path, "adzuna", [dict(item)], seen_at=T2)
    assert second == {"added": 0, "updated": 0, "unchanged": 1}
    assert len(read_json_list(path)) == 1