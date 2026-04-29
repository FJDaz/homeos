# FrontendMode (frd) — Mode FRONTEND de Sullivan

**Dernière mise à jour** : 2 février 2026  
**Public** : Développeurs utilisant l'orchestration multi-modèles pour workflows frontend

---

## 🎯 Vue d'ensemble

**FrontendMode** (`frd`) est le mode d'orchestration intelligente de Sullivan qui sélectionne automatiquement le meilleur modèle IA selon le type de tâche frontend :

- **Gemini** : Vision (analyse d'images), grands contextes (>50k tokens)
- **DeepSeek** : Génération de code, contextes moyens
- **Groq** : Micro-ajustements, dialogue conversationnel, validation (avec fallback Gemini)

### Workflow — « Orchestration Intelligente »

```
Tâche Frontend → FrontendRouter sélectionne modèle →
Exécution avec modèle optimal → Résultat
```

---

## 🔧 Architecture

### FrontendRouter

Le `FrontendRouter` (`Backend/Prod/models/frontend_router.py`) implémente la sélection intelligente de provider :

| Type de tâche | Provider | Condition |
|---------------|----------|-----------|
| `vision/analyze_design` | **Gemini** | Obligatoire (vision) |
| `generate_components/generate_html` | **Gemini** ou **DeepSeek** | Si `context_size > 50000` → Gemini, sinon DeepSeek |
| `refine_style/micro_adjustment` | **Groq** | Fallback Gemini si rate limit |
| `dialogue/chat` | **Groq** | Fallback Gemini si rate limit |
| `validate_homeostasis/validation` | **Groq** | Fallback Gemini si rate limit |

### Gestion du Rate Limiting

- **Groq** : Cache TTL de 60 secondes après erreur 429
- **Fallback automatique** : Si Groq rate limité → Gemini
- **Détection de disponibilité** : Vérifie les clés API avant sélection

---

## 📋 Méthodes FrontendMode

### 1. `analyze_design(image_path: Path) → Dict[str, Any]`

Analyse un design (image) avec Gemini vision via `DesignAnalyzer`.

**Input** :
- `image_path` : Chemin vers l'image (PNG, JPG, SVG)

**Output** :
- Structure de design : `{sections, components, layout, hierarchy}`

**Provider** : Gemini (obligatoire pour vision)

**Exemple** :
```python
from Backend.Prod.sullivan.modes.frontend_mode import FrontendMode

frontend_mode = FrontendMode()
structure = await frontend_mode.analyze_design(Path("design.png"))
```

---

### 2. `generate_components(design_structure, genome, webography, context_size) → str`

Génère des composants HTML selon la structure de design, le genome et la webographie.

**Input** :
- `design_structure` : Structure de design (dict)
- `genome` : Structure frontend optionnelle (dict)
- `webography` : Références webdesign (string)
- `context_size` : Taille du contexte en tokens (optionnel, calculé automatiquement)

**Output** :
- HTML généré (string)

**Provider** : Gemini si `context_size > 50000`, sinon DeepSeek

**Exemple** :
```python
html = await frontend_mode.generate_components(
    design_structure=structure,
    genome=genome_dict,
    webography=webography_text,
    context_size=60000  # → utilisera Gemini
)
```

---

### 3. `refine_style(html_fragment: str, instruction: str) → str`

Raffine le style d'un fragment HTML selon une instruction.

**Input** :
- `html_fragment` : Fragment HTML à modifier
- `instruction` : Instruction de raffinement (ex: "Rendre les boutons plus arrondis")

**Output** :
- HTML raffiné (string)

**Provider** : Groq (fallback Gemini si rate limit)

**Exemple** :
```python
refined = await frontend_mode.refine_style(
    html_fragment="<button>Click</button>",
    instruction="Ajouter un effet hover avec transition"
)
```

---

### 4. `dialogue(message: str, session_context: Optional[Dict]) → str`

Dialogue conversationnel avec Sullivan.

**Input** :
- `message` : Message utilisateur
- `session_context` : Contexte de session optionnel (dict)

**Output** :
- Réponse du modèle (string)

**Provider** : Groq (fallback Gemini si rate limit)

**Exemple** :
```python
response = await frontend_mode.dialogue(
    message="Comment améliorer l'accessibilité de ce formulaire ?",
    session_context={"current_page": "login", "user_level": "beginner"}
)
```

---

### 5. `validate_homeostasis(json_payload: Dict) → Dict[str, Any]`

Valide l'homéostasie (cohérence, complétude) d'un payload JSON.

**Input** :
- `json_payload` : Payload à valider (dict)

**Output** :
- Résultat de validation : `{valid: bool, issues: List[str], suggestions: List[str]}`

**Provider** : Groq (fallback Gemini si rate limit)

**Exemple** :
```python
result = await frontend_mode.validate_homeostasis({
    "endpoints": [...],
    "topology": [...]
})

if result["valid"]:
    print("✓ Payload valide")
else:
    for issue in result["issues"]:
        print(f"⚠ {issue}")
```

---

## 🖥️ CLI — `sullivan frd`

### Commandes disponibles

#### 1. Analyser un design

```bash
sullivan frd analyze --image design.png [--output structure.json]
```

**Exemple** :
```bash
sullivan frd analyze --image docs/DA/interface.png --output output/design_structure.json
```

---

#### 2. Générer des composants HTML

```bash
sullivan frd generate \
  --design-structure design.json \
  [--genome genome.json] \
  [--webography webography.md] \
  --output output.html \
  [--context-size 60000]
```

**Exemple** :
```bash
sullivan frd generate \
  --design-structure output/design_structure.json \
  --genome output/studio/homeos_genome.json \
  --output output/studio/studio_index.html
```

---

#### 3. Raffiner le style HTML

```bash
sullivan frd refine \
  --html fragment.html \
  --instruction "Rendre les boutons plus arrondis" \
  --output refined.html
```

**Exemple** :
```bash
sullivan frd refine \
  --html output/components/button.html \
  --instruction "Ajouter un effet hover avec transition 0.3s" \
  --output output/components/button_refined.html
```

---

#### 4. Dialogue conversationnel

```bash
sullivan frd dialogue \
  --message "Comment améliorer l'accessibilité ?" \
  [--session-context context.json] \
  [--output response.txt]
```

**Exemple** :
```bash
sullivan frd dialogue \
  --message "Quels sont les meilleurs patterns pour un formulaire d'inscription ?" \
  --output output/dialogue_response.txt
```

---

#### 5. Valider l'homéostasie JSON

```bash
sullivan frd validate \
  --json payload.json \
  [--output validation.json]
```

**Exemple** :
```bash
sullivan frd validate \
  --json output/studio/homeos_genome.json \
  --output output/validation_result.json
```

---

## 🌐 API REST

Les endpoints API pour FrontendMode sont disponibles dans `Backend/Prod/api.py` :

- `POST /sullivan/frontend/analyze` — Analyse de design
- `POST /sullivan/frontend/generate` — Génération de composants
- `POST /sullivan/frontend/refine` — Raffinement de style
- `POST /sullivan/dialogue` — Dialogue conversationnel
- `POST /sullivan/frontend/validate` — Validation homéostasie

Voir `docs/04-homeos/PRD_HOMEOS.md` pour les détails des endpoints.

---

## 🔄 Comparaison avec les autres modes

| Mode | Workflow | Provider Principal | Cas d'usage |
|------|----------|-------------------|-------------|
| **DevMode** | Analyse Backend → Inférence → Génération | AgentRouter (multi) | Backend → Frontend |
| **DesignerMode** | Upload Design → Analyse → Génération Miroir | Gemini (vision) | Design → Code |
| **FrontendMode** | Orchestration intelligente selon tâche | Gemini/DeepSeek/Groq | Workflows frontend avancés |

---

## 📚 Références

- **Code source** : `Backend/Prod/sullivan/modes/frontend_mode.py`
- **FrontendRouter** : `Backend/Prod/models/frontend_router.py`
- **PRD Sullivan** : `docs/02-sullivan/PRD_SULLIVAN.md`
- **Mode d'emploi Sullivan** : `docs/02-sullivan/MODE_EMPLOI_SULLIVAN_GENOME.md`

---

## 🚀 Exemples d'utilisation

### Workflow complet : Design → HTML

```bash
# 1. Analyser le design
sullivan frd analyze --image design.png --output design_structure.json

# 2. Générer le HTML
sullivan frd generate \
  --design-structure design_structure.json \
  --genome homeos_genome.json \
  --output studio_index.html

# 3. Raffiner le style
sullivan frd refine \
  --html studio_index.html \
  --instruction "Améliorer l'espacement et les contrastes" \
  --output studio_index_refined.html

# 4. Valider le résultat
sullivan frd validate \
  --json design_structure.json \
  --output validation.json
```

---

## ⚙️ Configuration

FrontendMode utilise les clients IA configurés dans `.env` :

- `GOOGLE_API_KEY` : Pour Gemini
- `DEEPSEEK_API_KEY` : Pour DeepSeek
- `GROQ_API_KEY` : Pour Groq

Le `FrontendRouter` détecte automatiquement les providers disponibles et applique les fallbacks si nécessaire.

---

## 🐛 Dépannage

### Erreur "Provider not available"

Vérifiez que les clés API sont configurées dans `.env` :
```bash
grep -E "(GOOGLE_API_KEY|DEEPSEEK_API_KEY|GROQ_API_KEY)" .env
```

### Rate limit Groq

Le `FrontendRouter` gère automatiquement les rate limits avec un cache TTL de 60 secondes. Si Groq est rate limité, le système bascule automatiquement vers Gemini.

### Erreur "Image not found"

Vérifiez que le chemin de l'image est correct et que le fichier existe :
```bash
ls -la path/to/image.png
```
