"""17 live native graphs: independent C instruction observer versus full validator trace."""
import json
from copy import deepcopy
from pathlib import Path
import pytest
from app import create_app
from app.services.c_code_service import CCodeService
from app.services.hierarchical_structure_service import HierarchicalStructureService as S
from app.domain.hierarchical.rbt_query_instruction import build_rbt_query_trace
from _audit_rbt_full_validator_baseline_low import CASES,build,oracle
from _audit_rbt_query_native_observer import observe
from test_audit_rbt_query_instruction_native import match
@pytest.mark.parametrize('name,desc',CASES,ids=[x[0] for x in CASES])
def test_full_rn_live_native_instruction_trace(tmp_path,name,desc):
 nodes=build(desc);expected=bool(oracle(nodes[0] if nodes else None));data=S.execute_operation('red_black','validar',{},[]);trace=deepcopy(data['execution_trace']);trace['source_code']=CCodeService.get_structure_data('red_black')['operations']['validar'];state=deepcopy(trace['steps'][0]['state_snapshot']);after=deepcopy(state);after['validation']=expected
 ptr=lambda i:'NULL' if i is None else 'N'+str(i+1)
 projection={'head':'N1' if desc else 'NULL','heap_nodes':[dict(id=ptr(i),value=v,color={'r':'RED','n':'BLACK'}.get(c,'INVALID'),parent=ptr(p),left=ptr(l),right=ptr(r),status='linked') for i,(v,c,p,l,r) in enumerate(desc)]}
 trace=build_rbt_query_trace(trace,state,after,native_projection=projection)
 client=create_app().test_client();raw=client.get('/help/source/red_black/source').data;header=client.get('/help/source/red_black/header').data;events=observe(trace['source_code'],'validar',[],0,raw,header,tmp_path,live_fixture=desc)
 match(trace,events);assert bool(events[-1]['wrapper'])==expected
 assert all(e['stdout_hex']=='' for e in events)
 assert all(e['heap']==events[0]['heap'] for e in events)
 (tmp_path/'trace.json').write_text(json.dumps(trace),encoding='utf-8')
 print(name,len(events),sum(e['phase']=='condition' for e in events))
