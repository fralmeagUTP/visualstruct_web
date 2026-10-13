"""Heap instruction frames checked against real C, including lifecycle and active tree."""
from pathlib import Path
from _audit_approved_source_supersessions import assert_historical_protected_hash
import json,hashlib
import pytest
from _audit_heapsort_baseline import audit,CASES
ROOT=Path(__file__).resolve().parents[1];E=ROOT/'openspec/changes/archive/2026-10-13-audit-local-quality-and-unified-controls/evidence/visible-sorting-heapsort-instructions';LOW=E.parent/'visible-sorting-heapsort-baseline-low'
@pytest.fixture(scope='module')
def full(tmp_path_factory):
    out=tmp_path_factory.mktemp('heap-full');audit(out);return out
@pytest.mark.parametrize('case',list(CASES))
def test_native_scopes_before_condition_source_and_active_heap(case,full):
    d=json.loads((full/(case+'.json')).read_text(encoding='utf-8'));heap_n=len(CASES[case]);suffix=set();previous={}
    source=d['response']['execution_trace']['source_code'].splitlines()
    from _audit_sorting_c_source import function_body
    canonical=(ROOT/'docs/tads_C/tad_ordenamiento.c').read_text(encoding='utf-8')
    for function in ('ordenar_heapsort','heapify','intercambiar','arreglo_valido'):assert function_body(canonical,function) in d['response']['execution_trace']['source_code']
    for idx,(s,c) in enumerate(zip(d['response']['execution_trace']['steps'],d['native'])):
        event=c['event'];token=event['token'];p=s['pedagogy'];ctx=s['state_after']['heap_context']
        assert s['debug']['instruction_event']==event and s['state_snapshot']['items']==d['native'][max(0,idx-1)]['array']
        assert (p['condition']['result'] if p['condition'] else None)==c['condition']
        assert s['line_text']==('' if token=='initial' else source[s['line_index']])
        assert p['source']['function']==event['function']
        if token=='extract_swap_resume':heap_n=event['i']-1;suffix.add(heap_n)
        if token=='sort_return':heap_n=0;suffix=set(range(len(CASES[case])))
        assert ctx['heap_n']==heap_n and ctx['suffix']==[dict(index=k,value=c['array'][k]) for k in sorted(suffix)]
        assert ctx['nodes']==[dict(index=k,value=c['array'][k],children=[j for j in (2*k+1,2*k+2) if j<heap_n]) for k in range(heap_n)]
        holds=all(c['array'][(k-1)//2]>=c['array'][k] for k in range(1,heap_n));assert ctx['max_heap']==p['invariant']['holds']==holds
        assert s['state_after']['sorted_indices']==sorted(suffix)
        v={(v['scope'],v['name']):v for v in p['variables']}
        for key,var in v.items():
            old=previous.get(key);assert var['previous']==(old['value'] if old else None)
            assert var['changed']==(old is None or (old['value'],old['initialized'])!=(var['value'],var['initialized']))
        previous=v
        calls=[call for call in p['call_stack'] if call['function']=='heapify'];assert len(calls)==len(event['frames'])
        for depth,(f,call) in enumerate(zip(event['frames'],calls),1):
            assert call['parameters']=={'arreglo':'arreglo del caller','n':f['n'],'raiz':f['raiz']}
            for name,value in f.items():
                key=(f'heapify[{depth}]',name)
                if value is None:assert key not in v
                else:assert v[key]['value']==value and v[key]['type']=='size_t' and v[key]['initialized']
        if event['a'] is not None:
            assert p['call_stack'][-1]['function']=='intercambiar'
            assert {ptr['name']:ptr['target'] for ptr in p['pointers']}=={key:f'arreglo[{event[key]}]' for key in ('a','b')}
            assert ('intercambiar','temporal') in v if event['temporal_declared'] else ('intercambiar','temporal') not in v
            if event['temporal_declared']:assert v['intercambiar','temporal']['initialized']==(event['temporal'] is not None)
        else:assert not p['pointers'] and all(key[0]!='intercambiar' for key in v)
        if token=='sort_return':assert not v and not p['call_stack']
    assert len(d['native'])==len(d['response']['execution_trace']['steps'])

def test_mechanical_negative_controls_and_observer_unchanged(full):
    counts=dict(short=0,partial=0,deep=0,nonheap=0,tie=0)
    for case in CASES:
        d=json.loads((full/(case+'.json')).read_text(encoding='utf-8'));native=d['native']
        for idx,c in enumerate(native):
            e=c['event'];token=e['token'];s=d['response']['execution_trace']['steps'][idx]
            if token in ('left_bound','right_bound') and not c['condition']:
                counts['short']+=1;assert native[idx+1]['event']['token']==token.replace('bound','test')
            if token=='swap_assign_a':
                counts['partial']+=1;assert c['array'][e['a']]==c['array'][e['b']] and e['temporal'] is not None
                before=native[idx-1]['array'];assert sorted(c['array'][:e['a']]+[e['temporal']]+c['array'][e['a']+1:])==sorted(before)
            if len(e['frames'])>=3:counts['deep']+=1
            if not s['state_after']['heap_context']['max_heap']:counts['nonheap']+=1
            if token.endswith('_compare'):
                f=e['frames'][-1];child=f['izquierdo' if token=='left_compare' else 'derecho']
                if c['array'][child]==c['array'][f['mayor']]:counts['tie']+=1;assert c['condition'] is False
    assert all(counts.values())
    for name in ('observed.c','native.jsonl'):assert (full/name).read_bytes()==(LOW/'native-final-second'/name).read_bytes()
    for name in ('tad_ordenamiento.c','tad_ordenamiento.h'):
        assert (full/name).read_bytes()==(ROOT/'docs/tads_C'/name).read_bytes()
        assert_historical_protected_hash(ROOT,'docs/tads_C/'+name,hashlib.sha256((LOW/'native-final-second'/name).read_bytes()).hexdigest())
@pytest.mark.parametrize('case',list(CASES))
def test_actual_full_browser_restoration_and_downloaded_callers(case):
    r=json.loads((E/'browser-final-verified/report.json').read_text(encoding='utf-8'));row=next(x for x in r['rows'] if x['case']==case)
    assert row['forward_reverse_restorations']==2*row['instructions'] and row['replay_extra_POSTs']==0 and row['page_errors']==[]
    assert row['JSON_exact_cursor_state_main_preserved'] and row['five_stages'] and row['reload_main_preserved'] and row['recursive_scopes_active_heap_suffix_match_C']
    caller=row['caller'];assert caller['strict_C17'] and caller['doxygen_warnings']==0 and caller['allocations']==caller['frees']==caller['live']==0 and caller['successful_native_runs']==1
    assert r['empty_UI_rejected'] and r['empty_caller']['successful_native_runs']==0

def test_original_regressions_and_seven_modules_hashes_preserved():
    original=json.loads((E/'original-regressions.json').read_text(encoding='utf-8-sig'));assert hashlib.sha256((ROOT/original['path']).read_bytes()).hexdigest()==original['sha256']
    protected=json.loads((E.parent/'visible-sorting-mergesort-instructions/implementation-hashes.json').read_text(encoding='utf-8'))['files']
    for method in ('intercambio','seleccion','insercion','burbuja','shell','quicksort','mergesort'):
        rel=f'app/domain/sorting/{method}_instructions.py';assert hashlib.sha256((ROOT/rel).read_bytes()).hexdigest()==protected[rel]
