import sys
import os
import json
import time
from pathlib import Path
from dotenv import load_dotenv
from openai import OpenAI

# Add project root to sys.path for potential imports
project_root = Path(__file__).parent.parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

# Load environment variables
env_path = project_root / "Backend/.env"
load_dotenv(env_path)

PROMPT = """You are a Lead Theme Architect for premium WordPress themes.
Your task is to generate a high-fidelity, SEMANTIC SVG for a UI "organ".

CRITICAL: The user must be able to identify every component in Figma/Illustrator.

TECHNICAL VISUAL REQUIREMENTS:
1. Output ONLY <svg>...</svg>. 1000x600.
2. SEMANTIC NAMING: Every component group MUST be wrapped in a `<g id="COMPONENT_ID">` where COMPONENT_ID is the 'id' from the JSON (e.g., <g id="comp_ir_table">).
3. VISUAL ANNOTATIONS: For each component, add a tiny, subtle label (text size 10px, fill-opacity 0.4) showing its ID at the top-left of the component.
4. METADATA: Include a `<title>` tag inside each `<g>` with the 'description_ui' from the JSON.
5. AESTHETICS: Use WordPress ThemeForest premium styles (gradients, rounded corners, soft shadows). No simplistic wireframes.
6. LEGEND: At the very bottom (y=580), add a small text label with the Organ Name and its ID.

Organ Data: {organ_name}
Layout Strategy: {layout_strategy}
Components JSON:
{components_json}
"""

def collect_components(organ):
    """Collect all n3_components from an organ's n2_features."""
    components = []
    for feature in organ.get("n2_features", []):
        components.extend(feature.get("n3_components", []))
    return components

def generate_svg_for_organ(client, organ, model):
    """Generate SVG for a single organ using KIMI API."""
    components = collect_components(organ)
    
    prompt = PROMPT.format(
        layout_strategy=organ.get("layout_strategy", "responsive_grid"),
        organ_name=organ.get("name", organ["id"]),
        components_json=json.dumps(components, indent=2)
    )
    
    response = client.chat.completions.create(
        model=model,
        messages=[
            {
                "role": "system", 
                "content": "You are a professional SVG UI designer specializing in high-fidelity WordPress wireframes."
            },
            {
                "role": "user", 
                "content": prompt
            }
        ],
        temperature=0.4,
        max_tokens=4000
    )
    
    content = response.choices[0].message.content or ""
    
    # Extract SVG from response
    if "<svg" in content:
        start_idx = content.find("<svg")
        end_idx = content.rfind("</svg>") + 6
        return content[start_idx:end_idx]
    
    return None

def main():
    """Main batch processing function."""
    api_key = os.getenv("KIMI_KEY")
    if not api_key:
        print("❌ KIMI_KEY not set in environment variables")
        return
    
    model = "kimi-k2.5"
    
    # Initialize OpenAI client for KIMI API
    client = OpenAI(
        base_url="https://api.moonshot.ai/v1",
        api_key=api_key
    )
    
    # Load genome data
    genome_path = project_root / "Frontend/2. GENOME/genome_enriched.json"
    if not genome_path.exists():
        print(f"❌ Genome file not found: {genome_path}")
        return
    
    with open(genome_path, 'r', encoding='utf-8') as f:
        genome = json.load(f)
    
    # Create exports directory
    exports_dir = project_root / "exports"
    exports_dir.mkdir(exist_ok=True)
    
    results = []
    organ_count = 0
    
    # Process all organs (n1_sections) in all phases (n0_phases)
    for n0 in genome.get("n0_phases", []):
        for organ in n0.get("n1_sections", []):
            organ_id = organ["id"]
            organ_count += 1
            
            print(f"\n[{organ_count}] Generating SVG for {organ_id}...")
            
            try:
                svg = generate_svg_for_organ(client, organ, model)
                
                if svg:
                    # Save individual SVG file
                    out_path = exports_dir / f"{organ_id}_kimi.svg"
                    out_path.write_text(svg, encoding='utf-8')
                    
                    # Add SVG payload to organ data
                    organ["svg_payload"]