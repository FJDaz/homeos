import base64
from Backend.Prod.models.gemini_client import GeminiClient
from pathlib import Path
import json
from typing import Dict, Any

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
    
    # Encode image to base64
    image_base64 = base64.b64encode(image_data).decode("utf-8")

    # 2. Prompt Gemini Vision
    prompt = """
    Analyse ce design d'interface et extrait :

    1. **Couleurs** :
       - Couleur de fond principale (bg)
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
       - Position et dimensions approximatives de chaque zone (x, y, w, h en pixels, si possible)
       - Composants visibles (boutons, cards, formulaires)

    Retourne un JSON structuré avec la structure suivante:
    ```json
    {
      "metadata": {
        "analyzed_at": "YYYY-MM-DDTHH:MM:SSZ",
        "model": "gemini-2.0-flash-exp",
        "source_png": "design.png"
      },
      "style": {
        "colors": {
          "bg": "#HEXCODE",
          "primary": "#HEXCODE",
          "secondary": "#HEXCODE",
          "text": "#HEXCODE",
          "border": "#HEXCODE"
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
          }
        ]
      }
    }
    ```
    Si tu ne peux pas déterminer une valeur, utilise `null`.
    ```
    """

    # 3. Appeler Gemini Vision
    client = GeminiClient()
    generation_result = await client.generate_with_image(
        image_base64=image_base64,
        prompt=prompt
    )
    
    if not generation_result.success:
        raise Exception(f"Gemini Vision API call failed: {generation_result.error}")
    
    response_text = generation_result.code

    # 4. Parser la réponse
    visual_report = parse_gemini_vision_response(response_text)

    # 5. Sauvegarder le rapport
    report_path = Path(f"~/.aetherflow/sessions/{session_id}/visual_report.json").expanduser()
    report_path.parent.mkdir(parents=True, exist_ok=True)

    with open(report_path, "w") as f:
        json.dump(visual_report, f, indent=2)

    return visual_report


def parse_gemini_vision_response(response_text: str) -> Dict[str, Any]:
    """Parse la réponse Gemini Vision en JSON structuré.
    Tente d'extraire un bloc JSON de la réponse texte."""
    try:
        # Gemini Vision might embed the JSON in a markdown code block
        if "```json" in response_text:
            json_str = response_text.split("```json")[1].split("```")[0].strip()
        else:
            json_str = response_text.strip()
        return json.loads(json_str)
    except json.JSONDecodeError as e:
        print(f"Error parsing Gemini Vision response to JSON: {e}")
        print(f"Response text: {response_text}")
        return {
            "error": "JSON parsing failed",
            "raw_response": response_text,
            "details": str(e)
        }
    except IndexError:
        print("Could not find JSON block in Gemini Vision response.")
        return {
            "error": "JSON block not found",
            "raw_response": response_text
        }