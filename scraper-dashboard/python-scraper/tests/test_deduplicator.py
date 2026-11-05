from types import SimpleNamespace

from scraper.deduplication.deduplicator import (
    canonical_url,
    canonical_url_key,
    content_hash,
    content_key,
    find_duplicate,
    merge_jobs,
    normalize_key_part,
    source_id_key,
)


def test_lowercase_accents_and_spaces():
    assert normalize_key_part("  Pessoa Desenvolvedora JÚNIOR ") == "pessoa desenvolvedora junior"


def test_none_returns_empty():
    assert normalize_key_part(None) == ""


def test_empty_string_returns_empty():
    assert normalize_key_part("") == ""
    assert normalize_key_part(" ") == ""


def test_removes_accents():
    assert normalize_key_part("Ação") == "acao"


def test_clean_string_stays_the_same():
    assert normalize_key_part("backend python") == "backend python"


def test_url_keeps_non_tracking_params():
    assert canonical_url("https://site.com/job/1?id=5&utm_medium=email") == "https://site.com/job/1?id=5"


def test_url_removes_gclid_and_fbclid():
    assert canonical_url("https://site.com/job/1?gclid=abc&fbclid=def") == "https://site.com/job/1"


def test_url_removes_fragment_and_trailing_slash():
    assert canonical_url("https://site.com/job/1/#apply") == "https://site.com/job/1"


def test_url_empty_returns_empty():
    assert canonical_url(None) == ""
    assert canonical_url("") == ""


def make_job(source="adzuna", external_id="123"):
    return SimpleNamespace(source=source, external_id=external_id)


def test_source_id_key_same_job_gives_same_key():
    assert source_id_key(make_job()) == source_id_key(make_job())


def test_source_id_key_different_source_gives_different_key():
    assert source_id_key(make_job(source="adzuna")) != source_id_key(make_job(source="other"))


def test_source_id_key_ignores_source_case_and_spaces():
    assert source_id_key(make_job(source=" Adzuna ")) == ("adzuna", "123")


def test_source_id_key_converts_numeric_id_to_string():
    assert source_id_key(make_job(external_id=123)) == ("adzuna", "123")


def test_source_id_key_returns_none_without_external_id():
    assert source_id_key(make_job(external_id=None)) is None


def test_source_id_key_returns_none_for_blank_id():
    assert source_id_key(make_job(external_id="   ")) is None


def make_url_job(source_url="https://site.com/job/1"):
    return SimpleNamespace(source_url=source_url)


def test_url_key_ignores_tracking_params():
    a = make_url_job("https://site.com/job/1?utm_source=email&gclid=abc")
    b = make_url_job("https://site.com/job/1")
    assert canonical_url_key(a) == canonical_url_key(b)


def test_url_key_ignores_fragment_slash_and_host_case():
    a = make_url_job("HTTPS://Site.com/job/1/#apply")
    b = make_url_job("https://site.com/job/1")
    assert canonical_url_key(a) == canonical_url_key(b)


def test_url_key_different_jobs_give_different_keys():
    a = make_url_job("https://site.com/job/1")
    b = make_url_job("https://site.com/job/2")
    assert canonical_url_key(a) != canonical_url_key(b)


def test_url_key_returns_none_without_url():
    assert canonical_url_key(make_url_job(None)) is None


def test_url_key_returns_none_for_blank_url():
    assert canonical_url_key(make_url_job("   ")) is None
    
    
def make_content_job(
    company="Empresa X",
    title="Desenvolvedor Python",
    city="Fortaleza",
    state="Ceará",
):
    return SimpleNamespace(company=company, title=title, city=city, state=state)


def test_content_key_same_job_gives_same_key():
    assert content_key(make_content_job()) == content_key(make_content_job())


def test_content_key_ignores_case_accents_and_spaces():
    a = make_content_job("  EMPRESA X ", "Desenvolvedor   Júnior", "FORTALEZA", "CEARÁ")
    b = make_content_job("empresa x", "desenvolvedor junior", "fortaleza", "ceara")
    assert content_key(a) == content_key(b)


def test_content_key_different_title_gives_different_key():
    a = make_content_job(title="Desenvolvedor Python")
    b = make_content_job(title="Desenvolvedor Java")
    assert content_key(a) != content_key(b)


def test_content_key_different_city_gives_different_key():
    a = make_content_job(city="Fortaleza")
    b = make_content_job(city="Recife", state="Pernambuco")
    assert content_key(a) != content_key(b)


def test_content_key_returns_none_without_company():
    assert content_key(make_content_job(company=None)) is None


def test_content_key_returns_none_without_title():
    assert content_key(make_content_job(title="  ")) is None


def test_content_key_allows_missing_location():
    job = make_content_job(city=None, state=None)
    assert content_key(job) == ("empresa x", "desenvolvedor python", "", "")
    
    
    


def make_hash_job(
    title="Desenvolvedor Python",
    company="Empresa X",
    description="Vaga para trabalhar com APIs REST.",
    city="Fortaleza",
    state="Ceará",
    fetched_at="2026-10-27T10:00:00Z",
):
    return SimpleNamespace(
        title=title,
        company=company,
        description=description,
        city=city,
        state=state,
        fetched_at=fetched_at,
    )


def test_content_hash_same_job_gives_same_hash():
    assert content_hash(make_hash_job()) == content_hash(make_hash_job())


def test_content_hash_ignores_case_accents_and_spaces():
    a = make_hash_job(description="  Vaga   para APIs REST.\n")
    b = make_hash_job(description="vaga para apis rest.")
    assert content_hash(a) == content_hash(b)


def test_content_hash_changes_when_description_changes():
    a = make_hash_job(description="Vaga para trabalhar com APIs REST.")
    b = make_hash_job(description="Vaga para trabalhar com GraphQL.")
    assert content_hash(a) != content_hash(b)


def test_content_hash_changes_when_title_changes():
    a = make_hash_job(title="Desenvolvedor Python")
    b = make_hash_job(title="Desenvolvedor Java")
    assert content_hash(a) != content_hash(b)


def test_content_hash_ignores_fetched_at():
    a = make_hash_job(fetched_at="2026-10-27T10:00:00Z")
    b = make_hash_job(fetched_at="2026-10-28T09:30:00Z")
    assert content_hash(a) == content_hash(b)


def test_content_hash_is_64_hex_characters():
    result = content_hash(make_hash_job())
    assert len(result) == 64
    assert all(c in "0123456789abcdef" for c in result)
    
    
    
def make_full_job(
    source="adzuna",
    external_id="1",
    source_url="https://site.com/job/1",
    company="Empresa X",
    title="Desenvolvedor Python",
    city="Fortaleza",
    state="Ceará",
):
    return SimpleNamespace(
        source=source,
        external_id=external_id,
        source_url=source_url,
        company=company,
        title=title,
        city=city,
        state=state,
    )


def test_find_duplicate_empty_list_returns_none():
    assert find_duplicate(make_full_job(), []) is None


def test_find_duplicate_by_source_and_id():
    existing = make_full_job(source_url="https://other.com/x", company="Outra", title="Outro")
    assert find_duplicate(make_full_job(), [existing]) is existing


def test_find_duplicate_by_canonical_url():
    existing = make_full_job(
        external_id="2",
        source_url="https://site.com/job/1?utm_source=x",
        company="Outra",
        title="Outro",
    )
    assert find_duplicate(make_full_job(), [existing]) is existing


def test_find_duplicate_by_content_across_sources():
    existing = make_full_job(source="other", external_id="9", source_url="https://other.com/9")
    assert find_duplicate(make_full_job(), [existing]) is existing


def test_find_duplicate_different_job_returns_none():
    existing = make_full_job(
        external_id="2",
        source_url="https://site.com/job/2",
        title="Desenvolvedor Java",
    )
    assert find_duplicate(make_full_job(), [existing]) is None


def test_find_duplicate_missing_keys_never_match():
    job = make_full_job(external_id=None, source_url=None, company=None)
    existing = make_full_job(external_id=None, source_url=None, company=None)
    assert find_duplicate(job, [existing]) is None


def test_find_duplicate_source_id_wins_over_content():
    content_match = make_full_job(source="other", external_id="9", source_url="https://other.com/9")
    id_match = make_full_job(source_url="https://x.com/z", company="Outra", title="Outro")
    assert find_duplicate(make_full_job(), [content_match, id_match]) is id_match
    
    
    
    
def make_merge_job(
    external_id="1",
    title="Desenvolvedor Python",
    description="Vaga para trabalhar com APIs REST.",
    fetched_at="2026-10-27T10:00:00Z",
):
    return SimpleNamespace(
        source="adzuna",
        external_id=external_id,
        source_url=f"https://site.com/job/{external_id}",
        company="Empresa X",
        title=title,
        description=description,
        city="Fortaleza",
        state="Ceará",
        fetched_at=fetched_at,
    )


def test_merge_adds_new_job():
    existing = []
    result = merge_jobs(existing, [make_merge_job()])
    assert len(existing) == 1
    assert result == {"added": 1, "updated": 0, "unchanged": 0}


def test_merge_same_job_is_not_added_twice():
    existing = [make_merge_job()]
    result = merge_jobs(existing, [make_merge_job(fetched_at="2026-10-28T09:00:00Z")])
    assert len(existing) == 1
    assert result == {"added": 0, "updated": 0, "unchanged": 1}


def test_merge_updates_job_when_content_changed():
    existing = [make_merge_job()]
    changed = make_merge_job(description="Nova descrição, agora com GraphQL.")
    result = merge_jobs(existing, [changed])
    assert len(existing) == 1
    assert existing[0].description == "Nova descrição, agora com GraphQL."
    assert result == {"added": 0, "updated": 1, "unchanged": 0}


def test_merge_unchanged_job_keeps_its_old_fetched_at():
    existing = [make_merge_job(fetched_at="2026-10-27T10:00:00Z")]
    merge_jobs(existing, [make_merge_job(fetched_at="2026-10-28T09:00:00Z")])
    assert existing[0].fetched_at == "2026-10-27T10:00:00Z"


def test_merge_updated_job_gets_new_fetched_at():
    existing = [make_merge_job(fetched_at="2026-10-27T10:00:00Z")]
    changed = make_merge_job(title="Desenvolvedor Python Sênior", fetched_at="2026-10-28T09:00:00Z")
    merge_jobs(existing, [changed])
    assert existing[0].fetched_at == "2026-10-28T09:00:00Z"


def test_merge_duplicate_inside_same_batch_is_added_once():
    existing = []
    result = merge_jobs(existing, [make_merge_job(), make_merge_job()])
    assert len(existing) == 1
    assert result == {"added": 1, "updated": 0, "unchanged": 1}

def test_running_twice_does_not_duplicate():
    # Etapa 10 "Concluído quando": executar duas vezes não duplica as vagas
    existing = []
    batch = [
        make_merge_job("1", title="Desenvolvedor Python"),
        make_merge_job("2", title="Desenvolvedor Java"),
        make_merge_job("3", title="Desenvolvedor Go"),
    ]
    first = merge_jobs(existing, batch)
    second = merge_jobs(existing, batch)
    assert len(existing) == 3
    assert first["added"] == 3
    assert second == {"added": 0, "updated": 0, "unchanged": 3}