"""Sullivan Activity Monitor - Logging centralisé.

Ce module fournit des fonctions pour logger les activités de KIMI, SULLIVAN,
et autres agents dans un fichier centralisé avec timestamps.

Usage:
    from Backend.Prod.sullivan.agent.monitor import (
        log_activity, 
        log_file_change, 
        log_mission_start, 
        log_mission_end
    )
    
    # Au début d'une mission
    log_mission_start("CLEANUP")
    
    # Quand tu modifies un fichier
    log_file_change("Backend/Prod/api.py")
    
    # À la fin
    log_mission_end("CLEANUP", success=True)
"""

import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional

# Déterminer le chemin du fichier log
# Remonter depuis Backend/Prod/sullivan/agent/ jusqu'à la racine du projet
PROJECT_ROOT = Path(__file__).parent.parent.parent.parent.parent
LOG_FILE = PROJECT_ROOT / "logs" / "sullivan_activity.log"

# S'assurer que le dossier logs existe
LOG_FILE.parent.mkdir(parents=True, exist_ok=True)


def log_activity(source: str, action_type: str, message: str):
    """Log une activité Sullivan/KIMI.

    Args:
        source: KIMI, SULLIVAN, CLAUDE, USER, SYSTEM
        action_type: ACTION, FILE, SUCCESS, ERROR, INFO, WARNING
        message: Description de l'action
    """
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_line = f"[{timestamp}] [{source}] [{action_type}] {message}\n"

    try:
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(log_line)
    except Exception as e:
        # Fallback sur stderr si le fichier n'est pas accessible
        print(f"[MONITOR ERROR] Impossible d'écrire dans {LOG_FILE}: {e}", file=sys.stderr)

    # Aussi afficher dans le terminal pour visibilité immédiate
    print(f"[MONITOR] [{source}] {message}")


def log_file_change(filepath: str, action: str = "MODIFIED"):
    """Log un changement de fichier.
    
    Args:
        filepath: Chemin du fichier modifié
        action: Type d'action (MODIFIED, CREATED, DELETED, BACKUP)
    """
    log_activity("KIMI", "FILE", f"{action}: {filepath}")


def log_mission_start(mission_name: str, description: Optional[str] = None):
    """Log le début d'une mission.
    
    Args:
        mission_name: Nom de la mission (ex: "CLEANUP", "DESIGN", "MISSION_0")
        description: Description optionnelle de la mission
    """
    msg = f"▶ Mission démarrée: {mission_name}"
    if description:
        msg += f" - {description}"
    log_activity("KIMI", "ACTION", msg)


def log_mission_end(mission_name: str, success: bool = True, details: Optional[str] = None):
    """Log la fin d'une mission.
    
    Args:
        mission_name: Nom de la mission
        success: True si succès, False si échec
        details: Détails optionnels sur le résultat
    """
    status = "SUCCESS" if success else "ERROR"
    emoji = "✓" if success else "✗"
    msg = f"{emoji} Mission terminée: {mission_name}"
    if details:
        msg += f" - {details}"
    log_activity("KIMI", status, msg)


def log_step(step_name: str, status: str = "IN_PROGRESS"):
    """Log une étape intermédiaire d'une mission.
    
    Args:
        step_name: Nom de l'étape
        status: Statut de l'étape (IN_PROGRESS, DONE, SKIPPED, FAILED)
    """
    emoji = {
        "IN_PROGRESS": "⏳",
        "DONE": "✓",
        "SKIPPED": "⊘",
        "FAILED": "✗"
    }.get(status, "•")
    
    log_activity("KIMI", "INFO", f"{emoji} Étape: {step_name} [{status}]")


def log_error(error_message: str, context: Optional[str] = None):
    """Log une erreur.
    
    Args:
        error_message: Description de l'erreur
        context: Contexte optionnel (fichier, ligne, etc.)
    """
    msg = error_message
    if context:
        msg = f"[{context}] {msg}"
    log_activity("KIMI", "ERROR", msg)


def log_user_action(action: str, details: Optional[str] = None):
    """Log une action utilisateur.
    
    Args:
        action: Type d'action (ex: "GO_RECEIVED", "MODIFICATION_REQUESTED")
        details: Détails optionnels
    """
    msg = action
    if details:
        msg += f": {details}"
    log_activity("USER", "ACTION", msg)


# Fonction de test
if __name__ == "__main__":
    print(f"Testing monitor module...")
    print(f"Log file: {LOG_FILE}")
    
    log_activity("TEST", "INFO", "Test du système de monitoring")
    log_mission_start("TEST_MONITOR", "Test des fonctions de log")
    log_step("Étape 1: Création fichier", "DONE")
    log_step("Étape 2: Écriture log", "DONE")
    log_file_change("test_file.py", "CREATED")
    log_mission_end("TEST_MONITOR", success=True, details="Tous les tests OK")
    
    print(f"✓ Test terminé. Vérifiez le fichier: {LOG_FILE}")
