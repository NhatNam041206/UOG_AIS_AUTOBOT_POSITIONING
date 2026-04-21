"""Dataset validation utility."""

from __future__ import annotations

import json
from pathlib import Path

from src.controller.route_manager import RouteManager


def validate_dataset(repo_root: Path) -> list[str]:
    """Validate route definitions, raw manifests, summaries, and processed outputs."""
    issues: list[str] = []

    route_manager = RouteManager(repo_root)
    try:
        routes = route_manager.all_routes()
        if not routes:
            issues.append("No routes configured in config/routes.yaml")
    except Exception as exc:  # noqa: BLE001
        issues.append(f"Route validation failed: {exc}")

    raw_runs_dir = repo_root / "data/raw/runs"
    for run_dir in sorted(raw_runs_dir.iterdir()) if raw_runs_dir.exists() else []:
        if not run_dir.is_dir() or run_dir.name == ".gitkeep":
            continue
        manifest = run_dir / "run_manifest.json"
        events = run_dir / "event_log.csv"
        commands = run_dir / "command_log.csv"
        if not manifest.exists():
            issues.append(f"{run_dir.name}: missing run_manifest.json")
        if not events.exists():
            issues.append(f"{run_dir.name}: missing event_log.csv")
        if not commands.exists():
            issues.append(f"{run_dir.name}: missing command_log.csv")

    summary_dir = repo_root / "data/processed/run_summaries"
    for summary_file in sorted(summary_dir.glob("*_summary.json")):
        try:
            payload = json.loads(summary_file.read_text(encoding="utf-8"))
            if "run_id" not in payload or "accepted_for_stats" not in payload:
                issues.append(f"{summary_file.name}: missing required summary fields")
        except Exception as exc:  # noqa: BLE001
            issues.append(f"{summary_file.name}: invalid json ({exc})")

    for required in [
        repo_root / "data/processed/accepted_runs.csv",
        repo_root / "data/processed/rejected_runs.csv",
        repo_root / "data/processed/route_stats.csv",
        repo_root / "data/processed/step_time_model.json",
    ]:
        if not required.exists():
            issues.append(f"Missing processed output: {required.relative_to(repo_root)}")

    return issues
