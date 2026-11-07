"""Finite byte-bound continuity for three reviewed spelling-only successors.

This verifies provenance and the text delta. It is neither a historical
functional approval nor a general normalization rule for future source edits.
"""
from __future__ import annotations

import ast
import hashlib
import json
from pathlib import Path
import unicodedata

_RECEIPT_SHA256 = "dd6b2967c39059d47e1db57027acbbac4da32e1fd49bb71e7f47a5d9c5e303e8"
_SOURCE_PAIRS = {
    "app/domain/sorting/shell_instructions.py": (
        "b69513305892a043e029eff8d7d8b49420e311e7158a2d1acf6911d911df4ba1",
        "28612b1820e76c7563e4c37ee5485333a8f7a972a7d7ed395b7f2913ac80052a",
        9,
    ),
    "app/domain/sorting/quicksort_instructions.py": (
        "ca82081fea5c768893062af935aab76f640c0fc60cdbb75a341d72b461ff1244",
        "c52a5b21f054016fef54ced423325b5d3c35b978c822bb9ff07bfcb2057f655f",
        15,
    ),
    "app/domain/sorting/heapsort_instructions.py": (
        "1d5bac5b1f10447a35b5af96be222e3d26ef0535cec7c5ef113e325b2b076a1d",
        "437f20568cb16b60c6307fa739d51d44d8d6335965c249c343c21a7ad2b9a204",
        4,
    ),
}


def _sha(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def _without_accents(text: str) -> str:
    return "".join(
        char for char in unicodedata.normalize("NFD", text)
        if unicodedata.category(char) != "Mn"
    )


def _assert_reviewed_text_delta(
    historical: bytes, current: bytes, reviewed_changes: list[dict[str, str]]
) -> None:
    """Require the exact reviewed string-literal changes and no other AST delta."""
    changes: list[dict[str, str]] = []

    def compare(old: object, new: object, path: str = "", literal: bool = False) -> None:
        if isinstance(old, ast.AST) and isinstance(new, ast.AST):
            assert type(old) is type(new), (path, "AST node type changed")
            for field in old._fields:
                compare(
                    getattr(old, field), getattr(new, field), path + "." + field,
                    isinstance(old, ast.Constant) and field == "value",
                )
        elif isinstance(old, list) and isinstance(new, list):
            assert len(old) == len(new), (path, "AST sequence changed")
            for index, (left, right) in enumerate(zip(old, new)):
                compare(left, right, f"{path}[{index}]")
        elif type(old) is not type(new) or old != new:
            assert literal and isinstance(old, str) and isinstance(new, str), (
                path, "Non-text AST value changed"
            )
            assert _without_accents(old) == _without_accents(new), (
                path, "Change is not limited to accents"
            )
            changes.append({"ast_path": path, "before": old, "after": new})

    compare(ast.parse(historical.decode("utf-8-sig")), ast.parse(current.decode("utf-8-sig")))
    assert changes == reviewed_changes, "Text changes differ from the individually reviewed delta"


def assert_sorting_text_source_continuity(root: Path, relative: str, expected: str) -> None:
    """Keep exact hashes, allowing only the three fixed and verified text successors."""
    relative = relative.replace("\\", "/")
    current = (root / relative).read_bytes()
    pair = _SOURCE_PAIRS.get(relative)
    if pair is None:
        assert _sha(current) == expected, (relative, "Unregistered protected source drift")
        return

    historical_sha, current_sha, count = pair
    assert expected == historical_sha, (relative, "Unknown historical hash")
    folder = root / "tests/fixtures/sorting-source-history"
    receipt = (folder / "recovered-sources.json").read_bytes()
    assert _sha(receipt) == _RECEIPT_SHA256, "Recovered source provenance or reviewed delta changed"
    record = json.loads(receipt)
    matches = [item for item in record["modules"] if item["path"] == relative]
    assert len(matches) == 1
    row = matches[0]
    assert (row["historical_sha256"], row["current_sha256"], row["changed_literal_count"]) == pair
    assert row["snapshot"] == Path(relative).name + ".snapshot"
    historical = (folder / row["snapshot"]).read_bytes()
    assert _sha(historical) == historical_sha, "Historical source snapshot changed"
    if _sha(current) == historical_sha:
        return
    assert _sha(current) == current_sha, (relative, "Unrecorded current source bytes")
    assert len(row["changes"]) == count
    _assert_reviewed_text_delta(historical, current, row["changes"])
