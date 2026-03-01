"""
infer_layout_test.py
Test A/B : inférence layout via Claude Haiku vs heuristique pure.
Usage : python infer_layout_test.py
"""

import json, os, re
from pathlib import Path

# Charger .env AetherFlow
_env = Path(__file__).parent.parent / ".env"
if _env.exists():
    for line in _env.read_text().splitlines():
        if "=" in line and not line.startswith("#"):
            k, _, v = line.partition("=")
            os.environ.setdefault(k.strip(), v.strip())

GENOME_PATH = Path(__file__).parent.parent / "Frontend/2. GENOME/genome_reference.json"
PATTERNS_PATH = Path(__file__).parent.parent / "Frontend/3. STENCILER/static/layout_patterns.json"

# --- Extraction des organes N1 ---
def extract_organs(genome):
    organs = []
    for phase in genome.get("n0_phases", []):
        for organ in phase.get("n1_sections", []):
            organs.append({
                "id": organ["id"],
                "name": organ.get("name", ""),
                "n2_count": len(organ.get("n2_features", [])),
                "density": organ.get("density"),
                "layout_hint": organ.get("layout_hint"),
            })
    return organs

# --- Méthode A : heuristique pure (sans API) ---
ROLE_KEYWORDS = {
    "navigation": ["nav", "navigation", "menu", "breadcrumb"],
    "toolbar":    ["toolbar", "tools", "controls", "palette"],
    "sidebar_controls": ["sidebar", "panel", "controls", "settings"],
    "editor":     ["editor", "code", "script", "json", "analyse"],
    "canvas":     ["canvas", "board", "drawing", "stencil"],
    "chat":       ["chat", "dialogue", "message", "input"],
    "preview":    ["preview", "render", "viewer", "output"],
    "dashboard":  ["dashboard", "session", "summary", "status", "report"],
    "deploy_pipeline": ["deploy", "pipeline", "export", "build", "publish"],
}

ROLE_LAYOUT = {
    "navigation":       {"zone": "header",        "w": 1024, "h": 48,   "layout": "flex"},
    "toolbar":          {"zone": "header",        "w": 1024, "h": 40,   "layout": "flex"},
    "sidebar_controls": {"zone": "sidebar_right", "w": 240,  "h": "auto","layout": "stack"},
    "editor":           {"zone": "main",          "w": 640,  "h": "auto","layout": "stack"},
    "canvas":           {"zone": "canvas",        "w": 1024, "h": "full","layout": "free"},
    "chat":             {"zone": "sidebar_right", "w": 336,  "h": "auto","layout": "stack"},
    "preview":          {"zone": "preview_band",  "w": 1024, "h": 120,  "layout": "flex"},
    "dashboard":        {"zone": "main",          "w": 1024, "h": 320,  "layout": "grid"},
    "deploy_pipeline":  {"zone": "footer",        "w": 1024, "h": 48,   "layout": "flex"},
}

def infer_role(organ_id, organ_name):
    pool = f"{organ_id} {organ_name}".lower()
    for role, keywords in ROLE_KEYWORDS.items():
        if any(k in pool for k in keywords):
            return role
    return None

def heuristic_infer(organs):
    result = {}
    for o in organs:
        role = infer_role(o["id"], o["name"])
        if role and role in ROLE_LAYOUT:
            result[o["id"]] = {"role": role, **ROLE_LAYOUT[role]}
        else:
            # Fallback : stack générique, largeur proportionnelle au nb d'enfants
            w = min(320 + o["n2_count"] * 32, 800)
            w = round(w / 8) * 8  # arrondi au multiple de 8
            result[o["id"]] = {"role": "unknown", "zone": "main", "w": w, "h": "auto", "layout": "stack"}
    return result

# --- Méthode B : Gemini Flash via API ---
SYSTEM_PROMPT = """Tu es un expert UX/layout. Pour chaque organe N1 d'un genome JSON,
tu inféres ses paramètres de layout SVG.

Règles strictes :
- reference_width = 1024px, grid_unit = 8px (toutes les valeurs en multiples de 8)
- zones disponibles : header, sidebar_left, sidebar_right, main, canvas, preview_band, footer
- layout types : flex, stack, grid, free
- h peut être un nombre (px) ou "auto" ou "full"
- w peut être un nombre (px) ou "full"

Réponds UNIQUEMENT avec un objet JSON valide, sans markdown, sans explication.
Format : { "organ_id": { "role": "...", "zone": "...", "w": ..., "h": ..., "layout": "..." }, ... }"""

def gemini_infer(organs):
    try:
        import google.generativeai as genai
    except ImportError:
        return None, "google-generativeai not installed — pip install google-generativeai"

    api_key = os.environ.get("GOOGLE_API_KEY")
    if not api_key:
        return None, "GOOGLE_API_KEY not set"

    genai.configure(api_key=api_key)
    model = genai.GenerativeModel(
        model_name="gemini-3-flash-preview",
        system_instruction=SYSTEM_PROMPT
    )

    organs_summary = [{"id": o["id"], "name": o["name"], "n2_count": o["n2_count"]} for o in organs]
    user_msg = f"Genome organs N1 :\n{json.dumps(organs_summary, ensure_ascii=False, indent=2)}"

    try:
        response = model.generate_content(user_msg)
        raw = response.text.strip()
        raw = re.sub(r"^```json\s*|\s*```$", "", raw, flags=re.MULTILINE).strip()
        result = json.loads(raw)
        return result, None
    except Exception as e:
        return None, str(e)

# --- Comparaison ---
def compare(heuristic, claude):
    print("\n" + "="*60)
    print(f"{'ORGAN':<30} {'HEURISTIC':>14}  {'CLAUDE':>14}")
    print("="*60)
    all_keys = sorted(set(list(heuristic.keys()) + (list(claude.keys()) if claude else [])))
    diffs = 0
    for key in all_keys:
        h = heuristic.get(key, {})
        c = claude.get(key, {}) if claude else {}
        h_str = f"{h.get('zone','?')} {h.get('w','?')}x{h.get('h','?')}"
        c_str = f"{c.get('zone','?')} {c.get('w','?')}x{c.get('h','?')}" if c else "—"
        diff = " ≠" if h_str != c_str else ""
        if diff: diffs += 1
        print(f"{key:<30} {h_str:>14}  {c_str:>14}{diff}")
    print("="*60)
    print(f"Divergences : {diffs}/{len(all_keys)}")

if __name__ == "__main__":
    genome = json.loads(GENOME_PATH.read_text())
    organs = extract_organs(genome)
    print(f"Organes trouvés : {len(organs)}")

    print("\n--- Méthode A : Heuristique pure ---")
    h_result = heuristic_infer(organs)
    print(json.dumps(h_result, indent=2, ensure_ascii=False))

    print("\n--- Méthode B : Gemini Flash ---")
    g_result, err = gemini_infer(organs)
    if err:
        print(f"Erreur : {err}")
    else:
        print(json.dumps(g_result, indent=2, ensure_ascii=False))

    if g_result:
        compare(h_result, g_result)
