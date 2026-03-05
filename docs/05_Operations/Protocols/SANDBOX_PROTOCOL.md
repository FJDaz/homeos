# 🧪 Sandbox Protocol V1.1 - Pure Frontend

> **Zero serveur modification - Zero backend touch**

---

## ✅ Constitution Compliance

| Règle | Statut |
|-------|--------|
| Pas de modif serveur | ✅ `server_9998_v2.py` intact |
| Pas de modif backend | ✅ `genome.json` intact |
| Pristine Mode | ✅ Production non affectée |
| Cache control | ✅ Bypass SW en sandbox |

---

## 🚀 Usage (3 étapes)

### 1. Ouvrir Stenciler
```
http://localhost:9998/stenciler
```

### 2. Activer Sandbox
Console (F12):
```javascript
window.enableSandbox()
```

### 3. Tester Layouts
```javascript
// Injecter un payload SVG
fetch('/static/../sandbox_payloads/frontend_wave_layout.svg')
  .then(r => r.text())
  .then(svg => window.sandboxInject(svg));
```

---

## 📦 Payloads

| Fichier | Description |
|-----------|-------------|
| `timeline_rail.svg` | Rail à 7 étapes |
| `frontend_card.svg` | Carte Hype Minimaliste |
| `frontend_wave_layout.svg` | Layout vague complet |

---

## 🎨 API Console

```javascript
window.enableSandbox()     // Active le mode 🧪
window.disableSandbox()    // Désactive
window.sandboxInject(svg)  // Injecte SVG
```

---

*« Le sandbox est dans le Frontend, pas dans le serveur »*  
— Constitution V3.1, Article 7
