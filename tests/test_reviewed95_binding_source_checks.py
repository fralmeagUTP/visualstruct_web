"""Check exact source guards without importing/executing application tests."""
import ast
import pytest
from scripts.build_reviewed95_bindings import assertion,params,helper

def function(source):
    return ast.parse(source).body[0]

def test_expected_must_belong_to_the_referenced_function():
    f=function("def test_case():\n    assert result['items'] == [1,2,3]\n")
    assert assertion(f,"result['items'] == [1,2,3]")['line']==2
    with pytest.raises(ValueError):assertion(f,"result['items'] == [3,2,1]")

def test_only_explicit_literal_parameter_set_can_be_resolved():
    f=function("@pytest.mark.parametrize('phase',['a','b'])\ndef test_case(phase):\n    pass\n")
    assert params(f,'phase')==['a','b']
    with pytest.raises(ValueError):params(f,'algorithm')
    dynamic=function("@pytest.mark.parametrize('phase',lookup())\ndef test_case(phase):\n    pass\n")
    with pytest.raises(ValueError):params(dynamic,'phase')

def test_helper_must_dispatch_the_expected_path_and_exact_payload():
    t=ast.parse("def _post(client,operation,payload):\n    return client.post('/graph/graph/operate',json={'operation':operation,'payload':payload})\n")
    assert helper(t,"'/graph/graph/operate'")['name']=='_post'
    with pytest.raises(AssertionError):helper(t,"'/other/operate'")
    wrong=ast.parse("def _post(client,operation,payload):\n    return client.post('/graph/graph/operate',json={'operation':'different','payload':payload})\n")
    with pytest.raises(AssertionError):helper(wrong,"'/graph/graph/operate'")
