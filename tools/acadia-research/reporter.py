"""Report generator for the Acadia research database.

Produces screen-reader-friendly reports: short lines, labeled sections,
no tables, no ASCII art. Follows CLAUDE.md screen reader rules.
"""

import os
from datetime import datetime


def generate_report(db, new_count=0, query_log=None):
    """Generate a screen-reader-friendly research report.

    Args:
        db: ResearchDatabase instance.
        new_count: Number of new entries added this run.
        query_log: List of (query, result_count) tuples from this run.

    Returns:
        Report text string.
    """
    stats = db.get_stats()
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    lines = []
    lines.append("OK: Acadia Research Report")
    lines.append("Date: {}".format(now))
    lines.append("")

    # Summary
    lines.append("Summary:")
    lines.append("- Total entries: {}".format(stats["total"]))
    lines.append("- New this run: {}".format(new_count))
    lines.append("- Sources: {}".format(
        ", ".join("{} ({})".format(k, v) for k, v in sorted(stats["by_source"].items()))
    ))
    if stats["by_decade"]:
        lines.append("- Decades: {}".format(
            ", ".join("{}s ({})".format(k, v) for k, v in sorted(stats["by_decade"].items()))
        ))
    lines.append("")

    # Query results
    if query_log:
        lines.append("Queries run:")
        for i, (query, count) in enumerate(query_log, 1):
            lines.append("  {}. \"{}\" - {} results".format(i, query, count))
        lines.append("")

    # Top recent additions
    if new_count > 0:
        recent = [e for e in db.data["entries"] if e.get("added_date") == datetime.now().strftime("%Y-%m-%d")]
        recent.sort(key=lambda e: e.get("citation_count", 0), reverse=True)
        top = recent[:10]
        if top:
            lines.append("Notable new entries:")
            for i, entry in enumerate(top, 1):
                authors_str = ", ".join(entry.get("authors", [])[:3])
                if len(entry.get("authors", [])) > 3:
                    authors_str += " et al."
                year = entry.get("year", "n.d.")
                cites = entry.get("citation_count", 0)
                lines.append("  {}. {} ({})".format(i, entry.get("title", "Untitled"), year))
                lines.append("     Authors: {}".format(authors_str))
                if cites > 0:
                    lines.append("     Citations: {}".format(cites))
                lines.append("     Source: {}".format(entry.get("source", "unknown")))
            lines.append("")

    # Top cited overall
    top_cited = db.get_entries(limit=5)
    if top_cited:
        lines.append("Top cited in database:")
        for i, entry in enumerate(top_cited, 1):
            year = entry.get("year", "n.d.")
            cites = entry.get("citation_count", 0)
            lines.append("  {}. {} ({}) - {} citations".format(
                i, entry.get("title", "Untitled"), year, cites
            ))
        lines.append("")

    lines.append("READY:")
    return "\n".join(lines)


def save_report(report_text, output_dir):
    """Save report to timestamped file in output_dir.

    Returns the file path.
    """
    os.makedirs(output_dir, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = "report_{}.txt".format(timestamp)
    filepath = os.path.join(output_dir, filename)
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(report_text)
    return filepath
