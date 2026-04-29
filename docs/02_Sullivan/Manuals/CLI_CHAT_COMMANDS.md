# Commandes CLI Sullivan Agent

**Date**: 2 février 2026  
**Version**: 1.0

---

## 🚀 Démarrage rapide

```bash
# Chat simple (message unique)
./aetherflow-chat "Ton message"

# Mode interactif (conversation continue)
./aetherflow-chat -i

# Ou avec le module Python complet
python -m Backend.Prod.cli sullivan chat "Message"
```

---

## 📋 Commandes disponibles

### `sullivan chat` - Chat avec Sullivan Agent

Chat avec l'agent conversationnel Sullivan, avec mémoire de session et outils.

#### Usage

```bash
python -m Backend.Prod.cli sullivan chat [OPTIONS] [MESSAGE]
```

#### Arguments

| Argument | Description |
|----------|-------------|
| `message` | Message à envoyer à Sullivan (optionnel si `-i`) |

#### Options

| Option | Court | Défaut | Description |
|--------|-------|--------|-------------|
| `--session` | `-s` | `None` | ID de session existante (pour reprendre) |
| `--user` | `-u` | `cli_user` | ID utilisateur |
| `--step` | - | `4` | Étape du parcours UX (1-9) |
| `--interactive` | `-i` | `False` | Mode interactif (conversation continue) |

#### Exemples

```bash
# Message simple
python -m Backend.Prod.cli sullivan chat "Bonjour"

# Mode interactif
python -m Backend.Prod.cli sullivan chat -i

# Reprendre une session
python -m Backend.Prod.cli sullivan chat "Suite" --session cli_user_20260202_143052_abc123

# Spécifier l'étape du parcours
python -m Backend.Prod.cli sullivan chat "Aide" --step 5

# Avec identifiant utilisateur
python -m Backend.Prod.cli sullivan chat "Hello" --user john_doe
```

---

## 🛠️ Alias pratiques

Créer un alias bash/zsh dans `~/.bashrc` ou `~/.zshrc` :

```bash
# Alias simple
alias sullivan='cd /path/to/AETHERFLOW && ./aetherflow-chat'

# Avec options par défaut
alias sullivan-chat='cd /path/to/AETHERFLOW && ./aetherflow-chat -i'

# Avec user personnalisé
alias sullivan-me='cd /path/to/AETHERFLOW && ./aetherflow-chat --user $USER'
```

Usage après alias :

```bash
sullivan "Bonjour"
sullivan-chat          # Mode interactif
sullivan-me "Message"  # Avec ton nom d'utilisateur
```

---

## 💬 Scénarios d'usage

### 1. Brainstorm rapide

```bash
$ ./aetherflow-chat "Je veux créer un dashboard analytics"

Sullivan: Parfait ! Pour un dashboard analytics, je suggère de commencer par 
identifier les KPIs clés. Quelles métriques souhaitez-vous afficher ?

Session: cli_user_20260202_143052_a1b2c3d4
```

### 2. Génération de composant

```bash
$ ./aetherflow-chat "Génère un bouton avec effet hover néon"

⚡ generate_component

Sullivan: Voici votre bouton néon ! J'ai utilisé un dégradé cyan-magenta 
avec un box-shadow animé au survol.
```

### 3. Mode interactif - Session de design

```bash
$ ./aetherflow-chat -i

🎭 Sullivan Agent - Mode interactif
Session: cli_user_20260202_143052_a1b2c3d4 | Étape: 4

Vous: Je veux une page de login
Sullivan: Quel style préférez-vous ? Minimal, glassmorphism, ou néon ?

Vous: Glassmorphism
Sullivan: Parfait ! Je génère le composant...
⚡ generate_component

Vous: Ajoute une ombre plus forte
Sullivan: J'affine le style...
⚡ refine_style

Vous: quit
Au revoir ! 👋
```

### 4. Reprendre une conversation

```bash
# Première session
$ ./aetherflow-chat "On parlait d'un dashboard"
Session: cli_user_20260202_143052_a1b2c3d4

# Plus tard, reprendre
$ ./aetherflow-chat "Oui je voulais ajouter un graphique" \
    --session cli_user_20260202_143052_a1b2c3d4

Sullivan: Absolument ! Pour le graphique, quel type préférez-vous ?
Line chart, bar chart, ou pie chart ?
```

---

## 🎯 Commandes complémentaires

### Liste des outils disponibles

```bash
# Via API
curl http://localhost:8000/sullivan/agent/tools

# Ou via le mode frd dialogue
python -m Backend.Prod.cli sullivan frd dialogue \
    --message "Quels outils as-tu ?"
```

### Voir une session

```bash
curl http://localhost:8000/sullivan/agent/session/{session_id}
```

### Effacer l'historique

```bash
curl -X POST http://localhost:8000/sullivan/agent/session/{session_id}/clear
```

---

## 🔧 Intégration avec d'autres commandes

### Chaîner les commandes

```bash
# Analyser une image puis discuter du résultat
python -m Backend.Prod.cli sullivan frd analyze --image design.png
./aetherflow-chat "J'ai uploadé une image. Que proposes-tu ?"

# Générer un genome puis demander conseil
python -m Backend.Prod.cli studio --genome output/studio/homeos_genome.json
./aetherflow-chat --step 4 "Analyse mon genome"
```

### Scripts automatisés

```bash
#!/bin/bash
# setup-project.sh - Créer un nouveau projet avec Sullivan

PROJECT_NAME=$1

echo "🚀 Création du projet $PROJECT_NAME avec Sullivan..."

# Chat pour définir les besoins
./aetherflow-chat "Je crée un projet: $PROJECT_NAME. C'est une app de gestion de tâches."

# Générer le genome
python -m Backend.Prod.cli studio --output "output/$PROJECT_NAME"

echo "✅ Projet créé !"
```

---

## 📊 Comparaison des modes

| Mode | Commande | Usage | Latence | Interactif |
|------|----------|-------|---------|------------|
| **Chat** | `sullivan chat` | Conversation | ~500ms | ✅ Oui |
| **FRD dialogue** | `sullivan frd dialogue` | Question rapide | ~500ms | ❌ Non |
| **FRD analyze** | `sullivan frd analyze` | Analyse image | ~3-5s | ❌ Non |
| **Designer** | `sullivan -d image.png` | Workflow complet | ~10s | ❌ Non |

---

## 🐛 Dépannage

### "Erreur de connexion"

```bash
# Vérifier que l'API est démarrée
curl http://localhost:8000/health

# Démarrer si nécessaire
./start_api.sh
```

### Session perdue

```bash
# Lister les sessions sauvegardées
ls ~/.aetherflow/sessions/

# Reprendre avec le bon ID
./aetherflow-chat --session cli_user_20260202_143052_abc123
```

### Réponse trop longue

```bash
# En mode interactif, Ctrl+C pour annuler
# Ou appuyer sur Espace pendant l'effet typewriter pour tout afficher
```

---

## 📝 Fichiers liés

- `Backend/Prod/sullivan/agent/sullivan_agent.py` - Agent principal
- `Backend/Prod/sullivan/agent/api.py` - Endpoints API
- `Backend/Prod/cli.py` - Commandes CLI
- `Frontend/sullivan-chat-widget.html` - Widget web

---

## 🎓 Tips avancés

### Historique bash

```bash
# Rechercher dans l'historique
ctrl+r
# Taper: sullivan

# Répéter la dernière commande
!!

# Modifier la dernière commande
^ancien^nouveau
```

### Redirection

```bash
# Sauvegarder la session dans un fichier
./aetherflow-chat "Crée une todo list" 2>&1 | tee sullivan-session.log

# Utiliser la sortie dans un script
RESPONSE=$(./aetherflow-chat "Génère un titre" 2>/dev/null)
echo "Titre: $RESPONSE"
```

---

**Prochains pas**:
- Essayer `./aetherflow-chat -i` pour une conversation
- Explorer les 6 outils disponibles
- Intégrer à ton workflow de développement
