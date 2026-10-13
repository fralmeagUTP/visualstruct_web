"""Hash equivalence must preserve all pairs with multi-digit integer keys."""
import shutil
import pytest
from app.services.conformance import ConformanceRunner, ScenarioOperation

@pytest.mark.skipif(shutil.which("gcc") is None,reason="gcc unavailable")
def test_hash_native_comparison_with_multidigit_keys_preserves_exact_map():
    operations=[ScenarioOperation("insert",{"key":str(k),"value":str(-k)}) for k in range(1,13)]
    result=ConformanceRunner().compare("hash_table",operations)
    assert result.equivalent
    assert len(result.c_state["state"]["pairs"])==12
    assert dict(result.c_state["state"]["pairs"])=={k:-k for k in range(1,13)}
    assert result.c_state==result.python_state
