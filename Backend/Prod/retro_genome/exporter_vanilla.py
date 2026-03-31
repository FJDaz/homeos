import os
import json
import zipfile
from pathlib import Path
from loguru import logger

def export_as_zip(project_name: str, html_content: str, output_dir: Path) -> Path:
    """Package reality.html and styles into a standalone ZIP."""
    safe_name = project_name.lower().replace(" ", "_")
    zip_path = output_dir / f"aetherflow_export_{safe_name}.zip"
    
    # We need to find the stenciler.css to include it
    # Local path relative to the script
    style_path = Path(__file__).parent.parent.parent / "Frontend" / "3. STENCILER" / "static" / "css" / "stenciler.css"
    
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as z:
        # 1. HTML (referenced as index.html for portability)
        # We might need to adjust the <link> tag to point to local style.css
        processed_html = html_content.replace('/static/css/stenciler.css', 'style.css')
        processed_html = processed_html.replace('href="static/css/stenciler.css"', 'href="style.css"')
        
        z.writestr("index.html", processed_html)
        
        # 2. CSS
        if style_path.exists():
            z.write(style_path, "style.css")
        else:
            logger.warning(f"stenciler.css not found at {style_path}")
            
    logger.info(f"📦 ZIP Export created: {zip_path}")
    return zip_path
