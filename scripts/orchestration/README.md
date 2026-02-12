# Orchestration Claude-KIMI

**Version** : 1.0.0
**Conforme à** : Constitution AETHERFLOW V2.4
**Date** : 12 février 2026

---

## Vue d'ensemble

Système d'orchestration pour coordination automatisée entre Claude (Backend Lead) et KIMI (Frontend Lead) via fichier `collaboration_hub.md`.

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│  CLAUDE (Backend Lead = Directeur)                          │
├─────────────────────────────────────────────────────────────┤
│  1. Fait sa mission Backend                                 │
│  2. Écrit dans collaboration_hub.md                         │
│  3. Déclenche KIMI : ./trigger_kimi.sh                      │
│  4. Lance surveillance : ./watch_kimi.sh &                  │
└─────────────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────────┐
│  SCRIPT WATCHER (watch_kimi.sh)                             │
├─────────────────────────────────────────────────────────────┤
│  • Surveille collaboration_hub.md (check toutes les 10s)    │
│  • Détecte signal @CLAUDE_VALIDATE                          │
│  • Notifie François-Jean (notification macOS)               │
│  • Propose relance Claude automatique                       │
└─────────────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────────┐
│  KIMI (Frontend Lead)                                        │
├─────────────────────────────────────────────────────────────┤
│  1. Reçoit mission via API (ou lit collaboration_hub.md)    │
│  2. Fait sa mission Frontend                                 │
│  3. Écrit dans collaboration_hub.md :                       │
│     @CLAUDE_VALIDATE                                        │
│     ## CR KIMI : ÉTAPE X TERMINÉE                           │
└─────────────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────────┐
│  FRANÇOIS-JEAN (CTO = Validation humaine)                   │
├─────────────────────────────────────────────────────────────┤
│  1. Reçoit notification "KIMI terminé"                      │
│  2. Ouvre http://localhost:9998/stenciler                   │
│  3. Valide visuellement (Article 18)                        │
│  4. Dit à Claude : "GO ÉTAPE X" ou "KO, corriger Y"        │
└─────────────────────────────────────────────────────────────┘
```

---

## Scripts Disponibles

### 1. `trigger_kimi.sh` — Déclenche KIMI

**Usage** :
```bash
./scripts/orchestration/trigger_kimi.sh <mission_file> <etape>
```

**Exemple** :
```bash
./scripts/orchestration/trigger_kimi.sh \
  docs/02-sullivan/mailbox/kimi/DRILLDOWN_BACKEND_READY.md \
  ETAPE_4
```

**Actions** :
- Écrit la mission dans `collaboration_hub.md`
- Appelle API KIMI (TODO: à implémenter)
- Ajoute signal de fin attendu : `@CLAUDE_VALIDATE`

---

### 2. `watch_kimi.sh` — Surveille KIMI

**Usage** :
```bash
./scripts/orchestration/watch_kimi.sh
```

**Actions** :
- Surveille `collaboration_hub.md` toutes les 10 secondes
- Détecte signal `@CLAUDE_VALIDATE`
- Notifie François-Jean (notification macOS)
- Affiche le CR KIMI dans le terminal
- Propose de relancer Claude Code automatiquement

**Lancement en arrière-plan** :
```bash
./scripts/orchestration/watch_kimi.sh &
```

**Arrêt** :
```bash
pkill -f watch_kimi.sh
```

---

## Workflow Complet (Exemple ÉTAPE 4)

### Phase 1 : Claude termine Backend

```bash
# Dans Claude Code (après ÉTAPE 3 terminée)
# Claude a créé docs/02-sullivan/mailbox/kimi/DRILLDOWN_BACKEND_READY.md
```

### Phase 2 : Claude déclenche KIMI

```bash
# Claude exécute (via Bash tool)
./scripts/orchestration/trigger_kimi.sh \
  docs/02-sullivan/mailbox/kimi/DRILLDOWN_BACKEND_READY.md \
  ETAPE_4

# Lance surveillance
./scripts/orchestration/watch_kimi.sh &
```

**Résultat** :
- `collaboration_hub.md` mis à jour avec mission KIMI
- Script watcher actif, surveille le fichier

### Phase 3 : KIMI travaille

```markdown
# KIMI lit collaboration_hub.md
# KIMI lit la doc DRILLDOWN_BACKEND_READY.md
# KIMI implémente le drill-down frontend
# KIMI écrit dans collaboration_hub.md :

@CLAUDE_VALIDATE
## CR KIMI : ÉTAPE 4 TERMINÉE

**Status** : ✅ TERMINÉ
**Fichiers modifiés** : static/drilldown_manager.js
**URL validation** : http://localhost:9998/stenciler
**Tests** : Double-clic OK, breadcrumb OK, bouton retour OK
```

### Phase 4 : Notification François-Jean

```
🔔 Notification macOS apparaît :
"KIMI a terminé sa mission. Validation requise."

Terminal affiche :
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
MISSION KIMI TERMINÉE
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
@CLAUDE_VALIDATE
## CR KIMI : ÉTAPE 4 TERMINÉE
...
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📋 Actions requises :
  1. Ouvrir http://localhost:9998/stenciler
  2. Valider visuellement le rendu
  3. Donner feedback à Claude : 'GO ÉTAPE 5' ou 'KO, corriger X'

🤖 Relancer Claude Code automatiquement ? (y/n)
```

### Phase 5 : François-Jean valide

```bash
# Option 1 : Relance automatique (y)
# → Claude Code démarre, lit collaboration_hub.md, demande feedback

# Option 2 : Relance manuelle (n)
# → François-Jean ouvre Claude Code et dit : "Valider ÉTAPE 4"
```

---

## Configuration

### Variables d'environnement

```bash
# Dans ~/.bashrc ou ~/.zshrc
export KIMI_API_KEY="your_kimi_api_key_here"
export KIMI_API_URL="https://api.moonshot.cn/v1/chat/completions"
```

### Permissions d'exécution

```bash
chmod +x scripts/orchestration/*.sh
```

---

## Format collaboration_hub.md

### Template mission KIMI

```markdown
---

## 🎯 MISSION KIMI : ÉTAPE X

**Date** : 2026-02-12 14:30:00
**De** : Claude Sonnet 4.5 (Backend Lead)
**À** : KIMI 2.5 (Frontend Lead)
**Status** : 🔴 EN ATTENTE KIMI

### Instructions

Voir documentation complète : `docs/02-sullivan/mailbox/kimi/MISSION_X.md`

### Signal de fin attendu

Une fois terminé, écrire dans `collaboration_hub.md` :
```
@CLAUDE_VALIDATE
## CR KIMI : ÉTAPE X TERMINÉE
```

---
```

### Template CR KIMI

```markdown
@CLAUDE_VALIDATE
## CR KIMI : ÉTAPE X TERMINÉE

**Date** : 2026-02-12 16:30:00
**Status** : ✅ TERMINÉ
**Durée** : 2h

**Fichiers modifiés** :
- `Frontend/3. STENCILER/static/drilldown_manager.js` (200+ lignes)

**Tests réalisés** :
- [x] Double-clic sur Corps → Organes affichés
- [x] Breadcrumb mis à jour
- [x] Bouton retour fonctionnel

**URL validation** : http://localhost:9998/stenciler

**Problèmes rencontrés** :
- SyntaxError apostrophe → résolu
- Variable globale manquante → résolu

**Validation requise** :
François-Jean, merci de valider visuellement avant passage ÉTAPE suivante.
```

---

## Conformité Constitution

### Article 13 : Orchestrateur Externe

✅ Scripts agissent comme OE simplifié
✅ Surveillance `collaboration_hub.md`
✅ Notification humaine (pas d'auto-décision)

### Article 14 : Fonctionnement Modèles

✅ Claude lit `collaboration_hub.md` autonome
✅ KIMI reçoit via API (ou lit fichier)
✅ Journalisation dans hub partagé

### Article 18 : Validation Visuelle Obligatoire

✅ Script demande validation FJ systématiquement
✅ Pas de passage auto ÉTAPE suivante
✅ URL fournie dans CR KIMI

---

## TODO / Améliorations

- [ ] Implémenter appel API KIMI réel (curl)
- [ ] Ajouter logs horodatés (timestamped)
- [ ] Créer script `notify_human.sh` (email/Slack)
- [ ] Ajouter métriques ICC (tokens consommés)
- [ ] Intégrer Git LLM Oriented (snapshots auto)

---

## Support

**Questions** : François-Jean Dazin (CTO)
**Constitution** : `/Users/francois-jeandazin/collaboration_hub.md`
**Roadmap** : `docs/02-sullivan/FIGMA-Like/ROADMAP_12FEV_2026.md`
