"""C-faithful traces, memory transitions and code assets for the sublist TAD."""

from app.routes.help_routes import _enrich_help_with_c_code
from app.services.c_code_service import CCodeService
from app.services.help_service import HelpService


def _operate(client, operation: str, payload: dict | None = None) -> dict:
    response = client.post(
        "/sequential/sublist/operate",
        json={"operation": operation, "payload": payload or {}},
    )
    assert response.status_code == 200, response.get_json()
    return response.get_json()


def _steps(result: dict) -> list[dict]:
    return result["execution_trace"]["steps"]


def _lines(result: dict) -> list[str]:
    return [step["line_text"].strip() for step in _steps(result)]


def _matching(result: dict, source_line: str) -> list[dict]:
    return [step for step in _steps(result) if step["line_text"].strip() == source_line]


def test_parent_insertion_takes_only_empty_or_nonempty_c_branch(client) -> None:
    first = _operate(client, "insertar_padre", {"parent": "4"})
    assert "*lista = nuevo;" in _lines(first)
    assert "actual = *lista;" not in _lines(first)
    allocation = _matching(first, "Nodo *nuevo = (Nodo *)malloc(sizeof(Nodo));")[0]
    assert allocation["state_after"]["items"] == []
    published = _matching(first, "*lista = nuevo;")[0]
    assert published["state_after"]["items"] == first["visual_state"]["items"]

    second = _operate(client, "insertar_padre", {"parent": "8"})
    assert _lines(second).count("while (actual->sgte != NULL) {") == 1
    assert "actual->sgte = nuevo;" in _lines(second)
    assert len(second["visual_state"]["items"]) == 2


def test_child_insertion_shows_allocator_and_links_at_the_real_assignment(client) -> None:
    _operate(client, "insertar_padre", {"parent": "4"})
    first = _operate(client, "insertar_hijo", {"parent": "4", "child": "10"})
    assert "static Sublista *crear_hijo(int valor) {" in _lines(first)
    assert "padre->sub = nuevo;" in _lines(first)
    assert "actual = padre->sub;" not in _lines(first)
    publish = _matching(first, "padre->sub = nuevo;")[0]
    assert publish["state_after"]["items"][0]["children"] == [10]

    second = _operate(client, "insertar_hijo", {"parent": "4", "child": "20"})
    assert "actual = padre->sub;" in _lines(second)
    assert "actual->sgte = nuevo;" in _lines(second)
    assert second["visual_state"]["items"][0]["children"] == [10, 20]


def test_duplicate_parent_values_keep_distinct_identity_and_valid_invariant(client) -> None:
    _operate(client, "insertar_padre", {"parent": "4"})
    result = _operate(client, "insertar_padre", {"parent": "4"})
    parents = result["visual_state"]["items"]
    assert [item["parent"] for item in parents] == [4, 4]
    assert parents[0]["id"] != parents[1]["id"]
    assert all(step["pedagogy"]["invariant"]["holds"] for step in _steps(result))


def test_delete_parent_removes_first_matching_node_and_frees_its_children(client) -> None:
    _operate(client, "insertar_padre", {"parent": "4"})
    _operate(client, "insertar_hijo", {"parent": "4", "child": "10"})
    _operate(client, "insertar_hijo", {"parent": "4", "child": "11"})
    _operate(client, "insertar_padre", {"parent": "4"})
    result = _operate(client, "eliminar_padre", {"parent": "4"})
    assert len(result["visual_state"]["items"]) == 1
    assert result["visual_state"]["items"][0]["children"] == []
    lines = _lines(result)
    assert "return false;" not in lines
    assert lines.count("free(actual);") == 3
    detach = _matching(result, "*lista = actual->sgte;")[0]
    assert detach["pedagogy"]["heap_transition"]["freed"] == []
    frees = _matching(result, "free(actual);")
    assert len(frees[0]["pedagogy"]["heap_transition"]["freed"]) == 1


def test_delete_child_removes_only_first_duplicate_child(client) -> None:
    _operate(client, "insertar_padre", {"parent": "4"})
    for _ in range(3):
        _operate(client, "insertar_hijo", {"parent": "4", "child": "10"})
    result = _operate(client, "eliminar_hijo", {"parent": "4", "child": "10"})
    assert result["visual_state"]["items"][0]["children"] == [10, 10]
    assert _lines(result).count("free(actual);") == 1
    assert "return false;" not in _lines(result)
    unlink = _matching(result, "padre->sub = actual->sgte;")[0]
    free = _matching(result, "free(actual);")[0]
    assert unlink["pedagogy"]["heap_transition"]["freed"] == []
    assert free["pedagogy"]["heap_transition"]["freed"][0]["fields"]["nro"] == 10


def test_delete_parent_on_empty_list_returns_without_scanning(client) -> None:
    result = _operate(client, "eliminar_padre", {"parent": "4"})
    lines = _lines(result)
    assert lines[-1] == "return false;"
    assert "actual = *lista;" not in lines
    assert "free(actual);" not in lines


def test_children_query_uses_real_c_method_and_traverses_matching_sublist(client) -> None:
    _operate(client, "insertar_padre", {"parent": "4"})
    _operate(client, "insertar_hijo", {"parent": "4", "child": "10"})
    _operate(client, "insertar_hijo", {"parent": "4", "child": "20"})
    result = _operate(client, "hijos_de", {"parent": "4"})
    assert result["result"] == [10, 20]
    assert "int sublista_obtener_hijos(" in result["execution_trace"]["source_code"]
    assert _lines(result).count("destino[usados] = actual->nro;") == 2
    assert _lines(result).count("while (actual != NULL && usados < capacidad) {") == 3


def test_clear_detaches_each_child_before_free_and_each_parent_before_free(client) -> None:
    _operate(client, "insertar_padre", {"parent": "4"})
    _operate(client, "insertar_hijo", {"parent": "4", "child": "10"})
    _operate(client, "insertar_hijo", {"parent": "4", "child": "20"})
    _operate(client, "insertar_padre", {"parent": "8"})
    result = _operate(client, "limpiar")
    steps = _steps(result)
    frees = [step for step in steps if step["line_text"].strip() == "free(actual);"]
    assert len(frees) == 4
    assert [step["line_text"].strip() for step in steps].index("*lista_hijos = next;") < [step["line_text"].strip() for step in steps].index("free(actual);")
    assert any(step["state_after"]["items"][0]["children"] == [20] for step in steps if step["state_after"]["items"])
    assert any(step["state_after"]["items"][0]["children"] == [] for step in steps if step["state_after"]["items"])
    assert result["visual_state"]["items"] == []
    assert result["execution_trace"]["final_state"] == result["visual_state"]


def test_help_panel_and_download_use_real_sublist_functions(client) -> None:
    data = CCodeService.get_structure_data("sublist")
    help_data = _enrich_help_with_c_code(
        HelpService.get_structure_help("sublist"), "sublist"
    )
    methods = {method["operation"].split("(", 1)[0]: method["code"] for method in help_data["c_methods"]}
    source = CCodeService.get_downloadable_tad_file("sublist", "source").read_text(encoding="utf-8")
    assert set(data["operations"]) == set(methods)
    assert all(methods[name] == snippet for name, snippet in data["operations"].items())
    for function in ("sublista_insertar_padre_final", "sublista_insertar_hijo", "sublista_eliminar_padre_primero", "sublista_eliminar_hijo", "sublista_obtener_hijos", "sublista_destruir"):
        assert f"{function}(" in source
    assert "/* Consulta de hijos en C" not in methods["hijos_de"]
    assert "void sublista_inicializar(" not in methods["limpiar"]
    downloaded = client.get("/help/source/sublist/source").get_data(as_text=True)
    assert "int sublista_obtener_hijos(" in downloaded
