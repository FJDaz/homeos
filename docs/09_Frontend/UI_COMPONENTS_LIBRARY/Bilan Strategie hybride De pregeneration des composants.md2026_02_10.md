• D'après mon analyse de la codebase, voici ce qui existe déjà :

  ✅ Ce qui est DÉJÀ implémenté

  1. Les 8 Layouts par défaut (identity.py ligne 114-172)

  SULLIVAN_LAYOUT_PROPOSALS = [
      {"id": "minimal", "name": "Minimaliste", "description": "Clean & Airy...", "co
  lors": {...}},
      {"id": "brutalist", "name": "Brutaliste", "description": "Raw & Bold...", ...}
  ,
      {"id": "tdah_focus", "name": "Focus TDAH", "description": "High Contrast & Low
  Noise...", ...},
      {"id": "glassmorphism", "name": "Glassmorphism", ...},
      {"id": "neumorphism", "name": "Neumorphism", ...},
      {"id": "cyberpunk", "name": "Cyberpunk", ...},
      {"id": "organic", "name": "Organique", ...},
      {"id": "corporate", "name": "Corporate", ...}
  ]

  Classe associée : LayoutProposals (ligne 863+) avec méthodes get_all(), get_by_id(
  ), get_preview_html()

  2. Templates HTML pour afficher les layouts

  • studio_step_5_layouts.html : Grille 2×4 des 8 styles avec aperçus visuels
  • studio_step_5_choice.html : Choix entre "Uploader PNG" ou "Voir les styles"
  • Routes API dans studio_routes.py (ligne 720+) : /studio/step/5/layouts, /studio/
    ep/5/layouts/select

  3. Design Principles & Fallbacks (identity.py)

  def _normalize_principles_to_style(dp: Dict) -> Dict[str, str]:
      """Mappe le format Gemini vers style_global."""
      # Fallback : si pas de principles extraits, utilise défauts

  4. Extraction des principles (design_principles_extractor.py)

  Utilisé par DesignerMode et FrontendMode pour extraire les vraies valeurs d'un PNG
  uploadé.

  ❌ Ce qui n'est PAS (ou peu) implémenté

  La stratégie de loading hybride (3 Tiers)

  C'est documenté dans STRATEGIE HYBRIDES DE PREGENRATION DES COMPOSANTS.md mais pas
  codé :

  • ❌ Pas de CORE LIBRARY pré-générée (Tier 1)
  • ❌ Pas de PATTERN LIBRARY avec cache (Tier 2)
  • ❌ Pas de logique "adaptation vs regénération" intelligente
  • ❌ Pas de cache sémantique "intent → composant"

  Design Tokens par défaut structurés

  Il y a des fallback dans le code, mais pas de fichier JSON centralisé comme :

  {
    "default_tokens": {
      "colors": {"primary": "#000000", "secondary": "#f5f5f5"},
      "typography": {"font_family": "monospace", "scale": 1.25}
    }
  }
