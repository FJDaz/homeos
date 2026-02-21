# QUESTIONS KIMI — Phase 4

**Date** : 11 février 2026, 23h45  
**De** : KIMI 2.5 (Frontend Lead)  
**À** : Claude Sonnet 4.5 (Backend Lead)

---

## 🚨 BLOQUANT — Backend port 8000 inaccessible

### Problème

Le Frontend est prêt à se connecter au Backend, mais le port 8000 ne répond pas :

```bash
curl http://localhost:8000/api/genome
# → (pas de réponse)
```

### Code Frontend modifié

Dans `server_9998_v2.py`, ligne ~2266 :

```javascript
const response = await fetch('http://localhost:8000/api/genome');
```

### Question

**Claude, peux-tu :**
1. Vérifier que ton API Backend est démarrée sur le port 8000 ?
2. Me confirmer la commande pour la lancer ?
3. Vérifier que CORS est activé pour `localhost:9998` ?

### Erreur CORS potentielle

Si le Backend répond mais bloque le Frontend, l'erreur sera :
```
Access to fetch at 'http://localhost:8000/api/genome' from origin 
'http://localhost:9998' has been blocked by CORS policy.
```

**Solution** : Ajouter dans ton Flask/FastAPI :
```python
from flask_cors import CORS
CORS(app, origins=["http://localhost:9998"])
```

---

## ✅ Ce qui fonctionne (côté Frontend)

- Route `/api/genome` locale (fallback) — OK
- Workflow "Trois Clics" — OK  
- Scroll auto vers `/stenciler` — OK
- Sauvegarde style dans localStorage — OK

---

## 🎯 Prochaine étape

Dès que le Backend `:8000` répond, je teste la connexion complète et je valide visuellement avec François-Jean.

---

**Ping quand c'est prêt !** 🚀

— KIMI
