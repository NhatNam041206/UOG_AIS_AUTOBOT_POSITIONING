from pathlib import Path

import pandas as pd

from src.baseline.progress_estimator import estimate_progress
from src.controller.pipeline import rebuild_all
from src.controller.route_manager import RouteManager


def test_aggregate_stat_computation() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    result = rebuild_all(repo_root)
    assert result["summaries"] >= 2
    route_stats = pd.read_csv(repo_root / "data/processed/route_stats.csv")
    assert "mean_total_time_sec" in route_stats.columns


def test_progress_estimator_clamping() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    route = RouteManager(repo_root).get_route("A_TO_B_MAIN")
    est = estimate_progress(
        route=route,
        elapsed_time_sec=999,
        route_timing_model={"mean_step_time_sec": 1.5, "start_offset_sec": 0.5, "stop_offset_sec": 0.5},
        default_step_time_sec=1.5,
        default_start_offset_sec=0.5,
        default_stop_offset_sec=0.5,
    )
    assert est["estimated_abstract_step_progress"] <= route.abstract_step_count
    assert est["estimated_step_index"] <= route.abstract_step_count
