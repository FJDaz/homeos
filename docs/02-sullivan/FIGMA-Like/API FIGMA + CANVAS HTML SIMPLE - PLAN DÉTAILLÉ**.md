# **OPTION 3 : API FIGMA + CANVAS HTML SIMPLE - PLAN DÉTAILLÉ**

## **ARCHITECTURE GLOBALE**

```
┌─────────────────────────────────────────────────────────────┐
│                      INTERFACE UTILISATEUR                   │
│  ┌───────────┐ ┌──────────────────────────┐ ┌───────────┐  │
│  │ PALETTE   │ │     CANVAS HTML          │ │ PROPRIÉTÉS│  │
│  │ HomeOS    │ │    (divs stylés)         │ │ Tailwind  │  │
│  │ Éléments  │ │   ┌────────────┐         │ │ + HTMX    │  │
│  │ prédéfinis│ │   │ <div>      │         │ │           │  │
│  │           │ │   │  Bouton    │         │ │           │  │
│  └───────────┘ │   └────────────┘         │ └───────────┘  │
└─────────────────────────────────────────────────────────────┘
         │                    │                      │
         ▼                    ▼                      ▼
┌─────────────────────────────────────────────────────────────┐
│                BRIDGE HOMEOS ↔ FIGMA (API)                  │
│  ┌────────────────────┐  ┌────────────────────┐            │
│  │   Cache Local      │  │   Sync Manager     │            │
│  │  État HomeOS       │  │  Envoi différé à   │            │
│  │                    │  │    Figma API       │            │
│  └────────────────────┘  └────────────────────┘            │
└─────────────────────────────────────────────────────────────┘
                                       │
                                       ▼
                                ┌──────────────┐
                                │  FIGMA API   │
                                │  (Backend)   │
                                └──────────────┘
```

---

## **PHASE 1 : INFRASTRUCTURE DE BASE (SEMAINE 1)**

### **1.1. Authentification Figma**
```python
# config/figma.py
class FigmaClient:
    def __init__(self):
        self.token = os.getenv("FIGMA_TOKEN")
        self.base_url = "https://api.figma.com/v1"
        
    async def get_file(self, file_key: str):
        """Récupère un fichier Figma"""
        response = await self._request(f"/files/{file_key}")
        return self._parse_figma_structure(response)
    
    async def update_node(self, file_key: str, node_id: str, updates: dict):
        """Met à jour un node dans Figma (écriture)"""
        # Note: L'API d'écriture est en beta, fallback possible
        pass
```

### **1.2. Modèle de données HomeOS**
```python
# models/homeos_elements.py
from enum import Enum

class HomeOSType(Enum):
    BUTTON = "button"
    INPUT = "input"
    CARD = "card"
    NAVBAR = "navbar"
    CONTAINER = "container"

class HomeOSElement:
    def __init__(self, element_id: str, element_type: HomeOSType):
        self.id = element_id
        self.type = element_type
        self.figma_node_id = None  # Lien vers le node Figma
        self.tailwind_classes = []
        self.hx_attributes = {}
        self.position = {"x": 0, "y": 0, "w": 100, "h": 50}
        self.content = ""
        
    def to_html(self) -> str:
        """Génère le HTML/HTMX correspondant"""
        if self.type == HomeOSType.BUTTON:
            return f'<button class="{" ".join(self.tailwind_classes)}" {self._format_hx_attrs()}>{self.content}</button>'
        # ... autres types
```

### **1.3. Interface Canvas HTML simple**
```html
<!-- templates/canvas.html -->
<div id="homeos-canvas" 
     class="relative w-full h-screen bg-gray-50 border-2 border-dashed border-gray-200">
     
  <!-- Éléments HomeOS rendus comme des divs simples -->
  <div v-for="element in elements" 
       :key="element.id"
       :id="'element-' + element.id"
       class="absolute border-2 border-blue-300 bg-white p-2 cursor-move"
       :style="{
         left: element.position.x + 'px',
         top: element.position.y + 'px',
         width: element.position.w + 'px',
         height: element.position.h + 'px'
       }"
       @mousedown="startDrag(element)">
       
    <!-- Contenu selon le type -->
    <div v-if="element.type === 'button'" 
         class="btn btn-primary w-full h-full flex items-center justify-center">
      {{ element.content || 'Button' }}
    </div>
    
    <!-- Poignées de redimensionnement -->
    <div class="resize-handle bottom-right" @mousedown="startResize(element, 'se')"></div>
  </div>
</div>
```

---

## **PHASE 2 : PALETTE D'ÉLÉMENTS HOMEOs (SEMAINE 2)**

### **2.1. Éléments prédéfinis avec mapping Figma**
```python
# data/homeos_components.py
HOMEOs_COMPONENTS = {
    "button": {
        "name": "Bouton HTMX",
        "figma_template": {
            "type": "RECTANGLE",
            "cornerRadius": 8,
            "fills": [{"type": "SOLID", "color": {"r": 0.29, "g": 0.56, "b": 1}}],
            "effects": [{"type": "DROP_SHADOW", "radius": 4}]
        },
        "default_tailwind": "px-4 py-2 rounded-lg bg-blue-600 text-white shadow hover:bg-blue-700",
        "required_hx": True,  # Doit avoir une action HTMX
        "default_content": "Click me"
    },
    
    "input": {
        "name": "Champ de saisie",
        "figma_template": {
            "type": "RECTANGLE",
            "fills": [{"type": "SOLID", "color": {"r": 1, "g": 1, "b": 1}}],
            "strokes": [{"type": "SOLID", "color": {"r": 0.88, "g": 0.88, "b": 0.88}}]
        },
        "default_tailwind": "border border-gray-300 rounded px-3 py-2",
        "hx_example": 'hx-get="/search" hx-trigger="keyup changed delay:500ms"',
        "placeholder": "Type here..."
    }
}
```

### **2.2. Interface palette**
```html
<!-- Palette latérale -->
<div id="homeos-palette" class="w-64 bg-white border-r border-gray-200 p-4">
  <h3 class="font-bold text-gray-700 mb-4">Éléments HomeOS</h3>
  
  <div class="space-y-2">
    <!-- Bouton -->
    <div class="palette-item" 
         draggable="true"
         data-type="button"
         @dragstart="dragStart($event, 'button')">
      <div class="flex items-center p-3 border rounded-lg hover:bg-gray-50">
        <div class="w-8 h-8 bg-blue-100 rounded flex items-center justify-center mr-3">
          <i data-lucide="square"></i>
        </div>
        <div>
          <div class="font-medium">Bouton HTMX</div>
          <div class="text-xs text-gray-500">Action + Style Tailwind</div>
        </div>
      </div>
    </div>
    
    <!-- Input -->
    <div class="palette-item" draggable="true" data-type="input">
      <!-- ... similaire ... -->
    </div>
  </div>
</div>
```

---

## **PHASE 3 : SYNC AVEC FIGMA (SEMAINE 3-4)**

### **3.1. Cache local pour performances**
```python
# bridge/local_cache.py
class HomeOSLocalCache:
    def __init__(self, figma_file_key: str):
        self.file_key = figma_file_key
        self.elements = {}  # id -> HomeOSElement
        self.figma_nodes = {}  # node_id -> raw Figma data
        self.modified = False
        
    def add_element(self, element: HomeOSElement) -> str:
        """Ajoute un élément dans le cache local"""
        element_id = f"homeos_{uuid.uuid4().hex[:8]}"
        element.id = element_id
        
        # Créer le node Figma correspondant
        figma_node = self._create_figma_node(element)
        figma_node_id = f"figma_{uuid.uuid4().hex[:8]}"
        
        # Lier les deux
        element.figma_node_id = figma_node_id
        self.elements[element_id] = element
        self.figma_nodes[figma_node_id] = figma_node
        self.modified = True
        
        return element_id
    
    async def sync_to_figma(self):
        """Synchronise les modifications avec Figma"""
        if not self.modified:
            return
            
        # Regrouper les updates pour minimiser les appels API
        updates = self._prepare_batch_updates()
        
        try:
            # Utiliser l'API beta d'écriture si disponible
            await self.figma_client.batch_update(
                file_key=self.file_key,
                updates=updates
            )
            self.modified = False
        except Exception as e:
            # Fallback: créer un nouveau fichier Figma
            await self._create_new_figma_file()
```

### **3.2. Mapper les styles Tailwind ↔ Figma**
```python
# bridge/style_mapper.py
class StyleMapper:
    # Mapping des propriétés Figma vers Tailwind
    FIGMA_TO_TAILWIND = {
        "cornerRadius": {
            "mapping": lambda r: f"rounded-{self._radius_to_class(r)}",
            "values": {0: "none", 2: "sm", 4: "md", 8: "lg", 16: "xl", 24: "2xl"}
        },
        "fills": {
            "mapping": self._color_to_bg_class,
            "color_map": {
                (0.29, 0.56, 1): "bg-blue-600",
                (0.16, 0.83, 0.58): "bg-emerald-500",
                (1, 1, 1): "bg-white"
            }
        },
        "fontSize": {
            "mapping": self._fontsize_to_text_class,
            "size_map": {12: "text-xs", 14: "text-sm", 16: "text-base"}
        }
    }
    
    def figma_to_tailwind(self, figma_node: dict) -> List[str]:
        """Convertit les styles Figma en classes Tailwind"""
        classes = []
        
        for prop, mapper in self.FIGMA_TO_TAILWIND.items():
            if prop in figma_node:
                tailwind_class = mapper["mapping"](figma_node[prop])
                if tailwind_class:
                    classes.append(tailwind_class)
        
        return classes
```

---

## **PHASE 4 : ÉDITION DES PROPRIÉTÉS (SEMAINE 5)**

### **4.1. Panneau de propriétés contextuel**
```html
<!-- Panneau de droite -->
<div id="properties-panel" class="w-80 bg-white border-l border-gray-200 p-6">
  <div v-if="selectedElement">
    <h3 class="font-bold text-lg mb-4">Propriétés</h3>
    
    <!-- Type d'élément -->
    <div class="mb-6">
      <label class="block text-sm font-medium text-gray-700 mb-2">Type</label>
      <div class="text-sm font-semibold text-blue-600">
        {{ selectedElement.type.toUpperCase() }}
      </div>
    </div>
    
    <!-- Contenu -->
    <div class="mb-4">
      <label class="block text-sm font-medium text-gray-700 mb-2">Texte</label>
      <input type="text" 
             v-model="selectedElement.content"
             @input="updateElementContent"
             class="w-full border rounded px-3 py-2">
    </div>
    
    <!-- Classes Tailwind -->
    <div class="mb-4">
      <label class="block text-sm font-medium text-gray-700 mb-2">
        Classes Tailwind
        <span class="text-xs text-gray-500">(séparées par des espaces)</span>
      </label>
      <textarea v-model="tailwindClassesString"
                @input="updateTailwindClasses"
                rows="3"
                class="w-full border rounded px-3 py-2 font-mono text-sm">
      </textarea>
      <div class="mt-2 text-xs text-gray-500">
        Classes détectées: {{ detectedClasses.join(', ') }}
      </div>
    </div>
    
    <!-- Attributs HTMX -->
    <div class="mb-6">
      <label class="block text-sm font-medium text-gray-700 mb-2">HTMX</label>
      <div class="space-y-3">
        <div class="flex items-center">
          <select v-model="hxMethod" class="border rounded px-2 py-1 mr-2">
            <option value="get">GET</option>
            <option value="post">POST</option>
            <option value="put">PUT</option>
          </select>
          <input type="text" 
                 v-model="hxUrl"
                 placeholder="/api/action"
                 class="flex-1 border rounded px-3 py-1">
        </div>
        <button @click="applyHX"
                class="text-sm bg-blue-100 text-blue-700 px-3 py-1 rounded">
          Appliquer hx-{{ hxMethod }}
        </button>
      </div>
    </div>
    
    <!-- Prévisualisation code -->
    <div class="mt-8 pt-6 border-t">
      <h4 class="font-medium text-gray-700 mb-2">Code généré</h4>
      <pre class="bg-gray-900 text-gray-100 p-4 rounded text-sm overflow-x-auto">
{{ generatedCode }}
      </pre>
      <button @click="copyCode"
              class="mt-2 text-sm bg-gray-800 text-white px-3 py-1 rounded">
        Copier le code
      </button>
    </div>
  </div>
  
  <div v-else class="text-gray-500 italic text-center py-12">
    Sélectionnez un élément pour éditer ses propriétés
  </div>
</div>
```

### **4.2. Mise à jour en temps réel**
```javascript
// frontend/canvas.js
class HomeOSCanvas {
  constructor() {
    this.selectedElement = null;
    this.elements = new Map();
    this.initEventListeners();
  }
  
  initEventListeners() {
    // Drag & drop depuis la palette
    document.addEventListener('dragover', (e) => e.preventDefault());
    document.addEventListener('drop', (e) => this.handleDrop(e));
    
    // Sélection d'éléments
    document.addEventListener('click', (e) => this.handleCanvasClick(e));
    
    // Redimensionnement
    this.initResizeHandles();
  }
  
  handleDrop(e) {
    e.preventDefault();
    const type = e.dataTransfer.getData('application/homeos-type');
    const rect = this.canvas.getBoundingClientRect();
    const x = e.clientX - rect.left;
    const y = e.clientY - rect.top;
    
    // Créer l'élément localement
    const element = this.createElement(type, x, y);
    
    // Envoyer au backend pour création dans Figma
    this.syncToBackend('create', element);
  }
  
  async syncToBackend(action, data) {
    // Envoi immédiat pour feedback
    this.updateUI(data);
    
    // Sync différée avec Figma
    setTimeout(async () => {
      try {
        const response = await fetch('/api/figma/sync', {
          method: 'POST',
          headers: {'Content-Type': 'application/json'},
          body: JSON.stringify({action, ...data})
        });
        
        if (response.ok) {
          console.log('Sync avec Figma réussi');
        }
      } catch (error) {
        console.warn('Sync Figma échoué (mode offline)', error);
        // On continue avec le cache local
      }
    }, 1000); // 1 seconde de délai
  }
}
```

---

## **PHASE 5 : IMPORT/EXPORT (SEMAINE 6)**

### **5.1. Import depuis Figma existant**
```python
# bridge/importer.py
class FigmaImporter:
    async def import_figma_file(self, file_key: str):
        """Importe un fichier Figma et propose des mappings"""
        
        # 1. Récupérer le fichier
        figma_data = await self.figma.get_file(file_key)
        
        # 2. Analyser la structure
        analysis = self.analyze_structure(figma_data)
        
        # 3. Proposer des mappings automatiques
        mappings = self.suggest_mappings(analysis)
        
        # 4. Interface pour validation utilisateur
        return {
            "file_name": figma_data.get("name", "Unnamed"),
            "total_nodes": len(analysis["nodes"]),
            "mapping_suggestions": mappings,
            "preview_image": await self.get_preview_image(file_key)
        }
    
    def suggest_mappings(self, analysis):
        """Propose des mappings Figma → HomeOS"""
        suggestions = []
        
        for node in analysis["nodes"]:
            if node["type"] == "RECTANGLE":
                # Est-ce un bouton ?
                if self.looks_like_button(node):
                    suggestions.append({
                        "node_id": node["id"],
                        "node_name": node.get("name", "Rectangle"),
                        "suggested_type": "button",
                        "confidence": 0.85,
                        "reason": "Petit rectangle avec texte au centre"
                    })
                # Est-ce une carte ?
                elif self.looks_like_card(node):
                    suggestions.append({
                        "node_id": node["id"],
                        "suggested_type": "card",
                        "confidence": 0.75
                    })
        
        return suggestions
```

### **5.2. Interface d'import**
```html
<!-- Modal d'import -->
<div id="import-modal" class="modal">
  <div class="modal-content max-w-4xl">
    <h2 class="text-2xl font-bold mb-6">Importer depuis Figma</h2>
    
    <!-- URL ou file key -->
    <div class="mb-6">
      <label class="block text-sm font-medium mb-2">URL ou File Key Figma</label>
      <input type="text" 
             v-model="figmaUrl"
             placeholder="https://www.figma.com/file/... ou file_key"
             class="w-full border rounded px-4 py-3">
      <button @click="fetchFigmaFile"
              class="mt-3 bg-blue-600 text-white px-6 py-2 rounded">
        Analyser
      </button>
    </div>
    
    <!-- Résultats d'analyse -->
    <div v-if="importResults" class="border rounded-lg p-6">
      <h3 class="font-bold text-lg mb-4">
        Suggestions de mapping ({{ importResults.mapping_suggestions.length }})
      </h3>
      
      <div class="space-y-4 max-h-96 overflow-y-auto">
        <div v-for="suggestion in importResults.mapping_suggestions"
             :key="suggestion.node_id"
             class="border rounded p-4 hover:bg-gray-50">
          <div class="flex items-center justify-between">
            <div>
              <div class="font-medium">{{ suggestion.node_name }}</div>
              <div class="text-sm text-gray-600">{{ suggestion.reason }}</div>
            </div>
            <div class="flex items-center space-x-4">
              <select v-model="suggestion.user_choice"
                      class="border rounded px-3 py-1">
                <option value="">Ignorer</option>
                <option value="button">Bouton HTMX</option>
                <option value="input">Champ de saisie</option>
                <option value="card">Carte</option>
              </select>
              <span class="text-xs px-2 py-1 rounded"
                    :class="suggestion.confidence > 0.8 ? 'bg-green-100 text-green-800' : 'bg-yellow-100 text-yellow-800'">
                {{ Math.round(suggestion.confidence * 100) }}% confiance
              </span>
            </div>
          </div>
        </div>
      </div>
      
      <div class="mt-6 flex justify-end space-x-4">
        <button @click="applyMappings"
                class="bg-green-600 text-white px-6 py-2 rounded">
          Appliquer les mappings sélectionnés
        </button>
      </div>
    </div>
  </div>
</div>
```

---

## **PHASE 6 : GÉNÉRATION DE CODE (SEMAINE 7)**

### **6.1. Générateur de code final**
```python
# generator/code_generator.py
class CodeGenerator:
    def generate_project(self, homeos_elements: List[HomeOSElement]) -> Dict:
        """Génère tout le code du projet"""
        
        # HTML principal
        html = self.generate_html(homeos_elements)
        
        # Fichier Tailwind config si nécessaire
        tailwind_config = self.generate_tailwind_config(homeos_elements)
        
        # Routes API basées sur les actions HTMX
        api_routes = self.generate_api_routes(homeos_elements)
        
        # Fichier de métadonnées Figma (pour re-import)
        figma_metadata = self.generate_figma_metadata(homeos_elements)
        
        return {
            "structure": {
                "html": html,
                "css": self.extract_css_classes(homeos_elements),
                "js": self.generate_js_helpers(homeos_elements)
            },
            "config_files": {
                "tailwind.config.js": tailwind_config,
                "routes.py": api_routes
            },
            "metadata": {
                "figma_mappings": figma_metadata,
                "homeos_version": "1.0",
                "generated_at": datetime.now().isoformat()
            }
        }
    
    def generate_html(self, elements: List[HomeOSElement]) -> str:
        """Génère le HTML avec HTMX"""
        lines = []
        lines.append('<!DOCTYPE html>')
        lines.append('<html lang="fr">')
        lines.append('<head>')
        lines.append('  <meta charset="UTF-8">')
        lines.append('  <meta name="viewport" content="width=device-width, initial-scale=1.0">')
        lines.append('  <title>HomeOS Generated</title>')
        lines.append('  <script src="https://unpkg.com/htmx.org@1.9.10"></script>')
        lines.append('  <script src="https://cdn.tailwindcss.com"></script>')
        lines.append('</head>')
        lines.append('<body class="bg-gray-50">')
        lines.append('  <div class="container mx-auto p-8">')
        
        # Ajouter les éléments dans l'ordre Z-index
        for element in sorted(elements, key=lambda e: e.position.get('z', 0)):
            lines.append(f'    {element.to_html()}')
        
        lines.append('  </div>')
        lines.append('</body>')
        lines.append('</html>')
        
        return '\n'.join(lines)
```

---

## **ROADMAP D'IMPLÉMENTATION**

### **Semaine 1-2 :** 
- Authentification Figma API
- Canvas HTML basique avec divs
- Palette d'éléments prédéfinis
- Drag & drop simple

### **Semaine 3-4 :** 
- Cache local HomeOS
- Mapper styles Tailwind ↔ Figma
- Sync basique avec Figma API
- Sauvegarde locale

### **Semaine 5-6 :** 
- Panneau de propriétés complet
- Édition en temps réel
- Import depuis Figma existant
- Suggestions de mapping

### **Semaine 7-8 :** 
- Générateur de code complet
- Export HTML/HTMX/Tailwind
- Documentation
- Tests et bug fixes

---

## **TECH STACK RECOMMANDÉ**

### **Frontend :**
- **Vue.js** ou **Alpine.js** pour l'interactivité
- **Tailwind CSS** pour le style
- **Lucide Icons** pour les pictos
- **Interact.js** pour le drag & drop

### **Backend :**
- **FastAPI** (Python) pour le serveur
- **Pydantic** pour la validation
- **aiohttp** pour les appels API Figma
- **SQLite** pour le cache local

### **DevOps :**
- **Docker** pour l'environnement
- **GitHub Actions** pour CI/CD
- **Vercel** ou **Railway** pour le déploiement

---

## **POINTS CRITIQUES À SURVEILLER**

1. **Rate limiting Figma API** : 2000 req/heure
2. **Latence** : Sync différé, pas en temps réel
3. **Fallback offline** : Cache local obligatoire
4. **API d'écriture beta** : Peut changer, prévoir fallback

---

**Résumé :** Cette option 3 te donne un contrôle total avec une complexité raisonnable. Tu ne réinventes pas Figma, tu construis une surcouche intelligente qui utilise Figma comme backend de stockage tout en offrant une interface simplifiée orientée HomeOS/HTMX.