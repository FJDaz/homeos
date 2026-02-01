import json
import logging
from pathlib import Path
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)

class ScreenPlanner:
    def __init__(self):
        pass

    def plan_from_genome(self, genome: Dict) -> List[Dict]:
        """
        Create a plan from a genome dictionary.

        Args:
        - genome (Dict): A dictionary containing topology and endpoints.

        Returns:
        - plan (List[Dict]): A list of body dictionaries with corps_id, label, organes, and endpoints.
        """
        topology = genome["topology"]
        endpoints = genome["endpoints"]

        # Group endpoints by first segment of path or x_ui_hint
        endpoint_groups = {}
        for endpoint in endpoints:
            path = endpoint["path"]
            first_segment = path.split("/")[1]
            x_ui_hint = endpoint.get("x_ui_hint")
            if x_ui_hint:
                key = x_ui_hint
            else:
                key = first_segment
            if key not in endpoint_groups:
                endpoint_groups[key] = []
            endpoint_groups[key].append(endpoint)

        # Distribute endpoints across bodies
        bodies = []
        for i, topology_element in enumerate(topology):
            body = {
                "corps_id": str(i + 1),
                "label": topology_element,
                "organes": [],
                "endpoints": []
            }
            for key, group in endpoint_groups.items():
                if i < len(group):
                    endpoint = group[i]
                    body["organes"].append({
                        "endpoint_path": endpoint["path"],
                        "method": endpoint["method"],
                        "x_ui_hint": endpoint.get("x_ui_hint")
                    })
                    body["endpoints"].append(endpoint)
            bodies.append(body)

        return bodies

    def save_plan(self, plan: List[Dict], output_path: Path):
        """
        Save a plan to a JSON file.

        Args:
        - plan (List[Dict]): A list of body dictionaries.
        - output_path (Path): The path to the output JSON file.
        """
        with open(output_path, "w") as f:
            json.dump(plan, f, indent=4)

def load_genome(path: Path) -> Dict:
    """
    Load a genome from a JSON file.

    Args:
    - path (Path): The path to the genome JSON file.

    Returns:
    - genome (Dict): A dictionary containing topology and endpoints.
    """
    with open(path, "r") as f:
        return json.load(f)

def plan_screens(genome_path: Path, output_path: Optional[Path] = None) -> List[Dict]:
    """
    Plan screens from a genome file.

    Args:
    - genome_path (Path): The path to the genome JSON file.
    - output_path (Optional[Path]): The path to the output JSON file. Defaults to output/studio/screen_plan.json.

    Returns:
    - plan (List[Dict]): A list of body dictionaries.
    """
    genome = load_genome(genome_path)
    planner = ScreenPlanner()
    plan = planner.plan_from_genome(genome)
    if output_path is None:
        output_path = Path("output/studio/screen_plan.json")
    planner.save_plan(plan, output_path)
    return plan

if __name__ == "__main__":
    genome_path = Path("path/to/genome.json")
    output_path = Path("output/studio/screen_plan.json")
    plan = plan_screens(genome_path, output_path)
    logger.info("Plan generated successfully!")

import json
import logging
from pathlib import Path
from typing import List, Dict, Optional

# Define the logger
logger = logging.getLogger(__name__)

# Define the brutalist CSS style
BRUTALIST_CSS = """
body {
    font-family: Arial, sans-serif;
    margin: 0;
    padding: 0;
}

section {
    border: 1px solid #ccc;
    margin: 20px;
    padding: 20px;
}

h1 {
    font-size: 24px;
    margin: 0;
    padding: 0;
}

.header, .main, .footer {
    border: 1px solid #ccc;
    padding: 20px;
}

.placeholder {
    border: 1px solid #ccc;
    padding: 20px;
}
"""

def load_screen_plan(path: Path) -> List[Dict]:
    """
    Load the screen plan from a JSON file.

    Args:
        path: The path to the JSON file.

    Returns:
        A list of dictionaries representing the screen plan.
    """
    try:
        with open(path, 'r') as f:
            screen_plan = json.load(f)
            return screen_plan
    except json.JSONDecodeError as e:
        logger.error(f"Failed to load screen plan: {e}")
        return []

def load_design_principles(path: Optional[Path]) -> Dict:
    """
    Load the design principles from a JSON file.

    Args:
        path: The path to the JSON file.

    Returns:
        A dictionary representing the design principles.
    """
    if path is None:
        return {}
    try:
        with open(path, 'r') as f:
            design_principles = json.load(f)
            return design_principles
    except json.JSONDecodeError as e:
        logger.error(f"Failed to load design principles: {e}")
        return {}

def generate_corps_html(screen_plan: List[Dict], design_principles: Dict, base_url: str) -> str:
    """
    Generate the HTML for the corps.

    Args:
        screen_plan: The list of dictionaries representing the screen plan.
        design_principles: The dictionary representing the design principles.
        base_url: The base URL for the endpoints.

    Returns:
        The HTML for the corps.
    """
    html = ""
    for corps in screen_plan:
        corps_id = corps['corps_id']
        label = corps['label']
        organes = corps['organes']
        html += f"<section id='corps_{corps_id}'>"
        html += f"<h1>{label}</h1>"
        html += "<div class='header'>Header</div>"
        html += "<div class='main'>"
        for organe in organes:
            endpoint_path = organe['endpoint_path']
            method = organe['method']
            x_ui_hint = organe['x_ui_hint']
            html += f"<div class='placeholder' data-endpoint-path='{endpoint_path}' data-method='{method}' data-x-ui-hint='{x_ui_hint}'>Placeholder</div>"
        html += "</div>"
        html += "<div class='footer'>Footer</div>"
        html += "</section>"
    # Apply design principles
    if design_principles:
        colors = design_principles.get('colors', {})
        font_family = design_principles.get('font_family', '')
        html += f"<style>body {{ font-family: {font_family}; }}</style>"
        html += f"<style>.header {{ background-color: {colors.get('header', '#ccc')}; }}</style>"
        html += f"<style>.main {{ background-color: {colors.get('main', '#fff')}; }}</style>"
        html += f"<style>.footer {{ background-color: {colors.get('footer', '#ccc')}; }}</style>"
    return html

def build_corps(screen_plan_path: Path, output_path: Path, design_principles_path: Optional[Path], base_url: str) -> None:
    """
    Build the corps HTML.

    Args:
        screen_plan_path: The path to the screen plan JSON file.
        output_path: The path to the output HTML file.
        design_principles_path: The path to the design principles JSON file.
        base_url: The base URL for the endpoints.
    """
    screen_plan = load_screen_plan(screen_plan_path)
    design_principles = load_design_principles(design_principles_path)
    html = generate_corps_html(screen_plan, design_principles, base_url)
    with open(output_path, 'w') as f:
        f.write(html)
    logger.info(f"Corps HTML built successfully: {output_path}")

if __name__ == '__main__':
    screen_plan_path = Path("screen_plan.json")
    output_path = Path("corps.html")
    design_principles_path = Path("design_principles.json")
    base_url = "https://example.com"
    build_corps(screen_plan_path, output_path, design_principles_path, base_url)