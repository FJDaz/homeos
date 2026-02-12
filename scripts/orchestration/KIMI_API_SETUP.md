# Configuration API KIMI (Moonshot AI)

**Objectif** : Obtenir une clé API pour appeler KIMI via l'orchestration.

---

## 📋 Informations API

**Provider** : Moonshot AI (开发者平台)
**Site** : https://platform.moonshot.cn
**Modèle** : `moonshot-v1-8k` (8K tokens context)
**API Endpoint** : `https://api.moonshot.cn/v1/chat/completions`

---

## 🔑 Obtenir une Clé API

### Étape 1 : Créer un compte

1. Aller sur https://platform.moonshot.cn
2. Cliquer sur "注册" (S'inscrire) ou "登录" (Se connecter)
3. S'inscrire avec :
   - Email
   - Numéro téléphone (possiblement requis pour CN)
   - Ou connexion via compte tiers

### Étape 2 : Accéder aux clés API

1. Une fois connecté, aller dans "API Keys" ou "密钥管理"
2. Cliquer sur "创建新的 Secret Key" (Créer nouvelle clé)
3. Copier la clé (format : `sk-...`)
4. **IMPORTANT** : Sauvegarder immédiatement, elle ne sera plus affichée

### Étape 3 : Configurer localement

```bash
# Dans ~/.bashrc ou ~/.zshrc
export KIMI_API_KEY="sk-votre_cle_ici"

# Recharger
source ~/.bashrc  # ou source ~/.zshrc
```

---

## 🧪 Tester la Clé

```bash
# Test simple
cd /Users/francois-jeandazin/AETHERFLOW
./scripts/orchestration/test_kimi_api.sh
```

**Résultat attendu** :
```
✅ API KIMI fonctionnelle !
📝 Réponse KIMI : TEST OK ...
📊 Tokens utilisés : ~50
```

---

## 💰 Tarification (à vérifier)

**Moonshot AI** propose généralement :
- ✅ Crédit gratuit initial (ex: 15 RMB)
- 💰 Tarif payant ensuite (ex: 0.012 RMB / 1K tokens)

**Équivalence** :
- 1 RMB ≈ 0.14 USD ≈ 0.13 EUR
- 15 RMB ≈ 2 USD (crédit gratuit)

---

## 🔄 Format API (Compatible OpenAI)

L'API Moonshot est compatible avec le format OpenAI :

```bash
curl -X POST https://api.moonshot.cn/v1/chat/completions \
  -H "Authorization: Bearer $KIMI_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "moonshot-v1-8k",
    "messages": [
      {"role": "system", "content": "Tu es KIMI..."},
      {"role": "user", "content": "Mission..."}
    ],
    "temperature": 0.3
  }'
```

---

## 🛡️ Sécurité

### ⚠️ Ne JAMAIS commiter la clé

```bash
# Ajouter au .gitignore
echo "*.env" >> .gitignore
echo ".kimi_api_key" >> .gitignore
```

### ✅ Utiliser variables d'environnement

```bash
# Option 1 : Export permanent
export KIMI_API_KEY="sk-..."

# Option 2 : Fichier .env (à ajouter au .gitignore)
echo "KIMI_API_KEY=sk-..." > .env
source .env

# Option 3 : Temporaire (une session)
KIMI_API_KEY="sk-..." ./test_kimi_api.sh
```

---

## 🔗 Liens Utiles

**Documentation API** : https://platform.moonshot.cn/docs
**Console** : https://platform.moonshot.cn/console
**Tarifs** : https://platform.moonshot.cn/pricing

---

## 🧪 Exemple de Prompt pour KIMI

```json
{
  "model": "moonshot-v1-8k",
  "messages": [
    {
      "role": "system",
      "content": "Tu es KIMI 2.5, Frontend Lead pour AETHERFLOW/Sullivan. Tu es spécialisé dans le rendu HTML/CSS/JS et le respect de la Constitution AETHERFLOW Article 18 (validation visuelle obligatoire)."
    },
    {
      "role": "user",
      "content": "Mission ÉTAPE 4 : Lire docs/02-sullivan/mailbox/kimi/DRILLDOWN_BACKEND_READY.md et implémenter le drill-down frontend. Quand terminé, écrire dans collaboration_hub.md : @CLAUDE_VALIDATE + ton CR."
    }
  ],
  "temperature": 0.3,
  "max_tokens": 2000
}
```

---

## ❓ FAQ

### Q: L'API est-elle disponible hors Chine ?

**R** : Oui, l'API Moonshot est accessible internationalement via HTTPS.

### Q: Quelle limite de tokens ?

**R** : Le modèle `moonshot-v1-8k` a une fenêtre de 8192 tokens (prompt + réponse).

### Q: Quel modèle choisir ?

**Options** :
- `moonshot-v1-8k` : 8K tokens (rapide, économique)
- `moonshot-v1-32k` : 32K tokens (plus cher, pour longs contextes)
- `moonshot-v1-128k` : 128K tokens (très cher, pour contextes massifs)

**Recommandation** : `moonshot-v1-8k` pour l'orchestration AETHERFLOW.

---

## 📊 Prochaines Étapes

Une fois la clé configurée :

1. ✅ Tester : `./test_kimi_api.sh`
2. ✅ Intégrer dans `trigger_kimi.sh`
3. ✅ Tester workflow complet : `./test_workflow.sh`
4. ✅ Valider avec François-Jean

---

**Créé le** : 12 février 2026, 16:10
**Par** : Claude Sonnet 4.5 (Backend Lead)
