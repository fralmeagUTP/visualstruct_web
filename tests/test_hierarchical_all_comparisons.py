"""Complete comparison catalogue and isolated execution acceptance tests."""
from __future__ import annotations

from copy import deepcopy
from html.parser import HTMLParser
from itertools import permutations

import pytest

from _final_hierarchy_oracle import assert_final_hierarchical_invariant
from app.services.hierarchical_structure_service import HierarchicalStructureService as Service

STRUCTURES = {"abb": "abb", "avl": "avl", "red-black": "red_black", "heap": "binary_heap"}
PAIRS = [(f"{left}-{right}", (STRUCTURES[left], STRUCTURES[right])) for left, right in permutations(STRUCTURES, 2)]
ALL = [(f"{alias}-all", (sid,) + tuple(other for other in STRUCTURES.values() if other != sid)) for alias, sid in STRUCTURES.items()]
CASES = PAIRS + ALL


@pytest.mark.parametrize("kind,expected", CASES)
@pytest.mark.parametrize("values", [[9, 3, 7, 1, 12], list(range(1, 32)), list(range(31, 0, -1)), [-2147483648, 0, 2147483647]])
def test_every_comparison_has_independent_synchronized_valid_states(kind, expected, values):
    original = values[:]
    result = Service.compare_structures(kind, values)
    assert result["input"] == original == values
    assert result["isolated"] is True
    assert tuple(side["structure"] for side in result["sides"]) == expected
    assert len({id(side["final_state"]) for side in result["sides"]}) == len(expected)
    if len(expected) == 2:
        assert result["left"] == result["sides"][0]
        assert result["right"] == result["sides"][1]
    for side in result["sides"]:
        assert side["size"] == len(original) and side["validation"] is True
        assert [step["inserted"] for step in side["timeline"]] == original
        assert [step["step"] for step in side["timeline"]] == list(range(1, len(original) + 1))
        for step in side["timeline"]:
            assert step["state"]["size"] == step["step"]
            assert step["validation"] is True
            assert_final_hierarchical_invariant(side["structure"], step["state"])
        assert_final_hierarchical_invariant(side["structure"], side["final_state"])
    assert Service.compare_structures(kind, original) == result
    result["sides"][0]["timeline"][0]["state"]["root"]["value"] = 999
    assert result["sides"][0]["final_state"] != result["sides"][0]["timeline"][0]["state"]
    assert result["sides"][1]["timeline"][0]["state"]["root"]["value"] == original[0]
    assert values == original


@pytest.mark.parametrize("kind,expected", CASES)
def test_comparison_endpoint_keeps_all_session_data(client, kind, expected):
    with client.session_transaction() as session:
        session["hierarchical::abb"] = [{"operation": "insertar", "payload": {"value": 88}}]
        session["comparison_test_marker"] = {"nested": [1, 2, 3]}
        before = deepcopy(dict(session))
    response = client.post("/hierarchical/compare", json={"kind": kind, "values": [9, 3, 7]})
    assert response.status_code == 200
    assert tuple(side["structure"] for side in response.json["sides"]) == expected
    with client.session_transaction() as session:
        assert dict(session) == before


@pytest.mark.parametrize("kind,values", [
    ("abb-abb", [1]), ("heap-heap", [1]), ("no-such-kind", [1]),
    ("abb-all", []), ("heap-all", [1, 1]), ("avl-all", [1.5]),
    ("red-black-all", [True]), ("abb-all", [None]),
    ("heap-all", list(range(32))), ("abb-all", [2147483648]),
    ("avl-all", [-2147483649]), ("heap-all", "1,2,3"),
])
def test_invalid_comparison_is_rejected(client, kind, values):
    response = client.post("/hierarchical/compare", json={"kind": kind, "values": values})
    assert response.status_code == 400
    assert response.json["success"] is False


class SelectOptions(HTMLParser):
    """Read comparison options without relying on a browser dependency."""
    def __init__(self):
        super().__init__()
        self.inside = False
        self.options = []
        self.selected = []

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == "select":
            self.inside = attrs.get("id") == "hier-compare-kind"
        if self.inside and tag == "option":
            self.options.append(attrs["value"])
            if "selected" in attrs:
                self.selected.append(attrs["value"])

    def handle_endtag(self, tag):
        if tag == "select":
            self.inside = False


@pytest.mark.parametrize("alias,sid", STRUCTURES.items())
def test_every_structure_page_offers_the_full_catalogue(client, alias, sid):
    parser = SelectOptions()
    parser.feed(client.get(f"/hierarchical/{sid}").get_data(as_text=True))
    assert len(parser.options) == 17
    assert set(parser.options) == {kind for kind, _ in CASES} | {"traversals"}
    assert len(parser.selected) == 1
    assert parser.selected[0].startswith(alias + "-")


def test_heap_validation_checks_order_instead_of_assuming_true(monkeypatch):
    original = Service._new_adapter
    def adapter(structure_id):
        instance = original(structure_id)
        if structure_id == "binary_heap":
            state = instance.to_visual_state
            def invalid_state():
                result = state()
                if len(result["array"]) > 1:
                    result["array"][0] = 999
                return result
            instance.to_visual_state = invalid_state
        return instance
    monkeypatch.setattr(Service, "_new_adapter", adapter)
    result = Service.compare_structures("heap-all", [3, 1])
    assert result["sides"][0]["timeline"][0]["validation"] is True
    assert result["sides"][0]["timeline"][1]["validation"] is False
    assert result["sides"][0]["validation"] is False
