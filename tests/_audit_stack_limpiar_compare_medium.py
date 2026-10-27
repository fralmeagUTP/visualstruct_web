"""Match the current limpiar trace to preserved original-C callbacks, no C rerun."""
from pathlib import Path
import json,sys
R=Path.cwd();sys.path.insert(0,str(R))
from app import create_app
from app.domain.sequential.stack_cleanup_instruction import build_stack_cleanup_trace
E=R/'openspec/changes/archive/2026-10-13-audit-local-quality-and-unified-controls/evidence/visible-stack-limpiar-instructions-medium';L=E.parent/'visible-stack-limpiar-baseline-low'

def compare(trace:dict,sample:int) -> dict:
    native=[n for n in json.loads((L/'native-report.json').read_text(encoding='utf-8')) if n['sample']==sample]
    frames=trace['steps'];assert [n['event'] for n in native]==[f['debug']['token'] for f in frames]
    identities=dict(zip(native[0]['root_ids'],[h['id'] for h in frames[0]['debug']['heap']]))
    for n,f in zip(native,frames):
        d=f['debug'];heap={h['id']:h for h in d['heap']};live={h['id']:h for h in d['heap'] if h['alive']};rootids=[identities[i] for i in n['root_ids']]
        assert d['root']['alive']==(not bool(n['root_argument_NULL']))
        assert d['root']['value']==(rootids[0] if rootids else None)
        assert [x['value'] for x in f['state_after']['items']]==n['root_values']
        assert set(live)=={identities[h['id']] for h in n['live']}
        assert all(live[identities[h['id']]]['fields']['nro']==h['value'] for h in n['live'])
        assert d['frees']==n['frees']
        assert n['condition']==(-1 if d['condition_result'] is None else int(d['condition_result']))
        if n['event']!='return':
            aux=d['aux'];assert bool(n['aux_initialized'])==(bool(aux and aux['initialized'])) and bool(n['aux_valid'])==bool(aux and aux['valid'])
            if aux and aux['valid']:assert aux['value']==identities[n['aux_id']]
        for h in heap.values():
            assert h['initialized_mask']==(3 if h['alive'] else 0)
            if not h['alive']:assert not h['fields_valid'] and all(value is None for value in h['fields'].values()) and h['historical_fields']
        if n['event']=='root_assigned':
            assert d['aux']['value'] not in rootids and live[d['aux']['value']]['status']=='detached'
        if n['event']=='return':assert d['scopes']==[] and d['call_stack']==[] and d['variables']==[]
    return {'sample':sample,'frames':len(frames),'conditions':sum(n['condition']!=-1 for n in native),'all_snapshots_match':True}

def collect() -> tuple[list[dict],list[dict]]:
    app=create_app();app.config['TESTING']=True;rows=[];comparisons=[];sample=0
    for name,values in [('empty',[]),('single',[-1]),('multi',[7,-2,7]),('reinsert',[7,-2,7])]:
        c=app.test_client()
        for value in values:c.post('/sequential/stack/operate',json={'operation':'apilar','payload':{'value':value}})
        for repeat in [1,2]:
            if name=='reinsert' and repeat==2:c.post('/sequential/stack/operate',json={'operation':'apilar','payload':{'value':8}})
            d=c.post('/sequential/stack/operate',json={'operation':'limpiar','payload':{}}).get_json();trace=d['execution_trace'];comparisons.append(compare(trace,sample));rows.append({'case':name,'repeat':repeat,'sample':sample,'data':d});sample+=1
        r=c.get('/help/source/stack/main');assert r.status_code==200;D=E/'callers';D.mkdir(exist_ok=True);(D/(name+'.c')).write_bytes(r.data)
    t=rows[0]['data']['execution_trace'];raw=build_stack_cleanup_trace(payload={},source_code=t['source_code'],code_title=t['code_title'],before_state=t['final_state'],after_state=t['final_state'],success=True,message='',null_root=True);comparisons.append(compare(raw,8));rows.append({'case':'NULL-root-native','sample':8,'trace':raw})
    return rows,comparisons

if __name__=='__main__':
    rows,comparisons=collect();(E/'report.json').write_text(json.dumps(rows,indent=2),encoding='utf-8');(E/'native-comparison.json').write_text(json.dumps(comparisons,indent=2),encoding='utf-8');print(json.dumps({'samples':9,'events':sum(c['frames'] for c in comparisons),'conditions':sum(c['conditions'] for c in comparisons),'C_artifact_reused':True,'original_C_callback_log_preserved':True}))
