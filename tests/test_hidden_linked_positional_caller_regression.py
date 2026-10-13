"""Actual hidden positional HTTP/DOM C callers, including boundaries and ownership."""
from pathlib import Path
import json,os,subprocess,sys
import pytest
ROOT=Path(__file__).resolve().parents[1]
@pytest.fixture(scope='module')
def positional_reports(tmp_path_factory):
    out=tmp_path_factory.mktemp('hidden-positional-callers')
    env=os.environ.copy();env['FOCAL_ALIAS_OUT']=str(out)
    script=ROOT/'openspec/changes/archive/2026-10-13-audit-local-quality-and-unified-controls/evidence/visible-canonical-focal-verification-low/hidden_alias_caller_baseline.py'
    run=subprocess.run([sys.executable,'-B',str(script)],cwd=ROOT,env=env,capture_output=True,text=True,timeout=120)
    (out/'execution.log').write_text(run.stdout+run.stderr,encoding='utf-8')
    assert run.returncode==0,run.stdout+run.stderr
    return {r['case_id']:r for r in json.loads((out/'report.json').read_text(encoding='utf-8'))['cases']}
@pytest.mark.parametrize('case_id',['legacy-insert-before-position2','legacy-relative-insert-after-position2','legacy-delete-position2','legacy-before-1','legacy-before-3','legacy-before-4','legacy-before-5','legacy-after-1','legacy-after-3','legacy-relative-before2','legacy-delete-1','legacy-delete-3'])
def test_hidden_caller_matches_API_and_owns_allocations(positional_reports,case_id):
    row=positional_reports[case_id]
    assert row['API_success'] and row['hidden_UI_NA'] and row['DOM_main_stable_reload']
    assert row['compile_exit']==0,row
    assert row['native_exit']==0 and row['matches'],row
    alloc,freed,live,bad=map(int,row['ownership'].split()[1:])
    assert alloc==freed and live==bad==0
