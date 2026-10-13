"""Fresh independent AVL native observer versus insertion model; actual C/H remain unchanged."""
from pathlib import Path
import sys,json,subprocess,re
from copy import deepcopy
import pytest
from app.adapters.avl_adapter import AVLAdapter
from app.services.c_code_service import CCodeService
from app.domain.hierarchical.avl_insert_instruction import build_avl_insert_trace
OBSERVER=Path(__file__).with_name('_audit_avl_insert_native_observer.py')
@pytest.fixture(scope='module')
def avl_insert_native(tmp_path_factory):
 out=tmp_path_factory.mktemp('avl-insert-native');script=OBSERVER.read_text(encoding='utf-8').replace("r=Path(r'D:\\MisProyectos\\Web_VisualEstruct')","r=Path("+repr(str(Path(__file__).resolve().parents[1]))+")").replace("o=w/'avl-insert-baseline-low'","o=Path("+repr(str(out))+')');(out/'observer.py').write_text(script,encoding='utf-8');run=subprocess.run([sys.executable,'-u',str(out/'observer.py')],capture_output=True,text=True,encoding='utf-8',timeout=90);(out/'observer.log').write_text(run.stdout+run.stderr,encoding='utf-8');assert run.returncode==0,run.stdout+run.stderr;d=json.loads((out/'review.json').read_text(encoding='utf-8'));assert len(d['events'])==714;d['source_lines']=(out/'tad_avl.c').read_text(encoding='utf-8-sig').splitlines();return d

def fixture(case,review):
 a=AVLAdapter();c=review['cases'][case]
 for v in c['seed']:a.execute('insertar',{'value':v})
 before=a.to_visual_state();after=deepcopy(before)
 if c.get('api_success'):a.execute('insertar',{'value':c['value']});after=a.to_visual_state()
 source=CCodeService.get_structure_data('avl')['operations']['insertar'];trace=build_avl_insert_trace({'source_code':source,'payload':{'value':c['value']},'success':True},before,after,fail_malloc=c.get('fail_malloc',False),null_ref=c.get('null_ref',False));return trace,before,after

def mapping(events):
 first=events[0];nodes={n['id']:n for n in first['nodes']};ids={0:'NULL',-2:'sin inicializar'}
 def walk(i):
  if i==0:return
  ids[i]='N'+str(len(ids)-1);walk(nodes[i]['left']);walk(nodes[i]['right'])
 walk(first['root'])
 for e in events:
  for n in e['nodes']:
   if n['id'] not in ids:ids[n['id']]='N'+str(len(ids)-1)
 return ids

def native_pairs(trace,events,rawlines):
 steps=trace['steps'];selected=[s for s in steps if s['pedagogy']['instruction_event']['phase'] not in ['caller_enter']];selected=selected[1:] # Outer caller call is not in TAD observer.
 assert len(selected)==len(events)-1 # Initial native snapshot is separate.
 return list(zip(selected,events[1:]))

def check(step,event,ids,base,rawlines):
 phase=step['pedagogy']['instruction_event']['phase'];assert phase==event['phase'];p=step['pedagogy'];state=step['state_snapshot'] if phase=='return' else p['memory_state']
 if event['line']:assert step['line_text'].strip()==rawlines[event['line']-1].strip()
 if event['line']:
  fn=event['frames'][-1]['function'];rawstart=next(i for i,l in enumerate(rawlines) if l.strip().startswith('void '+fn+'('));shownstart=next(i for i,l in enumerate(step['_source_lines']) if l.strip().startswith('void '+fn+'('));assert step['line_index']-shownstart==event['line']-1-rawstart
 assert state['head']==ids[event['root']];expected=[]
 for n in event['nodes']:
  m=n['mask'];expected.append({'id':ids[n['id']],'value':n['value'] if m&1 else 'sin inicializar','balance_factor':n['fe'] if m&2 else 'sin inicializar','left':ids[n['left']] if m&4 else 'sin inicializar','right':ids[n['right']] if m&8 else 'sin inicializar','parent':ids[n['parent']] if m&16 else 'sin inicializar'})
 assert sorted([{k:v for k,v in n.items() if k!='status'} for n in state['heap_nodes']],key=lambda n:n['id'])==sorted(expected,key=lambda n:n['id'])
 assert len(state['tree_frames'])==len(event['frames'])
 for f,n in zip(state['tree_frames'],event['frames']):
  assert f['function']==n['function'];assert f['id']=='F'+str(n['id']-base);assert f['locals']=={k:ids[v] if isinstance(v,int) else v for k,v in n['locals'].items()}
  assert f['parameters']==({'raiz':'&raiz' if n['ref'] else 'NULL','x':n['x']} if n['function']=='avl_insertar' else {'r':'&raiz' if n['ref'] else 'NULL','nodo':ids[n['node']]})
 if phase=='condition':assert step['condition_result']==bool(event['result'])
 assert not p['memory']['freed_objects'] and p['memory_state']['console_stdout']==''
 if phase=='return':assert p['instruction_event']['return']=='void' and len(p['memory_state']['tree_frames'])==len(event['frames'])-1
@pytest.mark.parametrize('case',range(15))
def test_avl_insert_each_native_instruction(avl_insert_native,case):
 d=avl_insert_native;trace,before,after=fixture(case,d);events=[e for e in d['events'] if e['case']==case];ids=mapping(events);base=events[1]['frames'][0]['id']-1;rawlines=d['source_lines']
 for step,e in native_pairs(trace,events,rawlines):step['_source_lines']=trace['source_code'].splitlines();check(step,e,ids,base,rawlines)
 assert trace['steps'][-1]['state_after']==after
 if case in [9,12,13,14]:assert trace['steps'][-1]['pedagogy']['memory_state']['root']==before['root']
