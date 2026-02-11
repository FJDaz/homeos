# Architecture Classes - Stenciler Sullivan

**Date** : 11 février 2026  
**Contexte** : Débat architecture entre KIMI (Frontend) et Backend (Python)  
**Objectif** : Définir la séparation des responsabilités entre logique métier et rendu

---

## 🎯 Principe Fondamental

**Sanctuarisation du Layout** : KIMI contrôle 100% du rendu visuel (CSS, HTML, animations).  
**Abstraction Métier** : Le backend fournit des données structurées, pas des instructions de présentation.

```
┌─────────────────────────────────────────────────────────────┐
│  FRONTEND (KIMI)                                            │
│  ├── CSS/Layout (SANCTUAIRE - intouchable par backend)      │
│  ├── HTML Sémantique                                        │
│  ├── Interactions DOM                                       │
│  └── Appels API vers backend                                │
└─────────────────────────┬───────────────────────────────────┘
                          │ HTTP/JSON
┌─────────────────────────┴───────────────────────────────────┐
│  BACKEND (Python)                                           │
│  ├── Classes Corps/Organe/Cellule/Atome                     │
│  ├── Gestionnaire de Cache & Persistance                    │
│  ├── Moteur de composants contextuels                       │
│  ├── Traducteur PNG → Attributs                             │
│  └── API REST (données pures, pas de CSS)                   │
└─────────────────────────────────────────────────────────────┘
```

---

## 📦 Classes Proposées

### 1. `CorpsEntity` (et équivalents Organe/Cellule/Atome)

**Rôle** : Représentation métier d'un niveau du genome avec son état courant.

```python
@dataclass
class CorpsEntity:
    id: str                    # "n0_frontend"
    name: str                  # "Frontend"
    color: str                 # Couleur thématique (pas CSS !)
    confidence: float          # 0.0 - 1.0
    
    # Structure hiérarchique
    organes: List[OrganeEntity]
    
    # État modifiable par l'utilisateur
    modifications: ModificationLog
    
    # Métadonnées
    visual_hint: str           # "design", "backend", etc.
    tier: int                  # 1, 2 ou 3 (stratégie hybride)
    
    def apply_modification(self, mod: UserModification):
        """Applique une modif et la journalise"""
        self.modifications.add(mod)
        self.tier = self._recalculate_tier()
    
    def to_preview_dict(self) -> dict:
        """Sérialisation légère pour preview 20%"""
        return {
            "id": self.id,
            "name": self.name,
            "color": self.color,
            "organes_count": len(self.organes),
            "preview_organes": [o.name for o in self.organes[:3]]
        }
```

**Front reçoit** : `{"id": "n0_frontend", "name": "Frontend", "color": "#ec4899", ...}`  
**Front fait** : Applique son CSS avec cette couleur.

---

### 2. `ModificationLog` & `UserModification`

**Rôle** : Traçabilité immuable des changements (pattern Event Sourcing light).

```python
@dataclass
class UserModification:
    timestamp: datetime
    user_id: str
    target_id: str           # "n0_frontend"
    target_level: str        # "corps", "organe", "cellule", "atome"
    
    # Type de modification
    action: str              # "color_change", "border_resize", "position_move", 
                             # "component_select", "tier_upgrade", etc.
    
    # Payload spécifique à l'action
    payload: dict            # {"old": "#fff", "new": "#ec4899"}
    
    # Contexte
    session_id: str
    step: int                # Étape du parcours (8 pour Stenciler)

class ModificationLog:
    """Journal chronologique des modifications"""
    
    def __init__(self, storage: PersistenceLayer):
        self.storage = storage
        self._buffer: List[UserModification] = []
    
    def add(self, mod: UserModification):
        """Ajoute en mémoire (buffer)"""
        self._buffer.append(mod)
        
        # Flush si buffer trop gros ou temps écoulé
        if len(self._buffer) >= 10:
            self.flush()
    
    def flush(self):
        """Persiste le buffer"""
        self.storage.save_modifications(self._buffer)
        self._buffer.clear()
    
    def get_history(self, target_id: str) -> List[UserModification]:
        """Historique complet d'un élément"""
        return self.storage.load_history(target_id)
    
    def generate_delta_json(self) -> dict:
        """Génère le JSON Modifs pour export"""
        # Agrège toutes les modifications par target
        pass
```

**Persistance** : 
- Cache Redis/Memcached (court terme, sessions actives)
- JSON fichier (moyen terme, état de session)
- SQLite/Postgres (long terme, analytics, audit)

---

### 3. `ComponentContextEngine`

**Rôle** : Proposer les composants pertinents selon le contexte (drill-down level, style, etc.).

```python
@dataclass
class ContextQuery:
    level: str               # "corps", "organe", "cellule", "atome"
    parent_id: Optional[str] # ID du parent (pour organes d'un corps)
    style: str               # "minimal", "brutalist", etc.
    user_tier: int           # 1, 2 ou 3 (progression hybride)
    viewport: Optional[dict] # {"width": 1920, "height": 1080}

@dataclass  
class ComponentSuggestion:
    id: str
    name: str
    visual_hint: str
    elite_component_id: Optional[str]  # Référence à la librairie
    confidence_score: float            # Score de pertinence
    reason: str                        # Pourquoi ce composant ?

class ComponentContextEngine:
    """
    Moteur de suggestion contextuelle.
    Ne décide PAS du layout, juste de QUELS composants proposer.
    """
    
    def __init__(self, genome: Genome, elite_library: EliteLibrary):
        self.genome = genome
        self.elite = elite_library
        
        # Règles métier
        self.context_rules = {
            "corps": self._suggest_for_corps,
            "organe": self._suggest_for_organe,
            "cellule": self._suggest_for_cellule,
            "atome": self._suggest_for_atome
        }
    
    def suggest(self, query: ContextQuery) -> List[ComponentSuggestion]:
        """Retourne les composants pertinents pour ce contexte"""
        
        # 1. Récupérer les composants du genome pour ce niveau
        base_components = self._get_genome_components(query.level, query.parent_id)
        
        # 2. Scorer selon le style et le tier
        scored = []
        for comp in base_components:
            score = self._calculate_relevance(comp, query)
            elite_ref = self.elite.find_best_match(comp.visual_hint, query.style)
            
            scored.append(ComponentSuggestion(
                id=comp.id,
                name=comp.name,
                visual_hint=comp.visual_hint,
                elite_component_id=elite_ref.id if elite_ref else None,
                confidence_score=score,
                reason=f"Match {query.style} tier {query.user_tier}"
            ))
        
        # 3. Trier par score décroissant
        return sorted(scored, key=lambda x: x.confidence_score, reverse=True)
    
    def _calculate_relevance(self, component: Component, query: ContextQuery) -> float:
        """Algorithme de scoring contextuel"""
        score = 0.0
        
        # Score de base selon le tier
        if component.tier <= query.user_tier:
            score += 0.5
        
        # Score style (certains composants sont plus adaptés à certains styles)
        if component.style_affinity.get(query.style, 0) > 0.7:
            score += 0.3
        
        # Score popularité/historique
        score += component.usage_frequency * 0.2
        
        return min(score, 1.0)
```

**Front appelle** : `GET /api/components/suggest?level=organe&parent=n0_frontend&style=minimal`  
**Front reçoit** : Liste de suggestions avec IDs.  
**Front décide** : Comment les afficher (grille, liste, carousel...).

---

### 4. `DrillDownManager`

**Rôle** : Gérer les transitions entre niveaux et maintenir l'état cohérent.

```python
@dataclass
class DrillDownState:
    current_level: str       # "corps", "organe", "cellule", "atome"
    path: List[str]          # ["n0_frontend", "n1_layout", "n2_upload"]
    zoom_level: float        # 0.2 (preview), 0.33 (tarmac), 1.0 (drill), etc.
    selected_components: Set[str]

class DrillDownManager:
    """
    Gestionnaire de navigation drill-down.
    Maintient l'état et déclenche les chargements nécessaires.
    """
    
    def __init__(self, cache: CacheLayer, mod_log: ModificationLog):
        self.cache = cache
        self.mod_log = mod_log
        self.sessions: Dict[str, DrillDownState] = {}
    
    def enter_level(self, session_id: str, target_id: str) -> DrillDownResult:
        """
        Entrée dans un niveau (trigger par double-clic front).
        Retourne les données nécessaires pour ce niveau.
        """
        state = self.sessions.get(session_id, DrillDownState())
        
        # Déterminer le niveau cible
        target_level = self._detect_level(target_id)
        
        # Charger les données (lazy loading)
        data = self._load_level_data(target_id, target_level)
        
        # Mettre à jour le state
        state.current_level = target_level
        state.path.append(target_id)
        state.zoom_level = self._zoom_for_level(target_level)
        
        self.sessions[session_id] = state
        
        return DrillDownResult(
            level=target_level,
            entity=data,
            suggestions=self._get_suggestions(state),
            modifications=self.mod_log.get_recent(target_id)
        )
    
    def exit_level(self, session_id: str) -> DrillDownResult:
        """Remonte d'un niveau (bouton 'Out')"""
        state = self.sessions.get(session_id)
        if not state or len(state.path) <= 1:
            return None  # Déjà au top
        
        state.path.pop()
        parent_id = state.path[-1]
        parent_level = self._detect_level(parent_id)
        
        state.current_level = parent_level
        state.zoom_level = self._zoom_for_level(parent_level)
        
        return self.enter_level(session_id, parent_id)
    
    def _zoom_for_level(self, level: str) -> float:
        """Définit le zoom selon le niveau"""
        return {
            "corps": 0.33,      # Tarmac
            "organe": 0.6,      # Drill niveau 2
            "cellule": 0.8,     # Drill niveau 3
            "atome": 1.0        # Composant final
        }.get(level, 1.0)
```

---

### 5. `PNGSemanticAnalyzer`

**Rôle** : Convertir une image PNG uploadée en attributs sémantiques (pas CSS !).

```python
@dataclass
class SemanticAttributes:
    """
    Attributs extraits d'une image, indépendants de toute technologie.
    KIMI traduira ces attributs en CSS/Tailwind.
    """
    # Palette
    dominant_colors: List[ColorValue]  # [{"hex": "#3b82f6", "ratio": 0.45}]
    background_color: Optional[str]
    text_color: Optional[str]
    accent_color: Optional[str]
    
    # Layout
    layout_type: str           # "grid", "flex", "absolute", "mixed"
    density: str               # "compact", "normal", "airy"
    alignment: str             # "left", "center", "right", "justified"
    
    # Typographie
    font_family_category: str  # "sans", "serif", "mono", "display"
    font_weight_tendency: str  # "light", "normal", "bold", "heavy"
    font_size_scale: str       # "small", "normal", "large", "xlarge"
    
    # Composants détectés
    detected_patterns: List[str]  # ["cards", "sidebar", "navbar", "hero"]
    
    # Spatial
    zones: List[LayoutZone]    # Zones détectées avec leur type

@dataclass
class LayoutZone:
    x: float                   # 0.0 - 1.0 (relative)
    y: float
    width: float
    height: float
    type: str                  # "header", "content", "sidebar", "footer"
    confidence: float

class PNGSemanticAnalyzer:
    """
    Analyse une image et extrait des attributs sémantiques.
    NE génère PAS de CSS.
    """
    
    def __init__(self, vision_model):
        self.vision = vision_model  # Gemini Vision ou autre
    
    async def analyze(self, image_path: str) -> SemanticAttributes:
        """
        Pipeline d'analyse :
        1. Extraction couleurs (K-means clustering)
        2. Détection zones (YOLO ou similar)
        3. Analyse typographie (OCR + classification)
        4. Classification layout (CNN)
        """
        
        # Analyse par le modèle de vision
        raw_analysis = await self.vision.analyze(image_path)
        
        # Conversion en attributs sémantiques
        return self._normalize_to_attributes(raw_analysis)
    
    def _normalize_to_attributes(self, raw) -> SemanticAttributes:
        """Normalise la sortie brute du modèle"""
        
        # Extraction couleurs
        colors = self._extract_color_palette(raw)
        
        # Détection layout
        layout = self._classify_layout(raw)
        
        # Zones
        zones = self._detect_zones(raw)
        
        return SemanticAttributes(
            dominant_colors=colors,
            background_color=colors[0].hex if colors else None,
            text_color=self._infer_text_color(colors),
            layout_type=layout,
            zones=zones,
            # ... etc
        )
```

**Front reçoit** : `{"layout_type": "grid", "dominant_colors": [...], "zones": [...]}`  
**Front traduit** : Ces attributs en classes Tailwind ou CSS custom.

---

### 6. `ToolRegistry`

**Rôle** : Système extensible pour ajouter des outils à la sidebar sans modifier le core.

```python
@dataclass
class ToolDefinition:
    id: str
    name: str
    icon: str                    # Emoji ou nom d'icône
    category: str                # "color", "dimension", "action", "transform"
    
    # Payload envoyé au front quand l'outil est activé
    config: dict
    
    # Validation
    requires_selection: bool     # Nécessite un objet sélectionné ?
    allowed_levels: List[str]    # ["corps", "organe", "all"]

class ToolRegistry:
    """
    Registre des outils disponibles.
    KIMI demande la liste, le backend retourne les définitions.
    """
    
    def __init__(self):
        self._tools: Dict[str, ToolDefinition] = {}
        self._register_defaults()
    
    def _register_defaults(self):
        """Outils par défaut"""
        self.register(ToolDefinition(
            id="color_border",
            name="Couleur de bordure",
            icon="🎨",
            category="color",
            config={
                "type": "color_picker",
                "default": "#3b82f6",
                "palette": "default"
            },
            requires_selection=True,
            allowed_levels=["all"]
        ))
        
        self.register(ToolDefinition(
            id="border_width",
            name="Épaisseur",
            icon="📏",
            category="dimension",
            config={
                "type": "slider",
                "min": 0,
                "max": 10,
                "default": 2,
                "unit": "px"
            },
            requires_selection=True,
            allowed_levels=["all"]
        ))
        
        self.register(ToolDefinition(
            id="delete",
            name="Supprimer",
            icon="🗑️",
            category="action",
            config={
                "type": "button",
                "confirm": True,
                "shortcut": "Delete"
            },
            requires_selection=True,
            allowed_levels=["all"]
        ))
    
    def register(self, tool: ToolDefinition):
        """Enregistrer un nouvel outil (plugins futurs)"""
        self._tools[tool.id] = tool
    
    def get_for_context(self, level: str, has_selection: bool) -> List[ToolDefinition]:
        """Retourne les outils disponibles pour ce contexte"""
        
        available = []
        for tool in self._tools.values():
            # Vérifier niveau
            if "all" not in tool.allowed_levels and level not in tool.allowed_levels:
                continue
            
            # Vérifier sélection
            if tool.requires_selection and not has_selection:
                continue
            
            available.append(tool)
        
        return available
```

**Front demande** : `GET /api/tools?level=corps&has_selection=true`  
**Front reçoit** : Liste de ToolDefinition.  
**Front rend** : Les boutons/sliders/color pickers selon son propre design system.

---

### 7. `StencilerSession`

**Rôle** : Agrégateur principal, façade pour le front.

```python
class StencilerSession:
    """
    Facade exposant l'API au frontend.
    Orchestre tous les composants sans jamais parler de CSS.
    """
    
    def __init__(self, session_id: str, genome: Genome):
        self.session_id = session_id
        self.genome = genome
        
        # Composants
        self.corps_manager = CorpsEntityManager(genome)
        self.mod_log = ModificationLog(FileStorage())
        self.drill_down = DrillDownManager(Cache(), self.mod_log)
        self.component_engine = ComponentContextEngine(genome, EliteLibrary())
        self.tool_registry = ToolRegistry()
        self.png_analyzer = PNGSemanticAnalyzer(GeminiVision())
    
    # ========== API pour le Front ==========
    
    def get_corps_previews(self) -> List[dict]:
        """Retourne les 4 corps pour la bande de preview"""
        return [
            corps.to_preview_dict() 
            for corps in self.corps_manager.get_all()
        ]
    
    def select_style(self, style_id: str) -> dict:
        """Appelé quand l'utilisateur choisit un style"""
        # Enregistrer le choix
        self.mod_log.add(UserModification(
            target_id="session",
            action="style_selected",
            payload={"style": style_id}
        ))
        
        # Précharger les composants suggérés pour ce style
        suggestions = self.component_engine.suggest(ContextQuery(
            level="corps",
            style=style_id
        ))
        
        return {
            "status": "ok",
            "next_step": "stenciler",
            "suggested_components": [s.to_dict() for s in suggestions[:10]]
        }
    
    def drop_corps_on_canvas(self, corps_id: str, position: dict) -> dict:
        """Appelé quand un corps est droppé sur le canvas"""
        
        # Charger les détails (lazy)
        corps = self.corps_manager.load_full(corps_id)
        
        # Enregistrer l'action
        self.mod_log.add(UserModification(
            target_id=corps_id,
            target_level="corps",
            action="dropped_on_canvas",
            payload={"position": position}
        ))
        
        # Suggérer les organes à afficher
        organes = self.component_engine.suggest(ContextQuery(
            level="organe",
            parent_id=corps_id,
            style=self.get_selected_style()
        ))
        
        return {
            "corps": corps.to_detail_dict(),
            "organes": [o.to_dict() for o in organes],
            "modifications": self.mod_log.get_recent(corps_id)
        }
    
    def drill_down(self, target_id: str) -> dict:
        """Double-clic : entrer dans un niveau"""
        result = self.drill_down.enter_level(self.session_id, target_id)
        return result.to_dict()
    
    def apply_tool(self, tool_id: str, target_id: str, params: dict) -> dict:
        """Appliquer un outil de la sidebar"""
        
        # Vérifier que l'outil existe
        tool = self.tool_registry.get(tool_id)
        if not tool:
            return {"error": "Tool not found"}
        
        # Créer la modification
        mod = UserModification(
            target_id=target_id,
            action=tool_id,
            payload=params
        )
        
        # Appliquer et logger
        entity = self.corps_manager.get(target_id)
        entity.apply_modification(mod)
        self.mod_log.add(mod)
        
        return {
            "status": "modified",
            "entity": entity.to_dict(),
            "modification": mod.to_dict()
        }
    
    def analyze_upload(self, image_data: bytes) -> dict:
        """Analyser un template uploadé"""
        
        # Sauvegarder temporairement
        temp_path = self._save_temp(image_data)
        
        # Analyser
        attributes = self.png_analyzer.analyze(temp_path)
        
        # Enregistrer
        self.mod_log.add(UserModification(
            target_id="session",
            action="template_uploaded",
            payload={"attributes": attributes.to_dict()}
        ))
        
        return {
            "semantic_attributes": attributes.to_dict(),
            "suggested_style": self._infer_style_from_attributes(attributes)
        }
    
    def export_modifications(self) -> dict:
        """Génère le JSON Modifs final"""
        return self.mod_log.generate_delta_json()
```

---

## 🔌 API REST Proposée

```
GET  /api/session/init                    → Crée session, retourne ID
GET  /api/corps/previews                  → Liste 4 corps (preview)
POST /api/style/select                    → {style_id} → suggestions
GET  /api/tools?level=X&selection=Y       → Outils disponibles
POST /api/canvas/drop                     → {corps_id, position} → details
POST /api/drill/enter                     → {target_id} → niveau+1
POST /api/drill/exit                      → Remonte d'un niveau
POST /api/tool/apply                      → {tool_id, target_id, params}
POST /api/upload/analyze                  → {image} → attributs sémantiques
GET  /api/modifications/export            → JSON Modifs final
```

**Toutes les réponses** sont du JSON pur, sans aucune instruction CSS.

---

## 🚫 Territoire Sanctuarisé (KIMI only)

**Le backend NE DOIT JAMAIS** :
- Générer du CSS inline
- Parler de `display: flex`, `grid`, `margin`, `padding`
- Définir des breakpoints responsive
- Choisir des polices ou tailles de texte
- Positionner des éléments (x, y, z-index)
- Animer des transitions

**Le backend DOIT** :
- Donner des **intentions** ("ce corps est important")
- Fournir des **données** (nom, couleur thématique, structure)
- Sugérer des **relations** ("cet organe dépend de ce corps")
- Exposer des **actions possibles** ("peut être colorié", "peut être supprimé")

---

## 📁 Fichiers à Créer

```
Backend/Prod/sullivan/stenciler/
├── __init__.py
├── entities.py              # CorpsEntity, OrganeEntity, etc.
├── modifications.py         # ModificationLog, UserModification
├── context_engine.py        # ComponentContextEngine
├── drill_down.py            # DrillDownManager
├── png_analyzer.py          # PNGSemanticAnalyzer
├── tool_registry.py         # ToolRegistry, ToolDefinition
├── session.py               # StencilerSession (facade)
└── api.py                   # Routes FastAPI
```

---

## 💡 Recommandation de Mise en Œuvre

1. **Phase 1** : Implémenter `CorpsEntity` + `ModificationLog` (core)
2. **Phase 2** : Implémenter `StencilerSession` avec API mock
3. **Phase 3** : Connecter KIMI à l'API (remplacer les données statiques)
4. **Phase 4** : Ajouter `ComponentContextEngine` (suggestions intelligentes)
5. **Phase 5** : Ajouter `PNGSemanticAnalyzer` (upload)
6. **Phase 6** : Optimiser cache et persistance

---

**François-Jean Dazin**  
*Pour débat avec KIMI*
