"""
API Key URL Refresher — Background task that searches for provider dashboard URLs
using Gemini + Google Search, caches results for 24h, validates with HTTP check.
Fallback: verified static URLs for providers that Gemini can't find.
"""
import os
import json
import asyncio
import time
import urllib.request
import urllib.error
from pathlib import Path
from loguru import logger

CACHE_PATH = Path(__file__).parent.parent.parent / "db" / "api_key_urls.json"
CACHE_TTL = 24 * 3600  # 24 hours

PROVIDERS = ["gemini", "groq", "openai", "kimi", "mimo", "deepseek", "qwen", "watson"]

# Verified fallback URLs (tested via HTTP HEAD/GET)
# pricing: "gratuit" or "payant" — clearly indicated in UI
# price_hint: free form price description for the UI
VERIFIED_URLS = {
    "gemini":   {"url": "https://aistudio.google.com/app/apikey", "instructions": "Gratuit — Google AI Studio, 15 RPM gratuit", "pricing": "gratuit", "price_hint": "Gratuit (15 RPM)"},
    "groq":     {"url": "https://console.groq.com/keys", "instructions": "Gratuit — console Groq, quota limité gratuit", "pricing": "gratuit", "price_hint": "Gratuit (quota limité)"},
    "openai":   {"url": "https://platform.openai.com/api-keys", "instructions": "Payant — OpenAI Platform, $5 de crédit offerts", "pricing": "payant", "price_hint": "~$0.005/1K tokens"},
    "deepseek": {"url": "https://platform.deepseek.com/api-keys", "instructions": "Payant — DeepSeek, très bon rapport qualité/prix", "pricing": "payant", "price_hint": "~$0.001/1K tokens"},
    "qwen":     {"url": "https://account.alibabacloud.com/login/login.htm?spm=5176.12901015-2.0.0.4af2525cpffRpb", "instructions": "Gratuit — Alibaba Cloud (DashScope), quota généreux", "pricing": "gratuit", "price_hint": "Gratuit (quota généreux)"},
    "kimi":     {"url": "https://platform.moonshot.cn/console/api-keys", "instructions": "Payant — Moonshot Platform (Kimi)", "pricing": "payant", "price_hint": "~$0.01/1K tokens"},
    "mimo":     {"url": "https://openrouter.ai/keys", "instructions": "Gratuit — OpenRouter, accès gratuit à MIMO-V2-Omni", "pricing": "gratuit", "price_hint": "Gratuit (via OpenRouter)"},
    "watson":   {"url": "https://cloud.ibm.com/catalog/services/watsonx-ai", "instructions": "Gratuit — IBM Cloud Lite + WatsonX", "pricing": "gratuit", "price_hint": "Gratuit (Lite tier)"},
}


def validate_url(url: str, timeout: int = 8) -> bool:
    """Validate URL is reachable (accepts 200, 302, 403, 405 — pages exist but may block HEAD)."""
    try:
        req = urllib.request.Request(url, method='HEAD')
        req.add_header('User-Agent', 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)')
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return resp.status < 500
    except urllib.error.HTTPError as e:
        # 403 = Cloudflare (page exists), 405 = HEAD blocked (page exists), 404 = gone
        return e.code in (200, 301, 302, 403, 405)
    except Exception:
        return False


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


async def refresh_all_urls(max_retries: int = 3):
    """Search for all provider URLs using Gemini + Search with retries."""
    urls = {}

    for attempt in range(max_retries):
        try:
            from Backend.Prod.models.gemini_client import GeminiClient
            gemini = GeminiClient()

            if attempt == 0:
                prompt = (
                    "You are an expert researcher. Find the EXACT dashboard URL where developers create API keys for EACH of these providers:\n"
                    + ", ".join(PROVIDERS) + "\n\n"
                    "Rules:\n"
                    "- Search Google for the CURRENT, VALID dashboard URL for each provider\n"
                    "- The URL must be the page where you CREATE a new API key (not docs, not pricing)\n"
                    "- Include the full HTTPS URL with path\n"
                    "- Also provide a 1-line French instruction indicating if it's free (gratuit) or paid (payant)\n"
                    "- If you cannot find a valid URL for a provider, return null for that provider\n\n"
                    "Respond ONLY with a JSON object:\n"
                    "{\n"
                    '  "gemini": {"url": "https://...", "instructions": "..."},\n'
                    '  ...\n'
                    "}\n"
                    "Do NOT guess. Use Google Search to verify."
                )
            else:
                missing = [p for p in PROVIDERS if p not in urls]
                prompt = (
                    f"Retry {attempt+1}/{max_retries}. I need the EXACT API key creation dashboard URL for:\n"
                    + ", ".join(missing) + "\n\n"
                    "NOT documentation. NOT homepage. The KEY MANAGEMENT page.\n"
                    "Return ONLY JSON: { \"provider\": {\"url\": \"https://...\", \"instructions\": \"...\"} }\n"
                    "Indicate gratuit/payant in instructions.\n"
                )

            result = await gemini.generate(
                prompt=prompt,
                output_constraint="JSON only",
                use_search=True,
                max_tokens=2000,
                temperature=0.1,
            )

            if not result.success:
                logger.warning(f"[API URLs] Gemini attempt {attempt+1} failed: {result.error}")
                if attempt < max_retries - 1:
                    await asyncio.sleep(2)
                continue

            # Parse JSON
            raw = result.code.strip()
            for marker in ["```json", "```"]:
                if raw.startswith(marker):
                    raw = raw[len(marker):]
            if raw.endswith("```"):
                raw = raw[:-3]
            raw = raw.strip()

            new_urls = json.loads(raw)

            # Validate with HTTP check
            for provider in list(new_urls.keys()):
                entry = new_urls[provider]
                if isinstance(entry, dict) and "url" in entry and entry["url"].startswith("https://"):
                    url = entry["url"]
                    if validate_url(url):
                        if not entry.get("instructions"):
                            entry["instructions"] = f"Crée une clé API {provider}"
                        urls[provider] = entry
                        logger.info(f"[API URLs] ✅ {provider}: {url}")
                    else:
                        logger.warning(f"[API URLs] ❌ {provider}: HTTP validation failed → {url}")
                else:
                    del new_urls[provider]

            found_count = len([p for p in PROVIDERS if p in urls])
            if found_count >= len(PROVIDERS) - 1:
                break

            if attempt < max_retries - 1:
                await asyncio.sleep(2)

        except Exception as e:
            logger.error(f"[API URLs] Attempt {attempt+1} exception: {e}")
            if attempt < max_retries - 1:
                await asyncio.sleep(2)
            continue

    # Fill in any missing providers with verified fallback URLs
    for provider in PROVIDERS:
        if provider not in urls and provider in VERIFIED_URLS:
            urls[provider] = VERIFIED_URLS[provider]
            logger.info(f"[API URLs] 📌 {provider}: using verified fallback")

    if urls:
        save_cached_urls(urls)
        logger.info(f"[API URLs] Final: {len(urls)}/{len(PROVIDERS)} URLs cached")
    else:
        urls = load_cached_urls()
        if urls:
            logger.info(f"[API URLs] Search yielded no results, keeping {len(urls)} cached URLs")

    return urls
