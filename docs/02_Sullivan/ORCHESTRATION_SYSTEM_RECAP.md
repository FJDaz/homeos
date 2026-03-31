# Système d'Orchestration Claude-KIMI — Récapitulatif

**Date** : 12 février 2026
**Mode** : Aetherflow `-q` (Quick)
**Statut** : ✅ Implémenté et documenté

---

## 🎯 Votre Question Initiale

> **"Tu es le directeur. On a un fichier commun entre toi et KIMI. Tu fais ta part, tu l'ajoutes au fichier commun, tu déclenches KIMI par fetch de son API, tu lui dis va voir le fichier, il va voir, il fait sa mission, tu lui as indiqué de signaler qu'il a fini, il a fini et là question : est-ce qu'un script peut te déclencher ?"**

### ✅ Réponse : OUI

Un script peut me déclencher **indirectement** via :
1. Détection signal KIMI (`@CLAUDE_VALIDATE`)
2. Notification François-Jean (macOS)
3. Proposition relance Claude Code (avec confirmation y/n)

---

## 📦 Ce Qui a Été Créé

### Scripts d'Orchestration

```
scripts/orchestration/
├── trigger_kimi.sh          3.3KB — Déclenche KIMI depuis Claude
├── watch_kimi.sh            2.4KB — Surveille signal KIMI
├── test_workflow.sh         2.3KB — Test simulation complète
├── README.md                9.5KB — Documentation complète
├── QUICKSTART.md            2.7KB — Démarrage 3 minutes
├── EXAMPLE_USAGE.md         8.9KB — Exemple ÉTAPE 4 détaillé
└── ARCHITECTURE.txt        15KB  — Diagramme ASCII complet
```

### Documentation Centrale

```
docs/02-sullivan/
├── ORCHESTRATION_CLAUDE_KIMI.md  — Récapitulatif technique (créé)
└── ORCHESTRATION_SYSTEM_RECAP.md — Ce fichier (récapitulatif FJ)
```

---

## 🔄 Workflow Implémenté

```
┌────────────────────────────────────────────────────┐
│ PHASE 1 : CLAUDE (Backend Lead = Directeur)       │
│                                                    │
│ 1. Claude termine Backend (ex: ÉTAPE 3)           │
│ 2. Écrit mission dans collaboration_hub.md        │
│ 3. Déclenche KIMI : ./trigger_kimi.sh             │
│ 4. Lance surveillance : ./watch_kimi.sh &         │
└─────────────────────┬──────────────────────────────┘
                      ↓
┌────────────────────────────────────────────────────┐
│ PHASE 2 : KIMI (Frontend Lead)                    │
│                                                    │
│ 1. Lit mission dans collaboration_hub.md          │
│ 2. Fait sa mission Frontend                       │
│ 3. Écrit signal : @CLAUDE_VALIDATE                │
└─────────────────────┬──────────────────────────────┘
                      ↓
┌────────────────────────────────────────────────────┐
│ PHASE 3 : SCRIPT WATCHER                          │
│                                                    │
│ 1. Détecte @CLAUDE_VALIDATE                       │
│ 2. Notifie François-Jean (macOS)                  │
│ 3. Affiche CR KIMI                                │
│ 4. Propose : Relancer Claude ? (y/n)              │
└─────────────────────┬──────────────────────────────┘
                      ↓
┌────────────────────────────────────────────────────┐
│ PHASE 4 : FRANÇOIS-JEAN (Validation)              │
│                                                    │
│ 1. Ouvre http://localhost:9998/stenciler          │
│ 2. Valide visuellement (Article 18)               │
│ 3. Choisit : y (auto) ou n (manuel)               │
│ 4. Feedback : "GO ÉTAPE X" ou "KO, corriger"      │
└────────────────────────────────────────────────────┘
```

---

## 🚀 Utilisation Pratique

### Test Rapide (Simulation)

```bash
cd /Users/francois-jeandazin/AETHERFLOW
./scripts/orchestration/test_workflow.sh
```

**Résultat attendu** :
- ✅ Mission écrite
- ✅ Signal détecté
- ✅ Notification affichée

---

### Usage Réel (Exemple ÉTAPE 4)

#### 1. Claude termine Backend (ÉTAPE 3)

```bash
# Dans Claude Code, après avoir créé la doc KIMI
```

#### 2. Claude déclenche orchestration

```bash
./scripts/orchestration/trigger_kimi.sh \
  docs/02-sullivan/mailbox/kimi/DRILLDOWN_BACKEND_READY.md \
  ETAPE_4

./scripts/orchestration/watch_kimi.sh &
```

#### 3. KIMI travaille et signale fin

```markdown
# KIMI écrit dans collaboration_hub.md
@CLAUDE_VALIDATE
## CR KIMI : ETAPE_4 TERMINÉE

**Status** : ✅ TERMINÉ
**URL** : http://localhost:9998/stenciler
```

#### 4. Notification François-Jean

```
🔔 Notification macOS :
"KIMI a terminé sa mission. Validation requise."

Terminal :
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
MISSION KIMI TERMINÉE
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
@CLAUDE_VALIDATE
## CR KIMI : ETAPE_4 TERMINÉE
...
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📋 Actions requises :
  1. Ouvrir http://localhost:9998/stenciler
  2. Valider visuellement
  3. Feedback : 'GO ÉTAPE 5' ou 'KO, corriger X'

🤖 Relancer Claude Code automatiquement ? (y/n) _
```

#### 5. Vous validez

**Si OK** :
```
y ← Taper 'y'
→ Claude redémarre
→ "✅ GO ÉTAPE 5"
```

**Si problème** :
```
n ← Taper 'n'
→ Ouvrir Claude manuellement
→ "❌ Breadcrumb ne fonctionne pas, corriger"
```

---

## 📋 Format collaboration_hub.md

### Mission écrite par Claude

```markdown
---

## 🎯 MISSION KIMI : ETAPE_4

**Date** : 2026-02-12 14:30:00
**De** : Claude Sonnet 4.5 (Backend Lead)
**À** : KIMI 2.5 (Frontend Lead)
**Status** : 🔴 EN ATTENTE KIMI

### Instructions

Voir : `docs/02-sullivan/mailbox/kimi/DRILLDOWN_BACKEND_READY.md`

### Signal de fin attendu

```
@CLAUDE_VALIDATE
## CR KIMI : ETAPE_4 TERMINÉE
```

---
```

### CR écrit par KIMI

```markdown
@CLAUDE_VALIDATE
## CR KIMI : ETAPE_4 TERMINÉE

**Date** : 2026-02-12 16:30:00
**Status** : ✅ TERMINÉ
**Durée** : 2h

**Fichiers modifiés** :
- `static/drilldown_manager.js` (200+ lignes)

**Tests** : ✅ Double-clic OK, breadcrumb OK, retour OK

**URL** : http://localhost:9998/stenciler
```

---

## ⚙️ Configuration Requise

### 1. Permissions scripts

```bash
chmod +x scripts/orchestration/*.sh
```

### 2. Variables environnement (optionnel pour API KIMI)

```bash
# Dans ~/.bashrc ou ~/.zshrc
export KIMI_API_KEY="your_key"
```

---

## ✅ Conformité Constitution V2.4

- **Article 13** : Scripts = OE simplifié ✅
- **Article 14** : Claude lit hub autonome, KIMI via API ✅
- **Article 17** : Frontière hermétique préservée ✅
- **Article 18** : Validation visuelle obligatoire ✅
- **Article 24** : Créé en mode Aetherflow `-q` ✅

---

## 🎯 Avantages

1. **Semi-automatisation** : Notification auto, validation humaine
2. **Traçabilité** : Historique complet dans `collaboration_hub.md`
3. **Flexibilité** : Relance auto OU manuelle (choix FJ)
4. **Simplicité** : Scripts bash, faciles à modifier

---

## 📚 Documentation Détaillée

**Démarrage 3 min** : [scripts/orchestration/QUICKSTART.md](../../scripts/orchestration/QUICKSTART.md)

**Doc complète** : [scripts/orchestration/README.md](../../scripts/orchestration/README.md)

**Exemple ÉTAPE 4** : [scripts/orchestration/EXAMPLE_USAGE.md](../../scripts/orchestration/EXAMPLE_USAGE.md)

**Architecture visuelle** : [scripts/orchestration/ARCHITECTURE.txt](../../scripts/orchestration/ARCHITECTURE.txt)

**Récap technique** : [ORCHESTRATION_CLAUDE_KIMI.md](ORCHESTRATION_CLAUDE_KIMI.md)

---

## 🔮 Prochaines Étapes

### ÉTAPE 5 : Sauvegarde persistance ✅ TERMINÉE

- ✅ `save_to_file()` ajouté dans `GenomeStateManager`
- ✅ Chargement auto au démarrage
- ✅ Tests réussis

**Validation FJ requise** avant passage ÉTAPE 6.

---

### ÉTAPE 6 : Connexion Backend réelle (SUIVANT)

**Qui** : KIMI (Claude vérifie)
**Durée** : 30min

**Tâches** :
- Remplacer `fetch('/static/4_corps_preview.json')` par `fetch('http://localhost:8000/api/genome')`
- Adapter parsing `data.genome.n0_phases`
- Gestion erreurs

---

### ÉTAPE 7 : Undo/Redo Backend (SI TEMPS)

**Qui** : Claude uniquement
**Durée** : 1h

**Tâches** :
- Créer `POST /api/modifications/undo`
- Créer `POST /api/modifications/redo`
- Ajouter `undo_stack` et `redo_stack` dans `ModificationLog`
- Retourner nouvel état après undo/redo
- Documenter avec exemples

**Note** : KIMI attend la fin de cette étape avant ÉTAPE 8.

---

## 🛠️ Commandes Essentielles

```bash
# Déclencher KIMI
./scripts/orchestration/trigger_kimi.sh <mission_file> <etape>

# Surveiller KIMI
./scripts/orchestration/watch_kimi.sh

# Arrêter surveillance
pkill -f watch_kimi.sh

# Test système
./scripts/orchestration/test_workflow.sh
```

---

## 📊 Statut Actuel Roadmap

| Étape | Statut | Validation FJ |
|-------|--------|---------------|
| 1. PropertyEnforcer Backend | ✅ | ✅ |
| 2. PropertyEnforcer Frontend | ✅ | ✅ |
| 3. Drill-down Backend | ✅ | ✅ |
| 4. Drill-down Frontend | ✅ | ✅ |
| **5. Sauvegarde persistance** | **✅** | **⏳ EN ATTENTE** |
| 6. Connexion Backend réelle | 🟡 | — |
| 7. Undo/Redo Backend | 🟡 | — |
| 8. Undo/Redo Frontend | 🟡 | — |

**Minimum viable (ÉTAPES 1-6)** : 5/6 terminées

---

## 🎯 Résumé

### Question : "Est-ce qu'un script peut te déclencher ?"

### ✅ Réponse : OUI

Le workflow que vous avez proposé est **opérationnel** :

```
✅ Claude = Directeur
✅ Fichier commun = collaboration_hub.md
✅ Déclenchement KIMI = trigger_kimi.sh
✅ KIMI signale fin = @CLAUDE_VALIDATE
✅ Script déclenche Claude = watch_kimi.sh (avec votre confirmation)
✅ Validation humaine = préservée (Article 18)
```

**Le système est prêt à l'emploi !**

---

## 📞 Support

**Questions** : Demander à Claude
**Test** : `./scripts/orchestration/test_workflow.sh`
**Roadmap** : [docs/02-sullivan/FIGMA-Like/ROADMAP_12FEV_2026.md](FIGMA-Like/ROADMAP_12FEV_2026.md)

---

**Créé le** : 12 février 2026, 15:45
**Par** : Claude Sonnet 4.5 (Backend Lead)
**Mode** : Aetherflow `-q` (Quick)
