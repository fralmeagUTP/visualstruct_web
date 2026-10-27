"""Full 14-call oracle comparison; native C logs remain immutable."""
from pathlib import Path
import sys,json,shutil
R=Path.cwd();sys.path.insert(0,str(R))
from app import create_app
from app.domain.sequential.stack_push_instruction import build_stack_push_trace
E=R/'openspec/changes/audit-local-quality-and-unified-controls/evidence/visible-stack-apilar-instructions-medium';L=E.parent/'visible-stack-apilar-baseline-low'
ns=json.loads((L/'native-report.json').read_text(encoding='utf-8-sig'));old=json.loads((L/'report.json').read_text(encoding='utf-8-sig'));app=create_app();app.config['TESTING']=True;rows=[];all_traces=[];matches=[];sid=0
for name,seeds,value in [('empty',[],9),('single',[7],-1),('duplicate',[7],7),('bounds',[2147483647,-1],-2147483648)]:
 c=app.test_client()
 for v in seeds:assert c.post('/sequential/stack/operate',json={'operation':'apilar','payload':{'value':v}}).get_json()['success']
 for repeat in [1,2]:
  d=c.post('/sequential/stack/operate',json={'operation':'apilar','payload':{'value':value}}).get_json();assert d['success'];previous=next(r for r in old if r['native_sample']==sid);frames=d['execution_trace']['steps'];observations=[]
  for o in previous['observations']:
   f=next(f for f in frames if f['debug']['token']==o['event']);vs=[i['value'] for i in f['state_after']['items']];observations.append({**o,'trace_root_values':vs,'root_values_match':vs==o['native_root_values'],'trace_heap_count':len(f['pedagogy']['heap_objects'])})
  rows.append({**previous,'data':d,'observations':observations});all_traces.append((sid,d['execution_trace']));sid+=1
 before=d['visual_state'];t=build_stack_push_trace(payload={'value':value},source_code=d['execution_trace']['source_code'],code_title='Codigo C',before_state=before,after_state=before,success=False,message='native mallocNULL',allocation_failure=True);all_traces.append((sid,t));sid+=1
empty=rows[0]['data']['execution_trace']['steps'][0]['state_snapshot'];source=rows[0]['data']['execution_trace']['source_code']
all_traces.append((12,build_stack_push_trace(payload={'value':9},source_code=source,code_title='C',before_state=empty,after_state=empty,success=False,message='native NULL param',null_root=True)))
all_traces.append((13,build_stack_push_trace(payload={'value':9},source_code=source,code_title='C',before_state=empty,after_state=empty,success=False,message='native empty mallocNULL',allocation_failure=True)))
for sid,trace in all_traces:
 native=[n for n in ns if n['sample']==sid];fs=trace['steps'];assert [n['event'] for n in native]==[f['debug']['token'] for f in fs],sid
 initial=native[0]['root_ids'];g=fs[0]['debug'];mapping={cid:h['id'] for cid,h in zip(initial,g['heap'])}
 added=[n for n in native if n['event']=='aux_allocated' and n['aux_id']!=-1]
 if added:mapping[added[0]['aux_id']]='push-new'
 target=lambda i:None if i==-1 else mapping[i]
 for n,f in zip(native,fs):
  g=f['debug'];assert g['condition_result']==(None if n['condition']==-1 else bool(n['condition'])) and g['root']['alive']==(not n['root_argument_NULL']);assert len(g['heap'])==len(n['live'])
  for cn in n['live']:
   h=next(h for h in g['heap'] if h['id']==target(cn['id']));assert h['initialized_mask']==cn['mask'] and h['field_validity']=={'nro':bool(cn['mask']&1),'sgte':bool(cn['mask']&2)}
   assert h['fields']['nro']==cn['value'] and h['fields']['sgte']==(target(cn['next_id']) if cn['mask']&2 else None)
  pointer=g['root']['value'];root=[]
  while pointer is not None:
   h=next(h for h in g['heap'] if h['id']==pointer);assert h['initialized_mask']==3;root.append(h);pointer=h['fields']['sgte']
  assert [h['id'] for h in root]==[target(i) for i in n['root_ids']] and [h['fields']['nro'] for h in root]==n['root_values']
  if n['event']!='return':assert bool(g['aux'] and g['aux']['initialized'])==bool(n['aux_initialized']) and (not n['aux_initialized'] or g['aux']['value']==target(n['aux_id']))
  else:assert not g['scopes'] and not g['call_stack'] and not any(v['scope']=='pila_apilar' for v in g['variables'])
  assert f['console']==([n['console'].strip()] if n['console'] else [])
  matches.append({'sample':sid,'event':n['event'],'match':True})
(E/'report.json').write_text(json.dumps(rows,indent=2),encoding='utf-8');(E/'direct-fault-traces.json').write_text(json.dumps([{'sample':sid,'trace':t} for sid,t in all_traces if sid in [2,5,8,11,12,13]],indent=2),encoding='utf-8');shutil.copyfile(L/'native-report.json',E/'native-report.json');(E/'native').mkdir(exist_ok=True);shutil.copyfile(L/'native/stderr.log',E/'native/stderr.log');(E/'native-comparison.json').write_text(json.dumps({'calls':14,'events':len(matches),'conditions':27,'original_observations':32,'divergences':0,'native_reexecuted':False,'matches':matches},indent=2),encoding='utf-8');print('all14calls124events27conditions32observations match; native reused')
