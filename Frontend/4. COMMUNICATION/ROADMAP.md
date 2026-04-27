# MISSION CONTROL : AETHERFLOW ROADMAP

> Missions complètes archivées dans [ROADMAP_ACHIEVED.md](./ROADMAP_ACHIEVED.md).

---

## 🧠 BOOTSTRAP GEMINI — À inclure dans TOUTE mission frontend

```
CONTEXTE TECHNIQUE OBLIGATOIRE — lis avant de coder :

1. DIAGNOSTIC DOM AVANT LISTENER
   Avant d'ajouter un event listener, remonte la chaîne du DOM :
   - Quel élément est réellement cliqué ? (e.target)
   - Y a-t-il un élément enfant `absolute inset-0` qui intercepte les clics avant le parent ?
   - Si oui → ajouter `pointer-events-none` sur l'intercepteur, puis le listener sur le parent.

2. OVERLAYS & Z-INDEX
   Un overlay `hidden` sur un parent = ses enfants sont invisibles même si LEUR hidden est retiré.

3. RÈGLE DE LIVRAISON
   Ne pas marquer TERMINÉ avant d'avoir testé manuellement le comportement dans le browser.

4. SCOPE STRICT
   Ne pas refactoriser les fichiers existants stables sans instruction explicite.

5. STYLE HOMÉOS
   Pas de majuscules dans les labels UI. Pas d'emojis. Border-radius max `rounded-[20px]`.
   Vert HoméOS (#8cc63f) uniquement en nudge — jamais en fond large.

6. ICÔNES — SVG INLINE UNIQUEMENT
   Règle : utiliser des SVG inline Lucide-style (viewBox 0 0 24 24, stroke currentColor, fill none, stroke-width 1.8).
```

---

## 🧠 BOOTSTRAP BACKEND — RÈGLE ASYNC (CRITIQUE)

```
INTERDICTION ABSOLUE : nest_asyncio.apply()
RÈGLE : pour exécuter du code synchrone bloquant dans un contexte async FastAPI, utiliser asyncio.to_thread(fn, *args).
```

---

## 🧠 BOOTSTRAP BACKEND — RÈGLE REDÉMARRAGE

```
RÈGLE OBLIGATOIRE : après toute mission livrée en backend, le serveur DOIT être redémarré (bash start.sh).
```

---

## Sprint actif — 2026-04-27

| Mission | Titre | Status | Actor |
|---------|-------|--------|-------|
| SPR_APR | Missions M327 à M355 | ✅ ARCHIVÉES | GEMINI |
| M358 | Sullivan ME — Droits écriture manifest (apply suggestion) | ✅ TERMINÉE | GEMINI |
| M350 | Vue "Live Watch" (Drill Status Polling) | 🟠 À TRAITER | GEMINI |
| M351 | Notation Automatique par Référentiel | 🟠 À TRAITER | CLAUDE |


---

## Thème 39 — Sullivan Manifest Editor

### M358 — Sullivan ME : droits écriture manifest (apply suggestion)
**ACTOR: GEMINI | MODE: CODE DIRECT | STATUS: ✅ TERMINÉE | DÉPEND: M357**

```
CONTEXTE TECHNIQUE OBLIGATOIRE — lis avant de coder :

1. DIAGNOSTIC DOM AVANT LISTENER
   Avant d'ajouter un event listener, remonte la chaîne du DOM.
2. SCOPE STRICT — ne pas refactoriser les fichiers existants stables.
3. RÈGLE DE LIVRAISON — ne pas marquer TERMINÉ sans test browser.
4. STYLE HOMÉOS — pas de majuscules, pas d'emojis, vert #8cc63f en nudge uniquement.
5. ICÔNES — SVG inline Lucide-style uniquement.
```

**Problème résolu :**
Sullivan suggère des modifications mais l'élève doit les recopier manuellement dans l'éditeur. Il faut un bouton "appliquer" par suggestion.

**Endpoint backend à créer dans `sullivan_router.py` :**
```
POST /api/sullivan/manifest-apply
Headers: X-User-Token
Body: { "manifest_text": "...", "suggestion": "...", "suggestion_id": 1 }
Response: { "proposed_manifest": "...", "error": null }
```
- Utilise GroqClient (même pattern que manifest-critique), timeout 20s
- Prompt : "Réécris ce manifest en intégrant naturellement cette suggestion. Retourne UNIQUEMENT le manifest réécrit, sans commentaire."
- Si échec → `{ "proposed_manifest": null, "error": "..." }`

**Frontend — `ManifestSullivan.js` UNIQUEMENT :**

1. Ajouter bouton "appliquer" dans `showSuggestions()` pour chaque carte :
```html
<button class="btn-apply-suggestion text-[10px] px-2 py-0.5 rounded-[6px] border border-[#e5e5e5] hover:border-[#8cc63f] hover:text-[#8cc63f] transition-all" data-id="1">appliquer</button>
```

2. Au clic : désactiver bouton → "en cours..." → POST `/api/sullivan/manifest-apply` → si `proposed_manifest` → appeler `refs.applyManifest(text)` → bouton passe en "appliqué ✓"

3. `refs.applyManifest` est fourni par ManifestBox dans l'appel `init()` existant — ajouter :
```javascript
applyManifest: (text) => { els.editor.value = text; onTextChange(); }
```

**Ce qui NE change PAS :** ManifestBox.js au-delà de l'ajout de `applyManifest` dans `init()`, la route manifest-critique, la structure critique/questions/suggestions.

**Test de validation :**
1. Critique apparaît → répondre oui/non → suggestions affichées avec bouton "appliquer"
2. Clic "appliquer" → spinner → éditeur mis à jour en < 5s
3. Recharger la page → manifest sauvegardé

---

## Thème 37 — NLP / HCI (Réservé FJD)

> **Ces travaux sont exclusivement menés par FJD. Ne pas déléguer.**

### Vision architecture BERT + Bayesian + MinB/MaxB

**Pipeline cible :**
```
Contexte large (RAG passages) + message user (500 tokens)
  → BERT all-MiniLM-L6-v2 (cosine sim → intent vector 384d)
  → Bayesian update : prior = sliding window 3 derniers intents
  → Routing MinB / MaxB
```

**État actuel dans `maiathon/Spinoza_Secours_HF/Backend/app_runpod.py` :**
- ✅ BERT `all-MiniLM-L6-v2` chargé
- ✅ 4 intent anchors (accord / confusion / resistance / neutre)
- ✅ Cosine similarity → intent label
- ❌ Score de confiance non retourné
- ❌ Aucun routing MinB/MaxB

---

## Thème 35 — Dashboard Prof : Suivi & Analytics

> Ce thème concerne la visibilité en temps réel de l'avancement des étudiants et la gestion granulaire des sujets.

### M350 — Vue "Live Watch" (Drill Status Polling) 
**STATUS: 🟠 À TRAITER | ACTOR: GEMINI**

### M351 — Notation Automatique par Référentiel
**STATUS: 🟠 À TRAITER | ACTOR: CLAUDE**

### M352 — CR (Compte-Rendu)
**STATUS: ✅ TERMINÉE | ACTOR: GEMINI**
- **Async Fix** : Passage de `extract_design_tokens` en `async def` dans `import_router.py`. La tâche de fond `extract_tokens_background` est maintenant invoquée proprement via le loop principal de FastAPI, prévenant les blocages d'event loop.
- **Archivage** : Déplacement du fichier legacy `design.md` (racine) vers `docs/04_Archives/design_stitch_legacy.md`. La Constitution (`Frontend/1. CONSTITUTION/DESIGN.md`) est désormais l'unique source de vérité stylistique.

### M353 — CR (Compte-Rendu)
**STATUS: ✅ TERMINÉE | ACTOR: GEMINI**
- **Inférence HCI** : Nouvelle route `POST /api/imports/infer-intent` implémentée.
- **Sullivan Bridge** : Utilisation de `GeminiClient` pour transformer les design tokens bruts (palette hex, typo, spacing) en intention structurée (archétype, humeur, sections suggérées).
- **Persistance Manifeste** : Les résultats sont sauvegardés dans `manifest.json["intent_inference"]`, permettant une pré-configuration intelligente du projet avant même que l'élève ne commence à câbler.
- **Robustesse** : Gestion des erreurs si les tokens sont absents et nettoyage automatique des sorties markdown/code-blocks de Sullivan.
