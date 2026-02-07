# AUDIT TEMPLATES — Nettoyage Urgent

**Date** : 3 février 2026
**Problème** : Chaos total dans les routes et templates

---

## État actuel (BORDEL)

### Templates existants
```
Backend/Prod/templates/
├── studio.html                    # VIEUX - Triptyque Revue/Arbitrage/Distillation
├── studio_homeos.html             # NOUVEAU - 4 tabs + sidebar + chatbox
├── studio_composants.html         # ISOLÉ - Grille composants sans layout
├── studio_arbitrage_forms.html    # FRAGMENT - Partiel HTMX
└── studio_section_1_4_fragment.html # FRAGMENT - Partiel HTMX
```

### Routes actuelles
| Route | Template | Layout |
|-------|----------|--------|
| `/studio` | `studio.html` | Triptyque VIEUX |
| `/studio?step=4` | `studio_composants.html` | Aucun (page isolée) |
| `/homeos` | `studio_homeos.html` | 4 tabs + sidebar NOUVEAU |
| `/studio/composants` | `studio_composants.html` | Aucun (doublon) |

### Problèmes identifiés

1. **Deux layouts incompatibles** :
   - `studio.html` = triptyque (Revue/Arbitrage/Distillation)
   - `studio_homeos.html` = 4 tabs (Brainstorm/Backend/Frontend/Deploy)

2. **Navigation cassée** :
   - `/homeos` → `/studio?step=4` = changement de layout complet
   - Perte du contexte (sidebar, chatbox, tabs)

3. **Doublons** :
   - `/studio/composants` et `/studio?step=4` → même template
   - Mais comportements différents

4. **Noms confus** :
   - "Studio Homeos" vs "HoméOS Sullivan" — c'est quoi le bon nom ?

---

## DÉCISION À PRENDRE

### Option A — Tout sur HomeOS (RECOMMANDÉ)

**Garder** : `studio_homeos.html` comme UNIQUE layout
**Supprimer** : `studio.html` (vieux triptyque)
**Modifier** : Toutes les routes pointent vers `studio_homeos.html`

```
/studio → studio_homeos.html (avec paramètre step)
/homeos → studio_homeos.html
/studio/composants → SUPPRIMER (utiliser /studio?step=4)
```

**Avantage** : UN SEUL layout, navigation cohérente

### Option B — Garder les deux (COMPLEXE)

**Garder** : Les deux layouts
**Séparer** :
- `/studio` = ancien mode (triptyque)
- `/homeos` = nouveau mode (4 tabs)

**Inconvénient** : Double maintenance, confusion utilisateur

---

## PLAN DE NETTOYAGE (si Option A validée)

### Étape 1 : Backup
```bash
cp Backend/Prod/templates/studio.html Backend/Prod/templates/studio_BACKUP.html
```

### Étape 2 : Unifier les routes dans api.py
```python
# SUPPRIMER ou REDIRIGER
# @app.get("/studio/composants") → rediriger vers /studio?step=4

# MODIFIER
@app.get("/studio")
@app.get("/studio/")
async def serve_studio_page(request: Request, step: int = 1):
    # TOUJOURS retourner studio_homeos.html
    return templates.TemplateResponse(
        "studio_homeos.html",
        {"request": request, "step": step}
    )

# /homeos devient un alias de /studio
@app.get("/homeos")
async def serve_homeos_page(request: Request):
    return RedirectResponse("/studio")
```

### Étape 3 : Modifier studio_homeos.html pour gérer les steps
Ajouter une logique JS/HTMX pour afficher le bon contenu selon `step` :
- step=1-3 → Brainstorm tab
- step=4 → Frontend tab (composants)
- step=5-9 → Frontend tab

### Étape 4 : Nettoyer les fichiers
```bash
# Supprimer après validation
rm Backend/Prod/templates/studio.html
rm Backend/Prod/templates/studio_composants.html
```

---

## QUESTION POUR L'UTILISATEUR

**Quel layout veux-tu garder ?**

- [ ] **Option A** : HomeOS (4 tabs + sidebar + chatbox) — `studio_homeos.html`
- [ ] **Option B** : Triptyque (Revue/Arbitrage/Distillation) — `studio.html`
- [ ] **Option C** : Les deux (routes séparées)

---

*En attente de décision avant nettoyage.*

*— Claude-Code Senior*
