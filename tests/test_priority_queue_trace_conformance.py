"""Step-level C/visual conformance checks for the priority queue."""

from __future__ import annotations

from app.routes.help_routes import _enrich_help_with_c_code
from app.services.c_code_service import CCodeService
from app.services.help_service import HelpService


def _operate(client, operation: str, payload: dict | None = None) -> dict:
    response = client.post(
        "/sequential/priority_queue/operate",
        json={"operation": operation, "payload": payload or {}},
    )
    assert response.status_code == 200, response.get_json()
    return response.get_json()


def _line_steps(result: dict, source_line: str) -> list[dict]:
    return [
        step for step in result["execution_trace"]["steps"]
        if step["line_text"].strip() == source_line
    ]


def test_enqueue_exposes_real_allocator_and_keeps_node_temporary_until_link(client) -> None:
    result = _operate(client, "encolar", {"value": "17", "priority": "3"})
    steps = result["execution_trace"]["steps"]
    assert any("static CPNodo *cp_crear_nodo(" in step["line_text"] for step in steps)
    assert any("malloc(sizeof(CPNodo))" in step["line_text"] for step in steps)
    allocated = next(step for step in steps if step.get("event_type") == "allocator_success_return")
    assert allocated["state_after"]["temporaries"]["nuevo"]["allocated"] is True
    assert allocated["state_after"]["items"] == []

    publish = _line_steps(result, "cola->delante = nuevo;")[0]
    assert len(publish["state_after"]["items"]) == 1
    assert publish["state_after"]["atras"] == "NULL"
    assert publish["pedagogy"]["heap_transition"]["freed"] == []
    assert result["execution_trace"]["final_state"] == result["visual_state"]


def test_dequeue_scans_every_node_stably_and_frees_only_after_unlink(client) -> None:
    for value, priority in ((10, 5), (20, 1), (30, 1), (40, 4)):
        _operate(client, "encolar", {"value": str(value), "priority": str(priority)})

    result = _operate(client, "desencolar")
    steps = result["execution_trace"]["steps"]
    assert result["result"] == 20  # Equal priorities retain first arrival.
    assert sum(step["line_text"].strip() == "while (actual != NULL) {" for step in steps) == 5
    assert sum("if (actual->prioridad < objetivo->prioridad)" in step["line_text"] for step in steps) == 4

    unlink = _line_steps(result, "objetivoPrev->sgte = objetivo->sgte;")[0]
    assert len(unlink["state_after"]["items"]) == 3
    assert unlink["state_after"]["temporaries"]["objetivo"]["allocated"] is True
    assert unlink["pedagogy"]["heap_transition"]["freed"] == []

    release = _line_steps(result, "free(objetivo);")[0]
    assert len(release["state_after"]["items"]) == 3
    assert len(release["pedagogy"]["heap_transition"]["freed"]) == 1
    assert release["pedagogy"]["heap_transition"]["freed"][0]["fields"]["value"] == 20
    assert result["execution_trace"]["final_state"] == result["visual_state"]


def test_front_scans_without_mutating_and_marks_progressing_candidate(client) -> None:
    for value, priority in ((10, 8), (20, 5), (30, 2)):
        _operate(client, "encolar", {"value": str(value), "priority": str(priority)})
    before = _operate(client, "frente")["visual_state"]
    result = _operate(client, "frente")
    steps = result["execution_trace"]["steps"]

    assert result["result"] == 30
    assert sum(step["line_text"].strip() == "while (actual != NULL) {" for step in steps) == 3
    assert [step["state_after"].get("out_index") for step in steps if step["line_text"].strip() == "objetivo = actual;"] == [1, 2]
    assert result["visual_state"] == before
    assert all(not step["pedagogy"]["heap_transition"]["freed"] for step in steps)


def test_clear_detaches_each_node_before_its_free_and_leaves_empty_tad(client) -> None:
    for value, priority in ((10, 3), (20, 1), (30, 2)):
        _operate(client, "encolar", {"value": str(value), "priority": str(priority)})

    result = _operate(client, "limpiar")
    steps = result["execution_trace"]["steps"]
    assert len(_line_steps(result, "free(aux);")) == 3
    assert [len(step["state_after"]["items"]) for step in _line_steps(result, "cola->delante = next;")] == [2, 1, 0]
    assert all(len(step["pedagogy"]["heap_transition"]["freed"]) == 1 for step in _line_steps(result, "free(aux);"))
    assert result["visual_state"]["items"] == []
    assert result["visual_state"]["size"] == 0
    assert result["execution_trace"]["final_state"] == result["visual_state"]


def test_panel_help_and_download_use_the_same_real_c_functions(client) -> None:
    code_data = CCodeService.get_structure_data("priority_queue")
    enriched_help = _enrich_help_with_c_code(HelpService.get_structure_help("priority_queue"), "priority_queue")
    help_methods = {method["operation"].split("(", 1)[0]: method["code"] for method in enriched_help["c_methods"]}
    source = CCodeService.get_downloadable_tad_file("priority_queue", "source").read_text(encoding="utf-8")

    assert help_methods["encolar"] == code_data["operations"]["encolar"]
    assert help_methods["limpiar"] == code_data["operations"]["limpiar"]
    assert "static CPNodo *cp_crear_nodo(" in help_methods["encolar"]
    assert "bool cp_encolar(" in help_methods["encolar"]
    assert "void cp_vaciar(" in help_methods["limpiar"]
    assert help_methods["encolar"].count("static CPNodo *cp_crear_nodo(") == 1
    assert all(function in source for function in ("static CPNodo *cp_crear_nodo(", "bool cp_encolar(", "void cp_vaciar("))

    downloaded = client.get("/help/source/priority_queue/source").get_data(as_text=True)
    assert "static CPNodo *cp_crear_nodo(" in downloaded
    assert "void cp_vaciar(" in downloaded
