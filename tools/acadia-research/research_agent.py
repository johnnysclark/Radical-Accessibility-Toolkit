#!/usr/bin/env python3
"""Acadia Research Agent -- searches, collects, and reports on research papers.

Builds the Acadia research database by querying Semantic Scholar, arXiv,
and scanning local project docs. Generates screen-reader-friendly reports.

Usage:
    python research_agent.py run          # Run one search cycle
    python research_agent.py run --topic "tactile maps"  # Single topic search
    python research_agent.py report       # Generate report from current DB
    python research_agent.py stats        # Print database stats
    python research_agent.py search "query"  # Ad-hoc search, add to DB
    python research_agent.py list [--topic TAG] [--limit N]
    python research_agent.py topics       # List all topic tags

Uses only Python stdlib -- no pip dependencies.
"""

import argparse
import json
import os
import sys
import time

# Resolve paths relative to this script
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(SCRIPT_DIR, "..", ".."))
DB_PATH = os.path.join(PROJECT_ROOT, "docs", "research", "database.json")
CONFIG_PATH = os.path.join(PROJECT_ROOT, "docs", "research", "config.json")
REPORT_DIR = os.path.join(PROJECT_ROOT, "docs", "research", "reports")

# Add tools dir to path for local imports
sys.path.insert(0, SCRIPT_DIR)

from database import ResearchDatabase
from sources import search_semantic_scholar, search_arxiv, scan_local_docs
from reporter import generate_report, save_report


def load_config():
    """Load search config from config.json."""
    if not os.path.exists(CONFIG_PATH):
        print("ERROR: Config not found at {}".format(CONFIG_PATH))
        sys.exit(1)
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def run_search_cycle(db, config, single_topic=None, verbose=False):
    """Run one full search cycle across all configured sources.

    Returns (new_count, query_log).
    """
    queries = config.get("search_queries", [])
    if single_topic:
        queries = [single_topic]

    ss_config = config.get("sources", {}).get("semantic_scholar", {})
    arxiv_config = config.get("sources", {}).get("arxiv", {})
    local_config = config.get("sources", {}).get("local_docs", {})

    ss_max = ss_config.get("max_results_per_query", 10)
    arxiv_max = arxiv_config.get("max_results_per_query", 10)

    all_entries = []
    query_log = []

    # Semantic Scholar
    if ss_config.get("enabled", True):
        for query in queries:
            if verbose:
                print("OK: Searching Semantic Scholar: \"{}\"".format(query))
            results = search_semantic_scholar(query, max_results=ss_max)
            all_entries.extend(results)
            query_log.append(("SS: {}".format(query), len(results)))
            # Rate limit: Semantic Scholar allows ~100 requests/5min unauthenticated
            time.sleep(1)

    # arXiv
    if arxiv_config.get("enabled", True):
        for query in queries:
            if verbose:
                print("OK: Searching arXiv: \"{}\"".format(query))
            results = search_arxiv(query, max_results=arxiv_max)
            all_entries.extend(results)
            query_log.append(("arXiv: {}".format(query), len(results)))
            time.sleep(0.5)

    # Local docs
    if local_config.get("enabled", True):
        scan_paths = local_config.get("scan_paths", ["docs/"])
        if verbose:
            print("OK: Scanning local docs")
        results = scan_local_docs(PROJECT_ROOT, scan_paths)
        all_entries.extend(results)
        query_log.append(("local_docs", len(results)))

    # Add to database (deduplicates internally)
    new_count = db.add_entries(all_entries)

    # Auto-tag
    db.tag_entries(config.get("topics", []))

    # Save
    db.save()

    return new_count, query_log


def cmd_run(args):
    """Run a search cycle and generate a report."""
    config = load_config()
    db = ResearchDatabase(DB_PATH)

    print("OK: Starting research cycle")
    new_count, query_log = run_search_cycle(
        db, config, single_topic=args.topic, verbose=args.verbose
    )
    print("OK: Added {} new entries (total: {})".format(
        new_count, len(db.data["entries"])
    ))

    # Generate and save report
    report = generate_report(db, new_count=new_count, query_log=query_log)
    filepath = save_report(report, REPORT_DIR)
    print("OK: Report saved to {}".format(os.path.relpath(filepath, PROJECT_ROOT)))

    # Print report to stdout
    print("")
    print(report)


def cmd_report(args):
    """Generate report from current database."""
    db = ResearchDatabase(DB_PATH)
    report = generate_report(db)
    filepath = save_report(report, REPORT_DIR)
    print("OK: Report saved to {}".format(os.path.relpath(filepath, PROJECT_ROOT)))
    print("")
    print(report)


def cmd_stats(args):
    """Print database statistics."""
    db = ResearchDatabase(DB_PATH)
    stats = db.get_stats()
    print("OK: Database stats")
    print("Total entries: {}".format(stats["total"]))
    print("By source: {}".format(
        ", ".join("{} ({})".format(k, v) for k, v in sorted(stats["by_source"].items()))
    ))
    if stats["by_decade"]:
        print("By decade: {}".format(
            ", ".join("{}s ({})".format(k, v) for k, v in sorted(stats["by_decade"].items()))
        ))
    print("Last updated: {}".format(stats["last_updated"]))
    print("READY:")


def cmd_search(args):
    """Ad-hoc search for a specific query."""
    config = load_config()
    db = ResearchDatabase(DB_PATH)
    query = " ".join(args.query)
    print("OK: Searching for: \"{}\"".format(query))

    all_entries = []
    results = search_semantic_scholar(query, max_results=10)
    all_entries.extend(results)
    print("OK: Semantic Scholar returned {} results".format(len(results)))

    time.sleep(0.5)
    results = search_arxiv(query, max_results=10)
    all_entries.extend(results)
    print("OK: arXiv returned {} results".format(len(results)))

    new_count = db.add_entries(all_entries)
    db.tag_entries(config.get("topics", []))
    db.save()
    print("OK: Added {} new entries".format(new_count))

    # Show what was found
    for i, entry in enumerate(all_entries[:10], 1):
        year = entry.get("year", "n.d.")
        cites = entry.get("citation_count", 0)
        authors = ", ".join(entry.get("authors", [])[:2])
        if len(entry.get("authors", [])) > 2:
            authors += " et al."
        print("  {}. {} ({}) by {} [{} cites]".format(
            i, entry.get("title", "Untitled"), year, authors, cites
        ))
    print("READY:")


def cmd_list(args):
    """List database entries with optional filters."""
    db = ResearchDatabase(DB_PATH)
    entries = db.get_entries(
        topic=args.topic,
        source=args.source,
        min_year=args.min_year,
        limit=args.limit or 20,
    )
    if not entries:
        print("OK: No entries found matching filters")
        print("READY:")
        return

    print("OK: {} entries".format(len(entries)))
    for i, entry in enumerate(entries, 1):
        year = entry.get("year", "n.d.")
        cites = entry.get("citation_count", 0)
        authors = ", ".join(entry.get("authors", [])[:2])
        if len(entry.get("authors", [])) > 2:
            authors += " et al."
        tags = ", ".join(entry.get("tags", []))
        print("  {}. {} ({})".format(i, entry.get("title", "Untitled"), year))
        print("     By: {}".format(authors))
        if cites:
            print("     Citations: {}".format(cites))
        if tags:
            print("     Tags: {}".format(tags))
    print("READY:")


def cmd_topics(args):
    """List all topic tags with counts."""
    db = ResearchDatabase(DB_PATH)
    tag_counts = {}
    for entry in db.data["entries"]:
        for tag in entry.get("tags", []):
            tag_counts[tag] = tag_counts.get(tag, 0) + 1
    if not tag_counts:
        print("OK: No tagged entries yet. Run 'run' first.")
        print("READY:")
        return
    print("OK: Topic tags")
    for tag, count in sorted(tag_counts.items(), key=lambda x: -x[1]):
        print("  {} ({})".format(tag, count))
    print("READY:")


def main():
    parser = argparse.ArgumentParser(
        description="Acadia Research Agent -- build the research database"
    )
    parser.add_argument(
        "-v", "--verbose", action="store_true", help="Verbose output"
    )
    subparsers = parser.add_subparsers(dest="command")

    # run
    run_parser = subparsers.add_parser("run", help="Run a search cycle")
    run_parser.add_argument(
        "--topic", type=str, default=None,
        help="Search a single topic instead of all configured queries"
    )
    run_parser.set_defaults(func=cmd_run)

    # report
    report_parser = subparsers.add_parser("report", help="Generate report")
    report_parser.set_defaults(func=cmd_report)

    # stats
    stats_parser = subparsers.add_parser("stats", help="Print DB stats")
    stats_parser.set_defaults(func=cmd_stats)

    # search
    search_parser = subparsers.add_parser("search", help="Ad-hoc search")
    search_parser.add_argument("query", nargs="+", help="Search query")
    search_parser.set_defaults(func=cmd_search)

    # list
    list_parser = subparsers.add_parser("list", help="List entries")
    list_parser.add_argument("--topic", type=str, help="Filter by topic tag")
    list_parser.add_argument("--source", type=str, help="Filter by source")
    list_parser.add_argument("--min-year", type=int, dest="min_year", help="Minimum year")
    list_parser.add_argument("--limit", type=int, help="Max results")
    list_parser.set_defaults(func=cmd_list)

    # topics
    topics_parser = subparsers.add_parser("topics", help="List topic tags")
    topics_parser.set_defaults(func=cmd_topics)

    args = parser.parse_args()
    if not args.command:
        parser.print_help()
        sys.exit(0)

    args.func(args)


if __name__ == "__main__":
    main()
