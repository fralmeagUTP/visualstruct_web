"""Current typed private Cima and live rejection baseline; reuse exact native inputs safely."""
from pathlib import Path
import sys,json,hashlib,shutil,tracemalloc,time
R=Path.cwd();sys.path.insert(0,str(R));sys.stdout.reconfigure(encoding='utf-8')
from app import create_app
from app.config import Config
from app.adapters.stack_adapter import StackAdapter
from app.services.structure_service import StructureService
from app.services.execution_trace_service import ExecutionTraceService
from app.domain.sequential import tad_pila as raw
E=R/'openspec/changes/audit-local-quality-and-unified-controls/evidence/visible-stack-cima-instructions-medium';L=E.parent/'visible-stack-cima-baseline-low';N=E/'native-reused';N.mkdir(exist_ok=True)
for filename in ['tad_pila.c','tad_pila.h','events.jsonl','driver.c','instrumented.c','hooks.h']:
    shutil.copyfile(L/'native'/filename,N/filename)
assert (N/'tad_pila.c').read_bytes()==(R/'docs/tads_C/tad_pila.c').read_bytes();assert (N/'tad_pila.h').read_bytes()==(R/'docs/tads_C/tad_pila.h').read_bytes()
class Q(Config):
    TESTING=True
    SESSION_CACHE_DIR=str(E/'private-API-sessions')
app=create_app(Q);native=[json.loads(x) for x in (N/'events.jsonl').read_text().splitlines()];samples=json.loads((L/'report.json').read_text(encoding='utf-8'));rows=[];resources=[];API=[]
for kind,ext in [('source','c'),('header','h')]:
    r=app.test_client().get('/help/source/stack/'+kind);assert r.status_code==200 and r.data==(N/('tad_pila.'+ext)).read_bytes()
for sample,d in enumerate(samples):
    values=d['items_top_to_bottom'];a=StackAdapter();node=None
    for v in reversed(values):a.execute('apilar',{'value':v});node=raw.NodoPila(v,node)
    visual=a.to_visual_state();before_root=a._structure._tope_ref[0];before_size=a._structure._tamano;before=[];ptr=before_root
    while ptr:before.append((id(ptr),ptr.nro,id(ptr.sgte)));ptr=ptr.sgte
    for repeat in [0,1]:
        expected=native[sample*6+repeat*3:sample*6+repeat*3+3]
        assert raw.pila_cima(node)==expected[-1]['result']
        tracemalloc.start();start=time.perf_counter();trace=ExecutionTraceService.build_trace(structure_id='stack',operation_name='cima',payload={},didactic_data=StructureService._didactic_content('stack'),before_state=visual,after_state=visual,success=bool(values),message='Consulta privada al adapter; fuera de API/UI.',mutates=False,console_events=[]);size=len(json.dumps(trace,ensure_ascii=False).encode('utf-8'));elapsed=time.perf_counter()-start;peak=tracemalloc.get_traced_memory()[1];tracemalloc.stop();resources.append({'case':d['case'],'repeat':repeat+1,'scope':'private typed trace build including C extraction and JSON serialization, no HTTP/session','python_peak_bytes':peak,'JSON_bytes':size,'instrumented_seconds':elapsed})
        assert len(trace['steps'])==3
        for c,step in zip(expected,trace['steps']):
            m=step['pedagogy'];memory=m['top_memory'];heap=m['heap_objects'];assert step['event_type']==c['phase'];assert [x['value'] for x in step['state_after']['items']]==c['items'];assert memory['root']['value']==('N1' if values else None);assert memory['allocations']==memory['frees']==0;assert step['console']==[] and m['heap_transition']['before']==m['heap_transition']['after'];assert len(heap)==len(values)
            for i,h in enumerate(heap):assert h['fields']=={'nro':c['items'][i],'sgte':f'N{i+2}' if i+1<len(values) else None} and h['initialized_mask']==3 and h['type']=='struct NodoPila' and h['alive']
            if c['phase']=='conditional':assert m['condition']['result']==bool(c['condition'])
            if c['phase']=='return':assert memory['return_value']==c['result'] and memory['return_written'];assert m['call_stack']==[] and all(x['scope']!='pila_cima' for x in m['variables']);assert m['scopes'][0]['state']=='ended';assert memory['parameter'] is None
            else:
                p=next(x for x in m['pointers'] if x['name']=='p');assert p['type']=='ptrPila' and p['target']==memory['root']['value'] and p['initialized'] and p['scope_state']=='active';assert memory['return_value'] is None and not memory['return_written']
            assert not memory['caller_storage']['initialized'] and not memory['caller_storage']['written'] and memory['caller_storage']['value'] is None
        ptr=a._structure._tope_ref[0];after=[]
        while ptr:after.append((id(ptr),ptr.nro,id(ptr.sgte)));ptr=ptr.sgte
        assert after==before and before_root is a._structure._tope_ref[0] and before_size==a._structure._tamano
        rows.append({'case':d['case'],'repeat':repeat+1,'native_sample':sample*2+repeat,'trace':trace,'events_aligned':3,'conditions_aligned':1,'divergences':0,'raw_result':raw.pila_cima(node),'caller_assignment_outside_function_pending':True})
    client=app.test_client()
    for v in reversed(values):assert client.post('/sequential/stack/operate',json={'operation':'apilar','payload':{'value':v}}).get_json()['success']
    from unittest.mock import patch
    original=StackAdapter.execute;queries=[]
    def observe(self,op,payload):
        if op=='cima':queries.append(op)
        return original(self,op,payload)
    with patch.object(StackAdapter,'execute',observe):
        rejected=[];tracemalloc.start();start=time.perf_counter()
        for _ in range(2):
            r=client.post('/sequential/stack/operate',json={'operation':'cima','payload':{}});data=r.get_json();assert r.status_code==400 and not data['success'] and data['visual_state']==visual;assert data['execution_trace']['steps']==[] and data['execution_trace']['execution_started'] is False;assert not any(x['operation']=='cima' for x in data['history']);rejected.append({'HTTP':400,'data':data})
        elapsed=time.perf_counter()-start;peak=tracemalloc.get_traced_memory()[1];tracemalloc.stop();resources.append({'case':d['case'],'scope':'two rejected HTTP POSTs including session mutation replay/serialization','python_peak_bytes':peak,'JSON_bytes':len(r.data),'instrumented_seconds':elapsed})
        assert client.get('/sequential/stack').status_code==200 and client.get('/sequential/stack').status_code==200 and queries==[]
    API.append({'case':d['case'],'rejected':rejected,'query_dispatch_POST_GET':0,'query_journal':0,'structural_readonly':True})
(E/'private-native-comparison.json').write_text(json.dumps({'native_reused_calls':16,'events_aligned':48,'conditions_aligned':16,'divergences':0,'C_H_current_exact':True,'native_execution_rerun':False,'rows':rows,'limits':'Private trace C-function boundaries only. Return int separate from pending caller assignment; no outputparams/localt/constqualification invented. Static initialized native setup no malloc/free. Not public UI execution.'},ensure_ascii=False,indent=2)+'\n',encoding='utf-8');(E/'API-report.json').write_text(json.dumps(API,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');summary={}
for scope in ['private typed trace build including C extraction and JSON serialization, no HTTP/session','two rejected HTTP POSTs including session mutation replay/serialization']:
    ss=[x for x in resources if x['scope']==scope];summary[scope]={'samples':len(ss),'max_python_peak_bytes':max(x['python_peak_bytes'] for x in ss),'max_JSON_bytes':max(x['JSON_bytes'] for x in ss),'max_instrumented_seconds':max(x['instrumented_seconds'] for x in ss)}
(E/'resources.json').write_text(json.dumps({'samples':resources,'by_scope':summary,'baseline_rejected_API':{'max_python_peak_bytes':514445,'max_JSON_bytes':7747,'max_instrumented_seconds':0.025802600001043174},'limits':'Finite fixtures only; private trace and rejected API measured separately. No successful API queries/RSS/browser/unboundedhistory/SLA/leak/OOM/sanitizer proof.'},indent=2)+'\n',encoding='utf-8');print('Current16private queries48events16conditions aligned0divs;8APIcases16reject validation0steps/querydispatchPOSTGET0; finite scopes separate')
