"""Actual downloaded C parity; pending numeric decisions remain failing regressions."""
from pathlib import Path
import json,subprocess,sys
import pytest
@pytest.fixture(scope='function')
def observed_baseline(tmp_path_factory,request):
 out=tmp_path_factory.mktemp('bellman-native');root=Path(__file__).resolve().parents[1]
 run=subprocess.run([sys.executable,'-u',str(Path(__file__).with_name('_audit_graph_bellman_ford_baseline.py')),str(out),request.node.callspec.params['name']],cwd=root,capture_output=True,text=True,encoding='utf-8',timeout=60)
 (out/'runner.log').write_text(run.stdout+run.stderr,encoding='utf-8');assert run.returncode==0,run.stdout+run.stderr
 r=json.loads((out/'report.json').read_text(encoding='utf-8'));assert r['cases']==1 and r['native_strict_c17'];assert len(r['rows'])==1 and r['rows'][0]['name']==request.node.callspec.params['name'];assert len(r['downloads_sha256'])==4;return {x['name']:x for x in r['rows']}
NAMES=['same_vertex', 'negative_edge', 'cheaper_negative_alternative', 'reachable_negative_cycle', 'reachable_cycle_with_direct_target', 'unreachable_negative_cycle', 'unreachable_destination', 'zero_cycle', 'equal_cost_order', 'negative_ids', 'missing_start', 'missing_end', 'intmax_minus_one', 'intmax_infinity', 'upper_bound_guard', 'intmin_edge', 'lower_bound_guard', 'undirected_negative_cycle', 'negative_cycle_bound_missed', 'empty_graph']
PENDING=['equal_cost_order', 'intmax_infinity', 'upper_bound_guard', 'lower_bound_guard', 'negative_cycle_bound_missed']
@pytest.mark.parametrize('name',NAMES)
def test_bellman_endpoint_matches_actual_c(name,observed_baseline):
 row=observed_baseline[name];assert row['differences']==[],json.dumps(row,ensure_ascii=False,indent=2)
 if not row['backend']['success']:assert row['failure_history_unchanged']
@pytest.mark.parametrize('name',['reachable_negative_cycle','reachable_cycle_with_direct_target','undirected_negative_cycle'])
def test_negative_cycle_matches_error_spec(name,observed_baseline):
 assert observed_baseline[name]['cycle_result_matches_error_spec']
