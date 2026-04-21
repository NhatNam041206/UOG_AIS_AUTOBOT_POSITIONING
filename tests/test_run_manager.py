import shutil
from pathlib import Path

from src.controller.route_manager import RouteManager
from src.logging_pipeline.run_manager import RunManager


def test_run_manifest_generation() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    RouteManager(repo_root).load_routes()
    manager = RunManager(repo_root)
    manifest = manager.start_run("A_TO_B_MAIN", trial_id="trial_test", notes=["unit test"])
    run_dir = repo_root / "data/raw/runs" / manifest.run_id
    try:
        assert run_dir.exists()
        assert (run_dir / "run_manifest.json").exists()
        manager.stop_run(manifest.run_id, notes=["done"])
    finally:
        if run_dir.exists():
            shutil.rmtree(run_dir)
