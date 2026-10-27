"""Reviewed concrete source bindings for the finite95context block."""
from pathlib import Path
import ast,hashlib,json
from collections import Counter
from scripts.build_app_quality_inventory import validate_executable_bindings
R=Path(__file__).resolve().parents[1];C=R/'openspec/changes/archive/2026-10-14-resolve-didactic-stack-c1-residuals'
def load(name,fn):
 p=R/name;t=ast.parse(p.read_text(encoding='utf-8-sig'));f=next(n for n in t.body if isinstance(n,ast.FunctionDef) and n.name==fn);return p,t,f
def assertion(f,expression):
 wanted=ast.dump(ast.parse(expression,mode='eval').body,include_attributes=False)
 a=next((n for n in ast.walk(f) if isinstance(n,ast.Assert) and ast.dump(n.test,include_attributes=False)==wanted),None)
 if a is None:raise ValueError('Expected assertion not present: '+expression)
 return {'expression':ast.unparse(a.test),'line':a.lineno}
def params(f,key):
 for d in f.decorator_list:
  if isinstance(d,ast.Call) and isinstance(d.func,ast.Attribute) and d.func.attr=='parametrize' and len(d.args)>=2 and ast.literal_eval(d.args[0])==key:return ast.literal_eval(d.args[1])
 raise ValueError('Parametrization not literal: '+key)
def helper(t,path):
 f=next(n for n in t.body if isinstance(n,ast.FunctionDef) and n.name=='_post');call=f.body[0].value
 assert isinstance(call,ast.Call) and ast.unparse(call.func)=='client.post'
 assert ast.unparse(call.args[0])==path
 assert ast.unparse(call.keywords[0].value)=="{'operation': operation, 'payload': payload}"
 return {'name':'_post','line':f.lineno,'path_expression':path}
def main():
 baseline=C/'bindings-pending-routes-operations';registry=json.loads((baseline/'app-executable-bindings.json').read_text(encoding='utf-8'));pending=json.loads((baseline/'unassigned.json').read_text(encoding='utf-8'));rows=json.loads((C/'gap-inventory232/items.json').read_text(encoding='utf-8'));target={x['id'] for x in rows if x['cause']=='EXISTING_TEST_CONTEXT_NOT_MAPPED'};assert len(target)==95
 added=[]
 def bind(ident,p,f,layer,input_data,checks,scope):
  if ident not in pending:return
  assert ident in target
  registry['items'][ident]={'test_node':p.relative_to(R).as_posix()+'::'+f.name,'layer':layer,'input':input_data,'expected':{'assertions':checks},'provenance':{'test_source_sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'function_line':f.lineno,'status':'SOURCE_LINK_VERIFIED_ONLY','execution':'NOT_RUN_THIS_PHASE','acceptance':'NOT_ADMITTED_THIS_PHASE'},'oracle_scope':scope};added.append(ident)
 # All algorithm parameters are declared literals; adapter fixture is real C.
 p,t,f=load('tests/test_sorting_trace.py','test_all_sorting_algorithms_satisfy_common_trace_contract')
 check=assertion(f,"result['visual_state']['items'] == [1, 2, 3, 4, 5]")
 fixture=next(n for n in t.body if isinstance(n,ast.FunctionDef) and n.name=='sorting_c_operations')
 assert "CCodeService.get_structure_data('sorting_array')" in ast.unparse(fixture)
 assert "adapter.execute('create_array', {'values': '5,1,4,2,3'})" in ast.unparse(f)
 assert "adapter.execute('run', {'mode': 'step_by_step', 'source_code': sorting_c_operations[algorithm_id]})" in ast.unparse(f)
 for algo in params(f,'algorithm_id'):
  bind('algorithm:sorting/'+algo,p,f,'unit',{'parameters':{'algorithm_id':algo},'adapter':'SortingAdapter','operations':[{'operation':'create_array','payload':{'values':'5,1,4,2,3'}},{'operation':'select_algorithm','payload':{'algorithm_id':algo}},{'operation':'run','payload':{'mode':'step_by_step','source_code_fixture':'sorting_c_operations[algorithm_id]'}}],'fixture':{'name':'sorting_c_operations','line':fixture.lineno,'provider':'CCodeService.get_structure_data(sorting_array).operations'},'route_relationship':{'contract':'POST /api/ordenamiento/run','status':'CONSUMER_NOT_EXERCISED_BY_THIS_UNIT_CASE'},'context':'complete referenced parametrized adapter test and fixture'},[check],'Adapter nominal sorted values only; not API, native equivalence or phase/UI acceptance.')
 # Hierarchical literal setup and helper requests, parameter context kept.
 p,t,f=load('tests/test_comprehensive_hierarchical_qa.py','test_balanced_tree_rotations_and_deletion_keep_invariants');h=helper(t,"f'/hierarchical/{structure}/operate'")
 loop=next(n for n in f.body if isinstance(n,ast.For));values=ast.literal_eval(loop.iter);assert values==('30','20','10','25','40','50')
 assert "_post(client, structure, 'eliminar', {'value': '30'})" in ast.unparse(f)
 setup=[{'operation':'insertar','payload':{'value':v}} for v in values]+[{'operation':'eliminar','payload':{'value':'30'}}]
 for sid in params(f,'structure'):
  for op,expr,value in [('validar',"validated['result'] is True",True),('inorden',"ordered['result'] == [10, 20, 25, 40, 50]",[10,20,25,40,50])]:
   assert f"_post(client, structure, '{op}', {{}})" in ast.unparse(f)
   check=assertion(f,expr);check['literal_expected']=[value]
   bind(f'operation:hierarchical/{sid}/{op}',p,f,'api',{'parameters':{'structure':sid},'request':{'method':'POST','path':f'/hierarchical/{sid}/operate','json':{'operation':op,'payload':{}}},'setup_operations':setup,'helper':h,'context':'complete test, including both queries after deletion'},[check],'Concrete validator result or in-order values for this seeded tree; not universal branch or C fidelity.')
 p,t,f=load('tests/test_comprehensive_hierarchical_qa.py','test_hierarchical_invalid_integer_is_rejected_without_history');h=helper(t,"f'/hierarchical/{structure}/operate'");checks=[assertion(f,'response.status_code == 400'),assertion(f,"response.get_json()['history'] == []")];assert "_post(client, structure, 'insertar', {'value': 'invalid'})" in ast.unparse(f)
 for sid in params(f,'structure'):
  bind(f'operation:hierarchical/{sid}/insertar',p,f,'api',{'parameters':{'structure':sid},'request':{'method':'POST','path':f'/hierarchical/{sid}/operate','json':{'operation':'insertar','payload':{'value':'invalid'}}},'setup_operations':[],'helper':h,'context':'empty fixture session'},checks,'Invalid integer rejection and unchanged empty history only; nominal insertion remains separate.')
 p,t,f=load('tests/test_comprehensive_hierarchical_qa.py','test_heap_extracts_in_ascending_order_and_preserves_heap_property');h=helper(t,"f'/hierarchical/{structure}/operate'");values=ast.literal_eval(next(n for n in f.body if isinstance(n,ast.For)).iter);assert values==('9','1','7','1','3');check=assertion(f,'extracted == [1, 1, 3, 7, 9]');assert "range(5)" in ast.unparse(f)
 bind('operation:hierarchical/binary_heap/extraer_raiz',p,f,'api',{'request':{'method':'POST','path':'/hierarchical/binary_heap/operate','json':{'operation':'extraer_raiz','payload':{}}},'repeat':5,'setup_operations':[{'operation':'insertar','payload':{'value':v}} for v in values],'helper':h,'context':'complete five extractions; expected is ordered aggregate, not five independent initial-state cases'},[check],'Five extraction results with duplicate1; not native/heap lifetime acceptance.')
 p,t,f=load('tests/test_comprehensive_graph_qa.py','test_graph_algorithms_return_expected_traversal_shortest_path_and_mst');h=helper(t,"'/graph/graph/operate'");base=ast.literal_eval(next(n.value for n in t.body if isinstance(n,ast.Assign) and any(isinstance(a,ast.Name) and a.id=='BASE' for a in n.targets)));check=assertion(f,"prim['total_weight'] == kruskal['total_weight'] == 3");check['literal_expected']=[3];assert "_post(client, 'run_prim', {'start': '1'})" in ast.unparse(f)
 bind('operation:graph/graph/run_prim',p,f,'api',{'request':{'method':'POST','path':'/graph/graph/operate','json':{'operation':'run_prim','payload':{'start':'1'}}},'setup_operations':[{'operation':op,'payload':payload} for op,payload in base],'helper':h,'context':'complete shared result test; no explicit phase GET is present'},[check],'Prim weight3 backend case; no proof of construction/MST phase UI interaction.')
 p,t,f=load('tests/test_comprehensive_graph_qa.py','test_every_graph_learning_phase_renders');phases=params(f,'phase');check=assertion(f,'phase.encode() in response.data');status=assertion(f,'response.status_code == 200');assert "client.get(f'/graph/graph/{phase}')" in ast.unparse(f)
 for phase in phases:
  data={'parameters':{'phase':phase},'request':{'method':'GET','path':'/graph/graph/'+phase},'context':'referenced phase parameter and fixture'}
  bind('phase:graph/'+phase,p,f,'api',data,[status,{**check,'literal_expected':[{'bytes_hex':phase.encode().hex()}]}],'Rendered phase identifier and HTTP200 only; no algorithm execution.')
 bind('route:GET /graph/<structure_id>/<phase>',p,f,'api',{'parameter_cases':[{'structure_id':'graph','phase':phase,'path':'/graph/graph/'+phase} for phase in phases],'context':'complete phase parametrization'},[status,check],'Four literal valid graph phases; not invalid phase/structure cases.')
 out=C/'bindings-map95';out.mkdir(exist_ok=True);manifest=json.loads((R/'docs/qa/app-coverage-manifest-v1.json').read_text(encoding='utf-8'));items={x['id']:x for x in manifest['items']};errors=validate_executable_bindings({'items':[items[x] for x in added]},{'schema':registry['schema'],'items':{x:registry['items'][x] for x in added}},project_root=R);assert not errors,errors
 remaining=[x for x in pending if x not in added];classification=[]
 for x in rows:
  if x['id'] not in target:continue
  shared=bool(x['scope_duplicate_flags']);classification.append({'id':x['id'],'status':'SOURCE_CASE_LINKED_EXECUTION_ACCEPTANCE_SEPARATE' if x['id'] in added else ('SHARED_CONTEXT_RETAINED_NEEDS_PHASE_ORACLE' if shared else 'CANDIDATE_NOT_YET_A_COMPLETE_CASE'),'binding_ref':'app-executable-bindings.json' if x['id'] in added else None,'next_action':'Associate accepted existing evidence or authorize focal execution if needed; no automatic admission.' if x['id'] in added else 'Resolve helpers/parameters and concrete correlated expectation; literal reference remains insufficient.'})
 summary={'candidates_reviewed':95,'shared_contexts_reviewed':14,'shared_requirements_removed':0,'new_source_links':len(added),'new_links_by_category':dict(Counter(items[x]['category'] for x in added)),'before_links':143,'after_links':len(registry['items']),'before_pending':232,'after_pending':len(remaining),'candidate_contexts_remaining':95-len(added),'application_test_bodies_executed':0,'new_acceptances':0,'gate_errors':len(errors)}
 for name,value in [('app-executable-bindings.json',registry),('unassigned.json',remaining),('classification95.json',classification),('summary.json',summary)]:
  (out/name).write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 print(json.dumps(summary))
if __name__=='__main__':main()
