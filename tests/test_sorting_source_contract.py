"""Approved early C-source admission, without sorting or fake success."""
from copy import deepcopy
import pytest
from app.adapters.sorting_adapter import SortingAdapter
from app.domain.sorting import SortingExecutionError, SORTING_ALGORITHMS
from app.services.c_code_service import CCodeService
from app.services.sorting_structure_service import SortingStructureService

@pytest.mark.parametrize("mode", ["fast", "step_by_step"])
@pytest.mark.parametrize("source", [None, "omitted", "", " \n\t", "void ordenar_burbuja(int a[], size_t n) {}", "int ordenar_burbuja(int *arreglo, size_t n) { return ORDENAMIENTO_OK; }"])
def test_invalid_source_rejected_before_interpreter_and_state_change(monkeypatch, mode, source):
    adapter = SortingAdapter()
    adapter.create_array([3, 1, 2])
    before = deepcopy(adapter.__dict__)
    calls = []
    def forbidden(*args, **kwargs):
        calls.append(True)
        raise AssertionError("Interpreter constructed before source rejection")
    monkeypatch.setattr("app.adapters.sorting_adapter.SortingInterpreter", forbidden)
    with pytest.raises(SortingExecutionError, match="[Cc]odigo C"):
        if source == "omitted":
            adapter.run(mode)
        else:
            adapter.run(mode, source_code=source)
    assert calls == []
    assert adapter.__dict__ == before


def test_missing_canonical_provider_is_http400_without_success_history(client, monkeypatch):
    before = client.post("/api/ordenamiento/create-array", json={"values": [3, 1, 2]}).get_json()
    calls = []
    def forbidden(*args, **kwargs):
        calls.append(True)
        raise AssertionError("Interpreter constructed despite missing C provider")
    monkeypatch.setattr("app.adapters.sorting_adapter.SortingInterpreter", forbidden)
    monkeypatch.setattr(CCodeService, "get_structure_data", lambda *_: {"operations": {"burbuja": ""}})
    monkeypatch.setattr(SortingStructureService, "_didactic_content", forbidden)
    response = client.post("/api/ordenamiento/run", json={"mode": "step_by_step", "algorithm_id": "burbuja"})
    data = response.get_json()
    assert response.status_code == 400
    assert data["success"] is False
    assert "codigo c" in data["message"].lower()
    assert data["history"] == before["history"]
    assert data["visual_state"]["items"] == before["visual_state"]["items"]
    assert not data.get("execution_trace", {}).get("steps")
    assert calls == []

@pytest.mark.parametrize("mode", ["fast", "step_by_step"])
def test_invalid_source_preserves_previous_accepted_trace_and_result(monkeypatch, mode):
    source = CCodeService.get_structure_data("sorting_array")["operations"]["burbuja"]
    adapter = SortingAdapter()
    adapter.create_array([3, 1, 2])
    adapter.run(mode, source_code=source)
    before = deepcopy(adapter.__dict__)
    def forbidden(*args, **kwargs):
        raise AssertionError("Invalid input started a second interpreter")
    monkeypatch.setattr("app.adapters.sorting_adapter.SortingInterpreter", forbidden)
    with pytest.raises(SortingExecutionError, match="Codigo C"):
        adapter.run(mode, source_code="")
    assert adapter.__dict__ == before

@pytest.mark.parametrize("kind", ["public_only", "comment_only"])
def test_required_helpers_and_uncommented_c_are_required(monkeypatch, kind):
    from app.services.sorting_source_contract import _without_comments
    source = CCodeService.get_structure_data("sorting_array")["operations"]["burbuja"]
    if kind == "public_only":
        source = CCodeService._extract_function_with_comment(source, "ordenar_burbuja")
    else:
        source = "/*" + _without_comments(source) + "*/"
    adapter = SortingAdapter()
    adapter.create_array([2, 1])
    def forbidden(*args, **kwargs):
        raise AssertionError("Missing executable helper C started interpreter")
    monkeypatch.setattr("app.adapters.sorting_adapter.SortingInterpreter", forbidden)
    with pytest.raises(SortingExecutionError, match="Codigo C"):
        adapter.run("fast", source_code=source)
    assert adapter.to_visual_state()["items"] == [2, 1]

def test_all_eleven_canonical_snippets_and_spacing_comments_pass_preflight():
    from app.services.sorting_source_contract import validate_sorting_source
    operations = CCodeService.get_structure_data("sorting_array")["operations"]
    assert len(SORTING_ALGORITHMS) == 11
    for profile in SORTING_ALGORITHMS:
        algorithm = profile["id"]
        source = operations[algorithm]
        validate_sorting_source(algorithm, source)
        validate_sorting_source(algorithm, "/* unchanged C */\n" + "\n".join("  " + line for line in source.splitlines()))

@pytest.mark.parametrize("mode", ["fast", "step_by_step"])
def test_unsupported_instruction_layout_rejected_before_interpreter(monkeypatch, mode):
    source = CCodeService.get_structure_data("sorting_array")["operations"]["burbuja"]
    adapter = SortingAdapter()
    adapter.create_array([2, 1])
    def forbidden(*args, **kwargs):
        raise AssertionError("Unmappable source layout reached interpreter")
    monkeypatch.setattr("app.adapters.sorting_adapter.SortingInterpreter", forbidden)
    with pytest.raises(SortingExecutionError, match="Codigo C"):
        adapter.run(mode, source_code=source.replace(" ", "  "))
    assert adapter.to_visual_state()["items"] == [2, 1]

@pytest.mark.parametrize("operation", ["run", "step", "compare"])
def test_absent_provider_never_uses_execution_fallback_and_keeps_accepted_history(client, monkeypatch, operation):
    client.post("/api/ordenamiento/create-array", json={"values": [3, 1, 2]})
    accepted = client.post("/api/ordenamiento/run", json={"mode": "fast", "algorithm_id": "burbuja"}).get_json()
    assert accepted["success"] is True
    before = client.get("/api/ordenamiento/state").get_json()
    def forbidden(*args, **kwargs):
        raise AssertionError("Missing C reached interpreter or fallback")
    monkeypatch.setattr("app.adapters.sorting_adapter.SortingInterpreter", forbidden)
    monkeypatch.setattr(SortingStructureService, "_didactic_content", forbidden)
    monkeypatch.setattr(CCodeService, "get_structure_data", lambda *_: None)
    payload = {"mode": "fast", "algorithm_id": "burbuja"} if operation != "compare" else {"values": [3, 1, 2], "left_algorithm": "burbuja", "right_algorithm": "seleccion"}
    response = client.post("/api/ordenamiento/" + operation, json=payload)
    data = response.get_json()
    assert response.status_code == 400
    assert data["success"] is False
    assert "codigo c" in data["message"].lower()
    if operation != "compare":
        assert data["history"] == before["history"]
        assert data["visual_state"]["items"] == before["visual_state"]["items"]
        assert not data.get("execution_trace", {}).get("steps")
    # Only presentation source lookup is restored to read the session; interpreter stays forbidden.
    monkeypatch.undo()
    monkeypatch.setattr("app.adapters.sorting_adapter.SortingInterpreter", forbidden)
    after = client.get("/api/ordenamiento/state").get_json()
    assert after["history"] == before["history"]
    assert after["visual_state"]["items"] == before["visual_state"]["items"]
