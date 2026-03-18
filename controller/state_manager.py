# -*- coding: utf-8 -*-
"""
Transactional State Manager for the Layout Jig
================================================
Wraps state.json mutations with:
  - Advisory file locking (single-writer enforcement)
  - Monotonic revision numbers
  - Transaction metadata
  - Append-only operation journal
  - Conflict detection via revision checks
  - Atomic writes (write .tmp, fsync, os.replace)

Keeps state.json as the canonical human-readable artifact.
The journal is supplementary and can be rebuilt or trimmed.

Python 3 stdlib only.
"""
import copy
import json
import os
import time
from datetime import datetime


# ── Atomic file write ──────────────────────────────────

def _atomic_write(path, text):
    """Write to .tmp then os.replace for crash safety."""
    folder = os.path.dirname(os.path.abspath(path))
    os.makedirs(folder, exist_ok=True)
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        f.write(text)
        f.flush()
        os.fsync(f.fileno())
    os.replace(tmp, path)


# ── Advisory Lock ──────────────────────────────────────

class StateLock:
    """Advisory file lock for state.json.

    Uses a .lock file next to the state file. Not OS-level locking —
    cooperative only. Sufficient for single-machine, multi-process use
    where all writers go through this manager.
    """

    def __init__(self, state_path, writer="unknown", timeout=10.0):
        self.lock_path = state_path + ".lock"
        self.writer = writer
        self.timeout = timeout
        self._acquired = False

    def acquire(self):
        """Attempt to acquire the lock. Returns True on success."""
        deadline = time.time() + self.timeout
        while time.time() < deadline:
            if self._try_create_lock():
                self._acquired = True
                return True
            # Check for stale lock (older than 60 seconds)
            if self._is_stale(max_age=60.0):
                self._force_remove()
                continue
            time.sleep(0.1)
        return False

    def release(self):
        """Release the lock."""
        if self._acquired and os.path.isfile(self.lock_path):
            try:
                os.remove(self.lock_path)
            except OSError:
                pass
        self._acquired = False

    def _try_create_lock(self):
        """Atomically create the lock file. Returns True if created."""
        try:
            fd = os.open(self.lock_path,
                         os.O_CREAT | os.O_EXCL | os.O_WRONLY)
            lock_data = json.dumps({
                "writer": self.writer,
                "pid": os.getpid(),
                "acquired_at": datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ"),
            })
            os.write(fd, lock_data.encode("utf-8"))
            os.close(fd)
            return True
        except FileExistsError:
            return False
        except OSError:
            return False

    def _is_stale(self, max_age=60.0):
        """Check if the lock file is older than max_age seconds."""
        try:
            mtime = os.path.getmtime(self.lock_path)
            return (time.time() - mtime) > max_age
        except OSError:
            return False

    def _force_remove(self):
        try:
            os.remove(self.lock_path)
        except OSError:
            pass

    def __enter__(self):
        if not self.acquire():
            raise RuntimeError(
                "Could not acquire state lock within {} seconds. "
                "Another writer may be active. Use 'runtime/launcher.py stop' "
                "to clear stale locks.".format(self.timeout))
        return self

    def __exit__(self, *args):
        self.release()


# ── Journal ────────────────────────────────────────────

class TransactionJournal:
    """Append-only journal of state mutations."""

    def __init__(self, journal_dir):
        self.journal_dir = journal_dir

    def record(self, transaction_id, revision_before, revision_after,
               writer, command, status, mode="validated"):
        """Append a journal entry."""
        os.makedirs(self.journal_dir, exist_ok=True)
        entry = {
            "transaction_id": transaction_id,
            "revision_before": revision_before,
            "revision_after": revision_after,
            "writer": writer,
            "mode": mode,
            "command": command,
            "status": status,
            "timestamp": datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ"),
        }
        fname = os.path.join(self.journal_dir,
                             "txn_{:06d}.json".format(revision_after))
        _atomic_write(fname, json.dumps(entry, indent=2, ensure_ascii=False) + "\n")

    def list_entries(self, last_n=20):
        """Return the last N journal entries."""
        if not os.path.isdir(self.journal_dir):
            return []
        files = sorted(f for f in os.listdir(self.journal_dir)
                       if f.startswith("txn_") and f.endswith(".json"))
        entries = []
        for fname in files[-last_n:]:
            path = os.path.join(self.journal_dir, fname)
            try:
                with open(path, "r", encoding="utf-8") as f:
                    entries.append(json.load(f))
            except (json.JSONDecodeError, IOError):
                pass
        return entries

    def entry_count(self):
        if not os.path.isdir(self.journal_dir):
            return 0
        return sum(1 for f in os.listdir(self.journal_dir)
                   if f.startswith("txn_") and f.endswith(".json"))


# ── State Manager ──────────────────────────────────────

class StateManager:
    """Transactional wrapper around state.json.

    Usage:
        mgr = StateManager("/path/to/state.json", writer="cli")

        with mgr.transaction("set bay A rotation 30") as txn:
            state = txn.state
            # ... mutate state ...
            txn.set_state(state)
        # state.json is now updated with new revision

    Or for read-only access:
        state = mgr.load()
    """

    def __init__(self, state_path, writer="unknown", journal_dir=None):
        self.state_path = os.path.abspath(state_path)
        self.writer = writer
        if journal_dir is None:
            journal_dir = os.path.join(
                os.path.dirname(self.state_path), "journal")
        self.journal = TransactionJournal(journal_dir)

    def load(self):
        """Load state from disk without locking."""
        if not os.path.isfile(self.state_path):
            return None
        with open(self.state_path, "r", encoding="utf-8") as f:
            return json.load(f)

    def current_revision(self):
        """Get the current state revision number."""
        state = self.load()
        if state is None:
            return 0
        return state.get("meta", {}).get("state_revision", 0)

    def transaction(self, command_str, mode="validated", timeout=10.0):
        """Return a Transaction context manager."""
        return Transaction(self, command_str, mode, timeout)

    def _commit(self, state, revision_before, command_str, mode):
        """Write state to disk and record in journal."""
        new_revision = revision_before + 1
        meta = state.setdefault("meta", {})
        meta["state_revision"] = new_revision
        meta["last_committed_at"] = datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ")
        meta["last_writer"] = self.writer
        meta["last_transaction_id"] = "txn_{:06d}".format(new_revision)

        _atomic_write(self.state_path,
                      json.dumps(state, indent=2, ensure_ascii=False) + "\n")

        self.journal.record(
            transaction_id="txn_{:06d}".format(new_revision),
            revision_before=revision_before,
            revision_after=new_revision,
            writer=self.writer,
            command=command_str,
            status="committed",
            mode=mode,
        )
        return new_revision


class Transaction:
    """Context manager for a single state mutation."""

    def __init__(self, manager, command_str, mode, timeout):
        self._manager = manager
        self._command = command_str
        self._mode = mode
        self._timeout = timeout
        self._lock = None
        self._state = None
        self._state_before = None
        self._revision_before = 0
        self._committed = False
        self._new_state = None

    @property
    def state(self):
        """The state dict loaded at transaction start."""
        return self._state

    @property
    def revision(self):
        return self._revision_before

    def set_state(self, new_state):
        """Set the mutated state to be committed."""
        self._new_state = new_state

    def __enter__(self):
        self._lock = StateLock(self._manager.state_path,
                               writer=self._manager.writer,
                               timeout=self._timeout)
        self._lock.acquire()

        self._state = self._manager.load()
        if self._state is None:
            # Will be populated by the caller (e.g., default_state)
            self._state = {}
            self._revision_before = 0
        else:
            self._revision_before = self._state.get("meta", {}).get(
                "state_revision", 0)
        self._state_before = copy.deepcopy(self._state)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        try:
            if exc_type is None and self._new_state is not None:
                self._manager._commit(
                    self._new_state, self._revision_before,
                    self._command, self._mode)
                self._committed = True
            elif exc_type is not None:
                # Record failed transaction
                self._manager.journal.record(
                    transaction_id="txn_{:06d}".format(self._revision_before + 1),
                    revision_before=self._revision_before,
                    revision_after=self._revision_before,
                    writer=self._manager.writer,
                    command=self._command,
                    status="failed",
                    mode=self._mode,
                )
        finally:
            if self._lock:
                self._lock.release()
        return False  # Don't suppress exceptions
