"""Step-level checks for C-faithful circular-list traces and code assets."""

from __future__ import annotations

from app.routes.help_routes import _enrich_help_with_c_code
from app.services.c_code_service import CCodeService
from app.services.help_service import HelpService


def _operate(client, operation: str, payload: dict | None = None) -> dict:
    response = client.post(
        "/sequential/circular_list/operate",
        json={"operation": operation, "payload": payload or {}},
    )
    assert response.status_code == 200, response.get_json()
    return response.get_json()


def _steps(result: dict) -> list[dict]:
    return result["execution_trace"]["steps"]


def _matching(result: dict, text: str) -> list[dict]:
    return [step for step in _steps(result) if step["line_text"].strip() == text]


def test_insertions_show_real_allocator_and_publish_only_at_pointer_assignment(client) -> None:
    first = _operate(client, "insertar_final", {"value": "4"})
    steps = _steps(first)
    allocation = next(step for step in steps if "malloc(sizeof(LCirNodo))" in step["line_text"])
    publish = _matching(first, "lista->cabeza = nuevo;")[0]
    assert allocation["state_after"]["items"] == []
    assert allocation["state_after"]["temporaries"]["nuevo"]["allocated"] is True
    assert len(publish["state_after"]["items"]) == 1
    assert first["execution_trace"]["final_state"] == first["visual_state"]

    second = _operate(client, "insertar_final", {"value": "9"})
    tail_link = _matching(second, "lista->cola->sgte = nuevo;")[0]
    new_tail = _matching(second, "lista->cola = nuevo;")[0]
    assert len(tail_link["state_after"]["items"]) == 1
    assert len(new_tail["state_after"]["items"]) == 2
    assert new_tail["state_after"]["cola_sgte"] == "N1"


def test_search_visits_one_full_lap_and_returns_one_based_positions(client) -> None:
    for value in (7, 4, 7, 7):
        _operate(client, "insertar_final", {"value": str(value)})
    result = _operate(client, "buscar_posiciones", {"value": "7"})
    steps = _steps(result)

    assert result["result"] == [1, 3, 4]
    assert sum(step["line_text"].strip() == "do {" for step in steps) == 4
    conditions = [step for step in steps if step["line_text"].strip() == "} while (actual != lista->cabeza);"]
    assert [step["pedagogy"]["condition"]["result"] for step in conditions] == [True, True, True, False]
    assert steps[-1]["state_after"]["items"] == result["visual_state"]["items"]
    assert result["execution_trace"]["final_state"] == result["visual_state"]


def test_empty_search_and_delete_take_only_the_guard_and_return(client) -> None:
    search = _operate(client, "buscar_posiciones", {"value": "7"})
    search_lines = [step["line_text"].strip() for step in _steps(search)]
    assert "return encontrados;" not in search_lines
    assert search_lines[-1] == "return 0;"
    assert "actual = lista->cabeza;" not in search_lines

    delete = _operate(client, "eliminar_primero", {"value": "7"})
    delete_lines = [step["line_text"].strip() for step in _steps(delete)]
    assert delete_lines[-1] == "return false;"
    assert "actual = lista->cabeza;" not in delete_lines
    assert "free(actual);" not in delete_lines


def test_delete_by_value_takes_only_first_match_and_frees_after_unlink(client) -> None:
    for value in (7, 4, 7):
        _operate(client, "insertar_final", {"value": str(value)})
    result = _operate(client, "eliminar_primero", {"value": "7"})

    assert [item["value"] for item in result["visual_state"]["items"]] == [4, 7]
    unlink = _matching(result, "anterior->sgte = actual->sgte;")[0]
    release = _matching(result, "free(actual);")[0]
    assert len(unlink["state_after"]["items"]) == 2
    assert unlink["pedagogy"]["heap_transition"]["freed"] == []
    assert release["pedagogy"]["heap_transition"]["freed"][0]["fields"]["valor"] == 7
    assert result["execution_trace"]["final_state"] == result["visual_state"]


def test_delete_head_and_singleton_follow_real_c_function(client) -> None:
    _operate(client, "insertar_final", {"value": "5"})
    _operate(client, "insertar_final", {"value": "6"})
    result = _operate(client, "eliminar_inicio")
    assert "bool lcir_eliminar_inicio(" in result["execution_trace"]["source_code"]
    assert [item["value"] for item in result["visual_state"]["items"]] == [6]
    assert len(_matching(result, "lista->cabeza = actual->sgte;")) == 1
    assert len(_matching(result, "free(actual);")) == 1
    assert result["execution_trace"]["final_state"] == result["visual_state"]

    singleton = _operate(client, "eliminar_inicio")
    assert singleton["visual_state"]["items"] == []
    assert _matching(singleton, "lista->cabeza = NULL;")
    assert _matching(singleton, "lista->cola = NULL;")


def test_reverse_reverses_each_link_then_swaps_head_and_tail(client) -> None:
    for value in (1, 2, 3, 4):
        _operate(client, "insertar_final", {"value": str(value)})
    result = _operate(client, "invertir")
    steps = _steps(result)

    assert [item["value"] for item in result["visual_state"]["items"]] == [4, 3, 2, 1]
    assert sum(step["line_text"].strip() == "do {" for step in steps) == 4
    assert sum(step["line_text"].strip() == "curr->sgte = prev;" for step in steps) == 4
    assert _matching(result, "lista->cabeza = lista->cola;")
    assert _matching(result, "lista->cola = old_head;")
    assert result["execution_trace"]["final_state"] == result["visual_state"]


def test_clear_detaches_each_node_before_free_and_handles_singleton(client) -> None:
    for value in (1, 2, 3):
        _operate(client, "insertar_final", {"value": str(value)})
    result = _operate(client, "limpiar")
    frees = _matching(result, "free(actual);")
    head_moves = _matching(result, "lista->cabeza = next;")

    assert len(frees) == 3
    assert [len(step["state_after"]["items"]) for step in head_moves] == [2, 1]
    assert all(step["pedagogy"]["heap_transition"]["freed"] for step in frees)
    assert result["visual_state"]["items"] == []
    assert result["visual_state"]["size"] == 0
    assert result["execution_trace"]["final_state"] == result["visual_state"]


def test_help_panel_and_download_share_the_actual_c_functions(client) -> None:
    code = CCodeService.get_structure_data("circular_list")
    help_data = _enrich_help_with_c_code(
        HelpService.get_structure_help("circular_list"), "circular_list"
    )
    methods = {
        method["operation"].split("(", 1)[0]: method["code"]
        for method in help_data["c_methods"]
    }
    source = CCodeService.get_downloadable_tad_file("circular_list", "source").read_text(encoding="utf-8")

    assert set(code["operations"]) == set(methods)
    assert all(methods[name] == snippet for name, snippet in code["operations"].items())
    assert "/* Este TAD en C no define" not in methods["eliminar_inicio"]
    for function in (
        "lcir_crear_nodo", "lcir_insertar_inicio", "lcir_insertar_final",
        "lcir_eliminar_inicio", "lcir_eliminar_primero", "lcir_buscar_posiciones",
        "lcir_invertir", "lcir_destruir",
    ):
        assert f"{function}(" in source
    downloaded = client.get("/help/source/circular_list/source").get_data(as_text=True)
    assert "bool lcir_eliminar_inicio(" in downloaded
    assert "void lcir_destruir(" in downloaded
