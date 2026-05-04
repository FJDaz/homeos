"""
DIAGNOSTIC TEMPOREL — Analyse ROADMAP via Gemini API
Lecture B : hotspots, régressions, dettes, chronologie

Usage : python3 scripts/diagnostic_temporal.py
Output : scripts/diagnostic_temporal.json
"""
import os
import json
import re
from pathlib import Path
import google.generativeai as genai

ROOT = Path(__file__).parent.parent
COMM = ROOT / "Frontend" / "4. COMMUNICATION"

ROADMAP_FILES = [
    COMM / "ROADMAP.md",
    COMM / "ROADMAP_ACHIEVED.md",
    COMM / "ROADMAP_ACHIEVED_2026_02.md",
    COMM / "ROADMAP_ACHIEVED_2026_03.md",
    COMM / "ROADMAP_ACHIEVED_2026_04.md",
    COMM / "ROADMAP_BACKLOG.md",
]

OUTPUT = ROOT / "scripts" / "diagnostic_temporal.json"

def load_roadmaps() -> str:
    parts = []
    for f in ROADMAP_FILES:
        if f.exists():
            parts.append(f"=== {f.name} ===\n{f.read_text(encoding='utf-8')}")
    return "\n\n".join(parts)

PROMPT = """Tu es un architecte logiciel senior chargé d'un audit de régression sur un projet fullstack.
Voici l'intégralité des fichiers ROADMAP du projet HoméOS/AetherFlow : missions, rapports de livraison, archives et backlog.

Effectue une analyse structurée en 4 axes. Réponds UNIQUEMENT en JSON valide, sans balise markdown.

{
  "hotspots": [
    {
      "file": "nom_du_fichier",
      "touch_count": 0,
      "missions": ["M123", "M145", ...],
      "verdict": "contrat jamais défini | accumulation de patches | zone stable"
    }
  ],
  "regressions": [
    {
      "pattern": "description courte du pattern",
      "introduced_by": "Mxxx",
      "broken_by": "Myyy",
      "zone": "nom du module ou fichier",
      "recurrence_count": 0
    }
  ],
  "dette": [
    {
      "mission": "Mxxx",
      "declared": "TERMINÉE",
      "reopened_by": "Myyy",
      "delay_days": 0,
      "zone": "module concerné",
      "note": "ce qui n'a pas tenu"
    }
  ],
  "chronologie_promesses": [
    {
      "feature": "description de la fonctionnalité promise",
      "first_promised": "Mxxx",
      "delivered": true,
      "held": false,
      "broke_at": "Myyy",
      "impact": "élèves | profs | admin | pipeline"
    }
  ],
  "synthese": {
    "zones_les_plus_instables": ["fichier1", "fichier2"],
    "cause_racine_principale": "une phrase",
    "nb_regressions_identifiees": 0,
    "nb_missions_reouvertes": 0,
    "recommandation": "une phrase sur ce qu'il faudrait stabiliser en premier"
  }
}

Corpus ROADMAP :

"""

def main():
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        env_path = ROOT / ".env"
        if env_path.exists():
            for line in env_path.read_text().splitlines():
                if line.startswith("GOOGLE_API_KEY="):
                    api_key = line.split("=", 1)[1].strip()
                    break
    if not api_key:
        print("ERROR: GOOGLE_API_KEY introuvable")
        return

    genai.configure(api_key=api_key)
    model = genai.GenerativeModel("gemini-1.5-flash")

    print("Chargement des ROADMAP...")
    corpus = load_roadmaps()
    print(f"Corpus : {len(corpus)} caractères")

    full_prompt = PROMPT + corpus

    print("Envoi à Gemini API...")
    response = model.generate_content(
        full_prompt,
        generation_config={"temperature": 0.1, "max_output_tokens": 8192}
    )

    text = response.text.strip()
    text = re.sub(r'^```[a-z]*\s*', '', text, flags=re.MULTILINE)
    text = re.sub(r'\s*```$', '', text, flags=re.MULTILINE)
    s, e = text.find('{'), text.rfind('}')
    if s >= 0 and e >= 0:
        text = text[s:e+1]

    try:
        result = json.loads(text)
        OUTPUT.write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding='utf-8')
        print(f"\nRésultat écrit dans : {OUTPUT}")
        s = result.get("synthese", {})
        print(f"\n--- SYNTHÈSE ---")
        print(f"Zones instables : {', '.join(s.get('zones_les_plus_instables', []))}")
        print(f"Cause racine : {s.get('cause_racine_principale', '')}")
        print(f"Régressions : {s.get('nb_regressions_identifiees', '?')}")
        print(f"Missions réouvertes : {s.get('nb_missions_reouvertes', '?')}")
        print(f"Recommandation : {s.get('recommandation', '')}")
    except json.JSONDecodeError as ex:
        print(f"JSON parse error: {ex}")
        OUTPUT.with_suffix('.raw.txt').write_text(text, encoding='utf-8')
        print(f"Raw output écrit dans : {OUTPUT.with_suffix('.raw.txt')}")

if __name__ == "__main__":
    main()
