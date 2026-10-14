"""Reject synthetic coverage claims without an explicit executable case assignment."""
from pathlib import Path
from copy import deepcopy
import pytest
from scripts import build_app_quality_inventory as inventory

@pytest.fixture
def project(tmp_path):
    folder=tmp_path/"tests";folder.mkdir()
    (folder/"test_contract.py").write_text("def test_contract():\n    assert 1 + 1 == 2\n",encoding="utf-8")
    return tmp_path

def sample(category="operation"):
    return {"items":[{"id":"new-option","category":category,"coverage":{"case_id":"QA-AUTO-ID","layer":"api","oracle":"synthetic"}}]}

def bindings(layer="api"):
    return {"schema":"app-executable-bindings/v1","items":{"new-option":{"test_node":"tests/test_contract.py::test_contract","input":{"value":7},"expected":{"result":7},"layer":layer}}}

def test_generated_case_id_does_not_replace_assignment(project):
    result=inventory.validate_executable_bindings(sample(),{"schema":"app-executable-bindings/v1","items":{}},project_root=project)
    assert result==["Sin prueba ejecutable asignada: new-option"]

def test_actual_node_with_concrete_input_expected_is_assignable(project):
    assert inventory.validate_executable_bindings(sample(),bindings(),project_root=project)==[]

@pytest.mark.parametrize("mutation,reason",[("missing_expected","entrada"),("missing_function","inexistente"),("outside_tests","fuera")])
def test_incomplete_or_unsafe_assignment_is_rejected(project,mutation,reason):
    data=bindings();case=data["items"]["new-option"]
    if mutation=="missing_expected": del case["expected"]
    elif mutation=="missing_function":case["test_node"]="tests/test_contract.py::test_does_not_exist"
    else:case["test_node"]="../private.py::test_secret"
    errors=inventory.validate_executable_bindings(sample(),data,project_root=project)
    assert any(reason in error for error in errors)

def test_control_requires_e2e_assignment(project):
    assert inventory.validate_executable_bindings(sample("control"),bindings(),project_root=project)
    assert inventory.validate_executable_bindings(sample("control"),bindings("e2e"),project_root=project)==[]

def test_anonymous_control_is_reported_in_strict_inventory(project,monkeypatch):
    templates=project/"templates";templates.mkdir();(templates/"example.html").write_text('<button type="button">Avanzar</button>',encoding="utf-8")
    monkeypatch.setattr(inventory,"ROOT",project)
    assert inventory._control_items()==[]
    items=inventory._control_items(include_unidentified=True)
    assert len(items)==1 and items[0]["metadata"]["synthetic_identifier"]
    assert inventory.validate_executable_bindings({"items":items},{"schema":"app-executable-bindings/v1","items":{}},project_root=project)

@pytest.mark.parametrize("value",[[],{}, {"schema":"app-executable-bindings/v1","items":[]}])
def test_invalid_binding_document_is_rejected(project,value):
    assert inventory.validate_executable_bindings(sample(),value,project_root=project)
