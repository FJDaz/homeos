# AetherFlow Status Report: Transition to V3 "Simplicity"

**Date**: March 2, 2026  
**Objectif**: Évaluer l'état actuel de l'orchestrateur (v2.3) et tracer la route vers une V3 radicalement simplifiée.

---

## 1. Audit Technique : L'Héritage V2

### 1.1 Complexité et Code Mort (Backend)
- **Bloat des Points d'Entrée** : `cli.py` (105 KB) et `api.py` (53 KB) sont saturés. Une unification en un `UnifiedExecutor` est impérative.
- **Redondance des Workflows** : `frd.py`, `proto.py` et `verify_fix.py` partagent ~80% de logique avec `prod.py`. C'est du code "zombie" à fusionner.
- **Surgical Editor (Dette Technique)** : `surgical_editor.py` (44 KB) est devenu trop complexe à maintenir. La V3 doit privilégier des méthodes plus simples (Smart Overwrite / Range-based).
- **Sullivan Legacy** : Plusieurs modules dans `Backend/Prod/sullivan/` (evaluators, analyzer) semblent orphelins ou sous-utilisés par rapport au nouveau moteur Stenciler V3.
- **HomeOS V2 (Overkill)** : Les modules de `homeos_v2` (Bayesian, Vigilance) apportent une complexité non alignée avec la cible "Simple V3".

### 1.2 Liste Détaillée du Code Mort / Legacy
Voici les composants identifiés pour suppression ou archivage immédiat en V3 :
- **Workflows Redondants** : `Backend/Prod/workflows/frd.py`, `proto.py`, `verify_fix.py`.
- **Sullivan Legacy** :
    - `Backend/Prod/sullivan/evaluators/` (accessibility, performance).
    - `Backend/Prod/sullivan/analyzer/design_analyzer.py`.
    - `Backend/Prod/sullivan/modes/` (`designer_mode.py`, `dev_mode.py`, `hybrid_frd_mode.py`).
- **Tests Obsolètes** : `test_registry.py`, `test_intent_translator.py`, `test_component_generator.py`.
- **Générations Temporaires** : Tous les `*.generated.py` persistants dans l'arborescence `sullivan/`.

### 1.3 État de la Roadmap Stenciler V3 (Frontend)
- **Phase 10 (Detail Cascade)** : ✅ Mission 10A (Atom-First) livrée.
- **Phase 11 (Illustration Mode)** : ✅ 11A/B (Group Edit & Inspector) livrés.
- **Phase 12 (Pivot Bottom-Up)** : ✅ 12A (SVG-Native Composition) livré. Le moteur est désormais WYSIWYG.
- **Phase 13 (Design System)** : 🔄 13A-DESIGN stabilisé, mais le cache Service Worker (SW) reste un bloqueur majeur à l'itération rapide.
- **Phase 14 (Édition Opérationnelle)** : 🚀 Mission 14A/B (Panel Primitives & Persistance RAM) livrées. Prochaines étapes : 14C (Copie/Duplication) et 14D (Sullivan Embedded).

---

## 2. Points de friction majeurs ("Hotspots")

1. **State Sync (Genome <-> Canvas)** : La remontée des modifications du Stenciler vers le Génome (Write-back) passe par trop d'intermédiaires, rendant la persistance incertaine.
2. **Setup Environnement** : Trop de dépendances (`astunparse`, FastAPI, etc.) pour un outil qui se veut "Standalone".
3. **Debug de Step** : Suivre l'état d'un plan multi-steps à travers les types `FAST`, `BUILD`, et `DOUBLE-CHECK` manque de clarté visuelle unifiée (le CLI est verbeux).

---

## 3. Stratégie Pivot V3 : "Pristine Mode"

### 3.1 Unification du Noyau (Core)
- **Workflow Unique** : Remplacer les N classes par un `UnifiedExecutor` paramétrable.
- **Simplification de l'Apply** : Prioriser le "Smart Overwrite" et le "Range Replacement" (via regex/search) plutôt que l'AST pur pour plus de résilience.
- **Fusion CLI/API** : Un seul cœur de moteur, exposé par deux interfaces légères.

### 3.2 Frontend "SVG-Native"
- **Abandon Définitif de WireframeLibrary** : Tout doit passer par l'`AtomRenderer` sémantique pour garantir le WYSIWYG.
- **Mode Sandbox par Défaut** : Simplifier le flux KIMI en rendant l'injection SVG payload standard au lieu d'une surcharge.

### 3.3 Roadmap V3 Prioritaire
1. **[V3-A] UnifiedExecutor** : Suppression de `workflows/*.py` au profit d'un seul exécuteur robuste.
2. **[V3-B] Fix Cache SW** : Résoudre le blocage du Service Worker pour libérer les itérations de design 14C/D.
3. **[V3-C] Sullivan Embedded** : Migration finale de l'UI Sullivan vers une intégration native Stenciler (La Valise).

---

**Conclusion** : AetherFlow v2.3 est une plateforme puissante mais "baroque". La V3 doit être une cure de minimalisme technique pour gagner en vitesse d'exécution et en facilité de contribution.
