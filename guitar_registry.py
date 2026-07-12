from __future__ import annotations

import json
from pathlib import Path
from typing import Any

REGISTRY_PATH = Path(__file__).with_name("guitars.json")

# Read guitars.json
def load_registry() -> dict[str, Any]:
    if not REGISTRY_PATH.exists():
        return {"default": None, "guitars": {}}

    with REGISTRY_PATH.open("r", encoding="utf-8") as handle:
        data = json.load(handle)

    if not isinstance(data, dict):
        raise ValueError("Invalid guitar registry")

    data.setdefault("default", None)
    data.setdefault("guitars", {})
    return data


# Update guitars.json
def save_registry(registry: dict[str, Any]) -> None:
    with REGISTRY_PATH.open("w", encoding="utf-8") as handle:
        json.dump(registry, handle, indent=2, sort_keys=True)
        handle.write("\n")


# Read guitar names
def list_guitar_names() -> list[str]:
    registry = load_registry()
    guitars = registry["guitars"]
    return list(guitars.keys())


# Read individual guitar record
def get_guitar_record(name: str) -> dict[str, Any]:
    registry = load_registry()
    guitars = registry["guitars"]
    guitar = guitars.get(name)
    if guitar is None:
        raise KeyError(f"Unknown guitar: {name}")
    return guitar


# Create new guitar record
def add_guitar_record(name: str, tuning: list[str], default: bool = False) -> dict[str, Any]:
    registry = load_registry()
    guitars = registry["guitars"]
    guitars[name] = {"tuning": tuning}
    if default or registry["default"] is None:
        registry["default"] = name
    save_registry(registry)
    return guitars[name]


# Delete a guitar record
def remove_guitar_record(name: str) -> None:
    registry = load_registry()
    guitars = registry["guitars"]
    if name not in guitars:
        raise KeyError(f"Unknown guitar: {name}")

    del guitars[name]
    if registry["default"] == name:
        registry["default"] = None
    save_registry(registry)


# Update "default" in guitars.json
def set_default_guitar_name(name: str) -> None:
    registry = load_registry()
    guitars = registry["guitars"]
    if name not in guitars:
        raise KeyError(f"Unknown guitar: {name}")

    registry["default"] = name
    save_registry(registry)


# Read "default" in guitars.json
def get_default_guitar_name() -> str | None:
    registry = load_registry()
    default = registry.get("default")
    return default if isinstance(default, str) else None


