"""Contracts for the comprehensive QA coverage inventory."""

from __future__ import annotations

import importlib.util
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT_PATH = ROOT / "scripts" / "build_app_quality_inventory.py"
MANIFEST_PATH = ROOT / "docs" / "qa" / "app-coverage-manifest-v1.json"


def _load_builder():
    specification = importlib.util.spec_from_file_location("app_quality_inventory", SCRIPT_PATH)
    assert specification is not None and specification.loader is not None
    module = importlib.util.module_from_spec(specification)
    specification.loader.exec_module(module)
    return module


def test_inventory_assigns_a_case_to_every_published_option() -> None:
    builder = _load_builder()
    inventory = builder.collect_inventory()

    assert builder.validate_inventory(inventory) == []
    assert inventory["summary"]["total"] > 0
    assert {"route", "structure", "operation", "algorithm", "phase", "control"}.issubset(inventory["summary"]["by_category"])


def test_versioned_inventory_is_fresh_and_matches_the_contract() -> None:
    builder = _load_builder()
    expected = builder.collect_inventory()
    committed = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))

    assert committed == expected
