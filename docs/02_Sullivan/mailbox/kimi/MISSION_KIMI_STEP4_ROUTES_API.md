# MISSION KIMI : Step 4.5 - Routes API Stenciler

**Date** : 9 février 2026
**Agent** : KIMI (FRD Lead)
**Mode AetherFlow** : BUILD
**Priorité** : 🔴 P0

---

## 0. RAPPEL - CHARGER TES SKILLS

⚠️ **AVANT de commencer** :

```
.cursor/skills/
├── GENERAL.md
├── kimi-binome/SKILL.md
├── kimi-binome/CHECKLIST.md
└── aetherflow-modes/
```

---

## 1. CONTEXTE

Tu as créé la classe `Stenciler` dans `identity.py` (Step 4 ✅).

Maintenant il faut exposer cette classe via des **routes API** pour que le frontend puisse l'utiliser.

---

## 2. OBJECTIF

Créer 3 routes dans `Backend/Prod/sullivan/studio_routes.py` :

| Route | Méthode | Description |
|-------|---------|-------------|
| `/studio/stencils` | GET | Liste des 9 Corps avec leur SVG |
| `/studio/stencils/select` | POST | Marquer un composant keep/reserve |
| `/studio/stencils/validated` | GET | Retourne le genome filtré (keep only) |

---

## 3. SPÉCIFICATIONS

### 3.1 GET /studio/stencils

**Response** :
```json
{
  "corps": [
    {
      "id": "phase_1_ir",
      "name": "Phase 1 - IR",
      "svg": "<svg>...</svg>",
      "components": [
        {"id": "comp_1", "name": "...", "status": "keep|reserve|none"}
      ]
    }
  ],
  "stats": {
    "total": 29,
    "keep": 10,
    "reserve": 5
  }
}
```

### 3.2 POST /studio/stencils/select

**Request** :
```json
{
  "component_id": "comp_1",
  "status": "keep"  // ou "reserve"
}
```

**Response** :
```json
{
  "success": true,
  "component_id": "comp_1",
  "status": "keep"
}
```

### 3.3 GET /studio/stencils/validated

**Response** :
```json
{
  "genome": { ... },  // genome filtré (keep only)
  "stats": {
    "total_kept": 10,
    "total_reserved": 5
  }
}
```

---

## 4. FICHIERS À MODIFIER

1. **`Backend/Prod/sullivan/studio_routes.py`**
   - Importer `stenciler` depuis `identity.py`
   - Ajouter les 3 routes

2. **`Backend/Prod/api.py`** (si nécessaire)
   - S'assurer que le router studio est inclus

---

## 5. TESTS

Créer/modifier `Backend/Prod/tests/sullivan/test_studio_routes.py` :

```python
def test_get_stencils():
    response = client.get("/studio/stencils")
    assert response.status_code == 200
    assert "corps" in response.json()

def test_select_component():
    response = client.post("/studio/stencils/select", json={
        "component_id": "phase_1_ir",
        "status": "keep"
    })
    assert response.status_code == 200

def test_get_validated_genome():
    response = client.get("/studio/stencils/validated")
    assert response.status_code == 200
    assert "genome" in response.json()
```

---

## 6. CRITÈRES D'ACCEPTATION

- [ ] Route GET /studio/stencils fonctionne
- [ ] Route POST /studio/stencils/select fonctionne
- [ ] Route GET /studio/stencils/validated fonctionne
- [ ] Tests passent
- [ ] Pas de régression sur les autres routes

---

## 7. LIVRAISON

**CR KIMI** : `docs/02-sullivan/mailbox/kimi/CR_STEP4_ROUTES_API.md`

**IMPORTANT - Handoff Gemini** :
Quand tu as terminé, dépose aussi une copie dans le dossier Gemini pour déclencher la QA :

```
docs/02-sullivan/mailbox/gemini/HANDOFF_KIMI_STEP4_ROUTES.md
```

Contenu du handoff :
```markdown
# Handoff KIMI → Gemini : Step 4.5 Routes API

**Date** : [date]
**De** : KIMI
**Pour** : Gemini

## Statut
Routes API terminées. Prêt pour QA.

## Fichiers modifiés
- Backend/Prod/sullivan/studio_routes.py
- Backend/Prod/tests/sullivan/test_studio_routes.py

## Tests
[résultat pytest]

## Action requise
Lire ta mission : `MISSION_GEMINI_QA_STEP4.md`
```

---

**Bonne mission !**
