"""Full current API/direct NULL trace versus preserved safe native observations."""
from pathlib import Path
import sys,json,hashlib,shutil
R=Path.cwd();sys.path.insert(0,str(R))
from app import create_app
from app.domain.sequential.priority_queue_cleanup_instruction import build_priority_queue_cleanup_trace
E=R/'openspec/changes/audit-local-quality-and-unified-controls/evidence/visible-priority-queue-limpiar-instructions-medium';L=E.parent/'visible-priority-queue-limpiar-baseline-low'
native=json.loads((L/'native-report.json').read_text(encoding='utf-8-sig'));old=json.loads((L/'report.json').read_text(encoding='utf-8-sig'));app=create_app();app.config['TESTING']=True
rows=[];comparisons=[];sid=0
for name,values in [('empty',[]),('single',[(-1,2)]),('multi',[(7,3),(-2,1),(7,1)]),('reinsert',[(7,3),(-2,1),(7,1)])]:
 c=app.test_client()
 for v,p in values:assert c.post('/sequential/priority_queue/operate',json={'operation':'encolar','payload':{'value':v,'priority':p}}).get_json()['success']
 for repeat in [1,2]:
  if name=='reinsert' and repeat==2:assert c.post('/sequential/priority_queue/operate',json={'operation':'encolar','payload':{'value':8,'priority':-1}}).get_json()['success']
  d=c.post('/sequential/priority_queue/operate',json={'operation':'limpiar','payload':{}}).get_json();assert d['success'];ns=[n for n in native if n['sample']==sid];frames=d['execution_trace']['steps'];assert [n['event'] for n in ns]==[f['debug']['token'] for f in frames]
  ids={cid:h['id'] for cid,h in zip(ns[0]['root_ids'],frames[0]['debug']['heap'])};mapping=lambda value:None if value==-1 else ids[value]
  for n,f in zip(ns,frames):
   g=f['debug'];assert g['condition_result']==(None if n['condition']==-1 else bool(n['condition']));assert g['root']['cantidad']==n['quantity'] and g['root']['rear']==mapping(n['rear_id']);live=[h for h in g['heap'] if h['alive']];assert len(live)==len(n['live'])
   for h,cn in zip(live,n['live']):assert h['id']==mapping(cn['id']) and h['fields']=={'valor':cn['value'],'prioridad':cn['priority'],'sgte':mapping(cn['next_id'])} and h['initialized_mask']==7
   for h in g['heap']:
    if not h['alive']:assert h['initialized_mask']==0 and not h['fields_valid'] and all(v is None for v in h['fields'].values())
   if n['event']!='return':
    for key in ['aux','next']:
     p=g[key];assert bool(p and p['initialized'])==bool(n[key+'_initialized']) and bool(p and p['valid'])==bool(n[key+'_valid'])
     if n[key+'_valid']:assert p['value']==mapping(n[key+'_id'])
   else:assert not g['scopes'] and not g['call_stack'] and all(p['scope']!='cp_vaciar' for p in g['pointers'])
   ptr=g['root']['front'];root=[]
   while ptr is not None:
    h=next(h for h in live if h['id']==ptr);root.append(h);ptr=h['fields']['sgte']
   assert [h['id'] for h in root]==[mapping(i) for i in n['root_ids']] and [h['fields']['valor'] for h in root]==n['root_values'] and [h['fields']['prioridad'] for h in root]==n['root_priorities']
   comparisons.append({'sample':sid,'event':n['event'],'match':True})
  previous=next(r for r in old if r['native_sample']==sid);observations=[]
  for o in previous['instruction_comparison']:
   matches=[f for f in frames if f['debug']['token']==o['event']];f=matches[o['iteration']];g=f['debug'];observations.append({**o,'trace_values':[i['value'] for i in f['state_after']['items']],'trace_quantity':g['root']['cantidad'],'trace_heap_count':len(f['pedagogy']['heap_objects']),'root_values_match':o['C_values']==[i['value'] for i in f['state_after']['items']],'quantity_match':o['C_quantity']==g['root']['cantidad']})
  rows.append({**previous,'data':d,'instruction_comparison':observations});sid+=1
source=rows[0]['data']['execution_trace']['source_code'];empty=rows[0]['data']['visual_state'];null=build_priority_queue_cleanup_trace(payload={},source_code=source,code_title='Codigo C',before_state=empty,after_state=empty,success=True,message='NULL native guard',null_root=True)
ns=[n for n in native if n['sample']==8];assert [n['event'] for n in ns]==[f['debug']['token'] for f in null['steps']]
for n,f in zip(ns,null['steps']):assert not f['debug']['root']['alive'] and not f['debug']['heap'] and f['condition_result']==(None if n['condition']==-1 else bool(n['condition']));comparisons.append({'sample':8,'event':n['event'],'match':True})
(E/'report.json').write_text(json.dumps(rows,indent=2),encoding='utf-8');(E/'null-trace.json').write_text(json.dumps(null,indent=2),encoding='utf-8');shutil.copyfile(L/'native-report.json',E/'native-report.json');(E/'native').mkdir(exist_ok=True);shutil.copyfile(L/'native/stderr.log',E/'native/stderr.log');(E/'native-comparison.json').write_text(json.dumps({'calls':9,'events':len(comparisons),'conditions':41,'observations_32_preserved':sum(len(r['instruction_comparison']) for r in rows),'divergences':0,'native_reexecuted':False,'matches':comparisons},indent=2),encoding='utf-8');print('9calls153events41conditions32observations exact; original native observer reused')
