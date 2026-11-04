"""Literature search: arXiv + OpenAlex (both free, no keys needed)."""
import os
import re
import xml.etree.ElementTree as ET

import requests

ARXIV_API = "http://export.arxiv.org/api/query"
OPENALEX_API = "https://api.openalex.org/works"
NS = {"a": "http://www.w3.org/2005/Atom"}


def search_arxiv(query: str, limit: int = 5):
    r = requests.get(
        ARXIV_API,
        params={"search_query": f"all:{query}", "start": 0, "max_results": limit,
                "sortBy": "relevance"},
        timeout=30,
    )
    r.raise_for_status()
    root = ET.fromstring(r.text)
    papers = []
    for e in root.findall("a:entry", NS):
        papers.append({
            "title": " ".join(e.findtext("a:title", "", NS).split()),
            "authors": [a.findtext("a:name", "", NS) for a in e.findall("a:author", NS)],
            "year": int(e.findtext("a:published", "0000", NS)[:4]),
            "abstract": " ".join(e.findtext("a:summary", "", NS).split()),
            "url": e.findtext("a:id", "", NS),
            "venue": "arXiv",
            "doi": "",
            "source": "arXiv",
        })
    return papers


def _inverted_to_text(inv):
    if not inv:
        return ""
    words = {}
    for word, positions in inv.items():
        for p in positions:
            words[p] = word
    return " ".join(words[i] for i in sorted(words))


def search_openalex(query: str, limit: int = 5):
    params = {"search": query, "per-page": limit}
    if os.getenv("OPENALEX_EMAIL"):
        params["mailto"] = os.getenv("OPENALEX_EMAIL")
    r = requests.get(OPENALEX_API, params=params, timeout=30)
    r.raise_for_status()
    papers = []
    for w in r.json().get("results", []):
        loc = w.get("primary_location") or {}
        src = loc.get("source") or {}
        papers.append({
            "title": w.get("title") or "Untitled",
            "authors": [a["author"]["display_name"] for a in w.get("authorships", [])][:8],
            "year": w.get("publication_year") or 0,
            "abstract": _inverted_to_text(w.get("abstract_inverted_index")),
            "url": w.get("doi") or w.get("id"),
            "venue": src.get("display_name") or "",
            "doi": (w.get("doi") or "").replace("https://doi.org/", ""),
            "source": "OpenAlex",
        })
    return papers


def _norm(t):
    return re.sub(r"[^a-z0-9]", "", t.lower())


def search_all(queries, per_query=4, sources=("arXiv", "OpenAlex")):
    seen, results = set(), []
    for q in queries:
        batch = []
        try:
            if "arXiv" in sources:
                batch += search_arxiv(q, per_query)
        except Exception as ex:
            print(f"arXiv error: {ex}")
        try:
            if "OpenAlex" in sources:
                batch += search_openalex(q, per_query)
        except Exception as ex:
            print(f"OpenAlex error: {ex}")
        for p in batch:
            key = _norm(p["title"])
            if key and key not in seen and p["abstract"]:
                seen.add(key)
                results.append(p)
    return results
