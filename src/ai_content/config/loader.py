"""
Configuration loader utilities.

Supports YAML and environment-based configuration.
"""

from pathlib import Path
from typing import Any
import yaml


def load_yaml_config(path: str | Path) -> dict[str, Any]:
    """
    Load configuration from a YAML file.

    Args:
        path: Path to YAML config file

    Returns:
        Configuration dictionary

    Raises:
        FileNotFoundError: If config file doesn't exist
    """
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f"Config file not found: {path}")

    with open(path, "r") as f:
        config = yaml.safe_load(f)

    return _flatten_config(config) if config else {}


def _flatten_config(config: dict, prefix: str = "") -> dict[str, Any]:
    """
    Flatten nested config into settings-compatible format.

    Converts:
        {"google": {"api_key": "xxx"}}
    To:
        {"google": GoogleSettings(api_key="xxx")}
    """
    result = {}

    for key, value in config.items():
        if isinstance(value, dict):
            # Handle nested sections
            if key in ("google", "aimlapi", "kling"):
                # Pass as nested settings
                result[key] = value
            else:
                # Flatten other nested dicts
                result.update(_flatten_config(value, f"{key}_"))
        else:
            result[f"{prefix}{key}"] = value

    return result


def merge_configs(*configs: dict[str, Any]) -> dict[str, Any]:
    """
    Deep merge multiple configuration dictionaries.

    Later configs override earlier ones.

    Args:
        *configs: Configuration dictionaries to merge

    Returns:
        Merged configuration
    """
    result: dict[str, Any] = {}

    for config in configs:
        for key, value in config.items():
            if (
                key in result
                and isinstance(result[key], dict)
                and isinstance(value, dict)
            ):
                result[key] = merge_configs(result[key], value)
            else:
                result[key] = value

    return result
