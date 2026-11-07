"""Integration tests for hash routes."""

from __future__ import annotations

import re
from html import unescape
from html.parser import HTMLParser

import pytest

from ui_stage_contract import assert_stage_contract, expected_stages


class _HashHeadings(HTMLParser):
    """Read heading text independently of whitespace and inline markup."""

    def __init__(self) -> None:
        super().__init__()
        self.headings: list[tuple[str, str | None, str]] = []
        self.visual_id_tags: list[str] = []
        self.current: tuple[str, str | None] | None = None
        self.parts: list[str] = []
        self.in_small = False

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        identifiers = [value for name, value in attrs if name == "id"]
        assert len(identifiers) <= 1, "Duplicate id attributes are invalid"
        identifier = identifiers[0] if identifiers else None
        if identifier == "hash-visual-title":
            self.visual_id_tags.append(tag)
        if tag in {"h3", "summary"}:
            self.current = (tag, identifier)
            self.parts = []
        if tag == "small":
            self.in_small = True

    def handle_data(self, data: str) -> None:
        if self.current is not None and not self.in_small:
            self.parts.append(data)

    def handle_endtag(self, tag: str) -> None:
        if tag == "small":
            self.in_small = False
        if self.current is not None and tag == self.current[0]:
            text = " ".join("".join(self.parts).split())
            self.headings.append((*self.current, text))
            self.current = None


def _assert_hash_stage_headings(html: str) -> None:
    parser = _HashHeadings()
    parser.feed(html)
    parser.close()
    assert parser.visual_id_tags == ["h3"]
    title = expected_stages("/hash/hash_table")[1]
    assert [heading for heading in parser.headings if heading[1] == "hash-visual-title"] == [
        ("h3", "hash-visual-title", title),
    ]
    numbered = [text for _, _, text in parser.headings if re.match(r"^\d+\s", text)]
    assert_stage_contract(numbered, "/hash/hash_table")


@pytest.mark.parametrize("mutation", [
    "missing_id", "duplicate_id", "wrong_tag", "missing_number", "wrong_number",
    "wrong_name", "missing_name", "unknown_suffix", "missing_stage", "duplicate_stage", "reordered",
])
def test_hash_structure_heading_contract_rejects_regressions(client, mutation: str) -> None:
    """The route consumer rejects lost identity, descriptions and stage order."""
    html = client.get("/hash/hash_table").get_data(as_text=True)
    title = '<h3 id="hash-visual-title"><span>2</span> Visualizar y ejecutar: Tabla hash</h3>'
    assert html.count(title) == 1
    replacement = title
    if mutation == "missing_id":
        replacement = title.replace('id="hash-visual-title"', 'id="other-title"')
    elif mutation == "duplicate_id":
        replacement += '<div id="hash-visual-title">Duplicate</div>'
    elif mutation == "wrong_tag":
        replacement = title.replace("h3", "div")
    elif mutation == "missing_number":
        replacement = title.replace("<span>2</span> ", "")
    elif mutation == "wrong_number":
        replacement = title.replace("<span>2</span>", "<span>3</span>")
    elif mutation == "wrong_name":
        replacement = title.replace("Tabla hash", "Pila")
    elif mutation == "missing_name":
        replacement = title.replace(": Tabla hash", "")
    elif mutation == "unknown_suffix":
        replacement = title.replace("Tabla hash", "Tabla hash y otra actividad")
    elif mutation == "duplicate_stage":
        replacement += title.replace('id="hash-visual-title"', 'id="duplicate-stage"')
    elif mutation == "missing_stage":
        html = html.replace("<span>4</span> Comprender", "Comprender")
    else:
        first = '<h3 id="hash-prepare-title"><span>1</span> Preparar y controlar ejecución</h3>'
        assert html.count(first) == 1
        html = html.replace(first, "__FIRST_STAGE__").replace(title, first)
        html = html.replace("__FIRST_STAGE__", title)
    with pytest.raises(AssertionError):
        _assert_hash_stage_headings(html.replace(title, replacement))


@pytest.mark.parametrize("attributes", [
    'id="lost-visual-title" id="hash-visual-title"',
    'id="hash-visual-title" id="lost-visual-title"',
    'id="hash-visual-title" id="hash-visual-title"',
])
def test_hash_structure_heading_contract_rejects_duplicate_id_attributes(client, attributes: str) -> None:
    """Reject ambiguous HTML identity through the same gate used for the route."""
    html = client.get("/hash/hash_table").get_data(as_text=True)
    original = '<h3 id="hash-visual-title">'
    assert html.count(original) == 1
    html = html.replace(original, f"<h3 {attributes}>")
    with pytest.raises(AssertionError, match="Duplicate id attributes"):
        _assert_hash_stage_headings(html)


def test_hash_structure_heading_contract_accepts_inline_markup_and_whitespace(client) -> None:
    """Equivalent rendered text need not have identical HTML serialization."""
    html = client.get("/hash/hash_table").get_data(as_text=True)
    html = html.replace(" Visualizar y ejecutar: Tabla hash</h3>",
                        "\n Visualizar y ejecutar: <em>Tabla hash</em>  </h3>")
    _assert_hash_stage_headings(html)


def test_hash_module_page_loads(client) -> None:
    """Hash module index should be reachable."""
    response = client.get("/hash/")
    assert response.status_code == 200
    assert "Módulo de Tablas Hash".encode("utf-8") in response.data


def test_hash_structure_page_loads(client) -> None:
    """Hash structure page should load."""
    response = client.get("/hash/hash_table")
    assert response.status_code == 200
    _assert_hash_stage_headings(response.get_data(as_text=True))


def test_create_table_valid_and_invalid_capacity_via_route(client) -> None:
    """Route should accept valid capacity and block invalid ones."""
    valid = client.post(
        "/hash/hash_table/operate",
        json={"operation": "create_table", "payload": {"capacity": "13"}},
    )
    assert valid.status_code == 200
    assert valid.get_json()["visual_state"]["metadata"]["capacity"] == 13

    invalid = client.post(
        "/hash/hash_table/operate",
        json={"operation": "create_table", "payload": {"capacity": "0"}},
    )
    assert invalid.status_code == 400
    assert "positiva" in invalid.get_json()["message"].lower()


def test_insert_update_search_contains_remove_via_route(client) -> None:
    """Core hash operations should work through routes."""
    insert = client.post(
        "/hash/hash_table/operate",
        json={"operation": "insert", "payload": {"key": "1", "value": "1"}},
    )
    assert insert.status_code == 200

    update = client.post(
        "/hash/hash_table/operate",
        json={"operation": "insert", "payload": {"key": "1", "value": "2"}},
    )
    assert update.status_code == 200
    assert update.get_json()["result"]["updated"] is True

    get_existing = client.post(
        "/hash/hash_table/operate",
        json={"operation": "get", "payload": {"key": "1"}},
    )
    assert get_existing.status_code == 200
    assert get_existing.get_json()["result"] == 2

    get_missing = client.post(
        "/hash/hash_table/operate",
        json={"operation": "get", "payload": {"key": "99"}},
    )
    assert get_missing.status_code == 400
    assert get_missing.get_json()["success"] is False
    assert get_missing.get_json()["result"] is None

    contains = client.post(
        "/hash/hash_table/operate",
        json={"operation": "contains", "payload": {"key": "1"}},
    )
    assert contains.status_code == 200
    assert contains.get_json()["result"] is True

    removed = client.post(
        "/hash/hash_table/operate",
        json={"operation": "remove", "payload": {"key": "1"}},
    )
    assert removed.status_code == 200
    assert removed.get_json()["result"] is True

    missing_remove = client.post(
        "/hash/hash_table/operate",
        json={"operation": "remove", "payload": {"key": "1"}},
    )
    assert missing_remove.status_code == 200
    assert missing_remove.get_json()["result"] is False


def test_queries_stats_visual_collisions_fixed_capacity_and_clear_via_route(client) -> None:
    client.post(
        "/hash/hash_table/operate",
        json={"operation": "create_table", "payload": {"capacity": "3"}},
    )
    client.post(
        "/hash/hash_table/operate",
        json={"operation": "insert", "payload": {"key": "1", "value": "10"}},
    )
    client.post(
        "/hash/hash_table/operate",
        json={"operation": "insert", "payload": {"key": "4", "value": "40"}},
    )
    third = client.post(
        "/hash/hash_table/operate",
        json={"operation": "insert", "payload": {"key": "7", "value": "70"}},
    )
    assert third.status_code == 200
    state_after_insert = third.get_json()["visual_state"]
    assert state_after_insert["metadata"]["capacity_policy"] == "fixed"
    assert state_after_insert["metadata"]["capacity"] == 3
    assert state_after_insert["metadata"]["collisions"] == 2

    keys = client.post("/hash/hash_table/operate", json={"operation": "keys", "payload": {}})
    values = client.post("/hash/hash_table/operate", json={"operation": "values", "payload": {}})
    items = client.post("/hash/hash_table/operate", json={"operation": "items", "payload": {}})
    stats = client.post("/hash/hash_table/operate", json={"operation": "stats", "payload": {}})

    assert keys.status_code == 200
    assert values.status_code == 200
    assert items.status_code == 200
    assert stats.status_code == 200
    assert stats.get_json()["result"]["size"] == 3

    clear = client.post("/hash/hash_table/operate", json={"operation": "clear", "payload": {}})
    assert clear.status_code == 200
    assert clear.get_json()["visual_state"]["metadata"]["size"] == 0


def test_hash_session_persistence_and_reset(client) -> None:
    """Hash history should persist in session and reset correctly."""
    client.post(
        "/hash/hash_table/operate",
        json={"operation": "insert", "payload": {"key": "42", "value": "420"}},
    )
    get_result = client.post(
        "/hash/hash_table/operate",
        json={"operation": "get", "payload": {"key": "42"}},
    )
    assert get_result.status_code == 200
    assert get_result.get_json()["result"] == 420

    reset = client.post("/hash/hash_table/reset")
    assert reset.status_code == 200
    assert reset.get_json()["visual_state"]["metadata"]["size"] == 0


def test_hash_help_pages_available(client) -> None:
    """Hash module and structure help pages should be reachable."""
    module_help = client.get("/help/hash")
    structure_help = client.get("/help/hash/hash_table")

    assert module_help.status_code == 200
    assert "Ayuda del módulo de tablas hash".encode("utf-8") in module_help.data
    assert structure_help.status_code == 200
    page = structure_help.get_data(as_text=True)
    method_cards = re.findall(r'<details><summary>(.*?)</summary>\s*<p>(.*?)</p>\s*<pre class="didactic-code">(.*?)</pre></details>', page, re.S)
    assert method_cards
    for symbol in ('th_inicializar', 'th_insertar', 'th_buscar', 'th_eliminar'):
        matches = [(heading, explanation, unescape(code)) for heading, explanation, code in method_cards if re.search(r'\b' + symbol + r'\s*\(', unescape(code))]
        assert matches, symbol
        assert any(re.sub(r'<[^>]+>', '', explanation).strip() for heading, explanation, code in matches), symbol
