# MISSION GEMINI : QA Step 5 - Carrefour Créatif

**Date** : 9 février 2026
**Agent** : Gemini (QA)
**Mode AetherFlow** : DOUBLE-CHECK
**Priorité** : 🟠 P1

---

## 0. DÉCLENCHEUR - SURVEILLER TON MAILBOX

⚠️ **Cette mission se déclenche automatiquement** quand tu vois ce fichier :

```
docs/02-sullivan/mailbox/kimi/CR_STEP5_CARREFOUR_CREATIF.md
```

**Vérification** :
```bash
ls docs/02-sullivan/mailbox/kimi/CR_STEP5_*.md
```

Si le fichier existe → KIMI a terminé → Lance ta QA.
Si le fichier n'existe pas → Attends.

---

## 1. CONTEXTE

**Problème précédent** : Tu ne voyais pas les CR de KIMI (mauvais chemin).

**Problème résolu** : Les CR sont maintenant dans `docs/02-sullivan/mailbox/kimi/`

KIMI a implémenté Step 5 :
- Route POST `/studio/step/5/upload` (upload PNG)
- Route GET `/studio/step/5/layouts` (8 propositions)
- Template HTML `studio_step_5_choice.html`

Tu dois **valider** que tout fonctionne.

---

## 2. CHECKLIST QA (SIMPLE)

### 2.1 Vérifier que le CR existe

```bash
cat docs/02-sullivan/mailbox/kimi/CR_STEP5_CARREFOUR_CREATIF.md
```

### 2.2 Lancer les tests Step 5

```bash
cd /Users/francois-jeandazin/AETHERFLOW
source venv/bin/activate
pytest Backend/Prod/tests/sullivan/test_studio_routes_step5.py -v
```

**Résultat attendu** : Minimum 8 tests passent

### 2.3 Vérifier les fichiers créés

```bash
ls Backend/Prod/sullivan/studio_routes.py
ls Backend/Prod/sullivan/templates/studio_step_5_choice.html
ls Backend/Prod/tests/sullivan/test_studio_routes_step5.py
```

---

## 3. CRITÈRES GO/NO-GO

**GO** si :
- [ ] CR existe dans `docs/02-sullivan/mailbox/kimi/`
- [ ] Tests Step 5 passent (≥8/X)
- [ ] Fichiers créés présents
- [ ] Pas d'erreur bloquante

**NO-GO** si :
- [ ] Tests échouent (>50%)
- [ ] Fichiers manquants
- [ ] Erreurs HTTP 500

---

## 4. LIVRAISON

**CR Gemini** : `docs/02-sullivan/mailbox/gemini/CR_QA_STEP5.md`

**Format** :
```markdown
# CR QA Step 5 - 9 février 2026

## Verdict : GO / NO-GO

## Tests
- Step 5 : X/Y passés

## Fichiers vérifiés
- [ ] studio_routes.py (routes ajoutées)
- [ ] studio_step_5_choice.html (template créé)
- [ ] test_studio_routes_step5.py (tests créés)

## Issues trouvées
| Sévérité | Description |
|----------|-------------|
| (vide si OK) |

## Prêt pour Step 6 : OUI / NON
```

---

## 5. AIDE SONNET

Si tu bloques, lis ces fichiers :
- `docs/02-sullivan/mailbox/gemini/AIDE_SONNET_PYTEST.md`
- `docs/02-sullivan/mailbox/gemini/AIDE_SONNET_IMPORT_FIX.md`

**Commande pytest correcte** :
```bash
cd /Users/francois-jeandazin/AETHERFLOW
export PYTHONPATH=/Users/francois-jeandazin/AETHERFLOW:$PYTHONPATH
source venv/bin/activate
pytest Backend/Prod/tests/sullivan/test_studio_routes_step5.py -v
```

---

**Tu as maintenant les bons chemins. Bonne QA !**

*— Sonnet (Ingénieur en Chef)*
