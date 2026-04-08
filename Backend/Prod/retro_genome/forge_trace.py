"""
ForgeTrace — Monitoring ultra-précis du pipeline de forge.

Trace chaque étape :
- Détection du format d'entrée
- Choix du convertisseur
- Appels LLM (modèle, tokens, coût, timing, retry)
- Fallbacks
- Écriture disque
- Mise à jour index.json

Un trace par job, pollable via GET /api/forge/{job_id}/trace
"""
import time
from typing import Optional
from loguru import logger


class ForgeStep:
    def __init__(self, name: str):
        self.name = name
        self.start = time.time()
        self.end: Optional[float] = None
        self.status = "running"
        self.detail = ""
        self.model = ""
        self.tokens_in = 0
        self.tokens_out = 0
        self.cost_usd = 0.0
        self.retries = 0
        self.error = ""

    def ok(self, detail: str = "", **kwargs):
        self.end = time.time()
        self.status = "ok"
        self.detail = detail
        for k, v in kwargs.items():
            setattr(self, k, v)

    def fail(self, error: str):
        self.end = time.time()
        self.status = "error"
        self.error = error

    @property
    def duration(self) -> float:
        return (self.end or time.time()) - self.start

    def to_dict(self) -> dict:
        d = {
            "name": self.name,
            "status": self.status,
            "duration_s": round(self.duration, 2),
        }
        if self.detail:
            d["detail"] = self.detail
        if self.model:
            d["model"] = self.model
        if self.tokens_in:
            d["tokens_in"] = self.tokens_in
        if self.tokens_out:
            d["tokens_out"] = self.tokens_out
        if self.cost_usd:
            d["cost_usd"] = round(self.cost_usd, 4)
        if self.retries:
            d["retries"] = self.retries
        if self.error:
            d["error"] = self.error
        return d


class ForgeTrace:
    def __init__(self, job_id: str, import_id: str, import_name: str):
        self.job_id = job_id
        self.import_id = import_id
        self.import_name = import_name
        self.steps: list[ForgeStep] = []
        self.overall_status = "running"
        self.started_at = time.time()
        self.ended_at: Optional[float] = None
        self.template_name: Optional[str] = None

    def step(self, name: str) -> ForgeStep:
        s = ForgeStep(name)
        self.steps.append(s)
        logger.info(f"[ForgeTrace] ▶ {name}")
        return s

    def summary(self) -> dict:
        total_time = round((self.ended_at or time.time()) - self.started_at, 2)
        total_cost = sum(s.cost_usd for s in self.steps)
        total_tokens = sum(s.tokens_in + s.tokens_out for s in self.steps)

        return {
            "job_id": self.job_id,
            "import_id": self.import_id,
            "import_name": self.import_name,
            "status": self.overall_status,
            "total_duration_s": total_time,
            "total_cost_usd": round(total_cost, 4),
            "total_tokens": total_tokens,
            "steps": [s.to_dict() for s in self.steps],
            "template_name": self.template_name,
        }

    def done(self, template_name: str):
        self.overall_status = "done"
        self.ended_at = time.time()
        self.template_name = template_name
        logger.info(f"[ForgeTrace] ✅ DONE — {template_name} in {self.summary()['total_duration_s']}s")

    def failed(self, error: str):
        self.overall_status = "error"
        self.ended_at = time.time()
        logger.error(f"[ForgeTrace] ❌ FAILED — {error}")


# Registry global
_FORGE_TRACES: dict[str, ForgeTrace] = {}


def new_trace(job_id: str, import_id: str, import_name: str) -> ForgeTrace:
    t = ForgeTrace(job_id, import_id, import_name)
    _FORGE_TRACES[job_id] = t
    return t


def get_trace(job_id: str) -> Optional[dict]:
    t = _FORGE_TRACES.get(job_id)
    if not t:
        return None
    return t.summary()
