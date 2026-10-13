"""Current queries versus retained independent C observations, no result relaxation."""
from pathlib import Path
import json
import pytest
BASE=Path(__file__).resolve().parents[1]/'openspec/changes/archive/2026-10-13-audit-local-quality-and-unified-controls/evidence/visible-hash-get-contains-baseline-low'
CASES=[('empty',3,[]),('chain',3,[(1,10),(4,40),(7,70)]),('negative',3,[(-1,-10),(-4,-40),(-6,-60)]),('extremes',3,[(-2147483648,2147483647),(2147483647,-2147483648)])]
@pytest.mark.parametrize('case,capacity,pairs',CASES)
def test_hash_queries_match_retained_native_each_instruction(client,case,capacity,pairs):
    client.post('/hash/hash_table/operate',json={'operation':'create_table','payload':{'capacity':capacity}})
    for key,value in pairs:client.post('/hash/hash_table/operate',json={'operation':'insert','payload':{'key':key,'value':value}})
    fixtures=json.loads((BASE/'report.json').read_text(encoding='utf-8'))
    for fixture in [r for r in fixtures if r['case']==case]:
        response=client.post('/hash/hash_table/operate',json={'operation':fixture['operation'],'payload':{'key':fixture['key']}});data=response.get_json()
        assert data['result']==fixture['result']
        absent=fixture['operation']=='get' and not fixture['native_result']
        assert response.status_code==(400 if absent else 200)
        assert data['success']==(not absent)
        frames=data['execution_trace']['steps'];native=fixture['native'];assert [f['event_type'] for f in frames]==[n['token'] for n in native]
        for f,n in zip(frames,native):
            debug=f['debug'];assert debug['condition_result']==n['condition']
            assert debug['output']['initialized']==n['output_initialized']
            assert debug['output']['value']==n['output']
            assert debug['comparisons']==n['comparisons'];assert debug['hash_calls']==n['hash_calls']
            assert debug['allocations']==debug['frees']==0
            assert f['state_after']['buckets']==fixture['data']['visual_state']['buckets']
            assert f['state_after']['metadata']==fixture['data']['visual_state']['metadata']
            assert not f['console']
            assert f['pedagogy']['variables']=={**{k:v['value'] for k,v in debug['variables'].items()},'tabla->capacidad':capacity,'tabla->cantidad':len(pairs),'retorno':debug['return_status']}
            for scope in debug['scopes']:
                assert scope['variables']['tabla']['type']=='const TablaHash *'
                assert scope['variables']['tabla']['value']==debug['root_identity']
            if f['event_type']=='key_compare' and n['condition'] is False:assert f['pedagogy']['chain']['found'] is False
        if fixture['operation']=='contains':
            assert frames[0]['debug']['output']['initialized'] is False
            assert frames[-1]['debug']['output']['alive'] is False
            assert not frames[-1]['debug']['variables']
        assert not data['execution_trace']['mutates']

def test_hash_query_history_journal_repetition_and_reloads(client):
    for op,p in [('create_table',{'capacity':3}),('insert',{'key':1,'value':10})]:client.post('/hash/hash_table/operate',json={'operation':op,'payload':p})
    for op,key in [('get',1),('get',1),('get',99),('contains',1),('contains',99)]:
        data=client.post('/hash/hash_table/operate',json={'operation':op,'payload':{'key':key}}).get_json()
        assert len(data['history'])==2
    main=client.get('/help/source/hash_table/main').data
    assert main.count(b'th_buscar(&tabla, 1,')==2 and b'th_buscar(&tabla, 99,' in main
    assert b'th_contiene(&tabla, 99)' in main
    assert data['main_c'].encode()==main
    assert b'"execution_trace"' in client.get('/hash/hash_table').data
    assert client.get('/help/source/hash_table/main').data==main
    client.post('/hash/hash_table/reset')
    reset=client.get('/help/source/hash_table/main').data
    assert b'th_buscar(' not in reset and b'th_contiene(' not in reset
