"""Restart step mapping (parity with config/ctm-rerun-step-map.json)."""

from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path


@lru_cache(maxsize=1)
def _map() -> dict:
    repo_root = Path(__file__).resolve().parents[2]
    mf_map = repo_root / "config" / "ctm-rerun-step-map.json"
    sap_map = Path(__file__).resolve().parents[1] / "config" / "ctm-rerun-step-map.json"
    path = sap_map if sap_map.is_file() else mf_map
    with path.open(encoding="utf-8") as fh:
        return json.load(fh)


def resolve_restart_step(failed_step: str) -> str:
    """Return Launcher restart step for a failed pipeline step name."""
    failed = failed_step.strip()
    step_name = failed.removeprefix("STEP.")
    overrides = _map().get("restartOverrides", {})

    if failed in overrides:
        return str(overrides[failed])
    if step_name in overrides:
        val = overrides[step_name]
        return val if val.startswith("STEP.") else f"STEP.{val}"

    if failed.startswith("STEP."):
        return failed
    return f"STEP.{step_name}"