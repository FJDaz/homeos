# MISSION : Implémentation du BRS_MODE (Brainstorming Stratégique)

**Agent** : KIMI / AetherFlow
**Contexte** : Restructuration HomeOS en 4 Corps (BRS, BKD, FRD, DPL)
**Objectif** : Créer le mode de fonctionnement dédié à la Phase BRS.

## 🛠 Tâches à accomplir

### 1. Création de `Backend/Prod/sullivan/modes/brs_mode.py`
Ce mode doit orchestrer la Phase 1 du workflow :
- Appel à `IntentTranslator` (STAR System).
- Intégration du système d'Arbitrage (Stencils).
- **Nouveauté** : Imposer le mapping vers la hiérarchie N0-N3 dès la sortie du BRS.

### 2. Enrichissement du système STAR
- Modifier `intent_translator.py` pour supporter une balise `biological_level` (N0|N1|N2|N3) dans les mappings.
- Assurer que chaque "Realisation" STAR pointe vers un type de composant valide (Atome, Cellule, etc.).

### 3. Workflow de Prototypage Rapide (PROTO)
- Le mode BRS doit fonctionner principalement en mode `-q` (FAST → DOUBLE-CHECK).
- La sortie doit être un `genome_brs_validated.json`.

## 📂 Fichiers cibles
- `Backend/Prod/sullivan/modes/brs_mode.py` (Nouveau)
- `Backend/Prod/sullivan/intent_translator.py` (Refacto)
- `Backend/Prod/sullivan/identity.py` (Vérifier conformité Stencils)

## 📊 Critères de succès
- Un utilisateur peut entrer une phrase libre.
- Le système ressort une liste d'Atomes et de Cellules classés par Organes.
- L'arbitrage permet de filtrer cette liste avant la phase BKD.

---
**Mission générée par Antigravity** - 10 février 2026
