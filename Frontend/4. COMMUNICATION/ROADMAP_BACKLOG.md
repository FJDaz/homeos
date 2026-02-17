# ROADMAP_BACKLOG — Phases Futures (non planifiées)

**Append-only. Ces phases ne sont pas en cours — elles sont documentées pour ne pas être perdues.**
**Quand une phase passe en active → copier dans ROADMAP.md + archiver ici avec STATUS: TRANSMIS.**

---

## PHASE 3 — Analyse Upload + Fulfillement Auto
STATUS: BACKLOG
DÉPEND DE: Phase 2 complète (drill-down + wireframes fixes)

### Périmètre

L'utilisateur peut uploader une maquette (image PNG/JPG) depuis la section "Importer ma Maquette"
déjà présente dans `viewer.html` (L151-166). Le système analyse l'image et l'adapte au genome.

### Cas à couvrir

**Cas 1 — Design complet**
Upload d'une maquette qui couvre la totalité des composants du genome.
→ Mapper les zones visuelles de la maquette aux n3_components correspondants.
→ Chaque composant hérite du style visuel détecté (couleurs, typographie, densité).

**Cas 2 — Design incomplet (le plus fréquent)**
Upload d'une maquette partielle (ex: only desktop, only login screen, etc.).
→ Détecter les composants manquants (ceux du genome sans correspondance visuelle).
→ **Fulfillement auto** : générer les composants manquants en cohérence avec le style détecté.
   Règles : emprunter la palette, la typographie, le niveau de densité de la maquette uploadée.
   Ne jamais laisser un composant du genome sans rendu visuel.

### Inputs / Outputs attendus

```
Input  : image (PNG/JPG) + genome_reference.json
Process: analyse visuelle → mapping genome → détection lacunes → fulfillement
Output : genome enrichi avec visual_tokens par composant (palette, density, layout_type)
```

### Notes techniques

- L'analyse d'image nécessite un appel LLM (vision) → côté backend, nouvel endpoint `/api/analyze-upload`
- Le fulfillement = inférence des tokens manquants → peut être règle-basé ou LLM
- Le `semantic_bridge.js` doit laisser passer les tokens visuels (pas de CSS — uniquement semantic attributes)
- Voir `Frontend/3. STENCILER/static/design-bundles.json` pour le format des tokens visuels existant

---

## PHASE 4 — Adaptation des 8 Styles
STATUS: BACKLOG
DÉPEND DE: Phase 2 (wireframes) + optionnellement Phase 3 (upload)

### Périmètre

Les 8 styles déjà présents dans `viewer.html` (L173-221) :
`minimal`, `corporate`, `creative`, `tech`, `elegant`, `playful`, `dark`, `colorful`

Ces style-cards sont actuellement des previews statiques — cliquer ne fait rien.

### Ce qui doit être implémenté

1. **Sélection active** : cliquer sur un style → état sélectionné (border colorée, check)
2. **Application au renderer** : chaque style = un mapping de tokens visuels
   - Injecter dans `sullivanRenderer` un `activeStyle` qui modifie les couleurs, borders, etc.
   - Les wireframes doivent refléter le style (ex: dark mode = fonds noirs, minimal = lignes fines)
3. **Persistance légère** : `sessionStorage` → le style reste choisi si on navigue entre sections
4. **Bouton "Appliquer" ou auto-apply** : décision UX à faire

### Format style-token

Le fichier `Frontend/3. STENCILER/static/design-bundles.json` existe déjà et contient
les bundles de design (vercel-like, minimal-light). C'est la base pour les 8 styles.

### Interaction avec Phase 3

Si Phase 3 est faite : le style choisi par l'utilisateur peut overrider les tokens extraits de l'upload
(l'upload donne une base, le style choice affine).

---

## PHASE 5 — UI Contextuel Complet (Cockpit Sullivan)
STATUS: BACKLOG
DÉPEND DE: Phase 2 + Phase 4
ACTOR: KIMI (mode -frd)

### Périmètre

Implémentation complète du "Dock Contextuel Glissant" (Gemini RECOMMANDATION_UI_STENCILER).
Refonte du viewer vers une architecture 4 zones.

### Architecture Cockpit Sullivan

```
┌─────────────────────────────────────────────────────────┐
│  TABS (brainstorm / backend / frontend / deploy)         │
├──────────┬──────────────────────────────┬───────────────┤
│  LEFT    │         CENTER               │  RIGHT        │
│ Genome   │      Fabric.js Canvas        │  Inspection   │
│ Tree     │  (composants N actif)        │  (propriétés  │
│ (N0→N3)  │  drag-and-drop               │   du sélect.) │
│          │  double-clic = drill down    │               │
│          │  breadcrumb intégré          │               │
├──────────┴──────────────────────────────┴───────────────┤
│  BOTTOM — Dock N+1 (composants enfants disponibles)      │
│  [ Corps ]  [ Organe 1 ]  [ Organe 2 ]  [ + Ajouter ]   │
└─────────────────────────────────────────────────────────┘
```

### Comportement Drill-down Cockpit

```
Niveau canvas N0 (Corps) → Dock = liste des N1 (Organes) du corpus actif
Niveau canvas N1 (Organe) → Dock = liste des N2 (Cellules) de cet organe
Niveau canvas N2 (Cellule) → Dock = liste des N3 (Atomes) de cette cellule
Double-clic canvas → entre dans le composant cliqué
Breadcrumb → retour au niveau parent
```

### Différence avec Phase 2 drill-down

Phase 2 = filtrage DOM simple (show/hide sections) → rapide, sans refonte
Phase 5 = vrai canvas interactif Fabric.js → drag, drop, resize, annotations

### Dépendance Fabric.js

Fabric.js n'est PAS actuellement dans le projet. À ajouter via CDN (no npm pour garder la légèreté).
Version recommandée : Fabric.js 5.x (stable) ou 6.x (si Canvas API 2025).

---

## PHASE 6 — Render Final en Local
STATUS: BACKLOG
DÉPEND DE: Phase 4 (styles) + Phase 5 (cockpit, optionnel)

### Périmètre

La finalité de Sullivan : prendre le genome + le style choisi → générer les fichiers
HTML/CSS/JS du projet final, téléchargeables et déployables.

### Workflow cible

```
1. Genome validé (Phase 1-2 : composants sélectionnés)
2. Style choisi (Phase 4 : un des 8 styles, ou tokens issus de l'upload Phase 3)
3. Clic "Générer le projet"
4. Backend génère les fichiers :
   - index.html + components/ + assets/ + styles/
5. ZIP téléchargeable ou déploiement direct (Vercel, local)
```

### Sortie attendue

```
project_output/
├── index.html
├── styles/
│   └── main.css  (tokens du style choisi appliqués)
├── components/
│   ├── corps_brainstorm.html
│   ├── organe_ir.html
│   └── ...
└── assets/
    └── (images, icons si upload Phase 3)
```

### Notes

- Le serveur `server_9998_v2.py` est PRISTINE — ne pas le modifier
- Créer un nouvel endpoint dans un `server_generator.py` séparé si besoin
- Ou : génération côté client (JS) et download via `Blob + createObjectURL`

---

## Récapitulatif des Phases

| Phase | Titre | Dépend de | Priorité estimée |
|-------|-------|-----------|-----------------|
| 1 | Wireframes Sullivan | — | ✅ ARCHIVÉ |
| 2 | Drill-down + Précision visuelle | Phase 1 | 🔥 EN COURS |
| 3 | Upload + Fulfillement auto | Phase 2 | Haute |
| 4 | Adaptation 8 styles | Phase 2 | Haute |
| 5 | Cockpit Sullivan (Fabric.js) | Phase 2+4 | Moyenne |
| 6 | Render final en local | Phase 4+5 | Basse (aboutissement) |
