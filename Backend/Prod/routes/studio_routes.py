from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel
import json
from pathlib import Path
from typing import Dict, List

# Define the ComponentLibrary class
class ComponentNotFoundError(Exception):
    """Custom exception for component not found"""
    pass

class ComponentLibrary:
    def __init__(self, components_file: Path):
        """
        Initialize the component library by loading the pre-generated components from a JSON file.

        Args:
        - components_file (Path): The path to the JSON file containing the pre-generated components.
        """
        self.components_file = components_file
        self.cache = self.load_components()

    def load_components(self) -> Dict:
        """
        Load the pre-generated components from the JSON file.

        Returns:
        - Dict: A dictionary containing the pre-generated components.
        """
        with open(self.components_file, "r") as f:
            return json.load(f)

    def get_component(self, style_id: str, atom_type: str, variant: str = 'primary') -> Dict:
        """
        Get a component from the cache.

        Args:
        - style_id (str): The ID of the style.
        - atom_type (str): The type of the atom.
        - variant (str): The variant of the component (default is 'primary').

        Returns:
        - Dict: A dictionary containing the component.

        Raises:
        - ComponentNotFoundError: If the component is not found in the cache.
        """
        if style_id in self.cache and atom_type in self.cache[style_id]:
            return self.cache[style_id][atom_type]
        else:
            raise ComponentNotFoundError(f"Component not found: {style_id} - {atom_type}")

    def get_all_atoms(self, style_id: str) -> List[str]:
        """
        Get all atom types for a style.

        Args:
        - style_id (str): The ID of the style.

        Returns:
        - List[str]: A list of atom types.
        """
        if style_id in self.cache:
            return list(self.cache[style_id].keys())
        else:
            return []

    def render_component(self, style_id: str, atom_type: str, variant: str, props: Dict) -> str:
        """
        Render a component by injecting props into the HTML.

        Args:
        - style_id (str): The ID of the style.
        - atom_type (str): The type of the atom.
        - variant (str): The variant of the component.
        - props (Dict): A dictionary of props to inject into the HTML.

        Returns:
        - str: The rendered HTML.
        """
        component = self.get_component(style_id, atom_type, variant)
        html = component["html"]
        for prop, value in props.items():
            html = html.replace(f"{{{prop}}}", value)
        return html

    def get_css_classes(self, style_id: str, atom_type: str, variant: str) -> List[str]:
        """
        Get the CSS classes for a component.

        Args:
        - style_id (str): The ID of the style.
        - atom_type (str): The type of the atom.
        - variant (str): The variant of the component.

        Returns:
        - List[str]: A list of CSS classes.
        """
        component = self.get_component(style_id, atom_type, variant)
        return component["css_classes"]

# Initialize the ComponentLibrary
components_file = Path("Backend/Prod/sullivan/pregenerated_components.json")
library = ComponentLibrary(components_file)

# Create the FastAPI app
app = FastAPI()

# Define the endpoint
@app.get("/api/components/library/{style_id}/{atom_type}", 
          summary='Tier 1 Component Library - Instant component retrieval (0ms latency)',
          description='Get a pre-generated component from the library')
async def get_component(style_id: str, 
                        atom_type: str, 
                        variant: str = Query("primary", description="The variant of the component"),
                        props: str = Query(None, description="A JSON string for customizing the component")):
    """
    Get a pre-generated component from the library.

    Args:
    - style_id (str): The ID of the style.
    - atom_type (str): The type of the atom.
    - variant (str): The variant of the component (default is 'primary').
    - props (str): A JSON string for customizing the component (optional).

    Returns:
    - Dict: A dictionary containing the component's HTML, CSS classes, accessibility features, and cache hit status.
    """
    try:
        # Get the component from the library
        component = library.get_component(style_id, atom_type, variant)
        
        # Render the component with props if provided
        if props:
            props_dict = json.loads(props)
            html = library.render_component(style_id, atom_type, variant, props_dict)
        else:
            html = component["html"]
        
        # Get the CSS classes for the component
        css_classes = library.get_css_classes(style_id, atom_type, variant)
        
        # Return the component's data
        return {
            "html": html,
            "css_classes": css_classes,
            "accessibility": component.get("accessibility", []),
            "cache_hit": True
        }
    except ComponentNotFoundError as e:
        # Raise a 404 error if the component is not found
        raise HTTPException(status_code=404, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel
import json
from pathlib import Path
from typing import Dict, List, Optional

# Define the ComponentLibrary class
class ComponentNotFoundError(Exception):
    """Custom exception for component not found"""
    pass

class ComponentLibrary:
    def __init__(self, components_file: Path):
        """
        Initialize the component library by loading the pre-generated components from a JSON file.

        Args:
        - components_file (Path): The path to the JSON file containing the pre-generated components.
        """
        self.components_file = components_file
        self.cache = self.load_components()

    def load_components(self) -> Dict:
        """
        Load the pre-generated components from the JSON file.

        Returns:
        - Dict: A dictionary containing the pre-generated components.
        """
        with open(self.components_file, "r") as f:
            return json.load(f)

    def get_component(self, style_id: str, atom_type: str, variant: str = 'primary') -> Dict:
        """
        Get a component from the cache.

        Args:
        - style_id (str): The ID of the style.
        - atom_type (str): The type of the atom.
        - variant (str): The variant of the component (default is 'primary').

        Returns:
        - Dict: A dictionary containing the component.

        Raises:
        - ComponentNotFoundError: If the component is not found in the cache.
        """
        try:
            # Access the nested structure: cache["styles"][style_id][atom_type][variant]
            component = self.cache["styles"][style_id][atom_type][variant]
            return component
        except KeyError:
            raise ComponentNotFoundError(
                f"Component not found: style_id='{style_id}', atom_type='{atom_type}', variant='{variant}'"
            )

    def get_all_atoms(self, style_id: str) -> List[str]:
        """
        Get all atom types for a style.

        Args:
        - style_id (str): The ID of the style.

        Returns:
        - List[str]: A list of atom types.
        """
        try:
            return list(self.cache["styles"][style_id].keys())
        except KeyError:
            return []

    def render_component(self, style_id: str, atom_type: str, variant: str, props: Dict) -> str:
        """
        Render a component by injecting props into the HTML.

        Args:
        - style_id (str): The ID of the style.
        - atom_type (str): The type of the atom.
        - variant (str): The variant of the component.
        - props (Dict): A dictionary of props to inject into the HTML.

        Returns:
        - str: The rendered HTML.
        """
        component = self.get_component(style_id, atom_type, variant)
        html = component["html"]

        # Handle different types of prop injection
        for prop, value in props.items():
            # Handle text content injection
            if prop == "text":
                # For buttons and badges, replace the text content
                if atom_type in ["button", "badge"]:
                    html = self._replace_text_content(html, value)
                # For cards, replace the card body content
                elif atom_type == "card":
                    html = self._replace_card_content(html, value)
            # Handle placeholder replacement
            elif prop == "placeholder":
                html = html.replace(f"placeholder='{prop}'", f"placeholder='{value}'")
            # Handle other attributes
            else:
                # Replace attributes in the HTML
                html = html.replace(f"{prop}=''", f"{prop}='{value}'")
                html = html.replace(f"{prop}='{prop}'", f"{prop}='{value}'")

        return html

    def _replace_text_content(self, html: str, text: str) -> str:
        """
        Replace the text content in HTML elements.

        Args:
        - html (str): The HTML string to modify.
        - text (str): The text to insert.

        Returns:
        - str: The modified HTML.
        """
        # For buttons and badges, replace the content between the tags
        if "button" in html or "badge" in html:
            start_tag_end = html.find(">")
            end_tag_start = html.rfind("<")
            return html[:start_tag_end+1] + text + html[end_tag_start:]
        return html

    def _replace_card_content(self, html: str, content: str) -> str:
        """
        Replace the content in card components.

        Args:
        - html (str): The HTML string to modify.
        - content (str): The content to insert.

        Returns:
        - str: The modified HTML.
        """
        # Find the card-body and replace its content
        start = html.find("<div class='card-body'")
        if start == -1:
            return html

        start_tag_end = html.find(">", start) + 1
        end_tag_start = html.find("</div>", start_tag_end)

        if end_tag_start == -1:
            return html

        # Rebuild the HTML with the new content
        return html[:start_tag_end] + content + html[end_tag_start:]

    def get_css_classes(self, style_id: str, atom_type: str, variant: str) -> List[str]:
        """
        Get the CSS classes for a component.

        Args:
        - style_id (str): The ID of the style.
        - atom_type (str): The type of the atom.
        - variant (str): The variant of the component.

        Returns:
        - List[str]: A list of CSS classes.
        """
        component = self.get_component(style_id, atom_type, variant)
        return component["css_classes"]

# Initialize the ComponentLibrary
components_file = Path("Backend/Prod/sullivan/pregenerated_components.json")
library = ComponentLibrary(components_file)

# Create the FastAPI app
app = FastAPI()

# Define the endpoint for getting a component
@app.get("/api/components/library/{style_id}/{atom_type}",
          summary='Tier 1 Component Library - Instant component retrieval (0ms latency)',
          description='Get a pre-generated component from the library')
async def get_component(style_id: str,
                        atom_type: str,
                        variant: str = Query("primary", description="The variant of the component"),
                        props: Optional[str] = Query(None, description="A JSON string for customizing the component")):
    """
    Get a pre-generated component from the library.

    Args:
    - style_id (str): The ID of the style.
    - atom_type (str): The type of the atom.
    - variant (str): The variant of the component (default is 'primary').
    - props (str): A JSON string for customizing the component (optional).

    Returns:
    - Dict: A dictionary containing the component's HTML, CSS classes, accessibility features, and cache hit status.

    Raises:
    - HTTPException: 404 if the component is not found.
    """
    try:
        # Get the component from the library
        component = library.get_component(style_id, atom_type, variant)

        # Render the component with props if provided
        if props:
            try:
                props_dict = json.loads(props)
                html = library.render_component(style_id, atom_type, variant, props_dict)
            except json.JSONDecodeError:
                raise HTTPException(status_code=400, detail="Invalid JSON format for props")
        else:
            html = component["html"]

        # Get the CSS classes for the component
        css_classes = library.get_css_classes(style_id, atom_type, variant)

        # Return the component's data
        return {
            "html": html,
            "css_classes": css_classes,
            "accessibility": component.get("accessibility", []),
            "cache_hit": True
        }
    except ComponentNotFoundError as e:
        # Raise a 404 error if the component is not found
        raise HTTPException(status_code=404, detail=str(e))

# Define the endpoint for getting all atoms for a style
@app.get("/api/components/library/{style_id}/atoms",
          summary='Get all atom types for a style',
          description='Retrieve all available atom types for a given style')
async def get_atoms(style_id: str):
    """
    Get all atom types for a style.

    Args:
    - style_id (str): The ID of the style.

    Returns:
    - Dict: A dictionary containing the list of atom types and cache hit status.
    """
    atoms = library.get_all_atoms(style_id)
    return {
        "atoms": atoms,
        "cache_hit": True
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)