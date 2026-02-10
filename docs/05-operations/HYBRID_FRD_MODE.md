# Hybrid FRD Mode - KIMI + DeepSeek

**Workflow automatisé** : KIMI (code) + DeepSeek (tests) + Sonnet (review)

---

## 🎯 Problème Résolu

**AVANT** :
- KIMI code sans tests
- Tests manuels après coup
- Bugs en production
- Temps perdu en debug

**MAINTENANT** :
- KIMI code (rapide)
- DeepSeek tests TDD (automatique)
- Sonnet review (GO/NO-GO)
- **Qualité garantie** ✅

---

## 🚀 Usage

### Méthode Simple (Recommandée)

```bash
aetherflow --hybrid "Create login component with form validation"
```

Ou avec le wrapper dédié :

```bash
./aetherflow-hybrid "Create login component with form validation"
```

### Méthode 1 : Depuis Mission (Avancée)

```bash
aetherflow sullivan frd hybrid --mission docs/02-sullivan/mailbox/kimi/MISSION_KIMI_STEP6_UI.md
```

### Méthode 2 : Depuis Tâche (Avancée)

```bash
aetherflow sullivan frd hybrid --task "Create login component with form validation"
```

---

## 🔄 Workflow Automatique

### Phase 1 : KIMI Code (5-10 min)

```
📋 Lecture mission
    ↓
💻 KIMI génère code
    ↓
📄 CR_KIMI.md déposé
```

**Output** :
- Code fonctionnel (routes, templates, logic)
- Sans tests (KIMI fait juste le code)

---

### Phase 2 : DeepSeek Tests (5-10 min)

```
📋 Lecture fichiers KIMI
    ↓
🧪 DeepSeek génère tests TDD
    ↓
📄 CR_DEEPSEEK_TESTS.md déposé
```

**Output** :
- Tests unitaires (pytest)
- Coverage >80%
- Mocking dépendances externes
- Edge cases couverts

---

### Phase 3 : Sonnet Review (2 min)

```
📊 Analyse code + tests
    ↓
✅ Verdict GO/NO-GO
    ↓
📄 CR_REVIEW.md déposé
```

**Critères GO** :
- ✅ Tests existent
- ✅ Coverage >80%
- ✅ Tests passent
- ✅ Pas de bugs critiques

---

## 📊 Comparaison

| Workflow | Temps | Tests | Qualité | Bugs |
|----------|-------|-------|---------|------|
| **KIMI seul** | 10 min | ❌ Aucun | ⚠️ Moyenne | 🔴 Fréquents |
| **Manuel** | 30 min | ⚠️ Partiels | ⚠️ Variable | 🟠 Occasionnels |
| **Hybrid** | 20 min | ✅ Complets | ✅ Élevée | 🟢 Rares |

---

## 💡 Exemples

### Exemple 1 : Component UI

```bash
aetherflow --hybrid "Create UserCard component with avatar, name, bio"
```

**Résultat** :
```
✅ KIMI :
   - Frontend/components/UserCard.html
   - Frontend/js/usercard.js
   - Frontend/css/usercard.css

✅ DeepSeek :
   - Backend/Prod/tests/frontend/test_usercard.py
   - Coverage : 87%

✅ Sonnet : GO
```

---

### Exemple 2 : Route API

```bash
aetherflow sullivan frd hybrid --mission docs/02-sullivan/mailbox/kimi/MISSION_KIMI_STEP6_UI.md
```

**Résultat** :
```
✅ KIMI :
   - Backend/Prod/sullivan/studio_routes.py (route /step/6/analyze)
   - Backend/Prod/sullivan/templates/step_6_analysis.html

✅ DeepSeek :
   - Backend/Prod/tests/sullivan/test_studio_step_6.py
   - Coverage : 92%

✅ Sonnet : GO
```

---

## 🔧 Configuration

### Variables d'Environnement

```bash
# Dans .env
HYBRID_FRD_TIMEOUT=600  # 10 min par phase max
HYBRID_FRD_MIN_COVERAGE=80  # Coverage minimum requis
HYBRID_FRD_AUTO_RUN_TESTS=true  # Lancer tests automatiquement
```

---

### Mailbox Paths

```
docs/02-sullivan/mailbox/
├── kimi/
│   ├── MISSION_KIMI_*.md     # Missions pour KIMI
│   └── CR_KIMI_*.md          # CR de KIMI
├── deepseek/
│   ├── MISSION_DEEPSEEK_*.md # Missions auto-générées
│   └── CR_DEEPSEEK_*.md      # CR de DeepSeek
└── REVIEW_*.md               # Reviews Sonnet
```

---

## 📝 Format Mission KIMI (compatible)

**Missions existantes** fonctionnent out-of-the-box :

```markdown
# MISSION KIMI : Step 6 UI

**Objectif** : Créer UI pour Step 6

## Spécifications

- Route /studio/step/6/analyze
- Template HTML
- ...

## Livraison

CR dans mailbox/kimi/
```

**Pas besoin de changer** les missions existantes ! Le mode hybrid les comprend automatiquement.

---

## 🎭 Workflow Détaillé

### 1. User lance commande

```bash
aetherflow --hybrid "Create X"
```

---

### 2. Hybrid Mode démarre

```
╔══════════════════════════════════════╗
║   Hybrid FRD Mode (KIMI + DeepSeek)  ║
╚══════════════════════════════════════╝

🎯 Tâche : Create X
```

---

### 3. Mission auto-créée (si --task)

```markdown
# MISSION KIMI : Create X

**Date** : 2026-02-09
**Agent** : KIMI
**Mode** : Hybrid

## Objectif
Create X

## Critères
- Code fonctionnel
- Tests DeepSeek (auto)
- Review Sonnet GO
```

---

### 4. Phase KIMI

```
⏳ Phase 1 : KIMI génère le code...
   → KIMI travaille...
   → Fichiers créés :
      - Backend/Prod/...
      - Frontend/...
✓ Phase 1 : Code généré
```

---

### 5. Phase DeepSeek

```
⏳ Phase 2 : DeepSeek génère les tests...
   → Analyse fichiers KIMI
   → Génère tests TDD
   → Tests créés :
      - test_....py (Coverage 87%)
✓ Phase 2 : Tests générés
```

---

### 6. Phase Sonnet

```
⏳ Phase 3 : Sonnet review...
   → Vérifie code
   → Vérifie tests
   → Lance pytest
   → Analyse coverage
✓ Phase 3 : Review ✅ GO

╔═══════════════════════════╗
║   WORKFLOW COMPLETED      ║
║   Verdict : GO            ║
║   Ready for production    ║
╚═══════════════════════════╝
```

---

## 🚦 Verdicts Possibles

### ✅ GO

**Conditions** :
- Tous les tests passent
- Coverage >80%
- Pas de bugs critiques
- Code review OK

**Action** : Prêt pour commit/deploy

---

### ❌ NO-GO

**Raisons possibles** :
- Tests échouent
- Coverage <80%
- Bugs critiques détectés
- Code review failed

**Action** : Corriger issues avant production

---

## 💰 Coûts

### Par Workflow

| Phase | Agent | Temps | Coût |
|-------|-------|-------|------|
| KIMI Code | KIMI (Moonshot) | 10 min | ~$0.02 |
| DeepSeek Tests | DeepSeek | 10 min | ~$0.01 |
| Sonnet Review | Sonnet (local) | 2 min | $0 |

**Total par workflow** : **~$0.03** (3 centimes)

---

### Comparaison

**Mode hybride** : $0.03 par feature
**Manuel** : $0 mais 30 min de dev
**Valeur temps** : 30 min = $25 (dev @$50/h)

**ROI** : **833x** (économie $24.97 par feature)

---

## 🎯 Quand Utiliser

### ✅ Utiliser Hybrid Mode pour :

- Nouvelles features (routes, components)
- Refactoring important
- Code critique (auth, paiement)
- API publiques

### ⚠️ Pas besoin pour :

- Typos/fixes mineurs
- Documentation
- Configuration simple
- Prototypes rapides

---

## 🔍 Monitoring

### Voir Progrès en Temps Réel

```bash
# Terminal 1 : Lancer workflow
aetherflow sullivan frd hybrid --task "X"

# Terminal 2 : Monitor KIMI
tail -f docs/02-sullivan/mailbox/kimi/CR_*.md

# Terminal 3 : Monitor DeepSeek
tail -f docs/02-sullivan/mailbox/deepseek/CR_*.md
```

---

### Check Status

```bash
# Lister missions en cours
ls docs/02-sullivan/mailbox/kimi/MISSION_*.md

# Lister CR disponibles
ls docs/02-sullivan/mailbox/kimi/CR_*.md
ls docs/02-sullivan/mailbox/deepseek/CR_*.md
```

---

## 🐛 Dépannage

### Timeout Phase KIMI

**Symptôme** : "KIMI CR not found (timeout)"

**Solution** :
```bash
# Augmenter timeout
export HYBRID_FRD_TIMEOUT=1200  # 20 min

# Relancer
aetherflow sullivan frd hybrid --task "X"
```

---

### Tests Échouent (Phase DeepSeek)

**Symptôme** : Coverage <80% ou tests failed

**Solution** :
1. Vérifier CR DeepSeek
2. Lancer tests manuellement :
   ```bash
   pytest Backend/Prod/tests/... -v
   ```
3. Corriger si nécessaire
4. Relancer review :
   ```bash
   aetherflow sullivan frd review --kimi CR_X.md --deepseek CR_Y.md
   ```

---

## 📚 Voir Aussi

- [WORKFLOW_FRD_KIMI_DEEPSEEK.md](WORKFLOW_FRD_KIMI_DEEPSEEK.md) - Workflow détaillé
- [DEEPSEEK_CHAT_CLI.md](DEEPSEEK_CHAT_CLI.md) - Chat CLI DeepSeek
- [NOTE_SONNET_CHOIX_AGENT.md](../02-sullivan/mailbox/NOTE_SONNET_CHOIX_AGENT.md) - Choix d'agent

---

**Créé le** : 9 février 2026
**Par** : Sonnet (Ingénieur en Chef)
**Status** : 🚧 Beta (à tester)
