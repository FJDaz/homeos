"""Capture screenshot from HTML content via Playwright (Chromium)."""
from __future__ import annotations

import asyncio
from typing import Union

from loguru import logger


async def capture_html_screenshot(
    html_content: str,
    viewport_width: int = 1280,
    viewport_height: int = 720,
    full_page: bool = False,
) -> bytes:
    """
    Render HTML and capture PNG screenshot using Playwright.

    Uses page.set_content(html) then page.screenshot(); no HTTP server needed.

    Args:
        html_content: Full HTML document (inline CSS/JS OK).
        viewport_width: Viewport width in px.
        viewport_height: Viewport height in px.
        full_page: If True, capture full scrollable page.

    Returns:
        PNG image bytes.
    """
    try:
        from playwright.async_api import async_playwright
    except ImportError:
        raise ImportError(
            "playwright is required for capture_html_screenshot. "
            "Install with: pip install playwright && playwright install chromium"
        ) from None

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        try:
            context = await browser.new_context(
                viewport={"width": viewport_width, "height": viewport_height},
            )
            page = await context.new_page()
            await page.set_content(html_content, wait_until="load")
            png_bytes = await page.screenshot(full_page=full_page, type="png")
            await context.close()
            logger.debug(
                f"Captured screenshot: {viewport_width}x{viewport_height}, "
                f"full_page={full_page}, {len(png_bytes)} bytes"
            )
            return png_bytes
        finally:
            await browser.close()


def capture_html_screenshot_sync(
    html_content: str,
    viewport_width: int = 1280,
    viewport_height: int = 720,
    full_page: bool = False,
) -> bytes:
    """Synchronous wrapper around capture_html_screenshot."""
    return asyncio.run(
        capture_html_screenshot(
            html_content,
            viewport_width=viewport_width,
            viewport_height=viewport_height,
            full_page=full_page,
        )
    )
