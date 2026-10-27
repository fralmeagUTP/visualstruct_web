"""Actual downloaded C parity; pending numeric decisions remain failing regressions."""
from pathlib import Path
import json,subprocess,sys
import pytest
@pytest.fixture(scope='module')
def observed_baseline(tmp_path_factory,request):
 selected=sorted({item.callspec.params['name'] for item in request.session.items if item.path==Path(__file__) and hasattr(item,'callspec') and 'name' in item.callspec.params})
 assert selected
 out=tmp_path_factory.mktemp('bellman-native');root=Path(__file__).resolve().parents[1]
 run=subprocess.run([sys.executable,'-u',str(Path(__file__).with_name('_audit_graph_bellman_ford_baseline.py')),str(out),*selected],cwd=root,capture_output=True,text=True,encoding='utf-8',timeout=300)
 (out/'runner.log').write_text(run.stdout+run.stderr,encoding='utf-8');assert run.returncode==0,run.stdout+run.stderr
 r=json.loads((out/'report.json').read_text(encoding='utf-8'));assert r['cases']==len(selected) and r['native_strict_c17'];assert {row['name'] for row in r['rows']}==set(selected);assert len(r['downloads_sha256'])==4;return {x['name']:x for x in r['rows']}
NAMES=['same_vertex', 'negative_edge', 'cheaper_negative_alternative', 'reachable_negative_cycle', 'reachable_cycle_with_direct_target', 'unreachable_negative_cycle', 'unreachable_destination', 'zero_cycle', 'equal_cost_order', 'negative_ids', 'missing_start', 'missing_end', 'intmax_minus_one', 'intmax_infinity', 'upper_bound_guard', 'intmin_edge', 'lower_bound_guard', 'undirected_negative_cycle', 'negative_cycle_bound_missed', 'empty_graph']
PENDING=['equal_cost_order', 'intmax_infinity', 'upper_bound_guard', 'lower_bound_guard', 'negative_cycle_bound_missed']
@pytest.mark.parametrize('name',NAMES)
def test_bellman_endpoint_matches_actual_c(name,observed_baseline):
 row=observed_baseline[name];assert row['differences']==[],json.dumps(row,ensure_ascii=False,indent=2)
 if not row['backend']['success']:assert row['failure_history_recorded'] and row['source_contract']=='graph-book/v1'
@pytest.mark.parametrize('name',['reachable_negative_cycle','reachable_cycle_with_direct_target','undirected_negative_cycle'])
def test_negative_cycle_matches_error_spec(name,observed_baseline):
 assert observed_baseline[name]['cycle_result_matches_error_spec']
