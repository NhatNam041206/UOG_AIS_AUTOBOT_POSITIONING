from pathlib import Path

from src.controller.route_manager import RouteManager


def test_route_loading_and_validation() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    manager = RouteManager(repo_root)
    routes = manager.load_routes()
    assert "A_TO_B_MAIN" in routes
    assert routes["A_TO_B_MAIN"].abstract_step_count == 8
