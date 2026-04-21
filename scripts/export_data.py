#!/usr/bin/env python3
"""Export processed data tables to export directories."""

from __future__ import annotations

import argparse
import shutil
import sys
from pathlib import Path

import pandas as pd

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))


def main() -> None:
    parser = argparse.ArgumentParser(description="Export processed tables")
    parser.add_argument("--with-parquet", action="store_true", help="Also export parquet files")
    args = parser.parse_args()

    processed = REPO_ROOT / "data/processed"
    export_csv = REPO_ROOT / "data/exports/csv"
    export_parquet = REPO_ROOT / "data/exports/parquet"
    export_csv.mkdir(parents=True, exist_ok=True)
    export_parquet.mkdir(parents=True, exist_ok=True)

    for name in ["accepted_runs.csv", "rejected_runs.csv", "route_stats.csv", "step_time_model.json"]:
        src = processed / name
        if src.exists():
            shutil.copy2(src, export_csv / name)

    if args.with_parquet:
        for name in ["accepted_runs.csv", "rejected_runs.csv", "route_stats.csv"]:
            src = processed / name
            if src.exists():
                df = pd.read_csv(src)
                df.to_parquet(export_parquet / name.replace(".csv", ".parquet"), index=False)

    print("Export complete")


if __name__ == "__main__":
    main()
