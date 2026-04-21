"""EDA plotting and table export for processed baseline data."""

from __future__ import annotations

from pathlib import Path

import matplotlib
import matplotlib.pyplot as plt
import pandas as pd

from src.stats.engine import StatsEngine

matplotlib.use("Agg")


class EDAVisualizer:
    """Generates required figures and summary tables from processed data."""

    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root
        self.figures_dir = repo_root / "outputs/figures"
        self.tables_dir = repo_root / "outputs/tables"
        self.figures_dir.mkdir(parents=True, exist_ok=True)
        self.tables_dir.mkdir(parents=True, exist_ok=True)

    def _save_empty_plot(self, name: str, title: str) -> None:
        fig, ax = plt.subplots(figsize=(6, 4))
        ax.text(0.5, 0.5, "No data available", ha="center", va="center")
        ax.set_title(title)
        ax.axis("off")
        fig.tight_layout()
        fig.savefig(self.figures_dir / name)
        plt.close(fig)

    def generate(self, summaries_df: pd.DataFrame, accepted_df: pd.DataFrame, rejected_df: pd.DataFrame) -> None:
        """Generate required plots and summary tables."""
        if summaries_df.empty:
            self._save_empty_plot("total_elapsed_time_by_run_index.png", "Total elapsed time by run index")
            self._save_empty_plot("estimated_step_time_by_run_index.png", "Estimated step time by run index")
            self._save_empty_plot("hist_total_elapsed_time.png", "Histogram of total elapsed time")
            self._save_empty_plot("hist_estimated_step_time.png", "Histogram of estimated step time")
            self._save_empty_plot("boxplot_total_time_by_route.png", "Boxplot total time by route")
            self._save_empty_plot("accepted_vs_rejected_count.png", "Accepted vs rejected runs")
            self._save_empty_plot("moving_average_trend.png", "Moving average trend")
            self._save_empty_plot("outlier_highlight_plot.png", "Outlier highlight plot")
            return

        plot_df = summaries_df.reset_index(drop=True).copy()
        plot_df["run_index"] = plot_df.index + 1

        fig, ax = plt.subplots(figsize=(8, 4))
        ax.plot(plot_df["run_index"], plot_df["total_elapsed_time_sec"], marker="o")
        ax.set_title("Total elapsed time by run index")
        ax.set_xlabel("Run index")
        ax.set_ylabel("Seconds")
        fig.tight_layout()
        fig.savefig(self.figures_dir / "total_elapsed_time_by_run_index.png")
        plt.close(fig)

        fig, ax = plt.subplots(figsize=(8, 4))
        ax.plot(plot_df["run_index"], plot_df["estimated_step_time_sec"], marker="o", color="tab:orange")
        ax.set_title("Estimated step time by run index")
        ax.set_xlabel("Run index")
        ax.set_ylabel("Seconds")
        fig.tight_layout()
        fig.savefig(self.figures_dir / "estimated_step_time_by_run_index.png")
        plt.close(fig)

        fig, ax = plt.subplots(figsize=(8, 4))
        ax.hist(plot_df["total_elapsed_time_sec"].dropna(), bins=10)
        ax.set_title("Histogram of total elapsed time")
        fig.tight_layout()
        fig.savefig(self.figures_dir / "hist_total_elapsed_time.png")
        plt.close(fig)

        fig, ax = plt.subplots(figsize=(8, 4))
        ax.hist(plot_df["estimated_step_time_sec"].dropna(), bins=10, color="tab:green")
        ax.set_title("Histogram of estimated step time")
        fig.tight_layout()
        fig.savefig(self.figures_dir / "hist_estimated_step_time.png")
        plt.close(fig)

        fig, ax = plt.subplots(figsize=(8, 4))
        grouped = [g["total_elapsed_time_sec"].dropna().tolist() for _, g in plot_df.groupby("route_id")]
        labels = [str(rid) for rid, _ in plot_df.groupby("route_id")]
        if grouped:
            ax.boxplot(grouped, tick_labels=labels)
        ax.set_title("Boxplot of total elapsed time by route")
        fig.tight_layout()
        fig.savefig(self.figures_dir / "boxplot_total_time_by_route.png")
        plt.close(fig)

        fig, ax = plt.subplots(figsize=(6, 4))
        ax.bar(["accepted", "rejected"], [len(accepted_df), len(rejected_df)], color=["tab:blue", "tab:red"])
        ax.set_title("Accepted vs rejected runs count")
        fig.tight_layout()
        fig.savefig(self.figures_dir / "accepted_vs_rejected_count.png")
        plt.close(fig)

        fig, ax = plt.subplots(figsize=(8, 4))
        accepted_sorted = accepted_df.reset_index(drop=True).copy()
        if not accepted_sorted.empty:
            ma = StatsEngine.moving_average(accepted_sorted["total_elapsed_time_sec"].astype(float), window=3)
            ax.plot(range(1, len(ma) + 1), ma, marker="o")
        ax.set_title("Moving average trend of accepted run time")
        ax.set_xlabel("Accepted run index")
        ax.set_ylabel("Seconds")
        fig.tight_layout()
        fig.savefig(self.figures_dir / "moving_average_trend.png")
        plt.close(fig)

        fig, ax = plt.subplots(figsize=(8, 4))
        totals = plot_df["total_elapsed_time_sec"].dropna().astype(float)
        outliers = StatsEngine.detect_outliers(totals)
        ax.scatter(plot_df.loc[totals.index, "run_index"], totals, color="tab:blue", label="normal")
        if len(outliers):
            outlier_index = totals.index[outliers]
            ax.scatter(plot_df.loc[outlier_index, "run_index"], totals.loc[outlier_index], color="tab:red", label="outlier")
        ax.set_title("Outlier highlight plot")
        ax.legend()
        fig.tight_layout()
        fig.savefig(self.figures_dir / "outlier_highlight_plot.png")
        plt.close(fig)

        summary_table = pd.DataFrame(
            [
                {"metric": "total_runs", "value": len(summaries_df)},
                {"metric": "accepted_runs", "value": len(accepted_df)},
                {"metric": "rejected_runs", "value": len(rejected_df)},
            ]
        )
        summary_table.to_csv(self.tables_dir / "dataset_summary.csv", index=False)
