"""Optional spoken output via the macOS say command. No-op elsewhere."""

import subprocess
import sys


def speak(text):
    if sys.platform != "darwin":
        return
    try:
        subprocess.Popen(["say", text])
    except OSError:
        pass
