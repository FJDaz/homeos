# Stratégie d'Upload, Lecteur de Template et Cycle de Retour

**Dernière mise à jour** : 3 février 2026  
**Public** : Développeurs Sullivan, intégrateurs frontend, équipe AetherFlow  
**Scope** : Architecture technique + Guide pratique d'utilisation

---

## 📋 Table des Matières

1. [Vue d'ensemble](#vue-densemble)
2. [Partie 1 : Stratégie d'Upload](#partie-1--stratégie-dupload)
3. [Partie 2 : Lecteur de Template](#partie-2--lecteur-de-template)
4. [Partie 3 : Cycle de Retour](#partie-3--cycle-de-retour)
5. [Intégration des trois systèmes](#intégration-des-trois-systèmes)
6. [Références](#références)

---

## Vue d'ensemble

Sullivan implémente trois systèmes complémentaires pour gérer le flux complet **Design → Code → Validation → Correction** :

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│    UPLOAD       │───→│    TEMPLATE     │───→│     RETOUR      │
│  (Acquisition)  │    │  (Génération)   │    │ (Amélioration)  │
└─────────────────┘    └─────────────────┘    └─────────────────┘
        │                       │                       │
   Image/Maquette         Structure HTML         Audit visuel
   Préprocessing          Variables dyn.         Critiques IA
   Validation             Rendu moteur           Révision auto
```

| Système | Rôle | Fichier clé |
|---------|------|-------------|
| **Upload** | Acquérir et prétraiter les designs/images | `sullivan/upload/image_preprocessor.py` |
| **Template** | Structurer et générer le code frontend | `sullivan/generator/design_to_html.py` |
| **Retour** | Auditer, critiquer et affiner le résultat | `sullivan/refinement.py` |

---

## Partie 1 : Stratégie d'Upload

### 🎯 Objectifs

1. **Latence optimisée** : Réduction drastique pour Gemini Vision (<500KB, <1024px)
2. **Qualité préservée** : Compression intelligente sans perte perceptible
3. **Validation précoce** : Rejet des formats/tailles incompatibles avant traitement

### 🔧 Architecture

```python
Backend/Prod/sullivan/upload/
├── __init__.py
└── image_preprocessor.py     # Core preprocessing
```

### Configuration par défaut

```python
# Optimisation latence (vs ancienne config lente)
TARGET_MAX_BYTES = 500 * 1024   # 500 KB (was 3MB)
MAX_DIMENSION = 1024            # px côté long (was 1920)
JPEG_QUALITY = 70               # was 85
GEMINI_TIMEOUT_SECONDS = 15
```

> **Rationale** : Gemini travaille en interne en 512x512 ou 1024x1024. Au-delà = latence sans gain qualité.

### API Upload

#### `preprocess_for_gemini(image_path: Path) → Tuple[bytes, str]`

Pré-traite une image fichier pour envoi à Gemini Vision.

**Args**:
- `image_path` : Chemin vers l'image (PNG, JPG, JPEG, WEBP)
- `target_max_bytes` : Taille max cible (défaut 500KB)
- `max_dimension` : Dimension max en px (défaut 1024)

**Returns**:
- `(bytes, mime_type)` : Données prêtes pour `base64.b64encode()`

**Exemple** :
```python
from pathlib import Path
from Backend.Prod.sullivan.upload.image_preprocessor import preprocess_for_gemini

image_bytes, mime_type = preprocess_for_gemini(Path("design.png"))
# → (b'...', 'image/jpeg')
```

#### `preprocess_bytes_for_gemini(image_bytes: bytes) → Tuple[bytes, str]`

Version pour traiter des bytes déjà en mémoire (upload via API).

```python
from Backend.Prod.sullivan.upload.image_preprocessor import preprocess_bytes_for_gemini

# Image uploadée via HTTP
processed_bytes, mime_type = preprocess_bytes_for_gemini(raw_bytes)
```

### Flux de traitement

```
Image Input
    │
    ▼
┌─────────────────────┐
│  Validation format  │ ← Vérifie PNG/JPG/WEBP
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│   Conversion RGB    │ ← RGBA/P → RGB
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│   Resize si >1024px │ ← LANCZOS pour qualité
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│ Compression JPEG 70%│ ← Optimisation progressive
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│ Si >500KB : réduire │ ← Qualité 60%, 50%...
│ qualité jusqu'à 40% │
└──────────┬──────────┘
           │
           ▼
    (bytes, "image/jpeg")
```

### Validation pré-upload

#### `validate_image_before_upload(image_path: Path) → Tuple[bool, str]`

Valide si une image respecte les limites **avant** upload.

```python
from Backend.Prod.sullivan.upload.image_preprocessor import validate_image_before_upload

is_valid, message = validate_image_before_upload(Path("huge_image.png"))
# is_valid = False
# message = "Image trop grande (5.2MB). Maximum recommandé: 2MB..."
```

**Seuils de validation** :
| Métrique | Limite warning | Action |
|----------|---------------|--------|
| Taille fichier | > 2MB | Rejette, suggère compression |
| Dimensions | > 2048px | Rejette, suggère resize |
| Format | Non supporté | Rejette avec formats valides |

### Utilitaires client

#### `get_recommended_upload_limits() → dict`

Retourne les limites pour affichage côté client.

```python
from Backend.Prod.sullivan.upload.image_preprocessor import get_recommended_upload_limits

limits = get_recommended_upload_limits()
# {
#     "max_dimension": 1024,
#     "max_file_size_bytes": 512000,
#     "recommended_format": "JPEG",
#     "recommended_quality": 70,
#     "gemini_timeout_seconds": 15,
#     "estimated_processing_time": "2-5s"
# }
```

### CLI Upload

```bash
# Via DesignerMode (inclut upload + analyse)
sullivan designer --image design.png --output output/

# Validation préalable
curl -X POST http://localhost:8000/sullivan/designer/validate \
  -F "image=@design.png"
```

---

## Partie 2 : Lecteur de Template

### 🎯 Objectifs

1. **Séparation concerns** : Structure logique (génome) vs rendu visuel (HTML)
2. **Réutilisabilité** : Templates paramétrables pour différents contextes
3. **Extensibilité** : Support variables dynamiques, conditions, boucles

### 🔧 Architecture

```
sullivan/generator/
├── design_to_html.py          # Moteur de rendu template
├── component_generator.py     # Générateur de composants
└── corps_generator.py         # Générateur niveau Corps
```

### Structure de Template

Un template Sullivan est une structure hiérarchique qui sépare :
- **Intention** : Objectif métier du composant
- **Corps** : Zones de contenu sémantiques
- **Organes** : Éléments d'interaction
- **Molécules** : Groupes de composants
- **Atomes** : Éléments HTML de base

```json
{
  "intention": "landing_page",
  "corps": {
    "hero": {
      "type": "social_proof",
      "organes": {
        "header": {
          "molecules": {
            "title": {
              "atoms": ["h1", "subtitle"]
            }
          }
        }
      }
    }
  }
}
```

### API Lecteur de Template

#### `generate_html_from_design(...)`

Génère du HTML depuis une structure de design et le frontend structure.

**Args** :
- `design_structure` : Structure extraite du design (sections, composants)
- `frontend_structure` : Structure logique inférée (Corps/Organes/Molécules/Atomes)
- `image_path` : Chemin vers l'image source (optionnel, pour référence)
- `webography_text` : Références webdesign (principes, patterns)
- `output_path` : Chemin de sortie du fichier HTML

**Exemple** :
```python
from Backend.Prod.sullivan.generator.design_to_html import generate_html_from_design
from pathlib import Path

html_path = await generate_html_from_design(
    design_structure={"sections": [...]},
    frontend_structure={"corps": {...}},
    image_path=Path("design.png"),
    webography_text="Principles: Brutalist, minimal...",
    output_path=Path("output/studio/index.html")
)
```

### Variables de Template

Le moteur supporte plusieurs types de variables :

| Type | Syntaxe | Exemple |
|------|---------|---------|
| **Statique** | `{{variable}}` | `{{title}}` → "Mon Produit" |
| **Conditionnelle** | `{% if condition %}` | `{% if has_cta %}...{% endif %}` |
| **Boucle** | `{% for item in items %}` | `{% for feature in features %}` |
| **Filtre** | `{{variable\|filter}}` | `{{name\|upper}}` → "TITRE" |

### Contexte de Rendu

Le contexte est enrichi automatiquement avec :

```python
context = {
    # Données du design
    "design_structure": {...},
    "frontend_structure": {...},
    "webography": "...",
    
    # Métadonnées
    "generated_at": "2026-02-03T10:30:00",
    "genome_version": "1.0",
    
    # Helpers
    "base_url": "http://localhost:8000",
    "static_url": "/static",
}
```

### Templates par défaut

| Template | Usage | Emplacement |
|----------|-------|-------------|
| `brutalist_base` | Page single-file minimaliste | Inline dans generator |
| `studio_shell` | Layout Studio avec sidebar | `templates/studio.html` |
| `component_wrapper` | Wrapper pour composants isolés | Inline |

### Génération via CLI

```bash
# Génération complète (design → HTML)
sullivan frd generate \
  --design-structure design.json \
  --genome genome.json \
  --webography refs.md \
  --output index.html

# Génération avec variables custom
sullivan frd generate \
  --design-structure design.json \
  --vars '{"primary_color": "#ff0000", "font": "Inter"}' \
  --output custom.html
```

---

## Partie 3 : Cycle de Retour

### 🎯 Objectifs

1. **Qualité garantie** : Score visuel > 85 avant acceptation
2. **Itératif** : Boucle amélioration jusqu'à atteindre le seuil
3. **Automatisé** : Peu ou pas d'intervention humaine

### 🔧 Architecture

```
sullivan/
├── refinement.py              # Boucle principale refinement
├── auditor/
│   ├── sullivan_auditor.py    # Audit visuel IA
│   └── screenshot_util.py     # Capture screenshots
└── builder/
    └── sullivan_builder.py    # Construction HTML
```

### Workflow Refinement

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   Build     │────→│  Screenshot │────→│    Audit    │
│   HTML      │     │   (PlayW)   │     │   (Gemini)  │
└─────────────┘     └─────────────┘     └──────┬──────┘
                                               │
                              Score >= 85 ?    │
                          ┌────┴────┐          │
                         OUI        NON         │
                          │          │          │
                          ▼          ▼          │
                    ┌─────────┐   ┌────────────┐│
                    │  Done   │   │  Critiques ││
                    └─────────┘   └─────┬──────┘│
                                        │         │
                                        ▼         │
                                  ┌──────────┐    │
                                  │  Revise  │────┘
                                  │ (Gemini) │
                                  └──────────┘
```

### API Refinement

#### `run_refinement(genome, output_path, base_url, max_iterations, score_threshold)`

Exécute la boucle complète Build → Screenshot → Audit → Revise.

**Args** :
- `genome` : Chemin ou dict du genome
- `output_path` : Où sauvegarder le HTML final
- `base_url` : URL base pour les appels API (défaut: http://localhost:8000)
- `max_iterations` : Nombre max d'itérations (défaut: 5)
- `score_threshold` : Score minimal pour arrêt (défaut: 85)

**Returns** :
- `(path_to_html, final_html, last_audit_result)`

**Exemple** :
```python
from Backend.Prod.sullivan.refinement import run_refinement
from pathlib import Path

output_path, html, audit = await run_refinement(
    genome=Path("genome.json"),
    output_path=Path("output/studio/index.html"),
    base_url="http://localhost:8000",
    max_iterations=5,
    score_threshold=85
)

print(f"Score final: {audit.visual_score}")
print(f"Itérations: {audit.iterations}")
```

### Métriques d'Audit

Le `SullivanAuditor` évalue selon 4 critères :

| Critère | Poids | Description |
|---------|-------|-------------|
| **Layout** | 25% | Alignement, espacement, grille |
| **Typography** | 25% | Hiérarchie, lisibilité, contraste |
| **Hierarchy** | 25% | Structure visuelle, priorité |
| **Aesthetics** | 25% | Cohérence style, brutalist compliance |

**Score composite** : Moyenne pondérée des 4 critères (0-100)

### Format des Critiques

```python
@dataclass
class AuditResult:
    visual_score: int              # 0-100
    layout_score: int              # 0-100
    typography_score: int          # 0-100
    hierarchy_score: int           # 0-100
    aesthetics_score: int          # 0-100
    critiques: List[str]           # Liste des problèmes détectés
    suggestions: List[str]         # Suggestions d'amélioration
    
    def passed(self, threshold: int = 85) -> bool:
        return self.visual_score >= threshold
```

**Exemple de critiques** :
```python
[
    "Button contrast too low (ratio 2.1:1, need 4.5:1)",
    "Typography hierarchy unclear between H2 and H3",
    "Sidebar spacing inconsistent (24px vs 32px)"
]
```

### Prompt de Révision

Le système utilise un prompt spécialisé pour la révision :

```python
REVISE_PROMPT = """You are an expert Brutalist UI designer. 
Revise the HTML below based on these critiques.

Critiques:
{critiques}

Rules:
- Keep Brutalist style: system fonts, minimal palette, no external libs, raw.
- Preserve structure: sidebar (topology) + main (organes)
- Fix only what the critiques mention
- Return the complete revised HTML document only"""
```

### Cycle de retour manuel

Pour une intervention manuelle dans la boucle :

```python
# Itération 1
html = build_html(genome)
screenshot = await capture_html_screenshot(html)
audit = await audit_visual_output(html, screenshot)

# Intervention humaine
if not audit.passed():
    critiques_custom = audit.critiques + ["Ajouter animation hover sur boutons"]
    html = await revise_html(html, critiques_custom)
```

### CLI Refinement

```bash
# Refinement complet
sullivan refine \
  --genome genome.json \
  --output output/studio/ \
  --max-iterations 5 \
  --threshold 85

# Audit seul (sans refinement)
sullivan audit \
  --html output/studio/index.html \
  --output audit_result.json
```

---

## Intégration des trois systèmes

### Workflow Complet : Design → Code → Qualité

```python
from pathlib import Path
from Backend.Prod.sullivan.modes.designer_mode import DesignerMode
from Backend.Prod.sullivan.refinement import run_refinement

# 1. UPLOAD + ANALYSE
designer = DesignerMode(
    design_path=Path("design.png"),
    output_path=Path("output/designer"),
    output_html=True
)
result = await designer.run()

# Récupère le HTML généré
generated_html_path = Path("output/studio/studio_index.html")

# 2. (Optionnel) REFINEMENT pour qualité > 85
output_path, final_html, audit = await run_refinement(
    genome=result["frontend_structure"],
    output_path=Path("output/studio/studio_index_refined.html"),
    score_threshold=85
)

print(f"✓ Design analysé: {result['design_structure']}")
print(f"✓ HTML généré: {generated_html_path}")
print(f"✓ Score final: {audit.visual_score}/100")
```

### Intégration API REST

Les trois systèmes sont exposés via API FastAPI :

| Endpoint | Système | Action |
|----------|---------|--------|
| `POST /sullivan/designer/upload` | Upload | Upload + analyse design |
| `POST /sullivan/designer/analyze` | Upload | Analyse image existante |
| `POST /sullivan/frontend/generate` | Template | Génération HTML |
| `POST /sullivan/frontend/refine` | Template | Raffinement style |
| `POST /sullivan/refinement/run` | Retour | Boucle complète refinement |
| `POST /sullivan/audit` | Retour | Audit visuel seul |

### Gestion des erreurs

| Erreur | Système | Solution |
|--------|---------|----------|
| `Image too large` | Upload | Redimensionner à < 2048px avant envoi |
| `Unsupported format` | Upload | Convertir en PNG/JPG |
| `Template variable missing` | Template | Vérifier le contexte de rendu |
| `Score < threshold after max iterations` | Retour | Augmenter `max_iterations` ou baisser `threshold` |
| `Screenshot timeout` | Retour | Vérifier que le serveur est démarré sur `base_url` |

---

## Références

### Fichiers source

| Module | Fichier | Description |
|--------|---------|-------------|
| Upload | `Backend/Prod/sullivan/upload/image_preprocessor.py` | Préprocessing images |
| Template | `Backend/Prod/sullivan/generator/design_to_html.py` | Moteur de génération HTML |
| Template | `Backend/Prod/sullivan/generator/component_generator.py` | Générateur de composants |
| Retour | `Backend/Prod/sullivan/refinement.py` | Boucle refinement |
| Retour | `Backend/Prod/sullivan/auditor/sullivan_auditor.py` | Audit visuel IA |
| Retour | `Backend/Prod/sullivan/auditor/screenshot_util.py` | Capture screenshots |

### Documentation liée

- **FrontendMode** : `docs/02-sullivan/FRONTEND_MODE.md`
- **DesignerMode** : Workflow "Génération Miroir" dans `PRD_SULLIVAN.md`
- **PRD Sullivan** : `docs/02-sullivan/PRD_SULLIVAN.md`
- **Mode d'emploi** : `docs/02-sullivan/MODE_EMPLOI_SULLIVAN_GENOME.md`

### Configuration environnement

Variables requises dans `.env` :

```bash
# Pour Upload (Gemini Vision)
GOOGLE_API_KEY=your_gemini_key

# Pour Template (DeepSeek/Gemini selon contexte)
DEEPSEEK_API_KEY=your_deepseek_key

# Pour Retour (Gemini pour révision)
GOOGLE_API_KEY=your_gemini_key  # (même clé)

# Optionnel pour fallback rapide
GROQ_API_KEY=your_groq_key
```

---

**Document généré automatiquement**  
**Version** : 1.0  
**Mainteneur** : Équipe AetherFlow/Sullivan
