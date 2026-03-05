# PLAN — Genome Design Bridge
## AetherFlow ↔ Illustrator ↔ Figma ↔ Web

**Auteur :** Claude + FJD
**Date :** 2026-03-02
**Statut :** DRAFT — à valider FJD

---

## Vision

```
AetherFlow génère le genome (QUOI + COMMENT ça fonctionne)
        ↓
Génère un SVG scaffold balisé (calques = IDs genome)
        ↓
Designer ouvre dans Illustrator → design libre → export SVG
        ↓
Import SVG dans Figma (natif, drag & drop)
        ↓
Plugin Figma : lit les layers → retrouve IDs genome → sync styles
              alerte si layer sans ID → "nouveau composant ?"
        ↓
AetherFlow reçoit les styles → génère le code HTML/CSS final
        ↓
Publication web (Railway / Vercel)
```

---

## Phase 1 — Genome → SVG scaffold

**Fichier :** `Backend/Prod/exporters/genome_to_svg.py`

**Ce que le script fait :**
- Lit `GET /api/genome`
- Génère un fichier SVG structuré par artboards N0 (phases)
- Chaque N1 organe = groupe SVG `<g id="n1_ir" data-genome-id="n1_ir">`
- Chaque N2 feature = sous-groupe `<g id="n2_auth">`
- Chaque N3 composant = rectangle étiqueté avec son `visual_hint`
- Les noms de calques = IDs genome (convention : préserver à l'import Illustrator)

**Format de sortie SVG :**
```xml
<svg xmlns="http://www.w3.org/2000/svg" width="1440" height="900">
  <!-- Phase: Onboarding -->
  <g id="n0_onboarding" class="af-phase">

    <!-- Organe: Interface Rapide -->
    <g id="n1_ir" class="af-organ" data-genome-id="n1_ir">
      <rect x="40" y="40" width="380" height="280" fill="#f7f6f2" rx="8"/>
      <text x="52" y="62" font-size="11" fill="#999">n1_ir / Interface Rapide</text>

      <!-- Feature: Authentification -->
      <g id="n2_auth" class="af-feature" data-genome-id="n2_auth">
        <rect x="52" y="72" width="356" height="80" fill="#ffffff" rx="4" stroke="#d5d4d0"/>

        <!-- Composant: Bouton Login -->
        <g id="n3_btn_login" class="af-component" data-hint="button">
          <rect x="64" y="84" width="120" height="32" fill="#3d3d3c" rx="4"/>
          <text x="124" y="104" font-size="10" fill="white" text-anchor="middle">Login</text>
        </g>
      </g>
    </g>

  </g>
</svg>
```

**Convention calques pour Illustrator :**
- Illustrator préserve les IDs SVG comme noms de calques
- Convention stricte : NE PAS renommer les calques `af-*`
- Les sous-calques peuvent être renommés librement (labels cosmétiques)
- L'ID SVG = lien genome. Tant que l'ID est là, le bridge fonctionne.

**Script de génération :**
```bash
python Backend/Prod/exporters/genome_to_svg.py --output exports/genome_scaffold.svg
```

**Endpoint serveur :**
```
GET /api/export/svg  →  télécharge genome_scaffold.svg
```

---

## Phase 2 — Plugin Figma

**Fichier :** `figma-plugin/` (nouveau dossier)

```
figma-plugin/
  manifest.json
  ui.html          ← interface du plugin (panel Figma)
  code.js          ← logique plugin (accès document Figma)
```

### 2A — Import : Genome → Figma

Le plugin lit le genome depuis AetherFlow et crée les frames Figma directement (sans SVG intermédiaire) :

```javascript
// code.js — création des frames depuis le genome
async function importGenome() {
  const genome = await fetch('http://localhost:9998/api/genome').then(r => r.json());

  for (const phase of genome.n0_phases) {
    const page = figma.createPage();
    page.name = phase.name;

    for (const organ of phase.n1_sections) {
      const frame = figma.createFrame();
      frame.name = organ.id;                    // ID genome = nom layer
      frame.setPluginData('genomeId', organ.id); // metadata persistante
      frame.setPluginData('genomeName', organ.name);
      // layout, taille par défaut...
      page.appendChild(frame);
    }
  }
}
```

### 2B — Alerte "hors genome"

Quand le designer ajoute un élément sans `pluginData.genomeId` :

```javascript
figma.on('documentchange', (event) => {
  for (const change of event.documentChanges) {
    if (change.type === 'CREATE') {
      const node = change.node;
      if (!node.getPluginData('genomeId')) {
        figma.notify(
          `"${node.name}" n'est pas dans le genome. Envoyer à AetherFlow ?`,
          { timeout: 8000, button: { text: 'Oui', action: () => requestNewFeature(node) } }
        );
      }
    }
  }
});

async function requestNewFeature(node) {
  await fetch('http://localhost:9998/api/genome/request-feature', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      name: node.name,
      visual_hint: guessHint(node),  // devine le type depuis la forme
      description: `Créé dans Figma par designer — ${new Date().toISOString()}`
    })
  });
  node.setPluginData('genomeId', 'pending_' + node.id);
  figma.notify('Envoyé à AetherFlow ✓');
}
```

### 2C — Export : Figma → AetherFlow (styles)

Le plugin lit les styles de chaque frame taguée et envoie à AetherFlow :

```javascript
async function syncStylesToAetherFlow() {
  const styleMap = {};

  for (const page of figma.root.children) {
    for (const node of page.children) {
      const genomeId = node.getPluginData('genomeId');
      if (!genomeId || genomeId.startsWith('pending_')) continue;

      styleMap[genomeId] = {
        fills: node.fills,
        strokes: node.strokes,
        cornerRadius: node.cornerRadius,
        fontName: extractFont(node),
        opacity: node.opacity
      };
    }
  }

  await fetch('http://localhost:9998/api/styles/sync', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(styleMap)
  });

  figma.notify('Styles synchronisés avec AetherFlow ✓');
}
```

---

## Phase 3 — AetherFlow reçoit les styles → génère le code

**Endpoint :** `POST /api/styles/sync`

AetherFlow reçoit le styleMap, le convertit en CSS variables, et régénère les composants HTML avec les vrais styles :

```python
# server_9998_v2.py — nouveau endpoint
def handle_styles_sync(self, body):
    styles = json.loads(body)
    style_map = {}

    for genome_id, figma_styles in styles.items():
        style_map[genome_id] = {
            'bg': figma_color_to_css(figma_styles.get('fills')),
            'border': figma_color_to_css(figma_styles.get('strokes')),
            'radius': figma_styles.get('cornerRadius', 0),
            'font': figma_styles.get('fontName', {}).get('family', 'inherit'),
            'opacity': figma_styles.get('opacity', 1)
        }

    # Sauvegarder dans styles.json
    styles_path = os.path.join(DATA_DIR, 'styles.json')
    existing = load_json(styles_path)
    existing.update(style_map)
    save_json(styles_path, existing)

    return {'status': 'ok', 'updated': len(style_map)}
```

**Endpoint :** `GET /api/styles/{genome_id}`
→ Retourne les styles CSS pour un nœud donné

**Endpoint :** `POST /api/genome/request-feature`
→ Crée un nouveau nœud genome pending depuis Figma

---

## Fichiers à créer

| Fichier | Rôle | Délai |
|---|---|---|
| `Backend/Prod/exporters/genome_to_svg.py` | Génère SVG scaffold pour Illustrator | J1 |
| `figma-plugin/manifest.json` | Config plugin Figma | J1 |
| `figma-plugin/ui.html` | UI panel plugin (boutons Import/Export/Sync) | J2 |
| `figma-plugin/code.js` | Logique plugin (import genome, alerte, export styles) | J2-J3 |
| `server_9998_v2.py` → `GET /api/export/svg` | Endpoint téléchargement SVG | J1 |
| `server_9998_v2.py` → `POST /api/styles/sync` | Réception styles depuis Figma | J2 |
| `server_9998_v2.py` → `POST /api/genome/request-feature` | Nouveau nœud depuis Figma | J2 |
| `Backend/Prod/core/style_engine.py` | Converts Figma styles → CSS | J3 |

---

## Workflow designer (ce qu'ils font concrètement)

### Option A — Figma natif
1. Ouvrir Figma → installer plugin AetherFlow
2. Plugin → "Importer genome" → frames créées automatiquement
3. Designer librement dans les frames
4. Plugin → "Sync vers AetherFlow" → styles envoyés
5. `GET /preview` → voir le rendu

### Option B — Illustrator first
1. `GET /api/export/svg` → télécharger `genome_scaffold.svg`
2. Ouvrir dans Illustrator → design libre (garder les noms de calques `af-*`)
3. Exporter SVG → drag dans Figma
4. Plugin AetherFlow → "Lire layers" → retrouve les IDs
5. Suite identique à Option A étapes 4-5

---

## Ce que ça change pour AetherFlow

AetherFlow devient **bi-couche** :
- Couche sémantique (genome) — déjà là ✅
- Couche visuelle (styles.json depuis Figma) — à ajouter

Le générateur de code final lit les deux :
```python
genome_node + styles[genome_node.id] → composant HTML stylisé
```

---

## Prochaine étape immédiate

**Commencer par Phase 1** — `genome_to_svg.py` + endpoint `GET /api/export/svg`.

C'est le plus rapide (~4h), ça valide la convention de nommage calques, et ça permet de tester l'import Illustrator → Figma immédiatement.
