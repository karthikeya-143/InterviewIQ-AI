"""
File-backed session store for mock interview sessions.
Persists to backend/data/sessions.json so sessions survive server restarts.
"""
import json
import threading
from pathlib import Path
from utils.config import SESSIONS_FILE, DATA_DIR

DATA_DIR.mkdir(parents=True, exist_ok=True)


class SessionStore:
    """Thread-safe in-memory store with JSON file persistence."""

    def __init__(self, file_path: Path = SESSIONS_FILE):
        self.file_path = file_path
        self._lock = threading.Lock()
        self._sessions: dict = {}
        self._load()

    def _load(self) -> None:
        if self.file_path.exists():
            try:
                with open(self.file_path, "r", encoding="utf-8") as f:
                    self._sessions = json.load(f)
            except (json.JSONDecodeError, OSError):
                self._sessions = {}

    def _save(self) -> None:
        with open(self.file_path, "w", encoding="utf-8") as f:
            json.dump(self._sessions, f, indent=2, default=str)

    def __contains__(self, key: str) -> bool:
        return key in self._sessions

    def __getitem__(self, key: str) -> dict:
        return self._sessions[key]

    def __setitem__(self, key: str, value: dict) -> None:
        with self._lock:
            self._sessions[key] = value
            self._save()

    def get(self, key: str, default=None):
        return self._sessions.get(key, default)

    def persist(self, session_id: str) -> None:
        """Persist after in-place mutations to an existing session."""
        with self._lock:
            if session_id in self._sessions:
                self._save()


# Shared singleton used across all route modules
sessions_db = SessionStore()
