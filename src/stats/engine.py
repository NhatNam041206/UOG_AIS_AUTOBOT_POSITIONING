"""Statistics helpers and route-level aggregation."""

from __future__ import annotations

import math
from pathlib import Path
from typing import Any

import pandas as pd


class StatsEngine:
    """Computes descriptive statistics and outlier flags."""

    @staticmethod
    def mean(values: pd.Series) -> float | None:
        return None if values.empty else float(values.mean())

    @staticmethod
    def std(values: pd.Series) -> float | None:
        return None if values.empty else float(values.std(ddof=1))

    @staticmethod
    def median(values: pd.Series) -> float | None:
        return None if values.empty else float(values.median())

    @staticmethod
    def min_max(values: pd.Series) -> tuple[float | None, float | None]:
        if values.empty:
            return None, None
        return float(values.min()), float(values.max())

    @staticmethod
    def confidence_interval(values: pd.Series, confidence_level: float = 0.95) -> tuple[float | None, float | None]:
        if values.empty:
            return None, None
        mean = float(values.mean())
        if len(values) < 2:
            return mean, mean
        std = float(values.std(ddof=1))
        z = 1.96 if math.isclose(confidence_level, 0.95) else 1.96
        margin = z * std / math.sqrt(len(values))
        return mean - margin, mean + margin

    @staticmethod
    def moving_average(values: pd.Series, window: int = 3) -> pd.Series:
        return values.rolling(window=window, min_periods=1).mean()

    @staticmethod
    def detect_outliers(values: pd.Series, method: str = "zscore", zscore_threshold: float = 2.5, iqr_multiplier: float = 1.5) -> pd.Series:
        if values.empty:
            return pd.Series(dtype=bool)
        if method.lower() == "iqr":
            q1 = values.quantile(0.25)
            q3 = values.quantile(0.75)
            iqr = q3 - q1
            low = q1 - iqr_multiplier * iqr
            high = q3 + iqr_multiplier * iqr
            return (values < low) | (values > high)
        std = values.std(ddof=1)
        if std == 0 or pd.isna(std):
            return pd.Series([False] * len(values), index=values.index)
        zscores = (values - values.mean()) / std
        return zscores.abs() > zscore_threshold


def aggregate_summaries(repo_root: Path, summaries_df: pd.DataFrame, stats_cfg: dict[str, Any]) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """Build accepted/rejected tables and route-level stats table."""
    processed_dir = repo_root / "data/processed"
    processed_dir.mkdir(parents=True, exist_ok=True)

    if summaries_df.empty:
        accepted_df = pd.DataFrame()
        rejected_df = pd.DataFrame()
        route_stats_df = pd.DataFrame()
    else:
        accepted_df = summaries_df[summaries_df["accepted_for_stats"] == True].copy()  # noqa: E712
        rejected_df = summaries_df[summaries_df["accepted_for_stats"] == False].copy()  # noqa: E712

        outlier_cfg = stats_cfg.get("outlier", {})
        moving_window = int(stats_cfg.get("moving_average_window", 3))
        conf_level = float(stats_cfg.get("confidence_level", 0.95))

        route_rows: list[dict[str, Any]] = []
        for route_id, route_df in accepted_df.groupby("route_id"):
            total = route_df["total_elapsed_time_sec"].dropna().astype(float)
            step = route_df["estimated_step_time_sec"].dropna().astype(float)
            outlier_mask = StatsEngine.detect_outliers(
                total,
                method=outlier_cfg.get("method", "zscore"),
                zscore_threshold=float(outlier_cfg.get("zscore_threshold", 2.5)),
                iqr_multiplier=float(outlier_cfg.get("iqr_multiplier", 1.5)),
            )
            ci_low, ci_high = StatsEngine.confidence_interval(total, conf_level)
            min_v, max_v = StatsEngine.min_max(total)
            route_rows.append(
                {
                    "route_id": route_id,
                    "accepted_run_count": int(len(route_df)),
                    "mean_total_time_sec": StatsEngine.mean(total),
                    "std_total_time_sec": StatsEngine.std(total),
                    "median_total_time_sec": StatsEngine.median(total),
                    "min_total_time_sec": min_v,
                    "max_total_time_sec": max_v,
                    "mean_step_time_sec": StatsEngine.mean(step),
                    "std_step_time_sec": StatsEngine.std(step),
                    "median_step_time_sec": StatsEngine.median(step),
                    "outlier_count": int(outlier_mask.sum()) if len(outlier_mask) else 0,
                    "ci_low_total_time_sec": ci_low,
                    "ci_high_total_time_sec": ci_high,
                    "moving_average_last_total_time_sec": float(
                        StatsEngine.moving_average(total.reset_index(drop=True), moving_window).iloc[-1]
                    )
                    if not total.empty
                    else None,
                }
            )
        route_stats_df = pd.DataFrame(route_rows)

    accepted_df.to_csv(processed_dir / "accepted_runs.csv", index=False)
    rejected_df.to_csv(processed_dir / "rejected_runs.csv", index=False)
    route_stats_df.to_csv(processed_dir / "route_stats.csv", index=False)
    return accepted_df, rejected_df, route_stats_df
