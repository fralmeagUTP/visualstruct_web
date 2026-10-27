"""Native C parity undirected; directed C/API contrast follows existing authorized policy."""
from pathlib import Path
import json,subprocess,sys
import pytest
@pytest.fixture(scope='module')
def native_baseline(tmp_path_factory,request):
 selected=sorted({item.callspec.params['name'] for item in request.session.items if item.path==Path(__file__) and hasattr(item,'callspec') and 'name' in item.callspec.params})
 assert selected
 out=tmp_path_factory.mktemp('prim-native');root=Path(__file__).resolve().parents[1]
 p=subprocess.run([sys.executable,'-u',str(Path(__file__).with_name('_audit_graph_prim_baseline.py')),str(out),*selected],cwd=root,capture_output=True,text=True,encoding='utf-8',timeout=300)
 (out/'runner.log').write_text(p.stdout+p.stderr,encoding='utf-8');assert p.returncode==0,p.stdout+p.stderr
 d=json.loads((out/'report.json').read_text(encoding='utf-8'));assert d['cases']==len(selected) and d['native_strict_c17'];assert {row['name'] for row in d['rows']}==set(selected);assert len(d['downloads_sha256'])==4;return {r['name']:r for r in d['rows']}
@pytest.mark.parametrize('name',['single_vertex', 'connected', 'disconnected', 'isolated_start', 'equal_cost', 'zero_weight', 'negative_edge', 'mixed_negative', 'self_loop', 'negative_ids', 'missing_start', 'empty', 'intmax_minus_one', 'intmax_sentinel', 'safe_large_total', 'intmin_ignored', 'directed_native_difference'])
def test_prim_native_parity(name,native_baseline):
 r=native_baseline[name]
 assert r['differences']==[],r
 if name=='directed_native_difference':
  assert r['input']['directed'] is True and r['native']['status']==6
  assert r['native']['null'] and r['native']['arcs']==[]
  assert r['backend']['c_status']==6 and not r['backend']['success']
 if r['backend']['success']:assert r['history_saved']==r['history_reload']==1
 else:assert r['failure_history_recorded'] and r['source_contract']=='graph-book/v1'
