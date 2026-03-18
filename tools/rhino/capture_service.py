# -*- coding: utf-8 -*-
"""
Capture Service — First-class capture/render artifact subsystem.
=================================================================
Manages repeatable high-resolution captures from named presets.
Produces both image files and structured status/manifests.

The service works in two modes:
  1. Via Rhino (connected): sends capture commands to Rhino
  2. Offline: generates manifest stubs and status without images

Python 3 stdlib only.
"""
import json
import os
import time
from datetime import datetime


def _atomic_write(path, text):
    folder = os.path.dirname(os.path.abspath(path))
    os.makedirs(folder, exist_ok=True)
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        f.write(text)
        f.flush()
        os.fsync(f.fileno())
    os.replace(tmp, path)


class CaptureService:
    """Manages capture jobs, manifests, and status."""

    def __init__(self, captures_dir, state_path=None, rhino_client=None):
        """
        Args:
            captures_dir: Directory for output images and manifests
            state_path: Path to state.json (for revision tracking)
            rhino_client: Optional rhino_client module for live captures
        """
        self.captures_dir = os.path.abspath(captures_dir)
        self.state_path = state_path
        self.rhino_client = rhino_client
        self.manifest_path = os.path.join(self.captures_dir, "manifest.json")
        self.status_path = os.path.join(self.captures_dir, "latest_status.json")

    def _get_state_revision(self):
        """Read current state revision from state.json."""
        if not self.state_path or not os.path.isfile(self.state_path):
            return None
        try:
            with open(self.state_path, "r", encoding="utf-8") as f:
                state = json.load(f)
            return state.get("meta", {}).get("state_revision")
        except (json.JSONDecodeError, IOError):
            return None

    def _rhino_available(self):
        """Check if Rhino is reachable."""
        if self.rhino_client is None:
            return False
        try:
            status = self.rhino_client.status()
            return "ONLINE" in str(status).upper()
        except Exception:
            return False

    def capture_one(self, preset):
        """Execute a single capture job.

        Returns a result dict:
          {"id": str, "status": "ok"|"error"|"skipped", "path": str, "message": str}
        """
        preset_id = preset.get("id", "unnamed")
        output_path = preset.get("output", "")
        if not output_path:
            return {"id": preset_id, "status": "error",
                    "path": "", "message": "No output path specified."}

        # Make output path absolute relative to captures_dir
        if not os.path.isabs(output_path):
            output_path = os.path.join(self.captures_dir, os.path.basename(output_path))

        if not preset.get("enabled", True):
            return {"id": preset_id, "status": "skipped",
                    "path": output_path, "message": "Preset disabled."}

        if not self._rhino_available():
            return {"id": preset_id, "status": "error",
                    "path": output_path,
                    "message": "Rhino is offline. Cannot capture."}

        # Attempt capture via Rhino client
        try:
            script = self._build_capture_script(preset, output_path)
            result = self.rhino_client.run_script(script)
            if os.path.isfile(output_path):
                return {"id": preset_id, "status": "ok",
                        "path": output_path,
                        "message": "Captured successfully."}
            else:
                return {"id": preset_id, "status": "error",
                        "path": output_path,
                        "message": "Rhino script ran but output file not found."}
        except Exception as e:
            return {"id": preset_id, "status": "error",
                    "path": output_path,
                    "message": "Capture failed: {}.".format(e)}

    def _build_capture_script(self, preset, output_path):
        """Build a RhinoScript command string for ViewCaptureToFile."""
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        width = preset.get("width", 4000)
        height = preset.get("height", 3000)
        view = preset.get("named_view", "Top")
        display = preset.get("display_mode", "Wireframe")
        # This generates a Rhino command-line macro
        lines = [
            "-SetView World {}".format(view),
            "-ViewCaptureToFile \"{}\" Width={} Height={} DrawGrid=No DrawAxis=No".format(
                output_path.replace("\\", "/"), width, height),
        ]
        return "\n".join(lines)

    def capture_all(self, presets):
        """Execute all enabled capture jobs.

        Returns a status dict with manifest and per-job results.
        """
        timestamp = datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ")
        revision = self._get_state_revision()

        results = []
        for preset in presets:
            if preset.get("enabled", True):
                results.append(self.capture_one(preset))
            else:
                results.append({
                    "id": preset.get("id", "unnamed"),
                    "status": "skipped",
                    "path": preset.get("output", ""),
                    "message": "Preset disabled."
                })

        status = {
            "state_revision": revision,
            "timestamp": timestamp,
            "rhino_available": self._rhino_available(),
            "total": len(results),
            "ok": sum(1 for r in results if r["status"] == "ok"),
            "errors": sum(1 for r in results if r["status"] == "error"),
            "skipped": sum(1 for r in results if r["status"] == "skipped"),
            "captures": results,
        }

        # Write manifest and status
        self._write_manifest(status)
        self._write_status(status)

        return status

    def _write_manifest(self, status):
        """Append to or create the capture manifest."""
        os.makedirs(self.captures_dir, exist_ok=True)
        manifest = {"runs": []}
        if os.path.isfile(self.manifest_path):
            try:
                with open(self.manifest_path, "r", encoding="utf-8") as f:
                    manifest = json.load(f)
            except (json.JSONDecodeError, IOError):
                manifest = {"runs": []}

        manifest["runs"].append(status)
        # Keep last 50 runs
        if len(manifest["runs"]) > 50:
            manifest["runs"] = manifest["runs"][-50:]

        _atomic_write(self.manifest_path,
                      json.dumps(manifest, indent=2, ensure_ascii=False) + "\n")

    def _write_status(self, status):
        """Write latest status file."""
        os.makedirs(self.captures_dir, exist_ok=True)
        _atomic_write(self.status_path,
                      json.dumps(status, indent=2, ensure_ascii=False) + "\n")

    def get_status(self):
        """Read the latest capture status."""
        if not os.path.isfile(self.status_path):
            return {"message": "No captures have been run yet."}
        try:
            with open(self.status_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            return {"message": "Could not read capture status."}

    def format_status(self, status=None):
        """Format capture status as screen-reader-friendly text."""
        if status is None:
            status = self.get_status()
        if "message" in status and "captures" not in status:
            return "OK: {}".format(status["message"])

        lines = []
        lines.append("Capture status (revision {}, {}):".format(
            status.get("state_revision", "unknown"),
            status.get("timestamp", "unknown")))
        lines.append("  {} total, {} ok, {} errors, {} skipped.".format(
            status.get("total", 0),
            status.get("ok", 0),
            status.get("errors", 0),
            status.get("skipped", 0)))
        for cap in status.get("captures", []):
            lines.append("  {}: {} — {}".format(
                cap.get("id", "?"),
                cap.get("status", "?"),
                cap.get("message", "")))
        return "\n".join(lines)
