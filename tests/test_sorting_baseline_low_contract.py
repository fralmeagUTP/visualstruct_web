"""Fresh actual-download native/API endpoint parity for11methods, not instruction signoff."""
from pathlib import Path
import subprocess,sys,json
import pytest
from app.domain.sorting import SORTING_ALGORITHMS
@pytest.fixture(scope='module')
def baseline(tmp_path_factory):
 out=tmp_path_factory.mktemp('sorting-native');root=Path(__file__).resolve().parents[1]
 r=subprocess.run([sys.executable,'-u',str(Path(__file__).with_name('_audit_sorting_baseline_low.py')),str(out)],cwd=root,capture_output=True,text=True,encoding='utf-8',timeout=120)
 (out/'runner.log').write_text(r.stdout+r.stderr,encoding='utf-8');assert r.returncode==0,r.stdout+r.stderr
 d=json.loads((out/'report.json').read_text(encoding='utf-8'));assert d['cases']==110 and d['strict_c17'];return d
@pytest.mark.parametrize('algorithm',[a['id'] for a in SORTING_ALGORITHMS])
def test_recorded_endpoint_cases_match_c_and_survive_get(algorithm,baseline):
 rows=[r for r in baseline['rows'] if r['algorithm']==algorithm];assert len(rows)==10
 for r in rows:
  assert r['differences']==[],r
  for mode in r['api_modes']:
   if mode['success']:assert mode['array']==mode['after_get_array'] and mode['history_runs']>0
