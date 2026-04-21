"""Progress estimation based on route and timing model."""

from __future__ import annotations

from typing import Any

from src.models.schemas import RouteDefinition


def estimate_progress(
    route: RouteDefinition,
    elapsed_time_sec: float,
    route_timing_model: dict[str, Any] | None,
    default_step_time_sec: float,
    default_start_offset_sec: float,
    default_stop_offset_sec: float,
) -> dict[str, float | int]:
    """Estimate abstract step progress using phase-based timing."""
    model = route_timing_model or {}
    step_count = route.abstract_step_count

    start_offset = float(model.get("start_offset_sec", default_start_offset_sec))
    stop_offset = float(model.get("stop_offset_sec", default_stop_offset_sec))
    step_time = float(model.get("mean_step_time_sec", default_step_time_sec))

    if step_time <= 0:
        step_time = default_step_time_sec

    core_time = max(0.0, elapsed_time_sec - start_offset)
    max_core_time = max(step_count * step_time, 0.0)
    effective_core = min(core_time, max_core_time + stop_offset)
    progress = effective_core / step_time if step_time > 0 else 0.0
    clamped_progress = min(float(step_count), max(0.0, progress))

    return {
        "estimated_abstract_step_progress": clamped_progress,
        "estimated_step_index": int(min(step_count, max(0, round(clamped_progress)))),
    }
