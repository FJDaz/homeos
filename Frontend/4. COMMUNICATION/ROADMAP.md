# ROADMAP AetherFlow — Phase Active

---

## PHASE 3 — Stenciler Factory : Extraction du monolithe

---

### 🏗 MODE AETHERFLOW : Workflow d'Alignement (5 Étapes)

> [!IMPORTANT]
> **Protocole d'Exécution Autonome** : Les agents utilisent le skill `aetherflow-roadmap-operator` pour surveiller ce fichier et exécuter les missions sans "essai-erreur" visuel superflu.

1.  **CLAUDE** (Chief Engineer) : Rédige la Mission (Plan) dans cette Roadmap.
2.  **GEMINI-PAI** (Implémentation) : Code le JS/HTML via `Lexicon.js` (Code Génétique).
3.  **KIMI** (Directeur Artistique) : Ajuste le CSS dans son "Périmètre de Peinture".
4.  **GEMINI** (Validation Visuelle) : Vérifie le rendu vs V2 et valide le Pixel Perfect.
5.  **CLAUDE** (Validation Tech) : Valide la robustesse, les APIs et ferme la Mission.

---

### Contexte
`stenciler_v2.html` est un monolithe de ~1540 lignes...

---

## WORKFLOW 5 ÉTAPES — Template opérationnel (futur mode AetherFlow)

```
ÉTAPE 1 — CLAUDE (Plan)      : Diagnostique + rédige la Mission
ÉTAPE 2 — GEMINI-PAI (Code)  : Produit le JS/CSS corrigé, implémente
ÉTAPE 3 — KIMI (DA CSS)      : Pose le "feeling" dans son Périmètre de Peinture
ÉTAPE 4 — GEMINI (Audit VX)  : Benchmark visuel V3 vs V2, Go/No-Go
ÉTAPE 5 — CLAUDE (Valid Tech): Review code + APIs + ferme la Mission
```

---

### ✅ Mission 3B-E1 — CLAUDE : Diagnostic bug Header + Plan (TERMINÉE)

**Bug identifié :** `Header.feature.js::render()` génère `<header class="stenciler-header">` imbriqué
dans le slot `<header class="stenciler-header" id="slot-header">` → double wrapper.

**Règle Feature (à propager)** :
> `render()` retourne UNIQUEMENT le contenu interne du slot.
> Le slot IS le conteneur — ne jamais re-déclarer sa balise.
> `mount()` : `this.el = parent` (pas `parent.firstElementChild`).

---

### ✅ Mission 3B-E2 — GEMINI-PAI : Fix Header + Audit Structural (TERMINÉE)
STATUS: TERMINÉE
MODE: CODE DIRECT — FJD
ACTOR: GEMINI-PAI

**Résultat :**
- `Header.feature.js` corrigé (double wrapper supprimé).
- Audit complet des features : standardisation sur la règle "Le slot est le conteneur".
- Tous les `render()` retournent maintenant du contenu pur.
- `Canvas.feature.js` et `PreviewBand.feature.js` nettoyés.

---

### ✅ Mission 3B-E2 bis — CLAUDE : Stabilisation Infra (TERMINÉE)
STATUS: TERMINÉE
ACTOR: CLAUDE

**Root cause :** `HTTPServer` Python = single-threaded. ES modules font 12+ requêtes parallèles au load → timeout 408.
**Fix :** `ThreadingHTTPServer` (2 lignes dans `server_9998_v2.py`) → connexions parallèles OK.
**Note :** `/api/lexicon` était déjà implémenté dans le serveur → Mission 3C partiellement TERMINÉE.

---

### ⏳ Mission 3B-E3 — KIMI : DA CSS V3
STATUS: MISSION (ACTIVE)
MODE: CODE DIRECT — FJD
ACTOR: KIMI

---
⚠️ BOOTSTRAP KIMI — Lire avant toute action
Constitution : Frontend/1. CONSTITUTION/CONSTITUTION_AETHERFLOW_V3.md
Lexique : Frontend/1. CONSTITUTION/LEXICON_DESIGN.json

PÉRIMÈTRE DE PEINTURE — RÈGLE ABSOLUE :
1. Tu n'interviens QUE sur stenciler.css (et viewer.css si nécessaire)
2. Tu ne touches JAMAIS les .feature.js, stenciler_v3_main.js, Lexicon.js, ni le HTML
3. Ta mission : faire que /stenciler_v3 ressemble à /stenciler (V2) visuellement
4. Si une règle V2 ne s'applique pas en V3 → AJOUTE-LA dans stenciler.css (ne modifie pas l'existant)
5. Référence visuelle : http://localhost:9998/stenciler (V2 = le "costume")
---

**Zones à inspecter :**
- `.stenciler-header` : h1 + header-actions + theme-toggle alignés horizontalement
- `.sidebar` gauche : navigation tabs + genome section + style section en colonne
- `.canvas-zone` : occupe l'espace restant, canvas Fabric centré
- `.sidebar` droite : TSL picker + color palette + border slider
- Mode dark : data-theme="dark" sur `<html>`

**Critères de succès :**
1. http://localhost:9998/stenciler_v3 ≈ visuellement http://localhost:9998/stenciler
2. Layout 3 colonnes intact (sidebar L | main | sidebar R)
3. François-Jean valide visuellement

---

### ⏳ Mission 3B-E4 — GEMINI : Audit Visuel (Pixel Perfect)
STATUS: EN ATTENTE (dépend 3B-E3)
ACTOR: GEMINI (natif Antigravity)

Benchmark côte à côte /stenciler vs /stenciler_v3.
Identifier les écarts restants → renvoyer en 3B-E3 OU valider "GO".

---

### ⏳ Mission 3C — CLAUDE : Endpoint /api/lexicon + Validation Tech
STATUS: EN ATTENTE (dépend GO visuel 3B-E4)
MODE: aetherflow -f
ACTOR: CLAUDE

Ajouter dans `server_9998_v2.py` :
- `GET /api/lexicon` → lit et sert `Frontend/1. CONSTITUTION/LEXICON_DESIGN.json`

Review code : Header.feature.js corrigé + audit anti-pattern features.

---
