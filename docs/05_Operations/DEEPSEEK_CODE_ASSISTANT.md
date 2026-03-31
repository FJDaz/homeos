# DeepSeek Code Assistant

**Chat CLI avec accès codebase** - Explorer et analyser le code avec IA

---

## 🚀 Lancement

### Méthode Rapide
```bash
cd /Users/francois-jeandazin/AETHERFLOW
./deepseek-code
```

### Méthode Python
```bash
source venv/bin/activate
python scripts/deepseek_code_assistant.py
```

---

## 🎮 Commandes Chat

| Commande | Description | Exemple |
|----------|-------------|---------|
| `/clear` | Effacer l'historique | `/clear` |
| `/system <text>` | Changer prompt système | `/system Tu es un expert Python` |
| `/exit` | Quitter | `/exit` |

---

## 🔧 Outils Codebase

### 1. `/read <file>` - Lire un fichier

```bash
Toi > /read Backend/Prod/sullivan/agent/api.py
```

**Résultat** :
```
📄 api.py
```python
# Contenu du fichier...
```
```

---

### 2. `/grep <pattern> [path]` - Chercher dans les fichiers

```bash
Toi > /grep "sullivan.*chat" Backend
```

**Résultat** :
```
🔍 Résultats :
Backend/Prod/cli.py:1759:    if args.command == "sullivan" and ...
Backend/Prod/sullivan/agent/api.py:5:- POST /sullivan/agent/chat
...
```

**Options** :
- Pattern : regex compatible grep
- Path : répertoire à chercher (défaut : projet entier)
- Case-insensitive par défaut

---

### 3. `/glob <pattern>` - Trouver fichiers par pattern

```bash
Toi > /glob Backend/Prod/sullivan/**/*.py
```

**Résultat** :
```
📁 Fichiers trouvés (24) :
  - Backend/Prod/sullivan/agent/api.py
  - Backend/Prod/sullivan/chatbot/sullivan_chatbot.py
  - Backend/Prod/sullivan/builder/corps1_chatbot_page.py
  ...
```

**Patterns** :
- `*.py` - Tous les fichiers Python
- `**/*.js` - Tous les JS récursivement
- `Frontend/**/*.html` - Tous les HTML dans Frontend

---

### 4. `/tree [path]` - Afficher arborescence

```bash
Toi > /tree Backend/Prod/sullivan
```

**Résultat** :
```
🌳 Arborescence :
Backend/Prod/sullivan
├── agent
│   ├── api.py
│   └── __init__.py
├── chatbot
│   ├── sullivan_chatbot.py
│   └── __init__.py
└── builder
    └── corps1_chatbot_page.py
```

**Options** :
- Path : répertoire à explorer (défaut : projet root)
- Max depth : 3 niveaux (modifiable)

---

## 💡 Cas d'Usage

### 1. Explorer une nouvelle feature

```bash
./deepseek-code

Toi > /grep "Sullivan.*Agent" Backend
Toi > Explique-moi comment fonctionne Sullivan Agent
DeepSeek > [Analyse basée sur les fichiers trouvés]

Toi > /read Backend/Prod/sullivan/agent/api.py
Toi > Quelles sont les routes exposées ?
DeepSeek > [Détaille les routes /chat et /chat/stream]
```

---

### 2. Analyser une implémentation

```bash
./deepseek-code --system "Tu es un expert en architecture Python"

Toi > /tree Backend/Prod/sullivan
Toi > Quelle est la structure de ce module ?
DeepSeek > [Analyse l'arborescence]

Toi > /read Backend/Prod/sullivan/agent/__init__.py
Toi > Quelles sont les dépendances ?
```

---

### 3. Rechercher références

```bash
./deepseek-code

Toi > /grep "sullivan.*chat" .
Toi > Liste toutes les implémentations de Sullivan Chat
DeepSeek > [Identifie les 3 systèmes]

Toi > /read Backend/Prod/sullivan/builder/corps1_chatbot_page.py
Toi > Est-ce que ce fichier est obsolète ?
DeepSeek > Oui, car il utilise /sullivan/chatbot alors que la route moderne est /sullivan/agent/chat
```

---

### 4. Code Review

```bash
./deepseek-code --system "Tu es un senior Python dev. Focus sur sécurité et performance."

Toi > /read Backend/Prod/sullivan/vision_analyzer.py
Toi > Quels sont les problèmes potentiels ?
DeepSeek >
1. Pas de validation format PNG
2. Gestion erreur API incomplète
3. Parsing JSON non sécurisé
```

---

## 🔍 Workflow Type

### Analyse "Sullivan Chat"

**Étapes** :
1. Chercher toutes les références
2. Lire les fichiers clés
3. Analyser l'architecture
4. Identifier problèmes/redondances

**Session complète** :
```bash
./deepseek-code

# 1. Recherche globale
Toi > /grep "sullivan.*chat" Backend

# 2. Lecture fichiers clés
Toi > /read Backend/Prod/sullivan/agent/api.py
Toi > /read Backend/Prod/sullivan/builder/corps1_chatbot_page.py

# 3. Analyse
Toi > Compare ces deux implémentations. Y a-t-il des conflits ?

DeepSeek > Oui, conflit de routes :
- /sullivan/agent/chat (moderne, production)
- /sullivan/chatbot (legacy, obsolète)
Recommandation : Supprimer l'ancienne route.

# 4. Rapport
Toi > Génère un rapport sur les implémentations Sullivan Chat
DeepSeek > [Génère analyse complète]
```

---

## ⚙️ Configuration Avancée

### Prompt Système Personnalisé

```bash
./deepseek-code --system "Tu es un expert en architecture logicielle. Analyse le code avec focus sur :
1. Patterns de design
2. Couplage/cohésion
3. Testabilité
4. Performance"
```

### Modèle DeepSeek Coder

Pour analyse de code complexe :
```bash
./deepseek-code --model deepseek-coder
```

**Différences** :
- `deepseek-chat` : Discussions générales, QA
- `deepseek-coder` : Code review, refactoring

---

## 🎯 Comparaison avec Chat Standard

| Fonctionnalité | DeepSeek Chat CLI | DeepSeek Code Assistant |
|----------------|-------------------|-------------------------|
| **Historique** | ✅ | ✅ |
| **Fichiers** | `/file` (lecture simple) | `/read` (avec contexte) |
| **Recherche** | ❌ | `/grep` (codebase) |
| **Exploration** | ❌ | `/glob`, `/tree` |
| **Analyse code** | Limitée | ✅ Complète |

**Quand utiliser** :
- **Chat CLI** : QA rapide, discussions
- **Code Assistant** : Exploration codebase, analyse architecture

---

## 📊 Exemples Réels

### Exemple 1 : Audit Sullivan Chat

**Objectif** : Identifier toutes les implémentations

**Commandes** :
```bash
./deepseek-code

Toi > /grep "sullivan.*chat" Backend
# Résultat : 13 occurrences

Toi > /grep "sullivan.*chat" Frontend
# Résultat : 8 occurrences

Toi > /read Backend/Prod/sullivan/agent/api.py
Toi > /read Backend/Prod/sullivan/builder/corps1_chatbot_page.py

Toi > Analyse ces implémentations et identifie les redondances
```

**Résultat** :
- 3 systèmes identifiés
- 1 obsolète (Corps1)
- Recommandation de nettoyage

---

### Exemple 2 : Recherche Genome

```bash
./deepseek-code

Toi > /grep "genome" Backend/Prod/sullivan
Toi > /glob Backend/Prod/sullivan/**/genome*.py
Toi > /tree Backend/Prod/sullivan/genome
```

---

### Exemple 3 : Analyse Routes API

```bash
./deepseek-code --system "Tu es un expert FastAPI"

Toi > /grep "@router\." Backend/Prod/sullivan
Toi > Liste toutes les routes API de Sullivan
DeepSeek > [Extrait et liste toutes les routes]

Toi > Y a-t-il des conflits de routes ?
```

---

## 🛠️ Dépannage

### Timeout sur /grep

**Problème** : Recherche trop large (>10s)

**Solution** :
```bash
# Au lieu de :
/grep "pattern" .

# Utiliser :
/grep "pattern" Backend/Prod
/grep "pattern" Frontend
```

### Tree non installé

**Message** : Arborescence manuelle utilisée

**Solution** (optionnel) :
```bash
# macOS
brew install tree

# Ubuntu
sudo apt-get install tree
```

### Fichier introuvable

**Problème** : Path relatif incorrect

**Solution** :
```bash
# Utiliser path depuis racine projet
/read Backend/Prod/sullivan/agent/api.py

# Pas :
/read sullivan/agent/api.py
```

---

## 💰 Coûts

**Même tarification que Chat CLI** :
- Input : $0.27/M tokens
- Output : $1.10/M tokens

**Session type** (30min exploration) :
- Tokens : ~20k (lecture fichiers + analyse)
- Coût : **~$0.01**

---

## 🔧 Personnalisation

### Modifier Timeout Grep

**Fichier** : `scripts/deepseek_code_assistant.py`

```python
# Ligne ~58 (dans grep method)
result = subprocess.run(
    cmd,
    capture_output=True,
    text=True,
    timeout=10  # ← Augmenter ici
)
```

### Ajouter Nouveaux Outils

```python
class CodebaseTools:
    def custom_tool(self, args: str) -> str:
        """Votre outil personnalisé"""
        # Implémentation
        return result
```

Puis ajouter dans `execute_tool()` :
```python
elif tool_name == "custom":
    return self.tools.custom_tool(args)
```

---

## 📝 Logs et Historique

**Historique conversation** : En mémoire (perdu à la fermeture)

**Pour sauvegarder** :
```bash
./deepseek-code > session.log 2>&1
```

---

## 🚦 Status

- ✅ **Production Ready**
- ✅ Testé avec codebase AETHERFLOW
- ✅ 4 outils intégrés (read, grep, glob, tree)
- ✅ Timeout gérés
- ✅ Fallbacks manuels

---

## 📚 Voir Aussi

- [DEEPSEEK_CHAT_CLI.md](DEEPSEEK_CHAT_CLI.md) - Chat CLI standard
- [ANALYSE_SULLIVAN_CHAT_IMPLEMENTATIONS.md](../02-sullivan/ANALYSE_SULLIVAN_CHAT_IMPLEMENTATIONS.md) - Exemple analyse

---

**Créé le** : 9 février 2026
**Par** : Sonnet (Ingénieur en Chef)
**Version** : 1.0
