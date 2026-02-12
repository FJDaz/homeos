# Système de Surveillance KIMI

**Version** : 2.0.0
**Date** : 12 février 2026, 21:00
**Auteur** : Claude Sonnet 4.5 (Backend Lead)
**Conformité** : Constitution AETHERFLOW V2.4, Article 10

---

## 📋 Vue d'ensemble

Ce système permet à Claude (Backend Lead) de déléguer des tâches à KIMI (Frontend Lead) et d'être automatiquement notifié quand KIMI termine.

**Workflow** :
```
Claude → trigger_kimi.sh → collaboration_hub.md
                              ↓
                           KIMI lit et travaille
                              ↓
                         @CLAUDE_VALIDATE écrit
                              ↓
                        watch_kimi.sh détecte
                              ↓
                      Notification François-Jean
```

---

## 🚀 Scripts Disponibles

### 1. trigger_kimi.sh

Crée une mission KIMI dans `collaboration_hub.md`.

**Usage** :
```bash
./scripts/orchestration/trigger_kimi.sh ETAPE_10
./scripts/orchestration/trigger_kimi.sh 10
```

**Ce qu'il fait** :
- Normalise le numéro d'étape (10 → ETAPE_10)
- Vérifie que l'étape existe dans la roadmap
- Recherche la documentation KIMI associée
- Extrait les tâches KIMI depuis la roadmap
- Écrit la mission dans `collaboration_hub.md`
- Affiche confirmation

**Exemple de sortie** :
```
✅ Mission KIMI créée : ETAPE_10

📋 Tâches déléguées :
  - [ ] Double-clic → contentEditable ou input overlay
  - [ ] Enter → appel PATCH Backend
  - [ ] Escape → annulation

📄 Documentation : docs/02-sullivan/mailbox/kimi/INLINE_EDIT_BACKEND_READY.md
🔗 Validation : http://localhost:9998/stenciler

⏳ En attente signal @CLAUDE_VALIDATE dans collaboration_hub.md

ℹ️  François-Jean, KIMI peut commencer sa mission.
```

---

### 2. watch_kimi.sh

Surveille `collaboration_hub.md` et détecte le signal `@CLAUDE_VALIDATE` de KIMI.

**Usage** :
```bash
# Avant-plan (bloque le terminal)
./scripts/orchestration/watch_kimi.sh

# Arrière-plan (libère le terminal)
./scripts/orchestration/watch_kimi.sh &

# Arrêter
Ctrl+C (avant-plan) ou kill <PID> (arrière-plan)
```

**Ce qu'il fait** :
- Vérifie `collaboration_hub.md` toutes les 10 secondes
- Détecte le signal `@CLAUDE_VALIDATE`
- Envoie notification macOS
- Affiche le CR KIMI formaté dans le terminal
- Propose de relancer Claude Code (y/n)

**Exemple de sortie** :
```
ℹ️  Démarrage surveillance collaboration_hub.md
ℹ️  Intervalle: 10s
ℹ️  Signal attendu: @CLAUDE_VALIDATE
ℹ️  Appuyez sur Ctrl+C pour arrêter

[10 secondes plus tard...]

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
MISSION KIMI TERMINÉE
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

@CLAUDE_VALIDATE
## CR KIMI : ETAPE_10 TERMINÉE

**Date** : 2026-02-12 21:00:00
**Status** : ✅ TERMINÉ

[...]

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📋 Actions requises :
  1. Ouvrir http://localhost:9998/stenciler
  2. Valider visuellement (Article 10 Constitution)
  3. Feedback : 'GO ÉTAPE suivante' ou 'KO, corriger X'

🤖 Relancer Claude Code automatiquement ? (y/n) _
```

---

## 🎯 Workflow Complet

### Scénario : ÉTAPE 10 (Édition inline)

**1. Claude termine Backend**
```bash
# Claude a créé l'endpoint PATCH /api/components/{id}/property
# Claude a écrit la doc dans docs/02-sullivan/mailbox/kimi/INLINE_EDIT_BACKEND_READY.md
```

**2. Claude déclenche KIMI**
```bash
./scripts/orchestration/trigger_kimi.sh 10
```

**3. Claude lance surveillance**
```bash
./scripts/orchestration/watch_kimi.sh &
```

**4. KIMI travaille**
```markdown
# KIMI lit collaboration_hub.md
# KIMI implémente édition inline
# KIMI écrit :

@CLAUDE_VALIDATE
## CR KIMI : ETAPE_10 TERMINÉE
[...]
```

**5. Notification François-Jean**
```
🔔 Notification macOS : "KIMI a terminé sa mission. Validation requise."
```

**6. François-Jean valide**
```
http://localhost:9998/stenciler

Si OK → "y" → Claude Code redémarre
Si KO → "n" → Claude relance KIMI avec corrections
```

---

## 🛠️ Configuration

### Prérequis

- Bash 4.0+
- macOS (pour notifications osascript)
- Fichiers requis :
  - `collaboration_hub.md` (créé automatiquement si absent)
  - `docs/02-sullivan/FIGMA-Like/ROADMAP_12FEV_2026.md`

### Variables d'environnement

Aucune configuration requise. Les scripts utilisent des chemins relatifs.

---

## 📐 Format collaboration_hub.md

### Mission KIMI (écrite par trigger_kimi.sh)

```markdown
---

## 🎯 MISSION KIMI : ETAPE_10

**Date** : 2026-02-12 21:00:00
**De** : Claude Sonnet 4.5 (Backend Lead)
**À** : KIMI 2.5 (Frontend Lead)
**Status** : 🔴 EN ATTENTE KIMI

### Instructions

Voir documentation complète : `docs/02-sullivan/mailbox/kimi/INLINE_EDIT_BACKEND_READY.md`

### Tâches à réaliser

- [ ] Double-clic → contentEditable ou input overlay
- [ ] Enter → appel PATCH Backend
- [ ] Escape → annulation

### Signal de fin attendu

Une fois terminé, écrire dans `collaboration_hub.md` :
```
@CLAUDE_VALIDATE
## CR KIMI : ETAPE_10 TERMINÉE
```

**URL validation** : http://localhost:9998/stenciler

---
```

### CR KIMI (écrit par KIMI)

```markdown
@CLAUDE_VALIDATE
## CR KIMI : ETAPE_10 TERMINÉE

**Date** : 2026-02-12 21:30:00
**Status** : ✅ TERMINÉ

**Fichiers modifiés** :
- Frontend/3. STENCILER/static/inline_editor.js

**Tests réalisés** :
- [x] Double-clic OK
- [x] Enter → sauvegarde OK
- [x] Escape → annulation OK

**URL validation** : http://localhost:9998/stenciler

Validation François-Jean requise.
```

---

## 🔍 Dépannage

### Problème : "Fichier collaboration_hub.md introuvable"

**Solution** : Le script crée automatiquement le fichier s'il est absent.

### Problème : "ETAPE_X introuvable dans la roadmap"

**Solution** : Vérifier que l'étape existe dans `docs/02-sullivan/FIGMA-Like/ROADMAP_12FEV_2026.md`

### Problème : "osascript non disponible"

**Solution** : Les notifications macOS ne fonctionneront pas, mais le reste du script fonctionne.

### Problème : Watcher ne détecte pas le signal

**Vérifications** :
```bash
# Vérifier que @CLAUDE_VALIDATE est bien dans le fichier
grep "@CLAUDE_VALIDATE" collaboration_hub.md

# Vérifier que le watcher tourne
ps aux | grep watch_kimi

# Logs du watcher (si lancé en arrière-plan)
tail -f /tmp/watch_kimi.log  # si logs activés
```

---

## 🎨 Personnalisation

### Modifier l'intervalle de surveillance

Éditer `watch_kimi.sh` :
```bash
readonly CHECK_INTERVAL=10  # Changer ici (en secondes)
```

### Changer le signal de détection

Éditer `watch_kimi.sh` :
```bash
readonly MARKER="@CLAUDE_VALIDATE"  # Changer ici
```

### Désactiver notifications macOS

Commenter la ligne dans `watch_kimi.sh` :
```bash
# send_notification "Aetherflow" "KIMI a terminé sa mission. Validation requise."
```

---

## ✅ Conformité Constitution

### Article 10 : Validation Visuelle Obligatoire

- ✅ URL validation systématiquement incluse
- ✅ Signal force intervention François-Jean
- ✅ Pas de passage automatique étape suivante

### Article 1 : Frontière Hermétique

- ✅ Claude = directeur (Backend Lead)
- ✅ KIMI = exécutant (Frontend Lead)
- ✅ Communication via `collaboration_hub.md` uniquement

---

## 📊 Statistiques

**Complexité** : ~400 lignes total
**Langages** : Bash
**Dépendances** : Aucune (natif Unix)
**Temps développement** : 2h (mode `-q`)

---

## 🔗 Liens Utiles

- **Constitution** : Frontend/1. CONSTITUTION/CONSTITUTION_AETHERFLOW.md
- **Roadmap** : docs/02-sullivan/FIGMA-Like/ROADMAP_12FEV_2026.md
- **Orchestration** : docs/02-sullivan/ORCHESTRATION_CLAUDE_KIMI.md

---

**Auteur** : Claude Sonnet 4.5
**Contact** : François-Jean Dazin (CTO)
**Dernière mise à jour** : 12 février 2026, 21:00
