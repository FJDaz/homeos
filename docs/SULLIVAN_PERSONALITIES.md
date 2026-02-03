# Sullivan Personalities 🎭

Système de personnalités multiples pour Sullivan. Tu peux avoir un Sullivan pro pour tes users, et un Sullivan déjanté pour toi.

## 🚀 Usage rapide

### Pour les users (par défaut)
```bash
# Rien à faire, c'est le défaut
./start_api.sh
```

### Pour toi (drôle d'oiseau edition)
```bash
# Option 1: Variable d'env
export SULLIVAN_PERSONALITY=weirdo
./start_api.sh

# Option 2: Fichier config (persistant)
echo '{"personality": "weirdo"}' > ~/.aetherflow/config.json
./start_api.sh
```

## 📁 Structure

```
Backend/Prod/sullivan/agent/personalities/
├── __init__.py              # Loader + registre
├── base.py                  # Classe abstraite
├── sullivan_default.py      # Version pro (users)
└── sullivan_weirdo.py       # Version perso (TOI)
```

## 🎨 Customiser ta personnalité

### 1. Ouvre le fichier template
```bash
# C'est celui-là à modifier
open Backend/Prod/sullivan/agent/personalities/sullivan_weirdo.py
```

### 2. Ce que tu peux changer

#### Identity (lignes ~30-40)
```python
NAME = "Sully"              # Ton nom pour Sullivan
ROLE = "Ton acolyte"       # Sa description
AVATAR = "🦆"              # Son emoji
```

#### Traits (lignes ~42-52)
```python
TRAITS = {
    "sarcasme": 9,         # 1-10 niveau de piquant
    "absurde": 7,          # 1-10 niveau de délire
    "formel": 1,           # 1 = pote, 10 = costard
    # ...
}
```

#### Le prompt système (méthode `get_system_prompt`)
C'est là que tu définis son style de réponse, ses références, son humour.

#### Les messages de bienvenue (méthode `get_welcome_message`)
Personnalise les messages pour chaque étape du parcours.

### 3. Les commentaires `EDITME`

Le fichier est rempli de commentaires `# EDITME` pour te guider :
- `# EDITME: Mets ton style ici`
- `# EDITME: Tes références`
- `# EDITME: Ton humour`

## 🧪 Tester ta personnalité

```bash
# 1. Active ta personnalité
export SULLIVAN_PERSONALITY=weirdo

# 2. Démarre l'API
./start_api.sh

# 3. Test via le widget ou CLI
./aetherflow-chat -i
```

## ➕ Créer une nouvelle personnalité

1. Copie `sullivan_weirdo.py` → `sullivan_machin.py`
2. Renomme la classe `SullivanMachin`
3. Customise le contenu
4. Ajoute au registre dans `__init__.py`:

```python
from .sullivan_machin import SullivanMachin

PERSONALITIES = {
    "default": SullivanDefault,
    "weirdo": SullivanWeirdo,
    "machin": SullivanMachin,  # ← Ta nouvelle
}
```

5. Utilise-la:
```bash
export SULLIVAN_PERSONALITY=machin
```

## 🔧 Configuration

### Ordre de priorité
1. Variable d'env `SULLIVAN_PERSONALITY`
2. Fichier `~/.aetherflow/config.json`
3. Défaut: `"default"`

### Vérifier la config active
```python
from Backend.Prod.sullivan.agent.personalities import get_personality_name, list_personalities

print(f"Active: {get_personality_name()}")
print(f"Disponibles: {list_personalities()}")
```

## 💡 Exemples de styles

| Style | Traits clés | Usage |
|-------|-------------|-------|
| **default** | Pro, pédagogique, concis | Production, users |
| **weirdo** | Sarcasme, absurde, honnête | Développement, toi |
| **formal** | Sérieux, complet, courtois | Clients enterprise |
| **coach** | Encouragements, méthodique | Users débutants |

---

**Note:** Le fichier `sullivan_weirdo.py` est un TEMPLATE. Change tout ce qui est marqué `EDITME` avec TON style, TES références, TON humour. C'est fait pour être personnalisé ! 🎨
