# 📝 IMPLEMENTATION PLAN — MISSION #0 ROUTES CONSOLIDATION

**Mission #0** — Consolidation des routes URL pour parcours UX 9 étapes  
**Date** : 3 février 2026  
**Auteur** : Kimi Padawan  
**Statut** : EN ATTENTE VALIDATION CodeReviewAgent

---

## 🏠 HOMEOS/SULLIVAN CONTEXT CHECK

### 📊 Statut
- Date : 2026-02-03
- Auteur : Kimi
- Module cible : Backend/Prod/api.py

### 📋 Checklist pré-action (Protocole Skills)
- [x] 1. Parcours UX lu : `docs/02-sullivan/Parcours UX Sullivan - Résumé exécutif.md` ✅
- [x] 2. Git status vérifié : Modifications en cours sur `feature/code-review-agent` ✅
- [x] 3. Mode AetherFlow : **SURGICAL** — Modification ciblée < 50 lignes
- [x] 4. Routes existantes auditées : 6 routes identifiées
- [x] 5. Templates vérifiés : 3 templates existants
- [x] 6. Plan présenté à l'utilisateur : ✅ GO reçu avec précisions
- [ ] 7. CodeReviewAgent : **EN ATTENTE**

---

## 📋 IMPLEMENTATIONPLAN (JSON)

```json
{
  "module_cible": "Backend/Prod/api.py",
  "mode_aetherflow": "surgical",
  "fichiers_crees": [],
  "fichiers_modifies": [
    "Backend/Prod/api.py"
  ],
  "fichiers_supprimes": [],
  "outils_sullivan_utilises": [],
  "z_index_layers": [],
  "risques_identifies": [
    "Route /studio existante modifiée — risque régression",
    "Validation step 1-9 — comportement fallback à tester"
  ],
  "tests_recommandes": [
    "test_route_studio_step_1",
    "test_route_studio_step_4_composants",
    "test_route_studio_step_invalid",
    "test_route_studio_without_step"
  ],
  "known_attention_points": [
    "Routes API existantes — ne pas casser /studio/genome, /homeos"
  ],
  "description": "Ajout paramètre 'step' (1-9) à la route /studio avec mapping étape→template et fallback studio.html"
}
```

---

## 🎯 Description détaillée

### Objectif
```
Le parcours UX Sullivan comporte 9 étapes (IR, Arbiter, Genome, Composants, Upload, Analyse, Dialogue, Validation, Adaptation).
Actuellement la route /studio ne gère pas le paramètre 'step'.
Cette mission ajoute la gestion du paramètre step avec mapping vers les templates appropriés.
```

### Contexte actuel
```
Routes existantes dans api.py:
- /studio (ligne 640) — sans paramètre step
- /studio/ (ligne 641) — sans paramètre step  
- /studio/genome (ligne 439) — route séparée
- /studio/composants (ligne 662) — route séparée
- /homeos (ligne 652) — layout 4 tabs

Templates disponibles:
- studio.html (étapes 1-3, 5-9)
- studio_composants.html (étape 4)
- studio_homeos.html (layout alternatif)
```

### Solution proposée
```
1. AJOUTER constante STEP_TEMPLATES mapping étape → template
2. MODIFIER route /studio pour accepter paramètre step: int = 1
3. AJOUTER validation step 1-9 avec fallback studio.html
4. PASSER step et layout au template via TemplateResponse
```

---

## 🔍 Analyse détaillée

### Architecture
```
Avant:
/studio → studio.html (toujours même template)

Après:
/studio?step=1 → studio.html (IR)
/studio?step=2 → studio.html (Arbiter)
/studio?step=3 → studio.html (Genome)
/studio?step=4 → studio_composants.html (Composants)
/studio?step=5 → studio.html (Upload)
/studio?step=6 → studio.html (Analyse)
/studio?step=7 → studio.html (Dialogue)
/studio?step=8 → studio.html (Validation)
/studio?step=9 → studio.html (Adaptation)
/studio?step=99 → studio.html (fallback)
/studio → studio.html (default step=1)
```

### Dépendances
```
Aucune dépendance externe supplémentaire.
Utilise FastAPI déjà présent.
```

### Impact sur code existant
```
Fichier: Backend/Prod/api.py
- AJOUT : Dictionnaire STEP_TEMPLATES (lignes à définir)
- MODIFICATION : Signature fonction serve_studio_page() (ligne ~640)
- MODIFICATION : TemplateResponse pour passer step et layout

Pas de modification des autres routes (/studio/genome, /homeos, etc.)
```

---

## ⚠️ Analyse des risques

| Risque | Probabilité | Impact | Mitigation |
|--------|-------------|--------|------------|
| Régression route /studio existante | Moyen | Majeur | Fallback step=1, tests curl |
| Step invalide non géré | Faible | Mineur | Fallback explicite studio.html |
| Conflit paramètre layout | Faible | Mineur | Paramètre optionnel, pas utilisé actuellement |

---

## 🧪 Stratégie de tests

### Tests manuels (curl)
```bash
# Test 1 : Route sans paramètre (backward compatibility)
curl -I "http://localhost:8000/studio"
# Attendu: 200 OK, template studio.html

# Test 2 : Steps valides 1-9
curl -I "http://localhost:8000/studio?step=1"
curl -I "http://localhost:8000/studio?step=4"
curl -I "http://localhost:8000/studio?step=9"
# Attendu: 200 OK

# Test 3 : Step invalide (fallback)
curl -I "http://localhost:8000/studio?step=99"
# Attendu: 200 OK (fallback studio.html)

# Test 4 : Step avec layout
curl -I "http://localhost:8000/studio?step=2&layout=triptyque"
# Attendu: 200 OK

# Test 5 : Autres routes préservées
curl -I "http://localhost:8000/studio/genome"
curl -I "http://localhost:8000/homeos"
curl -I "http://localhost:8000/studio/composants"
# Attendu: 200 OK
```

---

## 📅 Planning d'implémentation

### Étapes détaillées

1. **Étape 1** : Ajouter STEP_TEMPLATES mapping
   - Fichier : `Backend/Prod/api.py`
   - Localisation : Avant la route /studio (ligne ~635)
   - Durée estimée : 2 minutes

2. **Étape 2** : Modifier signature fonction serve_studio_page
   - Fichier : `Backend/Prod/api.py`
   - Localisation : Ligne ~640
   - Modifications : Ajouter step: int = 1, layout: Optional[str] = None
   - Durée estimée : 3 minutes

3. **Étape 3** : Implémenter logique template selection
   - Validation step 1-9
   - Fallback studio.html
   - Passage variables au template
   - Durée estimée : 5 minutes

4. **Étape 4** : Tests curl
   - Durée estimée : 5 minutes

---

## 🔧 Validation technique

### Checklist pré-implémentation
- [x] Architecture alignée avec HomeOS (FastAPI routes)
- [x] Pas de duplication code existant
- [x] Routes existantes préservées

### Checklist post-implémentation
- [ ] /studio fonctionne (backward compat)
- [ ] /studio?step=1 à 9 fonctionnent
- [ ] /studio?step=99 fallback OK
- [ ] /studio/genome préservé
- [ ] /homeos préservé
- [ ] /studio/composants préservé

---

## 💰 Estimation ressources

### Coût inference
| Étape | Modèle | Tokens | Coût |
|-------|--------|--------|------|
| Aucun appel LLM | - | 0 | $0.00 |

### Temps estimé
- Analyse : 10 minutes ✅ (faite)
- Implémentation : 10 minutes
- Tests : 5 minutes
- **Total** : 25 minutes

---

## ✅ VALIDATION REQUISE

### Pour CodeReviewAgent
```markdown
- **APPROUVÉ** : Prêt pour implémentation
- **MODIFICATIONS** : Voir commentaires
- **REJET** : Annuler
```

### Pour utilisateur
```markdown
Après validation CodeReviewAgent, répondre par :
- **GO** : Approuvé pour implémentation SURGICAL
- **MODIFICATIONS** : Ajustements requis
```

---

**Plan prêt pour validation CodeReviewAgent**
