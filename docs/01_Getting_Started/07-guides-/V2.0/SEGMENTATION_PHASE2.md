# Guide de Segmentation - Phase 2 AETHERFLOW

## Principe

La Phase 2 doit être segmentée en **parties testables indépendamment**. Chaque partie peut être testée avec AETHERFLOW avant de passer à la suivante.

## Segmentation Proposée

### Partie 1 : Router de Base (AgentRouter simple)

**Objectif** : Créer un router qui peut sélectionner un agent basique selon la complexité.

**Plan à demander à Claude Code** :
"Crée un plan pour implémenter un AgentRouter de base dans AETHERFLOW qui route vers DeepSeek si complexity < 0.7, sinon vers Claude API. Le router doit être dans `Backend/Prod/models/agent_router.py`."

**Critères de succès** :
- Router créé et fonctionnel
- Peut sélectionner DeepSeek ou Claude selon complexity
- Tests unitaires passent

**Test** :
```bash
python scripts/benchmark.py --plan Backend/Notebooks/benchmark_tasks/phase2_part1_router.json --output output/phase2_part1
```

---

### Partie 2 : Intégration Codestral (FIM)

**Objectif** : Ajouter Codestral comme agent spécialisé pour FIM (Fill-In-the-Middle).

**Plan à demander à Claude Code** :
"Crée un plan pour intégrer Codestral API dans AETHERFLOW comme agent spécialisé pour FIM. Créer `Backend/Prod/models/codestral_client.py` et l'intégrer dans le router."

**Critères de succès** :
- Client Codestral fonctionnel
- Router peut sélectionner Codestral pour tâches FIM
- Tests passent

---

### Partie 3 : Intégration Gemini (Analyse rapide)

**Objectif** : Ajouter Gemini comme agent pour analyse rapide.

**Plan à demander à Claude Code** :
"Crée un plan pour intégrer Gemini API dans AETHERFLOW comme agent pour analyse rapide. Créer `Backend/Prod/models/gemini_client.py` et l'intégrer dans le router."

---

### Partie 4 : Logique de Routage Avancée

**Objectif** : Implémenter la logique de routage intelligente basée sur type/complexity/dépendances.

**Plan à demander à Claude Code** :
"Crée un plan pour améliorer le router avec logique de routage avancée : sélection basée sur type de tâche, complexity, nombre de dépendances, et critères de validation."

---

## Workflow de Test Segmenté

Pour chaque partie :

1. **Claude Code génère le plan** pour la partie
2. **AETHERFLOW exécute** le plan (génère le code)
3. **Script benchmark** collecte les métriques
4. **Claude Code analyse** le rapport markdown généré
5. **Si OK** → Partie suivante, **sinon** → Correction

## Exemple d'Utilisation

```bash
# 1. Claude Code génère phase2_part1_router.json

# 2. Exécuter avec benchmark
python scripts/benchmark.py \
  --plan Backend/Notebooks/benchmark_tasks/phase2_part1_router.json \
  --output output/phase2_part1

# 3. Claude Code lit output/phase2_part1/benchmark_report.md
# 4. Claude Code décide : OK pour Partie 2 ou besoin de corrections
```

## Avantages de la Segmentation

- ✅ Tests isolés et reproductibles
- ✅ Détection précoce des problèmes
- ✅ Validation progressive
- ✅ Facilite le debug
- ✅ Permet d'itérer sur chaque partie
