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


def generate_markdown_report(db):
    """Generate a full markdown report of the entire research database.

    Organized by topic with all entries listed. Suitable for reading,
    sharing, and printing. Follows screen reader rules: no tables,
    no ASCII art, short labeled lines.

    Returns markdown string.
    """
    stats = db.get_stats()
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    lines = []

    lines.append("# Acadia Research Database")
    lines.append("")
    lines.append("Radical Accessibility Project -- UIUC School of Architecture")
    lines.append("")
    lines.append("Generated: {}".format(now))
    lines.append("")
    lines.append("Total entries: {}".format(stats["total"]))
    lines.append("")
    lines.append("Sources: {}".format(
        ", ".join("{} ({})".format(k, v) for k, v in sorted(stats["by_source"].items()))
    ))
    lines.append("")
    if stats["by_decade"]:
        lines.append("Coverage: {}".format(
            ", ".join("{}s ({})".format(k, v) for k, v in sorted(stats["by_decade"].items()))
        ))
        lines.append("")
    lines.append("---")
    lines.append("")

    # Topic sections
    topic_labels = {
        "accessible_architecture": "Accessible Architecture",
        "tactile_graphics": "Tactile Graphics",
        "blind_spatial_cognition": "Blind Spatial Cognition",
        "cli_cad": "CLI and Non-Visual CAD",
        "ai_assisted_development": "AI-Assisted Development",
        "inclusive_pedagogy": "Inclusive Pedagogy",
        "computational_design": "Computational Design",
        "acadia_proceedings": "ACADIA Proceedings",
    }

    # Collect entries by topic
    entries_by_topic = {}
    untagged = []
    for entry in db.data["entries"]:
        tags = entry.get("tags", [])
        if not tags:
            untagged.append(entry)
        else:
            for tag in tags:
                entries_by_topic.setdefault(tag, []).append(entry)

    # Render each topic section
    for tag, label in topic_labels.items():
        entries = entries_by_topic.get(tag, [])
        if not entries:
            continue
        # Sort by year descending
        entries.sort(key=lambda e: e.get("year") or 0, reverse=True)
        # Deduplicate within section (entry may appear under multiple tags)
        seen = set()
        unique = []
        for e in entries:
            key = e.get("title", "")
            if key not in seen:
                seen.add(key)
                unique.append(e)
        entries = unique

        lines.append("## {} ({})".format(label, len(entries)))
        lines.append("")
        for entry in entries:
            title = entry.get("title", "Untitled")
            year = entry.get("year", "n.d.")
            authors = _format_authors(entry.get("authors", []))
            abstract = entry.get("abstract", "")
            venue = entry.get("venue", "")
            doi = entry.get("doi", "")
            cites = entry.get("citation_count", 0)
            source = entry.get("source", "")

            lines.append("### {} ({})".format(title, year))
            lines.append("")
            if authors:
                lines.append("**Authors:** {}".format(authors))
                lines.append("")
            if venue:
                lines.append("**Venue:** {}".format(venue))
                lines.append("")
            if abstract:
                lines.append(abstract)
                lines.append("")
            detail_parts = []
            if cites > 0:
                detail_parts.append("Citations: {}".format(cites))
            if doi:
                detail_parts.append("DOI: {}".format(doi))
            if source:
                detail_parts.append("Source: {}".format(source))
            if detail_parts:
                lines.append("*{}*".format(" | ".join(detail_parts)))
                lines.append("")
        lines.append("---")
        lines.append("")

    # Untagged entries
    if untagged:
        untagged.sort(key=lambda e: e.get("year") or 0, reverse=True)
        lines.append("## Other References ({})".format(len(untagged)))
        lines.append("")
        for entry in untagged:
            title = entry.get("title", "Untitled")
            year = entry.get("year", "n.d.")
            authors = _format_authors(entry.get("authors", []))
            lines.append("- **{}** ({}){}".format(
                title, year,
                " -- {}".format(authors) if authors else ""
            ))
        lines.append("")
        lines.append("---")
        lines.append("")

    lines.append("*End of report.*")
    return "\n".join(lines)


def _format_authors(authors_list):
    """Format author list for display."""
    if not authors_list:
        return ""
    if len(authors_list) <= 3:
        return ", ".join(authors_list)
    return ", ".join(authors_list[:3]) + " et al."


def save_report(report_text, output_dir, extension="txt"):
    """Save report to timestamped file in output_dir.

    Returns the file path.
    """
    os.makedirs(output_dir, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = "report_{}.{}".format(timestamp, extension)
    filepath = os.path.join(output_dir, filename)
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(report_text)
    return filepath
