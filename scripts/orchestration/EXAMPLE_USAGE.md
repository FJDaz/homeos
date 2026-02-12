# Exemple d'Usage — Orchestration Claude-KIMI

**Scénario** : ÉTAPE 4 (Drill-down Frontend)

---

## Contexte

Claude vient de terminer ÉTAPE 3 (Drill-down Backend) :
- ✅ Endpoints créés (`/api/drilldown/enter`, `/exit`, `/breadcrumb`)
- ✅ Documentation écrite ([DRILLDOWN_BACKEND_READY.md](../../docs/02-sullivan/mailbox/kimi/DRILLDOWN_BACKEND_READY.md))
- ✅ Backend redémarré

**Objectif** : Déclencher KIMI pour implémenter le frontend.

---

## Phase 1 : Claude déclenche KIMI

### Dans Claude Code

```bash
# Claude exécute via Bash tool
cd /Users/francois-jeandazin/AETHERFLOW

# Déclencher KIMI
./scripts/orchestration/trigger_kimi.sh \
  docs/02-sullivan/mailbox/kimi/DRILLDOWN_BACKEND_READY.md \
  ETAPE_4

# Lancer surveillance
./scripts/orchestration/watch_kimi.sh &
```

### Terminal output

```
🚀 Déclenchement KIMI...
📄 Mission : docs/02-sullivan/mailbox/kimi/DRILLDOWN_BACKEND_READY.md
🎯 Étape : ETAPE_4

✅ Mission écrite dans collaboration_hub.md
📢 KIMI devrait démarrer sa mission

🔍 Pour surveiller : ./scripts/orchestration/watch_kimi.sh
```

### collaboration_hub.md mis à jour

```markdown
---

## 🎯 MISSION KIMI : ETAPE_4

**Date** : 2026-02-12 14:30:00
**De** : Claude Sonnet 4.5 (Backend Lead)
**À** : KIMI 2.5 (Frontend Lead)
**Status** : 🔴 EN ATTENTE KIMI

### Instructions

Voir documentation complète : `docs/02-sullivan/mailbox/kimi/DRILLDOWN_BACKEND_READY.md`

### Signal de fin attendu

Une fois terminé, écrire dans `collaboration_hub.md` :
```
@CLAUDE_VALIDATE
## CR KIMI : ETAPE_4 TERMINÉE
```

---
```

### Watcher actif

```
👀 Surveillance KIMI démarrée...
📄 Fichier surveillé : /Users/francois-jeandazin/collaboration_hub.md
⏱️  Intervalle : 10s

.........
```

---

## Phase 2 : KIMI travaille

KIMI reçoit la mission (via API ou lit `collaboration_hub.md`) :

1. Lit `DRILLDOWN_BACKEND_READY.md`
2. Implémente drill-down frontend :
   - Écoute double-clic sur Canvas
   - Appelle API `/api/drilldown/enter`
   - Affiche enfants (Organes)
   - Breadcrumb dynamique
   - Bouton retour
3. Teste le rendu
4. Écrit son compte-rendu

### KIMI écrit dans collaboration_hub.md

```markdown
@CLAUDE_VALIDATE
## CR KIMI : ETAPE_4 TERMINÉE

**Date** : 2026-02-12 16:30:00
**Status** : ✅ TERMINÉ
**Durée** : 2h

**Fichiers modifiés** :
- `Frontend/3. STENCILER/static/drilldown_manager.js` (200+ lignes)

**Tests réalisés** :
- [x] Double-clic sur Corps → Organes affichés
- [x] Breadcrumb mis à jour : "Brainstorm > Idéation Rapide"
- [x] Bouton retour fonctionnel
- [x] Enfants rendus physiquement sur canvas

**Problèmes résolus** :
- SyntaxError apostrophe non échappée → résolu
- Variable `tarmacCanvas` non globale → exposée via `window`

**URL validation** : http://localhost:9998/stenciler

**Validation requise** :
François-Jean, merci de valider visuellement avant passage ÉTAPE 5.
```

---

## Phase 3 : Notification François-Jean

### Watcher détecte signal

```
...........

✅ Signal KIMI détecté : @CLAUDE_VALIDATE
📢 Notification François-Jean...

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
MISSION KIMI TERMINÉE
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
@CLAUDE_VALIDATE
## CR KIMI : ETAPE_4 TERMINÉE

**Date** : 2026-02-12 16:30:00
**Status** : ✅ TERMINÉ
**Durée** : 2h
...
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📋 Actions requises :
  1. Ouvrir http://localhost:9998/stenciler
  2. Valider visuellement le rendu
  3. Donner feedback à Claude : 'GO ÉTAPE 5' ou 'KO, corriger X'

🤖 Relancer Claude Code automatiquement ? (y/n) _
```

### Notification macOS apparaît

```
╔════════════════════════════════════════╗
║  AETHERFLOW Orchestration              ║
║                                        ║
║  KIMI a terminé sa mission.            ║
║  Validation requise.                   ║
║                                        ║
║  [OK]                                  ║
╚════════════════════════════════════════╝
🔔 Son : "Ping"
```

---

## Phase 4 : François-Jean valide

### Étape 1 : Validation visuelle

François-Jean ouvre le navigateur :

```
http://localhost:9998/stenciler
```

**Tests** :
1. ✅ Double-clic sur Corps "Brainstorm" → Organes s'affichent
2. ✅ Breadcrumb visible : "Brainstorm > Idéation Rapide"
3. ✅ Bouton retour fonctionne
4. ✅ Enfants rendus physiquement

### Étape 2 : Feedback à Claude

**Option A** : Tout OK → GO ÉTAPE 5

```
# Dans terminal watcher
🤖 Relancer Claude Code automatiquement ? (y/n) y

🚀 Relance de Claude Code...
```

**Claude démarre** :

```
KIMI a terminé. Lire collaboration_hub.md pour validation.
```

François-Jean dit :

```
✅ ÉTAPE 4 validée. GO ÉTAPE 5 (Sauvegarde persistance).
```

**Option B** : Problème détecté → KO

```
# Dans terminal watcher
🤖 Relancer Claude Code automatiquement ? (y/n) n

⏸️  Relance manuelle requise : Ouvrir Claude Code et dire 'Valider KIMI'
```

François-Jean ouvre Claude Code :

```
❌ Problème ÉTAPE 4 : Le breadcrumb ne se met pas à jour correctement.
Demander à KIMI de corriger.
```

Claude analyse et relance KIMI avec correction.

---

## Phase 5 : Passage ÉTAPE suivante

### Si validation OK

Claude marque ÉTAPE 4 comme terminée dans la roadmap :

```markdown
### ÉTAPE 4 : Drill-down Frontend (✅ TERMINÉE)

**Status** : ✅ **TERMINÉE 16:30**
**CR KIMI** : Voir `collaboration_hub.md`
**Validation FJ** : ✅ OK

**✅ CLAUDE PEUT DÉMARRER ÉTAPE 5**
```

Claude démarre ÉTAPE 5 (Sauvegarde persistance).

### Si validation KO

Claude crée une nouvelle mission KIMI :

```bash
./scripts/orchestration/trigger_kimi.sh \
  docs/02-sullivan/mailbox/kimi/CORRECTION_ETAPE_4.md \
  ETAPE_4_CORRECTION
```

Cycle recommence jusqu'à validation OK.

---

## Résumé Workflow

```
┌─────────────────────┐
│  CLAUDE termine     │
│  Backend (ÉTAPE 3)  │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│  trigger_kimi.sh    │ ← Claude exécute
│  + watch_kimi.sh &  │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│  KIMI travaille     │
│  (Frontend)         │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│  KIMI écrit signal  │
│  @CLAUDE_VALIDATE   │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│  Watcher détecte    │
│  → Notif FJ         │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│  FJ valide rendu    │
│  (Article 18)       │
└──────────┬──────────┘
           │
      ┌────┴────┐
      │         │
      ▼         ▼
    ✅ GO     ❌ KO
      │         │
      │         └──► Correction KIMI
      │
      ▼
┌─────────────────────┐
│  ÉTAPE suivante     │
│  (Claude continue)  │
└─────────────────────┘
```

---

## Notes Importantes

1. **Validation humaine obligatoire** (Article 18) : Pas de passage auto ÉTAPE suivante
2. **Script watcher non bloquant** : Claude peut continuer à travailler pendant surveillance
3. **Signal `@CLAUDE_VALIDATE`** : Convention claire, facile à détecter
4. **Relance Claude optionnelle** : François-Jean choisit manuel/auto

---

## Dépannage

### Watcher ne détecte pas signal

```bash
# Vérifier signal dans collaboration_hub.md
grep "@CLAUDE_VALIDATE" /Users/francois-jeandazin/collaboration_hub.md

# Relancer watcher
./scripts/orchestration/watch_kimi.sh
```

### Notification macOS ne s'affiche pas

```bash
# Vérifier permissions notifications système
# Préférences Système > Notifications > Terminal

# Tester manuellement
osascript -e 'display notification "Test" with title "Test Notif"'
```

### KIMI ne répond pas

```bash
# Vérifier clé API
echo $KIMI_API_KEY

# Relancer trigger manuellement
./scripts/orchestration/trigger_kimi.sh <mission> <etape>
```
