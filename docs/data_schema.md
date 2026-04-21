# Data Schema

## Raw per-run files
- `run_manifest.json`: run metadata and lifecycle status
- `event_log.csv`: event stream (`RUN_STARTED`, `FORWARD_COMMAND_SENT`, `RUN_STOPPED`, etc.)
- `command_log.csv`: command stream and durations
- `notes.json`: free-form notes

## Processed files
- `run_summaries/<run_id>_summary.json`
- `accepted_runs.csv`
- `rejected_runs.csv`
- `route_stats.csv`
- `step_time_model.json`
