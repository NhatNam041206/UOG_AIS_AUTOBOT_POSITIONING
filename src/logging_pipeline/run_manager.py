"""Run lifecycle management for raw run logging."""

from __future__ import annotations

import csv
import json
from pathlib import Path
from uuid import uuid4

from src.controller.route_manager import RouteManager
from src.models.schemas import RunManifest
from src.utils.time_utils import to_iso, utc_now


class RunManager:
    """Creates and updates run folders and core logs."""

    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root
        self.route_manager = RouteManager(repo_root)
        self.raw_runs_dir = repo_root / "data/raw/runs"

    def _run_dir(self, run_id: str) -> Path:
        return self.raw_runs_dir / run_id

    def _write_csv_header(self, path: Path, columns: list[str]) -> None:
        with path.open("w", encoding="utf-8", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=columns)
            writer.writeheader()

    def start_run(self, route_id: str, trial_id: str | None = None, notes: list[str] | None = None) -> RunManifest:
        """Start a run and initialize raw artifacts."""
        route = self.route_manager.get_route(route_id)
        now = utc_now()
        run_id = f"run_{now.strftime('%Y%m%dT%H%M%S')}_{uuid4().hex[:8]}"
        resolved_trial_id = trial_id or f"trial_{route_id}_{now.strftime('%Y%m%d')}"
        manifest = RunManifest(
            run_id=run_id,
            trial_id=resolved_trial_id,
            route_id=route.route_id,
            start_point=route.start_point,
            end_point=route.end_point,
            abstract_step_count=route.abstract_step_count,
            started_at=now,
            ended_at=None,
            status="RUNNING",
            notes=notes or [],
        )

        run_dir = self._run_dir(run_id)
        run_dir.mkdir(parents=True, exist_ok=True)

        manifest_path = run_dir / "run_manifest.json"
        manifest_path.write_text(json.dumps(manifest.model_dump(mode="json"), indent=2), encoding="utf-8")

        event_path = run_dir / "event_log.csv"
        command_path = run_dir / "command_log.csv"
        notes_path = run_dir / "notes.json"

        self._write_csv_header(event_path, ["run_id", "event_time", "event_type", "event_value", "source", "comment"])
        self._write_csv_header(command_path, ["run_id", "timestamp", "command_type", "command_value", "duration_ms"])
        notes_path.write_text(json.dumps({"run_id": run_id, "notes": notes or []}, indent=2), encoding="utf-8")

        self.log_event(run_id, "RUN_STARTED", "1", "system", "run initialized")
        self.log_event(run_id, "FORWARD_COMMAND_SENT", "forward", "controller", "initial movement command")
        self.log_command(run_id, "FORWARD", "forward", 1000)

        return manifest

    def load_manifest(self, run_id: str) -> RunManifest:
        """Load a run manifest from disk."""
        manifest_path = self._run_dir(run_id) / "run_manifest.json"
        payload = json.loads(manifest_path.read_text(encoding="utf-8"))
        return RunManifest.model_validate(payload)

    def save_manifest(self, manifest: RunManifest) -> None:
        """Persist updated run manifest."""
        manifest_path = self._run_dir(manifest.run_id) / "run_manifest.json"
        manifest_path.write_text(json.dumps(manifest.model_dump(mode="json"), indent=2), encoding="utf-8")

    def log_event(
        self,
        run_id: str,
        event_type: str,
        event_value: str,
        source: str,
        comment: str,
    ) -> None:
        """Append one event row."""
        event_path = self._run_dir(run_id) / "event_log.csv"
        row = {
            "run_id": run_id,
            "event_time": to_iso(utc_now()),
            "event_type": event_type,
            "event_value": event_value,
            "source": source,
            "comment": comment,
        }
        with event_path.open("a", encoding="utf-8", newline="") as handle:
            writer = csv.DictWriter(
                handle,
                fieldnames=["run_id", "event_time", "event_type", "event_value", "source", "comment"],
            )
            writer.writerow(row)

    def log_command(self, run_id: str, command_type: str, command_value: str, duration_ms: int) -> None:
        """Append one command row."""
        command_path = self._run_dir(run_id) / "command_log.csv"
        row = {
            "run_id": run_id,
            "timestamp": to_iso(utc_now()),
            "command_type": command_type,
            "command_value": command_value,
            "duration_ms": duration_ms,
        }
        with command_path.open("a", encoding="utf-8", newline="") as handle:
            writer = csv.DictWriter(
                handle,
                fieldnames=["run_id", "timestamp", "command_type", "command_value", "duration_ms"],
            )
            writer.writerow(row)

    def stop_run(
        self,
        run_id: str,
        status: str = "COMPLETED",
        notes: list[str] | None = None,
        interrupted: bool = False,
        anomaly_flagged: bool = False,
    ) -> RunManifest:
        """Stop a running run and finalize manifest + events."""
        manifest = self.load_manifest(run_id)
        manifest.ended_at = utc_now()
        manifest.status = "INTERRUPTED" if interrupted else status
        if notes:
            manifest.notes.extend(notes)
        self.save_manifest(manifest)

        if interrupted:
            self.log_event(run_id, "MANUAL_INTERRUPT", "1", "operator", "manual interruption")
        if anomaly_flagged:
            self.log_event(run_id, "ANOMALY_FLAGGED", "1", "operator", "abnormal behavior flagged")
        self.log_event(run_id, "RUN_STOPPED", "1", "system", "run finalized")

        notes_path = self._run_dir(run_id) / "notes.json"
        existing_notes = {"run_id": run_id, "notes": []}
        if notes_path.exists():
            existing_notes = json.loads(notes_path.read_text(encoding="utf-8"))
        merged = list(existing_notes.get("notes", [])) + (notes or [])
        notes_path.write_text(json.dumps({"run_id": run_id, "notes": merged}, indent=2), encoding="utf-8")

        return manifest
