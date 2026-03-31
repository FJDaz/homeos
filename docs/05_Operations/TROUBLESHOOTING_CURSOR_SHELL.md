# Dépannage : erreurs shell Cursor (base64, dump_zsh_state)

## Symptômes

Lors de l’exécution de commandes AETHERFLOW depuis le **terminal intégré de Cursor**, les erreurs suivantes peuvent apparaître après chaque commande :

```
/usr/bin/base64: line 136: /dev/stdout: Operation not permitted
zsh:1: command not found: dump_zsh_state
```

**À noter** : ces messages viennent des **hooks shell de Cursor**, pas d’AETHERFLOW. Le même workflow exécuté dans un terminal externe (ex. Terminal.app) fonctionne normalement (ex. complétion en ~0,79 s, 100 % cache hits, 0,00 $).

---

## Solutions possibles

### 1. Désactiver les hooks Cursor (si disponible)

Dans Cursor : **Settings** → rechercher **"hooks"** ou **"shell"**. Si une option liée aux hooks du terminal intégré existe, la désactiver. **Note** : cette option n’est pas toujours présente (« No hooks configured ») ; dans ce cas, utiliser les solutions 2 ou 3.

### 2. Contournement dans `~/.zshrc`

Ajouter à la fin de `~/.zshrc` :

```bash
# Désactiver dump_zsh_state si non défini (contournement hooks Cursor)
type dump_zsh_state &>/dev/null || dump_zsh_state() { : }
```

Puis `source ~/.zshrc` ou rouvrir le terminal.

### 3. Utiliser un terminal externe pour AETHERFLOW (recommandé si pas de réglage hooks)

Lancer les commandes AETHERFLOW (CLI, `run_aetherflow.sh`, `run_via_api`, etc.) depuis **Terminal.app**, iTerm, ou tout terminal hors Cursor. Le workflow s’exécute correctement et le cache fonctionne comme prévu. C’est la solution la plus fiable lorsque les hooks ne sont pas désactivables.

---

## Références

- Mode serveur / `run_via_api` : voir [README](../README.md) section « Mode serveur » et [DOUBLE_CHECK_FASTAPI_INSTALLATION.md](DOUBLE_CHECK_FASTAPI_INSTALLATION.md).
