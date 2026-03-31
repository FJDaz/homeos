import asyncio
import tempfile
import time
from pathlib import Path
from playwright.async_api import async_playwright
from loguru import logger

class BrowserRenderer:
    """Headless Playwright rendering engine for Visual QA Loop."""
    
    @staticmethod
    async def capture_screenshot(html_content: str, width: int = 1440, height: int = 900) -> Path:
        """
        Rends the HTML content in a headless browser and returns the path to the screenshot PNG.
        """
        start_time = time.time()
        
        # We need a physical temp file for Playwright to load relative assets (if any) or properly structure DOM.
        # But since we use absolute CDN links or inline CSS, writing to a temp file is bulletproof.
        temp_html = tempfile.NamedTemporaryFile(delete=False, suffix=".html")
        temp_html_path = Path(temp_html.name)
        temp_html_path.write_text(html_content, encoding="utf-8")
        
        output_png = tempfile.NamedTemporaryFile(delete=False, suffix=".png")
        output_png_path = Path(output_png.name)
        
        try:
            async with async_playwright() as p:
                browser = await p.chromium.launch(headless=True)
                page = await browser.new_page(viewport={'width': width, 'height': height})
                
                # Navigate to the temp file
                await page.goto(f"file://{temp_html_path.absolute()}")
                
                # Wait for any network idle (fonts, CDNs) up to 2.5s to not hang the loop
                try:
                    await page.wait_for_load_state("networkidle", timeout=2500)
                except Exception:
                    logger.debug("BrowserRenderer: Networkidle timeout reached, capturing anyway.")
                    pass
                
                # Screenshot
                await page.screenshot(path=str(output_png_path), full_page=True)
                
                await browser.close()
                
        except Exception as e:
            logger.error(f"BrowserRenderer capture failed: {e}")
            raise
        finally:
            # Cleanup HTML, keep PNG for the DA (calling code will clean it up)
            try:
                temp_html_path.unlink()
            except Exception:
                pass
                
        elapsed = time.time() - start_time
        logger.debug(f"📸 Playwright render took {elapsed:.2f}s -> {output_png_path}")
        return output_png_path
