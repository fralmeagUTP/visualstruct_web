"""Negative controls for explicitly separated historical and current contracts."""
from copy import deepcopy
import json
from pathlib import Path
import zipfile
import pytest
from tests._published_source_successions import assert_published_source_identity, RECEIPT
from _linked_list_api_validation_consumer_oracle import (
    assert_linked_list_mode_validation, MESSAGE,
)
from scripts.published_test_inputs import audit_input_path

ROOT=Path(__file__).resolve().parents[1]


def graph_bytes(path):
    with zipfile.ZipFile(ROOT/'tests/fixtures/published-audit-inputs/inputs.zip') as package:
        return package.read(path),(ROOT/path).read_bytes()


@pytest.mark.parametrize('path',['docs/tads_C/tad_grafo.c','docs/tads_C/tad_grafo.h'])
def test_graph_succession_requires_exact_distinct_historical_and_current_sources(path):
    old,current=graph_bytes(path)
    assert old!=current
    assert_published_source_identity(path,old,current)


@pytest.mark.parametrize('path',['docs/tads_C/tad_grafo.c','docs/tads_C/tad_grafo.h'])
@pytest.mark.parametrize('fault',['historical','current','both','wrong_path','crlf_current','crlf_historical','receipt'])
def test_source_succession_rejects_content_or_authority_mutation(tmp_path,path,fault):
    old,current=graph_bytes(path)
    receipt=(ROOT/RECEIPT).read_bytes()
    if fault=='historical':old+=b'\n'
    elif fault=='current':current+=b'\n'
    elif fault=='both':old=current=b'forged identical source'
    elif fault=='wrong_path':path='docs/tads_C/tad_abb.c'
    elif fault=='crlf_current':current=current.replace(b'\n',b'\r\n')
    elif fault=='crlf_historical':old=old.replace(b'\r\n',b'\n') if b'\r\n' in old else old.replace(b'\n',b'\r\n')
    else:receipt+=b'\n'
    (tmp_path/RECEIPT).parent.mkdir(parents=True);(tmp_path/RECEIPT).write_bytes(receipt)
    with pytest.raises(AssertionError):assert_published_source_identity(path,old,current,root=tmp_path)


def test_non_graph_source_identity_keeps_exact_contents_apart_from_crlf():
    assert_published_source_identity('docs/tads_C/tad_abb.c',b'int x;\r\n',b'int x;\n')
    with pytest.raises(AssertionError):assert_published_source_identity('docs/tads_C/tad_abb.c',b'int x;\n',b'int y;\n')


def test_historical_refusal_and_current_spelling_are_not_interchangeable():
    source=ROOT/'openspec/changes/archive/2026-10-13-audit-local-quality-and-unified-controls/evidence/visible-linked-list-canonical-consumer-low/linkedcanonical-before-call-20-insertar_elemento-wire.json'
    historical=json.loads(audit_input_path(source).read_text())
    payload={'position':'1','relative':'1','value':'1'}
    assert_linked_list_mode_validation(historical['body'],historical['status'],payload,historical=True)
    with pytest.raises(AssertionError):assert_linked_list_mode_validation(historical['body'],historical['status'],payload)
    current=deepcopy(historical);body=current['body'];trace=body['execution_trace']
    body['message']=trace['message']=trace['validation']['message']=MESSAGE
    assert_linked_list_mode_validation(body,current['status'],payload)
    with pytest.raises(AssertionError):assert_linked_list_mode_validation(body,current['status'],payload,historical=True)
    trace['validation']['message']='different refusal'
    with pytest.raises(AssertionError):assert_linked_list_mode_validation(body,current['status'],payload)


@pytest.mark.parametrize('field',['algorithms','console_output','history','main_c','success','visual_state','execution_mode','execution_trace'])
def test_complete_counting_readonly_gate_rejects_mutated_returned_model(monkeypatch,field):
    from flask.testing import FlaskClient
    import test_sorting_counting_error_instructions as gate
    original=FlaskClient.get
    mutations=[]
    def corrupt_get(client,path,*args,**kwargs):
        response=original(client,path,*args,**kwargs)
        if path=='/api/ordenamiento/state':
            data=response.get_json()
            if data.get('execution_trace',{}).get('error'):
                assert field in data
                data[field]=None;mutations.append(field)
                response.set_data(json.dumps(data))
        return response
    monkeypatch.setattr(FlaskClient,'get',corrupt_get)
    with pytest.raises(AssertionError):
        gate.test_failed_attempt_after_accepted_run_preserves_existing_main_and_latest_trace(monkeypatch)
    assert mutations==[field]
