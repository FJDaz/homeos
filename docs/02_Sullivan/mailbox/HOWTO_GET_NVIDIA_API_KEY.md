# Comment Obtenir une Clé NVIDIA API (Gratuite)

**Date** : 9 février 2026
**Objectif** : Utiliser KIMI K2.5 via NVIDIA NIM (gratuit)

---

## 🎯 Pourquoi NVIDIA NIM ?

NVIDIA offre un accès **gratuit** au modèle **moonshotai/kimi-k2.5** via leur plateforme NIM.

**Avantages** :
- ✅ **Gratuit** (quotas généreux)
- ✅ **KIMI K2.5** (le meilleur pour frontend)
- ✅ **16k tokens** max par requête
- ✅ **Pas de limite stricte** (fair use)

---

## 📋 Étapes pour Obtenir la Clé

### 1. Aller sur NVIDIA Build

**URL** : https://build.nvidia.com/

### 2. Se Connecter

- Cliquer sur "Sign In" en haut à droite
- Utiliser compte NVIDIA (ou créer gratuitement)

### 3. Explorer les Modèles

- Chercher "**KIMI**" dans la barre de recherche
- Ou aller directement sur : https://build.nvidia.com/moonshotai/kimi-k2-5

### 4. Obtenir la Clé API

- Cliquer sur "**Get API Key**"
- Copier la clé (format : `nvapi-xxxxxx...`)

### 5. Ajouter dans `.env`

```bash
NVIDIA_API_KEY=nvapi-ta_clé_ici
```

---

## ✅ Tester l'Intégration

Une fois la clé ajoutée dans `.env`, tester :

```bash
python -m Backend.Prod.cli --hybrid "Create simple button component"
```

**Résultat attendu** :
```
→ Envoi requête à NVIDIA NIM (KIMI K2.5)...
→ CR créé : CR_xxxxx.md
✓ Phase 1 : Code généré par KIMI
```

---

## 🔧 Configuration dans AetherFlow

Le système est déjà configuré pour utiliser NVIDIA NIM :

**Endpoint** : `https://integrate.api.nvidia.com/v1/chat/completions`
**Modèle** : `moonshotai/kimi-k2.5`
**Max tokens** : 16384
**Fichier** : `Backend/Prod/sullivan/modes/hybrid_frd_mode.py:271`

---

## 💰 Quotas Gratuits

NVIDIA offre des quotas généreux :

| Ressource | Quota |
|-----------|-------|
| Requêtes/jour | ~1000 |
| Tokens/requête | 16384 max |
| Modèles | Tous NIM gratuits |

**Note** : Fair use policy, pas de limite stricte documentée.

---

## 🚀 Alternative : Moonshot Direct (Payant)

Si tu préfères utiliser Moonshot directement (payant) :

1. Aller sur https://platform.moonshot.cn/
2. Créer compte et obtenir API key
3. Mettre dans `.env` :
   ```bash
   KIMI_KEY=sk-ta_clé_moonshot
   ```
4. Changer l'endpoint dans le code vers Moonshot

**Coût Moonshot** : ~$0.002 par 1k tokens (raisonnable)

---

**Créé par** : Sonnet (Ingénieur en Chef)
**Pour** : Configuration KIMI dans Hybrid FRD Mode
