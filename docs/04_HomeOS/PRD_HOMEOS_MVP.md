# PRD HoméOS MVP — Document de Référence Technique
**Auteur :** FJD + Claude
**Dernière mise à jour :** 2026-03-30
**Statut :** en cours — pipeline Figma→FRD opérationnel, Wire mode en construction

---

## 0. Philosophie — L'Architecte, pas le Maçon

HoméOS ne cherche pas à cacher la complexité technique au designer. Il cherche à la rendre **lisible**.

Un architecte ne coule pas le béton. Mais il sait que le B40 ne se comporte pas comme le B25. Il sait que l'acier en zone sismique change tout, que le douglas outdoor a un DTU, que le plomb en façade implique des joints de dilatation. Il peut parler à l'ingénieur structure parce qu'ils partagent le vocabulaire des matériaux et des contraintes — pas l'expertise d'exécution.

HoméOS forme des **designers-architectes** : des personnes qui savent par quelle chaîne industrielle passe leur produit. Pas des experts omniscients — des professionnels qui n'ignorent rien de la composition des matériaux qu'ils prescrivent.

Ce que HoméOS enseigne en le montrant :
- Ce bouton appelle une route `POST` — c'est une promesse au serveur
- Une route sans test est une promesse non tenue
- Un déploiement sans CI/CD est une opération manuelle risquée
- Une modale au lieu d'une page implique un état frontend — ça coûte du dev
- Un sprint, un run, un déploiement — ce sont des rythmes de production que le designer prescrit autant que le dev

**Wire mode** est l'instrument central de cette pédagogie : il rend visible l'écart entre ce qui est conçu et ce qui est câblé. Cet écart n'est pas le problème du dev. C'est le problème du designer aussi.

**Sullivan** est l'autre versant : un expert design de haut niveau — typographie (Vox-ATypI, classification des graisses, rythme vertical), culture graphique (Étapes, Eye, Emigre, Typographica), innovation interfacielle (l'ambition Flash era — des interfaces conçues, pas templées). Sullivan parle aux designers dans leur langue. Il conseille, il invente, il challenge. Il n'est pas un générateur Tailwind de plus.

Le positionnement global : **Stitch et ses concurrents s'adressent aux devs qui veulent du UI correct. HoméOS s'adresse aux designers qui veulent du UI remarquable — et qui méritent de comprendre la chaîne entière de leur produit.**

---

## 1. Vision

HoméOS est un **atelier pédagogique de conception UI augmentée par IA**. Il transforme un export visuel Figma (SVG) en document fonctionnel (FRD — Functional Reality Document) prêt pour l'implémentation, en exposant à chaque étape la chaîne complète : intention détectée, code backend associé, bijection UI↔API, test, déploiement.

Pipeline cible :
```
Figma (design)
    ↓  Bridge Plugin (export SVG)
Landing Import  ←  réception + liste écrans
    ↓
Intent Viewer   ←  analyse archétype + tableau intentions
    ↓
FRD Editor      ←  wire mode + implémentation bijective
    ↓
Aperçu local    ←  test interactions réelles
    ↓
Deploy          ←  CI/CD → HF Spaces Docker
```

**Philosophie dérivée seconde :** HoméOS est construit depuis HoméOS pour éprouver Sullivan en live. Ce qu'un agent doit faire en autonomie devient une mission Gemini. Ce qui est hardcodé est signé `CODE DIRECT — FJD`.

---

## 2. Architecture Technique

### Serveur
- **Runtime :** Python 3.14, FastAPI, uvicorn
- **Port local :** 9998
- **Entrée :** `Frontend/3. STENCILER/server_v3.py`
- **Démarrage :** `python3 server_v3.py` (bloc `__main__` → `uvicorn.run(app, port=9998)`)
- **Production :** HF Spaces Docker, port 7860, `start_hf.sh`

### Fichiers clés
| Fichier | Rôle |
|---|---|
| `server_v3.py` | FastAPI principal — routes pages + montage routers |
| `Backend/Prod/retro_genome/routes.py` | Router `/api/retro-genome/*` |
| `Backend/Prod/wire_analyzer.py` | Analyse bijective UI↔API |
| `static/templates/landing.html` | Page d'accueil — liste imports Figma |
| `static/templates/intent_viewer.html` | Tableau intentions + annotation |
| `static/templates/frd_editor.html` | Éditeur FRD + Wire mode |
| `Frontend/figma-plugin/ui.html` | Panel plugin Figma Bridge |
| `Frontend/figma-plugin/code.js` | Logique plugin Figma (export SVG) |
| `static/css/stenciler.css` | Source de vérité design HoméOS |
| `exports/retro_genome/index.json` | Registre des imports Figma (50 derniers) |

### Stack Frontend
- **CSS :** `stenciler.css` (tokens warm neutrals) + Tailwind CDN pour layout
- **Typo :** Geist, -apple-system, 12px base
- **JS :** Vanilla uniquement
- **Éditeur :** Monaco Editor (CDN v0.45.0) — FRD Editor + Wire code popover

### Design tokens HoméOS (stenciler.css)
| Token | Valeur | Usage |
|---|---|---|
| `--bg-primary` | `#f7f6f2` | fond principal (crème chaud) |
| `--bg-secondary` | `#f0efeb` | fond carte/sidebar |
| `--border-subtle` | `#d5d4d0` | bordures |
| `--text-primary` | `#3d3d3c` | texte principal |
| `--text-muted` | `#999998` | labels secondaires |
| accent vert | `#8cc63f` | actions, badges, nudges |

**Règles absolues UI :** pas de `text-transform: uppercase`, pas d'emojis, pas de glassmorphism, pas de bleu iOS.

---

## 3. Pipeline d'Ingestion (Figma → index.json)

### 3.1 Plugin Figma Bridge
- **Fichiers :** `Frontend/figma-plugin/ui.html` + `code.js`
- **Fonctionnement :**
  1. `code.js` scanne les frames de la page courante (`figma.currentPage.children`)
  2. `ui.html` affiche la liste avec checkboxes
  3. L'utilisateur coche les frames → clique "envoyer à HoméOS"
  4. `code.js` exporte chaque frame en SVG (`node.exportAsync({ format: 'SVG' })`)
  5. `ui.html` poste chaque SVG via `POST /api/retro-genome/upload-svg`
  6. Feedback affiché : nom frame + archétype + nb éléments + lien intent viewer

### 3.2 Route `POST /api/retro-genome/upload-svg`
- **Parser :** `parse_figma_svg()` — analyse regex/DOM locale, **sans appel IA**
  - Extrait éléments (`text`, `rect`, `image`, `group`…) avec rôle apparent et contenu
  - Détecte les tokens design (fonts, couleurs)
- **Détection archétype :** `ArchetypeDetector.detect()` — règles heuristiques locales
  - Retourne `archetype_id`, `label`, `confidence`, `artifact_type`, `dev_brief`
- **Persistence :** sauvegarde SVG dans `exports/retro_genome/YYYY-MM-DD/SVG_*.svg`
- **index.json :** entrée enrichie avec `archetype_id`, `archetype_label`, `elements_count`
- **Notification :** incrémente `_NEW_IMPORTS_COUNT` (polling `/api/retro-genome/notifications`)

### 3.3 CORS
- `CORSMiddleware` avec `allow_origins=["*", "null"]` — nécessaire car le plugin Figma tourne dans une iframe sandboxée (`origin: null`)
- Exception handler global sur `Exception` → ajoute `Access-Control-Allow-Origin: *` sur les 500

---

## 4. Pages et Routes

| URL | Template | Statut |
|---|---|---|
| `/landing` | `landing.html` | ✅ opérationnel |
| `/intent-viewer` | `intent_viewer.html` | ✅ opérationnel |
| `/template-viewer?template=frd_editor.html` | `frd_editor.html` | ✅ opérationnel |
| `/brainstorm` | `brainstorm_war_room_tw.html` | ✅ opérationnel |
| `/` | 404 (pas de root par défaut) | — |

### 4.1 Landing (`/landing`)
- Fetch `/api/retro-genome/imports` au chargement → grille de cartes par import
- Badge notification si `new_count > 0` (polling + auto-clear)
- Polling 10s
- Bouton "analyser" → `/intent-viewer`

### 4.2 Intent Viewer (`/intent-viewer`)
- Auto-load dernier import Figma au `DOMContentLoaded` (fonction `autoLoadLatestImport`)
- Affiche nom, archétype, nb éléments, timestamp du dernier import
- Tableau des intentions détectées
- Drawer d'annotation (Pattern 5) → call `/api/frd/annotate`
- Lien direct vers FRD Editor par intention

### 4.3 FRD Editor
- Wire mode : analyse bijective UI↔API via `wire_analyzer.py`
- Table bijective : badges ok/error par intention
- Code popover Monaco : clic sur badge → affiche code Python du handler (M99)
- Peel-out CSS sur iframe en wire mode

---

## 5. Missions — État

### ✅ Terminées (cette session)

| Mission | Livré | Notes |
|---|---|---|
| M101-bis | Bridge Plugin design conforme | CODE DIRECT Claude — vert #8cc63f, pas d'uppercase, pas d'emojis |
| M100 | Landing Import (`/landing`) | Gemini (design) + Claude (route server_v3.py + hotfixes) |
| M102 | Intent Viewer auto-load | Claude CODE DIRECT — routes.py enrichissement index.json + intent_viewer.html autoLoadLatestImport |
| M106 | CI/CD HF Spaces | Claude CODE DIRECT — Dockerfile, start_hf.sh, requirements.hf.txt, deploy-hf.yml, README.md |

### ✅ Terminées (sessions précédentes, dans ROADMAP)

| Mission | Livré |
|---|---|
| M91 | API Generator Engine (retro-genome → FastAPI routes) |
| M92 | Archetypes HoméOS natifs (`functional_archetypes.json`) |
| M97 | Wire UX v2 : table bijective + diagnostic géographique |
| M98 | Wire UX v3 : skeleton mode |
| M99 | Wire UX v4 : peel-out CSS + pop-in Monaco + route `wire-source` |

### 🔵 En attente

| Mission | Priorité | Dépendances |
|---|---|---|
| M103 — Wire v5 : auto-launch + overlay z-index | P2 | M99 ✅ |
| M104 — INTENT_MAP enrichi (routes manifest + fetch inline) | P2 | M103 |
| M105 — Aperçu local (serveur temporaire + onglet réel) | P3 | — |

---

## 6. CI/CD — HF Spaces

### Infrastructure (M106 ✅)
- **Dockerfile :** `FROM python:3.11-slim`, port 7860, `USER 1000`, `start_hf.sh`
- **start_hf.sh :** `cd "Frontend/3. STENCILER" && uvicorn server_v3:app --port 7860`
- **requirements.hf.txt :** dépendances allégées (pas playwright, pas llama-index)
- **GitHub Actions :** `.github/workflows/deploy-hf.yml` — push `main` → `git push hf-space main --force`
- **README.md :** metadata YAML HF Spaces (`sdk: docker`, `app_port: 7860`)

### Ce qu'il reste à faire (FJD)
1. Créer le Space sur huggingface.co/new-space → `FJDaz/homeos` → SDK Docker
2. Ajouter secret `HF_TOKEN` dans GitHub → Settings → Secrets
3. `git push origin main` → déclenche le deploy automatiquement
4. DNS OVH (optionnel) : CNAME `homeos.fjdaz.com` → `fjdaz-homeos.hf.space`

---

## 7. Points d'attention techniques

- **`parse_figma_svg` est local, sans IA** : l'analyse de structure SVG est heuristique. La qualité dépend de la structure du SVG Figma (les frames vides ou hors-cadre échouent à l'export).
- **index.json** : les anciens imports (avant M102) n'ont pas `archetype_label`/`elements_count`. L'interface affiche `—` pour les champs manquants, pas d'erreur.
- **Serveur local vs HF** : port 9998 en local, port 7860 en prod. Les URLs hardcodées dans le plugin Figma (`localhost:9998`) ne fonctionnent qu'en local — c'est intentionnel pour la pédagogie.
- **stenciler.css vs landing.html** : landing utilise `--vert-homeos: #7aca6a` (Gemini) au lieu de `#8cc63f` (token officiel). À normaliser lors d'une prochaine passe design.
- **Stenciler V3** (`/stenciler`) : remplacé par Figma dans le workflow pédagogique. Toujours accessible mais en veille — nettoyage prévu post-MVP.
