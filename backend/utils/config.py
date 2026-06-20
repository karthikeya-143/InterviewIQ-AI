"""
Central configuration loaded from environment variables.
Model names and server settings can be overridden via .env file.
"""
import os
from pathlib import Path

try:
    from dotenv import load_dotenv
    load_dotenv(Path(__file__).resolve().parent.parent.parent / ".env")
except ImportError:
    pass

BACKEND_DIR = Path(__file__).resolve().parent.parent
PROJECT_ROOT = BACKEND_DIR.parent
DATA_DIR = BACKEND_DIR / "data"

HOST = os.getenv("HOST", "127.0.0.1")
PORT = int(os.getenv("PORT", "8000"))
WHISPER_MODEL = os.getenv("WHISPER_MODEL", "openai/whisper-tiny")
SBERT_MODEL = os.getenv("SBERT_MODEL", "all-MiniLM-L6-v2")
GENERATOR_MODEL = os.getenv("GENERATOR_MODEL", "google/flan-t5-small")
SESSIONS_FILE = DATA_DIR / "sessions.json"
