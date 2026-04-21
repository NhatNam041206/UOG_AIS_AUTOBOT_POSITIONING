#!/usr/bin/env python3
"""Rebuild processed summaries, stats, timing model, and EDA outputs."""

from __future__ import annotations

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from src.controller.pipeline import rebuild_all


def main() -> None:
    result = rebuild_all(REPO_ROOT)
    print("Rebuild complete:", result)


if __name__ == "__main__":
    main()
