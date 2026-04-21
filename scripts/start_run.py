#!/usr/bin/env python3
"""Start a new raw run for a configured route."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from src.controller.route_manager import RouteManager
from src.logging_pipeline.run_manager import RunManager


def main() -> None:
    parser = argparse.ArgumentParser(description="Start a baseline run")
    parser.add_argument("--route-id", required=True, help="Configured route_id")
    parser.add_argument("--trial-id", default=None, help="Optional trial ID")
    parser.add_argument("--note", action="append", default=[], help="Optional run note (can repeat)")
    args = parser.parse_args()

    route_manager = RouteManager(REPO_ROOT)
    route_manager.load_routes()

    manager = RunManager(REPO_ROOT)
    manifest = manager.start_run(route_id=args.route_id, trial_id=args.trial_id, notes=args.note)
    print(f"Started run_id={manifest.run_id} route={manifest.route_id} trial_id={manifest.trial_id}")


if __name__ == "__main__":
    main()
