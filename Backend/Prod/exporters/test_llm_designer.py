import sys
import os
import json
import logging
from pathlib import Path

# Add project root to sys.path to resolve Backend.Prod
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# Load env vars
from dotenv import load_dotenv
env_path = os.path.join(project_root, "Backend", ".env")
load_dotenv(env_path)

from Backend.Prod.models.gemini_client import GeminiClient

logging.basicConfig(level=logging.INFO)

PROMPT = """You are a Lead Theme Architect for premium WordPress themes (like Astra, Divi, ThemeForest top sellers).
Your task is to generate ONLY valid, clean SVG code to represent a single UI section (an "organ").
I will provide you with a list of components, their roles, and the target layout strategy.

REQUIREMENTS:
1. Output ONLY the <svg>...</svg> code block. No markdown around it, no explanations.
2. Dimensions: Create a vibrant SVG representation. Use a fixed viewBox, e.g. viewBox="0 0 1000 800". Make it highly detailed.
3. Aesthetics: The user is tired of empty grey rectangles. Draw ACTUAL premium components! If there is a "launch-button", draw a beautiful button with rounded corners, a gradient background, shadow, and text/icon. If there is a "preview", draw an impressive placeholder card with a subtle border and shadow.
4. Typography: Use generic system fonts but style them nicely with font-weight and fill colors.
5. Layout: Apply the strategy: {layout_strategy}. Organize the components beautifully according to this layout.
6. The background should be a sleek dark mode or clean light mode (your choice).
7. If a component has `description_ui`, represent that faithfully in the drawing!

Input Data:
Organ ID/Name: {organ_name}
Target Layout Strategy: {layout_strategy}
Components to draw:
{components_json}
"""

async def test_llm_svg_generation():
    genome_path = os.path.join(project_root, "Frontend", "2. GENOME", "genome_enriched.json")
    with open(genome_path, 'r') as f:
        genome = json.load(f)
        
    # Pick n1_analysis (Analyse PNG)
    target_organ = None
    for n0 in genome.get("n0_phases", []):
        for n1 in n0.get("n1_sections", []):
            if n1["id"] == "n1_analysis": # Contains preview, launch button, regenerate
                target_organ = n1
                break
    
    if not target_organ:
        print("Organ not found")
        return
        
    components = []
    for feature in target_organ.get("n2_features", []):
        components.extend(feature.get("n3_components", []))
        
    prompt = PROMPT.format(
        layout_strategy=target_organ.get("layout_strategy"),
        organ_name=target_organ.get("name"),
        components_json=json.dumps(components, indent=2)
    )
    
    client = GeminiClient()
    print("Generating Premium SVG with Gemini...")
    import asyncio
    result = await client.generate(prompt=prompt)
    
    svg_content = result.code if hasattr(result, 'code') else str(result)
    if "```svg" in svg_content:
        svg_content = svg_content.split("```svg")[1].split("```")[0].strip()
    elif "```xml" in svg_content:
        svg_content = svg_content.split("```xml")[1].split("```")[0].strip()
    elif "```" in svg_content:
        svg_content = svg_content.split("```")[1].split("```")[0].strip()
        
    output_path = os.path.join(project_root, "Frontend", "2. GENOME", "test_gemini_analysis.svg")
    with open(output_path, 'w') as f:
        f.write(svg_content)
        
    print(f"SVG saved to {output_path}")

if __name__ == "__main__":
    import asyncio
    asyncio.run(test_llm_svg_generation())
