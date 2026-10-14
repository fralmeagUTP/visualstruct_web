"""Concrete proposed cases and exact missing links for unresolved assigned IDs."""
import ast,hashlib,json
from collections import Counter
from pathlib import Path
R=Path(__file__).resolve().parents[1];C=R/'openspec/changes/archive/2026-10-14-resolve-didactic-stack-c1-residuals'
def proof(path):
 p=R/path;return {'path':path,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}
def op(name,payload=None):return {'operation':name,'payload':payload or {}}
def main():
 old=json.loads((C/'bindings-map95/classification95.json').read_text(encoding='utf-8'));assigned=[x['id'] for x in old if x['status']!='SOURCE_CASE_LINKED_EXECUTION_ACCEPTANCE_SEPARATE'];out=C/'bindings-resolve71';new=json.loads((out/'new-links.json').read_text(encoding='utf-8'));rows=[];plans=[]
 for ident in assigned:
  if ident in new:
   rows.append({'id':ident,'missing_link_resolved':'JSON expected projection/helper wait predicate/response-derived URL plus fixture context','status':'SOURCE_CHAIN_LINKED_ONLY','execution':'NOT_RUN','acceptance':'NOT_ADMITTED'});continue
  category,rest=ident.split(':',1);parts=rest.split('/');setup=[];payload={};expected={};sources=[];missing='';notes=[]
  if category=='algorithm':
   module,phase,name=parts;setup=[op('create_graph',{'directed':False})]+[op('insert_vertex',{'vertex':v}) for v in [1,2,3]]+[op('insert_edge',{'origin':1,'target':2,'weight':1}),op('insert_edge',{'origin':2,'target':3,'weight':2})]
   payload={} if name=='run_kruskal' else {'start':1}
   if name in ['run_dijkstra','run_bellman_ford']:payload['end']=3;expected={'result.path':[1,2,3],'result.distance_to_destination':3}
   elif name in ['run_prim','run_kruskal']:expected={'result.total_weight':3,'normalized_result.mst_edges':[[1,2,1],[2,3,2]],'result.connected':True,'result.components_count':1};sources.append(proof('app/adapters/graph_adapter.py'))
   else:expected={'result':[1,2,3]}
   request={'method':'POST','path':'/graph/graph/operate','json':op(name,payload)};setup.insert(0,{'method':'GET','path':'/graph/graph/'+phase,'expected_status':200,'expected_content':phase})
   missing='PHASE_SCOPED_REQUEST_AND_CONCRETE_RESULT_IN_SAME_CASE'
   sources += [proof('app/routes/graph_routes.py'),proof('tests/test_comprehensive_graph_qa.py'),proof('tests/test_ui_playwright_e2e.py')]
   notes=['Existing backend result tests lack explicit phase context; existing browser phase examples do not assert completed algorithm result. API-level contextual case proposed, not UI/native fidelity.','Chain graph avoids traversal-order and MST ties;3vertices below test bound8.']
  elif category=='operation':
   module,sid,name=parts;request={'method':'POST','path':f'/{module}/{sid}/operate','json':op(name)}
   sources=[proof('app/adapters/'+sid+'_adapter.py')] if module!='sorting' else [proof('app/adapters/sorting_adapter.py'),proof('app/routes/sorting_routes.py')]
   missing='CONCRETE_OPERATION_EXPECTED_CORRELATED_WITH_RESOLVED_SETUP'
   if module=='graph':
    setup=[op('create_graph',{'directed':True}),op('insert_vertex',{'vertex':1}),op('insert_vertex',{'vertex':2}),op('insert_edge',{'origin':1,'target':2,'weight':7})]
    if name=='clear_graph':expected={'followup.list_vertices.result':[],'followup.list_edges.result':[],'directed_preserved':True}
    elif name=='list_vertices':expected={'result':[1,2]}
    elif name=='list_edges':expected={'result_numeric_equality':[[1,2,7]]};notes=['Numeric equality preserves current adapter serialization; do not silently change number types.']
    elif name=='neighbors':payload={'vertex':1};expected={'result':[2]}
    elif name=='edge_weight':payload={'origin':1,'target':2};expected={'result':7}
    elif name=='exists_edge':payload={'origin':1,'target':2};expected={'result':True}
    elif name=='exists_vertex':payload={'vertex':1};expected={'result':True}
    else:raise ValueError(ident)
    sources.append(proof('app/domain/graph/tad_wrappers.py'));notes+=['Registered CASES and route query tests contain generic trace/status checks; no sufficient concrete result recovered in reviewed chain. This is not a claim that no other test exists.']
   elif module=='hierarchical':
    setup=[op('insertar',{'value':7})]
    if name in ['eliminar','limpiar']:payload={'value':7} if name=='eliminar' else {};expected={'followup.inorden.result':[]} if sid!='binary_heap' else {'followup.a_lista.result':[]}
    elif name=='altura':expected={'result':1}
    elif name=='buscar':payload={'value':7};expected={'result':True}
    elif name in ['minimo','maximo','raiz']:expected={'result':7}
    elif name=='contar_hojas':expected={'result':1}
    elif name in ['preorden','postorden','a_lista']:expected={'result':[7]}
    else:raise ValueError(ident)
    sources.append(proof('app/domain/hierarchical/tad_wrappers.py'));notes=['Current generic CASES trace consistency does not supply this literal expected; causal oracle-supported cases require further helper mapping before creating redundant tests.','Single-node setup avoids balancing/duplicate-order ambiguities.']
   elif module=='sequential':
    if sid in ['queue','priority_queue']:
     setup=[op('encolar',{'value':7,**({'priority':1} if sid=='priority_queue' else {})})];expected={'visual_state.size':0}
    elif sid=='circular_list':setup=[op('insertar_final',{'value':7})];expected={'result':7,'visual_state.size':0}
    elif sid=='linked_list':
     values=[1,3] if name in ['insertar_elemento','insertar_posicion'] else ([7,7] if name=='eliminar_repetidos' else [7]);setup=[op('insertar_final',{'value':v}) for v in values]
     if name=='buscar_elemento':payload={'value':7};expected={'result':[1]}
     elif name=='eliminar_elemento':payload={'value':7};expected={'followup.mostrar.result':[]}
     elif name in ['eliminar_inicio','eliminar_final']:expected={'result':7,'visual_state.size':0}
     elif name=='eliminar_repetidos':payload={'value':7};expected={'result':2,'followup.mostrar.result':[]}
     elif name in ['insertar_elemento','insertar_posicion']:payload={'value':2,'position':2} if name=='insertar_posicion' else {'value':2,'position':1,'relative':0};expected={'followup.mostrar.result':[1,2,3]}
     elif name=='limpiar':expected={'followup.mostrar.result':[]}
     elif name=='mostrar':expected={'result':[7]}
     elif name in ['primero','ultimo']:expected={'result':7}
     else:raise ValueError(ident)
    else:raise ValueError(ident)
    sources.append(proof('app/domain/sequential/tad_wrappers.py'));notes=['Map source CASES/setup and a literal operation result first; generic success/trace presence alone is not a completed binding.','Buscar_elemento uses base1 positions; relative0 inserts after anchor.']
   elif module=='sorting' and name=='select_algorithm':
    setup=[{'method':'POST','path':'/api/ordenamiento/create-array','json':{'values':[3,1]}}];request={'method':'POST','path':'/api/ordenamiento/algorithm','json':{'algorithm_id':'burbuja'}};expected={'visual_state.algorithm':'burbuja','visual_state.items':[3,1]};missing='SELECT_RESPONSE_STATE_EXPECTED_NOT_ONLY_SUCCESS_FLAG'
   else:raise ValueError(ident)
   if module!='sorting':request['json']=op(name,payload)
  elif category=='control':
   assert 'export-jpg-scale' in ident;missing='OWNED_URL_AND_CURRENT_ONLY_EXPORT_GEOMETRY_ORACLE'
   request={'page':'/sorting/visualizador','viewport':{'width':390,'height':844},'gesture':{'action':'select_option','selector':'#export-jpg-scale','value':'2'},'setup_input':[7,2,9],'followup_gesture':{'action':'click','selector':'#export-visual-jpg-btn'},'reference_export':{'select_scale':'1','download_decode':['W1','H1']},'owned_server':'New private-session Flask fixture; no existing externalURL, hostpermissions or user5051.'}
   expected={'selected_value':'2','download_mime':'image/jpeg','nonuniform_RGB':True,'export_POST_count':0,'dimension_oracle':{'decode_scale1_export':["W1","H1"],'decode_scale2_export':["2*W1","2*H1"],'precondition':'Same target, unchanged source dimensions; export scale1 once then scale2; current resolveExportDimensions rounds source dimensions before scaling.','no_historical_geometry_transplant':True}};sources=[proof('tests/test_sorting_empty_jpeg_regression.py'),proof('static/js/interpreter_runtime.js')];notes=['Existing conditional test requires JPEG_FOCAL_URL and historical runtime fixture; no current owned URL/context supplied in this block. Do not bind or transplant historical dimensions as a fresh oracle.']
  elif category=='route':
   assert ident=='route:POST /graph/compare';missing='CONCRETE_LEFT_RIGHT_RESULTS_AND_INDEPENDENCE_NOT_ONLY_ISOLATED_FLAG'
   graph={'directed':False,'nodes':[{'id':v} for v in [1,2,3]],'edges':[{'source':1,'target':2,'weight':1},{'source':2,'target':3,'weight':2}]};request={'method':'POST','path':'/graph/compare','json':{'kind':'prim-kruskal','graph':graph,'start':1}};expected={'left.summary.total_weight':3,'right.summary.total_weight':3,'input_equals_supplied_snapshot':True,'session_state_and_history_before_equals_after':True};sources=[proof('app/routes/graph_routes.py'),proof('app/services/graph_structure_service.py'),proof('tests/test_graph_pedagogy_phases_7_9.py')];notes=['Existing test asserts200 and isolated=True but not comparative result or actual before/after independence. Snapshot fixture is3vertices/no ties; do not infer independence from the flag alone.']
  else:raise ValueError(ident)
  assert expected and request
  readiness='CONCRETE_INPUT_EXPECTED_DRAFT'
  plan={'id':ident,'status':'PROPOSED_NOT_IMPLEMENTED_NOT_EXECUTED','missing_link':missing,'setup':setup,'request_or_gesture':request,'expected':expected,'expected_status':200 if category!='control' else None,'sources':sources,'notes':notes,'readiness':readiness,'pre_creation':'Review referenced helpers and accepted prior evidence for an existing sufficient case before authoring; no absolute absence asserted.','execution_constraints':'Private sessions, focal <=120s/2GiB, graph<=8vertices, no containers or campaigns; proposal only.'}
  plans.append(plan);rows.append({'id':ident,'status':'UNLINKED_CASE_DRAFTED','missing_link':missing,'proposed_case_ref':'proposed-tests.json#'+ident,'readiness':readiness})
 assert len(rows)==71 and len(plans)==58 and len({x['id'] for x in rows})==71
 for name,value in [('missing-links71.json',rows),('proposed-tests.json',plans)]:
  (out/name).write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 print(json.dumps({'71_statuses':dict(Counter(x['status'] for x in rows)),'proposal_causes':dict(Counter(x['missing_link'] for x in plans)),'proposal_readiness':dict(Counter(x['readiness'] for x in plans))}))
if __name__=='__main__':main()
