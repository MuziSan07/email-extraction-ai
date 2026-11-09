"""Environment-driven configuration.

All secrets and deployment-specific values are read from environment
variables (optionally loaded from a local ``.env`` file). Nothing sensitive
is hard-coded in the source tree.
"""

import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()


def _as_bool(value: str) -> bool:
    return value.strip().lower() in {"1", "true", "yes", "on"}


# --- Paths -----------------------------------------------------------------
BASE_DIR = Path(__file__).resolve().parent
TEMPLATES_DIR = BASE_DIR / "view" / "templates"
STATIC_DIR = BASE_DIR / "view" / "static"
PROJECT_ROOT = BASE_DIR.parent

# --- Database --------------------------------------------------------------
DB_PATH = os.getenv("DB_PATH", str(PROJECT_ROOT / "business_contacts.db"))

# --- Groq / LLM ------------------------------------------------------------
# Required for extraction. Get a key at https://console.groq.com
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_MODEL = os.getenv("GROQ_MODEL", "openai/gpt-oss-120b")
GROQ_TEMPERATURE = float(os.getenv("GROQ_TEMPERATURE", "0"))

# --- Limits ----------------------------------------------------------------
MAX_EMAIL_LENGTH = int(os.getenv("MAX_EMAIL_LENGTH", "20000"))

# --- Admin auth (HTTP Basic) ----------------------------------------------
# If BOTH are set, the admin panel, delete route, and Gmail routes require
# these credentials. If either is unset, those routes are open and a warning
# is logged at startup.
ADMIN_USERNAME = os.getenv("ADMIN_USERNAME")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD")
ADMIN_AUTH_ENABLED = bool(ADMIN_USERNAME and ADMIN_PASSWORD)

# --- CORS ------------------------------------------------------------------
CORS_ORIGINS = [
    origin.strip()
    for origin in os.getenv(
        "CORS_ORIGINS", "http://localhost:8000,http://127.0.0.1:8000"
    ).split(",")
    if origin.strip()
]

# --- Gmail / OAuth ---------------------------------------------------------
GOOGLE_CREDENTIALS_FILE = os.getenv("GOOGLE_CREDENTIALS_FILE", "credentials.json")
GOOGLE_TOKEN_FILE = os.getenv("GOOGLE_TOKEN_FILE", "token.json")
OAUTH_REDIRECT_URI = os.getenv(
    "OAUTH_REDIRECT_URI", "http://localhost:8000/oauth2callback"
)
GMAIL_SCOPES = ["https://www.googleapis.com/auth/gmail.readonly"]
GMAIL_MAX_RESULTS = int(os.getenv("GMAIL_MAX_RESULTS", "10"))

# Allow plain HTTP during the OAuth flow (local development only). Never
# enable this in production.
OAUTH_INSECURE_TRANSPORT = _as_bool(os.getenv("OAUTH_INSECURE_TRANSPORT", "false"))
