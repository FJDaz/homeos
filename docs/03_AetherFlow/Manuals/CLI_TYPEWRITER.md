# Effet Machine à Écrire - CLI

L'effet machine à écrire est aussi disponible dans le terminal !

## 🚀 Activation

Par défaut, le CLI affiche les réponses instantanément. Pour activer l'effet :

```bash
# Option 1: Variable d'env (pour cette session)
export SULLIVAN_TYPEWRITER=1
./aetherflow-chat -i

# Option 2: Une seule commande
SULLIVAN_TYPEWRITER=1 ./aetherflow-chat "Bonjour Sullivan"
```

## ⌨️ Contrôles

| Touche | Action |
|--------|--------|
| `Espace` | Skip l'effet (affiche tout instantanément) |
| `Entrée` | Skip l'effet |
| `Ctrl+C` | Skip l'effet |

## ⚙️ Configuration

Le comportement est configuré dans `Backend/Prod/cli.py` :

```python
class TypewriterConfig:
    ENABLED = False              # Désactivé par défaut
    BASE_SPEED = 0.015           # 15ms/caractère
    MIN_SPEED = 0.005            # 5ms min pour textes longs
    MAX_DURATION = 8.0           # Max 8 secondes
    PAUSE_CHARS = ".!?;,"        # Pause sur ponctuation
    PAUSE_DURATION = 0.08        # 80ms de pause
```

## 🎯 Comportement

- **Textes courts (< 200 car)** : Vitesse normale (15ms/char)
- **Textes moyens (200-500 char)** : Accélération progressive
- **Textes longs (> 500 char)** : Vitesse max (5ms/char)
- **Limite de sécurité** : Jamais plus de 8 secondes total

## 💡 Astuces

### Activer par défaut
Ajoute à ton `~/.bashrc` ou `~/.zshrc` :
```bash
export SULLIVAN_TYPEWRITER=1
```

### Désactiver temporairement
```bash
# Si activé par défaut
unset SULLIVAN_TYPEWRITER
./aetherflow-chat "message"
```

### Comparer les deux modes
```bash
# Sans effet
./aetherflow-chat "Explique-moi le Design Genome"

# Avec effet
SULLIVAN_TYPEWRITER=1 ./aetherflow-chat "Explique-moi le Design Genome"
```

## 🖥️ Compatibilité

| OS | Skip interactif | Notes |
|----|-----------------|-------|
| macOS/Linux | ✅ Oui | Terminal standard |
| Windows | ❌ Non | Fonctionne mais sans skip |

## 🎭 Différence avec le Frontend

| Fonctionnalité | Frontend (Web) | CLI (Terminal) |
|----------------|----------------|----------------|
| Actif par défaut | ✅ Oui | ❌ Non |
| Vitesse | 15ms/char | 15ms/char |
| Skip | Click/Espace/Entrée | Espace/Entrée |
| Pause ponctuation | ✅ Oui | ✅ Oui |
| Adaptatif (longs textes) | ✅ Oui | ✅ Oui |

---

**Note:** Le typewriter est désactivé par défaut en CLI car certains users préfèrent la vitesse brute en terminal. Active-le avec `SULLIVAN_TYPEWRITER=1` quand tu veux l'effet ! 🎬
