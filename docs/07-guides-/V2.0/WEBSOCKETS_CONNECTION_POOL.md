# WebSockets & Connection Pooling - Guide Technique

**Date** : 26 janvier 2025  
**Statut** : ✅ **IMPLÉMENTÉ (Connection Pooling)**  
**Référence** : Voir `ETAPE_9_REDUCTION_LATENCE.md` pour vue d'ensemble

---

## 🎯 Objectif

Réduire l'overhead réseau (DNS + TCP + TLS handshake) en réutilisant les connexions HTTP persistantes.

**Gain cible** : >30% réduction overhead réseau, ~350ms économisés par requête réutilisée

---

## 📋 Architecture

### **Connection Pooling HTTP**

Les clients HTTP utilisent `httpx.AsyncClient` qui gère automatiquement :
- **Connection pooling** : Réutilisation des connexions TCP
- **Keep-alive** : Maintien des connexions ouvertes
- **HTTP/2** : Support si disponible (réduction overhead)

**Overhead évité par réutilisation** :
- DNS lookup : ~50ms
- TCP handshake : ~100ms  
- TLS handshake : ~200ms
- **Total économisé** : ~350ms par requête réutilisée

---

## 🔧 Implémentation

### **Module** : `Backend/Prod/network/connection_pool.py`

**Classe principale** : `ConnectionPool`

```python
from Backend.Prod.network import ConnectionPool

pool = ConnectionPool()

# Get persistent client for a provider
client = pool.get_client(
    provider="deepseek",
    base_url="https://api.deepseek.com",
    headers={"Authorization": "Bearer ..."},
    timeout=120
)

# Client is reused across requests
response1 = await client.post("/v1/chat/completions", json=...)
response2 = await client.post("/v1/chat/completions", json=...)  # Reuses connection
```

---

## 🔌 Intégration Actuelle

### **Clients HTTP existants** :

Tous les clients (`DeepSeekClient`, `GeminiClient`, `GroqClient`, `CodestralClient`) utilisent déjà `httpx.AsyncClient` qui gère automatiquement le connection pooling.

**Optimisation actuelle** :
- ✅ Clients créés une fois dans `__init__`
- ✅ Réutilisés pour toutes les requêtes
- ✅ Connection pooling automatique via httpx
- ✅ Keep-alive activé par défaut

**Note** : Le `ConnectionPool` module est disponible pour une optimisation future si nécessaire (pool partagé entre instances).

---

## 📊 Métriques

### **ConnectionPoolStats** :

- `total_requests` : Total de requêtes
- `connections_reused` : Connexions réutilisées
- `connections_created` : Nouvelles connexions créées
- `connection_reuse_rate` : Taux de réutilisation (%)
- `dns_lookups_saved` : DNS lookups économisés
- `tls_handshakes_saved` : TLS handshakes économisés
- `network_overhead_reduction_ms` : Overhead réseau réduit (ms)

### **StepMetrics étendues** :

- `network_overhead_ms` : Overhead réseau mesuré
- `connection_reused` : Booléen (connexion réutilisée)

---

## 🌐 WebSockets (Optionnel)

### **Support WebSockets** :

**Gemini Live API** : Supporte WebSockets pour streaming temps réel
- Réduit encore plus l'overhead (pas de handshake par requête)
- Utile pour sessions longues avec streaming
- Nécessite API Gemini Live (différent de l'API standard)

**Autres providers** : DeepSeek, Groq, Codestral utilisent HTTP REST
- Pas de support WebSocket natif
- Connection pooling HTTP suffit pour optimiser

### **Implémentation future** :

Si besoin de WebSockets pour Gemini Live :
```python
# Exemple futur (non implémenté pour l'instant)
from websockets import connect

async def gemini_live_stream(prompt):
    async with connect("wss://gemini-live-api...") as ws:
        await ws.send(prompt)
        async for message in ws:
            yield message
```

---

## ⚙️ Configuration

### **httpx.AsyncClient** (déjà utilisé) :

- **Connection pooling** : Automatique
- **Keep-alive** : Activé par défaut (30s)
- **HTTP/2** : Activé si supporté
- **Max connections** : Illimité par défaut (peut être limité)

### **Optimisation recommandée** :

Pour limiter les connexions :
```python
limits = httpx.Limits(
    max_connections=100,
    max_keepalive_connections=20,
    keepalive_expiry=30.0
)

client = httpx.AsyncClient(limits=limits)
```

---

## 📈 Gains Attendus

| Métrique | Valeur | Description |
|----------|--------|-------------|
| **Overhead réduit** | ~350ms | Par requête réutilisée |
| **DNS lookups économisés** | 1 par requête | Après première connexion |
| **TLS handshakes économisés** | 1 par requête | Après première connexion |
| **Connection reuse rate** | >80% | Pour workflows répétitifs |

---

## 🔍 Détails Techniques

### **Comment ça fonctionne** :

1. **Première requête** : DNS lookup + TCP + TLS handshake (~350ms)
2. **Requêtes suivantes** : Réutilisation connexion existante (~0ms overhead)
3. **Keep-alive** : Connexion maintenue ouverte 30s
4. **HTTP/2** : Multiplexing si supporté (plusieurs requêtes sur même connexion)

### **httpx gère automatiquement** :

- Pool de connexions par domaine
- Réutilisation intelligente
- Nettoyage des connexions expirées
- Retry avec nouvelle connexion si nécessaire

---

## ✅ Statut

- ✅ Connection pooling automatique via httpx (déjà en place)
- ✅ Module `ConnectionPool` créé (pour optimisation future)
- ✅ Métriques réseau ajoutées à `StepMetrics`
- ⏳ WebSockets Gemini Live (optionnel, non implémenté)

---

## 📝 Notes

- **httpx.AsyncClient** : Gère déjà le connection pooling efficacement
- **Pas besoin de WebSockets** : Pour la plupart des cas, HTTP avec pooling suffit
- **WebSockets utiles** : Seulement pour streaming temps réel (Gemini Live)

---

## 🔗 Références

- Plan de réduction latence : `/docs/guides/Plan de rédcution de la latence API.md`
- Roadmap : `/docs/guides/PLAN_GENERAL_ROADMAP.md` (Étape 9)
- httpx documentation : https://www.python-httpx.org/
