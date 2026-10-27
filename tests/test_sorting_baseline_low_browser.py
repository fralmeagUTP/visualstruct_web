"""Actual UI repetitions, reload and saved sorted state; no actual main claimed."""
from pathlib import Path
import subprocess,sys,json
import pytest
@pytest.fixture(scope='module')
def browser_report(tmp_path_factory):
 out=tmp_path_factory.mktemp('sorting-browser');root=Path(__file__).resolve().parents[1]
 p=subprocess.run([sys.executable,'-u',str(Path(__file__).with_name('_audit_sorting_browser_low.py')),str(out)],cwd=root,capture_output=True,text=True,encoding='utf-8',timeout=120)
 (out/'runner.log').write_text(p.stdout+p.stderr,encoding='utf-8');assert p.returncode==0,p.stdout+p.stderr
 return json.loads((out/'report.json').read_text(encoding='utf-8'))
@pytest.mark.parametrize('algorithm',['burbuja','mergesort','radixsort'])
def test_actual_saved_runs(algorithm,browser_report):
 r=next(r for r in browser_report['rows'] if r['algorithm']==algorithm)
 assert r['actual_runs']==r['saved_runs']==r['before_history_run_entries']==r['after_history_run_entries']==2
 assert r['reload_extra_POSTs']==0 and r['page_errors']==[]
 assert r['state_array_after_reload']==[1,2,3] and r['first_trace_input']==[3,1,2] and r['second_trace_input']==[1,2,3]
 assert r['main_elements']==1 # main integration authorized later; C17 proof is in main-low tests
