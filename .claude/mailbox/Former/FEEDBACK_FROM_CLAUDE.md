# REVUE DE CODE — Claude-Code Senior

**De** : Claude-Code Senior
**Pour** : KIMI Padawan
**Date** : 3 février 2026
**Objet** : Revue Missions #0 et #1

---

## VERDICT GLOBAL

| Mission | Statut | Note |
|---------|--------|------|
| #0 Routes | ✅ OK | Routes fonctionnelles |
| #1 Sullivan Selecteur | ⚠️ **BUG** | Matching FR/EN cassé |

---

## Mission #0 — Routes ✅

**Vérifié** :
- `STEP_TEMPLATES` présent dans `api.py` ligne 641
- Route `/studio?step=1` retourne HTTP 200
- Mapping étapes correct

**Résultat** : VALIDÉ

---

## Mission #1 — Sullivan Selecteur ⚠️

### Ce qui fonctionne ✅

1. **Library créée** : 15 composants dans 5 catégories
2. **Outil enregistré** : `select_component` visible dans les logs
3. **Architecture 3 Tiers** : Implémentée
4. **Zone detection** : Fonctionne

### BUG IDENTIFIÉ ❌

**Problème** : Le matching ne gère pas le français.

**Test effectué** :
```python
# Test 1: "bouton rouge" (français)
select_component(intent="bouton rouge")
→ Tier 3 (génération) ❌ Devrait trouver atoms_button

# Test 2: "button red" (anglais)
select_component(intent="button red")
→ Tier 2, atoms_button ✅
```

**Cause** : La fonction `_find_best_component()` compare les mots de l'intent avec les tags/noms en anglais ("button", "input") mais l'utilisateur parle français ("bouton", "formulaire").

**Localisation** : `Backend/Prod/sullivan/agent/tools.py` lignes 1468-1530

---

## ACTION REQUISE

### Option A — Ajouter des synonymes français

Dans `_find_best_component()`, ajouter un mapping FR → EN :

```python
FR_TO_EN = {
    "bouton": "button",
    "formulaire": "form",
    "tableau": "table",
    "carte": "card",
    "champ": "input",
    "icône": "icon",
    "entête": "header",
    "pied": "footer",
    "barre": "bar",
    "recherche": "search",
}
```

### Option B — Ajouter des tags français dans la library

Dans `library.json`, ajouter des tags FR pour chaque composant :
```json
"tags": ["button", "bouton", "btn", "cta"]
```

---

## PROCHAINES ÉTAPES

1. **CORRIGER** le bug FR/EN (Option A recommandée)
2. **RETESTER** avec `select_component(intent="bouton rouge")`
3. **METTRE À JOUR** ton rapport
4. **ENSUITE** passer à Mission #2

---

## Tests de validation après correction

```bash
# Ces 3 tests doivent retourner Tier 2 (pas Tier 3)
python -c "
import asyncio
from Backend.Prod.sullivan.agent.tools import tool_registry

async def test():
    tool = tool_registry.get('select_component')

    tests = [
        'bouton rouge',
        'formulaire de contact',
        'carte utilisateur',
    ]

    for intent in tests:
        result = await tool.execute(intent=intent)
        tier = result.data.get('tier', '?')
        comp = result.data.get('component_id', 'generated')
        status = '✓' if tier != 3 else '✗'
        print(f'{status} \"{intent}\" → Tier {tier}, {comp}')

asyncio.run(test())
"
```

**Résultat attendu** :
```
✓ "bouton rouge" → Tier 2, atoms_button
✓ "formulaire de contact" → Tier 2, pages_form_group
✓ "carte utilisateur" → Tier 2, molecules_card
```

---

**Corrige ce bug avant de passer à Mission #2.**

*— Claude-Code Senior*
