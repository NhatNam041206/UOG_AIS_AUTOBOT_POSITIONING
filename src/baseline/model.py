"""Build and persist route-level baseline step-time model."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd

from src.controller.route_manager import RouteManager
from src.models.schemas import StepTimeModelEntry
from src.stats.engine import StatsEngine
from src.utils.config import ConfigLoader


def build_step_time_model(repo_root: Path, accepted_df: pd.DataFrame) -> dict[str, dict[str, Any]]:
    """Compute and save route-level step-time model from accepted run history."""
    route_manager = RouteManager(repo_root)
    routes = route_manager.all_routes()
    estimator_cfg = ConfigLoader(repo_root).load_yaml("estimator.yaml")
    defaults = estimator_cfg.get("default_offsets", {})
    start_offset = float(defaults.get("start_offset_sec", 0.5))
    stop_offset = float(defaults.get("stop_offset_sec", 0.5))

    model: dict[str, dict[str, Any]] = {}
    now = datetime.now(timezone.utc)

    for route in routes:
        route_df = accepted_df[accepted_df["route_id"] == route.route_id] if not accepted_df.empty else pd.DataFrame()
        total = route_df.get("total_elapsed_time_sec", pd.Series(dtype=float)).dropna().astype(float)
        step = route_df.get("estimated_step_time_sec", pd.Series(dtype=float)).dropna().astype(float)

        entry = StepTimeModelEntry(
            route_id=route.route_id,
            valid_run_count=int(len(route_df)),
            mean_total_time_sec=StatsEngine.mean(total),
            std_total_time_sec=StatsEngine.std(total),
            mean_step_time_sec=StatsEngine.mean(step),
            std_step_time_sec=StatsEngine.std(step),
            median_step_time_sec=StatsEngine.median(step),
            start_offset_sec=start_offset,
            stop_offset_sec=stop_offset,
            last_updated_at=now,
        )
        model[route.route_id] = entry.model_dump(mode="json")

    out_path = repo_root / "data/processed/step_time_model.json"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(model, indent=2), encoding="utf-8")
    return model
