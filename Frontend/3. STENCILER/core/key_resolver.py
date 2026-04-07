"""
Key Resolver — Mission 137
Résout les clés API : 1. clé user en DB (BYOK) → 2. fallback .env
"""

import os
import sqlite3
from pathlib import Path
from typing import Optional

# --- PATHS ---
CWD = Path(__file__).parent.parent.resolve()
ROOT_DIR = CWD.parent.parent
PROJECTS_DB_PATH = ROOT_DIR / "db/projects.db"

# Map provider → env var
ENV_MAP = {
    "gemini": "GOOGLE_API_KEY",
    "groq": "GROQ_API_KEY",
    "openai": "OPENAI_API_KEY",
    "mimo": "MIMO_KEY",
    "qwen": "QWEN_KEY",
    "kimi": "KIMI_KEY",
    "deepseek": "DEEPSEEK_API_KEY",
    "watson": "WATSON_API_KEY",
    "codestral": "MISTRAL_API_KEY",
}


def resolve_key(provider: str, user_id: Optional[str] = None) -> Optional[str]:
    """
    Priorité : 1. clé user en DB (BYOK) → 2. .env
    Retourne None si aucune clé trouvée.
    """
    env_var = ENV_MAP.get(provider)
    if not env_var:
        return None

    # 1. Chercher clé user en DB
    if user_id and PROJECTS_DB_PATH.exists():
        try:
            conn = sqlite3.connect(str(PROJECTS_DB_PATH))
            row = conn.execute(
                "SELECT api_key FROM user_keys WHERE user_id = ? AND provider = ?",
                (user_id, provider)
            ).fetchone()
            conn.close()
            if row and row[0]:
                return row[0]
        except Exception:
            pass

    # 2. Fallback .env
    return os.getenv(env_var)


def require_key(provider: str, user_id: Optional[str] = None) -> str:
    """Comme resolve_key mais raise HTTPException 402 si aucune clé."""
    from fastapi import HTTPException
    key = resolve_key(provider, user_id)
    if not key:
        raise HTTPException(
            status_code=402,
            detail={
                "error": "no_key",
                "provider": provider,
                "message": f"Aucune clé {provider} configurée. Ajoutez-la via ⚙ Settings ou GOOGLE_API_KEY dans .env"
            }
        )
    return key
