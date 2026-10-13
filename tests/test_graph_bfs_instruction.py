"""BFS outer instructions compared against independently observed downloaded C."""
import copy,json
from pathlib import Path
import pytest
from app.services.graph_structure_service import GraphStructureService as S
from app.services.c_code_service import CCodeService
from app.domain.graph.bfs_instruction import build_bfs_trace
from _audit_graph_bfs_native_observer import observe,CASES

@pytest.fixture(scope='module')
def bfs_native(tmp_path_factory):
    out=tmp_path_factory.mktemp('bfs-parent')/'observed'
    report=observe(out);report['_source_lines']=(out/'tad_grafo.c').read_text(encoding='utf-8').splitlines()
    return report

def case_trace(c,marks=None):
    history=[{'operation':'create_graph','payload':{'directed':True}},*[{'operation':'insert_vertex','payload':{'vertex':v}} for v in c['vertices']],*[{'operation':'insert_edge','payload':{'origin':u,'target':v,'weight':1}} for u,v in c['edges']]]
    before=S.get_view_model('graph',history)['visual_state'];data=S.execute_operation('graph','run_bfs',{'start':c['start']},history)
    if data['success'] and marks is None:return data['execution_trace']
    if marks:
        for n in before['nodes']:n['marked']=marks.get(int(n['id']),0)
    trace=copy.deepcopy(data['execution_trace']);trace['source_code']=CCodeService.get_structure_data('graph')['operations']['run_bfs'];return build_bfs_trace(trace,before,data['visual_state'])

@pytest.mark.parametrize('case',range(10))
def test_bfs_native_outer_instruction_projection(bfs_native,case):
    report=bfs_native;c=CASES[case];runs=2 if c.get('repeat') else 1;lastmarks=None
    for run in range(runs):
        trace=case_trace(c,lastmarks);native=[e for e in report['events'] if e['case']==case and e['run']==run]
        projected=[s for s in trace['steps'] if s['pedagogy']['instruction_event']['function']=='grafo_bfs' and s['pedagogy']['instruction_event']['phase'] not in ['call','scope_exit','caller']]
        assert len(projected)==len(native),(case,run,len(projected),len(native))
        identities={}
        def pointer(native_id,symbol):
            if not native_id:assert symbol=='NULL';return
            if native_id in identities:assert identities[native_id]==symbol
            else:assert symbol not in identities.values();identities[native_id]=symbol
        for step,e in zip(projected,native):
            ped=step['pedagogy'];st=ped['memory_state'];phase=ped['instruction_event']['phase'];expectedphase={'control':'break','statement':'allocate' if 'malloc' in step['line_text'] else 'statement'}.get(e['phase'],e['phase'])
            assert phase==expectedphase,(step['line_text'],e)
            assert step['line_text'].strip()==report['_source_lines'][e['line']-1].strip()
            assert (st['allocations'],st['frees'])==(e['allocations'],e['frees'])
            assert [(n['vertex'],n['mark']) for n in st['graph_marks']]==[(n['vertex'],n['mark']) for n in e['graph_marks']]
            assert [n['value'] for n in st['queue_nodes']]==[n['value'] for n in e['queue']]
            assert [n['value'] for n in st['result_nodes']]==e['returned_list']
            assert [n['value'] for n in st['successor_nodes']]==e['successors']
            for n,m in zip(st['queue_nodes'],e['queue']):pointer(m['id'],n['id'])
            if ped['condition']:assert ped['condition']['result']==bool(e['result'])
            assert step['console']==[] and st['console_stdout']==''
            assert ped['highlight_semantics']=='just-executed'
            assert step['state_after']['last_result'] is None
        lastmarks={n['vertex']:n['mark'] for n in native[-1]['graph_marks']}
        assert trace['steps'][-1]['pedagogy']['memory_state']['frames']==[]
        print('BFS native projection',case,run,len(native),'events;',len(trace['steps']),'modeled steps',flush=True)

def test_bfs_domain_marks_and_owned_result():
    from app.domain.graph import tad_grafo as G
    g=G.grafo_crear()
    for v in [-1,2,3,99]:G.grafo_insertar_vertice(g,v)
    for a,b in [(-1,2),(-1,3),(2,3),(3,-1)]:G.grafo_insertar_arco(g,a,b,1)
    for _ in range(2):
        n=G.grafo_bfs(g,-1);values=[]
        while n:assert n.marcado==0;values.append(n.dato);n=n.sig
        assert values==[-1,2,3] and g._marcas=={-1:1,2:1,3:1,99:0}
    assert G.grafo_bfs(g,101) is None and all(m==0 for m in g._marcas.values())

def test_bfs_history_rebuild_never_executes_query(monkeypatch):
    from app.adapters.graph_adapter import GraphAdapter
    h=[{'operation':'insert_vertex','payload':{'vertex':-1}}]
    for _ in range(2):
        d=S.execute_operation('graph','run_bfs',{'start':-1},h);assert d['success'];h=d['history']
    fail=S.execute_operation('graph','run_bfs',{'start':99},h);assert not fail['success'] and fail['history']==h
    calls=[];old=GraphAdapter.execute
    def spy(self,op,payload):calls.append(op);return old(self,op,payload)
    monkeypatch.setattr(GraphAdapter,'execute',spy)
    for _ in range(2):
        v=S.get_view_model('graph',h);assert v['history']==h and [n['id'] for n in v['visual_state']['nodes']]==['-1']
    assert calls==['insert_vertex','insert_vertex']
    assert [e['operation'] for e in h]==['insert_vertex','run_bfs','run_bfs']
