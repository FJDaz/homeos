# MISSION URGENTE — Nettoyage Templates

**De** : Claude-Code Senior
**Pour** : KIMI Padawan
**Date** : 3 février 2026
**Priorité** : **URGENTE** (bloque tout le reste)

---

## DÉCISION VALIDÉE : Option A — Tout sur HomeOS

L'utilisateur a validé : **UN SEUL layout** = `studio_homeos.html`

---

## Ce que tu dois faire

### Étape 1 : Backup
```bash
cp Backend/Prod/templates/studio.html Backend/Prod/templates/studio_BACKUP_20260203.html
```

### Étape 2 : Modifier api.py

**Fichier** : `Backend/Prod/api.py`

**A. Supprimer `STEP_TEMPLATES`** (lignes ~641-651) — plus besoin, un seul template

**B. Modifier la route `/studio`** :
```python
@app.get("/studio")
@app.get("/studio/")
async def serve_studio_page(
    request: Request,
    step: int = 1,
    layout: Optional[str] = None
):
    """Studio Sullivan — Layout HomeOS unifié."""
    from fastapi.templating import Jinja2Templates
    templates_dir = Path(__file__).resolve().parent / "templates"
    templates = Jinja2Templates(directory=str(templates_dir))

    # TOUJOURS studio_homeos.html
    return templates.TemplateResponse(
        "studio_homeos.html",
        {"request": request, "step": step, "layout": layout}
    )
```

**C. Modifier la route `/homeos`** — devient un redirect :
```python
from fastapi.responses import RedirectResponse

@app.get("/homeos")
@app.get("/homeos/")
async def serve_homeos_page(request: Request):
    """Redirige vers /studio (layout unifié)."""
    return RedirectResponse(url="/studio", status_code=302)
```

**D. Supprimer la route `/studio/composants`** (lignes ~694-708) :
```python
# SUPPRIMER CETTE ROUTE ENTIÈRE
# @app.get("/studio/composants")
# async def serve_studio_composants(request: Request):
#     ...
```

### Étape 3 : Nettoyer les templates

```bash
# Supprimer les templates obsolètes
rm Backend/Prod/templates/studio.html
rm Backend/Prod/templates/studio_composants.html
```

**Garder uniquement** :
- `studio_homeos.html` ← LE template principal
- `studio_arbitrage_forms.html` ← Fragment HTMX (si utilisé)
- `studio_section_1_4_fragment.html` ← Fragment HTMX (si utilisé)

### Étape 4 : Vérifier studio_homeos.html

Le template doit gérer le paramètre `step` passé par la route.

**Ajouter en haut du `<body>`** (si pas déjà présent) :
```html
<script>
    // Récupérer le step depuis l'URL
    const urlParams = new URLSearchParams(window.location.search);
    const currentStep = parseInt(urlParams.get('step')) || 1;

    // Activer le bon tab selon le step
    document.addEventListener('DOMContentLoaded', function() {
        // step 1-3 → Brainstorm
        // step 4 → Frontend (composants)
        // step 5-9 → Frontend
        let tabIndex = 0;
        if (currentStep >= 4 && currentStep <= 5) tabIndex = 2; // Frontend
        else if (currentStep >= 6) tabIndex = 2; // Frontend aussi

        // Activer le tab
        const tabs = document.querySelectorAll('.tab');
        if (tabs[tabIndex]) {
            tabs[tabIndex].click();
        }
    });
</script>
```

### Étape 5 : Tester

```bash
# Redémarrer le serveur
./start_api.sh

# Tester les routes
curl -I http://localhost:8000/studio        # → 200, studio_homeos.html
curl -I http://localhost:8000/studio?step=4 # → 200, studio_homeos.html
curl -I http://localhost:8000/homeos        # → 302, redirect vers /studio
curl -I http://localhost:8000/studio/composants # → 404 (supprimé)
```

---

## Routes après nettoyage

| Route | Comportement |
|-------|--------------|
| `/studio` | Template HomeOS, step=1 par défaut |
| `/studio?step=4` | Template HomeOS, onglet Frontend |
| `/homeos` | Redirect → `/studio` |
| `/studio/composants` | **SUPPRIMÉ** |

---

## RAPPEL PROTOCOLE

1. [ ] Backup fait
2. [ ] api.py modifié
3. [ ] Templates nettoyés
4. [ ] Tests passés
5. [ ] Rapport mis à jour

---

## Quand tu as terminé

Mets à jour `REPORT_FROM_KIMI.md` avec :
- [ ] Mission CLEANUP : TERMINÉE
- [ ] Routes testées
- [ ] Fichiers supprimés

---

**C'est une mission de NETTOYAGE. Ne crée PAS de nouveaux fichiers, SUPPRIME ceux qui sont obsolètes.**

*— Claude-Code Senior*
