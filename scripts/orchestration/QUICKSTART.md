# Orchestration Claude-KIMI — Démarrage Rapide

**Pour** : François-Jean Dazin (CTO)
**Date** : 12 février 2026

---

## 🎯 En 3 Minutes

### 1. Tester le système (simulation)

```bash
cd /Users/francois-jeandazin/AETHERFLOW
./scripts/orchestration/test_workflow.sh
```

**Résultat attendu** :
- Mission écrite dans `collaboration_hub.md` ✅
- Signal `@CLAUDE_VALIDATE` détecté ✅
- Notification macOS affichée ✅

---

### 2. Usage Réel (Claude → KIMI)

#### Quand Claude termine une ÉTAPE Backend

```bash
# Claude exécute (via Bash tool)
./scripts/orchestration/trigger_kimi.sh \
  docs/02-sullivan/mailbox/kimi/NOM_MISSION.md \
  ETAPE_X

# Lance surveillance
./scripts/orchestration/watch_kimi.sh &
```

#### Quand KIMI termine

```
🔔 Notification macOS apparaît
Terminal affiche CR KIMI

🤖 Relancer Claude Code automatiquement ? (y/n)
```

**Choix** :
- `y` → Claude redémarre automatiquement
- `n` → Tu ouvres Claude manuellement

#### Validation

1. Ouvre l'URL fournie (ex: http://localhost:9998/stenciler)
2. Valide visuellement
3. Dis à Claude : "GO ÉTAPE suivante" OU "KO, corriger X"

---

## 📋 Commandes Essentielles

```bash
# Déclencher KIMI
./scripts/orchestration/trigger_kimi.sh <fichier_mission> <etape>

# Surveiller KIMI
./scripts/orchestration/watch_kimi.sh

# Tester système
./scripts/orchestration/test_workflow.sh

# Arrêter surveillance
pkill -f watch_kimi.sh
```

---

## 📄 Fichiers Importants

```
collaboration_hub.md                    → Hub partagé Claude/KIMI
scripts/orchestration/trigger_kimi.sh   → Déclenche KIMI
scripts/orchestration/watch_kimi.sh     → Surveille KIMI
scripts/orchestration/README.md         → Doc complète
docs/02-sullivan/ORCHESTRATION_CLAUDE_KIMI.md → Récapitulatif
```

---

## ❓ FAQ

### Le watcher ne détecte pas KIMI

```bash
# Vérifier signal présent
grep "@CLAUDE_VALIDATE" /Users/francois-jeandazin/collaboration_hub.md

# Relancer watcher
./scripts/orchestration/watch_kimi.sh
```

### Notification macOS ne s'affiche pas

```bash
# Tester notification
osascript -e 'display notification "Test" with title "Test"'

# Si erreur → Vérifier permissions :
# Préférences Système > Notifications > Terminal → Autoriser
```

### Configurer API KIMI

```bash
# Dans ~/.bashrc ou ~/.zshrc
export KIMI_API_KEY="your_key"
export KIMI_API_URL="https://api.moonshot.cn/v1/chat/completions"
```

---

## ✅ C'est Tout !

**Le système est opérationnel.**

Pour plus de détails, voir :
- [README.md](README.md) — Documentation complète
- [EXAMPLE_USAGE.md](EXAMPLE_USAGE.md) — Exemple détaillé
- [ORCHESTRATION_CLAUDE_KIMI.md](../../docs/02-sullivan/ORCHESTRATION_CLAUDE_KIMI.md) — Récapitulatif

---

**Questions ?** → Demande à Claude ! 🤖
