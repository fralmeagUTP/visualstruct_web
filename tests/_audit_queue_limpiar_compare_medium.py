"""Match the current limpiar trace to preserved original-C callbacks, no C rerun."""
from pathlib import Path
import json,sys
R=Path.cwd();sys.path.insert(0,str(R))
from app import create_app
from app.domain.sequential.queue_cleanup_instruction import build_queue_cleanup_trace
E=R/'openspec/changes/archive/2026-10-13-audit-local-quality-and-unified-controls/evidence/visible-queue-limpiar-instructions-medium';L=E.parent/'visible-queue-limpiar-baseline-low'

from scripts.published_test_inputs import audit_input_path
def compare(trace:dict,sample:int) -> dict:
    native=[n for n in json.loads((audit_input_path(L/'native-report.json')).read_text(encoding='utf-8')) if n['sample']==sample]
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
        if not n['root_argument_NULL']:
            assert d['root']['rear_valid']==bool(n['rear_valid'])
            assert d['root']['rear']==(identities[n['rear_id']] if n['rear_valid'] and n['rear_id']!=-1 else None)
            assert d['root']['initialized_mask']==(3 if n['rear_valid'] else 1)
        assert n['condition']==(-1 if d['condition_result'] is None else int(d['condition_result']))
        if n['event']!='return':
            aux=d['aux'];assert bool(n['aux_initialized'])==(bool(aux and aux['initialized'])) and bool(n['aux_valid'])==bool(aux and aux['valid'])
            if aux and aux['valid']:assert aux['value']==identities[n['aux_id']]
        for h in heap.values():
            assert h['initialized_mask']==(3 if h['alive'] else 0)
            if not h['alive']:assert not h['fields_valid'] and all(value is None for value in h['fields'].values()) and h['historical_fields']
        if n['event']=='root_assigned':
            assert d['aux']['value'] not in rootids and live[d['aux']['value']]['status']=='detached'
        if n['event']=='return':assert d['scopes']==[] and d['call_stack']==[] and not any(v['scope']=='cola_vaciar' for v in d['variables'])
    return {'sample':sample,'frames':len(frames),'conditions':sum(n['condition']!=-1 for n in native),'all_snapshots_match':True}

def collect() -> tuple[list[dict],list[dict]]:
    app=create_app();app.config['TESTING']=True;rows=[];comparisons=[];sample=0
    for name,values in [('empty',[]),('single',[-1]),('multi',[7,-2,7]),('reinsert',[7,-2,7])]:
        c=app.test_client()
        for value in values:c.post('/sequential/queue/operate',json={'operation':'encolar','payload':{'value':value}})
        for repeat in [1,2]:
            if name=='reinsert' and repeat==2:c.post('/sequential/queue/operate',json={'operation':'encolar','payload':{'value':8}})
            d=c.post('/sequential/queue/operate',json={'operation':'limpiar','payload':{}}).get_json();trace=d['execution_trace'];comparisons.append(compare(trace,sample));original=next(r for r in json.loads((audit_input_path(L/'report.json')).read_text(encoding='utf-8')) if r['case']==name and r['repeat']==repeat);rows.append({'case':name,'repeat':repeat,'sample':sample,'data':d,'native_events':original['native_events'],'C_API_final_match':not d['visual_state']['items'],'instruction_comparison':original['instruction_comparison']});sample+=1

    t=rows[0]['data']['execution_trace'];raw=build_queue_cleanup_trace(payload={},source_code=t['source_code'],code_title=t['code_title'],before_state=t['final_state'],after_state=t['final_state'],success=True,message='',null_root=True);comparisons.append(compare(raw,8));rows.append({'case':'NULL-root-native','sample':8,'trace':raw})
    return rows,comparisons

if __name__=='__main__':
    rows,comparisons=collect();(E/'report.json').write_text(json.dumps(rows,indent=2),encoding='utf-8');(E/'native-comparison.json').write_text(json.dumps(comparisons,indent=2),encoding='utf-8');print(json.dumps({'samples':9,'events':sum(c['frames'] for c in comparisons),'conditions':sum(c['conditions'] for c in comparisons),'C_artifact_reused':True,'original_C_callback_log_preserved':True}))
