# MISSION GEMINI : QA Step 4 - Validation Stenciler

**Date** : 9 février 2026
**Agent** : Gemini (QA)
**Mode AetherFlow** : DOUBLE-CHECK
**Priorité** : 🟠 P1

---

## 0. DÉCLENCHEUR - SURVEILLER TON MAILBOX

⚠️ **Cette mission se déclenche automatiquement** quand tu vois ce fichier :

```
docs/02-sullivan/mailbox/gemini/HANDOFF_KIMI_STEP4_ROUTES.md
```

**Vérification** :
```bash
ls docs/02-sullivan/mailbox/gemini/HANDOFF_KIMI_*.md
```

Si le fichier existe → KIMI a terminé → Lance ta QA.
Si le fichier n'existe pas → Attends.

---

## 1. CONTEXTE

KIMI a implémenté :
- Classe `Stenciler` dans `identity.py` (25 tests)
- Routes API dans `studio_routes.py`

Tu dois **valider** que tout fonctionne correctement.

---

## 2. CHECKLIST QA

### 2.1 Code Review

- [ ] Lire `Backend/Prod/sullivan/identity.py` (lignes 577-767)
- [ ] Vérifier la structure de la classe `Stenciler`
- [ ] Vérifier les 9 méthodes documentées
- [ ] Pas de code mort ou dupliqué

### 2.2 Tests

```bash
cd /Users/francois-jeandazin/AETHERFLOW
source venv/bin/activate
pytest Backend/Prod/tests/sullivan/test_stenciler.py -v
pytest Backend/Prod/tests/sullivan/test_studio_routes.py -v
```

- [ ] Tous les tests Stenciler passent (25 attendus)
- [ ] Tous les tests routes passent
- [ ] Pas de warning ou deprecation

### 2.3 Intégration

```bash
# Démarrer l'API
python -m uvicorn Backend.Prod.api:app --reload --port 8000

# Tester les routes
curl http://localhost:8000/studio/stencils
curl -X POST http://localhost:8000/studio/stencils/select -H "Content-Type: application/json" -d '{"component_id":"phase_1_ir","status":"keep"}'
curl http://localhost:8000/studio/stencils/validated
```

- [ ] GET /studio/stencils retourne les 9 Corps
- [ ] POST /studio/stencils/select fonctionne
- [ ] GET /studio/stencils/validated retourne le genome filtré

### 2.4 Qualité

- [ ] Pas d'erreur mypy sur `identity.py`
- [ ] Docstrings présentes
- [ ] Noms de variables clairs

---

## 3. CRITÈRES GO/NO-GO

**GO** si :
- Tous les tests passent
- Routes API fonctionnelles
- Pas de bug bloquant

**NO-GO** si :
- Tests échouent
- Routes 500 error
- Code non maintenable

---

## 4. LIVRAISON

**CR** : `docs/02-sullivan/mailbox/gemini/CR_QA_STEP4.md`

Format :
```markdown
# CR QA Step 4 - 9 février 2026

## Verdict : GO / NO-GO

## Tests
- Stenciler : X/25 passed
- Routes : X/X passed

## Issues trouvées
| Sévérité | Fichier | Ligne | Description |
|----------|---------|-------|-------------|

## Recommandations
- ...

## Prêt pour Step 5 : OUI / NON
```

---

**Bonne validation !**
