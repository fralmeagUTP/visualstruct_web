"""DFS native statement/condition/frame/heap conformance on recorded fixtures."""
import copy,json
from pathlib import Path
import pytest
from app.services.graph_structure_service import GraphStructureService as S
from app.services.c_code_service import CCodeService
from app.domain.graph.dfs_instruction import build_dfs_trace
from _audit_graph_dfs_instruction_observer import observe,CASES

@pytest.fixture(scope='module')
def dfs_native(tmp_path_factory):
    out=tmp_path_factory.mktemp('dfs-parent')/'native';report=observe(out)
    report['_lines']=(out/'tad_grafo.c').read_text(encoding='utf-8').splitlines();return report

def case_trace(c,marks=None,history=None):
    h=[{'operation':'create_graph','payload':{'directed':True}},*[{'operation':'insert_vertex','payload':{'vertex':v}} for v in c['vertices']],*[{'operation':'insert_edge','payload':{'origin':a,'target':b,'weight':1}} for a,b in c['edges']]]
    if history is not None:h=history
    before=S.get_view_model('graph',h)['visual_state'];data=S.execute_operation('graph','run_dfs',{'start':c['start']},h)
    if data['success'] and (marks is None or history is not None):return data['execution_trace']
    if marks:
        for n in before['nodes']:n['marked']=marks.get(int(n['id']),0)
    trace=copy.deepcopy(data['execution_trace']);trace['source_code']=CCodeService.get_structure_data('graph')['operations']['run_dfs'];return build_dfs_trace(trace,before,data['visual_state'])

@pytest.mark.parametrize('case',range(10))
def test_dfs_native_instructions(dfs_native,case):
    c=CASES[case];previousmarks=None;history=None
    for run in range(c.get('repeat',1)):
        if run and c['start'] in c['vertices']:
            # Actual persisted first-call history, not a manually overwritten
            # input-state model, supplies marks for the second API trace.
            h=[{'operation':'create_graph','payload':{'directed':True}},*[{'operation':'insert_vertex','payload':{'vertex':v}} for v in c['vertices']],*[{'operation':'insert_edge','payload':{'origin':a,'target':b,'weight':1}} for a,b in c['edges']]]
            history=S.execute_operation('graph','run_dfs',{'start':c['start']},h)['history']
        trace=case_trace(c,previousmarks,history);native=[e for e in dfs_native['events'] if e['case']==case and e['run']==run]
        steps=[s for s in trace['steps'] if s['pedagogy']['instruction_event']['phase'] not in ['call','scope_exit','caller','operand']]
        assert len(steps)==len(native),(case,run,len(steps),len(native))
        identities={}
        def pointer(ident,symbol):
            if ident==-2:assert symbol=='sin inicializar';return
            if ident==0:assert symbol=='NULL';return
            clean=symbol.split(' (identidad histórica;')[0]
            if ident in identities:assert identities[ident]==clean,(ident,symbol,identities[ident])
            else:assert clean not in identities.values();identities[ident]=clean
        for s,e in zip(steps,native):
            ped=s['pedagogy'];st=ped['memory_state'];event=ped['instruction_event']
            assert event['function']==e['function'] and event['phase']==e['phase'],(case,s['line_text'],event,e)
            assert s['line_text'].strip()==dfs_native['_lines'][e['line']-1].strip()
            assert (st['allocations'],st['frees'])==(e['allocations'],e['frees'])
            if e['phase']=='condition':assert bool(e['result'])==ped['condition']['result']
            if e['phase']=='return':
                if e['function'] in ['grafo_existe_vertice','grafo_marcado_vertice']:assert ped['call_stack'][-1]['return_value']==e['result']
                elif e['function'] in ['grafo_dfs','grafo_sucesores']:pointer(e['result'],ped['call_stack'][-1]['return_value'])
                elif e['function'] in ['grafo_dfs_recursivo','grafo_agregar_recorrido']:assert ped['call_stack'][-1]['return_value']=='void'
            assert len(st['heap_nodes'])==len(e['heap'])
            # Bind identities from immutable graph fields first, then typed new reservations.
            for hn in e['heap']:
                kind={1:'result',2:'successor',3:'vertex',4:'arc'}[hn['kind']]
                if hn['id'] in identities:mn=next(n for n in st['heap_nodes'] if n['id']==identities[hn['id']])
                else:
                    candidates=[n for n in st['heap_nodes'] if n['kind']==kind and n['id'] not in identities.values()]
                    if kind=='vertex':candidates=[n for n in candidates if n['value']==hn['value']]
                    if kind=='arc':candidates=[n for n in candidates if (n['origin'],n['target'])==(hn['origin'],hn['target'])]
                    assert len(candidates)==1,(case,event,hn,candidates);mn=candidates[0];pointer(hn['id'],mn['id'])
                assert mn['kind']==kind
                if kind=='arc':assert (mn['origin'],mn['target'])==(hn['origin'],hn['target'])
                else:
                    for bit,field in [(1,'value'),(2,'mark'),(4,'next')]:
                        if hn['bits']&bit:
                            if field=='next':pointer(hn[field],mn[field])
                            else:assert mn[field]==hn[field]
                        else:assert mn[field]=='sin inicializar'
                if kind=='arc':pointer(hn['next'],mn['next'])
            pointer(e['head'],st['head_storage']['value'])
            assert len(ped['call_stack'])==len(e['frames'])
            for shown,nf in zip(ped['call_stack'],e['frames']):
                assert shown['function']==nf['function'] and shown['frame_id']=='F'+str(nf['id'])
                combined={**shown['parameters'],**shown['locals']}
                if nf['has_param']:
                    name='inicio' if nf['function']=='grafo_dfs' else 'actual' if nf['function']=='grafo_dfs_recursivo' else 'x'
                    assert combined[name]==nf['param']
                if nf['headref']:assert combined['recorrido']==st['head_storage']['id']
                for name,ident in nf['locals'].items():pointer(ident,combined[name])
            assert ped['highlight_semantics']=='just-executed' and s['console']==[] and st['console_stdout']==''
            assert s['state_after']['last_result'] is None
        previousmarks={n['vertex']:n['mark'] for n in steps[-1]['pedagogy']['memory_state']['graph_marks']}
        assert trace['steps'][-1]['pedagogy']['memory_state']['frames']==[]
        print('DFS',case,run,len(native),'native events;',len(trace['steps']),'steps',flush=True)
