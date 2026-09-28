"""Regression tests for C-faithful linked queue traces."""

from __future__ import annotations


def _values(step: dict) -> list[int]:
    return [item["value"] for item in step["state_after"].get("items", [])]


def _trace(client, operation: str, payload: dict, *, status: int = 200) -> list[dict]:
    response = client.post(
        "/sequential/queue/operate",
        json={"operation": operation, "payload": payload},
    )
    assert response.status_code == status
    return response.get_json()["execution_trace"]["steps"]


def test_enqueue_follows_only_the_actual_empty_or_nonempty_branch(client) -> None:
    empty_steps = _trace(client, "encolar", {"value": 10})
    empty_lines = [step["line_text"].strip() for step in empty_steps]
    assert any("q->delante = aux" in line for line in empty_lines)
    assert not any("q->atras->sgte = aux" in line for line in empty_lines)
    empty_by_line = {step["line_text"].strip(): step for step in empty_steps}
    assert _values(empty_by_line["aux->nro = valor;"]) == []
    assert _values(empty_by_line["q->delante = aux;  // Primer elemento encolado"]) == [10]
    assert empty_by_line["q->delante = aux;  // Primer elemento encolado"]["state_after"]["atras"] == "NULL"

    nonempty_steps = _trace(client, "encolar", {"value": 20})
    nonempty_lines = [step["line_text"].strip() for step in nonempty_steps]
    assert any("q->atras->sgte = aux" in line for line in nonempty_lines)
    assert not any("q->delante = aux" in line for line in nonempty_lines)


def test_dequeue_updates_back_only_for_the_last_node_and_prints_empty_error(client) -> None:
    _trace(client, "encolar", {"value": 7})
    steps = _trace(client, "desencolar", {})
    by_line = {step["line_text"].strip(): step for step in steps}

    assert _values(by_line["q->delante = aux->sgte;"]) == []
    assert by_line["q->delante = aux->sgte;"]["state_after"]["atras"] == "N1"
    assert by_line["q->atras = NULL;  // Cola vacía después de desencolar"]["state_after"]["atras"] == "NULL"
    assert by_line["free(aux);"]["pedagogy"]["heap_transition"]["freed"][0]["id"] == "aux"

    empty_steps = _trace(client, "desencolar", {}, status=400)
    printf_step = next(step for step in empty_steps if "printf(" in step["line_text"])
    assert printf_step["console"] == ["Cola vacía. No se puede desencolar."]


def test_clear_disconnects_and_frees_each_queue_node_in_the_same_loop_turn(client) -> None:
    for value in (1, 2):
        _trace(client, "encolar", {"value": value})

    steps = _trace(client, "limpiar", {})
    free_steps = [step for step in steps if step["line_text"].strip() == "free(aux);"]
    assert len(free_steps) == 2
    assert [_values(step) for step in free_steps] == [[2], []]
    assert [step["pedagogy"]["heap_transition"]["freed"][0]["fields"]["nro"] for step in free_steps] == [1, 2]
