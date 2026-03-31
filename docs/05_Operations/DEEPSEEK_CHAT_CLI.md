# DeepSeek Chat CLI

**Alternative rapide et économique à Gemini** pour QA, discussions et analyses.

---

## 🚀 Lancement Rapide

### Méthode 1 : Wrapper (recommandé)
```bash
cd /Users/francois-jeandazin/AETHERFLOW
./deepseek-chat
```

### Méthode 2 : Direct Python
```bash
cd /Users/francois-jeandazin/AETHERFLOW
source venv/bin/activate
python scripts/deepseek_chat.py
```

---

## 📋 Options de Lancement

### Chat Standard
```bash
./deepseek-chat
```

### Avec Prompt Système Personnalisé
```bash
./deepseek-chat --system "Tu es un expert QA Python. Sois concis et précis."
```

### Analyser un Fichier au Démarrage
```bash
./deepseek-chat --file docs/02-sullivan/mailbox/kimi/CR_STEP5.md
```

### Utiliser DeepSeek Coder (pour code)
```bash
./deepseek-chat --model deepseek-coder
```

---

## 🎮 Commandes Interactives

Une fois le chat lancé :

| Commande | Description | Exemple |
|----------|-------------|---------|
| `/file <path>` | Charger un fichier | `/file test_results.txt` |
| `/system <text>` | Changer prompt système | `/system Tu es un expert Git` |
| `/clear` | Effacer l'historique | `/clear` |
| `/exit` | Quitter | `/exit` |

---

## 💡 Cas d'Usage

### 1. QA Rapide d'un CR
```bash
./deepseek-chat --file docs/02-sullivan/mailbox/kimi/CR_STEP5_CARREFOUR_CREATIF.md

# Dans le chat :
Toi > Est-ce que tous les critères d'acceptation sont remplis ?
```

### 2. Analyser des Tests Pytest
```bash
./deepseek-chat

Toi > /file pytest_output.txt
Toi > Quels tests échouent et pourquoi ?
```

### 3. Révision de Code
```bash
./deepseek-chat --system "Tu es un code reviewer senior Python"

Toi > /file Backend/Prod/sullivan/vision_analyzer.py
Toi > Quels sont les problèmes potentiels dans ce code ?
```

### 4. Assistance Mission
```bash
./deepseek-chat --system "Tu es KIMI, FRD Lead pour Sullivan"

Toi > /file docs/02-sullivan/mailbox/kimi/MISSION_KIMI_STEP6_UI_VISION.md
Toi > Explique-moi ce que je dois faire en 3 étapes
```

---

## ⚡ Avantages vs Gemini

| Critère | DeepSeek Chat CLI | Gemini via API |
|---------|-------------------|----------------|
| **Vitesse** | ⚡⚡⚡ Très rapide (~2s) | ⏱️ Lent (>30s) |
| **Coût** | 💰 ~$0.0003/req | 💰💰 Gratuit mais limité |
| **Contexte** | 64k tokens | 1M tokens |
| **Vision** | ❌ Non | ✅ Oui |
| **QA Code** | ✅ Excellent | ⚠️ Moyen |
| **Fiabilité** | ✅ Stable | ⚠️ Rate limits |

---

## 🎯 Quand Utiliser

**DeepSeek Chat CLI** :
- ✅ QA rapide de CR
- ✅ Analyse tests pytest
- ✅ Code review
- ✅ Assistance missions
- ✅ Discussions générales

**Gemini API** :
- ✅ Analyse PNG/images (Vision)
- ✅ Contexte énorme (>64k tokens)
- ✅ Tâches multimodales

---

## 📊 Coûts

**DeepSeek Chat** (modèle `deepseek-chat`) :
- Input : $0.27/M tokens
- Output : $1.10/M tokens

**Exemple** : Session 20 messages (~50k tokens) = **$0.04** environ

---

## 🔧 Configuration

Le chat utilise automatiquement les variables `.env` :
```bash
DEEPSEEK_API_KEY=sk-...
DEEPSEEK_API_URL=https://api.deepseek.com/v1/chat/completions
```

---

## 🐛 Dépannage

### Erreur "Module not found"
```bash
cd /Users/francois-jeandazin/AETHERFLOW
source venv/bin/activate
python scripts/deepseek_chat.py
```

### Erreur API Key
Vérifier `.env` :
```bash
cat .env | grep DEEPSEEK_API_KEY
```

### Timeout
Augmenter dans `scripts/deepseek_chat.py` ligne 41 :
```python
timeout=120  # Augmenter si nécessaire
```

---

## 📝 Exemples de Prompts Système

### Expert QA
```bash
--system "Tu es un expert QA. Analyse les tests et identifie les bugs. Sois concis."
```

### Code Reviewer
```bash
--system "Tu es un senior Python dev. Review le code avec focus sur sécurité et performance."
```

### Agent Sullivan
```bash
--system "Tu es Sullivan, l'agent frontend. Tu connais le Genome et le Parcours UX 9 étapes."
```

---

## 🚦 Status

- ✅ **Production Ready**
- ✅ Testé avec DeepSeek V3
- ✅ Historique conversation
- ✅ Chargement fichiers
- ✅ Coûts tracking

---

**Créé le** : 9 février 2026
**Par** : Sonnet (Ingénieur en Chef)
**Pour** : Pallier les défaillances de Gemini sur QA
