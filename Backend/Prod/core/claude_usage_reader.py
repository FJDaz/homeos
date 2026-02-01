"""
Claude Code / Cursor usage reader (read-only).

Reads usage from Claude Code config dir (~/.config/claude or CLAUDE_CONFIG_DIR):
projects/*/*.jsonl (one file = one session). Aggregates tokens and cost.
Schema aligned with Claude-Code-Usage-Monitor and Claude Code JSONL format:
  https://github.com/Maciek-roboblog/Claude-Code-Usage-Monitor

Supports snake_case (usage.input_tokens) and camelCase (inputTokens, outputTokens,
cacheCreationTokens, cacheReadTokens, totalTokens, totalCost). Uses totalCost when
present, else estimates from Claude Sonnet pricing.
No writes to Claude config; optional snapshot to ~/.aetherflow/ is V2.
"""
import json
import os
from pathlib import Path
from typing import Any, Dict, Optional

from loguru import logger

# Claude Sonnet pricing (USD per 1M tokens) - fallback if JSONL has no cost
DEFAULT_INPUT_PER_M = 3.0
DEFAULT_OUTPUT_PER_M = 15.0


def _get_claude_config_dir() -> Optional[Path]:
    """Resolve Claude config directory (CLAUDE_CONFIG_DIR, ~/.config/claude, ~/.claude)."""
    dir_env = os.environ.get("CLAUDE_CONFIG_DIR")
    if dir_env:
        p = Path(dir_env).expanduser().resolve()
        if p.exists():
            return p
    for base in [
        Path.home() / ".config" / "claude",
        Path.home() / ".claude",
    ]:
        if (base / "projects").exists():
            return base
    return None


def _get_claude_cursor_config_dir() -> Optional[Path]:
    """Optional config dir for Cursor-only usage (CLAUDE_CURSOR_CONFIG_DIR). If set, Cursor usage is read from here and standalone from CLAUDE_CONFIG_DIR."""
    dir_env = os.environ.get("CLAUDE_CURSOR_CONFIG_DIR")
    if not dir_env:
        return None
    p = Path(dir_env).expanduser().resolve()
    return p if p.exists() and (p / "projects").is_dir() else None


def _is_cursor_source(data: Dict[str, Any]) -> Optional[bool]:
    """True if line is from Cursor, False if standalone, None if unknown. Checks client, source, origin, app_id, ide."""
    for key in ("client", "source", "origin", "app_id", "ide"):
        val = data.get(key)
        if val is None:
            continue
        s = str(val).lower()
        if "cursor" in s:
            return True
        if s in ("claude", "standalone", "app", "web"):
            return False
    return None


def _safe_int(val: Any) -> int:
    """Coerce to int; None or invalid -> 0."""
    if val is None:
        return 0
    try:
        return int(val)
    except (TypeError, ValueError):
        return 0


def _parse_usage_from_line(line: str) -> Dict[str, Any]:
    """
    Extract token counts and cost from a JSONL line.
    Aligned with Claude-Code-Usage-Monitor / Claude Code format:
    - snake_case: usage.input_tokens, usage.output_tokens, cache_creation_input_tokens
    - camelCase: inputTokens, outputTokens, cacheCreationTokens, cacheReadTokens, totalCost
    Returns dict with input_tokens, output_tokens, total_tokens, cache_tokens, cost_usd (or None).
    """
    out: Dict[str, Any] = {
        "input_tokens": 0,
        "output_tokens": 0,
        "total_tokens": 0,
        "cache_tokens": 0,
        "cost_usd": None,
        "is_cursor": None,
    }
    try:
        data = json.loads(line.strip())
        if not isinstance(data, dict):
            return out
        out["is_cursor"] = _is_cursor_source(data)
        # Nested usage (Anthropic API style)
        usage = data.get("usage") or (data.get("message") or {}).get("usage")
        if isinstance(usage, dict):
            in_tok = usage.get("input_tokens") or usage.get("input") or usage.get("inputTokens")
            out_tok = usage.get("output_tokens") or usage.get("output") or usage.get("outputTokens")
            out["input_tokens"] = _safe_int(in_tok)
            out["output_tokens"] = _safe_int(out_tok)
            out["total_tokens"] = _safe_int(usage.get("total_tokens") or usage.get("totalTokens")) or (
                out["input_tokens"] + out["output_tokens"]
            )
            cache_creation = usage.get("cache_creation_input_tokens") or usage.get("cacheCreationTokens")
            cache_read = usage.get("cache_read_tokens") or usage.get("cacheReadTokens")
            out["cache_tokens"] = _safe_int(cache_creation) + _safe_int(cache_read)
            if "cost" in usage or "cost_usd" in usage:
                c = usage.get("cost_usd") or usage.get("cost")
                if c is not None:
                    try:
                        out["cost_usd"] = float(c)
                    except (TypeError, ValueError):
                        pass
        # Top-level (camelCase from reports / Claude-Code-Usage-Monitor)
        out["input_tokens"] = out["input_tokens"] or _safe_int(data.get("inputTokens") or data.get("input_tokens") or data.get("input"))
        out["output_tokens"] = out["output_tokens"] or _safe_int(data.get("outputTokens") or data.get("output_tokens") or data.get("output"))
        out["total_tokens"] = out["total_tokens"] or _safe_int(data.get("totalTokens") or data.get("total_tokens"))
        if out["total_tokens"] == 0 and (out["input_tokens"] or out["output_tokens"]):
            out["total_tokens"] = out["input_tokens"] + out["output_tokens"]
        out["cache_tokens"] = out["cache_tokens"] or _safe_int(data.get("cacheCreationTokens")) + _safe_int(data.get("cacheReadTokens"))
        if out["cost_usd"] is None:
            cost_raw = data.get("totalCost") or data.get("cost_usd") or data.get("cost")
            if cost_raw is not None:
                try:
                    out["cost_usd"] = float(cost_raw)
                except (TypeError, ValueError):
                    pass
    except (json.JSONDecodeError, TypeError, ValueError) as e:
        logger.debug(f"Skip JSONL line: {e}")
    return out


def _estimate_cost_usd(
    input_tokens: int,
    output_tokens: int,
    cache_tokens: int = 0,
    input_per_m: float = DEFAULT_INPUT_PER_M,
    output_per_m: float = DEFAULT_OUTPUT_PER_M,
) -> float:
    """Estimate cost in USD (cache often billed at input rate or discounted)."""
    return (input_tokens * input_per_m / 1_000_000) + (output_tokens * output_per_m / 1_000_000) + (cache_tokens * input_per_m * 0.1 / 1_000_000)


def get_claude_code_usage(
    config_dir: Optional[Path] = None,
    input_per_m: float = DEFAULT_INPUT_PER_M,
    output_per_m: float = DEFAULT_OUTPUT_PER_M,
) -> Dict[str, Any]:
    """
    Aggregate Claude Code / Cursor usage from config dir.

    Returns dict with:
      total_tokens, input_tokens, output_tokens, cache_tokens,
      estimated_cost_usd, cost_source ("reported" if totalCost in JSONL else "estimated"),
      session_count, has_data (bool).
    Config absent or empty -> has_data=False, counts 0.
    """
    base = config_dir or _get_claude_config_dir()
    result: Dict[str, Any] = {
        "total_tokens": 0,
        "input_tokens": 0,
        "output_tokens": 0,
        "cache_tokens": 0,
        "estimated_cost_usd": 0.0,
        "cost_source": "estimated",
        "session_count": 0,
        "has_data": False,
    }
    if not base:
        return result

    projects_dir = base / "projects"
    if not projects_dir.is_dir():
        return result

    total_in, total_out, total_cache = 0, 0, 0
    total_cost_from_data: float = 0.0
    session_count = 0
    for project_path in projects_dir.iterdir():
        if not project_path.is_dir():
            continue
        for jsonl_path in project_path.glob("*.jsonl"):
            session_count += 1
            try:
                with open(jsonl_path, "r", encoding="utf-8", errors="replace") as f:
                    for line in f:
                        if not line.strip():
                            continue
                        u = _parse_usage_from_line(line)
                        total_in += u["input_tokens"]
                        total_out += u["output_tokens"]
                        total_cache += u["cache_tokens"]
                        if u.get("cost_usd") is not None:
                            total_cost_from_data += float(u["cost_usd"])
            except OSError as e:
                logger.debug(f"Skip {jsonl_path}: {e}")

    result["input_tokens"] = total_in
    result["output_tokens"] = total_out
    result["cache_tokens"] = total_cache
    result["total_tokens"] = total_in + total_out + total_cache or (total_in + total_out)
    # Use reported cost from JSONL when present (Claude-Code-Usage-Monitor / API), else estimate
    if total_cost_from_data > 0:
        result["estimated_cost_usd"] = round(total_cost_from_data, 4)
        result["cost_source"] = "reported"
    else:
        result["estimated_cost_usd"] = round(
            _estimate_cost_usd(total_in, total_out, total_cache, input_per_m, output_per_m), 4
        )
        result["cost_source"] = "estimated"
    result["session_count"] = session_count
    result["has_data"] = session_count > 0 or result["total_tokens"] > 0
    return result


def _aggregate_from_dir(
    base: Path,
    input_per_m: float,
    output_per_m: float,
    only_cursor: Optional[bool] = None,
) -> tuple[Dict[str, Any], bool]:
    """Aggregate usage from one config dir. only_cursor=True/False filters by line source; None = no filter. Returns (result_dict, had_unknown_source)."""
    result: Dict[str, Any] = {
        "total_tokens": 0,
        "input_tokens": 0,
        "output_tokens": 0,
        "cache_tokens": 0,
        "estimated_cost_usd": 0.0,
        "cost_source": "estimated",
        "session_count": 0,
        "has_data": False,
    }
    had_unknown = False
    projects_dir = base / "projects"
    if not projects_dir.is_dir():
        return result, had_unknown
    total_in, total_out, total_cache = 0, 0, 0
    total_cost_from_data: float = 0.0
    session_count = 0
    for project_path in projects_dir.iterdir():
        if not project_path.is_dir():
            continue
        for jsonl_path in project_path.glob("*.jsonl"):
            session_count += 1
            try:
                with open(jsonl_path, "r", encoding="utf-8", errors="replace") as f:
                    for line in f:
                        if not line.strip():
                            continue
                        u = _parse_usage_from_line(line)
                        if only_cursor is True and u.get("is_cursor") is not True:
                            continue
                        if only_cursor is False and u.get("is_cursor") is True:
                            continue
                        if only_cursor is not None and u.get("is_cursor") is None:
                            had_unknown = True
                        total_in += u["input_tokens"]
                        total_out += u["output_tokens"]
                        total_cache += u["cache_tokens"]
                        if u.get("cost_usd") is not None:
                            total_cost_from_data += float(u["cost_usd"])
            except OSError as e:
                logger.debug(f"Skip {jsonl_path}: {e}")
    result["input_tokens"] = total_in
    result["output_tokens"] = total_out
    result["cache_tokens"] = total_cache
    result["total_tokens"] = total_in + total_out + total_cache or (total_in + total_out)
    if total_cost_from_data > 0:
        result["estimated_cost_usd"] = round(total_cost_from_data, 4)
        result["cost_source"] = "reported"
    else:
        result["estimated_cost_usd"] = round(
            _estimate_cost_usd(total_in, total_out, total_cache, input_per_m, output_per_m), 4
        )
        result["cost_source"] = "estimated"
    result["session_count"] = session_count
    result["has_data"] = session_count > 0 or result["total_tokens"] > 0
    return result, had_unknown


def get_claude_code_usage_split(
    config_dir: Optional[Path] = None,
    cursor_config_dir: Optional[Path] = None,
    input_per_m: float = DEFAULT_INPUT_PER_M,
    output_per_m: float = DEFAULT_OUTPUT_PER_M,
) -> Dict[str, Any]:
    """
    Aggregate usage split: Claude Code in Cursor Pro vs Claude Code in Claude Pro (standalone).

    Returns dict with:
      cursor_pro: usage in Cursor Pro (from CLAUDE_CURSOR_CONFIG_DIR or lines tagged cursor)
      claude_pro_standalone: usage in Claude Pro app / standalone
      merged: True if we could not split (single dir, no source tags in JSONL)
    """
    cursor_dir = cursor_config_dir or _get_claude_cursor_config_dir()
    main_dir = config_dir or _get_claude_config_dir()
    empty = {
        "total_tokens": 0,
        "input_tokens": 0,
        "output_tokens": 0,
        "cache_tokens": 0,
        "estimated_cost_usd": 0.0,
        "cost_source": "estimated",
        "session_count": 0,
        "has_data": False,
    }
    out: Dict[str, Any] = {
        "cursor_pro": dict(empty),
        "claude_pro_standalone": dict(empty),
        "merged": False,
    }
    if cursor_dir and main_dir and cursor_dir != main_dir:
        # Two dirs: Cursor usage from cursor_dir, standalone from main_dir
        cur, _ = _aggregate_from_dir(cursor_dir, input_per_m, output_per_m, only_cursor=None)
        std, _ = _aggregate_from_dir(main_dir, input_per_m, output_per_m, only_cursor=None)
        out["cursor_pro"] = cur
        out["claude_pro_standalone"] = std
        out["merged"] = False
        return out
    # Single dir: split by is_cursor in each line
    base = main_dir or cursor_dir
    if not base:
        return out
    cur, had_cur_unknown = _aggregate_from_dir(base, input_per_m, output_per_m, only_cursor=True)
    std, had_std_unknown = _aggregate_from_dir(base, input_per_m, output_per_m, only_cursor=False)
    out["cursor_pro"] = cur
    out["claude_pro_standalone"] = std
    out["merged"] = had_cur_unknown or had_std_unknown or (not cur["has_data"] and not std["has_data"])
    # If no line had source tag, everything went to standalone; treat as merged
    if not cur["has_data"] and std["has_data"]:
        out["merged"] = True
    return out
