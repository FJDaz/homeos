#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Parse Components - Extrait les composants du fichier Collection de composants.txt

Ce script parse le fichier de collection et génère une library JSON structurée.
"""

import re
import json
from pathlib import Path
from typing import List, Dict, Any
from dataclasses import dataclass, asdict


@dataclass
class Component:
    """Représente un composant extrait."""
    id: str
    category: str  # atoms, molecules, organisms, templates, pages
    name: str
    html: str
    css: str
    description: str = ""
    tags: List[str] = None
    params: List[str] = None
    
    def __post_init__(self):
        if self.tags is None:
            self.tags = []
        if self.params is None:
            self.params = []


def parse_collection_file(filepath: Path) -> List[Component]:
    """
    Parse le fichier Collection de composants.txt
    
    Args:
        filepath: Chemin vers le fichier de collection
        
    Returns:
        Liste des composants extraits
    """
    content = filepath.read_text(encoding="utf-8")
    components = []
    
    # Pattern pour trouver les blocs de composants
    # Chaque composant commence par "### **N. Name" et contient un bloc ```html
    component_pattern = r'### \*\*\d+\.\s*([^*]+)\*\*.*?```html\n(.*?)```'
    
    # Pattern pour extraire le commentaire de catégorie <!-- category/name.html -->
    category_pattern = r'<!--\s*(\w+)/(\w+)\.html\s*-->'
    
    matches = re.findall(component_pattern, content, re.DOTALL)
    
    for i, (name, html_block) in enumerate(matches, 1):
        name = name.strip()
        
        # Chercher le commentaire de catégorie dans le bloc HTML
        cat_match = re.search(category_pattern, html_block)
        if cat_match:
            category = cat_match.group(1).lower()
            component_name = cat_match.group(2).lower()
        else:
            # Déduire la catégorie du contenu
            category = _detect_category(html_block)
            component_name = _sanitize_name(name)
        
        # Séparer HTML et CSS
        html, css = _split_html_css(html_block)
        
        # Extraire les tags automatiquement
        tags = _extract_tags(html_block, name)
        
        # Extraire les paramètres (variables CSS et data-attributes)
        params = _extract_params(html_block)
        
        component = Component(
            id=f"{category}_{component_name}",
            category=category,
            name=component_name,
            html=html,
            css=css,
            description=name,
            tags=tags,
            params=params,
        )
        components.append(component)
    
    return components


def _detect_category(html: str) -> str:
    """Détecte la catégorie d'un composant selon son contenu."""
    html_lower = html.lower()
    
    # Patterns pour détecter la complexité
    has_complex_structure = any(tag in html_lower for tag in ['<section', '<article', '<header', '<footer', '<nav'])
    has_multiple_components = html_lower.count('<button') + html_lower.count('<input') + html_lower.count('<div') > 3
    has_layout = any(tag in html_lower for tag in ['<main', '<layout', 'grid', 'flex'])
    
    if has_layout or '<!doctype' in html_lower or '<html' in html_lower:
        return 'pages'
    elif has_complex_structure or has_multiple_components:
        return 'organisms'
    elif html_lower.count('<div') > 0 or html_lower.count('<form') > 0 or has_multiple_components:
        return 'molecules'
    else:
        return 'atoms'


def _sanitize_name(name: str) -> str:
    """Convertit un nom en identifiant valide."""
    # Enlever les caractères spéciaux
    name = re.sub(r'[^\w\s-]', '', name)
    # Convertir en snake_case
    name = name.strip().lower().replace(' ', '_').replace('-', '_')
    return name


def _split_html_css(block: str) -> tuple:
    """Sépare le HTML du CSS dans un bloc."""
    # Chercher le style tag
    style_match = re.search(r'<style>(.*?)</style>', block, re.DOTALL)
    if style_match:
        css = style_match.group(1).strip()
        # HTML est tout sauf le style
        html = re.sub(r'<style>.*?</style>', '', block, flags=re.DOTALL).strip()
    else:
        css = ""
        html = block.strip()
    
    return html, css


def _extract_tags(html: str, name: str) -> List[str]:
    """Extrait les tags sémantiques d'un composant."""
    tags = []
    html_lower = html.lower()
    
    # Tags basés sur le nom
    name_lower = name.lower()
    if 'button' in name_lower or '<button' in html_lower:
        tags.append('button')
    if 'input' in name_lower or '<input' in html_lower:
        tags.append('input')
    if 'form' in name_lower or '<form' in html_lower:
        tags.append('form')
    if 'card' in name_lower:
        tags.append('card')
    if 'modal' in name_lower or 'dialog' in name_lower:
        tags.append('modal')
    if 'nav' in name_lower or '<nav' in html_lower:
        tags.append('navigation')
    if 'table' in name_lower or '<table' in html_lower:
        tags.append('table')
    if 'search' in name_lower:
        tags.append('search')
    if 'login' in name_lower or 'auth' in name_lower:
        tags.append('login')
    if 'list' in name_lower or '<ul' in html_lower or '<ol' in html_lower:
        tags.append('list')
    
    # Tags basés sur le contenu HTML
    tag_patterns = {
        'form': ['<form', '<input', '<select', '<textarea'],
        'navigation': ['<nav', 'role="navigation"', 'menu'],
        'data': ['<table', '<thead', '<tbody'],
        'card': ['card', 'shadow', 'rounded'],
        'modal': ['modal', 'dialog', 'overlay'],
        'button': ['<button', 'btn', 'click'],
        'image': ['<img', '<svg', '<picture'],
        'text': ['<p>', '<span', '<h1', '<h2', '<h3'],
        'layout': ['grid', 'flex', 'container'],
        'feedback': ['alert', 'toast', 'notification', 'message'],
        'media': ['video', 'audio', 'iframe'],
    }
    
    for tag, patterns in tag_patterns.items():
        if tag not in tags:  # Éviter les doublons
            if any(p in html_lower for p in patterns):
                tags.append(tag)
    
    return tags


def _extract_params(html: str) -> List[str]:
    """Extrait les paramètres adaptables d'un composant."""
    params = []
    
    # Variables CSS (--xxx)
    css_vars = re.findall(r'var\(--([\w-]+)\)', html)
    for var in set(css_vars):
        params.append(f"css:{var}")
    
    # Data attributes (data-xxx)
    data_attrs = re.findall(r'data-([\w-]+)=', html)
    for attr in set(data_attrs):
        params.append(f"data:{attr}")
    
    # Classes avec placeholder potentiel
    class_patterns = re.findall(r'class="([^"]*\{[^}]*\}[^"]*)"', html)
    for pattern in class_patterns:
        placeholders = re.findall(r'\{(\w+)\}', pattern)
        for ph in placeholders:
            if f"class:{ph}" not in params:
                params.append(f"class:{ph}")
    
    return params


def save_raw_library(components: List[Component], output_path: Path):
    """Sauvegarde la library brute en JSON."""
    library = {
        "version": "1.0",
        "source": "Collection de composants",
        "generated_at": Path(__file__).stat().st_mtime,
        "components": [asdict(c) for c in components]
    }
    
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(library, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"✓ Raw library sauvegardée: {output_path}")
    print(f"  {len(components)} composants extraits")


def enrich_library(raw_library_path: Path, output_path: Path):
    """
    Enrichit la library brute avec des métadonnées supplémentaires.
    
    Ajoute:
    - Defaults pour chaque paramètre
    - Score de popularité estimé
    - Documentation d'utilisation
    """
    data = json.loads(raw_library_path.read_text(encoding="utf-8"))
    components = data.get("components", [])
    
    enriched = {
        "version": "1.1-enriched",
        "source": "Collection de composants + enrichissement auto",
        "generated_at": Path(__file__).stat().st_mtime,
        "categories": {},
        "stats": {},
    }
    
    # Organiser par catégorie
    by_category = {}
    for comp in components:
        cat = comp["category"]
        if cat not in by_category:
            by_category[cat] = {}
        
        # Ajouter des defaults pour chaque paramètre
        defaults = {}
        for param in comp.get("params", []):
            if param.startswith("css:"):
                var_name = param[4:]
                defaults[param] = _get_css_default(var_name)
            elif param.startswith("data:"):
                defaults[param] = "medium"  # Valeur par défaut
            elif param.startswith("class:"):
                defaults[param] = "default"
        
        # Ajouter des exemples d'utilisation
        examples = _generate_examples(comp)
        
        by_category[cat][comp["name"]] = {
            **comp,
            "defaults": defaults,
            "examples": examples,
            "complexity": _calculate_complexity(comp),
        }
    
    enriched["categories"] = by_category
    
    # Stats globales
    enriched["stats"] = {
        "total": len(components),
        "by_category": {cat: len(comps) for cat, comps in by_category.items()},
        "total_params": sum(len(c.get("params", [])) for c in components),
    }
    
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(enriched, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"✓ Library enrichie sauvegardée: {output_path}")
    print(f"  Catégories: {dict(enriched['stats']['by_category'])}")


def _get_css_default(var_name: str) -> str:
    """Retourne une valeur par défaut pour une variable CSS."""
    defaults = {
        "btn-bg": "#007bff",
        "btn-color": "white",
        "btn-padding-x": "1rem",
        "btn-padding-y": "0.5rem",
        "btn-radius": "0.25rem",
        "input-border": "#ccc",
        "input-focus": "#007bff",
        "icon-size": "1em",
        "icon-color": "currentColor",
        "color-value": "#007bff",
    }
    return defaults.get(var_name, "inherit")


def _generate_examples(comp: Dict) -> List[Dict]:
    """Génère des exemples d'utilisation pour un composant."""
    examples = []
    
    # Exemple basique
    examples.append({
        "name": "basic",
        "description": f"Utilisation basique de {comp['name']}",
        "params": {},
    })
    
    # Exemples selon le type
    if "button" in comp.get("tags", []):
        examples.append({
            "name": "primary",
            "description": "Bouton primaire",
            "params": {"data:variant": "primary", "css:btn-bg": "#007bff"},
        })
        examples.append({
            "name": "danger",
            "description": "Bouton de danger",
            "params": {"data:variant": "danger", "css:btn-bg": "#dc3545"},
        })
    
    if "input" in comp.get("tags", []):
        examples.append({
            "name": "error",
            "description": "Input en erreur",
            "params": {"data:state": "error"},
        })
    
    return examples


def _calculate_complexity(comp: Dict) -> str:
    """Calcule la complexité d'un composant."""
    html_len = len(comp.get("html", ""))
    css_len = len(comp.get("css", ""))
    param_count = len(comp.get("params", []))
    
    if html_len > 1000 or css_len > 800 or param_count > 10:
        return "high"
    elif html_len > 500 or css_len > 400 or param_count > 5:
        return "medium"
    else:
        return "low"


def main():
    """Point d'entrée principal."""
    # Chemins
    root = Path("/Users/francois-jeandazin/AETHERFLOW")
    collection_file = root / "docs/02-sullivan/Composants/Collection de composants .txt"
    raw_output = root / "output/components/raw_library.json"
    enriched_output = root / "output/components/library.json"
    
    print("=" * 60)
    print("SULLIVAN COMPONENT PARSER")
    print("=" * 60)
    
    # Vérifier que le fichier source existe
    if not collection_file.exists():
        print(f"✗ Fichier source non trouvé: {collection_file}")
        return 1
    
    print(f"Source: {collection_file}")
    print(f"Taille: {collection_file.stat().st_size / 1024:.1f} KB")
    print()
    
    # Phase 1: Parsing
    print("Phase 1: Parsing des composants...")
    components = parse_collection_file(collection_file)
    save_raw_library(components, raw_output)
    print()
    
    # Phase 2: Enrichissement
    print("Phase 2: Enrichissement de la library...")
    enrich_library(raw_output, enriched_output)
    print()
    
    # Résumé
    print("=" * 60)
    print("RÉSUMÉ")
    print("=" * 60)
    print(f"✓ Parsing terminé avec succès")
    print(f"✓ {len(components)} composants extraits")
    print(f"✓ Library sauvegardée dans: {enriched_output}")
    print()
    print("Prochaine étape: Implémenter l'outil @select_component")
    
    return 0


if __name__ == "__main__":
    exit(main())
