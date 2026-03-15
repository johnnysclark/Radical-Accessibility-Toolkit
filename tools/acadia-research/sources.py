"""Source adapters for academic research APIs and local docs.

Fetches papers from Semantic Scholar, arXiv, and local project docs.
Uses only Python stdlib (urllib, xml, json) -- no pip dependencies.
"""

import json
import os
import re
import time
import urllib.request
import urllib.parse
import urllib.error
import xml.etree.ElementTree as ET


def _http_get(url, retries=3, backoff=2):
    """GET with retry and exponential backoff."""
    for attempt in range(retries):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "AcadiaResearchAgent/1.0"})
            with urllib.request.urlopen(req, timeout=30) as resp:
                return resp.read().decode("utf-8")
        except (urllib.error.URLError, urllib.error.HTTPError, OSError) as exc:
            if attempt == retries - 1:
                return None
            time.sleep(backoff ** attempt)
    return None


# -- Semantic Scholar ----------------------------------------------------------

def search_semantic_scholar(query, max_results=10, fields=None):
    """Search Semantic Scholar for papers matching query.

    Returns list of dicts with keys: source, paper_id, title, authors, year,
    abstract, citation_count, venue, url.
    """
    if fields is None:
        fields = "title,abstract,authors,year,citationCount,externalIds,url,venue"
    params = urllib.parse.urlencode({
        "query": query,
        "limit": max_results,
        "fields": fields,
    })
    url = "https://api.semanticscholar.org/graph/v1/paper/search?{}".format(params)
    body = _http_get(url)
    if body is None:
        return []
    try:
        data = json.loads(body)
    except json.JSONDecodeError:
        return []
    results = []
    for paper in data.get("data", []):
        authors = [a.get("name", "") for a in paper.get("authors", [])]
        ext_ids = paper.get("externalIds") or {}
        doi = ext_ids.get("DOI", "")
        results.append({
            "source": "semantic_scholar",
            "paper_id": paper.get("paperId", ""),
            "title": paper.get("title", ""),
            "authors": authors,
            "year": paper.get("year"),
            "abstract": (paper.get("abstract") or "")[:500],
            "citation_count": paper.get("citationCount", 0),
            "venue": paper.get("venue", ""),
            "url": paper.get("url", ""),
            "doi": doi,
        })
    return results


# -- arXiv ---------------------------------------------------------------------

def search_arxiv(query, max_results=10):
    """Search arXiv for papers matching query.

    Returns list of dicts with keys: source, paper_id, title, authors, year,
    abstract, url.
    """
    params = urllib.parse.urlencode({
        "search_query": "all:{}".format(query),
        "start": 0,
        "max_results": max_results,
        "sortBy": "relevance",
    })
    url = "http://export.arxiv.org/api/query?{}".format(params)
    body = _http_get(url)
    if body is None:
        return []
    try:
        root = ET.fromstring(body)
    except ET.ParseError:
        return []
    ns = {"atom": "http://www.w3.org/2005/Atom"}
    results = []
    for entry in root.findall("atom:entry", ns):
        title_el = entry.find("atom:title", ns)
        summary_el = entry.find("atom:summary", ns)
        published_el = entry.find("atom:published", ns)
        id_el = entry.find("atom:id", ns)
        title = title_el.text.strip() if title_el is not None else ""
        abstract = summary_el.text.strip()[:500] if summary_el is not None else ""
        paper_url = id_el.text.strip() if id_el is not None else ""
        year = None
        if published_el is not None and published_el.text:
            year_match = re.match(r"(\d{4})", published_el.text)
            if year_match:
                year = int(year_match.group(1))
        authors = []
        for author_el in entry.findall("atom:author", ns):
            name_el = author_el.find("atom:name", ns)
            if name_el is not None:
                authors.append(name_el.text.strip())
        arxiv_id = paper_url.split("/abs/")[-1] if "/abs/" in paper_url else ""
        results.append({
            "source": "arxiv",
            "paper_id": arxiv_id,
            "title": title,
            "authors": authors,
            "year": year,
            "abstract": abstract,
            "citation_count": 0,
            "venue": "arXiv",
            "url": paper_url,
            "doi": "",
        })
    return results


# -- Local docs ----------------------------------------------------------------

def scan_local_docs(base_dir, scan_paths):
    """Scan local markdown files for cited references.

    Extracts author-year citations and bibliographic entries from markdown.
    Returns list of dicts with keys: source, title, authors, year, context.
    """
    results = []
    seen_titles = set()
    # Pattern for references like "Author (Year)" or "Author, Year"
    cite_pattern = re.compile(
        r"(?:^[-*]\s+|\*\*\d+\.\*\*\s+)?"
        r"([A-Z][a-z]+(?:\s+(?:&|and)\s+[A-Z][a-z]+)?(?:\s+et\s+al\.?)?)"
        r"[\s,]*\(?\s*(\d{4})\s*\)?"
        r"[.:,]\s*(.+?)(?:\.|$)",
        re.MULTILINE
    )
    # Pattern for markdown bibliography entries
    bib_pattern = re.compile(
        r"^[-*]\s+(.+?)\s*\((\d{4})\)\s*[.:]?\s*(.+?)$",
        re.MULTILINE
    )
    for rel_path in scan_paths:
        full_path = os.path.join(base_dir, rel_path)
        if not os.path.isdir(full_path):
            continue
        for fname in os.listdir(full_path):
            if not fname.endswith(".md"):
                continue
            fpath = os.path.join(full_path, fname)
            try:
                with open(fpath, "r", encoding="utf-8") as f:
                    text = f.read()
            except OSError:
                continue
            for pattern in [cite_pattern, bib_pattern]:
                for match in pattern.finditer(text):
                    authors_str = match.group(1).strip()
                    year_str = match.group(2)
                    title_or_context = match.group(3).strip()[:200]
                    key = "{}_{}_{}".format(
                        authors_str.lower(), year_str, title_or_context[:40].lower()
                    )
                    if key in seen_titles:
                        continue
                    seen_titles.add(key)
                    try:
                        year = int(year_str)
                    except ValueError:
                        year = None
                    results.append({
                        "source": "local_docs",
                        "paper_id": "",
                        "title": title_or_context,
                        "authors": [authors_str],
                        "year": year,
                        "abstract": "",
                        "citation_count": 0,
                        "venue": "",
                        "url": "",
                        "doi": "",
                        "local_file": os.path.relpath(fpath, base_dir),
                    })
    return results
