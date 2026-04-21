from datetime import datetime, timezone
from pathlib import Path

from src.stats.summary_builder import RunSummaryBuilder
from src.utils.time_utils import elapsed_seconds


def test_elapsed_time_computation() -> None:
    start = datetime(2026, 1, 1, 0, 0, 0, tzinfo=timezone.utc)
    end = datetime(2026, 1, 1, 0, 0, 10, tzinfo=timezone.utc)
    assert elapsed_seconds(start, end) == 10.0


def test_acceptance_rejection_logic() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    builder = RunSummaryBuilder(repo_root)
    accepted = builder.summarize_run("run_mock_001")
    rejected = builder.summarize_run("run_mock_002")
    assert accepted.accepted_for_stats is True
    assert rejected.accepted_for_stats is False
