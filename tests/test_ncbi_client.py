"""
Unit and integration tests for NCBI Entrez E-Utilities client and PubMed verification.
Verifies:
  1. Disk cache integrity, schema validation, and complete PMID coverage.
  2. Offline resilience and embedded fallback when disk cache is absent.
  3. Batch summary retrieval and zero-network performance on cached PMIDs.
  4. MBI reference catalog enrichment with peer-reviewed bibliographic metadata.
  5. Exact parity between embedded assets and disk artifacts.
"""

import json
import sys
from pathlib import Path
import pytest

BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from models.ncbi_client import NCBIEntrezClient
from models.embedded_assets import (
    load_literature_mbi_reference_set,
    load_ncbi_pubmed_cache,
)

BASE_DIR = Path(__file__).resolve().parent.parent
CACHE_FILE = BASE_DIR / "data" / "packaged" / "ncbi_pubmed_cache.json"

EXPECTED_PMIDS = {
    "9652662",   # Mibefradil (Lancet)
    "10454485",  # Diltiazem (J Pharmacol Exp Ther)
    "12584155",  # Paroxetine (Drug Metab Dispos)
    "9548795",   # Bergamottin (Chem Res Toxicol)
    "9394031",   # Methoxsalen (Drug Metab Dispos)
    "8286335",   # Tienilic acid (Biochemistry)
    "21363997",  # Lapatinib (Drug Metab Dispos)
    "14563790",  # Clopidogrel (J Pharmacol Exp Ther)
    "15257612",  # Raloxifene (Chem Res Toxicol)
    "7975717",   # Furafylline (Xenobiotica)
}


def test_ncbi_cache_file_integrity():
    """Verify that the NCBI PubMed disk cache exists, is non-empty, and covers all 10 MBIs."""
    assert CACHE_FILE.exists(), f"NCBI cache file not found at {CACHE_FILE}"
    cache_data = json.loads(CACHE_FILE.read_text(encoding="utf-8"))
    assert isinstance(cache_data, dict)
    assert len(cache_data) >= 10

    cached_pmids = set(cache_data.keys())
    missing_pmids = EXPECTED_PMIDS - cached_pmids
    assert not missing_pmids, f"Cache missing expected reference PMIDs: {missing_pmids}"

    for pmid in EXPECTED_PMIDS:
        rec = cache_data[pmid]
        assert rec["pmid"] == pmid
        assert isinstance(rec["title"], str) and len(rec["title"]) > 10
        assert isinstance(rec["journal"], str) and len(rec["journal"]) > 0
        assert isinstance(rec["pubdate"], str) and len(rec["pubdate"]) > 0
        assert isinstance(rec["authors"], list) and len(rec["authors"]) > 0
        assert isinstance(rec["author_display"], str) and len(rec["author_display"]) > 0
        assert rec["pubmed_url"] == f"https://pubmed.ncbi.nlm.nih.gov/{pmid}/"
        assert rec["ncbi_verified"] is True


def test_ncbi_client_cached_fetch():
    """Verify that NCBIEntrezClient retrieves cached summaries with zero network latency."""
    client = NCBIEntrezClient(cache_path=CACHE_FILE)
    results = client.fetch_summaries(list(EXPECTED_PMIDS), force_refresh=False)

    assert len(results) == len(EXPECTED_PMIDS)
    assert results["9652662"]["journal"] == "Lancet"
    assert "mibefradil" in results["9652662"]["title"].lower()
    assert results["15257612"]["journal"] == "Chem Res Toxicol"
    assert "raloxifene" in results["15257612"]["title"].lower()
    assert results["8286335"]["journal"] == "Biochemistry"


def test_ncbi_client_embedded_fallback():
    """Verify that NCBIEntrezClient falls back to embedded assets when cache file is absent."""
    nonexistent_path = BASE_DIR / "data" / "packaged" / "does_not_exist.json"
    client = NCBIEntrezClient(cache_path=nonexistent_path)

    # Should have loaded from embedded assets
    assert len(client._cache) >= 10
    results = client.fetch_summaries(["9652662"])
    assert "9652662" in results
    assert results["9652662"]["ncbi_verified"] is True
    assert results["9652662"]["journal"] == "Lancet"


def test_ncbi_client_offline_resilience_on_uncached_pmid():
    """Verify that queries for un-cached PMIDs when network is disabled return structured fallback."""
    # Use dummy cache path and invalid base URL to force offline error handling
    client = NCBIEntrezClient(cache_path=BASE_DIR / "tmp_nonexistent.json", timeout=0.1)
    # Point to invalid port to force connection failure
    import models.ncbi_client
    orig_url = models.ncbi_client.DEFAULT_EUTILS_URL
    models.ncbi_client.DEFAULT_EUTILS_URL = "http://127.0.0.1:1"
    try:
        results = client.fetch_summaries(["99999999"])
        assert "99999999" in results
        fallback = results["99999999"]
        assert fallback["ncbi_verified"] is False
        assert "Offline" in fallback["title"]
        assert fallback["pubmed_url"] == "https://pubmed.ncbi.nlm.nih.gov/99999999/"
    finally:
        models.ncbi_client.DEFAULT_EUTILS_URL = orig_url


def test_enrich_mbi_catalog():
    """Verify that enrich_mbi_catalog correctly injects NCBI metadata into reference entries."""
    client = NCBIEntrezClient(cache_path=CACHE_FILE)
    test_entries = [
        {"name": "Mibefradil", "pubmed_id": "9652662"},
        {"name": "Raloxifene", "pubmed_id": "15257612"},
        {"name": "Unknown", "pubmed_id": None},
    ]

    enriched = client.enrich_mbi_catalog(test_entries)
    assert len(enriched) == 3

    mibe = next(e for e in enriched if e["name"] == "Mibefradil")
    assert mibe["ncbi_verified"] is True
    assert mibe["ncbi_journal"] == "Lancet"
    assert mibe["ncbi_doi"] == "10.1016/s0140-6736(05)78800-0"
    assert mibe["pubmed_url"] == "https://pubmed.ncbi.nlm.nih.gov/9652662/"

    ralox = next(e for e in enriched if e["name"] == "Raloxifene")
    assert ralox["ncbi_verified"] is True
    assert ralox["ncbi_journal"] == "Chem Res Toxicol"

    unknown = next(e for e in enriched if e["name"] == "Unknown")
    assert "ncbi_verified" not in unknown


def test_literature_mbi_reference_set_ncbi_parity():
    """Verify that load_literature_mbi_reference_set has verified NCBI metadata for all 10 compounds."""
    mbi_data = load_literature_mbi_reference_set()
    assert mbi_data.get("metadata", {}).get("ncbi_enriched") is True

    entries = mbi_data.get("entries", [])
    assert len(entries) == 10

    for entry in entries:
        assert entry.get("ncbi_verified") is True, f"{entry['name']} missing ncbi_verified=True"
        assert entry.get("ncbi_journal"), f"{entry['name']} missing ncbi_journal"
        assert entry.get("ncbi_title"), f"{entry['name']} missing ncbi_title"
        assert entry.get("pubmed_id") in EXPECTED_PMIDS, f"{entry['name']} pmid unexpected"


def test_embedded_ncbi_pubmed_cache_parity():
    """Verify that the embedded NCBI cache exactly matches the disk artifact."""
    disk_cache = json.loads(CACHE_FILE.read_text(encoding="utf-8"))
    embedded_cache = load_ncbi_pubmed_cache()

    assert set(disk_cache.keys()) == set(embedded_cache.keys())
    for pmid in disk_cache:
        assert disk_cache[pmid]["title"] == embedded_cache[pmid]["title"]
        assert disk_cache[pmid]["journal"] == embedded_cache[pmid]["journal"]
        assert disk_cache[pmid]["pubdate"] == embedded_cache[pmid]["pubdate"]
        assert disk_cache[pmid]["ncbi_verified"] == embedded_cache[pmid]["ncbi_verified"]


def test_ncbi_provenance_metadata_and_hash():
    """Verify that cache records contain retrieval timestamp, endpoint, and sha256 provenance hash."""
    cache = json.loads(CACHE_FILE.read_text(encoding="utf-8"))
    for pmid, rec in cache.items():
        assert "retrieved_at_utc" in rec, f"Missing retrieved_at_utc for {pmid}"
        assert rec["source_endpoint"] == "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi"
        assert "provenance_sha256" in rec and len(rec["provenance_sha256"]) == 64


def test_ncbi_partial_response_handling(tmp_path):
    """Verify that partial ESummary responses return structured fallback records without omitting keys or raising."""
    client = NCBIEntrezClient(cache_path=tmp_path / "cache.json")
    mock_record = {
        "pmid": "9652662",
        "title": "Mibefradil withdrawal",
        "journal": "Lancet",
        "pubdate": "1998",
        "authors": ["A"],
        "author_display": "A",
        "doi": "10.1016/s0140-6736",
        "pubmed_url": "https://pubmed.ncbi.nlm.nih.gov/9652662/",
        "doi_url": "https://doi.org/10.1016/s0140-6736",
        "ncbi_verified": True,
    }
    # Mock _query_ncbi to return only 1 of 2 requested PMIDs
    client._query_ncbi = lambda pmids: {"9652662": mock_record}

    res = client.fetch_summaries(["9652662", "9999999"], force_refresh=True)
    assert "9652662" in res
    assert res["9652662"]["ncbi_verified"] is True

    assert "9999999" in res
    assert res["9999999"]["ncbi_verified"] is False
    assert "error" in res["9999999"]
    assert "Partial Response" in res["9999999"]["title"]


def test_ncbi_no_hardcoded_personal_credentials(monkeypatch):
    """Verify that NCBIEntrezClient does not have hardcoded personal credentials in default fallbacks."""
    monkeypatch.setattr("models.ncbi_client._get_env_fallback", lambda k, default=None: None)
    monkeypatch.delenv("NCBI_EMAIL", raising=False)
    monkeypatch.delenv("NCBI_API_KEY", raising=False)

    client = NCBIEntrezClient(email=None, cache_path=Path("/tmp/fake_cache.json"))
    assert "@gmail.com" not in (client.email or "")
    assert client.email == "" or client.email is None


def test_ncbi_doi_coverage_exact_eight_of_ten():
    """Verify empirical PubMed DOI coverage: exactly 8/10 curated PMIDs have DOIs, and 10/10 have PubMed URLs."""
    cache = json.loads(CACHE_FILE.read_text(encoding="utf-8"))
    curated_records = [cache[p] for p in EXPECTED_PMIDS if p in cache]
    assert len(curated_records) == 10

    with_doi = [r for r in curated_records if r.get("doi") is not None]
    without_doi = [r for r in curated_records if r.get("doi") is None]

    assert len(with_doi) == 8, f"Expected exactly 8 PMIDs with DOIs, got {len(with_doi)}"
    assert len(without_doi) == 2, f"Expected exactly 2 PMIDs without DOIs, got {len(without_doi)}"

    # Specific historical PMIDs without digital DOIs in PubMed
    no_doi_pmids = {r["pmid"] for r in without_doi}
    assert no_doi_pmids == {"10454485", "9394031"}

    # All 10 must have PubMed URLs
    for r in curated_records:
        assert r["pubmed_url"].startswith("https://pubmed.ncbi.nlm.nih.gov/")
        assert r["ncbi_verified"] is True
