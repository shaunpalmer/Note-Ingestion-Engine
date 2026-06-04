"""
state_manager.py
Purpose: Thread-safe state management with file locking.
Uses filelock for cross-process safety and atomic writes for crash resilience.
"""

from __future__ import annotations

import json
import os
import tempfile
from pathlib import Path

from filelock import FileLock

from .config import get_state_dir
from .models import PipelineState, StateEntry


# ---------------------------------------------------------------------------
# State Manager
# ---------------------------------------------------------------------------

class StateManager:
    """Manages pipeline state with file locking and atomic writes."""

    def __init__(self, state_path: Path | None = None) -> None:
        self.state_path = state_path or get_state_dir() / "processed-files.json"
        self.lock_path = self.state_path.with_suffix(".json.lock")
        self.lock = FileLock(str(self.lock_path), timeout=10)

    def load(self) -> PipelineState:
        """Load state from disk, acquiring the file lock."""
        with self.lock:
            if not self.state_path.exists():
                return PipelineState()
            with open(self.state_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            return PipelineState.model_validate(data)

    def save(self, state: PipelineState) -> None:
        """Save state atomically: write to temp, then replace."""
        with self.lock:
            # Write to a temporary file in the same directory (atomic on same filesystem)
            fd, temp_path = tempfile.mkstemp(
                dir=self.state_path.parent,
                prefix=".state_tmp_",
                suffix=".json",
            )
            try:
                with os.fdopen(fd, "w", encoding="utf-8") as f:
                    json.dump(state.model_dump(mode="json"), f, indent=2)
                # Atomic rename
                os.replace(temp_path, self.state_path)
            except Exception:
                # Clean up temp file on failure
                try:
                    os.unlink(temp_path)
                except OSError:
                    pass
                raise

    def get_entry(self, sha256: str) -> StateEntry | None:
        """Retrieve a single entry by hash."""
        state = self.load()
        return state.entries.get(sha256)

    def upsert_entry(self, entry: StateEntry) -> None:
        """Insert or update an entry, then persist."""
        state = self.load()
        state.entries[entry.sha256] = entry
        state.last_updated = __import__("datetime").datetime.now()
        self.save(state)

    def get_unprocessed(self) -> list[StateEntry]:
        """Return all entries with status 'queued'."""
        state = self.load()
        return [e for e in state.entries.values() if e.status == "queued"]

    def sha_exists(self, sha256: str) -> bool:
        """Check if a hash is already known without loading full state."""
        # Fast path: check without lock for read-only operations
        if not self.state_path.exists():
            return False
        with self.lock:
            with open(self.state_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            return sha256 in data.get("entries", {})
