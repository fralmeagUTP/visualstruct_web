"""Counting isolated compact core: frozen real C events, deltas/spans and budgets."""
from pathlib import Path
import json,pytest
from app.domain.sorting.counting_sparse_instructions import run_counting_sparse_trace
from app.domain.sorting.counting_sparse_tape import expand_small,sparse_window
ROOT=Path(__file__).resolve().parents[1];B=ROOT/'openspec/changes/audit-local-quality-and-unified-controls';OLD=B/'evidence/visible-sorting-counting-baseline-low/native-final';E=B/'evidence/visible-sorting-counting-expanded-fidelity'
@pytest.mark.parametrize('case',['single','ordered','reverse','duplicates','negative','extremes'])
def test_frozen_real_C_events_equal_without_reexecuting_closed_oracle(case):
    d=json.loads((OLD/(case+'.json')).read_text(encoding='utf-8'));r=run_counting_sparse_trace(d['input']);t=r['steps'];assert len(t)==len(d['native'])
    for i,c in enumerate(d['native']):
        event=t[i]['instruction_event'];event['conteo']=expand_small(event['conteo']);assert event=={k:v for k,v in c.items() if k!='case'}
@pytest.mark.parametrize('values',[[5,4,3,2,1],[0,5],[0,16,8,0,16,4,12,8],[2]*80,list(range(79,-1,-1)),[-2147483643,-2147483648],[2147483647,2147483642],[0,1000]])
def test_compact_core_outside_four_controls_scopes_zeroing_and_memory(values):
    d=run_counting_sparse_trace(values);t=d['steps'];assert d['final_state']['items']==sorted(values) and d['metrics']['comparisons']==2*(len(values)-1) and d['metrics']['moves']==3*len(values)
    tokens=set();pending=0
    for i in range(len(t)):
        f=t[i];tokens.add(f['line_token']);event=f['instruction_event'];ctx=f['counting_context'];snapshot=event['conteo']
        if f['line_token']=='count_init':assert snapshot['default']==0 and snapshot['nonzero']==[]
        if f['line_token']=='array_write':pending+=1;assert ctx['pending_decrement']==1 and t[i+1]['line_token']=='count_write'
        if f['line_token']=='count_free':assert snapshot is None and not any(p['name']=='conteo' for p in f['instruction_pointers'])
        if snapshot is not None:assert sum(v for _,v in snapshot['nonzero'])==ctx['filled']-ctx['consumed']
        if i:
            previous={(v['scope'],v['name']):v for v in t[i-1]['instruction_variables']}
            for v in f['instruction_variables']:
                old=previous.get((v['scope'],v['name']));assert v['previous']==(old['value'] if old else None)
                assert v['changed']==(old is None or (old['value'],old['initialized'])!=(v['value'],v['initialized']))
    assert {'minmax_entry','min_compare','max_compare','count_init','rebuild_test','bucket_test','array_write','count_write','count_free','sort_return'}<=tokens and pending==len(values)

def test_cap_million_native_C_samples_and_logical_event_count():
    t=run_counting_sparse_trace([999999,0])['steps'];r=json.loads((E/'native-cap-scalar/report.json').read_text());assert r['actual_C_bodies'] and r['size_t64'] and r['logical_events']==len(t)==3000051 and r['allocations']==r['frees']==1 and r['live']==0
    for line in (E/'native-cap-scalar/stdout.jsonl').read_text().splitlines():
        c=json.loads(line);e=t[c['index']]['instruction_event']
        for key,value in c.items():
            if key not in ['index','selected_counts']:assert e[key]==value
        selected=[dict(e['conteo']['nonzero']).get(k,0) for k in [0,1,499999,999999]] if e['conteo'] is not None else None;assert selected==c['selected_counts']

def test_bounded_pages_windows_and_read_only_backward_forward():
    t=run_counting_sparse_trace([999999,0])['steps'];before=json.dumps(t.records,sort_keys=True)
    assert len(t.records)<100
    for index in [0,1,len(t)//2,len(t)-3,len(t)-1]:
        first=t.page(index,min(64,len(t)-index));second=t.page(index,min(64,len(t)-index));assert first==second
        first[0]['array_snapshot'][0]=99;assert t[index]['array_snapshot'][0]!=99
        snapshot=t[index]['instruction_event']['conteo']
        if snapshot is not None:assert len(sparse_window(snapshot,499999,64))==64
    assert json.dumps(t.records,sort_keys=True)==before
    with pytest.raises(ValueError):t.page(0,129)
    with pytest.raises(ValueError):sparse_window(t[40]['instruction_event']['conteo'],0,129)
    with pytest.raises(ValueError):expand_small(t[40]['instruction_event']['conteo'])
