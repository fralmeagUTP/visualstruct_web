"""Four retained hidden methods compared with immutable actual native observers."""
import hashlib,json,os
from pathlib import Path
import pytest
from app import create_app
from app.config import Config
ROOT=Path(__file__).resolve().parents[1]
BASE=ROOT/'openspec/changes/archive/2026-10-13-audit-local-quality-and-unified-controls/evidence/visible-four-hidden-residual-and-final-disposition-low'
from scripts.published_test_inputs import audit_input_path
BASELINE=json.loads((audit_input_path(BASE/'four-hidden-native-HTTP-baseline.json')).read_text(encoding='utf-8'))
@pytest.fixture(scope='module')
def app(tmp_path_factory):
 out=Path(os.environ.get('HIDDEN_TERMINAL_OUT',str(tmp_path_factory.mktemp('terminal'))));out.mkdir(parents=True,exist_ok=True)
 class QA(Config):
  SECRET_KEY='private-terminal-regression'
  SESSION_CACHE_DIR=str(out/'private-cache')
  SESSION_CACHE_THRESHOLD=0
 a=create_app(QA);a.config.update(TESTING=True);assert Path(a.config['SESSION_CACHELIB']._path).resolve().is_relative_to(out.resolve())
 c=a.test_client()
 for kind in ['source','header']:
  r=c.get('/help/source/linked_list/'+kind);assert r.status_code==200 and hashlib.sha256(r.data).hexdigest()==BASELINE['sources_HTTP_SHA'][kind]
 return a,out
@pytest.mark.parametrize('case',BASELINE['cases'],ids=[x['operation']+'-'+str(len(x['seed'])) for x in BASELINE['cases']])
def test_four_hidden_native_equivalence(app,case):
 a,out=app;c=a.test_client()
 for value in case['seed']:assert c.post('/sequential/linked_list/operate',json={'operation':'insertar_final','payload':{'value':value}}).get_json()['success']
 d=c.post('/sequential/linked_list/operate',json={'operation':case['operation'],'payload':{}});assert d.status_code==case['HTTP_status'];d=d.get_json();trace=d['execution_trace'];assert trace['hidden_terminal_instruction_model']
 assert d['result']==case['result'] if d.get('success') else not case['seed']
 assert d['visual_state']==case['state']
 if not d['success']:
  assert trace['steps']==[] and trace['execution_started'] is False;return
 steps=[s for s in trace['steps'] if s['event_type']!='scope_exit'];native=case['native_events'];assert len(steps)==len(native)
 for s,n in zip(steps,native):
  assert s['line_text'].strip()==n['line']
  assert s['condition_result']==(None if n['condition']==-1 else bool(n['condition']))
  memory=s['pedagogy']['memory_state'];ptr=lambda x:0 if x=='NULL' else int(x[1:])
  assert ptr(memory['head'])==n['head'] and memory['free_count']==n['free_count']
  assert [{'id':ptr(x['id']),'value':x['value'],'next':ptr(x['next'])} for x in memory['heap_nodes']]==n['heap']
  assert not s['pedagogy']['heap_transition']['dangling_references']
  if s['condition_result'] is not None:
   assert 'NULL->' not in s['pedagogy']['condition']['substituted']
  if 'free(' in s['line_text']:
   assert len(s['pedagogy']['heap_transition']['freed'])==1
   p=next(p for p in s['pedagogy']['pointers'] if p['name'] in {'eliminado','actual'})
   assert p['dangling'] and not p['valid']
 last=trace['steps'][-1];assert last['state_after']==d['visual_state'] and last['pedagogy']['scopes'][0]['state']=='ended' and last['pedagogy']['call_stack']==[]
 if case['operation']=='mostrar':
  outputs=[s['console'][-1] for s in steps if 'printf(' in s['line_text']]
  assert outputs==[f' {i+1}) {value}' for i,value in enumerate(case['seed'])]
 else:assert last['debug']['output']==case['native_return_output_remaining_conditions_frees'][1]
 (out/(case['operation']+'-'+str(len(case['seed']))+'.json')).write_text(json.dumps(d,indent=2),encoding='utf-8')
