import json
import asyncio
from pathlib import Path
from playwright.async_api import async_playwright
from loguru import logger

class ManifestInferer:
    """Uses Playwright to read the rendered DOM and infer a structured manifest.json for Figma."""
    
    @staticmethod
    async def infer_from_html(html_path: Path) -> dict:
        logger.info(f"🔍 Inferring manifest from {html_path}")
        
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()
            
            # Use absolute path for file://
            abs_path = "file://" + str(html_path.absolute())
            await page.goto(abs_path)
            
            # Extract elements from the DOM
            # We look for anything that looks like a structural component or has text
            elements = await page.evaluate('''() => {
                const results = [];
                // Target all direct children of body and things with IDs or common component classes
                const items = document.querySelectorAll('section, nav, header, footer, div, button, h1, h2, h3, p, input, textarea');
                
                items.forEach((el, index) => {
                    const rect = el.getBoundingClientRect();
                    // Filters: only visible elements with size
                    if (rect.width > 2 && rect.height > 2 && el.offsetParent !== null) {
                        // Extract all data-af-* attributes
                        const metadata = {};
                        for (const attr of el.attributes) {
                            if (attr.name.startsWith('data-af-')) {
                                metadata[attr.name] = attr.value;
                            }
                        }

                        results.push({
                            id: el.getAttribute('data-id') || el.id || `el_${index}`,
                            name: el.tagName + (el.className ? `.${el.className.split(' ')[0]}` : ''),
                            type: el.tagName,
                            x: Math.round(rect.left),
                            y: Math.round(rect.top),
                            width: Math.round(rect.width),
                            height: Math.round(rect.height),
                            text_content: el.innerText.substring(0, 50).trim(),
                            visual_hint: el.getAttribute('data-af-visual-hint') || '',
                            structural_role: el.getAttribute('data-af-region') || '',
                            metadata: metadata,
                            style: {
                                backgroundColor: window.getComputedStyle(el).backgroundColor,
                                color: window.getComputedStyle(el).color,
                                borderRadius: window.getComputedStyle(el).borderRadius
                            }
                        });
                    }
                });
                return results;
            }''')
            
            await browser.close()
            
            manifest = {
                "version": "2.0",
                "source": "AetherFlow Reality View",
                "extracted_at": str(Path('.')),
                "elements": elements
            }
            
            return manifest

    @staticmethod
    def save_manifest(manifest: dict, output_path: Path):
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(manifest, f, indent=2, ensure_ascii=False)
        logger.info(f"✅ Manifest saved to {output_path}")

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    
    async def run():
        inf = ManifestInferer()
        manifest = await inf.infer_from_html(Path(args.input))
        inf.save_manifest(manifest, Path(args.output))
        
    asyncio.run(run())
