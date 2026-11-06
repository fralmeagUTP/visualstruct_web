"""Anonymous initial panels are intentionally hidden until an actual execution frame."""
import json,subprocess
from pathlib import Path
import pytest
from app.services.hierarchical_structure_service import HierarchicalStructureService as H
from app.services.structure_service import StructureService as S

@pytest.mark.parametrize('family,operation,payload',[
 ('abb','insertar',{'value':4}),('sublist','insertar_padre',{'parent':9}),
 ('sublist','insertar_hijo',{'parent':7,'child':9}),('sublist','eliminar_padre',{'parent':7}),
 ('sublist','limpiar',{}),('sublist','hijos_de',{'parent':7}),
])
def test_real_contextual_help_reaches_variables_only_with_frames(tmp_path,family,operation,payload):
 service=H if family=='abb' else S;history=[]
 seeds=[('insertar',{'value':7})] if family=='abb' else [('insertar_padre',{'parent':7}),('insertar_hijo',{'parent':7,'child':3})]
 for op,pay in seeds:
  data=service.execute_operation(family,op,pay,history);assert data['success'];history=data['history']
 data=service.execute_operation(family,operation,payload,history);assert data['success']
 frames=[s['pedagogy'] for s in data['execution_trace']['steps']]
 prefix='hier' if family=='abb' else 'seq';target='hier-variables-view' if prefix=='hier' else 'seq-variable-view'
 file=tmp_path/'input.json';file.write_text(json.dumps(dict(prefix=prefix,target=target,family=family,operation=operation,frames=frames)))
 run=subprocess.run(['node','qa/check_contextual_variable_reachability.js',str(file)],cwd=Path(__file__).resolve().parents[1],capture_output=True,text=True,timeout=30)
 assert run.returncode==0,run.stderr
 assert json.loads(run.stdout)['frames']==len(frames)
