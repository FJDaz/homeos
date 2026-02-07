# MISSION #0 POUR KIMI PADAWAN — PRIORITÉ ABSOLUE

**De** : Claude-Code (Senior)
**Pour** : KIMI Padawan
**Date** : 3 février 2026
**Priorité** : **BLOQUANTE** (faire AVANT toute autre mission)
**Statut** : EN ATTENTE D'EXÉCUTION

---

## STOP — Cette mission est BLOQUANTE

Tu ne peux PAS commencer les autres missions (Sullivan Selecteur, Arbiter) sans avoir d'abord consolidé les routes URL.

---

## Contexte

Le parcours UX Sullivan suit **9 étapes** (voir `docs/02-sullivan/Parcours UX Sullivan - Résumé exécutif.md`) :

| Étape | Nom | URL cible |
|-------|-----|-----------|
| 1 | IR (Intention) | `/studio?step=1` |
| 2 | Arbiter | `/studio?step=2` |
| 3 | Genome | `/studio?step=3` |
| 4 | Composants Défaut | `/studio/composants` |
| 5 | Template Upload | `/studio?step=5` |
| 6 | Analyse | `/studio?step=6` |
| 7 | Dialogue | `/studio?step=7` |
| 8 | Validation | `/studio?step=8` |
| 9 | Adaptation | `/studio?step=9` |

**Routes alternatives** :
- `/homeos` → Layout HomeOS avec 4 tabs
- `/studio/genome` → Visualisation Génome

---

## Routes existantes dans api.py

```python
@app.get("/studio")           # Ligne 640
@app.get("/studio/")          # Ligne 641
@app.get("/homeos")           # Ligne 652
@app.get("/homeos/")          # Ligne 653
@app.get("/studio/composants") # Ligne 662
@app.get("/studio/genome")    # Ligne 439
```

---

## Ta mission

### Étape 1 : Auditer les routes existantes
**Fichier** : `Backend/Prod/api.py`

Vérifie que chaque route :
1. Existe et fonctionne
2. Pointe vers le bon template
3. Gère le paramètre `step` si applicable

### Étape 2 : Consolider la route `/studio`
**Fichier** : `Backend/Prod/api.py`

La route `/studio` doit :
1. Accepter un paramètre `step` (1-9)
2. Accepter un paramètre `layout` (optionnel)
3. Retourner le template approprié selon l'étape

```python
@app.get("/studio")
@app.get("/studio/")
async def serve_studio_page(
    request: Request,
    step: int = 1,
    layout: Optional[str] = None
):
    """
    Studio Sullivan - Parcours en 9 étapes

    Args:
        step: Étape du parcours (1-9)
        layout: Layout optionnel (triptyque, dashboard, etc.)
    """
    # Vérifier que le template existe
    # Passer step et layout au template
    return templates.TemplateResponse(
        "studio.html",  # ou studio_homeos.html selon le step
        {"request": request, "step": step, "layout": layout}
    )
```

### Étape 3 : Créer un mapping étape → template
**Fichier** : `Backend/Prod/api.py`

```python
STEP_TEMPLATES = {
    1: "studio.html",           # IR
    2: "studio.html",           # Arbiter
    3: "studio.html",           # Genome
    4: "studio_composants.html", # Composants
    5: "studio.html",           # Upload
    6: "studio.html",           # Analyse
    7: "studio.html",           # Dialogue
    8: "studio.html",           # Validation
    9: "studio.html",           # Adaptation
}
```

### Étape 4 : Vérifier les templates existent
**Dossier** : `Backend/Prod/templates/`

Vérifie que ces templates existent :
- [ ] `studio.html`
- [ ] `studio_homeos.html`
- [ ] `studio_composants.html`

Si un template manque, **signale-le dans ton rapport** (ne le crée pas toi-même).

### Étape 5 : Tester les routes
```bash
# Test route studio avec step
curl -I "http://localhost:8000/studio?step=1"
curl -I "http://localhost:8000/studio?step=5&layout=triptyque"

# Test routes spécifiques
curl -I "http://localhost:8000/studio/composants"
curl -I "http://localhost:8000/studio/genome"
curl -I "http://localhost:8000/homeos"
```

---

## RAPPEL PROTOCOLE OBLIGATOIRE

**AVANT de coder, tu DOIS** :

1. [ ] Lire `docs/02-sullivan/Parcours UX Sullivan - Résumé exécutif.md`
2. [ ] Vérifier `git status`
3. [ ] Mode identifié : **SURGICAL** (modification ciblée api.py)
4. [ ] Lister les routes existantes
5. [ ] Présenter ton plan à l'utilisateur
6. [ ] Attendre "GO" explicite

---

## Quand tu as terminé

Crée un fichier rapport :
```
.claude/mailbox/REPORT_FROM_KIMI.md
```

Avec :
- [ ] Routes consolidées
- [ ] Templates vérifiés (existants/manquants)
- [ ] Tests exécutés
- [ ] Prêt pour Mission #1 (Sullivan Selecteur)

---

## Après cette mission

Une fois les routes consolidées, tu peux passer à :
1. **Mission #1** : `TASK_FOR_KIMI.md` (Sullivan Selecteur)
2. **Mission #2** : `TASK_FOR_KIMI_02.md` (Arbiter Interface)

---

**C'est une mission de préparation. Ne te lance pas dans les missions suivantes sans avoir consolidé les routes.**

*— Claude-Code Senior*
