#!/bin/bash
# Script pour pousser le code vers GitHub
# Usage: ./scripts/push_to_github.sh

set -e

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$PROJECT_ROOT"

echo "============================================================"
echo "Push vers GitHub: https://github.com/FJDaz/homeos"
echo "============================================================"
echo ""

# Vérifier si git est installé
if ! command -v git &> /dev/null; then
    echo "❌ Git n'est pas installé"
    exit 1
fi

# Initialiser git si nécessaire
if [ ! -d ".git" ]; then
    echo "📦 Initialisation du dépôt Git..."
    git init
fi

# Configurer le remote (mise à jour si existe déjà)
if git remote get-url origin &> /dev/null; then
    echo "🔄 Mise à jour du remote origin..."
    git remote set-url origin https://github.com/FJDaz/homeos.git
else
    echo "➕ Ajout du remote origin..."
    git remote add origin https://github.com/FJDaz/homeos.git
fi

# Vérifier la configuration Git
echo ""
echo "📋 Configuration Git:"
git config user.name || echo "⚠️  user.name non configuré"
git config user.email || echo "⚠️  user.email non configuré"
echo ""

# Ajouter les fichiers
echo "📝 Ajout des fichiers..."
git add .

# Vérifier s'il y a des changements à commiter
if git diff --staged --quiet; then
    echo "ℹ️  Aucun changement à commiter"
else
    echo "💾 Création du commit..."
    git commit -m "Initial commit: Homeos/AETHERFLOW orchestrator" || \
    git commit -m "Update: Homeos/AETHERFLOW orchestrator"
fi

# Renommer la branche en main si nécessaire
current_branch=$(git branch --show-current 2>/dev/null || echo "main")
if [ "$current_branch" != "main" ]; then
    echo "🔄 Renommage de la branche en 'main'..."
    git branch -M main
fi

# Pousser vers GitHub
echo ""
echo "🚀 Push vers GitHub..."
echo "   Si c'est la première fois, GitHub peut demander une authentification."
echo "   Utilisez un Personal Access Token comme mot de passe."
echo ""

git push -u origin main || {
    echo ""
    echo "❌ Échec du push. Causes possibles:"
    echo "   1. Authentification requise (utilisez un Personal Access Token)"
    echo "   2. Le dépôt GitHub n'est pas vide (utilisez: git pull --allow-unrelated-histories)"
    echo ""
    echo "Pour créer un token: https://github.com/settings/tokens"
    exit 1
}

echo ""
echo "✅ Code poussé avec succès vers https://github.com/FJDaz/homeos"
echo ""
