"""Build processed run summaries from raw run artifacts."""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path

import pandas as pd

from src.models.schemas import RunManifest, RunSummary


class RunSummaryBuilder:
    """Summarizes raw run folders into processed summary records."""

    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root
        self.raw_runs_dir = repo_root / "data/raw/runs"
        self.summaries_dir = repo_root / "data/processed/run_summaries"
        self.stats_cfg = self._load_stats_config()

    def _load_stats_config(self) -> dict:
        stats_file = self.repo_root / "config/stats.yaml"
        if not stats_file.exists():
            return {}
        import yaml

        with stats_file.open("r", encoding="utf-8") as handle:
            return yaml.safe_load(handle) or {}

    def _duration_limits(self) -> tuple[float, float]:
        limits = self.stats_cfg.get("duration_thresholds", {})
        return float(limits.get("min_total_time_sec", 0.0)), float(limits.get("max_total_time_sec", 1e9))

    def summarize_run(self, run_id: str) -> RunSummary:
        """Generate one run summary from raw files."""
        run_dir = self.raw_runs_dir / run_id
        run_dir.mkdir(parents=True, exist_ok=True)
        manifest_path = run_dir / "run_manifest.json"
        event_path = run_dir / "event_log.csv"
        command_path = run_dir / "command_log.csv"

        rejection_reasons: list[str] = []
        anomaly_flags: list[str] = []
        elapsed: float | None = None
        estimated_step_time: float | None = None
        route_id = "UNKNOWN"
        abstract_step_count = 1

        if not manifest_path.exists():
            rejection_reasons.append("missing_manifest")
            started = None
            ended = None
            status = "MISSING"
        else:
            manifest_payload = json.loads(manifest_path.read_text(encoding="utf-8"))
            manifest = RunManifest.model_validate(manifest_payload)
            route_id = manifest.route_id
            abstract_step_count = manifest.abstract_step_count
            started = manifest.started_at
            ended = manifest.ended_at
            status = manifest.status

        if started is None or ended is None:
            rejection_reasons.append("missing_start_or_end_timestamp")
        else:
            elapsed = (ended - started).total_seconds()
            if elapsed <= 0:
                rejection_reasons.append("non_positive_elapsed_time")
            else:
                estimated_step_time = elapsed / max(abstract_step_count, 1)

        if status.upper() == "INTERRUPTED":
            rejection_reasons.append("interrupted_run")

        if not event_path.exists():
            rejection_reasons.append("missing_event_log")
            event_df = pd.DataFrame()
        else:
            event_df = pd.read_csv(event_path)

        if not command_path.exists():
            rejection_reasons.append("missing_command_log")
            command_df = pd.DataFrame()
        else:
            command_df = pd.read_csv(command_path)

        if not command_df.empty and "command_type" in command_df.columns:
            essential_ok = command_df["command_type"].astype(str).str.upper().eq("FORWARD").any()
        else:
            essential_ok = False
        if not essential_ok:
            rejection_reasons.append("missing_essential_command")

        if not event_df.empty and "event_type" in event_df.columns:
            if event_df["event_type"].astype(str).str.upper().eq("MANUAL_INTERRUPT").any():
                rejection_reasons.append("interrupted_run")
            if event_df["event_type"].astype(str).str.upper().eq("ANOMALY_FLAGGED").any():
                rejection_reasons.append("abnormal_flagged")
                anomaly_flags.append("abnormal_flagged")

        min_limit, max_limit = self._duration_limits()
        if elapsed is not None and (elapsed < min_limit or elapsed > max_limit):
            rejection_reasons.append("duration_outside_config_limits")

        unique_reasons = sorted(set(rejection_reasons))
        accepted = len(unique_reasons) == 0
        quality_score = max(0.0, 1.0 - 0.2 * len(unique_reasons))

        summary = RunSummary(
            run_id=run_id,
            route_id=route_id,
            total_elapsed_time_sec=elapsed,
            abstract_step_count=abstract_step_count,
            estimated_step_time_sec=estimated_step_time,
            accepted_for_stats=accepted,
            rejection_reason=";".join(unique_reasons),
            anomaly_flags=sorted(set(anomaly_flags)),
            quality_score=quality_score,
        )

        self.summaries_dir.mkdir(parents=True, exist_ok=True)
        out_path = self.summaries_dir / f"{run_id}_summary.json"
        out_path.write_text(json.dumps(summary.model_dump(mode="json"), indent=2), encoding="utf-8")
        return summary

    def summarize_all_runs(self) -> list[RunSummary]:
        """Summarize every raw run folder."""
        summaries: list[RunSummary] = []
        if not self.raw_runs_dir.exists():
            return summaries
        for path in sorted(self.raw_runs_dir.iterdir()):
            if path.is_dir() and path.name != ".gitkeep":
                summaries.append(self.summarize_run(path.name))
        return summaries

    def load_all_summaries_df(self) -> pd.DataFrame:
        """Load all summary json files into a DataFrame."""
        if not self.summaries_dir.exists():
            return pd.DataFrame()
        rows: list[dict] = []
        for path in sorted(self.summaries_dir.glob("*_summary.json")):
            rows.append(json.loads(path.read_text(encoding="utf-8")))
        return pd.DataFrame(rows)
