#!/usr/bin/env python3
"""
Run N× workflow via API (mode serveur).

Le modèle reste chargé en mémoire entre les runs. Démarrer l'API une fois, puis :

  python scripts/run_via_api.py 11 -q
  python scripts/run_via_api.py 5 -f --plan Backend/Notebooks/benchmark_tasks/test_workflow_prod.json

Usage:
  run_via_api.py [N] -q [--plan PATH] [--base-url URL]   PROTO (quick)
  run_via_api.py [N] -f [--plan PATH] [--base-url URL]   PROD (full)
"""
from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path

project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))

try:
    import httpx
except ImportError:
    print("httpx required: pip install httpx", file=sys.stderr)
    sys.exit(1)


DEFAULT_PLAN = "Backend/Notebooks/benchmark_tasks/test_workflow_prod.json"
DEFAULT_BASE_URL = "http://127.0.0.1:8000"


def main() -> int:
    ap = argparse.ArgumentParser(
        description="Run N× AETHERFLOW workflow via API (mode serveur, modèle gardé en mémoire)."
    )
    ap.add_argument("runs", type=int, nargs="?", default=1, help="Number of runs (default: 1)")
    ap.add_argument("-q", action="store_true", help="PROTO workflow (quick)")
    ap.add_argument("-f", "--full", action="store_true", dest="full", help="PROD workflow (full)")
    ap.add_argument("--plan", type=str, default=DEFAULT_PLAN, help=f"Plan path (default: {DEFAULT_PLAN})")
    ap.add_argument("--base-url", type=str, default=DEFAULT_BASE_URL, help=f"API base URL (default: {DEFAULT_BASE_URL})")
    args = ap.parse_args()

    if not args.q and not args.full:
        ap.error("Specify -q (PROTO) or -f (PROD)")

    workflow = "PROD" if args.full else "PROTO"
    base = args.base_url.rstrip("/")
    plan_path = args.plan
    n = max(1, args.runs)

    plan_abs = (project_root / plan_path).resolve()
    if not plan_abs.exists():
        print(f"Plan not found: {plan_abs}", file=sys.stderr)
        return 1

    try:
        plan_for_api = str(plan_abs.relative_to(project_root))
    except ValueError:
        plan_for_api = str(plan_abs)

    url = f"{base}/execute"
    payload = {"plan_path": plan_for_api, "workflow": workflow}

    print(f"Mode serveur: {n}× {workflow} via {url}")
    print(f"Plan: {plan_for_api}")
    print()

    success = 0
    total_time = 0.0
    total_cost = 0.0

    timeout = httpx.Timeout(600.0, connect=10.0)
    with httpx.Client(timeout=timeout) as client:
        for i in range(1, n + 1):
            t0 = time.perf_counter()
            try:
                r = client.post(url, json=payload)
                r.raise_for_status()
                data = r.json()
                elapsed = time.perf_counter() - t0
                total_time += elapsed
                m = data.get("metrics") or {}
                c = float(m.get("total_cost", 0) or 0)
                total_cost += c
                ok = data.get("success", True)
                if ok:
                    success += 1
                status = "✓" if ok else "✗"
                print(f"  Run {i}/{n}: {elapsed:.2f}s  ${c:.4f}  {status}")
            except (httpx.ConnectError, httpx.ConnectTimeout) as e:
                print(f"  Run {i}/{n}: API non joignable. Démarrez l'API : ./start_api.sh ou python -m Backend.Prod.api", file=sys.stderr)
                print(f"  {e}", file=sys.stderr)
                break
            except httpx.HTTPStatusError as e:
                print(f"  Run {i}/{n}: HTTP {e.response.status_code} {e.response.text[:200]}", file=sys.stderr)
            except Exception as e:
                print(f"  Run {i}/{n}: {e}", file=sys.stderr)

    print()
    print(f"Total: {success}/{n} success, {total_time:.1f}s, ${total_cost:.4f}")
    return 0 if success == n else 1


if __name__ == "__main__":
    sys.exit(main())
