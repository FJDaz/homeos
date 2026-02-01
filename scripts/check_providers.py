#!/usr/bin/env python3
"""Vérifier que Groq, DeepSeek, Codestral et Gemini sont opérationnels."""
import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from Backend.Prod.config.settings import settings
from Backend.Prod.models.execution_router import ExecutionRouter
from Backend.Prod.models.agent_router import AgentRouter
from Backend.Prod.models.plan_reader import Step


def _mask(s: str) -> str:
    if not s or len(s) < 8:
        return "***"
    return s[:4] + "…" + s[-2:]


async def main() -> int:
    router = ExecutionRouter()
    avail = router.available_providers

    print("=" * 60)
    print("  AETHERFLOW — État des providers (employés)")
    print("=" * 60)

    # 1. Config (clé présente et valide)
    key_map = {
        "deepseek": getattr(settings, "deepseek_api_key", None) or "",
        "groq": getattr(settings, "groq_api_key", None) or "",
        "gemini": getattr(settings, "google_api_key", None) or "",
        "codestral": getattr(settings, "mistral_api_key", None) or "",
    }
    print("\n1. Config (clé présente, ascii, pas placeholder)")
    for name in ["deepseek", "groq", "gemini", "codestral"]:
        key = key_map[name]
        ok = avail.get(name, False)
        mask = _mask(key) if key else "—"
        status = "ok" if ok else "absent / invalide"
        print(f"   {name:12} {status:20} {mask}")

    # 2. Init (clients créés)
    print("\n2. Init (clients initialisés)")
    try:
        ar = AgentRouter(execution_mode="FAST")
        inits = list(ar._clients.keys())
        for name in ["deepseek", "groq", "gemini", "codestral"]:
            ok = name in inits
            status = "ok" if ok else "—"
            print(f"   {name:12} {status}")
        print(f"   → {len(inits)} client(s) au total")
    except Exception as e:
        print(f"   Erreur init AgentRouter: {e}")
        return 1

    # 3. Ping (generate minimal)
    print("\n3. Ping (generate minimal par provider)")
    step = Step({
        "id": "ping",
        "description": "Return the number 42.",
        "type": "code_generation",
        "complexity": 0.1,
        "estimated_tokens": 50,
        "dependencies": [],
        "validation_criteria": [],
        "context": {"language": "python", "files": []},
    })

    for name in sorted(ar._clients.keys()):
        client = ar._clients[name]
        try:
            res = await client.generate(
                prompt="Reply with exactly: 42",
                context="Python",
                max_tokens=20,
            )
            ok = res.success
            status = "ok" if ok else "fail"
            extra = ""
            if res.success:
                extra = f" ({res.tokens_used} tok, ${res.cost_usd:.4f})"
            print(f"   {name:12} {status}{extra}")
        except Exception as e:
            print(f"   {name:12} fail — {e}")

    await ar.close()

    n_ok = sum(1 for n in ["deepseek", "groq", "gemini", "codestral"] if n in inits)
    print("\n" + "=" * 60)
    if n_ok == 4:
        print("Résumé: 4/4 providers opérationnels.")
    else:
        print(f"Résumé: {n_ok}/4 providers opérationnels.", end="")
        if "codestral" not in inits:
            print(" Codestral: définir MISTRAL_API_KEY (clé ascii, pas 'votre_').", end="")
        print()
    return 0


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
