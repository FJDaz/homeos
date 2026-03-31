# Instructions pour pousser le code vers GitHub

## État actuel

✅ Dépôt GitHub créé : https://github.com/FJDaz/homeos  
⏳ Command Line Tools en cours d'installation  
📝 README mis à jour avec le nom "Homeos"  

## Une fois les Command Line Tools installés

### 1. Vérifier que git fonctionne

```bash
git --version
```

Vous devriez voir : `git version 2.x.x`

### 2. Pousser le code (méthode rapide)

```bash
cd /Users/francois-jeandazin/AETHERFLOW
./scripts/push_to_github.sh
```

### 3. Ou manuellement

```bash
cd /Users/francois-jeandazin/AETHERFLOW

# Initialiser git
git init

# Configurer votre identité
git config user.name "FJDaz"
git config user.email "votre.email@example.com"

# Ajouter tous les fichiers
git add .

# Premier commit
git commit -m "Initial commit: Homeos/AETHERFLOW orchestrator"

# Connecter au dépôt GitHub
git remote add origin https://github.com/FJDaz/homeos.git

# Pousser vers GitHub
git push -u origin main
```

## Authentification GitHub

Si GitHub demande une authentification lors du `git push` :

1. **Créer un Personal Access Token** :
   - Allez sur https://github.com/settings/tokens
   - Cliquez sur "Generate new token" → "Generate new token (classic)"
   - Donnez-lui un nom (ex: "Homeos Local")
   - Cochez la permission `repo`
   - Cliquez sur "Generate token"
   - **Copiez le token** (vous ne pourrez plus le voir après)

2. **Utiliser le token lors du push** :
   - Username : `FJDaz`
   - Password : **collez le token** (pas votre mot de passe GitHub)

## Fichiers protégés

Le `.gitignore` protège automatiquement :
- Fichiers de cache et logs
- Fichiers d'environnement (`.env`)
- Fichiers générés (`.generated.py`)
- Outputs d'exécution

## Protection contre l'écrasement

Le système a été modifié pour que le refactoring :
- Ne remplace **PAS** les fichiers existants
- Sauvegarde dans un fichier `.generated` pour révision manuelle
- Crée uniquement les nouveaux fichiers

Cela évite d'écraser des fichiers comme `agent_router.py`.
