# MISSION GEMINI : Audit Codebase - Phase 1 (Corrections Critiques)

**Date** : 8 février 2026
**Assigné à** : Gemini (Terminal)
**Statut** : EN ATTENTE
**Référence** : `docs/support/audit/AUDIT_CODEBASE_COMPLET.md`

---

## 🎯 OBJECTIF

Exécuter les corrections critiques P0 de l'audit pour faire passer le score de **6.5/10 → 7/10**.

---

## 📋 TÂCHES À EXÉCUTER (dans l'ordre)

### 1. Installer les type stubs manquants

```bash
cd /Users/francois-jeandazin/AETHERFLOW && source venv/bin/activate
pip install types-PyYAML types-requests
```

**Résultat attendu** : Installation réussie

---

### 2. Mettre à jour les dépendances sécurisées (sans conflit)

```bash
pip install --upgrade "jinja2>=3.1.6"
pip install --upgrade pip
```

**Résultat attendu** : jinja2 3.1.6+, pip 26.0+

---

### 3. Corriger le MD5 restant dans semantic_cache.py

Le fichier `Backend/Prod/cache/semantic_cache.py` ligne 228 a encore un appel MD5 sans `usedforsecurity=False`.

**Action** : Modifier la ligne 228 :
```python
# AVANT
return hashlib.md5(prompt.encode()).hexdigest()

# APRÈS
return hashlib.md5(prompt.encode(), usedforsecurity=False).hexdigest()
```

---

### 4. Vérifier les corrections

```bash
pip-audit 2>&1 | head -30
bandit Backend/Prod/cache/semantic_cache.py -ll
```

**Résultat attendu** :
- jinja2 et pip ne sont plus listés dans pip-audit
- Pas d'alerte HIGH sur semantic_cache.py

---

### 5. Exécuter les tests

```bash
pytest Backend/Prod/tests -v --tb=short 2>&1 | tee docs/support/audit/pytest_report.txt | tail -100
```

**Résultat attendu** : Rapport de tests généré

---

## 📝 COMPTE-RENDU À FOURNIR

Après exécution, créer le fichier :
`/Users/francois-jeandazin/AETHERFLOW/.claude/mailbox/CR_GEMINI_AUDIT_PHASE1.md`

Avec le format :

```markdown
# CR GEMINI : Audit Phase 1

**Date** : [date]
**Statut** : ✅ TERMINÉ / ⚠️ PARTIEL / ❌ BLOQUÉ

## Résultats

| Tâche | Statut | Notes |
|-------|--------|-------|
| Type stubs | ✅/❌ | ... |
| jinja2 upgrade | ✅/❌ | version finale |
| pip upgrade | ✅/❌ | version finale |
| MD5 fix | ✅/❌ | ... |
| pip-audit | ✅/❌ | CVEs restantes |
| pytest | ✅/❌ | X passed, Y failed |

## Problèmes Rencontrés

[Détails si applicable]

## Prochaines Actions Suggérées

[Suggestions pour Phase 2]
```

---

## ⚠️ ATTENTION

- **NE PAS** mettre à jour `llama-index` (conflits connus)
- **NE PAS** mettre à jour `starlette` sans tester FastAPI
- **NE PAS** modifier d'autres fichiers que `semantic_cache.py`

---

**Merci Gemini !**
