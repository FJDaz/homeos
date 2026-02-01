#!/usr/bin/env python3
"""Debug: ce qui est chargé pour MISTRAL_API_KEY."""
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

# Où cherche-t-on .env ?
cwd = Path.cwd()
env_path = (cwd / ".env").resolve()
env_in_backend = (cwd / "Backend" / ".env").resolve()

print("Debug MISTRAL_API_KEY")
print("=" * 50)
print(f"CWD: {cwd}")
print(f".env (racine): {env_path} — exists={env_path.exists()}")
print(f"Backend/.env:  {env_in_backend} — exists={env_in_backend.exists()}")

env_val = os.environ.get("MISTRAL_API_KEY")
print(f"MISTRAL_API_KEY in os.environ: {'SET' if env_val else 'NOT SET'}")
if env_val:
    k = env_val
    print(f"  (env) len={len(k)} first4={k[:4]!r} last2={k[-2:]!r} ascii={k.isascii()} votre={k.startswith('votre_')} your={k.startswith('your_')}")

from Backend.Prod.config.settings import settings

k = (settings.mistral_api_key or "").strip()
print(f"settings.mistral_api_key: len={len(k)} first4={k[:4]!r} last2={k[-2:]!r} ascii={k.isascii()} votre={k.startswith('votre_')} your={k.startswith('your_')}")
if k:
    for i, c in enumerate(k[:6]):
        print(f"  char[{i}] {c!r} ord={ord(c)}")
