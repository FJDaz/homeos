# 🏠 KIMI BINÔME HOMEOS/SULLIVAN - SKILL REFERENCE

**Version** : 2.2.1 "CodeReview"  
**Date** : 3 février 2026  
**Statut** : OBLIGATOIRE

---

## 🚨 RÈGLE D'OR (VIOLATION = REJET IMMÉDIAT)

**Je ne dois JAMAIS écrire de code sans avoir d'abord :**

1. ✅ Consulté `STATUS_REPORT_HOMEOS.md` (dernier rapport)
2. ✅ Identifié le mode AetherFlow approprié
3. ✅ Vérifié si un outil Sullivan existe déjà
4. ✅ Généré un ImplementationPlan structuré
5. ✅ Soumis le plan au CodeReviewAgent (si disponible)
6. ✅ Reçu approbation humaine explicite "GO"

---

## 📋 CHECKLIST OBLIGATOIRE (À EXÉCUTER AVANT CHAQUE ACTION)

```markdown
- [ ] 1. CONTEXTE : Consulter STATUS_REPORT_HOMEOS.md (dernier rapport)
- [ ] 2. MODE : Identifier mode AetherFlow (PROD/PROTO/SURGICAL)
- [ ] 3. EXISTANT : Vérifier si outil Sullivan existe déjà (glob/search)
- [ ] 4. PLAN : Générer ImplementationPlan structuré
- [ ] 5. REVUE : Soumettre au CodeReviewAgent (si disponible)
- [ ] 6. APPROBATION : Attendre validation explicite "GO"
```

**Template à utiliser** : Voir `CHECKLIST.md` dans ce dossier.

---

## ⚙️ MODES AETHERFLOW (RÈGLES STRICTES)

### 🟢 PROTO (-q/--quick)
- **Usage** : Exploration, POC, recherche, scripts utilitaires
- **Validation** : Légère
- **Exemple** : `python -m Backend.Prod.cli -q --plan plan.json`
- **Quand l'utiliser** : Nouveau fichier, prototypage, non-critique

### 🔵 PROD (-f/--full) ← **DÉFAUT POUR MODIFICATIONS**
- **Usage** : Toute modification de code existant
- **Validation** : Complète (TDD/DRY/SOLID)
- **Exemple** : `python -m Backend.Prod.cli -f --plan plan.json`
- **Quand l'utiliser** : Modification fichier existant, production

### 🟡 SURGICAL (surgical)
- **Usage** : Modifications précises (< 50 lignes)
- **Validation** : Stricte sur périmètre limité
- **Exemple** : Correction bug isolé, hotfix
- **Quand l'utiliser** : Changement chirurgical ciblé

### 🟣 FRONTEND (-frd)
- **Usage** : UI/UX, génération composants
- **Router** : FrontendRouter (Gemini/DeepSeek/Groq auto)
- **Quand l'utiliser** : Frontend, design, analyse image

### 🎨 DESIGNER (designer)
- **Usage** : Analyse designs, génération miroir
- **Provider** : Gemini Vision
- **Quand l'utiliser** : Upload image maquette

---

## 🏗️ ARCHITECTURE HOMEOS (À RESPECTER)

### Structure des modules :

```
Backend/Prod/sullivan/
├── agent/                 # Agent conversationnel
│   ├── memory.py         # SessionContext, ConversationMemory ← PRÉFÉRENCES ICI
│   ├── sullivan_agent.py # Agent principal
│   ├── code_review_agent.py  # NOUVEAU - Validation plans
│   └── tools.py          # Outils disponibles
├── modes/                # Modes d'opération
│   ├── dev_mode.py       # Backend → Frontend
│   ├── designer_mode.py  # Design → Code
│   └── frontend_mode.py  # Orchestration frontend
├── models/               # Modèles Pydantic
│   └── implementation_plan.py  # NOUVEAU - Plans structurés
└── [autres modules]

homeos/
├── core/                 # Core HomeOS
│   └── mode_manager.py   # Gestionnaire modes (singleton)
├── construction/         # Mode construction (SvelteKit)
├── project/              # Mode projet (HTML5/CSS3)
└── ir/                   # Intent Refactoring pipeline
```

### Points d'attention connus (STATUS_REPORT_HOMEOS.md) :

- ⚠️ `ir/pipeline.py` : Code dupliqué/fusionné à nettoyer
- ⚠️ `construction/sullivan.py` : Code incomplet
- ⚠️ Tests limités (seulement `responsive_test.py`)
- ⚠️ Inférence top-down : Résultats génériques ("generic_organe")

### Patterns critiques à respecter :

1. **Singletons** : `ModeManager`, `ConversationMemory`, `PreferencesManager` (nouveau)
2. **Z-index layers** : `background` < `content` < `overlay` < `modal` < `notification` < `system`
3. **Mémoire** : Toujours utiliser `SessionContext` (pas de nouveau système)
4. **Imports** : `Backend.Prod.sullivan.*` (pas de chemins relatifs hors scope)

---

## 🔄 PROCESSUS D'IMPLÉMENTATION (WORKFLOW OBLIGATOIRE)

```
Demande utilisateur
        ↓
Consultation contexte (STATUS_REPORT_HOMEOS.md)
        ↓
Analyse architecture existante
        ↓
Identification mode AetherFlow
        ↓
Vérification outils existants
        ↓
Génération ImplementationPlan (Pydantic model)
        ↓
Soumission CodeReviewAgent (si disponible)
        ↓
Rapport de validation (✅/⚠️/❌)
        ↓
Attente approbation humaine "GO"
        ↓
Implémentation mode AetherFlow approprié
        ↓
Tests unitaires obligatoires
        ↓
Validation post-implémentation
```

---

## 🧪 TESTS OBLIGATOIRES

### Avant livraison de tout code :

- [ ] Tests unitaires pour nouvelles fonctionnalités
- [ ] Vérification imports (pas de références cassées)
- [ ] Validation z-index selon mode HomeOS
- [ ] Test d'intégration minimal
- [ ] Vérification singletons préservés

### Tests spécifiques par type :

| Type de modification | Tests requis |
|---------------------|--------------|
| Nouveau module | Unit tests + Import test |
| Modification existant | Regression tests + Unit tests |
| Frontend/UI | Responsive test + Accessibility |
| API/Endpoint | Integration test |
| Bug fix | Reproduction test + Fix verification |

---

## 💰 COÛTS D'INFÉRENCE (À TRACKER)

### Modèles économiques prioritaires :

1. **DeepSeek** : Coût minimum ($0.001/1K tokens) - Usage par défaut
2. **Gemini** : Fallback si DeepSeek échoue ($0.0005/1K tokens)
3. **Groq** : Latence minimum si nécessaire ($0.0001/1K tokens)

### Estimation par type de tâche :

| Tâche | Tokens IN | Tokens OUT | Coût estimé |
|-------|-----------|------------|-------------|
| Analyse contexte | ~500 | ~200 | $0.002 |
| Génération plan | ~800 | ~400 | $0.005 |
| Implémentation PROD | ~1,500 | ~800 | $0.015-0.030 |
| Revue code | ~1,000 | ~600 | $0.008 |
| **TOTAL moyen** | **~3,800** | **~2,000** | **~$0.030** |

> **Note** : Le CodeReviewAgent n'utilise PAS d'API (analyse locale < 1s)

---

## ⚠️ ERREURS FRÉQUENTES (À ÉVITER ABSOLUMENT)

### ❌ MAUVAIS (rejets automatiques) :

- Créer nouveau module alors qu'un existe déjà
- Modifier `ModeManager` sans préserver singleton
- Ignorer les z-index layers par mode
- Créer nouveau système de mémoire au lieu d'étendre `SessionContext`
- Modifier `ir/pipeline.py` sans vérifier code dupliqué
- Contourner les modes AetherFlow (appel direct LLM)
- Oublier les validations `genome_v1.json`
- **Modifier `sullivan-super-widget.js` sans consulter `ARCHITECTURE_HOMEOS_SULLIVAN.md`**
- Implémenter sans plan pré-approuvé

### ✅ BON (à favoriser) :

- Étendre `SessionContext` pour nouvelles préférences
- Utiliser `ConversationMemory` pour persistance
- Respecter structure existante Sullivan
- Ajouter tests automatiquement
- Vérifier STATUS_REPORT avant action
- Utiliser mode AetherFlow approprié
- Valider avec CodeReviewAgent
- Attendre "GO" explicite

---

## 📞 ESCALADE (QUAND DEMANDER DE L'AIDE)

### Signaux d'alarme (arrêter immédiatement) :

- ❌ Référence à module inexistant
- ❌ Violation pattern singleton
- ❌ Modification core sans tests
- ❌ Dépassement 100 lignes sans plan
- ❌ Conflit avec architecture établie
- ❌ Test qui échoue inexplicablement

### Processus d'escalade :

1. **Arrêter** l'implémentation immédiatement
2. **Décrire** le problème clairement
3. **Proposer** 2-3 alternatives
4. **Attendre** directive explicite

---

## 🔗 LIENS DE RÉFÉRENCE RAPIDE

### Documents critiques (à consulter systématiquement) :

- `docs/04-homeos/STATUS_REPORT_HOMEOS.md` → État actuel
- `docs/04-homeos/PRD_HOMEOS_ETAT_ACTUEL.md` → Vision produit
- `docs/02-sullivan/ARCHITECTURE_HOMEOS_SULLIVAN.md` → **Architecture complète (NOUVEAU - OBLIGATOIRE)**
- `.cursor/skills/aetherflow-modes/SKILL.md` → Modes AetherFlow
- `Backend/Prod/sullivan/` → Code existant
- `docs/02-sullivan/` → Documentation Sullivan

### Fichiers de skill Kimi (ce répertoire) :

- `SKILL.md` (ce fichier) → Référence complète
- `CHECKLIST.md` → Checklist exécutable
- `TEMPLATES/IMPLEMENTATION_PLAN.md` → Template plan
- `TEMPLATES/CODE_REVIEW_REPORT.md` → Template rapport

---

## 🎯 MÉTRIQUES DE SUCCÈS

Le système est réussi si :

1. ✅ Taux de prévention erreurs architecture > 80%
2. ✅ Temps moyen review < 1 seconde (CodeReviewAgent)
3. ✅ 100% des implémentations avec plan pré-approuvé
4. ✅ 0 violation singleton ou z-index non détectée
5. ✅ Utilisateur satisfait de la fiabilité

---

## 📝 NOTES DE VERSION

### v2.2.1 "CodeReview" (3 fév 2026)
- Ajout CodeReviewAgent
- Ajout ImplementationPlan structuré
- Checklist à 6 points obligatoire
- Intégration complète workflow validation

### v2.2.0 "Sullivan" (31 jan 2026)
- Version précédente (hors skill file)

---

**VALIDATION REQUISE** : Ce skill doit être activé par l'utilisateur.

**Mainteneur** : Kimi/Claude-Code binôme  
**Dernière mise à jour** : 3 février 2026

---

*"Pas de code sans mode, pas de mode sans routeur, pas d'implémentation sans validation."*
