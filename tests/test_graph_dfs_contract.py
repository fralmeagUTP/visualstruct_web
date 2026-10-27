"""Finite DFS contract parity; not instruction-level or all-path proof."""
import json,os,subprocess,sys
from pathlib import Path
from app.services.graph_structure_service import GraphStructureService as S
from app.adapters.graph_adapter import GraphAdapter

def test_dfs_downloaded_native_contract(tmp_path):
    env=dict(os.environ,AUDIT_OUTPUT_DIR=str(tmp_path/'native'),PYTHONIOENCODING='utf-8')
    run=subprocess.run([sys.executable,'-u',str(Path(__file__).with_name('_audit_graph_dfs_contract_observer.py'))],capture_output=True,text=True,env=env,timeout=90)
    assert run.returncode==0,run.stdout+run.stderr
    report=json.loads((tmp_path/'native/report.json').read_text())
    assert report['native_runs']==11 and report['final_orders_match']
    assert report['marks_mismatches']==report['output_marks_mismatches']==report['successful_history_missing']==0

def test_dfs_history_rebuild_no_query_redispatch(monkeypatch):
    h=[{'operation':'insert_vertex','payload':{'vertex':-1}}]
    for _ in range(2):
        data=S.execute_operation('graph','run_dfs',{'start':-1},h);assert data['success'];h=data['history']
    failed=S.execute_operation('graph','run_dfs',{'start':999},h)
    assert not failed['success'] and failed['history']==h
    calls=[];original=GraphAdapter.execute
    def spy(self,op,payload):calls.append(op);return original(self,op,payload)
    monkeypatch.setattr(GraphAdapter,'execute',spy)
    for _ in range(2):assert S.get_view_model('graph',h)['history']==h
    assert calls==['insert_vertex','insert_vertex']
    assert [e['operation'] for e in h]==['insert_vertex','run_dfs','run_dfs']
