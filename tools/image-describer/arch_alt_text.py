#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Arch-Alt-Text — Architectural Image Description CLI (v1.0)
============================================================
Describes architectural images for blind / low-vision students
using Claude's vision API.  Produces structured Macro / Meso / Micro
descriptions optimized for screen readers and braille displays.

Part of the Radical Accessibility Project — UIUC School of Architecture.

Dependencies: Python 3 stdlib only (no pip installs).
Requires:     ANTHROPIC_API_KEY environment variable.
"""

import argparse
import base64
import json
import mimetypes
import os
import sys
import urllib.request
import urllib.error
from datetime import datetime

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

VERSION = "1.1"
API_URL = "https://api.anthropic.com/v1/messages"
DEFAULT_MODEL = "claude-sonnet-4-5-20250929"
MAX_TOKENS = 4096
ANTHROPIC_VERSION = "2023-06-01"
HISTORY_FILENAME = "arch_alt_text_history.json"

SUPPORTED_MIME = ("image/jpeg", "image/png", "image/gif", "image/webp")

# ---------------------------------------------------------------------------
# Mode presets — loaded from patterns/image_description_machine/*.md
# ---------------------------------------------------------------------------

# Map short mode names to filenames (without .md)
MODE_FILES = {
    "general": "image_description_machine",
    "site-visit": "site_visit",
    "design-studio": "design_studio",
    "design-review": "design_review",
    "structures": "structures_lecture",
    "history": "history_lecture",
}

DEFAULT_MODE = "general"


def _patterns_dir():
    """Return the patterns/image_description_machine/ directory."""
    # Navigate from tools/image-describer/ up to CONTROLLER/patterns/
    script = os.path.dirname(os.path.abspath(__file__))
    controller = os.path.dirname(os.path.dirname(script))
    return os.path.join(controller, "patterns", "image_description_machine")


def _load_mode_prompt(mode_name):
    """Load a system prompt from the patterns directory by mode name.

    Returns the file contents, or None if not found.
    """
    filename = MODE_FILES.get(mode_name)
    if not filename:
        return None
    path = os.path.join(_patterns_dir(), filename + ".md")
    if not os.path.isfile(path):
        return None
    with open(path, "r", encoding="utf-8") as f:
        return f.read().strip()


def _list_modes():
    """Return list of (mode_name, available_bool) tuples."""
    result = []
    for name in MODE_FILES:
        path = os.path.join(_patterns_dir(), MODE_FILES[name] + ".md")
        result.append((name, os.path.isfile(path)))
    return result

# ---------------------------------------------------------------------------
# System prompt — the full Arch-Alt-Text persona
# ---------------------------------------------------------------------------

SYSTEM_PROMPT = r"""You are Arch-Alt-Text, an expert narrator for a blind architecture student.

Your mission: translate ANY visual used in architecture education into a vivid, multi-sensory mental model. Only describe what is in the image. Do not embellish, interpret, or contextualize. Do not ask questions in your answer or provoke discussion. Do not repeat yourself within the answer.

OUTPUT FORMAT (STRICT — three paragraphs, no bullets or lists):

Title: <concise title. Say the title of the piece if it is known, OR "Unknown" if no source is evident>

Macro Layer (exactly 3 sentences):
Identify the medium (photo, drawing, painting, plan, section, axonometric, exploded diagram, CFD field, FEM stress map, material micrograph, rendering, model photo, film still, multi-panel collage, chart/graph, etc). State the principal subject and the image's purpose/argument (comparative, analytical, atmospheric, speculative, schematic). Convey the dominant atmosphere or pedagogical intent.

Meso Layer (at least 4 sentences):
Decompose composition and hierarchy: main masses/forms, axes/grids, figure-ground, foreground/background; for drawings, note line-weight tiers. Talk about proportions of elements in the image. Name primary materials/assemblies or graphical conventions (hatches, color keys, arrow flows, dashed demo lines, section cuts). Give orientation and viewpoint/projection (viewer's left/right, cardinal if marked, top-of-page if implied; bird's-eye, worm's-eye, isometric, one-point perspective, exploded). Describe scale cues (human figures, scale bars, module/spacing) and lighting qualities OR, for diagrammatic media, the dominant flow or causal direction. Summarize relationships among parts (load path, circulation spine, service core, facade rhythm, thermal gradient, timeline). Mention annotations/legends without transcribing yet; flag if text exists for later verbatim capture.

Micro Layer (at least 8 sentences):
Detail textures and assemblies (joinery, fasteners, courses, panelization), structural logic (supports, spans, connections), and environmental strategies (daylighting, shading, ventilation, envelope, water). For technical media: explain axes/units, variables, symbol meanings, line/marker styles, trends, inflection points, thresholds, outliers and relate them to design intent or performance. Describe representational conventions (hatching types, poche, entourage, diagram layering such as services over structure, historical overlays). Provide proportional/relative dimensions (column spacing about triple the beam depth); avoid invented exact numbers unless given; if both SI/Imperial appear, report as shown. Clarify ambiguities without guessing (hatching suggests CLT, though could indicate generic mass timber; tonal noise obscures joint detail). Map visual traits to multi-sensory analogies (tactile, acoustic, thermal, airflow, smell when reasonable) to strengthen spatial imagination. Include accessibility/inclusive-design cues (ramp slopes, tactile paving, contrast edges, door clearances if discernible). State occlusions and limits (north facade cropped; roof edge not visible) and how that affects interpretation.

WRITING AND ACCESSIBILITY RULES:
- Present tense; American English; 25 words or fewer per sentence; no lists/bullets in the final output (only the Title plus three paragraphs).
- Start with plain language; introduce advanced terms only when useful, with a brief parenthetical gloss if unfamiliar.
- Colors: name plainly AND, when helpful, tie to common referents or patterns/textures (verdigris green, like weathered copper; alternating black-yellow hazard striping).
- Orientation: say viewer's left/right unless a north arrow or labels justify cardinal directions; for plans/sections, state top of page if north is unknown.
- Never refer to "this image/photo"; describe directly (A timber pavilion cantilevers over a shallow basin).
- People/privacy: describe count/position/clothing roles only if relevant to scale/use; do not speculate about identity or emotions.
- Units: mirror what is shown; otherwise prefer relative/proportional language over invented precision.

MEDIA-SPECIFIC EDGE CASES:
- Multi-panel/collage: Treat as one composition at Macro; in Meso/Micro, clearly differentiate panels in flowing prose (Left panel... Right panel...), not lists.
- Charts/graphs: Name chart type; decode axes, units, scales, ranges, trend shapes; explain what the data argues for in the architectural context.
- Simulations (CFD/energy/daylight/FEM): Translate color maps and vectors to phenomena (velocity, temperature, illuminance, stress), note scales/legends, call out hotspots and performance implications.
- Fabrication/craft images: Note tools, joints, tolerances, grain/knit/weave, surface treatments, likely feel and sound during use.
- Archival/historic images: Mention process (albumen print, engraving) if visible, condition (fading, patina), and any period cues in attire/vehicles/signage.

TEXT IN IMAGE (OPTIONAL ADD-ON):
If legible text exists, append AFTER the Micro layer:
  Text present: "<verbatim transcription>"
Note language if not English; do not translate unless asked."""


# ---------------------------------------------------------------------------
# Utility helpers
# ---------------------------------------------------------------------------

def _now():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def _script_dir():
    try:
        return os.path.dirname(os.path.abspath(__file__))
    except Exception:
        return os.getcwd()


def _get_api_key():
    """Read API key from environment or a .env file beside the script."""
    key = os.environ.get("ANTHROPIC_API_KEY", "").strip()
    if key:
        return key
    env_file = os.path.join(_script_dir(), ".env")
    if os.path.exists(env_file):
        with open(env_file, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line.startswith("ANTHROPIC_API_KEY="):
                    return line.split("=", 1)[1].strip().strip('"').strip("'")
    return ""


# ---------------------------------------------------------------------------
# Image loading
# ---------------------------------------------------------------------------

def _encode_local_image(path):
    """Read a local image file.  Returns (base64_data, media_type)."""
    abs_path = os.path.abspath(path)
    if not os.path.isfile(abs_path):
        raise FileNotFoundError(f"Image not found: {abs_path}")
    mime, _ = mimetypes.guess_type(abs_path)
    if mime not in SUPPORTED_MIME:
        raise ValueError(
            f"Unsupported image type '{mime}' for {os.path.basename(abs_path)}. "
            f"Supported: JPEG, PNG, GIF, WebP."
        )
    with open(abs_path, "rb") as f:
        data = base64.standard_b64encode(f.read()).decode("ascii")
    size_mb = os.path.getsize(abs_path) / (1024 * 1024)
    if size_mb > 20:
        raise ValueError(
            f"Image is {size_mb:.1f} MB. Claude accepts up to ~20 MB. "
            "Resize or compress the image first."
        )
    return data, mime


def _fetch_url_image(url):
    """Download an image from a URL.  Returns (base64_data, media_type)."""
    req = urllib.request.Request(url, headers={"User-Agent": "Arch-Alt-Text/1.0"})
    try:
        resp = urllib.request.urlopen(req, timeout=30)
    except urllib.error.URLError as e:
        raise ConnectionError(f"Could not fetch URL: {e}")
    ct = resp.headers.get("Content-Type", "").split(";")[0].strip()
    if ct not in SUPPORTED_MIME:
        raise ValueError(
            f"URL content type is '{ct}', not an image. "
            "Expected JPEG, PNG, GIF, or WebP."
        )
    raw = resp.read()
    data = base64.standard_b64encode(raw).decode("ascii")
    return data, ct


def _is_url(s):
    return s.startswith("http://") or s.startswith("https://")


def _resolve_image_path(source):
    """Clean up and resolve an image path.

    Strips surrounding quotes (Windows 'Copy as path' adds them),
    normalizes slashes, and checks both cwd and the script's own
    directory for relative paths.
    """
    # Strip surrounding quotes that Windows "Copy as path" adds
    source = source.strip().strip('"').strip("'")
    # Normalize path separators
    source = source.replace("\\", "/")
    # If already absolute and exists, return it
    if os.path.isabs(source):
        return source
    # Try relative to cwd first
    from_cwd = os.path.join(os.getcwd(), source)
    if os.path.isfile(from_cwd):
        return os.path.abspath(from_cwd)
    # Try relative to the script's own directory
    from_script = os.path.join(_script_dir(), source)
    if os.path.isfile(from_script):
        return os.path.abspath(from_script)
    # Return the cwd version (will fail with a clear error message)
    return os.path.abspath(from_cwd)


# ---------------------------------------------------------------------------
# API call
# ---------------------------------------------------------------------------

def _call_claude(api_key, image_data, media_type, model,
                  system_prompt=None, focus=""):
    """Send image to Claude Messages API.  Returns description text."""
    prompt = system_prompt if system_prompt else SYSTEM_PROMPT

    # Build the user message — add focus context if set
    if focus:
        user_text = "Context: " + focus + "\n\nDescribe this architectural image."
    else:
        user_text = "Describe this architectural image."

    payload = {
        "model": model,
        "max_tokens": MAX_TOKENS,
        "system": prompt,
        "messages": [
            {
                "role": "user",
                "content": [
                    {
                        "type": "image",
                        "source": {
                            "type": "base64",
                            "media_type": media_type,
                            "data": image_data,
                        },
                    },
                    {
                        "type": "text",
                        "text": user_text,
                    },
                ],
            }
        ],
    }

    body = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        API_URL,
        data=body,
        headers={
            "Content-Type": "application/json",
            "x-api-key": api_key,
            "anthropic-version": ANTHROPIC_VERSION,
        },
        method="POST",
    )

    try:
        resp = urllib.request.urlopen(req, timeout=120)
        result = json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        err_body = e.read().decode("utf-8", errors="replace")
        try:
            err_json = json.loads(err_body)
            msg = err_json.get("error", {}).get("message", err_body)
        except Exception:
            msg = err_body
        raise ConnectionError(f"API error ({e.code}): {msg}")
    except urllib.error.URLError as e:
        raise ConnectionError(f"Cannot reach API: {e}")

    blocks = [b["text"] for b in result.get("content", []) if b.get("type") == "text"]
    if not blocks:
        raise ValueError("API returned no text content.")
    return "\n".join(blocks)


# ---------------------------------------------------------------------------
# Describe — top-level function
# ---------------------------------------------------------------------------

def describe_image(api_key, source, model, system_prompt=None, focus=""):
    """Load image from path or URL, call API, return description."""
    if _is_url(source):
        image_data, media_type = _fetch_url_image(source)
    else:
        source = _resolve_image_path(source)
        image_data, media_type = _encode_local_image(source)
    return _call_claude(api_key, image_data, media_type, model,
                        system_prompt=system_prompt, focus=focus)


# ---------------------------------------------------------------------------
# History / archive
# ---------------------------------------------------------------------------

def _history_path():
    return os.path.join(_script_dir(), HISTORY_FILENAME)


def _load_history():
    path = _history_path()
    if not os.path.isfile(path):
        return []
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def _save_to_history(source, description):
    history = _load_history()
    history.append({
        "timestamp": _now(),
        "source": source,
        "description": description,
    })
    path = _history_path()
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(history, f, indent=2, ensure_ascii=False)
    os.replace(tmp, path)
    return len(history)


def _save_description_to_file(source, description):
    """Save the latest description as a plain-text file beside the image."""
    if _is_url(source):
        return None
    base = os.path.splitext(source)[0]
    txt_path = base + "_description.txt"
    tmp = txt_path + ".tmp"
    header = f"Arch-Alt-Text description\nSource: {source}\nDate: {_now()}\n\n"
    with open(tmp, "w", encoding="utf-8") as f:
        f.write(header + description + "\n")
    os.replace(tmp, txt_path)
    return txt_path


# ---------------------------------------------------------------------------
# Help text
# ---------------------------------------------------------------------------

HELP_TEXT = f"""
Arch-Alt-Text v{VERSION} — Architectural Image Description
Describes images for blind / low-vision architecture students.
Uses Claude vision API. Structured Macro / Meso / Micro output.

COMMANDS:
  describe <path-or-url> .... Describe an image file or URL
  mode ....................... Show current mode and list presets
  mode <name> ................ Switch to a preset (general, site-visit, design-studio, design-review, structures, history)
  focus ...................... Show current focus
  focus <your words> ......... Set a context overlay in your own words
  focus clear ................ Remove the focus
  last ....................... Repeat the last description
  save ....................... Save last description to a text file beside the image
  history .................... List all past descriptions
  history <n> ................ Show description number N
  model ...................... Show current model name
  model <name> ............... Change the Claude model
  help / h / ? ............... This message
  quit / q / exit ............ Exit

MODE PRESETS:
  general ............. Default prompt, works for any architectural image
  site-visit .......... On location. Wayfinding, materials, sounds, smells.
  design-studio ....... Peer work, sketches, models. What is being explored.
  design-review ....... Boards and crits. Board layout you can reference in conversation.
  structures .......... Lecture slides, FBDs, equations. Load paths and math.
  history ............. Lecture slides, engravings, photos. Period context and style.

FOCUS:
  Add context in your own words. This rides alongside each image.
  Example: focus steel connection detail, tell me about bolt patterns
  Example: focus I am in a courtyard and cannot see the roof
  Example: focus comparing two options side by side for studio tomorrow

EXAMPLES:
  mode site-visit
  focus construction joint at the base of a concrete column
  describe photo.jpg

SUPPORTED FORMATS:
  JPEG, PNG, GIF, WebP (up to ~20 MB)

SETUP:
  Set ANTHROPIC_API_KEY as an environment variable, or
  place a .env file next to this script containing:
    ANTHROPIC_API_KEY=sk-ant-...
"""


# ---------------------------------------------------------------------------
# Interactive REPL
# ---------------------------------------------------------------------------

def _run_interactive(api_key, model, initial_mode=DEFAULT_MODE,
                     initial_focus=""):
    """Main interactive loop."""
    current_mode = initial_mode
    current_focus = initial_focus
    active_prompt = _load_mode_prompt(current_mode) or SYSTEM_PROMPT

    print(f"Arch-Alt-Text v{VERSION} — Architectural Image Description")
    print(f"Model: {model}")
    print(f"Mode: {current_mode}")
    if current_focus:
        print(f"Focus: {current_focus}")
    print("Type 'help' for commands.")

    last_description = None
    last_source = None

    while True:
        try:
            raw = input(">> ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nExiting.")
            break

        if not raw:
            continue

        parts = raw.split(None, 1)
        cmd = parts[0].lower()
        arg = parts[1].strip() if len(parts) > 1 else ""

        # -- Exit --
        if cmd in ("quit", "q", "exit"):
            print("Exiting.")
            break

        # -- Help --
        if cmd in ("help", "h", "?"):
            print(HELP_TEXT)
            continue

        # -- Mode --
        if cmd == "mode":
            if not arg:
                print(f"Current mode: {current_mode}")
                modes = _list_modes()
                for name, available in modes:
                    marker = " (active)" if name == current_mode else ""
                    status = "" if available else " (file missing)"
                    print(f"  {name}{marker}{status}")
                print("READY:")
                continue
            name = arg.lower().strip()
            if name not in MODE_FILES:
                print(f"ERROR: Unknown mode '{name}'.")
                print("Available: " + ", ".join(MODE_FILES.keys()))
                continue
            loaded = _load_mode_prompt(name)
            if not loaded:
                print(f"ERROR: Prompt file for '{name}' not found.")
                continue
            current_mode = name
            active_prompt = loaded
            print(f"OK: Mode set to {current_mode}.")
            print("READY:")
            continue

        # -- Focus --
        if cmd == "focus":
            if not arg:
                if current_focus:
                    print(f"Focus: {current_focus}")
                else:
                    print("No focus set. Use 'focus <your words>' to add context.")
                print("READY:")
                continue
            if arg.lower() == "clear":
                current_focus = ""
                print("OK: Focus cleared.")
                print("READY:")
                continue
            current_focus = arg
            print(f"OK: Focus set to: {current_focus}")
            print("READY:")
            continue

        # -- Last --
        if cmd == "last":
            if last_description:
                print(last_description)
            else:
                print("ERROR: No description yet. Use 'describe <image>' first.")
            continue

        # -- Save --
        if cmd == "save":
            if not last_description or not last_source:
                print("ERROR: No description to save. Use 'describe <image>' first.")
                continue
            if _is_url(last_source):
                print("ERROR: Cannot auto-save for URL sources. Copy the text manually.")
                continue
            try:
                txt_path = _save_description_to_file(last_source, last_description)
                print(f"OK: Description saved to {txt_path}")
            except Exception as e:
                print(f"ERROR: {e}")
            continue

        # -- Model --
        if cmd == "model":
            if not arg:
                print(f"Model: {model}")
            else:
                model = arg
                print(f"OK: Model set to {model}.")
            continue

        # -- History --
        if cmd == "history":
            history = _load_history()
            if not history:
                print("No descriptions in history yet.")
                continue
            if arg:
                try:
                    idx = int(arg) - 1
                except ValueError:
                    print("ERROR: Provide a number. Example: history 3")
                    continue
                if idx < 0 or idx >= len(history):
                    print(f"ERROR: Out of range. History has {len(history)} entries.")
                    continue
                entry = history[idx]
                print(f"Source: {entry['source']}")
                print(f"Date: {entry['timestamp']}")
                print()
                print(entry["description"])
                continue
            for i, entry in enumerate(history, 1):
                first_line = entry["description"].split("\n")[0][:80]
                print(f"{i}. [{entry['timestamp']}] {entry['source']}")
                print(f"   {first_line}")
            continue

        # -- Describe --
        if cmd == "describe":
            if not arg:
                print("ERROR: Provide an image path or URL.")
                print("Example: describe photo.jpg")
                continue
            source = arg
        elif _is_url(raw):
            source = raw
        elif os.path.isfile(_resolve_image_path(raw)):
            # User typed a bare path without "describe"
            source = raw
        else:
            print(f"ERROR: Unknown command '{cmd}'. Type 'help' for commands.")
            continue

        # Resolve path (strips quotes, checks script dir too)
        if not _is_url(source):
            source = _resolve_image_path(source)

        status = f"Describing: {os.path.basename(source) if not _is_url(source) else source}"
        status += f" [mode: {current_mode}]"
        if current_focus:
            status += f" [focus: {current_focus}]"
        print(status)
        print("Processing... this may take a moment.")

        try:
            description = describe_image(
                api_key, source, model,
                system_prompt=active_prompt,
                focus=current_focus,
            )
            print()
            print(description)
            last_description = description
            last_source = source
            _save_to_history(source, description)
            count = len(_load_history())
            print(f"\nOK: Description complete. History entry {count}.")
            print("READY:")
        except FileNotFoundError as e:
            print(f"ERROR: {e}")
            print("Check the file path and try again.")
        except ValueError as e:
            print(f"ERROR: {e}")
        except ConnectionError as e:
            print(f"ERROR: {e}")
            print("Check your API key and internet connection.")
        except Exception as e:
            print(f"ERROR: Unexpected problem: {e}")


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main():
    ap = argparse.ArgumentParser(
        description="Arch-Alt-Text — Architectural image descriptions for blind users"
    )
    ap.add_argument(
        "image", nargs="?", default=None,
        help="Image file path or URL. Omit to enter interactive mode."
    )
    ap.add_argument(
        "--model", default=DEFAULT_MODEL,
        help=f"Claude model ID (default: {DEFAULT_MODEL})"
    )
    ap.add_argument(
        "--mode", default=DEFAULT_MODE,
        choices=list(MODE_FILES.keys()),
        help=f"Description mode preset (default: {DEFAULT_MODE})"
    )
    ap.add_argument(
        "--focus", default="",
        help="Context overlay in your own words, e.g. 'steel connection detail'"
    )
    ap.add_argument(
        "--json", action="store_true",
        help="Output JSON instead of plain text (single-shot mode only)"
    )
    ap.add_argument(
        "--no-history", action="store_true",
        help="Do not save this description to the history file"
    )
    ap.add_argument(
        "--save", action="store_true",
        help="Save description as a .txt file beside the image (single-shot only)"
    )
    args = ap.parse_args()

    # -- Check API key --
    api_key = _get_api_key()
    if not api_key:
        print("ERROR: No API key found.")
        print("Set the ANTHROPIC_API_KEY environment variable, or")
        print("create a .env file next to this script containing:")
        print("  ANTHROPIC_API_KEY=sk-ant-...")
        sys.exit(1)

    model = args.model

    # -- Load mode prompt --
    system_prompt = _load_mode_prompt(args.mode)
    if not system_prompt:
        if args.mode != DEFAULT_MODE:
            print(f"ERROR: Could not load prompt for mode '{args.mode}'. "
                  "Using default.")
        system_prompt = SYSTEM_PROMPT

    # -- Single-shot mode --
    if args.image:
        source = args.image
        if not _is_url(source):
            source = _resolve_image_path(source)

        try:
            description = describe_image(
                api_key, source, model,
                system_prompt=system_prompt,
                focus=args.focus,
            )
        except Exception as e:
            print(f"ERROR: {e}")
            sys.exit(1)

        if args.json:
            output = {
                "source": source,
                "timestamp": _now(),
                "model": model,
                "mode": args.mode,
                "focus": args.focus or None,
                "description": description,
            }
            print(json.dumps(output, indent=2, ensure_ascii=False))
        else:
            print(description)

        if not args.no_history:
            _save_to_history(source, description)

        if args.save and not _is_url(source):
            txt_path = _save_description_to_file(source, description)
            if txt_path:
                print(f"\nOK: Saved to {txt_path}")

        sys.exit(0)

    # -- Interactive mode --
    _run_interactive(api_key, model,
                     initial_mode=args.mode,
                     initial_focus=args.focus)


if __name__ == "__main__":
    main()
