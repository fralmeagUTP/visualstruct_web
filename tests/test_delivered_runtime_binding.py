"""Bind the authorized delivery without waiving any old review reference."""
from pathlib import Path
import hashlib
import pytest
from _audit_approved_source_supersessions import delivered_runtime_successor
import _audit_approved_source_supersessions as bindings
import json

ROOT=Path(__file__).resolve().parents[1]
CURRENT='9c053251f39f44681479d312f42a1f882bbb8fcf4bf048bae8cc83843b145456'
HISTORICAL='80f9b5ff6950076406e1574b5bf653e5c8a3c0eb2b72369ff6ee6ee2ecbb7c29'

def test_runtime_matches_user_delivery_and_exact_historical_preimage():
    actual=hashlib.sha256((ROOT/'static/js/interpreter_runtime.js').read_bytes()).hexdigest()
    assert actual==CURRENT
    assert delivered_runtime_successor(ROOT,'static/js/interpreter_runtime.js',{actual},HISTORICAL)

def test_unapproved_runtime_or_another_source_is_never_a_delivery_successor():
    assert not delivered_runtime_successor(ROOT,'static/js/interpreter_runtime.js',{'changed'},HISTORICAL)
    assert not delivered_runtime_successor(ROOT,'docs/tads_C/tad_grafo.c',{CURRENT},HISTORICAL)

def test_delivery_receipt_mutation_fails_closed(tmp_path):
    target=tmp_path/'docs/qa/delivered-runtime-source-20261027.json';target.parent.mkdir(parents=True)
    target.write_bytes((ROOT/'docs/qa/delivered-runtime-source-20261027.json').read_bytes()+b' ')
    with pytest.raises(AssertionError,match='receipt changed'):
        delivered_runtime_successor(tmp_path,'static/js/interpreter_runtime.js',{CURRENT},HISTORICAL)

def test_delivery_does_not_waive_a_failed_historical_review(tmp_path,monkeypatch):
    source=tmp_path/'static/js/interpreter_runtime.js';source.parent.mkdir(parents=True)
    source.write_bytes((ROOT/'static/js/interpreter_runtime.js').read_bytes())
    receipt=tmp_path/'docs/qa/delivered-runtime-source-20261027.json';receipt.parent.mkdir(parents=True)
    receipt.write_bytes((ROOT/'docs/qa/delivered-runtime-source-20261027.json').read_bytes())
    (tmp_path/'review.md').write_bytes(b'different review')
    (tmp_path/'authority.json').write_text(json.dumps({'accepted':HISTORICAL}))
    row={'allowed_historical_sha256':[HISTORICAL],'accepted_current_sha256':HISTORICAL,
         'reference_bindings':{'review.md':hashlib.sha256(b'original review').hexdigest()},
         'authority':{'path':'authority.json','kind':'hash_map','key':'accepted'}}
    monkeypatch.setattr(bindings,'SUPERSESSIONS',{'static/js/interpreter_runtime.js':row})
    with pytest.raises(AssertionError,match='approval binding changed'):
        bindings.assert_historical_protected_hash(tmp_path,'static/js/interpreter_runtime.js',HISTORICAL)
