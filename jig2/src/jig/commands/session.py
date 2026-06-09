"""Session: owns the live state, the undo stack, and persistence."""

import copy
import json
import os

from jig.model.io import atomic_write, load_or_new, save_state
from jig.commands import registry

UNDO_LIMIT = 100


class Session:
    def __init__(self, state_path="state.json"):
        self.state_path = os.path.abspath(state_path)
        self.state = load_or_new(self.state_path)
        self.undo_stack = []

    # -- dispatch ---------------------------------------------------------

    def execute(self, line):
        """Run one command line. Returns the success message; raises
        registry.CommandError on failure."""
        return registry.dispatch(self, line)

    def run_mutation(self, spec, args, flags):
        backup = copy.deepcopy(self.state)
        try:
            message = spec.handler(self, args, flags)
        except Exception:
            self.state = backup  # never leave a half-mutated state
            raise
        self.undo_stack.append(backup)
        del self.undo_stack[:-UNDO_LIMIT]
        self.save()
        return message

    def run_script(self, lines):
        """Run several lines as one undo step; roll back all on first error."""
        backup = copy.deepcopy(self.state)
        outputs = []
        for line in lines:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            tokens = registry.tokenize(line)
            spec, rest = registry.find(tokens)
            if spec is None:
                self.state = backup
                raise registry.CommandError(
                    "script stopped, nothing changed. Unknown command: {}".format(line))
            args, flags = registry.split_flags(rest)
            try:
                outputs.append(spec.handler(self, args, flags))
            except Exception as exc:
                self.state = backup
                raise registry.CommandError(
                    "script stopped at {!r}, nothing changed: {}".format(line, exc))
        self.undo_stack.append(backup)
        del self.undo_stack[:-UNDO_LIMIT]
        self.save()
        return outputs

    # -- persistence ------------------------------------------------------

    def save(self):
        save_state(self.state, self.state_path)

    def undo(self, steps=1):
        if not self.undo_stack:
            raise registry.CommandError("nothing to undo")
        steps = min(int(steps), len(self.undo_stack))
        for _ in range(steps):
            self.state = self.undo_stack.pop()
        self.save()
        return steps

    # -- snapshots --------------------------------------------------------

    @property
    def snapshot_dir(self):
        return os.path.join(os.path.dirname(self.state_path), "snapshots")

    def snapshot_path(self, name):
        safe = "".join(ch for ch in name if ch.isalnum() or ch in "-_")
        if not safe:
            raise registry.CommandError("snapshot name must use letters, numbers, hyphens")
        return os.path.join(self.snapshot_dir, safe + ".json")

    def snapshot_save(self, name):
        os.makedirs(self.snapshot_dir, exist_ok=True)
        atomic_write(self.snapshot_path(name),
                     json.dumps(self.state.to_dict(), indent=2) + "\n")

    def snapshot_list(self):
        if not os.path.isdir(self.snapshot_dir):
            return []
        return sorted(f[:-5] for f in os.listdir(self.snapshot_dir)
                      if f.endswith(".json"))
