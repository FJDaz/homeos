"""
API Key URL Refresher — Background task that searches for provider dashboard URLs
using Gemini + Google Search, caches results for 24h.
"""
import os
import json
import asyncio
import time
from pathlib import Path
from loguru import logger

CACHE_PATH = Path(__file__).parent.parent.parent / "db" / "api_key_urls.json"
CACHE_TTL = 24 * 3600  # 24 hours

PROVIDERS = ["gemini", "groq", "openai", "kimi", "mimo", "deepseek", "qwen", "watson"]

def load_cached_urls():
    """Load cached URLs if file exists and not expired."""
    if CACHE_PATH.exists():
        try:
            data = json.loads(CACHE_PATH.read_text(encoding="utf-8"))
            if time.time() - data.get("cached_at", 0) < CACHE_TTL:
                return data.get("urls", {})
            else:
                logger.info("[API URLs] Cache expired, will refresh")
        except Exception as e:
            logger.warning(f"[API URLs] Failed to load cache: {e}")
    return {}

def save_cached_urls(urls: dict):
    """Save URLs to cache file."""
    CACHE_PATH.parent.mkdir(parents=True, exist_ok=True)
    data = {"cached_at": time.time(), "urls": urls}
    CACHE_PATH.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
    logger.info(f"[API URLs] Cached {len(urls)} URLs to {CACHE_PATH}")


async def refresh_all_urls():
    """Search for all provider URLs using Gemini + Search."""
    try:
        from Backend.Prod.models.gemini_client import GeminiClient
        gemini = GeminiClient()

        prompt = (
            "You are an expert researcher. Find the EXACT dashboard URL where developers create API keys for EACH of these providers:\n"
            + ", ".join(PROVIDERS) + "\n\n"
            "Rules:\n"
            "- Search Google for the CURRENT, VALID dashboard URL for each provider\n"
            "- The URL must be the page where you CREATE a new API key (not docs, not pricing)\n"
            "- Include the full HTTPS URL with path\n"
            "- Also provide a 1-line French instruction on how to create a key\n"
            "- If you cannot find a valid URL for a provider, return null for that provider\n\n"
            "Respond ONLY with a JSON object:\n"
            "{\n"
            '  "gemini": {"url": "https://...", "instructions": "..."},\n'
            '  "groq": {"url": "https://...", "instructions": "..."},\n'
            '  ...\n'
            "}\n"
            "Do NOT guess. If uncertain, use the Google Search tool to verify each URL."
        )

        result = await gemini.generate(
            prompt=prompt,
            output_constraint="JSON only",
            use_search=True,
            max_tokens=2000,
            temperature=0.1,
        )

        if not result.success:
            logger.error(f"[API URLs] Gemini search failed: {result.error}")
            return load_cached_urls()  # Keep old cache

        # Parse JSON from response
        raw = result.code.strip()
        if raw.startswith("```json"):
            raw = raw[7:]
        elif raw.startswith("```"):
            raw = raw[3:]
        if raw.endswith("```"):
            raw = raw[:-3]
        raw = raw.strip()

        urls = json.loads(raw)

        # Validate structure
        for provider in PROVIDERS:
            if provider in urls:
                entry = urls[provider]
                if isinstance(entry, dict) and "url" in entry and entry["url"].startswith("https://"):
                    if not entry.get("instructions"):
                        entry["instructions"] = f"Crée une clé API {provider}"
                else:
                    del urls[provider]  # Remove invalid entry

        save_cached_urls(urls)
        logger.info(f"[API URLs] Refreshed {len(urls)} URLs successfully")
        return urls

    except Exception as e:
        logger.error(f"[API URLs] Refresh error: {e}", exc_info=True)
        return load_cached_urls()  # Keep old cache on error
