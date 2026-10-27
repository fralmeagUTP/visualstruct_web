"""Independent actual-download native Dijkstra parity and successful-query history regressions."""
from pathlib import Path
import json,subprocess,sys
import pytest
NAMES=['same_vertex','direct','cheaper_alternative','equal_priority_order','equal_priority_reverse_vertices','unreachable','zero_cycle','undirected','negative_ids','missing_start','missing_end','negative_weight_rejected','negative_disconnected_rejected','intmax_minus_one','intmax_infinity','overflow_guard']
@pytest.fixture(scope='module')
def observed_baseline(tmp_path_factory,request):
 selected=sorted({item.callspec.params['name'] for item in request.session.items if item.path==Path(__file__) and hasattr(item,'callspec') and 'name' in item.callspec.params})
 assert selected
 out=tmp_path_factory.mktemp('dijkstra-native');helper=Path(__file__).with_name('_audit_graph_dijkstra_baseline.py');root=Path(__file__).resolve().parents[1]
 run=subprocess.run([sys.executable,'-u',str(helper),str(out),*selected],cwd=root,capture_output=True,text=True,encoding='utf-8',timeout=300)
 (out/'runner.log').write_text(run.stdout+run.stderr,encoding='utf-8');assert run.returncode==0,run.stdout+run.stderr
 r=json.loads((out/'report.json').read_text(encoding='utf-8'));assert r['cases']==len(selected) and r['native_strict_c17'];assert {row['name'] for row in r['rows']}==set(selected);assert len(r['downloads_sha256'])==4;return {x['name']:x for x in r['rows']}
@pytest.mark.parametrize('name',NAMES)
def test_dijkstra_endpoint_matches_actual_c(name,observed_baseline):
 row=observed_baseline[name];assert row['differences']==[],json.dumps(row,ensure_ascii=False,indent=2)
 if not row['backend']['success']:assert row['failure_history_recorded'] and row['source_contract']=='graph-book/v1'
@pytest.mark.parametrize('name',['same_vertex','direct'])
def test_successful_dijkstra_retained_without_reexecution(name,observed_baseline):
 row=observed_baseline[name];assert row['backend']['success']
 assert row['successful_query_saved']==1 and row['successful_query_after_reload']==1,row
