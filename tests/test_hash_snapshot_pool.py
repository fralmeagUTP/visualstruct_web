"""Lossless versioned transport, complete C events and compact session ownership."""
from copy import deepcopy
import json
import pytest
from app.domain.hash.snapshot_pool import HashSnapshotPool, compact_hash_trace, expand_hash_trace
from app.services.hash_structure_service import HashStructureService

@pytest.mark.parametrize('operation', ['keys', 'values', 'items', 'stats'])
def test_codec_deep_roundtrip_preserves_complete_logical_trace(operation):
    history = [{'operation':'create_table','payload':{'capacity':3}},
               {'operation':'insert','payload':{'key':-1,'value':2147483647}}]
    logical = HashStructureService.execute_operation('hash_table',operation,{},history)['execution_trace']
    before = deepcopy(logical)
    wire = HashSnapshotPool().pack(logical)
    restored = expand_hash_trace(json.loads(json.dumps(wire)))
    assert logical == before
    # JSON transport, including the legacy HTTP serializer, represents tuples as arrays.
    assert restored == json.loads(json.dumps(before))
    assert restored['steps'][0]['state_snapshot'] is restored['steps'][1]['state_snapshot']
    assert compact_hash_trace(wire) is wire
    assert compact_hash_trace(logical) is logical

@pytest.mark.parametrize('capacity', [64,128])
def test_supported_large_capacity_keeps_complete_compact_checkpoint(client, capacity, tmp_path):
    assert client.post('/hash/hash_table/operate',json={'operation':'create_table','payload':{'capacity':capacity}}).status_code == 200
    budget = 6_000_000 if capacity == 64 else 12_000_000
    for operation in ['keys','stats','items']:
        response = client.post('/hash/hash_table/operate',json={'operation':operation,'payload':{}})
        assert response.status_code == 200
        assert len(response.data) < budget
        data = response.get_json();wire = data['execution_trace']
        assert wire['hash_snapshot_codec'] == 'hash-snapshot-pool/v1'
        trace = expand_hash_trace(wire)
        assert len(trace['steps']) == wire['hash_snapshot_stats']['steps']
        assert wire['hash_snapshot_stats']['sampling'] is False
        assert ''.join(fragment for step in trace['steps'] for fragment in step['console']) == data['console_stdout']
        assert trace['steps'][-1]['state_after'] == data['visual_state']
        with client.session_transaction() as session:
            from app.services.session_service import SESSION_KEY
            checkpoint = session[SESSION_KEY]['hash::hash_table']['checkpoint']['trace']
            assert checkpoint == wire
            assert len(json.dumps(checkpoint)) < budget
        assert client.get('/hash/hash_table').status_code == 200
    client.post('/hash/hash_table/reset')
    with client.session_transaction() as session:
        assert 'hash::hash_table' not in session[SESSION_KEY]

@pytest.mark.parametrize('bad', [True,-1,999999,'0'])
def test_decoder_rejects_invalid_reference(bad):
    with pytest.raises(ValueError):
        expand_hash_trace({'hash_snapshot_codec':'hash-snapshot-pool/v1','hash_snapshot_pool':[[1,[{'$hash_ref':bad}]]],'steps':[]})

@pytest.mark.parametrize('records', [[[0,[['a',1,2]]]], [[0,[['a',1],['a',2]]]], [[1,[{'$hash_ref':1}]]], [[1,[{'$hash_ref':0}]]]])
def test_decoder_rejects_malformed_pairs_duplicate_and_cyclic_records(records):
    with pytest.raises(ValueError):
        expand_hash_trace({'hash_snapshot_codec':'hash-snapshot-pool/v1','hash_snapshot_pool':records,'steps':[]})


def test_actual_javascript_decoder_and_runtime(tmp_path):
    import os
    import subprocess
    from qa.generate_hash_snapshot_fixture import make_fixture
    fixture = tmp_path / 'hash-snapshot.json'
    fixture.write_text(json.dumps(make_fixture(3)), encoding='utf-8')
    result = subprocess.run(['node','qa/hash_snapshot_codec_check.js',str(fixture)], capture_output=True, text=True, timeout=45, env=os.environ.copy())
    assert result.returncode == 0, result.stdout + result.stderr
    assert 'real steps rendered/seeked' in result.stdout

@pytest.mark.parametrize('capacity', [3,8])
@pytest.mark.parametrize('populated', [False,True])
@pytest.mark.parametrize('operation', ['keys','values','items','stats'])
def test_constructor_interning_equals_independent_copies(monkeypatch, capacity, populated, operation):
    """Catch alias mutation independently of the wire codec's own roundtrip."""
    import app.domain.hash.listing_instruction as listing
    import app.domain.hash.stats_instruction as stats
    history = [{'operation':'create_table','payload':{'capacity':capacity}}]
    if populated:
        history += [{'operation':'insert','payload':{'key':key,'value':value}}
                    for key,value in [(-1,10),(capacity-1,-20),(2*capacity-1,30)]]
    shared = HashStructureService.execute_operation('hash_table',operation,{},history)
    class IndependentCopies:
        def intern(self, value):
            return deepcopy(value)
    monkeypatch.setattr(listing,'HashSnapshotPool',IndependentCopies)
    monkeypatch.setattr(stats,'HashSnapshotPool',IndependentCopies)
    independent = HashStructureService.execute_operation('hash_table',operation,{},history)
    assert json.loads(json.dumps(shared)) == json.loads(json.dumps(independent))
