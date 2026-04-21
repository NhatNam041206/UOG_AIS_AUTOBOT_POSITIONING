"""Configuration loading helpers."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml


class ConfigLoader:
    """Loads YAML configuration from the config directory."""

    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root
        self.config_dir = repo_root / "config"

    def load_yaml(self, file_name: str) -> dict[str, Any]:
        """Load a YAML file into a dictionary."""
        path = self.config_dir / file_name
        if not path.exists():
            return {}
        with path.open("r", encoding="utf-8") as handle:
            return yaml.safe_load(handle) or {}
