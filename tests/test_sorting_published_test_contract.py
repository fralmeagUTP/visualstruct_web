"""Negative controls for the traceable historical-test portability successor."""
from pathlib import Path
import json
import shutil
import pytest
from scripts.published_test_inputs import audit_input_path
from _sorting_published_test_contract import assert_published_test_successor

ROOT=Path(__file__).resolve().parents[1]

@pytest.fixture(params=['mergesort','counting','burbuja'])
def successor(tmp_path,request):
    source=ROOT/'tests/fixtures/sorting-history'
    shutil.copytree(source,tmp_path/'tests/fixtures/sorting-history')
    algorithm=request.param
    receipt=json.loads((source/(algorithm+'-test-migration.json')).read_text(encoding='utf-8'))
    current=tmp_path/receipt['source']['path'];current.parent.mkdir(parents=True,exist_ok=True)
    current.write_bytes((ROOT/receipt['source']['path']).read_bytes())
    if receipt['original_preimage_available']:
        historical=dict(path=receipt['source']['path'],sha256=receipt['original_declared_sha256'])
    else:
        historical=json.loads(audit_input_path(ROOT/receipt['historical_record']).read_text(encoding='utf-8'))
    return tmp_path,current,historical,algorithm

def test_original_cases_and_assertions_survive_only_fixture_adapters(successor):
    root,current,historical,algorithm=successor
    assert_published_test_successor(root,historical,algorithm)

def test_extra_behavior_or_changed_historical_authority_is_rejected(successor):
    root,current,historical,algorithm=successor
    current.write_text(current.read_text(encoding='utf-8')+'\nassert False\n',encoding='utf-8')
    with pytest.raises(AssertionError):assert_published_test_successor(root,historical,algorithm)
    with pytest.raises(AssertionError):assert_published_test_successor(root,{**historical,'sha256':'changed'},algorithm)
