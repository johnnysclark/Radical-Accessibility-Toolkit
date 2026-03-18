# -*- coding: utf-8 -*-
"""
Capture Presets — Named view/render presets for the capture subsystem.
======================================================================
Manages capture job definitions: named views, display modes,
resolution, format, and output paths.

Presets are stored in state.json under "capture_jobs" or in
a separate captures/capture_config.json file.

Python 3 stdlib only.
"""
import json
import os

DEFAULT_PRESETS = [
    {
        "id": "plan_technical",
        "enabled": True,
        "named_view": "Top",
        "display_mode": "Technical",
        "width": 4000,
        "height": 3000,
        "format": "png",
        "output": "captures/plan_technical.png",
        "description": "Top-down technical plan view.",
    },
    {
        "id": "axon_technical",
        "enabled": True,
        "named_view": "Perspective",
        "display_mode": "Technical",
        "width": 4000,
        "height": 3000,
        "format": "png",
        "output": "captures/axon_technical.png",
        "description": "Axonometric technical view.",
    },
    {
        "id": "perspective_pen",
        "enabled": False,
        "named_view": "Perspective",
        "display_mode": "Pen",
        "width": 5000,
        "height": 3500,
        "format": "png",
        "output": "captures/perspective_pen.png",
        "description": "Perspective pen-style rendering.",
    },
]


def _atomic_write(path, text):
    folder = os.path.dirname(os.path.abspath(path))
    os.makedirs(folder, exist_ok=True)
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        f.write(text)
        f.flush()
        os.fsync(f.fileno())
    os.replace(tmp, path)


class CapturePresetManager:
    """Manages capture job presets."""

    def __init__(self, config_path=None, state=None):
        """Load presets from config file or state dict.

        Args:
            config_path: Path to captures/capture_config.json
            state: State dict (uses capture_jobs key)
        """
        self._config_path = config_path
        self._presets = []
        if state and "capture_jobs" in state:
            self._presets = list(state["capture_jobs"])
        elif config_path and os.path.isfile(config_path):
            self._load_from_file(config_path)
        else:
            self._presets = list(DEFAULT_PRESETS)

    def _load_from_file(self, path):
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
            self._presets = data.get("capture_jobs", [])
        except (json.JSONDecodeError, IOError):
            self._presets = list(DEFAULT_PRESETS)

    def list_presets(self):
        """Return list of all preset dicts."""
        return list(self._presets)

    def get_preset(self, preset_id):
        """Get a preset by ID. Returns None if not found."""
        for p in self._presets:
            if p.get("id") == preset_id:
                return dict(p)
        return None

    def add_preset(self, preset):
        """Add or update a preset."""
        preset_id = preset.get("id")
        if not preset_id:
            raise ValueError("Preset must have an 'id'.")
        # Remove existing with same id
        self._presets = [p for p in self._presets if p.get("id") != preset_id]
        self._presets.append(preset)

    def remove_preset(self, preset_id):
        """Remove a preset by ID. Returns True if removed."""
        before = len(self._presets)
        self._presets = [p for p in self._presets if p.get("id") != preset_id]
        return len(self._presets) < before

    def set_field(self, preset_id, field, value):
        """Set a field on an existing preset."""
        for p in self._presets:
            if p.get("id") == preset_id:
                p[field] = value
                return True
        return False

    def enabled_presets(self):
        """Return only enabled presets."""
        return [p for p in self._presets if p.get("enabled", True)]

    def save_to_file(self, path=None):
        """Save presets to a JSON config file."""
        path = path or self._config_path
        if not path:
            raise ValueError("No config path specified.")
        data = {"capture_jobs": self._presets}
        _atomic_write(path, json.dumps(data, indent=2, ensure_ascii=False) + "\n")

    def to_state_section(self):
        """Return the presets list for embedding in state.json."""
        return list(self._presets)

    def format_list(self):
        """Format presets as screen-reader-friendly text."""
        if not self._presets:
            return "OK: No capture presets defined."
        lines = ["OK: {} capture presets:".format(len(self._presets))]
        for i, p in enumerate(self._presets, 1):
            status = "enabled" if p.get("enabled", True) else "disabled"
            lines.append("  {}. {} — {} ({}, {}x{}, {})".format(
                i, p.get("id", "unnamed"),
                p.get("description", ""),
                status,
                p.get("width", 0), p.get("height", 0),
                p.get("format", "png")))
        return "\n".join(lines)
