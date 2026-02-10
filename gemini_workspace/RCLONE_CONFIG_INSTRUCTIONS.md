# Instructions : Configuration de Rclone pour Google Drive

Pour que je puisse téléverser la documentation de votre projet sur votre Google Drive via `rclone`, vous devez d'abord installer et configurer `rclone` sur votre système. `rclone` est un outil en ligne de commande qui simplifie la gestion des services de stockage cloud.

**⚠️ Attention :** La configuration de `rclone` est un processus interactif que **vous devrez effectuer manuellement** dans votre terminal. Je ne peux pas le faire à votre place.

---

## Étape 1 : Installation de Rclone

Ouvrez votre terminal et suivez les instructions correspondant à votre système d'exploitation :

### macOS (via Homebrew - Recommandé)
```bash
brew install rclone
```

### Linux (Debian/Ubuntu)
```bash
sudo apt update
sudo apt install rclone
```

### Linux (Fedora/RHEL)
```bash
sudo dnf install rclone
```

### Autres systèmes d'exploitation ou installation manuelle
Consultez la documentation officielle de `rclone` pour les instructions d'installation : [https://rclone.org/install/](https://rclone.org/install/)

---

## Étape 2 : Configuration de Rclone pour Google Drive

Une fois `rclone` installé, vous devez le configurer pour qu'il puisse accéder à votre Google Drive.

1.  Dans votre terminal, exécutez la commande suivante :
    ```bash
    rclone config
    ```

2.  Le programme vous posera plusieurs questions. Suivez ces étapes :
    *   `n)` pour "New remote".
    *   Entrez un **nom** pour votre "remote" (par exemple : `gdrive_aetherflow` ou tout autre nom facile à retenir).
    *   Choisissez le type de stockage. Pour Google Drive, tapez `drive` et appuyez sur Entrée. (Il vous proposera une liste numérotée, cherchez "Google Drive").
    *   Laissez les champs `client_id` et `client_secret` vides (appuyez sur Entrée deux fois). `rclone` utilisera ses propres identifiants par défaut, ce qui est généralement suffisant.
    *   Pour `scope`, choisissez le niveau d'accès. `1)` "Full access all files" est souvent nécessaire pour téléverser.
    *   Laissez les autres options par défaut jusqu'à ce qu'il demande `Auto config?`. Entrez `y)` (pour "yes").
    *   Votre navigateur web s'ouvrira et vous demandera de vous connecter à votre compte Google et d'autoriser `rclone` à accéder à votre Google Drive. **Ceci est une étape cruciale :** suivez les instructions à l'écran dans votre navigateur pour accorder l'autorisation.
    *   Une fois l'autorisation accordée, le navigateur affichera un code de succès. Retournez à votre terminal.
    *   Il vous demandera `Configure this as a team drive?`. Entrez `n)` (pour "no"), sauf si vous souhaitez spécifiquement utiliser un Drive partagé.
    *   Entrez `y)` pour confirmer la configuration.
    *   Entrez `q)` pour quitter la configuration.

---

## Étape 3 : Vérification de la Configuration

Pour vérifier que `rclone` est correctement configuré et peut voir votre Drive, exécutez la commande suivante en remplaçant `gdrive_aetherflow` par le nom que vous avez donné à votre remote :

```bash
rclone lsd gdrive_aetherflow:
```
Cette commande devrait lister les dossiers de niveau supérieur de votre Google Drive.

---

## Étape 4 : Téléversement de la Documentation (par Gemini)

Une fois que vous avez installé et configuré `rclone` (et vérifié son fonctionnement avec l'Étape 3), veuillez me le confirmer.

Je vous fournirai alors la commande `rclone` exacte pour téléverser les fichiers de documentation de votre projet (les fichiers `.md` du répertoire `docs/` et le `README.md` principal) vers le dossier Google Drive que vous avez indiqué (`1VMVnqTptqYDHc2v-PFuGIjNpwAtA4eqR`).
