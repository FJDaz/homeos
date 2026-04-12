"""
M294: Model Health Manager — Circuit Breaker + Passive Health Monitoring.
Zero-cost: no ping. Uses real requests as health sensors.
Shared across all users — if one student triggers circuit breaker, the whole class benefits.
"""
import os
import json
import time
import logging
from pathlib import Path
from typing import Dict, Optional, List
from threading import Lock

logger = logging.getLogger("AetherFlowV3")

# --- PATHS ---
CWD = Path(__file__).parent.parent.resolve()
ROOT_DIR = CWD.parent.parent
DB_DIR = ROOT_DIR / "db"
HEALTH_FILE = DB_DIR / "provider_health.json"

# --- Circuit Breaker States ---
HEALTHY = "healthy"
DEGRADED = "degraded"
DOWN = "down"

FAILURE_THRESHOLD = 3  # failures before circuit opens
RECOVERY_TIMEOUT = 300  # seconds (5 min) before half-open test
DEGRADED_TTFT = 10.0    # seconds — if avg TTFT > this, mark degraded


class ProviderHealth:
    """Health state for a single provider."""
    def __init__(self, name: str):
        self.name = name
        self.status = HEALTHY
        self.failure_count = 0
        self.last_failure_ts = 0
        self.last_success_ts = 0
        self.ttft_samples: List[float] = []
        self.avg_ttft = 0.0
        self.total_requests = 0
        self.total_failures = 0

    def record_success(self, ttft: float = 0):
        self.failure_count = 0
        self.last_success_ts = time.time()
        self.total_requests += 1

        if ttft > 0:
            self.ttft_samples.append(ttft)
            # Keep last 20 samples for rolling average
            if len(self.ttft_samples) > 20:
                self.ttft_samples = self.ttft_samples[-20:]
            self.avg_ttft = sum(self.ttft_samples) / len(self.ttft_samples)

        if self.avg_ttft > DEGRADED_TTFT:
            self.status = DEGRADED
        else:
            self.status = HEALTHY

    def record_failure(self):
        self.failure_count += 1
        self.last_failure_ts = time.time()
        self.total_requests += 1
        self.total_failures += 1

        if self.failure_count >= FAILURE_THRESHOLD:
            self.status = DOWN
            logger.warning(f"[M294] Circuit breaker OPEN for {self.name} ({self.failure_count} failures)")
        elif self.avg_ttft > DEGRADED_TTFT:
            self.status = DEGRADED
        else:
            self.status = HEALTHY

    def can_attempt(self) -> bool:
        if self.status != DOWN:
            return True
        # Half-open: try after recovery timeout
        return (time.time() - self.last_failure_ts) > RECOVERY_TIMEOUT

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "status": self.status,
            "avg_ttft": round(self.avg_ttft, 2),
            "total_requests": self.total_requests,
            "total_failures": self.total_failures,
            "failure_streak": self.failure_count,
            "last_success": time.time() - self.last_success_ts if self.last_success_ts else None,
        }


class ModelHealthRegistry:
    """Global registry of provider health states. Singleton."""
    def __init__(self):
        self._lock = Lock()
        self.providers: Dict[str, ProviderHealth] = {}
        self._load_state()

    def get(self, name: str) -> ProviderHealth:
        with self._lock:
            if name not in self.providers:
                self.providers[name] = ProviderHealth(name)
            return self.providers[name]

    def record_success(self, name: str, ttft: float = 0):
        with self._lock:
            self.get(name).record_success(ttft)
        self._save_state()

    def record_failure(self, name: str):
        with self._lock:
            self.get(name).record_failure()
        self._save_state()

    def can_attempt(self, name: str) -> bool:
        return self.get(name).can_attempt()

    def get_best_provider(self, preferred_order: List[str]) -> Optional[str]:
        """Return the best available provider from preferred order list."""
        for name in preferred_order:
            if self.can_attempt(name):
                return name
        return None

    def get_all_status(self) -> List[dict]:
        return [p.to_dict() for p in self.providers.values()]

    def _load_state(self):
        if HEALTH_FILE.exists():
            try:
                data = json.loads(HEALTH_FILE.read_text(encoding='utf-8'))
                for name, state in data.items():
                    p = ProviderHealth(name)
                    p.status = state.get("status", HEALTHY)
                    p.failure_count = state.get("failure_streak", 0)
                    p.total_requests = state.get("total_requests", 0)
                    p.total_failures = state.get("total_failures", 0)
                    p.avg_ttft = state.get("avg_ttft", 0)
                    p.ttft_samples = [p.avg_ttft] * 5  # rough restore
                    self.providers[name] = p
            except Exception as e:
                logger.warning(f"[M294] Failed to load health state: {e}")

    def _save_state(self):
        try:
            data = {name: p.to_dict() for name, p in self.providers.items()}
            DB_DIR.mkdir(parents=True, exist_ok=True)
            HEALTH_FILE.write_text(json.dumps(data, indent=2), encoding='utf-8')
        except Exception as e:
            logger.warning(f"[M294] Failed to save health state: {e}")


# --- Global singleton ---
registry = ModelHealthRegistry()


def record_provider_success(name: str, ttft: float = 0):
    registry.record_success(name, ttft)

def record_provider_failure(name: str):
    registry.record_failure(name)

def get_best_provider(preferred: List[str]) -> Optional[str]:
    return registry.get_best_provider(preferred)

def get_all_health() -> List[dict]:
    return registry.get_all_status()
