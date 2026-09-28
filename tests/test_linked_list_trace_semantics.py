"""Regression tests for faithful C playback of the singly linked list."""

from __future__ import annotations

from typing import Any


def _operate(client: Any, operation: str, payload: dict[str, str]) -> dict[str, Any]:
    response = client.post(
        "/sequential/linked_list/operate",
        json={"operation": operation, "payload": payload},
    )
    assert response.status_code == 200
    return response.get_json()


def _lines(data: dict[str, Any]) -> list[str]:
    return [str(step["line_text"]).strip().lower() for step in data["execution_trace"]["steps"]]


def _values(state: dict[str, Any]) -> list[int]:
    return [int(item["value"]) for item in state.get("items", [])]


def _seed(client: Any, *values: int) -> None:
    for value in values:
        _operate(client, "insertar_final", {"value": str(value)})


def test_insert_at_head_publishes_q_only_at_lista_assignment(client: Any) -> None:
    _seed(client, 10)
    data = _operate(client, "insertar_inicio", {"value": "20"})
    steps = data["execution_trace"]["steps"]
    by_line = {str(step["line_text"]).strip(): step for step in steps}

    assert _values(by_line["q->sgte = *lista;"]["state_after"]) == [10]
    assert by_line["q->sgte = *lista;"]["state_after"]["temporaries"]["q"]["nro"] == 20
    assert _values(by_line["*lista = q;"]["state_after"]) == [20, 10]
    assert data["execution_trace"]["final_state"] == data["visual_state"]


def test_append_follows_only_nonempty_branch_and_commits_at_tail_link(client: Any) -> None:
    _seed(client, 10, 20)
    data = _operate(client, "insertar_final", {"value": "30"})
    lines = _lines(data)
    steps = data["execution_trace"]["steps"]

    assert "*lista = q;" not in lines
    assert lines.count("while (t->sgte != null) {") == 2
    tail_link = next(step for step in steps if "t->sgte = q;" in step["line_text"])
    assert _values(tail_link["state_snapshot"]) == [10, 20]
    assert _values(tail_link["state_after"]) == [10, 20, 30]


def test_positional_insert_uses_documented_base_position_semantics(client: Any) -> None:
    _seed(client, 10, 20, 30)
    data = _operate(client, "lista_insertar_elemento", {"value": "99", "position": "2"})

    assert _values(data["visual_state"]) == [10, 20, 99, 30]
    link_q = next(
        step for step in data["execution_trace"]["steps"] if "q->sgte = t->sgte" in step["line_text"]
    )
    link_t = next(
        step for step in data["execution_trace"]["steps"] if "t->sgte = q" in step["line_text"]
    )
    assert _values(link_q["state_after"]) == [10, 20, 30]
    assert _values(link_t["state_after"]) == [10, 20, 99, 30]


def test_invalid_position_releases_q_without_executing_insert_branch(client: Any) -> None:
    _seed(client, 10)
    data = _operate(client, "lista_insertar_elemento", {"value": "99", "position": "9"})
    lines = _lines(data)
    console = [line for step in data["execution_trace"]["steps"] for line in step.get("console", [])]

    assert "q->sgte = t->sgte;" not in lines
    assert "t->sgte = q;" not in lines
    assert "free(q);" in lines
    assert any("posicion no encontrada" in line.lower() for line in console)
    assert _values(data["visual_state"]) == [10]


def test_delete_head_does_not_continue_into_nonexecuted_loop_path(client: Any) -> None:
    _seed(client, 10, 20)
    data = _operate(client, "eliminar_elemento", {"value": "10"})
    lines = _lines(data)
    steps = data["execution_trace"]["steps"]

    assert "*lista = p->sgte;" in lines
    assert "free(p);" in lines
    assert "ant = p;" not in lines
    assert not any("valor no encontrado" in line for line in lines)
    detach = next(step for step in steps if "*lista = p->sgte" in step["line_text"])
    free = next(step for step in steps if "free(p)" in step["line_text"])
    assert _values(detach["state_after"]) == [20]
    assert free["pedagogy"]["heap_transition"]["freed"][0]["fields"]["nro"] == 10


def test_clear_removes_one_head_per_called_operation(client: Any) -> None:
    _seed(client, 10, 20, 30)
    data = _operate(client, "limpiar", {})
    states = [_values(step["state_after"]) for step in data["execution_trace"]["steps"]]

    assert [20, 30] in states
    assert [30] in states
    assert states[-1] == []


def test_search_reports_each_c_printf_position_and_skips_not_found_branch(client: Any) -> None:
    _seed(client, 7, 9, 7)
    data = _operate(client, "buscar_elemento", {"value": "7"})
    lines = _lines(data)
    console = [line for step in data["execution_trace"]["steps"] for line in step.get("console", [])]

    assert lines.count('printf("\\n encontrado en la posicion %d\\n", i);') == 2
    assert "if (!encontrado) {" not in lines
    assert console == ["\n Encontrado en la posicion 1", "\n Encontrado en la posicion 3"]


def test_delete_repeated_unlinks_and_frees_each_matching_node(client: Any) -> None:
    _seed(client, 7, 9, 7, 7)
    data = _operate(client, "eliminar_repetidos", {"value": "7"})
    steps = data["execution_trace"]["steps"]
    states = [_values(step["state_after"]) for step in steps]
    lines = _lines(data)

    assert states.count([9, 7, 7]) >= 1
    assert states.count([9, 7]) >= 1
    assert states.count([9]) >= 1
    assert lines.count("free(temp);") == 3
    assert all("valores eliminados" not in line for line in lines[:-1])
