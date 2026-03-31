#!/usr/bin/env python3
"""
MiMo Monitor — AetherFlow utility.
Tracks Xiaomi MiMo token usage from the local cost logs.
"""
import sys
import os
from pathlib import Path

# Fix path to allow importing Backend
project_root = Path(__file__).resolve().parents[3]
sys.path.append(str(project_root))

from Backend.Prod.core.cost_tracker import get_cost_tracker
from Backend.Prod.config.settings import settings

def show_mimo_status():
    tracker = get_cost_tracker()
    usage = tracker.get_usage_stats()
    
    mimo_stats = usage["by_provider"].get("mimo", {"calls": 0, "tokens": 0, "cost": 0.0})
    
    total_tokens = mimo_stats["tokens"]
    free_quota = settings.mimo_free_quota_tokens
    remaining = max(0, free_quota - total_tokens)
    percent_used = (total_tokens / free_quota * 100) if free_quota > 0 else 0
    
    print("=" * 60)
    print("           XIAOMI MIMO - MONITORING LOCAL (AetherFlow)")
    print("=" * 60)
    print(f"📊 Nombre d'appels   : {mimo_stats['calls']}")
    print(f"📈 Tokens consommés  : {total_tokens:,}")
    print(f"💰 Coût estimé       : ${mimo_stats['cost']:.6f}")
    print("-" * 60)
    print(f"🎁 Offre gratuite    : {free_quota:,} tokens (est.)")
    print(f"⏳ Quota restant     : {remaining:,} tokens")
    
    # Progress bar
    bar_width = 40
    filled = int(bar_width * percent_used / 100)
    bar = "█" * filled + "░" * (bar_width - filled)
    print(f"📈 Progression       : [{bar}] {percent_used:.2f}%")
    
    if percent_used > 90:
        print("\n⚠️  ATTENTION : Ton tiers gratuit est presque épuisé !")
    elif total_tokens == 0:
        print("\n💡 Aucun usage MiMo détecté pour l'instant.")
    else:
        print("\n✅ Ton tiers gratuit est encore largement disponible.")
        
    print("=" * 60)
    print(f"Note : Ces chiffres sont basés sur tes fichiers de log locaux.")
    print(f"Lieu du log : {tracker.storage_path}")
    print("=" * 60)

if __name__ == "__main__":
    show_mimo_status()
