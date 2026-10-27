"""Insertion baseline contracts plus deliberate failing instruction-conformance regressions."""
import json,hashlib
from pathlib import Path
import pytest
from app import create_app
from _audit_insercion_baseline import audit,CASES
from test_graph_bfs_documentation import run_doxygen
ROOT=Path(__file__).resolve().parents[1]
EVIDENCE=ROOT/'openspec/changes/archive/2026-10-13-audit-local-quality-and-unified-controls/evidence/visible-sorting-insercion-baseline-low'

@pytest.fixture(scope='module')
def observed(tmp_path_factory):
 out=tmp_path_factory.mktemp('insercion-baseline');return out,audit(out)

from scripts.published_test_inputs import audit_input_path
@pytest.mark.parametrize('case',list(CASES))
def test_final_metrics_and_every_existing_mutation_match_native(case,observed):
 out,report=observed;data=json.loads((audit_input_path(out/(case+'.json'))).read_text(encoding='utf-8'));row=next(r for r in report['rows'] if r['case']==case)
 assert row['final_and_metrics_match'] and row['projected_array_differences']==0
 assert data['response']['visual_state']['items']==data['fast_response']['visual_state']['items']==sorted(CASES[case])
 for projection in data['projection']:
  native=data['native'][projection['native_index']];step=data['response']['execution_trace']['steps'][projection['runtime_index']]
  assert native['array']==step['state_after']['items']
  if projection['token']=='while_compare':assert native['condition']==step['pedagogy']['condition']['result']


def test_native_shortcircuit_and_empty_api_rejection(observed):
 out,report=observed;assert report['native_guard_cases']==2 and report['native_guard_observations']==19 and report['api_empty_rejected']
 native=[json.loads(line) for line in (audit_input_path(out/'native.jsonl')).read_text().splitlines()]
 assert not any(row['event']['token']=='valid_n' for row in native if row['case']==7)
 for index,row in enumerate(native):
  if row['event']['token']=='while_left' and not row['condition']:
   assert row['event']['j']==0 and native[index+1]['event']['token']=='while_test' and not native[index+1]['condition']


def test_c_h_downloads_doxygen_unchanged(observed):
 out,report=observed;run_doxygen(out,[out/'tad_ordenamiento.c',out/'tad_ordenamiento.h'])
 for extension in ['c','h']:
  assert (audit_input_path(out/('tad_ordenamiento.'+extension))).read_bytes().replace(b'\r\n',b'\n')==(audit_input_path(ROOT/'docs/tads_C'/('tad_ordenamiento.'+extension))).read_bytes().replace(b'\r\n',b'\n')


def test_repeated_insertion_history_and_get_preserve_original_caller(monkeypatch):
 from app.adapters.sorting_adapter import SortingAdapter
 client=create_app().test_client();client.post('/api/ordenamiento/create-array',json={'values':[2,1]})
 first=client.post('/api/ordenamiento/run',json={'algorithm_id':'insercion','mode':'fast'}).get_json();second=client.post('/api/ordenamiento/run',json={'algorithm_id':'insercion','mode':'fast'}).get_json()
 assert first['success'] and second['success'];assert sum(e['operation']=='run' for e in second['history'])==2
 assert first['history'][-1]['array_effect']['input']==[2,1] and second['history'][-1]['array_effect']['input']==[1,2]
 monkeypatch.setattr(SortingAdapter,'run',lambda *a,**k:pytest.fail('GET must not execute insertion again'))
 state=client.get('/api/ordenamiento/state').get_json();assert state['history']==second['history'] and state['main_c']==second['main_c'] and state['main_c'].count('ordenar_insercion(arreglo, n);')==2
 assert client.get('/help/source/sorting_array/main').data.decode('utf-8')==state['main_c']

@pytest.mark.parametrize('case',list(CASES))
def test_recorded_actual_browser_and_downloaded_caller_baseline(case):
 report=json.loads((audit_input_path(EVIDENCE/'browser/report.json')).read_text(encoding='utf-8'));row=next(r for r in report['rows'] if r['case']==case)
 assert row['coarse_restorations']==2*row['coarse_steps'] and row['replay_extra_POSTs']==0 and row['page_errors']==[] and row['main_preserved_after_reload'] and row['five_stages']
 assert row['caller']['strict_C17'] and row['caller']['doxygen_warnings']==0 and row['caller']['allocations']==row['caller']['frees']==row['caller']['live']==0
 assert row['caller']['arrays']==[CASES[case],sorted(CASES[case])]
 for filename,checksum in row['caller']['source_hashes'].items():assert hashlib.sha256((audit_input_path(EVIDENCE/'browser'/case/filename)).read_bytes()).hexdigest()==checksum
 assert report['empty_UI_rejected'] and report['empty_caller']['successful_native_runs']==0

@pytest.mark.parametrize('case',list(CASES))
def test_every_insertion_instruction_is_represented_with_actual_locals(case,observed):
 """Must fail until the new trace preserves actual C clauses, locals and shortcircuit."""
 out,_=observed;data=json.loads((audit_input_path(out/(case+'.json'))).read_text(encoding='utf-8'));steps=data['response']['execution_trace']['steps'];native=data['native']
 assert len(steps)==len(native),f'{case}: C has {len(native)} observed transitions, UI trace has {len(steps)}'
 for step,c in zip(steps,native):
  assert step['debug'].get('instruction_event')==c['event']
  assert step['state_after']['items']==c['array']
  assert (step['pedagogy']['condition']['result'] if step['pedagogy']['condition'] else None)==c['condition']
