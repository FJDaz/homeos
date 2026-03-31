# Configuration du dépôt GitHub pour Homeos/AETHERFLOW

## Dépôt GitHub créé
✅ **Dépôt** : https://github.com/FJDaz/homeos

## Étapes pour connecter le dépôt local

### 1. Installer/Mettre à jour les Command Line Tools (si nécessaire)

Si vous avez l'erreur `xcrun: error: invalid active developer path`, exécutez :

```bash
xcode-select --install
```

Puis redémarrez votre terminal.

### 2. Initialiser Git et connecter au dépôt GitHub

```bash
cd /Users/francois-jeandazin/AETHERFLOW

# Initialiser git (si pas déjà fait)
git init

# Configurer votre identité Git
git config user.name "FJDaz"
git config user.email "votre.email@example.com"  # Remplacez par votre email GitHub

# Ajouter tous les fichiers (sauf ceux dans .gitignore)
git add .

# Premier commit
git commit -m "Initial commit: Homeos/AETHERFLOW orchestrator"

# Ajouter le remote GitHub
git remote add origin https://github.com/FJDaz/homeos.git

# Vérifier que le remote est bien configuré
git remote -v

# Renommer la branche en main (si nécessaire)
git branch -M main

# Pousser vers GitHub
git push -u origin main
```

### 3. Si vous avez besoin d'authentification

Si GitHub demande une authentification, vous pouvez :

**Option A : Utiliser un Personal Access Token**
1. Allez sur https://github.com/settings/tokens
2. Créez un nouveau token avec les permissions `repo`
3. Utilisez le token comme mot de passe lors du push

**Option B : Utiliser SSH (recommandé)**
```bash
# Générer une clé SSH (si vous n'en avez pas)
ssh-keygen -t ed25519 -C "votre.email@example.com"

# Ajouter la clé à ssh-agent
eval "$(ssh-agent -s)"
ssh-add ~/.ssh/id_ed25519

# Copier la clé publique
cat ~/.ssh/id_ed25519.pub

# Ajouter cette clé sur GitHub : https://github.com/settings/keys

# Changer le remote en SSH
git remote set-url origin git@github.com:FJDaz/homeos.git

# Pousser
git push -u origin main
```

## Fichiers protégés

Le fichier `.gitignore` protège automatiquement :
- Fichiers de cache (`cache/`, `__pycache__/`)
- Logs (`logs/`)
- Outputs (`output/`)
- Fichiers d'environnement (`.env`)
- Fichiers temporaires

## Protection contre l'écrasement

Le fichier `Backend/Prod/claude_helper.py` a été modifié pour que le refactoring :
- **Ne remplace PAS** les fichiers existants
- Sauvegarde dans un fichier `.generated` pour révision manuelle
- Crée uniquement les nouveaux fichiers

## Commandes utiles

```bash
# Voir l'état du dépôt
git status

# Voir les fichiers modifiés
git diff

# Ajouter un fichier spécifique
git add chemin/vers/fichier

# Commit avec message
git commit -m "Description des changements"

# Pousser vers GitHub
git push

# Récupérer les changements depuis GitHub
git pull
```
