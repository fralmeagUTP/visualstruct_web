"""Test-only native cp_desencolar lifetime contract for the focal interior tie."""
from __future__ import annotations

def assert_priority_dequeue_lifetime(body: dict) -> None:
    steps = body["execution_trace"]["steps"]
    def one(line):
        matches = [s for s in steps if s["line_text"].strip() == line]
        assert len(matches) == 1
        return matches[0]
    unlink = one("objetivoPrev->sgte = objetivo->sgte;")
    value = one("*valor = objetivo->valor;")
    priority = one("*prioridad = objetivo->prioridad;")
    release = one("free(objetivo);")
    assert steps.index(unlink) < steps.index(value) < steps.index(priority) < steps.index(release)
    original = unlink["pedagogy"]["heap_transition"]["before"]
    assert len(original) == 4 and len({n["id"] for n in original}) == 4
    assert len({n["fields"]["valor"] for n in original}) == len(original)
    by_value = {n["fields"]["valor"]: n for n in original}
    assert set(by_value) == {10, 20, 30, 40}
    ids = {v: n["id"] for v, n in by_value.items()}
    expected = {10: (5, ids[20]), 20: (1, ids[30]), 30: (1, ids[40]), 40: (4, None)}
    for v, n in by_value.items():
        assert n["fields"] == {"valor": v, "prioridad": expected[v][0], "sgte": expected[v][1]}
    identity = ids[20]
    for step in (unlink, value, priority):
        m = step["pedagogy"]["dequeue_memory"]
        cards = m["heap"]
        assert len(cards) == 4 and len({n["id"] for n in cards}) == len(cards)
        transition = step["pedagogy"]["heap_transition"]
        before_cards = transition["before"]
        assert len(before_cards) == 4 and len({n["id"] for n in before_cards}) == len(before_cards)
        assert {n["id"] for n in before_cards} == set(ids.values())
        assert transition["after"] == cards
        heap = {n["id"]: n for n in cards}
        assert len(heap) == 4 and set(heap) == set(ids.values()) and m["retired"] == []
        node = heap[identity]
        assert node["fields"] == by_value[20]["fields"]
        assert node["alive"] is True and node["allocated"] is True and node["freed"] is False
        assert node["status"] == "detached" and node["initialized_mask"] == 7
        assert node["fields_valid"] is True and all(x is True for x in node["field_validity"].values())
        assert heap[ids[10]]["fields"]["sgte"] == ids[30]
        pointer = next(p for p in m["pointers"] if p["name"] == "objetivo")
        assert pointer["target"] == identity and pointer["valid"] is True and pointer["initialized"] is True
        assert pointer["dangling"] is False and pointer["scope_state"] == "active" and pointer["scope"] == "cp_desencolar"
        assert step["pedagogy"]["heap_objects"] == m["heap"]
        assert step["pedagogy"]["heap_transition"]["freed"] == []
        assert [x["value"] for x in step["state_after"]["items"]] == [10, 30, 40]
    assert unlink["pedagogy"]["dequeue_memory"]["outputs"] == {"value": None, "priority": None, "value_written": False, "priority_written": False}
    assert value["pedagogy"]["dequeue_memory"]["outputs"] == {"value": 20, "priority": None, "value_written": True, "priority_written": False}
    assert priority["pedagogy"]["dequeue_memory"]["outputs"] == {"value": 20, "priority": 1, "value_written": True, "priority_written": True}
    m = release["pedagogy"]["dequeue_memory"]
    assert len(m["heap"]) == 3 and {n["id"] for n in m["heap"]} == {ids[v] for v in (10,30,40)}
    assert release["pedagogy"]["heap_objects"] == m["heap"]
    retired = m["retired"]
    assert len(retired) == 1 and retired[0]["id"] == identity
    assert retired[0]["alive"] is False and retired[0]["freed"] is True
    assert retired[0]["historical_fields"] == by_value[20]["fields"] and "fields" not in retired[0]
    assert release["pedagogy"]["heap_transition"]["freed"] == retired
    pointer = next(p for p in m["pointers"] if p["name"] == "objetivo")
    assert pointer["historical_id"] == identity and pointer["valid"] is False and pointer["dangling"] is True
    assert body["result"] == 20 and [x["value"] for x in body["visual_state"]["items"]] == [10,30,40]
