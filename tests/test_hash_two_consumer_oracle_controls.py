from copy import deepcopy
import json
from pathlib import Path
import pytest
from _hash_two_consumer_oracle import assert_hash_empty_insert,assert_fixed_capacity_source
P=Path(__file__).resolve().parents[1]/"openspec/changes/archive/2026-10-13-audit-local-quality-and-unified-controls/evidence/visible-hash-two-consumers-low"
def fixture():
    return json.loads((P/"hash-consumers-before-traces.json").read_text(encoding="utf-8"))[-1]
def test_original_capture_matches_c_oracle():
    assert_hash_empty_insert(fixture())
@pytest.mark.parametrize("fault",["drop","order","source","mask","key","value","next","capacity","count","allocation","free","link","snapshot"])
def test_corrupt_original_capture_rejected(fault):
    r=deepcopy(fixture());s=r["execution_trace"]["steps"]
    if fault=="drop":s.pop(8)
    elif fault=="order":s[7],s[8]=s[8],s[7]
    elif fault=="source":s[13]["line_index"]=s[14]["line_index"]
    elif fault=="mask":s[13]["debug"]["heap"][0]["initialized_mask"]=7
    elif fault in ("key","value","next"):s[14]["debug"]["heap"][0][fault]=99
    elif fault=="capacity":s[16]["debug"]["root"]["capacity"]=10
    elif fault=="count":s[16]["debug"]["count_writes"]=1
    elif fault=="allocation":s[10]["debug"]["allocations"]=1
    elif fault=="free":s[18]["debug"]["freed"]=["0xHASH-1"]
    elif fault=="link":s[15]["debug"]["link_writes"]=2
    else:s[16]["state_after"]["metadata"]["size"]=1
    with pytest.raises(AssertionError):assert_hash_empty_insert(r)
def test_comments_are_not_executable_resize():
    source=(P/"before-3.bin").read_text(encoding="utf-8")
    assert_fixed_capacity_source(source+"\n/* realloc( and rehash( are forbidden here. */")
@pytest.mark.parametrize("statement",["realloc(tabla, 9);","rehash(tabla);","tabla->capacidad = 9;"])
def test_executable_resize_rejected(statement):
    source=(P/"before-3.bin").read_text(encoding="utf-8").replace("tabla->cantidad++;",statement+" tabla->cantidad++;")
    with pytest.raises(AssertionError):assert_fixed_capacity_source(source)
