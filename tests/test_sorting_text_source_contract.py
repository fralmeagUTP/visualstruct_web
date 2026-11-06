"""Positive and adversarial checks for the finite Sorting spelling contract."""
from __future__ import annotations

import ast
import copy
import hashlib
import json
from pathlib import Path
import shutil

import pytest

from tests._sorting_text_source_contract import (
    _SOURCE_PAIRS,
    _assert_reviewed_text_delta,
    assert_sorting_text_source_continuity,
)

ROOT = Path(__file__).resolve().parents[1]
FOLDER = ROOT / "tests/fixtures/sorting-source-history"
RECORD = json.loads((FOLDER / "recovered-sources.json").read_text(encoding="utf-8"))
ROWS = {item["path"]: item for item in RECORD["modules"]}


def sources(relative: str) -> tuple[bytes, bytes]:
    return (FOLDER / ROWS[relative]["snapshot"]).read_bytes(), (ROOT / relative).read_bytes()


@pytest.mark.parametrize("relative", _SOURCE_PAIRS)
def test_three_exact_recovered_preimages_and_text_successors(relative: str) -> None:
    old, current = sources(relative)
    assert hashlib.sha256(old).hexdigest() == _SOURCE_PAIRS[relative][0]
    assert hashlib.sha256(current).hexdigest() == _SOURCE_PAIRS[relative][1]
    assert_sorting_text_source_continuity(ROOT, relative, _SOURCE_PAIRS[relative][0])


@pytest.mark.parametrize("relative", _SOURCE_PAIRS)
@pytest.mark.parametrize("mutation", ["operator", "number", "deletion", "narration", "technical_accent"])
def test_ast_contract_rejects_unreviewed_changes(relative: str, mutation: str) -> None:
    old, current = sources(relative)
    tree = ast.parse(current.decode("utf-8-sig"))
    if mutation == "operator":
        node = next(node for node in ast.walk(tree) if isinstance(node, ast.BinOp))
        node.op = ast.Sub() if not isinstance(node.op, ast.Sub) else ast.Add()
    elif mutation == "number":
        node = next(node for node in ast.walk(tree) if isinstance(node, ast.Constant) and type(node.value) is int)
        node.value += 1
    elif mutation == "deletion":
        tree.body.pop()
    elif mutation == "narration":
        target = ROWS[relative]["changes"][0]["after"]
        node = next(node for node in ast.walk(tree) if isinstance(node, ast.Constant) and node.value == target)
        node.value += " Resultado garantizado."
    else:
        node = next(node for node in ast.walk(tree) if isinstance(node, ast.Constant) and node.value == "initial")
        node.value = "ínitial"
    mutated = ast.unparse(tree).encode()
    with pytest.raises(AssertionError):
        _assert_reviewed_text_delta(old, mutated, ROWS[relative]["changes"])


@pytest.mark.parametrize("relative", _SOURCE_PAIRS)
@pytest.mark.parametrize("mutation", ["future_bytes", "receipt", "snapshot", "historical_hash"])
def test_exact_byte_and_provenance_pins_reject_drift(tmp_path: Path, relative: str, mutation: str) -> None:
    folder = tmp_path / "tests/fixtures/sorting-source-history"
    shutil.copytree(FOLDER, folder)
    target = tmp_path / relative
    target.parent.mkdir(parents=True)
    target.write_bytes((ROOT / relative).read_bytes())
    expected = _SOURCE_PAIRS[relative][0]
    if mutation == "future_bytes":
        target.write_bytes(target.read_bytes() + b"\n")
    elif mutation == "receipt":
        receipt = folder / "recovered-sources.json"
        receipt.write_bytes(receipt.read_bytes() + b"\n")
    elif mutation == "snapshot":
        snapshot = folder / ROWS[relative]["snapshot"]
        snapshot.write_bytes(snapshot.read_bytes() + b"\n")
    else:
        expected = "0" * 64
    with pytest.raises(AssertionError):
        assert_sorting_text_source_continuity(tmp_path, relative, expected)


def test_unregistered_source_still_requires_exact_hash(tmp_path: Path) -> None:
    path = tmp_path / "unregistered.py"
    path.write_bytes(b"value = 1\n")
    expected = hashlib.sha256(path.read_bytes()).hexdigest()
    assert_sorting_text_source_continuity(tmp_path, path.name, expected)
    path.write_bytes(b"value = 2\n")
    with pytest.raises(AssertionError):
        assert_sorting_text_source_continuity(tmp_path, path.name, expected)


def test_reviewed_list_cannot_remove_or_add_a_text_delta() -> None:
    relative = next(iter(_SOURCE_PAIRS))
    old, current = sources(relative)
    reviewed = copy.deepcopy(ROWS[relative]["changes"])
    for edited in (reviewed[:-1], reviewed + [reviewed[0]]):
        with pytest.raises(AssertionError):
            _assert_reviewed_text_delta(old, current, edited)
