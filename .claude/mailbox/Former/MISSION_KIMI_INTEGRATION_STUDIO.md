# MISSION KIMI : Integrer le drilldown dans le studio

**De** : Claude-Code Senior
**Pour** : KIMI Padawan
**Date** : 5 fevrier 2026
**Priorite** : HAUTE

---

## Objectif

Le drilldown-sidebar.html fonctionne en standalone.
Maintenant il faut l'integrer dans le studio existant (step 4+).

## Ce que tu dois faire

### 1. Creer une route dans studio_routes.py

Ajouter dans `Backend/Prod/sullivan/studio_routes.py` :

```python
@router.get("/drilldown", response_class=HTMLResponse)
async def get_drilldown_view(request: Request):
    """Vue drill-down du genome enrichi."""
    # Lire le fichier drilldown-sidebar.html
    from pathlib import Path
    html_path = Path("Frontend/drilldown-sidebar.html")
    if html_path.exists():
        return HTMLResponse(content=html_path.read_text())
    return HTMLResponse(content="<p>Drilldown not available</p>")
```

### 2. Creer une route pour servir le genome enrichi

```python
@router.get("/genome/enriched", response_class=JSONResponse)
async def get_enriched_genome():
    """Retourne le genome enrichi pour le drilldown."""
    import json
    from pathlib import Path
    genome_path = Path("output/studio/genome_enrichi.json")
    if genome_path.exists():
        return JSONResponse(content=json.loads(genome_path.read_text()))
    return JSONResponse(content={"error": "Genome enrichi non disponible"})
```

### 3. Modifier le fetch dans drilldown-sidebar.html

Remplacer :
```javascript
const response = await fetch('/output/studio/genome_enrichi.json');
```

Par :
```javascript
const response = await fetch('/studio/genome/enriched');
```

### 4. Ajouter un lien dans le studio principal

Dans le template studio (step 4 ou apres l'Arbiter), ajouter un bouton/lien :

```html
<a href="/studio/drilldown" class="btn btn-primary">
    Ouvrir le Drill-Down
</a>
```

Ou en HTMX si on veut charger dans la zone principale :

```html
<div hx-get="/studio/drilldown" hx-target="#studio-main-zone" hx-trigger="click">
    Drill-Down
</div>
```

## Fichiers concernes

- `Backend/Prod/sullivan/studio_routes.py` — ajouter 2 routes
- `Frontend/drilldown-sidebar.html` — modifier le fetch URL

## Important

- NE MODIFIE PAS le reste de studio_routes.py
- Ajoute les routes AVANT la ligne `__all__ = ["router"]`
- Teste avec : http://localhost:8000/studio/drilldown

---

*— Claude-Code Senior*
