# MISSION : Afficher les Composants VISUELLEMENT

**De** : Claude-Code (Senior)
**Pour** : KIMI Padawan
**Date** : 4 février 2026

---

## CONTEXTE

Le layout tableau de l'Arbiter fonctionne. Mais les composants sont affichés comme des **noms textuels** avec checkboxes. L'utilisateur veut voir les **composants rendus graphiquement**.

Exemple actuel (MAUVAIS):
```
☑ Card
☑ Button
☑ Badge
```

Exemple souhaité (BON):
```
┌─────────────────────┐
│ Card Title          │
│ Card content...     │
│            [Action] │
└─────────────────────┘

[Button Label]

[Badge]
```

---

## CE QUE TU DOIS FAIRE

### 1. Dans `studio_routes.py`, modifier la fonction `build_section()`

**Fichier** : `Backend/Prod/sullivan/studio_routes.py`
**Ligne ~1630** : La boucle qui génère `comps_html`

**AVANT** (ligne ~1643-1650):
```python
for comp_id, comp in comps.items():
    comp_info = library.get("categories", {}).get(comp.category, {}).get(comp_id, {})
    comp_name = comp_info.get("name", comp_id.replace("_", " ").title())
    comps_html += f'''
    <div class="comp-item">
        <label>
            <input type="checkbox" checked name="comp_{section_id}_{entry}" value="{comp_id}">
            <span>{comp_name}</span>
        </label>
    </div>
    '''
```

**APRÈS** (rendre le composant visuellement):
```python
for comp_id, comp in comps.items():
    comp_info = library.get("categories", {}).get(comp.category, {}).get(comp_id, {})
    comp_name = comp_info.get("name", comp_id.replace("_", " ").title())
    comp_html = comp_info.get("html", "")  # ← LE HTML DU COMPOSANT
    comp_css = comp_info.get("css", "")    # ← LE CSS DU COMPOSANT

    # Nettoyer le HTML (retirer les commentaires)
    import re
    comp_html_clean = re.sub(r'<!--.*?-->', '', comp_html, flags=re.DOTALL).strip()

    comps_html += f'''
    <div class="comp-visual-item" data-comp-id="{comp_id}">
        <div class="comp-checkbox-row">
            <input type="checkbox" checked name="comp_{section_id}_{entry}" value="{comp_id}">
            <span class="comp-name">{comp_name}</span>
        </div>
        <div class="comp-preview">
            <style scoped>{comp_css}</style>
            {comp_html_clean}
        </div>
    </div>
    '''
```

### 2. Ajouter les styles pour `.comp-visual-item`

Dans le même fichier, dans la section `<style>` (ligne ~1748), ajouter :

```css
/* Composants visuels */
.comp-visual-item {
    border: 1px solid #e0e0e0;
    border-radius: 8px;
    margin-bottom: 12px;
    overflow: hidden;
}
.comp-checkbox-row {
    display: flex;
    align-items: center;
    gap: 8px;
    padding: 8px 12px;
    background: #f8f8f8;
    border-bottom: 1px solid #e0e0e0;
    font-size: 11px;
}
.comp-name {
    font-weight: 600;
    color: #555;
}
.comp-preview {
    padding: 16px;
    background: white;
    transform: scale(0.8);
    transform-origin: top left;
    max-height: 150px;
    overflow: hidden;
}
```

---

## STRUCTURE LIBRARY.JSON

La library contient déjà le HTML et CSS:

```json
{
  "categories": {
    "molecules": {
      "card": {
        "id": "molecules_card",
        "name": "card",
        "html": "<article class=\"card\" role=\"article\">...",
        "css": ".card { --card-bg: white; ... }",
        ...
      }
    }
  }
}
```

Tu dois juste **récupérer** `comp_info["html"]` et `comp_info["css"]` et les injecter.

---

## FICHIERS À MODIFIER

| Fichier | Action |
|---------|--------|
| `Backend/Prod/sullivan/studio_routes.py` | MODIFIER build_section() pour rendre le HTML |

---

## TEST

1. Lance le serveur : `python -m Backend.Prod.api`
2. Va sur `/studio?step=4`
3. Les composants doivent apparaître comme des vrais éléments UI (boutons, cartes, etc.)

---

## NE PAS FAIRE

- ❌ Ne pas créer de nouveaux fichiers
- ❌ Ne pas toucher à `library.json`
- ❌ Ne pas ajouter d'imports externes

## FAIRE

- ✅ Modifier `studio_routes.py` seulement
- ✅ Rendre le HTML/CSS des composants inline
- ✅ Ajouter les styles CSS pour `.comp-visual-item`

---

*— Claude-Code Senior*
