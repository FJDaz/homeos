#!/usr/bin/env python3
"""
frd_logic.py — Mission 45
Logique pour la gestion des templates via l'éditeur Monaco (FRD).
"""

import os
from pathlib import Path
from typing import Dict, Any, Optional
from loguru import logger

TEMPLATES_DIR = Path(__file__).parent.parent.parent.parent / "Frontend" / "3. STENCILER" / "static" / "templates"

def read_template(file_name: str) -> str:
    """ Lit le contenu d'un template. """
    # Sécurité : empêcher le path traversal
    safe_name = os.path.basename(file_name)
    file_path = TEMPLATES_DIR / safe_name
    
    if not file_path.exists():
        logger.error(f"[FRD] File not found: {file_path}")
        raise FileNotFoundError(f"Template {safe_name} introuvable.")
    
    return file_path.read_text(encoding="utf-8")

def write_template(file_name: str, content: str) -> None:
    """ Sauvegarde le contenu d'un template. """
    safe_name = os.path.basename(file_name)
    file_path = TEMPLATES_DIR / safe_name
    
    # Backup optionnel ? Pour l'instant on écrase proprement
    file_path.write_text(content, encoding="utf-8")
    logger.info(f"[FRD] File saved: {file_path}")
