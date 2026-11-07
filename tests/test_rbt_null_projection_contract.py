"""Complete RN NULL edges retain exact identity, cards, geometry and viewport state."""
import json,subprocess
from pathlib import Path
import pytest
from app.services.hierarchical_structure_service import HierarchicalStructureService as S

@pytest.mark.parametrize('size',[0,1,7,31,127,257])
def test_reachable_insert_trace_has_complete_null_links_and_stable_controls(tmp_path,size):
 history=[{'operation':'insertar','payload':{'value':v}} for v in range(size)]
 data=S.execute_operation('red_black','insertar',{'value':size},history);assert data['success']
 states=[dict(label=f'{size}:{i}',state=s['pedagogy']['memory_state']) for i,s in enumerate(data['execution_trace']['steps'])]
 run_projection(tmp_path,states)


def run_projection(tmp_path,states):
 path=tmp_path/'states.json';path.write_text(json.dumps(states));root=Path(__file__).resolve().parents[1]
 result=subprocess.run(['node','qa/check_rbt_null_projection.js',str(path)],cwd=root,capture_output=True,text=True,timeout=90)
 assert result.returncode==0,result.stderr
 result=json.loads(result.stdout);assert result['frames']==len(states)
 assert not result['collisions'],result['collisions'][:5]
 return result


@pytest.mark.parametrize('mutation',['uninitialized','retired','cycle','shared','detached'])
def test_transient_links_never_fabricate_null_or_reserves(tmp_path,mutation):
 from copy import deepcopy
 state=deepcopy(json.loads((Path(__file__).resolve().parents[1]/'qa/rn_classroom_fixture.json').read_text()))
 if mutation=='uninitialized':state['heap_nodes'][0]['left']='sin inicializar'
 elif mutation=='retired':state['heap_nodes'][0]['left']='valor indeterminado; identidad previa N99'
 elif mutation=='cycle':state['heap_nodes'][0]['left']=state['heap_nodes'][0]['id']
 elif mutation=='shared':state['heap_nodes'][0]['left']=state['heap_nodes'][0]['right']=state['heap_nodes'][1]['id']
 else:state['head']='NULL'
 run_projection(tmp_path,[{'label':mutation,'state':state}])


@pytest.mark.parametrize('damage',['omit-null','invent-null','drop-node','duplicate-edge','repoint-card'])
def test_projection_oracle_rejects_missing_invented_or_disagreeing_evidence(tmp_path,damage):
 root=Path(__file__).resolve().parents[1]
 state=json.loads((root/'qa/rn_classroom_fixture.json').read_text())
 path=tmp_path/'states.json';path.write_text(json.dumps([{'label':damage,'state':state}]))
 run=subprocess.run(['node','qa/check_rbt_null_projection.js',str(path),damage],cwd=root,capture_output=True,text=True,timeout=30)
 assert run.returncode!=0 and 'AssertionError' in run.stderr
