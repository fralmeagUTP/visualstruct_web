"""Native C parity undirected; directed C/API contrast follows existing authorized policy."""
from pathlib import Path
import json,subprocess,sys
import pytest
@pytest.fixture(scope='function')
def native_baseline(tmp_path_factory,request):
 out=tmp_path_factory.mktemp('prim-native');root=Path(__file__).resolve().parents[1]
 p=subprocess.run([sys.executable,'-u',str(Path(__file__).with_name('_audit_graph_prim_baseline.py')),str(out),request.node.callspec.params['name']],cwd=root,capture_output=True,text=True,encoding='utf-8',timeout=60)
 (out/'runner.log').write_text(p.stdout+p.stderr,encoding='utf-8');assert p.returncode==0,p.stdout+p.stderr
 d=json.loads((out/'report.json').read_text(encoding='utf-8'));assert d['cases']==1 and d['native_strict_c17'];assert len(d['rows'])==1 and d['rows'][0]['name']==request.node.callspec.params['name'];assert len(d['downloads_sha256'])==4;return {r['name']:r for r in d['rows']}
@pytest.mark.parametrize('name',['single_vertex', 'connected', 'disconnected', 'isolated_start', 'equal_cost', 'zero_weight', 'negative_edge', 'mixed_negative', 'self_loop', 'negative_ids', 'missing_start', 'empty', 'intmax_minus_one', 'intmax_sentinel', 'safe_large_total', 'intmin_ignored', 'directed_native_difference'])
def test_prim_native_parity(name,native_baseline):
 r=native_baseline[name]
 if name=='directed_native_difference':
  # C selects arcs as connections; the approved API exposes MST only undirected.
  assert r['input']['directed'] is True
  assert r['differences']==['directed_app_rejection_native_selection'],r
  assert r['native']['arcs']==[[1,2,3]] and r['native']['cost']==3
  assert r['native']['null'] is False
  assert r['backend']['success'] is False and r['backend']['result'] is None
  assert 'no dirigidos' in r['backend']['message']
  assert r['history_saved']==r['history_reload']==0 and r['failure_history_unchanged'] is True
 else:assert r['differences']==[],r
 if r['backend']['success']:assert r['history_saved']==r['history_reload']==1
 else:assert r['failure_history_unchanged']
