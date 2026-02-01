#!/usr/bin/env python3
"""Test direct du provider Codestral (Mistral)."""
import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from Backend.Prod.config.settings import settings
from Backend.Prod.models.codestral_client import CodestralClient


async def main() -> int:
    print("Codestral (Mistral) — test direct")
    print("=" * 50)

    key = (settings.mistral_api_key or "").strip()
    if not key:
        print("MISTRAL_API_KEY non définie dans .env")
        return 1
    if not key.isascii():
        print("MISTRAL_API_KEY contient des caractères non-ASCII (ex. é). Utilisez une clé ASCII.")
        return 1
    if key.lower().startswith("votre_") or key.lower().startswith("your_"):
        print("MISTRAL_API_KEY ressemble à un placeholder (votre_/your_). Utilisez une vraie clé.")
        return 1

    print(f"Clé: {key[:6]}…{key[-2:]}")
    print("Init client…")

    try:
        client = CodestralClient()
    except Exception as e:
        print(f"Init échec: {e}")
        return 1

    print("Generate (prompt minimal)…")
    try:
        res = await client.generate(
            prompt="Reply with exactly: 42",
            context="Python",
            max_tokens=50,
        )
        await client.close()
    except Exception as e:
        print(f"Generate échec: {e}")
        return 1

    if res.success:
        print(f"OK — {res.tokens_used} tok, ${res.cost_usd:.4f}")
        print(f"Réponse: {(res.code or '')[:200]}")
        return 0
    print(f"Échec: {res.error}")
    return 1


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
