#!/usr/bin/env python3
"""Stop an existing run and generate processed summary."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from src.logging_pipeline.run_manager import RunManager
from src.stats.summary_builder import RunSummaryBuilder


def main() -> None:
    parser = argparse.ArgumentParser(description="Stop a baseline run")
    parser.add_argument("--run-id", required=True, help="Run ID to stop")
    parser.add_argument("--note", action="append", default=[], help="Optional stop note")
    parser.add_argument("--interrupted", action="store_true", help="Mark run as interrupted")
    parser.add_argument("--anomaly", action="store_true", help="Mark run as anomaly flagged")
    args = parser.parse_args()

    manager = RunManager(REPO_ROOT)
    manifest = manager.stop_run(
        run_id=args.run_id,
        notes=args.note,
        interrupted=args.interrupted,
        anomaly_flagged=args.anomaly,
    )

    summary = RunSummaryBuilder(REPO_ROOT).summarize_run(args.run_id)
    print(
        f"Stopped run_id={manifest.run_id} status={manifest.status} "
        f"accepted={summary.accepted_for_stats} reasons={summary.rejection_reason or 'none'}"
    )


if __name__ == "__main__":
    main()
