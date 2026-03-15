"""Database manager for the Acadia research database.

Reads/writes docs/research/database.json with atomic writes.
Deduplicates entries by title similarity and paper_id.
"""

import copy
import json
import os
import re
import tempfile
from datetime import datetime


def _atomic_write(path, text):
    """Write text to path atomically: write .tmp, fsync, os.replace."""
    dir_name = os.path.dirname(path)
    fd, tmp_path = tempfile.mkstemp(dir=dir_name, suffix=".tmp")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            f.write(text)
            f.flush()
            os.fsync(f.fileno())
        os.replace(tmp_path, path)
    except Exception:
        if os.path.exists(tmp_path):
            os.unlink(tmp_path)
        raise


def _normalize_title(title):
    """Lowercase, strip punctuation for dedup comparison."""
    return re.sub(r"[^a-z0-9 ]", "", title.lower()).strip()


class ResearchDatabase:
    """Manages the research database JSON file."""

    def __init__(self, db_path):
        self.db_path = db_path
        self.data = self._load()

    def _load(self):
        """Load database from disk."""
        if not os.path.exists(self.db_path):
            return {
                "schema": "acadia_research_db_v1",
                "meta": {
                    "project": "Radical Accessibility Project",
                    "description": "Research database for ACADIA papers",
                    "created": datetime.now().strftime("%Y-%m-%d"),
                    "last_updated": datetime.now().strftime("%Y-%m-%d"),
                    "total_entries": 0,
                },
                "topics": [],
                "entries": [],
            }
        with open(self.db_path, "r", encoding="utf-8") as f:
            return json.load(f)

    def save(self):
        """Persist database to disk atomically."""
        self.data["meta"]["last_updated"] = datetime.now().strftime("%Y-%m-%d")
        self.data["meta"]["total_entries"] = len(self.data["entries"])
        text = json.dumps(self.data, indent=2, ensure_ascii=False) + "\n"
        _atomic_write(self.db_path, text)

    def _is_duplicate(self, entry):
        """Check if entry already exists by paper_id or normalized title."""
        norm_new = _normalize_title(entry.get("title", ""))
        if not norm_new:
            return True
        for existing in self.data["entries"]:
            # Match by paper_id if both have one
            if entry.get("paper_id") and existing.get("paper_id"):
                if entry["paper_id"] == existing["paper_id"]:
                    return True
            # Match by normalized title
            norm_existing = _normalize_title(existing.get("title", ""))
            if norm_new == norm_existing:
                return True
        return False

    @staticmethod
    def _clean_title(title):
        """Strip markdown artifacts from title text."""
        if not title:
            return title
        # Remove leading markdown: **, [, ", combinations like ["
        title = re.sub(r'^[\s\*\[\]"\(]+', "", title)
        # Remove trailing markdown
        title = re.sub(r'[\s\*\[\]"\)]+$', "", title)
        # Remove leading/trailing quotes
        title = title.strip("\"'")
        # Remove orphaned closing brackets/parens
        title = re.sub(r'^\[+|^\(+', "", title)
        return title.strip()

    def add_entries(self, entries):
        """Add new entries, skipping duplicates. Returns count of added."""
        added = 0
        for entry in entries:
            entry["title"] = self._clean_title(entry.get("title", ""))
            if self._is_duplicate(entry):
                continue
            entry["added_date"] = datetime.now().strftime("%Y-%m-%d")
            entry["tags"] = entry.get("tags", [])
            entry["notes"] = entry.get("notes", "")
            entry["relevance_score"] = entry.get("relevance_score", 0)
            self.data["entries"].append(entry)
            added += 1
        return added

    def get_entries(self, topic=None, source=None, min_year=None, limit=None):
        """Query entries with optional filters."""
        results = self.data["entries"]
        if topic:
            results = [e for e in results if topic in e.get("tags", [])]
        if source:
            results = [e for e in results if e.get("source") == source]
        if min_year:
            results = [e for e in results if (e.get("year") or 0) >= min_year]
        # Sort by citation count descending, then year descending
        results.sort(
            key=lambda e: (e.get("citation_count", 0), e.get("year") or 0),
            reverse=True,
        )
        if limit:
            results = results[:limit]
        return results

    def get_stats(self):
        """Return summary statistics."""
        entries = self.data["entries"]
        sources = {}
        years = {}
        for e in entries:
            src = e.get("source", "unknown")
            sources[src] = sources.get(src, 0) + 1
            yr = e.get("year")
            if yr:
                decade = (yr // 10) * 10
                years[decade] = years.get(decade, 0) + 1
        return {
            "total": len(entries),
            "by_source": sources,
            "by_decade": dict(sorted(years.items())),
            "last_updated": self.data["meta"].get("last_updated", ""),
        }

    def tag_entries(self, topic_keywords):
        """Auto-tag entries based on keyword matching in title/abstract."""
        tag_map = {
            "accessible_architecture": [
                "accessible", "accessibility", "blind", "low-vision",
                "disability", "inclusive", "universal design",
            ],
            "tactile_graphics": [
                "tactile", "haptic", "swell paper", "piaf", "raised line",
                "braille", "emboss",
            ],
            "blind_spatial_cognition": [
                "spatial cognition", "wayfinding", "mental map",
                "spatial representation", "blind navigation",
            ],
            "cli_cad": [
                "command line", "cli", "text-based", "non-visual interface",
                "screen reader",
            ],
            "ai_assisted_development": [
                "llm", "large language model", "ai-assisted", "claude",
                "chatgpt", "copilot", "code generation",
            ],
            "inclusive_pedagogy": [
                "pedagogy", "education", "studio", "curriculum",
                "teaching", "learning", "student",
            ],
            "computational_design": [
                "computational design", "parametric", "algorithmic",
                "generative", "grasshopper", "rhinoceros",
            ],
            "acadia_proceedings": [
                "acadia",
            ],
        }
        for entry in self.data["entries"]:
            text = "{} {}".format(
                entry.get("title", ""), entry.get("abstract", "")
            ).lower()
            for tag, keywords in tag_map.items():
                if any(kw in text for kw in keywords):
                    if tag not in entry.get("tags", []):
                        entry.setdefault("tags", []).append(tag)
