"""Route definition loading and validation."""

from __future__ import annotations

import json
from pathlib import Path

from src.models.schemas import RouteDefinition
from src.utils.config import ConfigLoader


class RouteManager:
    """Loads and validates abstract route definitions."""

    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root
        self._routes: dict[str, RouteDefinition] = {}

    def load_routes(self) -> dict[str, RouteDefinition]:
        """Load all route definitions from config/routes.yaml."""
        cfg = ConfigLoader(self.repo_root).load_yaml("routes.yaml")
        routes = cfg.get("routes", [])
        loaded: dict[str, RouteDefinition] = {}
        for route_data in routes:
            route = RouteDefinition.model_validate(route_data)
            loaded[route.route_id] = route
        self._routes = loaded
        return self._routes

    def get_route(self, route_id: str) -> RouteDefinition:
        """Return route by ID or raise KeyError."""
        if not self._routes:
            self.load_routes()
        return self._routes[route_id]

    def all_routes(self) -> list[RouteDefinition]:
        """Return all route definitions."""
        if not self._routes:
            self.load_routes()
        return list(self._routes.values())

    def export_snapshot(self, output_dir: Path) -> Path:
        """Export a route definition snapshot to raw route_definitions directory."""
        if not self._routes:
            self.load_routes()
        output_dir.mkdir(parents=True, exist_ok=True)
        out_file = output_dir / "routes_snapshot.json"
        payload = [route.model_dump(mode="json") for route in self.all_routes()]
        out_file.write_text(json.dumps(payload, indent=2), encoding="utf-8")
        return out_file
