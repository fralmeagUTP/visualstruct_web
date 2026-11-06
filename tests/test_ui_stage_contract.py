"""Positive and negative controls for the exact family-specific stage labels."""

from __future__ import annotations

import pytest

from ui_stage_contract import STAGES, assert_stage_contract, expected_stages

PATHS = ["/sequential/stack", "/hash/hash_table", "/sorting/visualizador"]


@pytest.mark.parametrize("path", PATHS)
def test_exact_reviewed_family_contract(path: str) -> None:
    labels = expected_stages(path)
    assert len(labels) == 5
    assert [label.split(" ", 1)[0] for label in labels] == list("12345")
    assert labels[0] == "1 Preparar y controlar ejecución"
    assert_stage_contract(labels, path)


def test_only_exact_named_paths_have_descriptive_variants() -> None:
    assert expected_stages("/hash/hash_table")[1] == "2 Visualizar y ejecutar: Tabla hash"
    assert expected_stages("/sorting/visualizador")[3] == "4 Comprender el método"
    for path in ("/sequential/queue", "/hierarchical/abb", "/graph/graph/construccion",
                 "/hash/other", "/sorting/other"):
        assert expected_stages(path) == list(STAGES)


@pytest.mark.parametrize("path", PATHS)
@pytest.mark.parametrize("mutation", [
    "missing", "duplicate", "reordered", "short_first", "unknown_suffix",
    "unknown_label", "wrong_number", "extra_stage", "missing_number",
])
def test_rejects_incomplete_reordered_duplicate_and_unknown_labels(path: str, mutation: str) -> None:
    labels = expected_stages(path)
    if mutation == "missing":
        del labels[1]
    elif mutation == "duplicate":
        labels[2] = labels[1]
    elif mutation == "reordered":
        labels[1], labels[2] = labels[2], labels[1]
    elif mutation == "short_first":
        labels[0] = "1 Preparar"
    elif mutation == "unknown_suffix":
        labels[3] += " y cualquier otra cosa"
    elif mutation == "unknown_label":
        labels[1] = "2 Elegir otra actividad"
    elif mutation == "wrong_number":
        labels[2] = "2 Relacionar con código"
    elif mutation == "extra_stage":
        labels.append("6 Una etapa adicional")
    else:
        labels[1] = labels[1][2:]
    with pytest.raises(AssertionError):
        assert_stage_contract(labels, path)


@pytest.mark.parametrize("source,target", [
    ("/hash/hash_table", "/sequential/stack"),
    ("/sorting/visualizador", "/sequential/stack"),
    ("/hash/hash_table", "/sorting/visualizador"),
    ("/sorting/visualizador", "/hash/hash_table"),
])
def test_rejects_variant_on_the_wrong_family(source: str, target: str) -> None:
    with pytest.raises(AssertionError):
        assert_stage_contract(expected_stages(source), target)


def test_returns_independent_label_lists() -> None:
    labels = expected_stages("/hash/hash_table")
    labels[0] = "1 Alterado"
    assert expected_stages("/hash/hash_table")[0] == STAGES[0]
