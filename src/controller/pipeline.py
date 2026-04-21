"""Controller pipeline to rebuild processed artifacts and outputs."""

from __future__ import annotations

from pathlib import Path

from src.baseline.model import build_step_time_model
from src.stats.engine import aggregate_summaries
from src.stats.summary_builder import RunSummaryBuilder
from src.utils.config import ConfigLoader
from src.visualization.eda import EDAVisualizer


def rebuild_all(repo_root: Path) -> dict[str, int]:
    """Rebuild summaries, aggregate tables, model, and EDA outputs."""
    summary_builder = RunSummaryBuilder(repo_root)
    summary_builder.summarize_all_runs()
    summaries_df = summary_builder.load_all_summaries_df()

    stats_cfg = ConfigLoader(repo_root).load_yaml("stats.yaml")
    accepted_df, rejected_df, route_stats_df = aggregate_summaries(repo_root, summaries_df, stats_cfg)
    build_step_time_model(repo_root, accepted_df)

    visualizer = EDAVisualizer(repo_root)
    visualizer.generate(summaries_df, accepted_df, rejected_df)

    return {
        "summaries": int(len(summaries_df)),
        "accepted": int(len(accepted_df)),
        "rejected": int(len(rejected_df)),
        "route_stats_rows": int(len(route_stats_df)),
    }
