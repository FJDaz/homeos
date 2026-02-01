# Analyse des Erreurs de Requête AETHERFLOW

**Date** : 26 janvier 2025

---

## 🔍 Types d'Erreurs "Request error"

Les erreurs `RequestError` dans httpx sont des erreurs de base qui englobent plusieurs types d'erreurs réseau et de timeout.

### Hiérarchie des Exceptions httpx

```
RequestError (base class)
├── TimeoutException
│   ├── ConnectTimeout - Échec établissement connexion
│   ├── ReadTimeout - Échec réception données
│   ├── WriteTimeout - Échec envoi données
│   └── PoolTimeout - Échec acquisition connexion du pool
└── NetworkError
    ├── ConnectError - Échec établissement connexion
    ├── ReadError - Échec réception données
    └── WriteError - Échec envoi données
```

---

## 🎯 Causes Probables dans notre Cas

### 1. **Timeout de Connexion (ConnectTimeout)**

**Symptômes** :
- Erreur après ~60 secondes (timeout configuré)
- Les deux requêtes en parallèle échouent simultanément

**Causes possibles** :
- **API DeepSeek surchargée** : Trop de requêtes simultanées
- **Problème réseau temporaire** : Latence élevée, paquets perdus
- **Rate limiting côté API** : L'API refuse les connexions temporairement
- **Timeout trop court** : 60s peut être insuffisant pour certaines requêtes longues

**Solution actuelle** :
- ✅ Retry automatique avec backoff exponentiel (2^attempt secondes)
- ✅ Les retries ont réussi dans notre cas (step_2 et step_3 ont finalement réussi)

---

### 2. **Rate Limiting de l'API**

**Symptômes** :
- Erreurs simultanées sur plusieurs requêtes parallèles
- Erreurs après ~1 minute (timeout avant que le rate limit soit clair)

**Causes** :
- **Limite de requêtes par minute** : DeepSeek peut limiter le nombre de requêtes
- **Limite de requêtes simultanées** : L'API peut limiter les connexions parallèles
- **Quota dépassé** : Limite mensuelle/quota atteint

**Solution actuelle** :
- ✅ Le code détecte les erreurs 429 (rate limit) et attend avant retry
- ⚠️ Mais les RequestError peuvent masquer les erreurs 429 si timeout avant réponse

---

### 3. **Problèmes Réseau Temporaires**

**Symptômes** :
- Erreurs intermittentes
- Erreurs sur plusieurs requêtes simultanées

**Causes** :
- **Instabilité réseau** : Connexion internet instable
- **DNS resolution** : Problème de résolution DNS temporaire
- **Firewall/Proxy** : Blocage temporaire des connexions
- **Problème côté serveur DeepSeek** : Maintenance ou problème infrastructure

**Solution actuelle** :
- ✅ Retry automatique avec backoff exponentiel
- ✅ Les retries permettent de contourner les problèmes temporaires

---

### 4. **Connexions Parallèles**

**Symptômes** :
- Les deux requêtes en parallèle échouent simultanément
- Une seule requête réussit généralement

**Causes** :
- **Limite de connexions simultanées** : L'API peut limiter les connexions parallèles
- **Pool de connexions épuisé** : httpx peut avoir des limites sur le pool
- **Conflit de ressources** : Partage de ressources entre requêtes parallèles

**Observation** :
- Dans notre cas, les deux requêtes (step_2 et step_3) ont échoué simultanément
- Mais les retries ont réussi, suggérant un problème temporaire plutôt qu'une limite structurelle

---

## 📊 Analyse de notre Cas Concret

### Scénario Observé

```
09:33:14 - Démarrage step_2 et step_3 en parallèle
09:34:15 - Les deux échouent avec "Request error" (après ~60s)
09:35:22 - step_3 réussit après retry (128s total)
09:35:40 - step_2 réussit après retry (146s total)
```

### Interprétation

1. **Timeout probable** : Les deux requêtes ont timeout après ~60s (timeout configuré)
2. **Problème temporaire** : Les retries ont réussi, indiquant un problème temporaire
3. **Pas de limite structurelle** : Les requêtes ont finalement réussi

### Causes Probables (par ordre)

1. **API DeepSeek temporairement surchargée** (70%)
   - Trop de requêtes simultanées
   - Rate limiting temporaire
   - Latence élevée côté serveur

2. **Timeout trop court pour requêtes longues** (20%)
   - 60s peut être insuffisant pour générer 2000-2500 tokens
   - Les requêtes prennent du temps à générer

3. **Problème réseau temporaire** (10%)
   - Instabilité réseau
   - Problème DNS temporaire

---

## 🔧 Solutions et Améliorations Possibles

### 1. Augmenter le Timeout

**Actuel** : 60 secondes
**Recommandé** : 120-180 secondes pour requêtes longues

```python
# Backend/Prod/config/settings.py
timeout: int = Field(
    default=120,  # Augmenté de 60 à 120
    alias="TIMEOUT",
    description="Request timeout in seconds"
)
```

### 2. Améliorer la Gestion des Erreurs

**Actuel** : `RequestError` générique
**Amélioration** : Détecter le type spécifique d'erreur

```python
except httpx.ConnectTimeout:
    # Timeout de connexion - retry avec backoff plus long
    wait_time = 5 * (2 ** attempt)
except httpx.ReadTimeout:
    # Timeout de lecture - requête trop longue, augmenter timeout
    # ou diviser la requête
except httpx.ConnectError:
    # Erreur de connexion - problème réseau, retry normal
```

### 3. Limiter les Requêtes Parallèles

**Actuel** : Toutes les étapes indépendantes en parallèle
**Amélioration** : Limiter à 2-3 requêtes simultanées par provider

```python
# Semaphore pour limiter les requêtes parallèles
semaphore = asyncio.Semaphore(2)  # Max 2 requêtes simultanées

async def _execute_step_with_monitoring(...):
    async with semaphore:
        # Exécuter la requête
```

### 4. Améliorer les Logs

**Actuel** : "Request error: {str(e)}"
**Amélioration** : Logs plus détaillés

```python
except httpx.RequestError as e:
    error_type = type(e).__name__
    error_details = {
        "type": error_type,
        "message": str(e),
        "url": self.api_url,
        "attempt": attempt + 1
    }
    logger.warning(f"Request error ({error_type}): {error_details}")
```

---

## ✅ Ce qui Fonctionne Déjà

1. **Retry automatique** : ✅ Fonctionne (les requêtes ont réussi après retry)
2. **Backoff exponentiel** : ✅ Fonctionne (2^attempt secondes d'attente)
3. **Gestion des erreurs** : ✅ Les erreurs sont capturées et retryées
4. **Parallélisation** : ✅ Fonctionne (les deux étapes ont finalement réussi)

---

## 📋 Recommandations

### Court Terme

1. **Augmenter le timeout** à 120-180 secondes
2. **Améliorer les logs** pour mieux diagnostiquer les erreurs
3. **Surveiller les patterns** : Si les erreurs se répètent, investiguer

### Moyen Terme

1. **Limiter les requêtes parallèles** par provider (semaphore)
2. **Détecter les types d'erreurs spécifiques** pour adapter la stratégie
3. **Ajouter des métriques** : Taux d'erreur, temps moyen de retry

### Long Terme

1. **Circuit breaker** : Arrêter les requêtes si trop d'erreurs
2. **Fallback providers** : Utiliser un autre provider si un échoue
3. **Queue system** : Mettre en queue les requêtes si API surchargée

---

## 🎯 Conclusion

**Les erreurs "Request error" dans notre cas sont probablement dues à** :
1. **API DeepSeek temporairement surchargée** (cause principale)
2. **Timeout de 60s peut-être trop court** pour certaines requêtes longues
3. **Problème réseau temporaire** (moins probable)

**Le système de retry fonctionne bien** : Les requêtes ont finalement réussi après retry, ce qui montre que le problème était temporaire et que la stratégie de retry est efficace.

**Recommandation principale** : Augmenter le timeout à 120-180 secondes pour réduire les erreurs de timeout.

---

**Dernière mise à jour** : 26 janvier 2025
