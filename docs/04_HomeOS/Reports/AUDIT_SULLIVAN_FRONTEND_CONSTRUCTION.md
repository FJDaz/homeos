# Audit — Sullivan, frontend mode construction

**Date** : 30 janvier 2026  
**Objectif** : État des lieux concret, câblage, pertinence des tests, et ordre par rapport à l’HCI IR.

---

## 1. Où on en est

### 1.1 Backend (API)

| Élément | État | Fichier / remarque |
|--------|------|---------------------|
| `GET /studio/genome` | ✅ Exposé | `Backend/Prod/api.py` — fichier ou génération à la volée ; fallback genome minimal si échec |
| `_get_minimal_genome()` | ✅ Implémenté | Fallback mode construction (metadata, topology, 4 endpoints) |
| `GET /health` | ✅ | Health check |
| `POST /sullivan/search` | ✅ | Recherche composant |
| `POST /sullivan/dev/analyze` | ✅ | DevMode |
| `POST /sullivan/designer/upload` | ✅ | DesignerMode |
| Routes preview, execute, etc. | ✅ | Présentes |
| CORS | ✅ | `allow_origins=["*"]` |
| Route `/` | ✅ | Landing API ou index si fichiers présents |

### 1.2 Frontend SvelteKit (mode construction)

| Élément | État | Fichier / remarque |
|--------|------|---------------------|
| Route `/studio` | ✅ | `frontend-svelte/src/routes/studio/+page.svelte` |
| Chargement genome | ✅ | `getGenome()` depuis `$lib/api` dans `onMount` |
| Affichage organes | ✅ | Boucle sur `genome.endpoints`, un bloc par endpoint avec `x_ui_hint` |
| Boutons Fetch/Execute | ✅ | `callEndpoint(ep.path, ep.method)` au clic |
| ValidationOverlay | ✅ | `?validation=1` → overlay z-index 10000 (Accept/Reject/Refine stub) |
| Proxy Vite `/api` → 8000 | ✅ | `frontend-svelte/vite.config.js` |
| `getApiBase()` en dev | ✅ | Retourne `'/api'` si `import.meta.dev` |

### 1.3 Incohérence de câblage (source possible de 404)

- **getGenome()** : utilise `$lib/api` → `getApiBase()` → en dev = `'/api'` → requête `GET /api/studio/genome` → proxy → `GET http://127.0.0.1:8000/studio/genome`. ✅
- **callEndpoint()** : utilise `API_BASE = env.PUBLIC_API_URL || 'http://127.0.0.1:8000'` → en dev sans env = **`http://127.0.0.1:8000`** → requêtes directes vers 8000 (pas via proxy).
- Conséquence : même origine pour le genome, origine différente pour les appels aux organes. Si l’API n’est pas sur 8000 ou qu’une route appelée n’existe pas, on peut avoir 404 ou erreur réseau.
- **Recommandation** : utiliser la même base que `getGenome()` pour les appels organes (ex. importer `getApiBase` depuis `$lib/api` et utiliser `getApiBase()` pour `API_BASE` dans la page Studio).

### 1.4 Ce qui n’est pas fait (vision doc)

- **Layout inféré par Aetherflow** : pas de flux “Sullivan lit le genome → Aetherflow infère un layout → layout proposé”. Le Studio affiche **directement** les endpoints du genome (un organe par endpoint), pas un layout “proposé” puis amendable.
- **Chatbot pour amender le layout** : lien Chatbox ↔ Studio prévu, mais pas de dialogue structuré pour amender un layout (phase ultérieure).
- **HCI Intent Refactoring (IR)** : 3 panels, 7 phases visuelles, WebSocket — **non implémenté** ; décrit dans `docs/02-sullivan/HCI DE L'INTENT REFACTORING.md` et plan Phase C.

---

## 2. Câblage : est-ce correct ?

- **API ↔ Genome** : correct. `GET /studio/genome` sert fichier ou génération ou genome minimal.
- **Frontend ↔ Genome** : correct **si** API sur 8000 + front en dev (proxy actif). `getGenome()` → `/api/studio/genome` → proxy → 8000.
- **Frontend ↔ Appels organes** : incohérent. La page utilise `API_BASE` (127.0.0.1:8000) au lieu de la base “proxy” (`/api`). À aligner pour tout passer par la même base en dev.
- **404 `{"detail":"Not Found"}`** : peut venir (1) d’une route inexistante appelée par le front, (2) d’un sous-chemin mal formé, (3) d’une API non redémarrée après ajout du fallback genome. Vérifier en devtools quelle URL renvoie 404.

---

## 3. Tester le parcours à ce stade : utile ou pas ?

- **Utile** pour vérifier que :
  - l’API démarre ;
  - `GET /studio/genome` renvoie 200 (fichier ou minimal) ;
  - le front SvelteKit charge et affiche au moins les 4 organes du genome minimal (Health, Get Genome, Execute, Index) ;
  - les clics sur les organes appellent bien l’API (après alignement de `API_BASE`).
- **Limites** : pas de “layout inféré”, pas d’amendement par chat, pas d’IR. Donc test = **parcours construction minimal** (genome → affichage organes → appels API), pas le parcours produit complet.

Conclusion : **oui, c’est utile** de tester ce parcours maintenant pour valider le câblage et éviter les 404 ; en parallèle, traiter l’incohérence `API_BASE` / `getApiBase()`.

---

## 4. Faut-il implémenter l’HCI IR avant d’afficher quoi que ce soit ?

- **Non.** La doc (MODE_EMPLOI_SULLIVAN_GENOME, plan Studio concret) décrit :
  1. **D’abord** : Genome → Studio affiche les organes (ce qu’on a en place).
  2. **Ensuite** : Layout inféré par Aetherflow + amendement via chatbot.
  3. **Phase C** : HCI IR (3 panels, 7 phases) pour rendre visible l’écart intention / implémentation.

L’HCI IR est une **couche supplémentaire** (Intent Refactoring, décisions Garder/Réserve/Obsolète, gel du genome). Elle n’est pas prérequise pour afficher le Studio à partir du genome. Ordre recommandé : **stabiliser l’affichage construction actuel** (genome → organes, sans 404), puis enchaîner sur Phase C (IR) quand on voudra exploiter intention vs implémentation.

---

## 5. Actions recommandées (ordre)

1. **Corriger le câblage Studio** : dans `frontend-svelte/src/routes/studio/+page.svelte`, utiliser pour les appels organes la même base que pour le genome (ex. `import { getGenome, getApiBase } from '$lib/api'` et `const API_BASE = getApiBase()`), pour que en dev tout passe par `/api` (proxy).
2. **Vérifier la 404** : avec l’API démarrée (`./start_api.sh`) et le front en dev, ouvrir l’onglet Network, recharger `/studio`, et noter l’URL qui renvoie `{"detail":"Not Found"}` (ex. `/studio/genome` vs autre).
3. **Tester le parcours minimal** : API + front dev → ouvrir http://localhost:5173/studio → vérifier chargement genome (200) et affichage des organes → cliquer Health / Get Genome → vérifier réponses 200.
4. **Ensuite** : Phase A (ETAT_LIEUX, README) et Phase C (HCI IR) selon le plan, sans bloquer l’affichage actuel sur l’IR.

---

## 6. Références

- `docs/02-sullivan/MODE_EMPLOI_SULLIVAN_GENOME.md`
- `docs/02-sullivan/HCI DE L'INTENT REFACTORING.md`
- `docs/04-homeos/ETAT_LIEUX.md`
- `.cursor/plans/studio_concret_puis_doc.plan.md`
- `Backend/Prod/api.py` (get_studio_genome, _get_minimal_genome)
- `frontend-svelte/src/lib/api.js` (getApiBase, getGenome)
- `frontend-svelte/src/routes/studio/+page.svelte`
