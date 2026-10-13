"""Independent native event oracle plus actual private Graph query player."""
from pathlib import Path
import json,os,subprocess,sys
import pytest
ROOT=Path(__file__).resolve().parents[1]
CHANGE=ROOT/'openspec/changes/archive/2026-10-13-audit-local-quality-and-unified-controls/evidence'
def execute(script,out,vars):
    env=os.environ.copy();env.update(vars)
    run=subprocess.run([sys.executable,'-B',str(script)],cwd=ROOT,env=env,capture_output=True,text=True,timeout=120)
    (out/'execution.log').write_text(run.stdout+run.stderr,encoding='utf-8')
    assert run.returncode==0,run.stdout+run.stderr
    return json.loads((out/'report.json').read_text(encoding='utf-8'))
def test_independent_native_neighbors_events_locals_fields_and_ownership(tmp_path):
    report=execute(CHANGE/'visible-canonical-focal-repair-medium/neighbor_native_instructions.py',tmp_path,{'NEIGHBOR_NATIVE_OUT':str(tmp_path)})
    assert report['compile_exit']==report['native_exit']==0
    assert len(report['cases'])==6
    for case in report['cases']:
        assert case['all_callee_events_locals_partial_fields_match']
        a,f,live,bad=map(int,case['ownership'].split()[1:])
        assert a==f and live==bad==0

@pytest.mark.parametrize('vertex',[3,1],ids=['empty-successors','owned-results'])
def test_actual_query_player_no_false_highlight_frames_reverse_and_reload(tmp_path,vertex):
    report=execute(Path(__file__).with_name('_graph_query_browser_contract_observer.py'),tmp_path,{'FOCAL_QUERY_BROWSER_OUT':str(tmp_path),'FOCAL_EXPECT_FIXED':'1','FOCAL_QUERY_VERTEX':str(vertex)})
    assert report['fixed_verified'] and not report['incorrect_body_highlights']
    assert report['replay_POSTs']==report['reload_POSTs']==0
    assert report['DOM_HTTP_main_identical'] and not report['query_recorded_in_main']
    assert not report['errors']
