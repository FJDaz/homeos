#!/bin/bash
# Vider les caches et outputs AETHERFLOW pour repartir d'une situation vierge.
# Usage: ./scripts/clear_aetherflow_cache.sh

set -e
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

rm -rf output cache rag_index logs docs/logs 2>/dev/null || true
mkdir -p output output/studio output/fast output/validation
echo "Cache and output cleared. Recreated output/ tree."
