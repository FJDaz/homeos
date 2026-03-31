"""Preview generator for Sullivan components - Génération HTML de prévisualisation."""
from typing import List
from pathlib import Path
from loguru import logger

from ..models.component import Component


def generate_preview_html(component: Component, base_url: str) -> str:
    """
    Génère HTML de prévisualisation pour un composant avec iframe sécurisé.
    
    Args:
        component: Composant à prévisualiser
        base_url: URL de base pour les liens
        
    Returns:
        HTML de prévisualisation avec style brutaliste
    """
    # Construire URL de prévisualisation du composant
    component_id = component.name.replace("component_", "")
    preview_url = f"{base_url.rstrip('/')}/sullivan/preview/{component_id}"
    
    html = f'''<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Preview: {component.name}</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
            background: #fff;
            color: #000;
            padding: 20px;
        }}
        .preview-container {{
            max-width: 1200px;
            margin: 0 auto;
        }}
        h1 {{
            font-size: 24px;
            font-weight: bold;
            margin-bottom: 20px;
            border-bottom: 3px solid #000;
            padding-bottom: 10px;
        }}
        .preview-frame {{
            width: 100%;
            height: 600px;
            border: 2px solid #000;
            margin: 20px 0;
        }}
        .component-info {{
            margin: 20px 0;
            padding: 15px;
            border: 1px solid #000;
            background: #f5f5f5;
        }}
        .component-info h2 {{
            font-size: 18px;
            margin-bottom: 10px;
        }}
        .component-info p {{
            margin: 5px 0;
        }}
        .score-badge {{
            display: inline-block;
            padding: 5px 10px;
            margin: 5px;
            background: #000;
            color: #fff;
            font-weight: bold;
        }}
    </style>
</head>
<body>
    <div class="preview-container">
        <h1>Preview: {component.name}</h1>
        
        <div class="component-info">
            <h2>Informations</h2>
            <p><strong>Score Sullivan:</strong> <span class="score-badge">{component.sullivan_score:.1f}</span></p>
            <p><strong>Taille:</strong> {component.size_kb} KB</p>
            <p><strong>Performance:</strong> {component.performance_score}/100</p>
            <p><strong>Accessibilité:</strong> {component.accessibility_score}/100</p>
            <p><strong>Écologie:</strong> {component.ecology_score}/100</p>
        </div>
        
        <h2>Rendu du composant</h2>
        <iframe 
            src="{preview_url}" 
            class="preview-frame"
            title="Component Preview"
            sandbox="allow-scripts allow-same-origin"
        ></iframe>
    </div>
</body>
</html>'''
    
    return html


def generate_preview_page(components: List[Component], base_url: str) -> str:
    """
    Génère page HTML de liste de tous les composants avec liens vers prévisualisations.
    
    Args:
        components: Liste de composants
        base_url: URL de base pour les liens
        
    Returns:
        HTML de page de liste avec style brutaliste
    """
    items_html = ""
    for comp in components:
        component_id = comp.name.replace("component_", "")
        preview_url = f"{base_url.rstrip('/')}/sullivan/preview/{component_id}/render"
        items_html += f'''
        <li style="margin: 10px 0; padding: 15px; border: 1px solid #000;">
            <a href="{preview_url}" style="text-decoration: none; color: #000; font-weight: bold;">
                {comp.name}
            </a>
            <span style="margin-left: 10px; color: #666;">
                (Score: {comp.sullivan_score:.1f}, {comp.size_kb} KB)
            </span>
        </li>'''
    
    html = f'''<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Liste des composants</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
            background: #fff;
            color: #000;
            padding: 20px;
        }}
        .container {{
            max-width: 1200px;
            margin: 0 auto;
        }}
        h1 {{
            font-size: 28px;
            font-weight: bold;
            margin-bottom: 30px;
            border-bottom: 3px solid #000;
            padding-bottom: 10px;
        }}
        ul {{
            list-style: none;
            padding: 0;
        }}
        a:hover {{
            text-decoration: underline;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>Composants disponibles ({len(components)})</h1>
        <ul>
            {items_html}
        </ul>
    </div>
</body>
</html>'''
    
    return html
