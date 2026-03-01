# Guide d'Utilisation AetherFlow sur Google IDX

Bienvenue dans l'environnement AetherFlow pour Google IDX. Cet environnement est configuré pour vous permettre de tester et développer avec AetherFlow rapidement.

## 1. Configuration initiale

Avant de commencer, vous devez configurer vos clés API :

1.  Dans le terminal, copiez le fichier d'exemple :
    ```bash
    cp .env.example .env
    ```
2.  Ouvrez le fichier `.env` et ajoutez vos clés (DeepSeek, Gemini, etc.).
    *Note: Google IDX vous permet d'utiliser votre clé Gemini facilement.*

## 2. Installation des dépendances

L'environnement IDX pré-installe Python, mais vous devez installer les bibliothèques spécifiques au projet :

```bash
# Créer et activer l'environnement virtuel (si pas déjà fait par IDX)
python -m venv venv
source venv/bin/activate

# Installer les dépendances
pip install -r requirements.txt

# Installer les navigateurs pour Sullivan (Visual Auditor)
playwright install chromium
```

## 3. Lancer l'API AetherFlow

Pour démarrer le serveur API :

```bash
./start_api.sh
```

L'API sera accessible sur le port 8000. Google IDX devrait vous proposer une notification pour ouvrir le port ou afficher une prévisualisation.

## 4. Utilisation des Modes AetherFlow

Vous pouvez utiliser les scripts wrappers pour lancer des tâches :

*   **Mode Proto (Rapide)** : `./aetherflow-chat "Votre demande"`
*   **Mode Hybride** : `./aetherflow-hybrid "Votre demande"`
*   **Mode Monitor** : `./aetherflow-monitor`

## 5. Audit de la fonction "Apply"

Un audit des problèmes connus de la fonction "Apply" (application automatique du code) est disponible dans le fichier `AETHERFLOW_APPLY_AUDIT.md`. Consultez-le si vous remarquez que le code n'est pas mis à jour comme prévu.
