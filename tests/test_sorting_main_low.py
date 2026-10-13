"""Regression of actual sorting main downloads, not instruction fidelity signoff."""
from pathlib import Path
import json,subprocess,sys
import pytest
from app.adapters.sorting_adapter import SortingAdapter
from app.domain.sorting import SORTING_ALGORITHMS
from app.services.sorting_structure_service import SortingStructureService as S
ROOT=Path(__file__).resolve().parents[1]

def execute(op,p,h):
 return S.execute_operation(structure_id='sorting_array',operation_name=op,payload=p,history=h)

@pytest.fixture
def actual_callers(tmp_path_factory,request):
 selected=request.node.callspec.params['method'] if hasattr(request.node,'callspec') else 'empty'
 out=tmp_path_factory.mktemp('sorting-main-actual');r=subprocess.run([sys.executable,'-B',str(Path(__file__).with_name('_audit_sorting_main_browser_low.py')),str(out),selected],cwd=ROOT,capture_output=True,text=True,encoding='utf-8',timeout=120);(out/'runner.log').write_text(r.stdout+r.stderr,encoding='utf-8');assert r.returncode==0,r.stdout+r.stderr;return json.loads((out/'report.json').read_text(encoding='utf-8'))

@pytest.mark.parametrize('method',[a['id'] for a in SORTING_ALGORITHMS])
def test_actual_ui_main_download_c17_history_ownership(method,actual_callers):
 r=next(row for row in actual_callers['rows'] if row['algorithm']==method);n=r['native']
 assert n['actual_UI_download'] and n['strict_C17'] and n['doxygen_warnings']==0 and n['live']==0 and n['allocations']==n['frees']
 assert r['same_main_after_reload'] and r['reload_replay_extra_POSTs']==0 and r['duplicate_pending_extra_run_POSTs']==0 and r['page_errors']==[]
 assert r['new_execution_buttons']==0 and r['control_button_elements']==10 and r['primary_execution_control_elements']==7 and r['counting_navigation_control_elements']==3 and r['five_stages']
 assert r['runs']==n['successful_native_runs']
 assert {d['kind'] for d in r['downloads']}=={'main','source','header'}
 if method in {'mergesort','counting_sort','binsort','radixsort'}:
  assert n['first_allocation_failure']['returncode']==1 and n['first_allocation_failure']['live']==0 and n['first_allocation_failure']['no_success_array_after_failure']

def test_empty_actual_download_and_reset_do_not_invent_callers(actual_callers):
 e=actual_callers['empty'];assert e['successful_native_runs']==0 and e['arrays']==[[]] and e['allocations']==0 and e['live']==0;assert actual_callers['empty_reset_verified']

def test_saved_random_values_do_not_regenerate_or_sort_on_get(client,monkeypatch):
 d=client.post('/api/ordenamiento/random-array',json={'size':4,'min_value':-5,'max_value':5,'seed':42}).get_json();assert d['history'][-1]['materialized_values']==[5,-4,-5,-1]
 d=client.post('/api/ordenamiento/run',json={'algorithm_id':'radixsort','mode':'fast'}).get_json();expected=d['main_c'];history=d['history']
 monkeypatch.setattr(SortingAdapter,'run',lambda *a,**k:pytest.fail('historical sort dispatched'))
 monkeypatch.setattr(SortingAdapter,'generate_random_array',lambda *a,**k:pytest.fail('historical random regenerated'))
 for route in ['/api/ordenamiento/state','/sorting/visualizador','/help/source/sorting_array/main']:
  r=client.get(route);assert r.status_code==200
  if route.endswith('/main'):assert r.data.decode()==expected and 'no-store' in r.headers['Cache-Control']
 state=client.get('/api/ordenamiento/state').get_json();assert state['history']==history and state['main_c']==expected and state['visual_state']['items']==[-5,-4,-1,5]

def test_legacy_seed_materializes_and_missing_seed_is_not_invented():
 payload={'size':4,'min_value':-5,'max_value':5,'seed':42};legacy=[{'operation':'generate_random_array','payload':payload}];view=S.get_view_model('sorting_array',legacy);assert view['history'][0]['materialized_values']==[5,-4,-5,-1];assert 'arreglo[0] = 5;' in view['main_c'] and 'rand(' not in view['main_c']
 missing=[{'operation':'generate_random_array','payload':{k:v for k,v in payload.items() if k!='seed'}}];assert S.get_view_model('sorting_array',missing)['history']==[]

@pytest.mark.parametrize('values',[[True,1],[2],[6,1],[2147483648,1],[1.5,1]])
def test_invalid_materialized_history_is_excluded(values):
 history=[{'operation':'generate_random_array','payload':{'size':2,'min_value':0,'max_value':5,'seed':42},'materialized_values':values}];v=S.get_view_model('sorting_array',history);assert v['history']==[] and v['visual_state']['items']==[] and 'printf("Run ' not in v['main_c']

def test_main_route_allowlist_and_session_isolation(client,app):
 d=client.post('/api/ordenamiento/create-array',json={'values':'3,1,2'}).get_json();expected=d['main_c']
 assert client.get('/help/source/sorting_array/unknown').status_code==404
 stack=client.get('/help/source/stack/main');assert stack.status_code==200
 assert stack.headers['Content-Disposition']=='attachment; filename=main.c'
 assert client.get('/help/source/sorting_array/main').data.decode()==expected
 other=app.test_client();assert other.get('/help/source/sorting_array/main').data.decode()!=expected
 assert client.get('/help/source/sorting_array/main').headers['Content-Disposition']=='attachment; filename=main.c'

def test_selection_failure_and_reset_preserve_accepted_history(client):
 client.post('/api/ordenamiento/create-array',json={'values':[3,1,2]});d=client.post('/api/ordenamiento/algorithm',json={'algorithm_id':'mergesort'}).get_json();before=d['main_c'];assert 'Metodo preparado: ordenar_mergesort' in before and 'int estado_' not in before
 for route,payload in [('create-array',{'values':[2147483648]}),('run',{'algorithm_id':'mergesort','mode':'bad'})]:
  r=client.post('/api/ordenamiento/'+route,json=payload);assert r.status_code==400 and r.get_json()['main_c']==before
 reset=client.post('/api/ordenamiento/reset',json={}).get_json();assert reset['history']==[] and 'printf("Run ' not in reset['main_c'];assert client.get('/help/source/sorting_array/main').data.decode()==reset['main_c']


def test_legacy_random_session_migrates_once_on_download(client,monkeypatch):
 from app.services.session_service import SESSION_KEY
 legacy=[{'operation':'generate_random_array','payload':{'size':4,'min_value':-5,'max_value':5,'seed':42}}]
 with client.session_transaction() as session:session[SESSION_KEY]={'sorting::sorting_array':legacy}
 first=client.get('/help/source/sorting_array/main');assert first.status_code==200
 with client.session_transaction() as session:
  saved=session[SESSION_KEY]['sorting::sorting_array']['history'];assert saved[0]['materialized_values']==[5,-4,-5,-1]
 monkeypatch.setattr(SortingAdapter,'generate_random_array',lambda *a,**k:pytest.fail('legacy random regenerated twice'))
 assert client.get('/help/source/sorting_array/main').data==first.data
 assert client.get('/api/ordenamiento/state').get_json()['history']==saved
 assert client.get('/sorting/visualizador').status_code==200
