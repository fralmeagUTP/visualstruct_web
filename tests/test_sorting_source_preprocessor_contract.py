"""Focal rejected preprocessing counterexample; no native C execution."""
from copy import deepcopy
import pytest
from app.adapters.sorting_adapter import SortingAdapter
from app.domain.sorting import SORTING_ALGORITHMS
from app.services.c_code_service import CCodeService
from app.services.sorting_source_contract import SortingSourceError, validate_sorting_source

@pytest.mark.parametrize("algorithm", [p["id"] for p in SORTING_ALGORITHMS])
@pytest.mark.parametrize("mode", ["fast", "step_by_step"])
def test_disabled_canonical_source_rejected_before_interpreter(monkeypatch, algorithm, mode):
    source = CCodeService.get_structure_data("sorting_array")["operations"][algorithm]
    adapter = SortingAdapter()
    adapter.create_array([2, 1])
    adapter.select_algorithm(algorithm)
    before = deepcopy(adapter.__dict__)
    calls = []
    def forbidden(*args, **kwargs):
        calls.append(True)
        raise AssertionError("Disabled C reached interpreter")
    monkeypatch.setattr("app.adapters.sorting_adapter.SortingInterpreter", forbidden)
    with pytest.raises(SortingSourceError, match="Codigo C"):
        adapter.run(mode, source_code="#if 0\n" + source + "\n#endif")
    assert calls == []
    assert adapter.__dict__ == before

@pytest.mark.parametrize("prefix", ["#define ordenar_burbuja otra_funcion\n", "#undef ordenar_burbuja\n", "#if 1\n#endif\n", "%:if 0\n%:endif\n", "??=if 0\n??=endif\n", "#\\\nif 0\n#endif\n", "??=??/\nif 0\n??=endif\n", "/* comment */ #define size_t int\n"])
def test_preprocessing_outside_supported_subset_rejected_before_interpreter(monkeypatch, prefix):
    source = CCodeService.get_structure_data("sorting_array")["operations"]["burbuja"]
    adapter = SortingAdapter()
    adapter.create_array([2, 1])
    before = deepcopy(adapter.__dict__)
    def forbidden(*args, **kwargs):
        raise AssertionError("Preprocessing reached interpreter")
    monkeypatch.setattr("app.adapters.sorting_adapter.SortingInterpreter", forbidden)
    with pytest.raises(SortingSourceError, match="Codigo C"):
        adapter.run("fast", source_code=prefix + source)
    assert adapter.__dict__ == before

@pytest.mark.parametrize("algorithm", [p["id"] for p in SORTING_ALGORITHMS])
def test_supported_native_source_and_directive_text_in_comments_remain_valid(algorithm):
    source = CCodeService.get_structure_data("sorting_array")["operations"][algorithm]
    validate_sorting_source(algorithm, source)
    validate_sorting_source(algorithm, "/* #if 0\n#define size_t int\n#endif */\n// #if 0\n" + "\n".join("  " + line for line in source.splitlines()))

@pytest.mark.parametrize("operation", ["run", "step", "compare"])
def test_disabled_provider_c_preserves_accepted_history_and_never_constructs(client, monkeypatch, operation):
    client.post("/api/ordenamiento/create-array", json={"values": [3, 1, 2]})
    accepted = client.post("/api/ordenamiento/run", json={"mode": "fast", "algorithm_id": "burbuja"}).get_json()
    assert accepted["success"] is True
    before = client.get("/api/ordenamiento/state").get_json()
    provider = deepcopy(CCodeService.get_structure_data("sorting_array"))
    provider["operations"] = {key: "#if 0\n" + value + "\n#endif" for key, value in provider["operations"].items()}
    calls = []
    def forbidden(*args, **kwargs):
        calls.append(True)
        raise AssertionError("Disabled provider reached interpreter")
    monkeypatch.setattr("app.adapters.sorting_adapter.SortingInterpreter", forbidden)
    monkeypatch.setattr(CCodeService, "get_structure_data", lambda *_: provider)
    payload = {"mode": "fast", "algorithm_id": "burbuja"} if operation != "compare" else {"values": [3, 1, 2], "left_algorithm": "burbuja", "right_algorithm": "seleccion"}
    response = client.post("/api/ordenamiento/" + operation, json=payload)
    data = response.get_json()
    assert response.status_code == 400
    assert data["success"] is False
    assert not data.get("execution_trace", {}).get("steps")
    if operation != "compare":
        assert data["history"] == before["history"]
        assert data["visual_state"]["items"] == before["visual_state"]["items"]
    monkeypatch.undo()
    monkeypatch.setattr("app.adapters.sorting_adapter.SortingInterpreter", forbidden)
    after = client.get("/api/ordenamiento/state").get_json()
    assert after["history"] == before["history"]
    assert after["visual_state"]["items"] == before["visual_state"]["items"]
    assert calls == []
