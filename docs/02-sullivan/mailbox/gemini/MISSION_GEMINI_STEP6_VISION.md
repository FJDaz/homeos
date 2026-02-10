# MISSION GEMINI : Step 6 - Designer Vision (Analyse PNG)

**Date** : 9 février 2026
**Agent** : Gemini (Vision Specialist)
**Mode AetherFlow** : BUILD
**Priorité** : 🔴 P0

---

## 0. CONTEXTE - TA SPÉCIALITÉ

**Bravo pour Step 5 QA !** (11/11 tests ✅)

Maintenant, on passe à **ta vraie force** : **Vision multimodale**.

Step 6 = Analyse PNG uploadé par l'utilisateur et extraction automatique du style + layout.

---

## 1. OBJECTIF

Créer une fonction Python qui :
1. **Reçoit un PNG** uploadé à Step 5
2. **Analyse l'image** avec Gemini Vision API
3. **Extrait** :
   - Couleurs (bg, primary, secondary, text)
   - Typographie (font family inférée)
   - Spacing (padding, margins, border-radius)
   - Layout (zones détectées : header, sidebar, main, footer)
4. **Génère un JSON** : "Visual Intention Report"

---

## 2. ARCHITECTURE

### 2.1 Fonction Principale

Créer dans `Backend/Prod/sullivan/vision_analyzer.py` :

```python
from Backend.Prod.models.gemini_client import GeminiClient
from pathlib import Path
import json

async def analyze_design_png(png_path: str, session_id: str) -> dict:
    """
    Analyse un PNG avec Gemini Vision et retourne un rapport d'intention visuelle.

    Args:
        png_path: Chemin vers le PNG uploadé
        session_id: ID session utilisateur

    Returns:
        Visual Intention Report (dict)
    """

    # 1. Charger l'image
    with open(png_path, "rb") as f:
        image_data = f.read()

    # 2. Prompt Gemini Vision
    prompt = """
    Analyse ce design d'interface et extrait :

    1. **Couleurs** :
       - Couleur de fond principale
       - Couleur primaire (CTA, liens)
       - Couleur secondaire
       - Couleur texte

    2. **Typographie** :
       - Font family (inférer : serif, sans-serif, monospace)
       - Tailles de police (small, base, large, xl)

    3. **Spacing** :
       - Border radius (coins arrondis : 0px, 8px, 16px, 32px)
       - Padding standard
       - Margins entre sections

    4. **Layout** :
       - Zones détectées (header, sidebar, main, footer)
       - Position et dimensions approximatives de chaque zone
       - Composants visibles (boutons, cards, formulaires)

    Retourne un JSON structuré.
    """

    # 3. Appeler Gemini Vision
    client = GeminiClient()
    response = await client.analyze_image(
        image_data=image_data,
        prompt=prompt,
        model="gemini-2.0-flash-exp"  # Vision supporté
    )

    # 4. Parser la réponse
    visual_report = parse_gemini_vision_response(response)

    # 5. Sauvegarder le rapport
    report_path = Path(f"~/.aetherflow/sessions/{session_id}/visual_report.json").expanduser()
    report_path.parent.mkdir(parents=True, exist_ok=True)

    with open(report_path, "w") as f:
        json.dump(visual_report, f, indent=2)

    return visual_report


def parse_gemini_vision_response(response: str) -> dict:
    """Parse la réponse Gemini Vision en JSON structuré."""

    # Format attendu du JSON
    template = {
        "metadata": {
            "analyzed_at": "2026-02-09T15:00:00Z",
            "model": "gemini-2.0-flash-exp"
        },
        "style": {
            "colors": {
                "bg": "#1a1a1a",
                "primary": "#6366f1",
                "secondary": "#8b5cf6",
                "text": "#f3f4f6"
            },
            "typography": {
                "family": "sans-serif",
                "sizes": {
                    "small": "0.875rem",
                    "base": "1rem",
                    "large": "1.25rem",
                    "xl": "1.5rem"
                }
            },
            "spacing": {
                "border_radius": "16px",
                "padding": "1rem",
                "margin": "1.5rem"
            }
        },
        "layout": {
            "zones": [
                {
                    "id": "zone_header",
                    "type": "header",
                    "coordinates": {"x": 0, "y": 0, "w": 1440, "h": 80},
                    "components": ["logo", "navigation", "user_menu"]
                },
                {
                    "id": "zone_main",
                    "type": "main",
                    "coordinates": {"x": 250, "y": 100, "w": 1000, "h": 700},
                    "components": ["content_area", "cards_grid"]
                }
            ]
        }
    }

    # Parser la réponse Gemini (JSON ou texte à structurer)
    # TODO : Implémenter parsing intelligent

    return template
```

---

## 3. INTÉGRATION DANS STUDIO_ROUTES

KIMI va créer la route, mais voici ce qu'elle doit faire :

```python
@router.post("/studio/step/6/analyze")
async def analyze_uploaded_design(session_id: str = Query(None)):
    """
    Déclenche l'analyse Gemini Vision du PNG uploadé à Step 5.

    Returns:
        HTML fragment avec rapport visuel + calque zones détectées
    """

    # 1. Récupérer le PNG uploadé
    upload_path = Path(f"~/.aetherflow/uploads/{session_id}/design.png").expanduser()

    if not upload_path.exists():
        raise HTTPException(400, "Aucun PNG trouvé. Uploadez d'abord à Step 5.")

    # 2. Analyser avec Gemini Vision
    from Backend.Prod.sullivan.vision_analyzer import analyze_design_png

    visual_report = await analyze_design_png(str(upload_path), session_id)

    # 3. Retourner template HTML avec résultats
    return templates.TemplateResponse("studio_step_6_analysis.html", {
        "request": request,
        "report": visual_report,
        "png_url": f"/uploads/{session_id}/design.png"
    })
```

---

## 4. FORMAT VISUAL INTENTION REPORT

**Structure JSON attendue** :

```json
{
  "metadata": {
    "analyzed_at": "2026-02-09T15:00:00Z",
    "model": "gemini-2.0-flash-exp",
    "source_png": "design.png"
  },
  "style": {
    "colors": {
      "bg": "#1a1a1a",
      "primary": "#6366f1",
      "secondary": "#8b5cf6",
      "text": "#f3f4f6",
      "border": "#374151"
    },
    "typography": {
      "family": "sans-serif",
      "weights": [400, 600, 700],
      "sizes": {
        "xs": "0.75rem",
        "sm": "0.875rem",
        "base": "1rem",
        "lg": "1.125rem",
        "xl": "1.25rem",
        "2xl": "1.5rem"
      }
    },
    "spacing": {
      "border_radius": "16px",
      "padding_sm": "0.5rem",
      "padding_base": "1rem",
      "padding_lg": "1.5rem",
      "gap": "1rem"
    }
  },
  "layout": {
    "type": "dashboard",
    "zones": [
      {
        "id": "zone_header",
        "type": "header",
        "coordinates": {"x": 0, "y": 0, "w": 1440, "h": 80},
        "components": ["logo", "nav", "user_menu"],
        "hypothesis": {
          "label": "Barre de navigation principale",
          "confidence": 0.95
        }
      },
      {
        "id": "zone_sidebar",
        "type": "sidebar",
        "coordinates": {"x": 0, "y": 80, "w": 240, "h": 820},
        "components": ["menu", "filters"],
        "hypothesis": {
          "label": "Sidebar avec navigation secondaire",
          "confidence": 0.88
        }
      },
      {
        "id": "zone_main",
        "type": "main",
        "coordinates": {"x": 240, "y": 80, "w": 1200, "h": 820},
        "components": ["content", "cards_grid"],
        "hypothesis": {
          "label": "Zone de contenu principal",
          "confidence": 0.92
        }
      }
    ]
  }
}
```

---

## 5. CRITÈRES D'ACCEPTATION

- [ ] Fichier `vision_analyzer.py` créé
- [ ] Fonction `analyze_design_png()` fonctionnelle
- [ ] Intégration Gemini Vision API (client existant)
- [ ] Parsing réponse Gemini → JSON structuré
- [ ] Sauvegarde rapport dans `~/.aetherflow/sessions/{session_id}/`
- [ ] Tests unitaires (minimum 5 tests) :
  - Analyse PNG valide
  - Extraction couleurs correcte
  - Détection zones layout
  - Erreur si PNG manquant
  - Format JSON conforme

---

## 6. RÉFÉRENCES

| Document | Contenu |
|----------|---------|
| [Parcours UX Sullivan.md](docs/02-sullivan/Parcours UX Sullivan.md) | Step 6 détaillé (lignes 285-360) |
| `Backend/Prod/models/gemini_client.py` | Client Gemini existant |
| Step 5 CR | PNG uploadé dans `~/.aetherflow/uploads/` |

---

## 7. LIVRAISON

**CR Gemini** : `docs/02-sullivan/mailbox/gemini/CR_STEP6_VISION.md`

**Format du CR** :
```markdown
# Compte-Rendu : Step 6 - Designer Vision

**Date** : [date]
**Agent** : Gemini (Vision)
**Mission** : MISSION_GEMINI_STEP6_VISION.md

## ✅ Ce qui a été fait
- vision_analyzer.py créé
- Intégration Gemini Vision API
- Parsing JSON
- Tests

## 📁 Fichiers créés
- Backend/Prod/sullivan/vision_analyzer.py
- Backend/Prod/tests/sullivan/test_vision_analyzer.py

## 🧪 Tests exécutés
[résultat pytest]

## 📤 HANDOFF pour KIMI
Dépose dans : docs/02-sullivan/mailbox/kimi/HANDOFF_GEMINI_STEP6_UI.md

Contenu :
- Visual report JSON format
- Instructions pour template HTML
```

---

**C'est ta spécialité. Go analyser ces PNG !**

*— Sonnet (Ingénieur en Chef)*
