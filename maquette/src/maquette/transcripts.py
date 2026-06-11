"""Chat transcripts: a plain text file for people, a JSONL twin for tools.

Every chat session writes transcripts/<date>-<time>.txt with
role-prefixed lines (YOU:, CLAUDE:, plus OK:/ERROR: tool lines kept
verbatim) and a .jsonl file with one {ts, role, text} object per line.
"""

from __future__ import annotations

import datetime
import json
import os


class Transcript:
    def __init__(self, directory: str):
        os.makedirs(directory, exist_ok=True)
        stamp = datetime.datetime.now().strftime("%Y-%m-%d-%H%M%S")
        self.text_path = os.path.join(directory, stamp + ".txt")
        self.jsonl_path = os.path.join(directory, stamp + ".jsonl")
        self._text = open(self.text_path, "a", encoding="utf-8")
        self._jsonl = open(self.jsonl_path, "a", encoding="utf-8")

    def write(self, role: str, text: str) -> None:
        text = text.rstrip()
        if not text:
            return
        if role in ("YOU", "CLAUDE"):
            self._text.write("{0}: {1}\n".format(role, text))
        else:  # tool and status lines already carry OK:/ERROR: prefixes
            self._text.write(text + "\n")
        self._jsonl.write(json.dumps({
            "ts": datetime.datetime.now().isoformat(timespec="seconds"),
            "role": role, "text": text}) + "\n")
        self._text.flush()
        self._jsonl.flush()

    def close(self) -> None:
        self._text.close()
        self._jsonl.close()
