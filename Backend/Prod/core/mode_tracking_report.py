# -*- coding: utf-8 -*-
"""
Mode Tracking Report - Génération de rapports d'utilisation des modes AetherFlow

Ce module génère des rapports sur l'utilisation des modes:
- PROTO: Mode rapide/POC (Groq)
- PROD: Mode production/AgentRouter
- FRONTEND: Mode frontend (-frd)
- DESIGNER: Mode analyse design
- SURGICAL: Mode édition chirurgicale
"""

from typing import Optional
from datetime import datetime, timedelta
from pathlib import Path
import json

from .mode_monitor import ModeMonitor


def generate_report(format: str = "text", period: str = "all") -> str:
    """
    Génère un rapport d'utilisation des modes.
    
    Args:
        format: Format de sortie ("text" ou "json")
        period: Période du rapport ("day", "week", "month", "all")
    
    Returns:
        Rapport formaté en string
    """
    monitor = ModeMonitor()
    
    # Filtrer par période si nécessaire
    executions = monitor.executions
    if period != "all":
        executions = _filter_by_period(executions, period)
    
    # Calculer les stats avec les exécutions (filtrées ou non)
    stats = _calculate_stats(executions)
    
    if format == "json":
        return _generate_json_report(stats, executions, period)
    else:
        return _generate_text_report(stats, executions, period)


def _filter_by_period(executions, period: str):
    """Filtre les exécutions par période."""
    now = datetime.now()
    
    if period == "day":
        cutoff = now - timedelta(days=1)
    elif period == "week":
        cutoff = now - timedelta(weeks=1)
    elif period == "month":
        cutoff = now - timedelta(days=30)
    else:
        return executions
    
    filtered = []
    for exec in executions:
        try:
            exec_time = datetime.fromisoformat(exec.timestamp)
            if exec_time >= cutoff:
                filtered.append(exec)
        except (ValueError, TypeError):
            continue
    
    return filtered


def _calculate_stats(executions):
    """Recalcule les stats à partir d'une liste d'exécutions."""
    from collections import defaultdict
    
    stats = defaultdict(lambda: {
        "total_executions": 0,
        "successful": 0,
        "failed": 0,
        "success_rate": 0.0,
        "total_time_ms": 0.0,
        "total_cost_usd": 0.0,
        "total_tokens": 0
    })
    
    for exec in executions:
        mode = exec.mode
        stats[mode]["total_executions"] += 1
        if exec.success:
            stats[mode]["successful"] += 1
        else:
            stats[mode]["failed"] += 1
        stats[mode]["total_time_ms"] += exec.execution_time_ms
        stats[mode]["total_cost_usd"] += exec.cost_usd
        stats[mode]["total_tokens"] += exec.tokens_used
    
    # Calculer les taux de succès
    for mode in stats:
        count = stats[mode]["total_executions"]
        if count > 0:
            stats[mode]["success_rate"] = stats[mode]["successful"] / count
    
    return dict(stats)


def _generate_text_report(stats, executions, period: str) -> str:
    """Génère un rapport formaté en texte avec Rich styling."""
    lines = []
    
    # Header
    period_label = {
        "day": "dernières 24h",
        "week": "7 derniers jours",
        "month": "30 derniers jours",
        "all": "tout l'historique"
    }.get(period, period)
    
    lines.append("")
    lines.append("╔══════════════════════════════════════════════════════════════╗")
    lines.append("║           📊 RAPPORT D'UTILISATION DES MODES                 ║")
    lines.append(f"║                   ({period_label:^30})                 ║")
    lines.append("╚══════════════════════════════════════════════════════════════╝")
    lines.append("")
    
    # Statistiques par mode
    lines.append("┌──────────────────────────────────────────────────────────────┐")
    lines.append("│  STATISTIQUES PAR MODE                                       │")
    lines.append("├──────────┬─────────┬──────────┬────────────┬─────────────────┤")
    lines.append("│ Mode     │ Exécs   │ Succès   │ Coût ($)   │ Temps (ms)      │")
    lines.append("├──────────┼─────────┼──────────┼────────────┼─────────────────┤")
    
    modes = ["PROTO", "PROD", "FRONTEND", "DESIGNER", "SURGICAL"]
    total_cost = 0.0
    total_execs = 0
    total_time = 0.0
    
    for mode in modes:
        mode_stats = stats.get(mode, {})
        count = mode_stats.get("total_executions", 0)
        success = mode_stats.get("successful", 0)
        cost = mode_stats.get("total_cost_usd", 0.0)
        time_ms = mode_stats.get("total_time_ms", 0.0)
        
        total_cost += cost
        total_execs += count
        total_time += time_ms
        
        lines.append(f"│ {mode:<8} │ {count:>7} │ {success:>7}/{count:<3} │ ${cost:>8.4f} │ {time_ms:>13.0f} │")
    
    lines.append("├──────────┼─────────┼──────────┼────────────┼─────────────────┤")
    lines.append(f"│ TOTAL    │ {total_execs:>7} │          │ ${total_cost:>8.4f} │ {total_time:>13.0f} │")
    lines.append("└──────────┴─────────┴──────────┴────────────┴─────────────────┘")
    lines.append("")
    
    # Taux de succès
    lines.append("┌──────────────────────────────────────────────────────────────┐")
    lines.append("│  TAUX DE SUCCÈS                                              │")
    lines.append("├──────────┬────────────────┬──────────────────────────────────┤")
    lines.append("│ Mode     │ Taux           │ Barre                            │")
    lines.append("├──────────┼────────────────┼──────────────────────────────────┤")
    
    for mode in modes:
        mode_stats = stats.get(mode, {})
        count = mode_stats.get("total_executions", 0)
        success = mode_stats.get("successful", 0)
        
        if count > 0:
            rate = success / count
            percentage = f"{rate*100:.1f}%"
            bar_length = int(rate * 30)
            bar = "█" * bar_length + "░" * (30 - bar_length)
        else:
            percentage = "N/A"
            bar = "░" * 30
        
        lines.append(f"│ {mode:<8} │ {percentage:>14} │ {bar} │")
    
    lines.append("└──────────┴────────────────┴──────────────────────────────────┘")
    lines.append("")
    
    # Récentes exécutions (5 dernières)
    if executions:
        lines.append("┌──────────────────────────────────────────────────────────────┐")
        lines.append("│  5 DERNIÈRES EXÉCUTIONS                                      │")
        lines.append("├──────────────┬──────────┬──────────────────┬────────┬────────┤")
        lines.append("│ Horodatage   │ Mode     │ Action           │ Statut │ Coût   │")
        lines.append("├──────────────┼──────────┼──────────────────┼────────┼────────┤")
        
        recent = sorted(executions, key=lambda x: x.timestamp, reverse=True)[:5]
        for exec in recent:
            ts = exec.timestamp[:16] if len(exec.timestamp) >= 16 else exec.timestamp[:10]
            mode = exec.mode[:8]
            action = exec.action_type[:16] if len(exec.action_type) > 16 else exec.action_type
            status = "✓ OK" if exec.success else "✗ KO"
            cost = f"${exec.cost_usd:.3f}"
            
            lines.append(f"│ {ts:<12} │ {mode:<8} │ {action:<16} │ {status:<6} │ {cost:<6} │")
        
        lines.append("└──────────────┴──────────┴──────────────────┴────────┴────────┘")
        lines.append("")
    
    # Résumé
    lines.append("┌──────────────────────────────────────────────────────────────┐")
    lines.append("│  RÉSUMÉ                                                      │")
    lines.append(f"│  • Total exécutions: {total_execs:>5}                                   │")
    lines.append(f"│  • Coût total: ${total_cost:>8.4f}                                    │")
    lines.append(f"│  • Temps total: {total_time/1000:.1f}s                                           │")
    lines.append("│                                                              │")
    lines.append("│  💡 Pour plus de détails: sullivan monitor --format json     │")
    lines.append("└──────────────────────────────────────────────────────────────┘")
    lines.append("")
    
    return "\n".join(lines)


def _generate_json_report(stats, executions, period: str) -> str:
    """Génère un rapport au format JSON."""
    report_data = {
        "generated_at": datetime.now().isoformat(),
        "period": period,
        "statistics_by_mode": {},
        "executions": []
    }
    
    # Statistiques par mode
    modes = ["PROTO", "PROD", "FRONTEND", "DESIGNER", "SURGICAL"]
    for mode in modes:
        mode_stats = stats.get(mode, {})
        count = mode_stats.get("total_executions", 0)
        success = mode_stats.get("successful", 0)
        failed = mode_stats.get("failed", 0)
        
        report_data["statistics_by_mode"][mode] = {
            "total_executions": count,
            "successful": success,
            "failed": failed,
            "success_rate": (success / count * 100) if count > 0 else 0,
            "total_cost_usd": round(mode_stats.get("total_cost_usd", 0.0), 4),
            "total_time_ms": round(mode_stats.get("total_time_ms", 0.0), 2),
            "total_tokens": mode_stats.get("total_tokens", 0)
        }
    
    # Exécutions détaillées
    for exec in executions:
        report_data["executions"].append({
            "timestamp": exec.timestamp,
            "mode": exec.mode,
            "action_type": exec.action_type,
            "success": exec.success,
            "execution_time_ms": exec.execution_time_ms,
            "cost_usd": exec.cost_usd,
            "tokens_used": exec.tokens_used,
            "files_modified": exec.files_modified,
            "files_created": exec.files_created,
            "plan_id": exec.plan_id
        })
    
    return json.dumps(report_data, indent=2, ensure_ascii=False)
