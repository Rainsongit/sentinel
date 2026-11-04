import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

ROOT = Path(__file__).resolve().parent.parent
DOMAINS_DIR = ROOT / "domains"
LOG_DIR = ROOT / "logs"

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
SMALL_MODEL = os.getenv("SMALL_MODEL", "openai/gpt-oss-20b")
LARGE_MODEL = os.getenv("LARGE_MODEL", "openai/gpt-oss-120b")
EMBED_MODEL = "sentence-transformers/all-MiniLM-L6-v2"

# USD per 1M tokens (input, output). Groq list prices, Oct 2026. Update if they change.
PRICES = {
    "openai/gpt-oss-20b": (0.075, 0.30),
    "openai/gpt-oss-120b": (0.15, 0.60),
}

TOP_K = 3
CACHE_THRESHOLD = 0.90
CACHE_TTL_SECONDS = 3600
MAX_TOOL_ROUNDS = 3
INJECTION_THRESHOLD = 2
