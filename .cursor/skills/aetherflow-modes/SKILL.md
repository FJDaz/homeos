# SKILL: AetherFlow Modes — Guide d'Implémentation par Mode

**Version**: 1.0  
**Date**: 2 février 2026  
**Public**: Claude, Cursor, Kimi et autres agents IA sur le projet AetherFlow

---

## 🎯 Principe Fondamental

**AVANT TOUTE IMPLÉMENTATION**, identifier le mode AetherFlow approprié.  
Ne jamais implémenter "directement" — toujours passer par l'abstraction d'un mode.

> "Pas de code sans mode, pas de mode sans routeur."

---

## 📋 Les Modes AetherFlow

### 1. Mode PROTO (`-q` / Quick)

| Attribut | Valeur |
|----------|--------|
| **Flag** | `-q` |
| **Vitesse** | Rapide |
| **Qualité** | Suffisante pour prototypage |
| **Provider** | Groq (LLaMA) par défaut |
| **Workflow** | `ProtoWorkflow` |

**Quand l'utiliser**:
- Proof of concept rapide
- Scripts utilitaires
- Tests unitaires simples
- Génération de données/mock
- Réponses à faible criticité

**Exemples de prompts**:
```
"Génère un script Python pour parser des logs"
"Crée un mock de données pour tester l'API"
"Ajoute une fonction utilitaire pour formatter les dates"
```

---

### 2. Mode PROD (`-f` / Full)

| Attribut | Valeur |
|----------|--------|
| **Flag** | `-f` |
| **Vitesse** | Standard |
| **Qualité** | Production-ready |
| **Provider** | AgentRouter (sélection intelligente) |
| **Workflow** | `ProdWorkflow` avec Surgical Edit |

**Quand l'utiliser**:
- Code production critique
- Modification de fichiers Python existants
- Algorithmes complexes nécessitant validation
- Features utilisateur finales
- Intégration avec code legacy

**Caractéristiques spéciales**:
- **Surgical Edit** : Modifications chirurgicales des fichiers existants
- **DOUBLE-CHECK** : Validation TDD/DRY/SOLID
- **AgentRouter** : Sélection automatique du meilleur modèle

**Exemples de prompts**:
```
"Implémente l'authentification JWT dans api.py"
"Refactorise la classe Orchestrator pour supporter l'async"
"Ajoute la gestion des erreurs dans le workflow PROD"
```

---

### 3. Mode VFX (`-vfx` / Visual Effects)

| Attribut | Valeur |
|----------|--------|
| **Flag** | `-vfx` |
| **Usage** | Frontend, UI/UX, génération visuelle |
| **Provider** | Gemini (Vision) + DeepSeek (code) |
| **Workflow** | Génération HTML/CSS/JS |

**Quand l'utiliser**:
- Génération de composants frontend
- Analyse de maquettes/datasheets
- Modifications visuelles
- Génération de templates
- Intégration HTML/CSS

**Exemples de prompts**:
```
"Génère un composant React pour afficher un dashboard"
"Transforme ce wireframe en HTML/CSS"
"Ajoute des animations à ce composant"
```

---

### 4. Mode FRONTEND (`-frd` / FrontendMode)

| Attribut | Valeur |
|----------|--------|
| **Flag** | `-frd` |
| **Usage** | Orchestration intelligente frontend |
| **Router** | `FrontendRouter` |
| **Providers** | Gemini / DeepSeek / Groq (auto) |

**Routing automatique**:

| Type de tâche | Provider | Raison |
|--------------|----------|--------|
| Vision (analyse image) | **Gemini** | Capacités vision natives |
| Grand contexte (>50k) | **Gemini** | Context window 1M tokens |
| Génération code | **DeepSeek** | Qualité code, coût |
| Micro-ajustements | **Groq** | Latence faible |
| Dialogue/Chat | **Groq** | Réactivité |
| Validation | **Groq** | Rapidité, fallback Gemini |

**Quand l'utiliser**:
- Workflows frontend complexes
- Analyse de design (PNG/Figma)
- Génération de composants avec contraintes
- Dialogue interactif avec l'utilisateur
- Validation d'homéostasie

**Commandes disponibles**:
```bash
sullivan frd analyze --image design.png
sullivan frd generate --design-structure ds.json
sullivan frd refine --html component.html --instruction "..."
sullivan frd dialogue --message "..."
sullivan frd validate --json payload.json
```

**Exemples de prompts**:
```
"Analyse ce design PNG et extrais la structure"
"Génère les composants HTML depuis ce design"
"Raffine ce bouton avec un effet hover"
"Valide la cohérence de ce JSON"
```

---

### 5. Mode DESIGNER (`designer` / DesignerMode)

| Attribut | Valeur |
|----------|--------|
| **Usage** | Analyse de designs + génération miroir |
| **Provider** | Gemini (Vision) |
| **Spécificité** | Extraction de principes design |

**Quand l'utiliser**:
- Upload d'image de design
- Extraction de style/structure visuelle
- Génération "miroir" (design → code)
- Analyse de datasheets

**Exemples de prompts**:
```
"Analyse cette maquette et génère le HTML correspondant"
"Extrais les principes design de cette image"
"Reproduis ce layout en Tailwind CSS"
```

---

### 6. Mode DEV (`dev` / DevMode)

| Attribut | Valeur |
|----------|--------|
| **Usage** | Analyse backend → génération frontend |
| **Workflow** | Collaboration Heureuse |
| **Spécificité** | Inférence top-down |

**Quand l'utiliser**:
- Analyse de codebase backend existante
- Inférence de la fonction globale
- Génération frontend depuis backend
- Analyse de structure de projet

**Exemples de prompts**:
```
"Analyse ce backend FastAPI et suggère un frontend"
"Extrais les intents de cette API"
"Génère les composants pour ces endpoints"
```

---

### 7. Mode UPLOAD (`upload` / Image Upload)

| Attribut | Valeur |
|----------|--------|
| **Usage** | Préprocessing d'images |
| **Module** | `image_preprocessor.py` |
| **Limite** | Respect des contraintes Gemini (~20MB) |

**Quand l'utiliser**:
- Upload d'images pour analyse
- Préprocessing avant vision API
- Optimisation de taille/qualité

**Processus**:
1. Analyse du type d'image (photo vs diagramme)
2. Sélection de la stratégie (JPEG adaptatif, resize, etc.)
3. Compression optimisée
4. Retour bytes prêts pour base64

---

## 🔄 Algorithme de Décision

Pour CHAQUE demande d'implémentation, suivre ce flux :

```
┌─────────────────────────────────────────────────────────────┐
│ 1. La demande concerne-t-elle du frontend/UI/visuel ?       │
└──────────────────────┬──────────────────────────────────────┘
                       │
         ┌─────────────▼─────────────┐
         │ OUI                       │ NON
         ▼                           ▼
┌────────────────────┐    ┌─────────────────────────────────────┐
│ Analyse d'image ?  │    │ 2. Modification de fichier Python   │
└─────────┬──────────┘    │    existant ?                       │
          │               └─────────────┬───────────────────────┘
   ┌──────▼──────┐                      │
   │ OUI         │ NON         ┌────────▼────────┐
   ▼             ▼             │ OUI             │ NON
┌─────────┐ ┌──────────┐       ▼                 ▼
│Designer │ │  -frd    │ ┌────────────────┐ ┌───────────────────┐
│  Mode   │ │  (router)│ │     -f         │ │    -q             │
└─────────┘ └──────────┘ │  (PROD/Surgical│ │  (PROTO rapide)   │
                         │   Edit)        │ └───────────────────┘
                         └────────────────┘
```

---

## ✅ Checklist Pré-Implémentation

Avant d'écrire UNE SEULE LIGNE de code :

- [ ] **Identifier le type de tâche** (frontend, backend, analyse, etc.)
- [ ] **Identifier le mode approprié** selon l'algorithme ci-dessus
- [ ] **Vérifier si un mode existe déjà** pour ce cas d'usage
- [ ] **Utiliser le workflow/mode** plutôt que d'appeler directement un LLM
- [ ] **Respecter la signature** du mode (arguments, return type)

---

## 🛠️ Patterns d'Implémentation

### Pattern 1: Via FrontendMode (frd)

```python
from Backend.Prod.sullivan.modes.frontend_mode import FrontendMode

frontend = FrontendMode()

# Analyse d'image
structure = await frontend.analyze_design(Path("design.png"))

# Génération
html = await frontend.generate_components(
    design_structure=structure,
    genome=genome_dict,
    webography=webography_text
)

# Raffinement
refined = await frontend.refine_style(html, "Rendre plus moderne")

# Validation
result = await frontend.validate_homeostasis(payload)
```

### Pattern 2: Via AgentRouter (prod)

```python
from Backend.Prod.models.agent_router import AgentRouter

router = AgentRouter(execution_mode="BUILD")

# Le router choisit automatiquement le meilleur modèle
result = await router.route_and_execute(
    prompt="Implémente une fonction de tri rapide",
    context=files,
    output_constraint="Python code only"
)
```

### Pattern 3: Via Mode CLI

```bash
# Toujours privilégier l'appel CLI si disponible
./aetherflow -f --plan plan.json
sullivan frd analyze --image design.png
```

---

## ❌ Anti-Patterns à Éviter

| ❌ Mauvais | ✅ Bon |
|-----------|--------|
| Appeler directement `GeminiClient.generate()` pour du code | Utiliser `AgentRouter` ou `-f` |
| Appeler `GroqClient` directement pour du dialogue | Utiliser `frontend.dialogue()` (frd) |
| Implémenter un preprocessing d'image from scratch | Utiliser `image_preprocessor.py` (upload) |
| Générer du HTML avec un LLM générique | Utiliser `FrontendMode.generate_components()` |
| Modifier un fichier Python existant sans validation | Utiliser `-f` (Surgical Edit + DOUBLE-CHECK) |

---

## 📚 Références

- **Mode emploi Sullivan**: `docs/02-sullivan/MODE_EMPLOI_SULLIVAN_GENOME.md`
- **FrontendMode**: `docs/02-sullivan/FRONTEND_MODE.md`
- **Surgical Edit**: `docs/guides/Surgical_Edit.md`
- **Guide rapide**: `docs/01-getting-started/GUIDE_RAPIDE_AETHERFLOW.md`
- **CLI Chat**: `docs/02-sullivan/CLI_CHAT_COMMANDS.md`
- **Widget Chat**: `Frontend/sullivan-chat-widget.html`
- **AgentRouter**: `Backend/Prod/models/agent_router.py`
- **FrontendMode code**: `Backend/Prod/sullivan/modes/frontend_mode.py`

---

## 🚀 Exemple de Flux Complet

**Demande**: "Implémente une fonction pour uploader et analyser des images de design"

**Réflexe attendu**:
1. C'est du frontend + traitement d'image
2. Mode approprié: `-frd` pour l'analyse, `upload` pour le preprocessing
3. Implémentation:
   ```python
   from Backend.Prod.sullivan.upload.image_preprocessor import preprocess_for_gemini
   from Backend.Prod.sullivan.modes.frontend_mode import FrontendMode
   
   async def analyze_uploaded_image(image_path: Path):
       # Mode upload: preprocessing
       image_bytes, mime_type = preprocess_for_gemini(image_path)
       
       # Mode frd: analyse
       frontend = FrontendMode()
       structure = await frontend.analyze_design(image_path)
       
       return structure
   ```

**Ce qu'il ne faut PAS faire**:
- Appeler directement `GeminiClient.generate_with_image()`
- Réimplémenter la logique de compression d'image
- Ne pas utiliser les modes existants

---

**Mise à jour**: Documenter tout nouveau mode ajouté à AetherFlow dans ce skill.
