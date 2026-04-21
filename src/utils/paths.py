"""Path utilities for project directories."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from src.utils.config import ConfigLoader


@dataclass
class AppPaths:
    """Resolved project paths from app config."""

    repo_root: Path
    raw_runs: Path
    route_definitions: Path
    run_summaries: Path
    accepted_runs: Path
    rejected_runs: Path
    route_stats: Path
    step_time_model: Path
    export_csv: Path
    export_parquet: Path
    export_reports: Path
    figures: Path
    tables: Path
    summaries: Path

    @classmethod
    def from_config(cls, repo_root: Path) -> "AppPaths":
        """Build resolved paths from config/app.yaml."""
        cfg = ConfigLoader(repo_root).load_yaml("app.yaml")
        data_dirs = cfg.get("data_directories", {})
        output_dirs = cfg.get("output_directories", {})
        return cls(
            repo_root=repo_root,
            raw_runs=repo_root / data_dirs.get("raw_runs", "data/raw/runs"),
            route_definitions=repo_root / data_dirs.get("route_definitions", "data/raw/route_definitions"),
            run_summaries=repo_root / data_dirs.get("run_summaries", "data/processed/run_summaries"),
            accepted_runs=repo_root / data_dirs.get("accepted_runs", "data/processed/accepted_runs.csv"),
            rejected_runs=repo_root / data_dirs.get("rejected_runs", "data/processed/rejected_runs.csv"),
            route_stats=repo_root / data_dirs.get("route_stats", "data/processed/route_stats.csv"),
            step_time_model=repo_root / data_dirs.get("step_time_model", "data/processed/step_time_model.json"),
            export_csv=repo_root / data_dirs.get("export_csv", "data/exports/csv"),
            export_parquet=repo_root / data_dirs.get("export_parquet", "data/exports/parquet"),
            export_reports=repo_root / data_dirs.get("export_reports", "data/exports/reports"),
            figures=repo_root / output_dirs.get("figures", "outputs/figures"),
            tables=repo_root / output_dirs.get("tables", "outputs/tables"),
            summaries=repo_root / output_dirs.get("summaries", "outputs/summaries"),
        )

    def ensure_directories(self) -> None:
        """Ensure all configured directories exist."""
        dirs = [
            self.raw_runs,
            self.route_definitions,
            self.run_summaries,
            self.export_csv,
            self.export_parquet,
            self.export_reports,
            self.figures,
            self.tables,
            self.summaries,
            self.accepted_runs.parent,
            self.rejected_runs.parent,
            self.route_stats.parent,
            self.step_time_model.parent,
        ]
        for directory in dirs:
            directory.mkdir(parents=True, exist_ok=True)


def discover_repo_root() -> Path:
    """Discover repository root from package file location."""
    return Path(__file__).resolve().parents[2]
