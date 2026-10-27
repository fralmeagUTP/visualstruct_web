"""Regression tests for the C-faithful stack teaching trace."""

from __future__ import annotations


def _values(step: dict) -> list[int]:
    return [item["value"] for item in step["state_after"].get("items", [])]


def test_stack_push_publishes_node_only_when_top_is_updated(client) -> None:
    response = client.post(
        "/sequential/stack/operate",
        json={"operation": "apilar", "payload": {"value": 9}},
    )

    assert response.status_code == 200
    steps = response.get_json()["execution_trace"]["steps"]
    by_line = {step["line_text"].strip(): step for step in steps}

    assert _values(by_line["ptrPila aux = (ptrPila) malloc(sizeof(struct NodoPila));"]) == []
    assert _values(by_line["aux->nro = valor;"]) == []
    assert _values(by_line["aux->sgte = *p;"]) == []
    assert _values(by_line["*p = aux;"]) == [9]
    assert by_line["*p = aux;"]["pedagogy"]["heap_transition"]["freed"] == []


def test_stack_pop_keeps_aux_until_the_real_free_and_emits_printf(client) -> None:
    assert client.post(
        "/sequential/stack/operate",
        json={"operation": "apilar", "payload": {"value": 7}},
    ).get_json()["success"]
    response = client.post(
        "/sequential/stack/operate",
        json={"operation": "desapilar", "payload": {}},
    )

    steps = response.get_json()["execution_trace"]["steps"]
    by_line = {step["line_text"].strip(): step for step in steps}
    assert _values(by_line["ptrPila aux = *p;"]) == [7]
    assert _values(by_line["*p = aux->sgte;"]) == []
    assert by_line["*p = aux->sgte;"]["pedagogy"]["heap_transition"]["freed"] == []
    assert by_line["free(aux);"]["pedagogy"]["heap_transition"]["freed"][0]["id"] == "aux"

    empty = client.post(
        "/sequential/stack/operate",
        json={"operation": "desapilar", "payload": {}},
    ).get_json()["execution_trace"]["steps"]
    printf_step = next(step for step in empty if "printf(" in step["line_text"])
    assert printf_step["console"] == ["Pila vacía. No se puede desapilar."]
