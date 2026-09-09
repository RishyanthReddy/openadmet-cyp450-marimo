"""
NCBI Entrez E-Utilities Client for OpenADMET Literature Verification.
Task: Real-time & offline verification of PubMed IDs (PMIDs), DOIs, and bibliographic metadata.
"""

from __future__ import annotations

import datetime
import hashlib
import json
import os
import re
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any

BASE_DIR = Path(__file__).resolve().parent.parent
CACHE_FILE = BASE_DIR / "data" / "packaged" / "ncbi_pubmed_cache.json"
DEFAULT_EUTILS_URL = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"


def _get_env_fallback(key: str, default: str | None = None) -> str | None:
    val = os.getenv(key)
    if val:
        return val
    env_file = BASE_DIR / ".env"
    if env_file.exists():
        try:
            for line in env_file.read_text(encoding="utf-8").splitlines():
                line = line.strip()
                if line.startswith(f"{key}="):
                    return line.split("=", 1)[1].strip().strip('"').strip("'")
        except Exception:
            pass
    return default


class NCBIEntrezClient:
    """Resilient client for NCBI Entrez E-Utilities API with local disk caching."""

    def __init__(
        self,
        api_key: str | None = None,
        email: str | None = None,
        cache_path: Path | None = None,
        timeout: float = 10.0,
    ):
        self.api_key = api_key or _get_env_fallback("NCBI_API_KEY")
        self.email = email or _get_env_fallback("NCBI_EMAIL") or os.environ.get("NCBI_EMAIL", "")
        self.cache_path = cache_path or CACHE_FILE
        self.timeout = timeout
        self._cache: dict[str, dict[str, Any]] = self._load_cache()

    def _load_cache(self) -> dict[str, dict[str, Any]]:
        if self.cache_path and self.cache_path.exists():
            try:
                return json.loads(self.cache_path.read_text(encoding="utf-8"))
            except Exception:
                pass
        try:
            from models.embedded_assets import load_ncbi_pubmed_cache
            return load_ncbi_pubmed_cache()
        except Exception:
            return {}

    def _save_cache(self) -> None:
        if not self.cache_path:
            return
        try:
            self.cache_path.parent.mkdir(parents=True, exist_ok=True)
            tmp_path = self.cache_path.with_suffix(".tmp")
            tmp_path.write_text(json.dumps(self._cache, indent=2), encoding="utf-8")
            os.replace(tmp_path, self.cache_path)
        except (OSError, PermissionError):
            pass

    def fetch_summaries(self, pmids: list[str], force_refresh: bool = False) -> dict[str, dict[str, Any]]:
        """
        Fetch publication summaries for a list of PMIDs via NCBI Entrez E-Utilities.
        Uses local cache unless force_refresh is True or PMIDs are missing from cache.
        """
        results: dict[str, dict[str, Any]] = {}
        missing_pmids: list[str] = []

        for pmid in pmids:
            pmid_clean = str(pmid).strip()
            if not pmid_clean:
                continue
            if not force_refresh and pmid_clean in self._cache:
                results[pmid_clean] = self._cache[pmid_clean]
            else:
                missing_pmids.append(pmid_clean)

        if missing_pmids:
            try:
                live_results = self._query_ncbi(missing_pmids)
                for pmid in missing_pmids:
                    if pmid in live_results:
                        self._cache[pmid] = live_results[pmid]
                        results[pmid] = live_results[pmid]
                    else:
                        results[pmid] = {
                            "pmid": pmid,
                            "title": "NCBI Record Not Found (E-Utilities Partial Response)",
                            "journal": "N/A",
                            "pubdate": "N/A",
                            "doi": None,
                            "authors": [],
                            "author_display": "N/A",
                            "pubmed_url": f"https://pubmed.ncbi.nlm.nih.gov/{pmid}/",
                            "doi_url": None,
                            "ncbi_verified": False,
                            "error": "PMID not present in NCBI ESummary response",
                        }
                self._save_cache()
            except Exception as err:
                # If network fails, return cached records where available
                for pmid in missing_pmids:
                    if pmid in self._cache:
                        results[pmid] = self._cache[pmid]
                    else:
                        results[pmid] = {
                            "pmid": pmid,
                            "title": "NCBI Metadata Unavailable (Network Offline)",
                            "journal": "N/A",
                            "pubdate": "N/A",
                            "doi": None,
                            "authors": [],
                            "author_display": "N/A",
                            "pubmed_url": f"https://pubmed.ncbi.nlm.nih.gov/{pmid}/",
                            "doi_url": None,
                            "ncbi_verified": False,
                            "error": str(err),
                        }

        return results

    def _query_ncbi(self, pmids: list[str]) -> dict[str, dict[str, Any]]:
        params = {
            "db": "pubmed",
            "id": ",".join(pmids),
            "retmode": "json",
            "tool": "OpenADMET",
        }
        if self.email:
            params["email"] = self.email
        if self.api_key:
            params["api_key"] = self.api_key

        url = f"{DEFAULT_EUTILS_URL}/esummary.fcgi?{urllib.parse.urlencode(params)}"
        user_agent = f"OpenADMET-Research/1.0 (mailto:{self.email})" if self.email else "OpenADMET-Research/1.0"
        req = urllib.request.Request(
            url,
            headers={"User-Agent": user_agent},
        )

        with urllib.request.urlopen(req, timeout=self.timeout) as resp:
            data = json.loads(resp.read().decode("utf-8"))

        raw_records = data.get("result", {})
        parsed: dict[str, dict[str, Any]] = {}

        now_utc = datetime.datetime.now(datetime.timezone.utc).isoformat()
        for pmid in pmids:
            rec = raw_records.get(pmid)
            if not rec or "error" in rec:
                continue

            raw_title = rec.get("title", "")
            clean_title = re.sub(r"<[^>]+>", "", raw_title).strip()
            if clean_title.endswith("."):
                clean_title = clean_title[:-1]

            authors = rec.get("authors", [])
            author_names = [a.get("name", "") for a in authors if isinstance(a, dict)]
            if len(author_names) > 1:
                author_display = f"{author_names[0]} et al."
            elif len(author_names) == 1:
                author_display = author_names[0]
            else:
                author_display = "N/A"

            articleids = rec.get("articleids", [])
            doi = next((a.get("value") for a in articleids if isinstance(a, dict) and a.get("idtype") == "doi"), None)

            raw_summary_bytes = json.dumps(
                {
                    "pmid": pmid,
                    "title": clean_title,
                    "journal": rec.get("source", "N/A"),
                    "pubdate": rec.get("pubdate", "N/A"),
                    "doi": doi,
                },
                sort_keys=True,
            ).encode("utf-8")
            prov_hash = hashlib.sha256(raw_summary_bytes).hexdigest()

            parsed[pmid] = {
                "pmid": pmid,
                "title": clean_title,
                "journal": rec.get("source", "N/A"),
                "pubdate": rec.get("pubdate", "N/A"),
                "authors": author_names,
                "author_display": author_display,
                "doi": doi,
                "pubmed_url": f"https://pubmed.ncbi.nlm.nih.gov/{pmid}/",
                "doi_url": f"https://doi.org/{doi}" if doi else None,
                "ncbi_verified": True,
                "retrieved_at_utc": now_utc,
                "source_endpoint": f"{DEFAULT_EUTILS_URL}/esummary.fcgi",
                "provenance_sha256": prov_hash,
            }

        return parsed

    def enrich_mbi_catalog(self, entries: list[dict[str, Any]]) -> list[dict[str, Any]]:
        """Enriches literature MBI reference entries with NCBI verified metadata."""
        pmids = [e.get("pubmed_id") for e in entries if e.get("pubmed_id")]
        summaries = self.fetch_summaries(pmids)

        enriched: list[dict[str, Any]] = []
        for entry in entries:
            item = dict(entry)
            pmid = item.get("pubmed_id")
            if pmid and pmid in summaries:
                s = summaries[pmid]
                item["ncbi_verified"] = s.get("ncbi_verified", False)
                item["ncbi_title"] = s.get("title")
                item["ncbi_journal"] = s.get("journal")
                item["ncbi_pubdate"] = s.get("pubdate")
                item["ncbi_doi"] = s.get("doi")
                item["ncbi_doi_url"] = s.get("doi_url")
                item["ncbi_author_display"] = s.get("author_display")
                item["pubmed_url"] = s.get("pubmed_url")
            enriched.append(item)

        return enriched
