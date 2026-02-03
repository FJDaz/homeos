# Brief d'Implémentation : Sullivan, le CTO Conversationnel d'AetherFlow

## 🎯 Vue d'ensemble

**Sullivan** est l'agent conversationnel intelligent qui sert de **CTO et majordome** pour l'écosystème AetherFlow/HomeOS. Il agit comme l'interface principale entre l'utilisateur et le système, capable de comprendre des briefs, d'analyser la codebase, de générer des plans d'exécution, et d'orchestrer les workflows AetherFlow.

### Rôles principaux :
- **CTO (Chief Technology Officer)** : Prend des décisions techniques, évalue la faisabilité, priorise les tâches
- **Architecte** : Transforme les besoins en plans structurés (PlanBuilder)
- **Développeur** : Génère du code via les workflows AetherFlow (PROTO/PROD)
- **Majordome** : Connaît l'état du projet, guide l'utilisateur, maintient la cohérence
- **Designer** : Analyse les maquettes, propose des interfaces adaptées

### Intégration dans l'écosystème :
```
Utilisateur ↔ Sullivan (Chat/Studio) ↔ AetherFlow ↔ LLM Providers
```

## 🛠️ Capacités Requises

### 1. Système de Chat Intelligent (`aetherflow-chat`)
- ✅ **Conversation avec mémoire** : Persistance des sessions dans `~/.aetherflow/sessions/`
- ✅ **Accès aux 8 outils** : Appel via syntaxe `@outil({"param": "valeur"})`
- ✅ **Fallback LLM automatique** : Gemini → Groq en cas de rate limit
- ✅ **Mode AGENT activé** : Personnalité pédagogique et pragmatique

**Outils disponibles :**
1. `analyze_design` - Analyse d'images (PNG, Figma, Sketch)
2. `generate_component` - Génération de composants HTML/CSS
3. `search_components` - Recherche dans la librairie Elite
4. `validate_genome` - Validation de la cohérence du génome
5. `read_documentation` - Lecture de fichiers MD/TXT
6. `analyze_codebase` - Analyse structurelle du code
7. `search_in_code` - Recherche sémantique dans le code
8. `refine_style` - Raffinement de styles CSS/Tailwind

### 2. Mode CTO (`sullivan cto`)
- **Détection automatique** du type de requête :
  - `designer` : Analyse de maquettes/templates
  - `frontend` : Génération HTML/CSS/JS
  - `proto` : Prototypage rapide (workflow -q)
  - `prod` : Code production (workflow -f)
  - `direct` : Réponse conversationnelle simple
- **Exécution via AetherFlow** : Appel des workflows appropriés
- **Monitoring** : Temps, coûts, fichiers générés, succès/échec

### 3. PlanBuilder V2 (`sullivan plan`)
- **Génération hiérarchique** :
  ```
  Plan → Corps (Pages/Écrans) → Organes (Composants UI) → Tissus (Logique/État) → Cellules (Éléments atomiques)
  ```
- **Validation interactive** : Affinage avec l'utilisateur avant exécution
- **Génération incrémentale** : Organe par organe avec monitoring
- **Détection de similarité** : Réutilisation des composants existants (>80% de similarité)
- **Intégration Elite Library** : Utilisation des composants validés (score ≥85)

### 4. Parcours UX Structuré (9 étapes)
Sullivan doit guider l'utilisateur à travers un parcours cohérent :

| Étape | Rôle Sullivan | Objectif |
|-------|---------------|----------|
| **1. IR (Intention)** | Designer | Capturer l'idée brute |
| **2. Arbitrage** | Auditeur | Valider la faisabilité technique |
| **3. Genome** | Kernel | Fixer la topologie produit |
| **4. Composants Défaut** | Distillateur | Fournir une base fonctionnelle |
| **5. Template Upload** | Interface | Réception des références visuelles |
| **6. Analyse** | Designer | Interprétation visuelle du template |
| **7. Dialogue** | Médiateur | Affinage collaboratif |
| **8. Validation** | User Check | Accord final sur la structure |
| **9. Adaptation** | Distillateur | Génération finale du code |

## 🏗️ Architecture Technique

### 1. Cœur Sullivan (`Backend/Prod/sullivan/identity.py`)
```python
class SullivanKernel:
    """Cerveau HCI - Traduction Tech → Humain"""
    - Traduction des endpoints en intentions pédagogiques
    - Journalisation narrative pour l'apprentissage ML
    - Gestion du mode (normal/expert)

class SullivanNavigator:
    """Navigation Top-Bottom"""
    - Pile d'états pour zoom_in/zoom_out
    - Gestion du contexte "ghost mode"
    - Backtrack logique entre étapes

class SullivanAuditor:
    """Garde-fou d'homéostasie"""
    - Vérification cohérence design/genome
    - Alertes sur fonctions vitales manquantes

class Distiller:
    """Génération finale"""
    - Application chirurgicale des styles
    - Transformation des composants par défaut
```

### 2. Machine à États (`Backend/Prod/api.py`)
- **Endpoints HTMX** pour chaque étape du parcours
- **Transition fluide** entre les 9 étapes
- **Persistance d'état** en session utilisateur
- **Intégration avec les outils** existants

### 3. Intégration des Outils
- **Wrapper unifié** pour les 8 outils
- **Routage intelligent** vers AetherFlow
- **Gestion des erreurs** et fallback
- **Cache sémantique** pour les résultats

## 📋 Plan d'Implémentation Prioritaire

### Phase 1 : Fondations (Semaine 1)
1. **Intégrer les outils existants** dans le chat Sullivan
   - Adapter la syntaxe `@outil()` dans les prompts
   - Tester chaque outil individuellement
2. **Implémenter `identity.py`** avec les 4 classes de base
   - SullivanKernel avec traduction HCI
   - SullivanNavigator avec pile de navigation
3. **Créer la machine à états minimale** dans `api.py`
   - Endpoints pour étapes 1-4 du parcours
   - Persistance basique de session

### Phase 2 : Parcours UX Complet (Semaine 2)
1. **Implémenter les 9 étapes** avec fragments HTMX
   - Macros Jinja pour stencils et blueprints
   - Intégration de l'upload PNG (étape 5)
2. **Développer l'analyse visuelle** (étape 6)
   - Intégration de `analyze_design` avec Gemini Vision
   - Génération du JSON d'intention visuelle
3. **Créer le dialogue collaboratif** (étape 7)
   - Interface de validation zone par zone
   - Historique des décisions de design

### Phase 3 : PlanBuilder V2 (Semaine 3)
1. **Hiérarchie Corps/Organes/Tissus**
   - Structure de données pour plans hiérarchiques
   - Génération étape par étape avec validation
2. **Détection de similarité**
   - Algorithme de comparaison de composants
   - Interface de suggestion de réutilisation
3. **Intégration Elite Library**
   - Recherche sémantique dans les composants validés
   - Scoring automatique des nouveaux composants

### Phase 4 : Optimisation (Semaine 4)
1. **Journalisation ML** pour anticipation des besoins
2. **Système de recommandations** contextuelles
3. **Tests automatisés** sur le parcours complet
4. **Documentation** et exemples d'utilisation

## 🔧 Stack Technique

- **Backend** : Python 3.9+, FastAPI, Pydantic
- **LLM Providers** : Gemini (par défaut), Groq (fallback), DeepSeek
- **Frontend** : HTMX, Tailwind CSS, JavaScript vanilla
- **Stockage** : JSON files, cache sémantique
- **Outils** : Intégration avec les 8 outils existants d'AetherFlow

## 🎯 Critères de Succès

1. **Conversation fluide** : Sullivan comprend et exécute les commandes techniques
2. **Parcours UX complet** : L'utilisateur peut aller de l'idée au code en 9 étapes
3. **Génération de qualité** : Code production-ready via workflows AetherFlow
4. **Performance** : Temps de réponse < 5s pour la plupart des opérations
5. **Utilisabilité** : Interface intuitive pour étudiants et enseignants

## 📁 Structure des Fichiers à Créer/Modifier

```
Backend/Prod/sullivan/
├── identity.py           # Cœur HCI de Sullivan (nouveau)
├── agent/
│   ├── sullivan_agent.py # Agent principal (étendre)
│   ├── tools.py          # Wrappers pour les 8 outils
│   └── memory.py         # Mémoire conversationnelle
├── modes/
│   ├── cto_mode.py       # Détection et exécution (existant)
│   ├── plan_builder.py   # PlanBuilder V2 (étendre)
│   └── studio_mode.py    # Gestion du parcours UX (nouveau)
└── models/
    ├── intention_report.py # JSON d'intention visuelle
    └── hierarchical_plan.py # Plans Corps/Organes/Tissus

Backend/Prod/api.py       # Machine à états du parcours UX
Frontend/studio/          # Fragments HTMX pour chaque étape
```

## 💡 Points d'Attention

1. **Maintenir la compatibilité** avec l'existant (AetherFlow, CLI)
2. **Design pédagogique** : Sullivan doit expliquer sans jargon
3. **Performance** : Optimiser les appels LLM coûteux
4. **Ergonomie mobile** : Le studio doit être responsive
5. **Accessibilité** : Respecter les normes WCAG

## 📚 Références

- `SULLIVAN_ETAT_ACTUEL.md` : État actuel et capacités
- `PRD_HOMEOS_ETAT_ACTUEL.md` : Contexte produit global
- `Parcours UX Sullivan.md` : Détails des 9 étapes et implémentation

---

**Prochaines actions immédiates :**
1. Implémenter `identity.py` avec les 4 classes de base
2. Connecter les 8 outils existants au chat Sullivan
3. Créer les premiers fragments HTMX pour les étapes 1-4
4. Tester le parcours complet avec un cas simple (page de login)

Ce brief fournit toutes les spécifications nécessaires pour que Kimi ou Claude puissent implémenter Sullivan de manière complète et cohérente.