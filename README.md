# robot_time_baseline

Time-based baseline backend for robot-positioning research using abstract tile steps.

## Purpose

This project records repeated route runs (e.g., A→B), preserves raw logs, validates runs, computes route-level timing baselines, and generates EDA outputs. It intentionally excludes RPM/camera/SLAM localization.

Model used:

`T_total = T_start_offset + n * T_abstract_step + T_stop_offset`

## Architecture

- `src/controller`: orchestration and validation
- `src/logging_pipeline`: run lifecycle logging
- `src/stats`: summary and descriptive stats
- `src/baseline`: timing model + progress estimator
- `src/visualization`: EDA plots and tables
- `src/models`: pydantic schemas
- `src/utils`: config/time/path helpers

## Folder structure

Includes required directories under `config/`, `data/`, `docs/`, `logs/`, `notebooks/`, `outputs/`, `scripts/`, `src/`, and `tests/`.

## Installation

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Quick start

1. Rebuild summaries/stats/model/EDA from sample raw runs:

```bash
python scripts/rebuild_stats.py
```

2. Validate dataset:

```bash
python scripts/validate_dataset.py
```

3. Start a new run:

```bash
python scripts/start_run.py --route-id A_TO_B_MAIN --note "baseline trial"
```

4. Stop a run:

```bash
python scripts/stop_run.py --run-id <RUN_ID>
```

5. Export processed data:

```bash
python scripts/export_data.py --with-parquet
```

## Abstract-step baseline logic

- Routes are defined by abstract step counts, not real tile identity.
- Accepted runs update route-level timing statistics.
- Rejected runs are preserved and tracked separately.
- Progress estimation is time-based and clamped to `[0, abstract_step_count]`.

## Current limitations

- No RPM encoder integration
- No servo-angle odometry
- No camera tile correction
- No SLAM/fusion/localization coordinates

## Future extension points

- Add RPM-assisted estimators in `src/baseline/`
- Add sensor-fusion quality scoring in `src/stats/`
- Add richer anomaly classification in `src/logging_pipeline/`
