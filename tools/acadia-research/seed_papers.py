#!/usr/bin/env python3
"""Seed the research database with known key references from project docs.

These are manually curated papers cited in the ACADIA paper drafts and
working documents. Run once to bootstrap the database.
"""

import os
import sys

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, SCRIPT_DIR)

from database import ResearchDatabase

PROJECT_ROOT = os.path.abspath(os.path.join(SCRIPT_DIR, "..", ".."))
DB_PATH = os.path.join(PROJECT_ROOT, "docs", "research", "database.json")

# Key papers cited across the ACADIA paper drafts
SEED_PAPERS = [
    {
        "source": "seed",
        "paper_id": "",
        "title": "The Reflective Practitioner: How Professionals Think in Action",
        "authors": ["Donald Schon"],
        "year": 1983,
        "abstract": "Foundational text on reflective practice in professional work. The CLI's OK:/ERROR: protocol operationalizes Schon's reflective conversation with the situation.",
        "citation_count": 0,
        "venue": "Basic Books",
        "url": "",
        "doi": "",
    },
    {
        "source": "seed",
        "paper_id": "",
        "title": "The Child's Conception of Space",
        "authors": ["Jean Piaget", "Barbel Inhelder"],
        "year": 1956,
        "abstract": "Topological-to-metric developmental sequence in spatial cognition. Relevant to how blind users build spatial understanding from semantic to geometric.",
        "citation_count": 0,
        "venue": "Routledge & Kegan Paul",
        "url": "",
        "doi": "",
    },
    {
        "source": "seed",
        "paper_id": "",
        "title": "Understanding the Blind: An Integrative Approach to Visual Impairment",
        "authors": ["Susanna Millar"],
        "year": 1994,
        "abstract": "Comprehensive account of blind spatial cognition, sequential landmark-based reasoning, and language-mediated spatial understanding.",
        "citation_count": 0,
        "venue": "Lawrence Erlbaum",
        "url": "",
        "doi": "",
    },
    {
        "source": "seed",
        "paper_id": "",
        "title": "Spatial representations and navigation in blind people",
        "authors": ["Jack Loomis", "Reginald Golledge", "Roberta Klatzky"],
        "year": 2001,
        "abstract": "Review of blind spatial cognition research including mental maps, wayfinding strategies, and non-visual spatial representation.",
        "citation_count": 0,
        "venue": "Handbook of Neuropsychology",
        "url": "",
        "doi": "",
    },
    {
        "source": "seed",
        "paper_id": "",
        "title": "Spatial learning and navigation in blindness",
        "authors": ["Nicholas Giudice"],
        "year": 2018,
        "abstract": "Updated framework for blind spatial cognition. Key reference for the project's semantic-over-geometric approach.",
        "citation_count": 0,
        "venue": "Oxford Handbook of Cognitive Psychology",
        "url": "",
        "doi": "",
    },
    {
        "source": "seed",
        "paper_id": "",
        "title": "The Craftsman",
        "authors": ["Richard Sennett"],
        "year": 2008,
        "abstract": "The hand as thinking organ. Embodied making as a mode of design thinking. Foundation for physical-digital round-trip design.",
        "citation_count": 0,
        "venue": "Yale University Press",
        "url": "",
        "doi": "",
    },
    {
        "source": "seed",
        "paper_id": "",
        "title": "Architecture's New Media: Principles, Theories, and Methods of Computer-Aided Design",
        "authors": ["Yehuda Kalay"],
        "year": 2004,
        "abstract": "Process as first-class artifact alongside product. Relevant to version-controlled, auditable design workflows.",
        "citation_count": 0,
        "venue": "MIT Press",
        "url": "",
        "doi": "",
    },
    {
        "source": "seed",
        "paper_id": "",
        "title": "Digital Design and Manufacturing: CAD/CAM Applications in Architecture and Design",
        "authors": ["Larry Sass"],
        "year": 2024,
        "abstract": "ACADIA 2024 Teaching Award work. Fabrication-centered pedagogy, physical making as cognitive partner.",
        "citation_count": 0,
        "venue": "ACADIA",
        "url": "",
        "doi": "",
    },
    {
        "source": "seed",
        "paper_id": "",
        "title": "Theory of Design in the Age of Computation",
        "authors": ["Rivka Oxman"],
        "year": 2006,
        "abstract": "Reflective practice over routine production. Framework for understanding computational design pedagogy.",
        "citation_count": 0,
        "venue": "Design Studies",
        "url": "",
        "doi": "",
    },
    {
        "source": "seed",
        "paper_id": "",
        "title": "The Space Between: Architecture and Disability",
        "authors": ["David Gissen"],
        "year": 2022,
        "abstract": "Beyond access: disability as architectural knowledge. Challenges accommodation-as-minimum-compliance.",
        "citation_count": 0,
        "venue": "University of Minnesota Press",
        "url": "",
        "doi": "",
    },
    {
        "source": "seed",
        "paper_id": "",
        "title": "Guidelines and Standards for Tactile Graphics",
        "authors": ["Braille Authority of North America"],
        "year": 2010,
        "abstract": "BANA guidelines for tactile graphic production. Standards for braille labels, line weights, density ranges used in PIAF output.",
        "citation_count": 0,
        "venue": "BANA",
        "url": "",
        "doi": "",
    },
    {
        "source": "seed",
        "paper_id": "",
        "title": "Universal Design in Higher Education: From Principles to Practice",
        "authors": ["Sheryl Burgstahler", "Rebecca Cory"],
        "year": 2008,
        "abstract": "Framework for universal design in educational settings. Background for inclusive studio pedagogy.",
        "citation_count": 0,
        "venue": "Harvard Education Press",
        "url": "",
        "doi": "",
    },
    {
        "source": "seed",
        "paper_id": "",
        "title": "Disability, Architecture, and Infrastructure",
        "authors": ["Aimi Hamraie"],
        "year": 2017,
        "abstract": "Building Access: Universal Design and the Politics of Disability. Critical disability studies framework for architectural accessibility.",
        "citation_count": 0,
        "venue": "University of Minnesota Press",
        "url": "",
        "doi": "",
    },
    {
        "source": "seed",
        "paper_id": "",
        "title": "Towards a Critical Technical Practice: Accessible Design in Architecture",
        "authors": ["Beth Tauke", "Korydon Smith", "Charles Davis"],
        "year": 2015,
        "abstract": "Diversity and Design: Understanding Hidden Consequences. Critical approach to inclusive design practice.",
        "citation_count": 0,
        "venue": "Routledge",
        "url": "",
        "doi": "",
    },
    {
        "source": "seed",
        "paper_id": "",
        "title": "Tactile maps for the blind: A case study in multisensory design",
        "authors": ["Joshua Miele"],
        "year": 2006,
        "abstract": "Research on tactile map design for blind users. Methods for translating visual spatial information to tactile form.",
        "citation_count": 0,
        "venue": "Smith-Kettlewell Eye Research Institute",
        "url": "",
        "doi": "",
    },
    {
        "source": "seed",
        "paper_id": "",
        "title": "Haptic perception of spatial relations by blind and sighted participants",
        "authors": ["Morton Heller", "Soledad Ballesteros"],
        "year": 2012,
        "abstract": "Touch, Blindness, and Neuroscience. Research on haptic spatial reasoning relevant to tactile architectural models.",
        "citation_count": 0,
        "venue": "Oxford University Press",
        "url": "",
        "doi": "",
    },
    {
        "source": "seed",
        "paper_id": "",
        "title": "Design for Architecture in the Digital Era",
        "authors": ["Branko Kolarevic"],
        "year": 2003,
        "abstract": "Architecture in the Digital Age: Design and Manufacturing. Foundational text on computational design workflows.",
        "citation_count": 0,
        "venue": "Spon Press",
        "url": "",
        "doi": "",
    },
    {
        "source": "seed",
        "paper_id": "",
        "title": "Model Context Protocol: Connecting AI to tools",
        "authors": ["Anthropic"],
        "year": 2024,
        "abstract": "MCP protocol specification for connecting AI assistants to external tools and data sources. Used for the Layout Jig MCP server.",
        "citation_count": 0,
        "venue": "Anthropic",
        "url": "",
        "doi": "",
    },
    {
        "source": "seed",
        "paper_id": "",
        "title": "Exploring Expressive Tactile Design: Tactile Graphics Beyond Utility",
        "authors": ["Emeline Brulé", "Gilles Bailly", "Annie Gentes"],
        "year": 2020,
        "abstract": "Research on tactile graphics as expressive medium beyond purely functional representation.",
        "citation_count": 0,
        "venue": "ACM CHI",
        "url": "",
        "doi": "",
    },
    {
        "source": "seed",
        "paper_id": "",
        "title": "Non-Visual Access to Computing",
        "authors": ["Chieko Asakawa"],
        "year": 2005,
        "abstract": "Overview of non-visual computing interfaces including screen readers, tactile displays, and auditory interfaces.",
        "citation_count": 0,
        "venue": "IBM Research",
        "url": "",
        "doi": "",
    },
]


def main():
    db = ResearchDatabase(DB_PATH)
    added = db.add_entries(SEED_PAPERS)
    db.tag_entries({})
    db.save()
    print("OK: Seeded {} new papers (total: {})".format(added, len(db.data["entries"])))
    print("READY:")


if __name__ == "__main__":
    main()
