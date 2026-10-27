"""Actual Kruskal UI history, downloaded program output and allocation ownership."""
from pathlib import Path
import json,subprocess,sys
import pytest
pytestmark=pytest.mark.e2e
@pytest.fixture(scope='module')
def actual_browser_callers(tmp_path_factory):
 out=tmp_path_factory.mktemp('kruskal-browser');helper=Path(__file__).with_name('_audit_graph_kruskal_caller_verified.py');root=Path(__file__).resolve().parents[1]
 run=subprocess.run([sys.executable,'-u',str(helper),str(out)],cwd=root,capture_output=True,text=True,encoding='utf-8',timeout=120);(out/'runner.log').write_text(run.stdout+run.stderr,encoding='utf-8');assert run.returncode==0,run.stdout+run.stderr
 report=json.loads((out/'report.json').read_text(encoding='utf-8'));return {x['case']:x for x in report['rows']},out
@pytest.mark.parametrize('case',['single_vertex','connected','disconnected'])
def test_actual_kruskal_history_download_and_ownership(case,actual_browser_callers):
 rows,out=actual_browser_callers;r=rows[case]
 assert r['actual_calls']==r['before_reload_calls']==r['after_reload_calls']==2
 assert r['extra_reload_POSTs']==r['replay_extra_POSTs']==0 and r['page_errors']==[]
 assert r['original_strict_c17_pass'] and r['original_returncode']==0
 assert not r['caller_output_is_precomputed']
 assert r['ownership']['allocations']==r['ownership']['frees'] and r['ownership']['live']==0
 lines=[l for l in r['original_stdout'].splitlines() if l.startswith('Kruskal:')]
 expected={'single_vertex':'Kruskal: | costo=0','connected':'Kruskal: 2-3(2) 3-1(1) | costo=3','disconnected':'Kruskal: 4-3(3) 2-1(2) | costo=5'}[case]
 assert lines==[expected]*2
 # UI/backend tie choice is still held; compare generated main to real native
 # output, not to a precomputed or invented backend path.
 from test_graph_bfs_documentation import run_doxygen
 run_doxygen(out/case,[out/case/'main.c'])
