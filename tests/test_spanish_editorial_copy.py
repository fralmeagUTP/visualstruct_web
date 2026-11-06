"""Regression coverage for Spanish editorial copy, without changing C source text."""
from __future__ import annotations

import pytest

from app.services.c_code_service import CCodeService
from app.services.trace.control_flow import ControlFlowPlanner

FAMILIES = {
    "sequential": ["stack", "queue", "priority_queue", "linked_list", "circular_list", "sublist"],
    "hierarchical": ["abb", "avl", "red_black", "binary_heap"],
    "graph": ["graph"], "hash": ["hash_table"], "sorting": ["sorting_array"],
}
ROUTES = ["/", "/help/manual"]
for family, structures in FAMILIES.items():
    ROUTES += [f"/{family}/", f"/help/{family}"]
    ROUTES += [f"/help/{family}/{structure}" for structure in structures]
    if family not in {"graph", "sorting"}:
        ROUTES += [f"/{family}/{structure}" for structure in structures]
ROUTES += [f"/graph/graph/{phase}" for phase in ["construccion", "recorridos", "camino-minimo", "expansion-minima"]]
ROUTES += ["/sorting/visualizador"]


@pytest.mark.parametrize("route", ROUTES)
def test_pages_preserve_correct_institutional_name(client, route):
    response = client.get(route)
    assert response.status_code == 200
    text = response.get_data(as_text=True)
    assert "Universidad Tecnológica de Pereira, Facultad de Ingenierías" in text
    assert "Universidad Tecnologica de Pereira" not in text
    assert "\ufffd" not in text


@pytest.mark.parametrize("structure", [s for structures in FAMILIES.values() for s in structures])
def test_c_panel_title_uses_accent_without_changing_structure_identifiers(structure):
    data = CCodeService.get_structure_data(structure)
    assert data is not None
    assert data["code_title"] == ("Código C canónico del libro — tad_grafo.c" if structure == "graph" else "Código C")
    assert data["record"]


@pytest.mark.parametrize("title", ["Codigo C", "Código C", "CÓDIGO C: Insertar"])
def test_c_directives_remain_nonexecutable_with_accented_title(title):
    assert not ControlFlowPlanner.is_executable_line("#include <stdio.h>", title)
    assert ControlFlowPlanner.is_executable_line("int x = 1;", title)
    assert not ControlFlowPlanner.is_executable_line("// Comentario", title)


@pytest.mark.parametrize("label", ["Insertar posición", "Eliminar posición", "Último"])
def test_help_labels_do_not_inherit_unaccented_operation_identifiers(client, label):
    response = client.get("/help/sequential/linked_list")
    assert response.status_code == 200
    assert f"{label} · código C" in response.get_data(as_text=True)
