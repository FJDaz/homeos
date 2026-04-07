import os
import sqlite3
import time
import threading
import json
import urllib.request
import urllib.error
from typing import Dict, List, Optional, Any
from datetime import datetime
from pathlib import Path

# --- CONFIGURATION ---
SULLIVAN_BASE_DIR = Path(__file__).parent.resolve()
SULLIVAN_DB_PATH = SULLIVAN_BASE_DIR / "db/metrics.db"
# S'assurer que le dossier db existe
SULLIVAN_DB_PATH.parent.mkdir(parents=True, exist_ok=True)

PULSE_INTERVAL_S = 120
PROBE_TIMEOUT_S = 3
LOCAL_AI_ENABLED = False  # Désactivé sur Intel

def _load_env():
    """Charge le .env AetherFlow dans os.environ (setdefault)."""
    # On cherche dans le dossier parent (Frontend/3. STENCILER -> Frontend -> Root)
    env_path = Path(__file__).parent.parent.parent / ".env"
    if env_path.exists():
        for line in env_path.read_text().splitlines():
            if "=" in line and not line.startswith("#"):
                k, _, v = line.partition("=")
                os.environ.setdefault(k.strip(), v.strip())

# Charger l'environnement au boot du module
_load_env()

# --- TAXONOMIE UNIFIÉE ---
# Mapping des types de run vers les modèles primaires et fallbacks
TIER_MAP = {
    "quick":        {"primary": {"provider": "mimo", "model": "mimo-v2-flash"}, "fallback": {"provider": "gemini", "model": "gemini-2.5-flash"}},
    "construct":    {"primary": {"provider": "mimo", "model": "mimo-v2-flash"}, "fallback": {"provider": "gemini", "model": "gemini-2.5-flash"}},
    "conseil":      {"primary": {"provider": "mimo", "model": "mimo-v2-flash"}, "fallback": {"provider": "gemini", "model": "gemini-2.5-flash"}},
    "architect":    {"primary": {"provider": "mimo", "model": "mimo-v2-flash"}, "fallback": {"provider": "gemini", "model": "gemini-2.5-flash"}},
    "code-simple":  {"primary": {"provider": "mimo", "model": "mimo-v2-flash"}, "fallback": {"provider": "gemini", "model": "gemini-2.5-flash"}},
    "code-complex": {"primary": {"provider": "mimo", "model": "mimo-v2-flash"}, "fallback": {"provider": "gemini", "model": "gemini-2.5-flash"}},
    "wire":         {"primary": {"provider": "mimo", "model": "mimo-v2-flash"}, "fallback": {"provider": "gemini", "model": "gemini-2.5-flash"}},
    "diagnostic":   {"primary": {"provider": "mimo", "model": "mimo-v2-flash"}, "fallback": {"provider": "gemini", "model": "gemini-2.5-flash"}},
}

class SullivanSentinel:
    """Gestionnaire de métriques de performance AI via SQLite."""
    
    def __init__(self, db_path: str = SULLIVAN_DB_PATH):
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS ai_calls (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                provider TEXT,
                model TEXT,
                run_type TEXT,
                latency_ms INTEGER,
                success INTEGER,
                ts DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        conn.commit()
        conn.close()

    def log(self, provider: str, model: str, run_type: str, latency_ms: int, success: bool):
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO ai_calls (provider, model, run_type, latency_ms, success) VALUES (?, ?, ?, ?, ?)",
                (provider, model, run_type, int(latency_ms), 1 if success else 0)
            )
            conn.commit()
            conn.close()
        except Exception as e:
            print(f"[SENTINEL] Error logging metrics: {e}")

    def get_avg_latency(self, provider: str, window_s: int = 300) -> float:
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute(
                "SELECT AVG(latency_ms) FROM ai_calls WHERE provider = ? AND success = 1 AND ts > datetime('now', ?)",
                (provider, f'-{window_s} seconds')
            )
            res = cursor.fetchone()[0]
            conn.close()
            return res if res else 0.0
        except Exception:
            return 0.0

PROBE_CACHE_TTL_S = 600  # Re-probe si cache > 10 min

# Tous les providers connus avec leur modèle de probe
ALL_PROVIDERS = [
    ("gemini",    "gemini-2.5-flash"),
    ("mimo",      "mimo-v2-flash"),
    ("groq",      "llama-3.3-70b-versatile"),
    ("codestral", "codestral-latest"),
]

class SullivanPulse:
    """Probe lazy : sonde TOUS les providers en parallèle avant chaque run (TTL=10min)."""

    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super(SullivanPulse, cls).__new__(cls)
                cls._instance.metrics = {}
                cls._instance._last_full_probe_ts = 0
        return cls._instance

    def start(self):
        print("[PULSE] Lazy probe mode (on-demand, all providers, TTL=10min).")

    def _is_stale(self) -> bool:
        return (time.time() - self._last_full_probe_ts) > PROBE_CACHE_TTL_S

    def _call_api_lite(self, provider: str, model: str) -> bool:
        """Appel minimal de 5 tokens pour tester la réactivité."""
        arbitrator = SullivanArbitrator()
        config = arbitrator._get_api_config(provider, model)
        if not config["api_key"]: return False

        prompt = "Say OK"
        try:
            if provider == "gemini":
                url = config["base_url"] + f"?key={config['api_key']}"
                data = {"contents": [{"parts": [{"text": prompt}]}]}
                req = urllib.request.Request(url, data=json.dumps(data).encode(), headers={"Content-Type": "application/json"})
                with urllib.request.urlopen(req, timeout=PROBE_TIMEOUT_S) as response:
                    return response.getcode() == 200
            else:
                # Format OpenAI (MiMo, Qwen)
                url = config["base_url"]
                data = {
                    "model": model,
                    "messages": [{"role": "user", "content": prompt}],
                    "max_tokens": 5
                }
                headers = {
                    "Authorization": f"Bearer {config['api_key']}",
                    "Content-Type": "application/json"
                }
                req = urllib.request.Request(url, data=json.dumps(data).encode(), headers=headers)
                with urllib.request.urlopen(req, timeout=PROBE_TIMEOUT_S) as response:
                    return response.getcode() == 200
        except Exception as e:
            print(f"[PULSE] Probe failed for {provider}: {e}")
            return False

    def _probe_all(self):
        # Gemini exclue de la probe (quota journalier limité — MiMo couvre le fallback)
        probes = [
            ("mimo", "mimo-v2-flash"),
        ]
        
        sentinel = SullivanSentinel()
        for provider, model in probes:
            start = time.time()
            success = self._call_api_lite(provider, model)
            latency = int((time.time() - start) * 1000)
            
            self.metrics[provider] = {
                "latency_ms": latency,
                "ok": success,
                "ts": datetime.now().isoformat()
            }
            # Log via Sentinel
            sentinel.log(provider, model, "pulse", latency, success)
            if success:
                print(f"[PULSE] {provider} ({model}): {latency}ms ✅")
            else:
                print(f"[PULSE] {provider} ({model}): FAILED ❌")

    def probe_all_if_stale(self):
        """Probe désactivée — MiMo seul provider actif, pas de quota à brûler."""
        return

    def get_status(self) -> Dict:
        return self.metrics

class SullivanArbitrator:
    """Arbitre dynamique qui choisit le meilleur modèle/provider."""
    
    def __init__(self):
        self.sentinel = SullivanSentinel()
        self.pulse = SullivanPulse()

    def pick(self, run_type: str) -> Dict:
        """Retourne MiMo directement — seul provider actif, probe désactivée."""
        return self._enrich_config({"provider": "mimo", "model": "mimo-v2-flash"})

    def _enrich_config(self, model_config: Dict) -> Dict:
        """Enrichit une config de modèle (provider, model) avec les clés et URLs API."""
        return self._get_api_config(model_config["provider"], model_config["model"])

    def _get_api_config(self, provider: str, model: str) -> Dict:
        """Récupère les clés et URLs depuis l'environnement."""
        config = {
            "provider": provider,
            "model": model,
            "api_key": "",
            "base_url": ""
        }
        
        if provider == "gemini":
            config["api_key"] = os.getenv("GOOGLE_API_KEY", "")
            config["base_url"] = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"
        elif provider == "mimo":
            config["api_key"] = os.getenv("MIMO_KEY", "")
            config["base_url"] = "https://api.xiaomimimo.com/v1/chat/completions"
        elif provider == "qwen":
            # Priorité SiliconFlow > OpenRouter
            sf_key = os.getenv("QWEN_KEY", "")
            if sf_key:
                config["api_key"] = sf_key
                config["base_url"] = "https://api.siliconflow.cn/v1/chat/completions"
            else:
                config["api_key"] = os.getenv("OPEN_ROUTER_QWEN_KEY", os.getenv("OPENROUTER_API_KEY", ""))
                config["base_url"] = "https://openrouter.ai/api/v1/chat/completions"
                
        return config

    def log_call(self, provider: str, model: str, run_type: str, latency_ms: int, success: bool):
        self.sentinel.log(provider, model, run_type, latency_ms, success)

    def dispatch(self, config: Dict, messages: List[Dict], system: str = "", tools: List[Dict] = None) -> Dict:
        """Exécute l'appel API vers le provider choisi avec le bon format."""
        provider = config["provider"]
        model = config["model"]
        api_key = config["api_key"]
        url = config["base_url"]
        
        start_time = time.time()
        try:
            if provider == "gemini":
                # Format Google Gemini
                full_url = f"{url}?key={api_key}"
                contents = []
                for m in messages:
                    # Conversion role assistant -> model pour Gemini
                    role = "model" if m["role"] == "assistant" else m["role"]
                    contents.append({"role": role, "parts": [{"text": m["content"]}]})
                
                payload = {
                    "contents": contents,
                    "generationConfig": {
                        "maxOutputTokens": 16384,
                        "temperature": 0.7
                    }
                }
                if system:
                    payload["systemInstruction"] = {"parts": [{"text": system}]}
                if tools:
                    payload["tools"] = tools # On passe les outils tels quels (format Google)
                
                req = urllib.request.Request(full_url, data=json.dumps(payload).encode(), headers={"Content-Type": "application/json"})
                with urllib.request.urlopen(req, timeout=60) as response:
                    res = json.loads(response.read().decode())
                    # Extraction texte (simplifiée)
                    parts = res['candidates'][0]['content']['parts']
                    text = parts[0].get('text', '')
                    fc = parts[0].get('functionCall')
                    
                    latency = int((time.time() - start_time) * 1000)
                    self.log_call(provider, model, "chat", latency, True)
                    return {"text": text, "function_call": fc, "success": True}

            else:
                # Format OpenAI (MiMo, Qwen)
                openai_messages = []
                if system:
                    openai_messages.append({"role": "system", "content": system})
                for m in messages:
                    openai_messages.append(m)
                
                payload = {
                    "model": model,
                    "messages": openai_messages,
                    "temperature": 0.7,
                    "max_tokens": 16384
                }
                # TODO: Mapper les outils vers format OpenAI si nécessaire
                
                headers = {
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json"
                }
                req = urllib.request.Request(url, data=json.dumps(payload).encode(), headers=headers)
                with urllib.request.urlopen(req, timeout=60) as response:
                    res = json.loads(response.read().decode())
                    text = res['choices'][0]['message']['content']
                    
                    latency = int((time.time() - start_time) * 1000)
                    self.log_call(provider, model, "chat", latency, True)
                    return {"text": text, "success": True}

        except Exception as e:
            print(f"[DISPATCH] Error with {provider}: {e}")
            return {"success": False, "error": str(e)}

if __name__ == "__main__":
    # Test Debug
    print("--- SULLIVAN ARBITRATOR TEST ---")
    arb = SullivanArbitrator()
    
    # Test Pick
    for rt in ["quick", "wire", "diagnostic"]:
        config = arb.pick(rt)
        print(f"Pick for {rt}: {config['provider']} ({config['model']})")
    
    # Test Pulse (Single round)
    print("\n--- PULSE TEST ---")
    pulse = SullivanPulse()
    pulse._probe_all()
    print("Status:", json.dumps(pulse.get_status(), indent=2))
