"""Debug de toutes les clés API (env vs .env, ascii, placeholder)."""
import os
from pathlib import Path

from .config.settings import settings


KEY_CONFIG = [
    ("DEEPSEEK_API_KEY", "deepseek_api_key", "DeepSeek"),
    ("GROQ_API_KEY", "groq_api_key", "Groq"),
    ("GOOGLE_API_KEY", "google_api_key", "Gemini"),
    ("MISTRAL_API_KEY", "mistral_api_key", "Codestral"),
    ("ANTHROPIC_API_KEY", "anthropic_api_key", "Claude"),
]


def _mask(s: str) -> str:
    if not s or len(s) < 6:
        return "***"
    return s[:4] + "…" + s[-2:]


def _check(k: str) -> dict:
    k = (k or "").strip()
    return {
        "len": len(k),
        "mask": _mask(k),
        "ascii": k.isascii(),
        "votre": k.lower().startswith("votre_"),
        "your": k.lower().startswith("your_"),
        "ok": bool(k) and k.isascii() and not k.lower().startswith("votre_") and not k.lower().startswith("your_"),
    }


def run_debug_keys(verbose: bool = True) -> None:
    """Affiche le debug de toutes les clés API (env vs settings)."""
    cwd = Path.cwd()
    env_path = (cwd / ".env").resolve()
    lines = []
    lines.append("Debug API Keys")
    lines.append("=" * 60)
    if verbose:
        lines.append(f"CWD: {cwd}")
        lines.append(f".env: {env_path} — exists={env_path.exists()}")
        lines.append("")
    lines.append(f"{'Key':<22} {'Source':<14} {'Mask':<12} {'Len':<5} {'ASCII':<6} {'OK':<5}")
    lines.append("-" * 65)

    for env_var, attr, label in KEY_CONFIG:
        env_set = env_var in os.environ
        try:
            settings_val = (getattr(settings, attr, None) or "").strip()
        except Exception:
            settings_val = ""
        c = _check(settings_val)
        source = "env" if env_set else ".env"
        if env_set:
            source = "env (override)"
        lines.append(
            f"{label:<22} {source:<14} {c['mask']:<12} {c['len']:<5} {str(c['ascii']):<6} {str(c['ok']):<5}"
        )

    lines.append("")
    lines.append("Si source = env(override), la variable d'environnement écrase le .env.")
    lines.append("Pour utiliser le .env: unset <VAR> puis relancer.")
    print("\n".join(lines))
