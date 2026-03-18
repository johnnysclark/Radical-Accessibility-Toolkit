# -*- coding: utf-8 -*-
"""
Cross-platform compatibility layer for RAP Rhino scripts.
==========================================================
Works in both IronPython 2.7 (Rhino 8 Windows) and CPython 3.x (Rhino 8 Mac).

Import this module before using platform-specific features.
No f-strings.  No pathlib.  .format() only.

Usage in rhino_watcher.py:
    from compat import chime, speak, make_guid, find_rhino_object
"""
import os
import subprocess
import sys

# ── Platform detection ────────────────────────────────────
# IronPython sets sys.platform to "cli" and includes "IronPython"
# in sys.version.  CPython on Mac sets sys.platform to "darwin".

IS_IRONPYTHON = (sys.platform == "cli"
                 or "IronPython" in sys.version)
IS_CPYTHON = not IS_IRONPYTHON
IS_MAC = (os.name == "posix" and "darwin" in sys.platform.lower()) if IS_CPYTHON else False
IS_WINDOWS = (os.name == "nt") or (sys.platform == "cli")

# ── CLR / .NET imports (IronPython only) ──────────────────

_System = None

if IS_IRONPYTHON:
    try:
        import clr
        clr.AddReference("RhinoCommon")
        import System
        _System = System
    except Exception:
        pass
else:
    # Rhino 8 Mac CPython may provide System via pythonnet.
    # Try it; if unavailable we fall back to uuid.
    try:
        import System
        _System = System
    except ImportError:
        pass

# ── GUID helpers ──────────────────────────────────────────

def make_guid(guid_string):
    """Create a GUID object from a string.

    Returns a System.Guid on IronPython or when pythonnet is available.
    Falls back to uuid.UUID on CPython without pythonnet.
    """
    if _System is not None:
        return _System.Guid(str(guid_string))
    import uuid
    return uuid.UUID(str(guid_string))


def find_rhino_object(doc, guid_string):
    """Find a RhinoObject by GUID string, cross-platform.

    Args:
        doc: scriptcontext.doc (the active Rhino document).
        guid_string: String representation of the object GUID.

    Returns:
        The RhinoObject, or None if not found.
    """
    guid = make_guid(guid_string)
    try:
        return doc.Objects.FindId(guid)
    except Exception:
        return None

# ── Audio feedback ────────────────────────────────────────

def chime():
    """Play a short audio chime.  Non-blocking, fire-and-forget."""
    try:
        if IS_WINDOWS:
            subprocess.Popen(
                ["powershell", "-NoProfile", "-Command",
                 "[System.Console]::Beep(880, 120)"],
                stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        elif IS_MAC:
            subprocess.Popen(
                ["afplay", "/System/Library/Sounds/Tink.aiff"],
                stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except Exception:
        pass


def speak(text, rate=3):
    """Speak text via platform TTS.  Non-blocking, fire-and-forget.

    Args:
        text: The text to speak.
        rate: Speech rate.  Windows: -10..10.  Mac: mapped to words-per-minute.
    """
    try:
        if IS_WINDOWS:
            escaped = text.replace("'", "''")
            ps_cmd = (
                "Add-Type -AssemblyName System.Speech;"
                "$s=New-Object System.Speech.Synthesis.SpeechSynthesizer;"
                "$s.Rate={0};"
                "$s.Speak('{1}')").format(rate, escaped)
            subprocess.Popen(
                ["powershell", "-NoProfile", "-Command", ps_cmd],
                stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        elif IS_MAC:
            # Map rate (-10..10) to say WPM.  Default ~220 wpm.
            wpm = 180 + int(rate) * 20
            subprocess.Popen(
                ["say", "-r", str(wpm), text],
                stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except Exception:
        pass
