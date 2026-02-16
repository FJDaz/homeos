# Architecture de Séparation des Rôles : Claude (Backend) ↔ KIMI (Frontend)

**Date** : 11 février 2026
**Auteur** : Claude (Backend Lead)
**Contexte** : Échecs répétés de KIMI sur l'intégration du Stenciler → Nécessité de redéfinir les frontières

---

## 🎯 Problème identifié

KIMI et Claude se marchent dessus parce qu'il n'existe **aucune frontière claire** entre :
- La **logique métier** (territoire Claude)
- Le **rendu visuel** (territoire KIMI)

Le fichier `server_9998_v2.py` actuel est un **monolithe** : il mélange génération HTML, logique de hiérarchie genome, et absence totale de gestion d'état.

**Conséquence** : KIMI essaie de fusionner des logiques incompatibles (HTML collapsible vs Canvas Fabric.js), casse tout, crée des fichiers dupliqués qui ne s'intègrent pas.

---

## 🏛️ Principe architectural

```
┌─────────────────────────────────────────────────────────────┐
│                    KIMI (Frontend)                          │
│  HTML + CSS + Fabric.js + HTMX                              │
│  Reçoit JSON, rend visuellement, capture events             │
└──────────────────┬──────────────────────────────────────────┘
                   │ REST API (JSON pur)
┌──────────────────▼──────────────────────────────────────────┐
│              Flask Server (Orchestrateur)                    │
│  Routes : /api/genome, /api/modifications, etc.             │
└──────────────────┬──────────────────────────────────────────┘
                   │
     ┌─────────────┼─────────────┬──────────────┬─────────────┐
     │             │             │              │             │
┌────▼────┐ ┌─────▼─────┐ ┌────▼─────┐ ┌──────▼──────┐ ┌───▼────┐
│ Genome  │ │   Corps   │ │DrillDown │ │ Component   │ │  Tool  │
│  State  │ │ Hierarchy │ │ Manager  │ │Contextualizer│ │Registry│
│ Manager │ │           │ │          │ │             │ │        │
└─────────┘ └───────────┘ └──────────┘ └─────────────┘ └────────┘
     │             │             │              │             │
     └─────────────┴─────────────┴──────────────┴─────────────┘
                              │
                    ┌─────────▼─────────┐
                    │  Persistance      │
                    │  Cache/LocalStorage│
                    │  (+ Base future)  │
                    └───────────────────┘
```

---

## 🧠 Territoire Claude (Backend/Logique)

### Classes d'abstraction nécessaires

#### 1. `GenomeStateManager` ⭐ Priorité 1

**Responsabilité** : Gestion de l'état du genome en cours de modification

**Données** :
- JSON de modifs (delta par rapport au genome de référence)
- Historique immutable des changements

**Persistance** :
- Cache → localStorage → Base (si nécessaire)

**API** :
```python
class GenomeStateManager:
    def apply_modification(self, path: str, property: str, value: Any) -> ModificationResult
    def get_modified_genome(self) -> Dict
    def rollback_to(self, snapshot_id: str) -> bool
    def save_checkpoint(self) -> str
    def get_history(self, since: Optional[datetime] = None) -> List[Modification]
```

**Exemple d'usage** :
```python
manager = GenomeStateManager("genome_20250211_v1")
result = manager.apply_modification(
    path="n0[0].n1[2]",
    property="border_color",
    value="#FF5733"
)
# → Valide, enregistre dans JSON Modifs, retourne le nœud mis à jour
```

---

#### 2. `CorpsHierarchy` (ou `GenomeStructure`) ⭐ Priorité 2

**Responsabilité** : Typologie des objets graphiques (Corps → Organes → Cells → Atomset)

**Mapping** : Chaque niveau a ses propres règles de composition

**API** :
```python
class CorpsHierarchy:
    def get_node(self, path: str) -> GraphicNode
    def get_children(self, path: str, level: Optional[int] = None) -> List[GraphicNode]
    def validate_modification(self, node: GraphicNode, property: str, value: Any) -> ValidationResult
    def get_modifiable_properties(self, node: GraphicNode) -> List[str]
```

**Validation métier** :
- Un atomset SVG icon ne peut pas avoir sa couleur de fond modifiée
- Un Corps ne peut pas avoir plus de 12 organes (exemple)
- Certaines propriétés sont read-only selon le niveau

---

#### 3. `DrillDownManager` ⭐ Priorité 3

**Responsabilité** : Gestion des niveaux de profondeur (n0 → n1 → n2 → n3)

**Trigger** : Double-clic, navigation via breadcrumb

**API** :
```python
class DrillDownManager:
    def enter_level(self, node_id: str, target_level: int) -> DrillDownContext
    def exit_level(self) -> DrillDownContext
    def get_current_context(self) -> DrillDownContext
    def get_breadcrumb(self) -> List[BreadcrumbItem]
```

**DrillDownContext** contient :
- Le nœud actuel
- Les composants contextuels disponibles
- Le niveau de profondeur
- Les outils applicables

---

#### 4. `ComponentContextualizer` ⭐ Priorité 3

**Responsabilité** : Propose les composants selon le niveau de drill-down et le contexte

**Logique** : Tier 1 (cache) → Tier 2 (adaptation) → Tier 3 (generation)

**API** :
```python
class ComponentContextualizer:
    def get_available_components(
        self,
        level: int,
        context: Dict,
        style: str
    ) -> List[Component]

    def adapt_component(
        self,
        component_id: str,
        modifs: Dict
    ) -> Component

    def get_tier_for_component(self, component_id: str) -> int  # 1, 2, ou 3
```

**Stratégie de chargement** :
- **Tier 1** : 66 composants Elite pré-générés (cache, 0ms)
- **Tier 2** : Adaptation légère via LLM (< 100ms)
- **Tier 3** : Génération from scratch (1-5s)

---

#### 5. `ToolRegistry` ⭐ Priorité 4

**Responsabilité** : Gestion extensible des outils (color picker, border slider, gradient, etc.)

**Extensibilité** : Ajouter un nouvel outil sans toucher au reste du code

**API** :
```python
class Tool:
    id: str
    name: str
    icon: str
    applicable_to: List[str]  # ['Corps', 'Organe', 'Cell']

    def render_config(self) -> Dict  # Config JSON pour KIMI
    def validate_value(self, value: Any) -> bool
    def apply(self, target: GraphicNode, value: Any) -> bool

class ToolRegistry:
    def register_tool(self, tool: Tool)
    def get_tools_for_context(self, node_type: str) -> List[Tool]
    def apply_tool(self, tool_id: str, target: str, params: Dict) -> ToolResult
```

**Outils de base** :
- `ColorPicker` : Couleurs de fond, texte, border
- `BorderSlider` : Épaisseur 0-10px
- `SpacingTool` : Padding/margin
- `TypographyTool` : Font family, size, weight
- `GradientPicker` (futur)

---

#### 6. `PNGSegmentationEngine` (Futur)

**Responsabilité** : Analyse d'image uploadée → Attributs Tailwind CSS

**Output** : JSON structuré avec les zones détectées et leurs propriétés

**API** :
```python
class PNGSegmentationEngine:
    def analyze_upload(self, image_path: str) -> SegmentationResult
    def map_to_tailwind(self, segment: Segment) -> Dict[str, str]
    def generate_genome_from_segments(
        self,
        segments: List[Segment]
    ) -> Dict  # Genome JSON
```

**Techno envisagée** :
- OpenCV pour la segmentation basique
- Vision LLM (GPT-4V, Claude 3.5) pour interprétation sémantique
- Mapping vers classes Tailwind CSS

---

## 🎨 Territoire KIMI (Frontend/Rendu)

### Logique Layout sanctuarisée

Ce que KIMI gère **sans que Claude s'en mêle** :

| Domaine | Exemples |
|---------|----------|
| **CSS** | Positionnement, flexbox, grid, transitions, animations |
| **Fabric.js** | Manipulation canvas, drag & drop, sélection visuelle |
| **HTMX** | Déclenchement des appels API, mise à jour partielle du DOM |
| **Event Handlers** | Click, double-click, drag, drop, hover |
| **Visual Feedback** | Hover states, selected borders, active tool highlight |
| **Responsive** | Adaptation mobile, sidebar collapse, breakpoints |

### Le contrat d'interface : REST API pure

KIMI consomme des **endpoints REST** qui retournent du **JSON structuré** :

```
GET  /api/genome/:id                          → JSON du genome complet
GET  /api/corps/:id                           → Détails d'un Corps
GET  /api/corps/:id/organes                   → Liste des organes d'un Corps
POST /api/modifications                       → Applique une modif, retourne delta
GET  /api/components/contextual/:level        → Composants disponibles
GET  /api/tools/:node_type                    → Outils disponibles
POST /api/drilldown/enter                     → Entre dans un niveau
POST /api/drilldown/exit                      → Sort d'un niveau
GET  /api/breadcrumb                          → Breadcrumb actuel
POST /api/snapshot                            → Crée un checkpoint
```

**KIMI reçoit du JSON, rend du HTML/CSS/JS. Point.**

---

## 📄 Le JSON Modifs : Pivot central

C'est **le seul objet partagé** entre Claude et KIMI. Il doit être **parfaitement défini**.

### Structure proposée

```json
{
  "genome_id": "genome_20250211_v1",
  "base_snapshot": "hash_du_genome_original",
  "user_session_id": "session_xyz",
  "created_at": "2026-02-11T14:30:00Z",
  "last_modified": "2026-02-11T14:35:15Z",
  "modifications": [
    {
      "id": "mod_001",
      "timestamp": "2026-02-11T14:32:00Z",
      "path": "n0[0].n1[2]",
      "operation": "style_change",
      "property": "border_color",
      "old_value": "#000000",
      "new_value": "#FF5733",
      "user_action": "color_picker"
    },
    {
      "id": "mod_002",
      "timestamp": "2026-02-11T14:33:15Z",
      "path": "n0[1].n1[0].n2[3]",
      "operation": "component_swap",
      "old_component_id": "button_primary",
      "new_component_id": "button_ghost",
      "user_action": "drag_drop"
    },
    {
      "id": "mod_003",
      "timestamp": "2026-02-11T14:35:00Z",
      "path": "n0[0]",
      "operation": "layout_change",
      "property": "organes_order",
      "old_order": [0, 1, 2, 3],
      "new_order": [2, 0, 1, 3],
      "user_action": "reorder_canvas"
    },
    {
      "id": "mod_004",
      "timestamp": "2026-02-11T14:36:20Z",
      "path": "n0[0].n1[1]",
      "operation": "delete",
      "deleted_node": { /* sauvegarde complète du nœud */ },
      "user_action": "delete_button"
    }
  ]
}
```

### Règles du JSON Modifs

1. **Historique immutable** : On n'efface jamais, on ajoute
2. **Path standardisé** : `n0[i].n1[j].n2[k].n3[l]`
3. **Operations typées** :
   - `style_change` : Modification d'une propriété visuelle
   - `component_swap` : Remplacement d'un composant
   - `layout_change` : Réorganisation spatiale
   - `delete` : Suppression d'un nœud
   - `duplicate` : Duplication d'un nœud
   - `insert` : Ajout d'un nouveau nœud
4. **Rollback possible** : Rejouer l'historique jusqu'à un timestamp donné
5. **User action tracking** : Permet d'analyser les patterns d'usage

---

## 🚧 Frontière critique : Qui décide quoi ?

### Territoire sanctuarisé KIMI

| Concept | Exemple | Qui décide ? |
|---------|---------|--------------|
| **Structure HTML** | `<div class="corps">` vs `<section>` | KIMI |
| **Classes Tailwind** | `bg-blue-500` vs `bg-blue-600` | KIMI (sauf modif user) |
| **Agencement Canvas** | Position x/y des objets Fabric.js | KIMI (puis persisté par Claude) |
| **Animations** | Transition entre drill-down levels | KIMI |
| **Event binding** | `onclick="selectCorps(id)"` | KIMI |
| **Layout responsive** | Sidebar collapse, mobile breakpoints | KIMI |

### Territoire sanctuarisé Claude

| Concept | Exemple | Qui décide ? |
|---------|---------|--------------|
| **Quel Corps afficher** | Liste des 4 Corps à rendre | Claude (via `GenomeStateManager`) |
| **Quels organes dans un Corps** | Structure hiérarchique | Claude (via `CorpsHierarchy`) |
| **Quels composants proposer** | Tier 1/2/3 selon contexte | Claude (via `ComponentContextualizer`) |
| **Validation des modifs** | "Peut-on changer la couleur ici ?" | Claude (règles métier) |
| **Persistance** | Sauvegarder dans cache/localStorage/base | Claude (via `GenomeStateManager`) |
| **Tier de chargement** | Cache vs adaptation vs generation | Claude (via `ComponentContextualizer`) |

---

## 🎬 Workflow idéal

### Scénario : User change la couleur d'un border

1. **KIMI** : User clique sur color picker dans la sidebar, sélectionne `#FF5733`
2. **KIMI** :
   ```javascript
   fetch('/api/modifications', {
     method: 'POST',
     body: JSON.stringify({
       path: 'n0[0].n1[2]',
       operation: 'style_change',
       property: 'border_color',
       value: '#FF5733'
     })
   })
   ```
3. **Claude** :
   - `GenomeStateManager.apply_modification()` est appelé
   - Validation via `CorpsHierarchy.validate_modification()`
   - Enregistrement dans JSON Modifs
   - Retourne `{success: true, updated_node: {...}}`
4. **KIMI** :
   - Reçoit le JSON de confirmation
   - Met à jour le canvas Fabric.js avec la nouvelle couleur
   - Déclenche une animation de feedback visuel (pulse, glow)
5. **Persistance** : Claude sauvegarde dans localStorage en background

**Aucun CSS n'a été touché côté backend. Aucun JSON n'a été construit côté frontend.**

---

### Scénario : User fait un drill-down (double-clic sur organe)

1. **KIMI** : User double-clique sur un organe `organe_002`
2. **KIMI** :
   ```javascript
   fetch('/api/drilldown/enter', {
     method: 'POST',
     body: JSON.stringify({
       node_id: 'n0[0].n1[2]',
       target_level: 2  // n2 = Cells
     })
   })
   ```
3. **Claude** :
   - `DrillDownManager.enter_level()` est appelé
   - Récupération des cells de cet organe via `CorpsHierarchy`
   - Récupération des composants contextuels via `ComponentContextualizer`
   - Récupération des outils applicables via `ToolRegistry`
   - Retourne :
     ```json
     {
       "level": 2,
       "node": { /* organe complet */ },
       "children": [ /* liste des cells */ ],
       "components": [ /* composants tier 1/2 disponibles */ ],
       "tools": [ /* outils applicables aux cells */ ],
       "breadcrumb": [
         {"label": "Phase 1", "path": "n0[0]"},
         {"label": "Organe Header", "path": "n0[0].n1[2]"}
       ]
     }
     ```
4. **KIMI** :
   - Reçoit le contexte de drill-down
   - Anime la transition (zoom, fade)
   - Affiche les cells dans le canvas
   - Met à jour le breadcrumb
   - Rafraîchit la sidebar avec les nouveaux outils

---

## 🔧 Ce qui manque actuellement

### 1. Pas de séparation données/rendu

**Problème** : `server_9998_v2.py` génère directement du HTML dans `generate_html()`. C'est un monolithe.

**Solution** :
- `generate_html()` devient `render_template(genome_data: Dict)`
- Le genome_data est fourni par `GenomeStateManager.get_modified_genome()`

### 2. Pas de gestion d'état

**Problème** : Si l'user modifie un border, où ça va ? Nulle part. Pas de persistance.

**Solution** :
- `POST /api/modifications` appelle `GenomeStateManager.apply_modification()`
- Sauvegarde automatique dans localStorage
- Snapshot périodique dans cache

### 3. Pas de découplage tools

**Problème** : Pour ajouter un "Gradient Picker", il faut modifier tout le code.

**Solution** :
- `ToolRegistry` permet d'enregistrer des outils extensibles
- Chaque outil est une classe indépendante
- KIMI reçoit la config JSON de chaque outil et rend l'UI

### 4. Pas de validation métier

**Problème** : KIMI peut-il laisser l'user changer la couleur d'un atomset SVG icon ? Non. Mais qui décide ?

**Solution** :
- `CorpsHierarchy.validate_modification()` applique les règles métier
- L'API REST retourne `{success: false, error: "Property not modifiable"}` si invalide
- KIMI affiche une erreur visuelle (shake, red border)

### 5. Pas de composants contextuels

**Problème** : À chaque niveau de drill-down, quels composants proposer ? Actuellement, rien.

**Solution** :
- `ComponentContextualizer.get_available_components(level, context, style)` retourne la liste
- Tier 1/2/3 selon disponibilité dans le cache Elite

---

## 📋 Plan de migration

### Phase 1 : Définir le contrat (Durée : 1-2 jours)

- [ ] Documenter la structure exacte du JSON Modifs
- [ ] Lister tous les endpoints REST nécessaires
- [ ] Définir les types d'opérations supportées
- [ ] Créer un JSON Schema pour validation
- [ ] Partager avec KIMI pour validation du contrat

### Phase 2 : Implémenter les classes backend (Durée : 3-5 jours)

- [ ] `GenomeStateManager` (priorité 1)
  - [ ] Lecture/écriture JSON Modifs
  - [ ] Validation des modifications
  - [ ] Rollback vers snapshot
  - [ ] Tests unitaires
- [ ] `CorpsHierarchy` (priorité 2)
  - [ ] Parsing du genome JSON
  - [ ] Navigation dans l'arbre
  - [ ] Règles de validation métier
  - [ ] Tests unitaires
- [ ] `ComponentContextualizer` (priorité 3)
  - [ ] Intégration avec `component_library.py` existant
  - [ ] Logique Tier 1/2/3
  - [ ] Tests unitaires
- [ ] `DrillDownManager` (priorité 3)
  - [ ] Gestion de la pile de navigation
  - [ ] Contexte de drill-down
  - [ ] Tests unitaires
- [ ] `ToolRegistry` (priorité 4)
  - [ ] Enregistrement des outils de base
  - [ ] Validation des valeurs
  - [ ] Tests unitaires

### Phase 3 : Créer les endpoints REST (Durée : 2-3 jours)

- [ ] Route `/api/genome/:id`
- [ ] Route `/api/corps/:id/organes`
- [ ] Route `/api/modifications` (POST)
- [ ] Route `/api/components/contextual/:level`
- [ ] Route `/api/tools/:node_type`
- [ ] Route `/api/drilldown/enter` (POST)
- [ ] Route `/api/drilldown/exit` (POST)
- [ ] Route `/api/breadcrumb`
- [ ] Tests d'intégration

### Phase 4 : KIMI consomme les endpoints (Durée : 3-5 jours - KIMI Lead)

- [ ] Refactoring de `generate_html()` pour devenir un renderer
- [ ] Implémentation des event handlers qui appellent l'API REST
- [ ] Gestion du state côté frontend (optimistic updates)
- [ ] Integration avec Fabric.js canvas
- [ ] Tests end-to-end

### Phase 5 : Persistance et optimisations (Durée : 2-3 jours)

- [ ] Cache intelligent (Tier 1/2/3)
- [ ] localStorage pour les modifs en cours
- [ ] Compression du JSON Modifs si trop gros
- [ ] Base de données SQLite si volume explose
- [ ] Monitoring des performances

---

## ❓ Questions ouvertes pour débat avec KIMI

### 1. Format du path

**Option A** : `n0[0].n1[2]` (style Python array)
**Option B** : `phase_0/organe_2` (style REST path)
**Option C** : `n0.0.n1.2` (style dot notation)

👉 **Quel format KIMI préfère pour le parsing côté JS ?**

### 2. Optimistic updates

**Approche A** : KIMI met à jour le canvas immédiatement, puis rollback si l'API dit "non"
**Approche B** : KIMI attend la confirmation de l'API avant de mettre à jour

👉 **Quelle approche pour la meilleure UX ?**

### 3. Granularité des endpoints

**Option A** : Un seul endpoint générique `/api/modifications`
**Option B** : Endpoints spécialisés `/api/style`, `/api/layout`, `/api/components`

👉 **Quelle granularité pour la maintenabilité ?**

### 4. Gestion des conflits (future feature collaborative)

Si deux users modifient le même genome simultanément :
- **Option A** : Last write wins
- **Option B** : Operational Transform (complexe)
- **Option C** : Lock pessimiste (un seul user à la fois)

👉 **À considérer plus tard, mais architecture à prévoir ?**

### 5. Snapshot automatique

**Fréquence** :
- Toutes les N modifications ?
- Tous les X minutes ?
- Sur action user explicite uniquement ?

👉 **Quelle stratégie pour ne pas polluer le cache ?**

### 6. Format des composants retournés par l'API

**Option A** : HTML complet (prêt à insérer)
```json
{
  "id": "button_primary",
  "html": "<button class='bg-blue-500'>Click</button>"
}
```

**Option B** : Structure JSON (KIMI construit le HTML)
```json
{
  "id": "button_primary",
  "type": "button",
  "classes": ["bg-blue-500", "px-4", "py-2"],
  "content": "Click"
}
```

👉 **Quelle approche pour la flexibilité ?**

---

## 🎯 Résumé : Les 3 Règles d'Or

### Règle 1 : Frontière hermétique
- **Claude** = Cerveau (État, Validation, Persistance, Logique métier)
- **KIMI** = Mains (Rendu, Layout, Interactions, Feedback visuel)
- **JSON Modifs** = Contrat de communication

### Règle 2 : Aucun empiétement
- Aucun CSS dans les classes Claude
- Aucun `GenomeStateManager` dans le code KIMI
- Communication uniquement via REST API JSON

### Règle 3 : Single Source of Truth
- Le JSON Modifs est l'unique source de vérité
- Historique immutable
- Rollback possible à tout moment

---

## 📚 Annexes

### Exemple de classe `GraphicNode`

```python
from dataclasses import dataclass
from typing import List, Dict, Any, Optional

@dataclass
class GraphicNode:
    id: str
    level: int  # 0=Corps, 1=Organe, 2=Cell, 3=Atomset
    path: str   # n0[0].n1[2]
    type: str   # 'Corps', 'Organe', 'Cell', 'Atomset'
    properties: Dict[str, Any]
    children: List['GraphicNode']
    parent: Optional['GraphicNode'] = None

    def get_modifiable_properties(self) -> List[str]:
        """Retourne les propriétés modifiables selon le type."""
        base = ['border_color', 'border_width', 'background_color']
        if self.type == 'Atomset' and self.properties.get('is_svg_icon'):
            # Un icon SVG ne peut pas avoir de background
            return ['border_color', 'border_width']
        return base

    def validate_property_change(self, property: str, value: Any) -> bool:
        """Valide qu'une modification est autorisée."""
        if property not in self.get_modifiable_properties():
            return False
        # Validation de type, range, etc.
        return True
```

### Exemple d'endpoint Flask

```python
from flask import Flask, jsonify, request
from backend.sullivan.genome_state_manager import get_genome_state_manager

app = Flask(__name__)

@app.route('/api/modifications', methods=['POST'])
def apply_modification():
    data = request.json
    manager = get_genome_state_manager()

    result = manager.apply_modification(
        path=data['path'],
        property=data['property'],
        value=data['value']
    )

    if result.success:
        return jsonify({
            'success': True,
            'updated_node': result.node.to_dict(),
            'modification_id': result.modification_id
        })
    else:
        return jsonify({
            'success': False,
            'error': result.error_message
        }), 400
```

---

## 🎨 Interopérabilité Figma

### Objectif stratégique

Sullivan doit devenir **Figma-compatible** pour ouvrir l'écosystème :
- Import/Export de designs Figma → Sullivan
- Plugins Figma réutilisables
- Intégration avec workflows design existants

### 7. `FigmaInteropBridge` ⭐ Nouvelle priorité 2

**Responsabilité** : Bidirectionnalité Figma ↔ Sullivan

**API** :
```python
class FigmaInteropBridge:
    def import_figma_file(self, figma_file_url: str) -> Dict  # Genome JSON
    def export_to_figma(self, genome_id: str) -> FigmaExport  # JSON Figma compatible
    def map_figma_node_to_genome(self, figma_node: Dict) -> GraphicNode
    def map_genome_node_to_figma(self, genome_node: GraphicNode) -> Dict
    def sync_changes(self, figma_file_id: str, genome_id: str) -> SyncResult
```

**Mapping des concepts** :

| Figma | Sullivan | Mapping |
|-------|----------|---------|
| Frame | Corps (n0) | Container de plus haut niveau |
| Section | Organe (n1) | Groupement sémantique |
| Component Instance | Cell (n2) | Composant réutilisable |
| Layer | Atomset (n3) | Primitive graphique |
| Auto Layout | Tailwind classes | `flex`, `grid`, spacing |
| Variant | Style property | Minimal, Elegant, Corporate, etc. |
| Plugin | Tool (ToolRegistry) | Extension du stenciler |

**Format d'export Figma** :
```json
{
  "figma_version": "1.0",
  "nodes": [
    {
      "id": "0:1",
      "name": "Phase 1",
      "type": "FRAME",
      "sullivan_path": "n0[0]",
      "children": [
        {
          "id": "1:2",
          "name": "Header",
          "type": "SECTION",
          "sullivan_path": "n0[0].n1[0]",
          "layout": {
            "mode": "HORIZONTAL",
            "padding": {"top": 16, "right": 24, "bottom": 16, "left": 24}
          },
          "fills": [{"type": "SOLID", "color": {"r": 1, "g": 1, "b": 1, "a": 1}}],
          "strokes": [{"type": "SOLID", "color": {"r": 0, "g": 0, "b": 0, "a": 1}}],
          "strokeWeight": 2
        }
      ]
    }
  ]
}
```

**Import Figma → Sullivan** :
1. Parse le fichier Figma JSON via API Figma
2. Détecte la hiérarchie (Frame → Section → Component → Layer)
3. Mappe vers la structure Sullivan (n0 → n1 → n2 → n3)
4. Convertit les styles Figma → Classes Tailwind CSS
5. Génère un JSON Modifs initial avec le genome importé
6. Propose à l'user de choisir un style Sullivan (Minimal, Elegant, etc.)
7. Adapte les composants via `ComponentContextualizer` Tier 2/3

**Export Sullivan → Figma** :
1. Parcourt le genome JSON (avec les modifs appliquées)
2. Convertit chaque nœud en Frame/Section/Component Figma
3. Mappe les classes Tailwind → Propriétés Figma (fills, strokes, layout)
4. Génère un fichier JSON compatible avec l'API Figma
5. Upload via Figma REST API ou export en `.fig` local

**Synchronisation bidirectionnelle** :
- **Conflict resolution** : Si modifs simultanées Figma + Sullivan, proposer merge ou override
- **Versioning** : Garder un historique des syncs (snapshots côté Sullivan)
- **Selective sync** : Permettre de ne synchroniser que certains Corps/Organes

**Endpoints REST supplémentaires** :
```
POST /api/figma/import                   → Importe un fichier Figma
POST /api/figma/export/:genome_id        → Exporte vers Figma
POST /api/figma/sync/:genome_id          → Synchronise avec Figma
GET  /api/figma/mapping/:figma_node_id   → Mapping Figma ↔ Sullivan
```

**Contraintes techniques** :
- **Figma API** : Nécessite un access token Figma (OAuth)
- **Rate limiting** : Figma API a des limites (respecter les quotas)
- **Styles mapping** : Certains effets Figma (blur, shadows complexes) peuvent ne pas avoir d'équivalent Tailwind → fallback vers CSS custom

**Plugins Figma compatibles** :
- Les plugins Figma manipulant la structure des nodes peuvent fonctionner
- Les plugins modifiant les propriétés visuelles (couleurs, typographie) sont compatibles
- Possibilité de créer un **plugin Figma dédié** qui :
  - Exporte directement vers Sullivan depuis Figma
  - Permet de preview un design Figma avec les styles Sullivan
  - Synchronise en temps réel (WebSocket ?)

**Vision long terme** :
- Sullivan devient un **"Figma for code"** : Design visuel → Code production en un clic
- Workflow designer : Figma (maquette) → Sullivan (génération composants) → Export React/Vue/Tailwind
- Sullivan pourrait également devenir compatible avec **Penpot** (alternative open-source à Figma)

---

### Révision du Plan de migration avec Figma

#### Phase 2 bis : Figma Interoperability (après Phase 2)

- [ ] `FigmaInteropBridge` (nouvelle priorité 2)
  - [ ] Parser Figma JSON (nodes, styles, layout)
  - [ ] Mapper Figma → Sullivan (Frame → Corps, etc.)
  - [ ] Mapper Sullivan → Figma (GraphicNode → Figma nodes)
  - [ ] Convertir styles Figma → Tailwind CSS
  - [ ] Convertir classes Tailwind → Propriétés Figma
  - [ ] Gestion des access tokens Figma (OAuth)
  - [ ] Tests d'import/export avec vrais fichiers Figma
  - [ ] Sync bidirectionnelle avec conflict resolution

#### Endpoints Figma (Phase 3 bis)

- [ ] Route `/api/figma/import` (POST)
- [ ] Route `/api/figma/export/:genome_id` (POST)
- [ ] Route `/api/figma/sync/:genome_id` (POST)
- [ ] Route `/api/figma/mapping/:figma_node_id` (GET)
- [ ] Tests d'intégration avec Figma API

#### KIMI : UI pour Figma import/export (Phase 4 bis)

- [ ] Bouton "Import from Figma" dans le stenciler
- [ ] Modal pour entrer Figma file URL ou access token
- [ ] Prévisualisation du design importé avant validation
- [ ] Bouton "Export to Figma" pour exporter le genome actuel
- [ ] Indicateur de sync status (synced, conflicts, pending)

---

### Questions ouvertes supplémentaires pour Figma

#### 7. Stratégie de conversion Figma → Tailwind

**Problème** : Figma permet des valeurs arbitraires (padding: 17px), Tailwind est plus contraint (p-4 = 16px)

**Options** :
- **A** : Arrondir aux valeurs Tailwind les plus proches (17px → 16px)
- **B** : Utiliser les arbitrary values Tailwind (`p-[17px]`)
- **C** : Forcer l'user à choisir lors de l'import (assistant)

👉 **Quelle approche pour préserver la fidélité visuelle ?**

#### 8. Gestion des composants Figma non mappables

**Problème** : Un composant Figma complexe (ex: graphique interactif) n'a pas d'équivalent Sullivan

**Options** :
- **A** : Importer comme image PNG (fallback)
- **B** : Créer un placeholder avec un message "Non supporté"
- **C** : Proposer à l'user de mapper manuellement vers un composant Sullivan

👉 **Quelle UX pour les edge cases ?**

#### 9. Sync temps réel vs ponctuelle

**Approche A** : Sync ponctuelle sur action user (bouton "Sync with Figma")
**Approche B** : Sync temps réel via WebSocket (complexe, coûteux en API calls)
**Approche C** : Polling périodique (check toutes les N minutes si changements)

👉 **Quelle stratégie pour la collaboration designer ↔ developer ?**

---

**Document vivant** : À mettre à jour au fur et à mesure des décisions prises avec KIMI.

---

François-Jean Dazin
Boss @ Sullivan
Claude (Backend Lead)
