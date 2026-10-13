"""Downloaded Rojo-Negro clear lifetimes: baseline only, not instruction UI closure."""
import os,json,subprocess,sys
from pathlib import Path
import pytest
@pytest.fixture(scope='module')
def rbt_clear_baseline(tmp_path_factory):
 out=tmp_path_factory.mktemp('rbt-clear-native');root=Path(__file__).resolve().parents[1];env={**os.environ,'AUDIT_REPO':str(root),'AUDIT_OUTPUT_DIR':str(out),'PYTHONPATH':str(root),'PYTHONIOENCODING':'utf-8'}
 run=subprocess.run([sys.executable,str(Path(__file__).with_name('_audit_rbt_clear_native_observer.py'))],cwd=root,env=env,capture_output=True,text=True,encoding='utf-8',timeout=90);(out/'run.log').write_text(run.stdout+run.stderr,encoding='utf-8');assert run.returncode==0,run.stdout+run.stderr
 return json.loads((out/'review.json').read_text())
@pytest.mark.parametrize('case',range(5))
def test_rbt_clear_native_cached_lifetime_postorder_and_repetition(rbt_clear_baseline,case):
 report=rbt_clear_baseline;assert report['native_events']==215 and report['native_frees']==15 and report['native_fixture_invariants_verified'];meta=report['cases'][case];events=[e for e in report['events'] if e['case']==case];repeat=[e for e in report['events'] if e['case']==case+5]
 assert meta['endpoint_empty'] and meta['repeat_empty'] and len(repeat)==5
 initial=events[0]['records'];live={n['id'] for n in initial};freed=[]
 for e in events:
  now={n['id'] for n in e['records'] if n['live']}
  if e['phase']=='free':
   target=e['result'];assert target in live and target not in now;freed.append(target);assert live-now=={target};record=next(x for x in initial if x['id']==target);assert all(x==0 or x in freed[:-1] for x in [record['left_identity'],record['right_identity']])
  else:assert now==live
  live=now
  for f in e['frames']:assert f['usable']==int(f['identity']==0 or f['identity'] in live)
 assert len(freed)==len(meta['seed']) and not live
 assert next(e for e in events if e['phase']=='caller_resume')['root_identity']==(1 if meta['seed'] else 0)
 assert next(e for e in events if e['phase']=='caller_assign')['root_identity']==0
 assert all(e['root_identity']==0 and not any(x['live'] for x in e['records']) for e in repeat) and not any(e['phase']=='free' for e in repeat)
 assert all(n['color_before_free'] in [ord('r'),ord('n')] for n in initial)
 def tree(identity):
  if not identity:return None
  n=next(x for x in initial if x['id']==identity);return {'value':n['value_before_free'],'color':'RED' if n['color_before_free']==ord('r') else 'BLACK','left':tree(n['left_identity']),'right':tree(n['right_identity'])}
 assert meta['trace']['steps'][0]['state_snapshot']['root']==tree(1 if meta['seed'] else 0)
