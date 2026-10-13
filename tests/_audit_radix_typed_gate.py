"""Compare rendered declared variables and previous values with independent C observations."""
from pathlib import Path
import json,sys
ROOT=Path.cwd();sys.path.insert(0,str(ROOT));sys.path.insert(0,str(ROOT/'tests'))
from _audit_radix_baseline_low import CASES
from app.domain.sorting.tad_ordenamiento import SortingInterpreter
from app.domain.sorting.radix_instructions import SimulatedRadixAllocationFailure,RadixExecutionFailure
from app.services.radix_trace_service import RadixPageSource
from app.services.sorting_structure_service import SortingStructureService
E=ROOT/'openspec/changes/audit-local-quality-and-unified-controls/evidence/visible-sorting-radix-instructions';N=E/'native-expanded'
rows=[json.loads(s) for s in (N/'native.jsonl').read_text(encoding='utf-8').splitlines()]
source=SortingStructureService._didactic_content('sorting_array')['operations']['radixsort']
status_names={0:'undeclared',1:'uninitialized',2:'NULL',3:'live',4:'freed'}
def variables(row,n):
 o=row['typed_observation'];out=[]
 def add(name,kind,value,scope,initialized=True):out.append(dict(name=name,type=kind,value=value if initialized else None,scope=scope,initialized=initialized))
 def ptr(name,target,scope):
  status=o[target+'_status'];size=o['helper_n'] if target=='output' else n
  # Only output pointer is presented while helper is active, so helper_n is actual capacity.
  cells=row['digit_output'] if target=='output' else row[target]+[None]*(n-len(row[target])) if status==3 else None
  value='NULL' if status==2 else dict(alias=target,status=status_names[status],capacity=size,cells=cells if status==3 else None)
  add(name,'uint32_t *',value,scope,status>=2)
 if row['wrapper_active']:
  scope='ordenar_radixsort';add('arreglo','int *',{'alias':'caller'},scope);add('n','size_t',n,scope)
  if o['wrapper_declared']:
   ptr('negativos','negative',scope);ptr('positivos','positive',scope)
   add('cant_negativos','size_t',row['negative_count'],scope);add('cant_positivos','size_t',row['positive_count'],scope)
   add('i','size_t',row['wrapper_i'],scope,row['wrapper_i'] is not None);add('indice','size_t',row['caller_output_index'],scope,o['index_initialized'])
  if o['block']:
   scope='ordenar_radixsort/bloque_'+('negativos' if o['block']==1 else 'positivos');add('maximo','uint32_t',row['maximo'],scope);add('exp','uint32_t',row['exp'],scope)
  if o['magnitud'] is not None:add('magnitud','uint32_t',o['magnitud'],'ordenar_radixsort/recomponer_negativos')
 if row['valid_active']:
  add('arreglo','const int *',{'alias':'caller'},'arreglo_valido');add('n','size_t',n,'arreglo_valido')
 if row['helper_active']:
  scope='counting_por_digito';group=o['helper_alias'];add('arreglo','uint32_t *',{'alias':group,'cells':row[group][:o['helper_n']]},scope);add('n','size_t',o['helper_n'],scope);add('exp','uint32_t',row['exp'],scope)
  if o['helper_declared']:
   add('conteo','size_t[10]',row['counts'],scope);ptr('salida','output',scope);add('i','size_t',row['helper_i'],scope,row['helper_i'] is not None)
  if row['valor'] is not None:add('valor','uint32_t',row['valor'],scope+'/distribucion_inversa')
  if row['digito'] is not None:add('digito','uint32_t',row['digito'],scope+'/distribucion_inversa')
 return out
report=[]
cases=[(name,v,0,i) for i,(name,v) in enumerate(CASES.items())]+[('fault_'+str(i),[-5,2],i,19+i) for i in range(1,5)]+[('maximum',[-2147483648,2147483647]*40,0,40),('normal_second',sorted(CASES['normal']),0,50),('negative_second',sorted(CASES['negative_duplicates']),0,51),('extremes_second',sorted(CASES['int32_extremes']),0,52)]
for name,values,fault,case in cases:
 def allocator(name,capacity,attempt):
  if attempt==fault:raise SimulatedRadixAllocationFailure('private typed gate')
 try:d=SortingInterpreter(values,'radixsort',radix_allocator=allocator if fault else None).run();tape=d['steps'];error=None
 except RadixExecutionFailure as ex:tape=ex.steps;error=ex.error_info
 p=RadixPageSource(tape,source,error_info=error);native=[r for r in rows if r.get('case')==case and 'token'in r];old={}
 for i,r in enumerate(native):
  expected=variables(r,len(values));frame=p.frame(i);shown=frame['pedagogy']['variables'];expected_keys={}
  for v in expected:
   prior=old.get((v['scope'],v['name']));v.update(previous=prior['value'] if prior and prior['initialized'] else None,changed=prior is None or prior['initialized']!=v['initialized'] or prior['value']!=v['value']);expected_keys[(v['scope'],v['name'])]=v
  actual={(v['scope'],v['name']):{k:v[k] for k in ['name','type','value','scope','initialized','previous','changed']} for v in shown}
  assert expected_keys==actual,(name,i,r['token'],expected_keys,actual)
  stack=[]
  if r['wrapper_active']:stack.append(dict(function='ordenar_radixsort',parameters={'arreglo':'caller','n':len(values)}))
  if r['valid_active']:stack.append(dict(function='arreglo_valido',parameters={'arreglo':'caller','n':len(values)}))
  if r['helper_active']:stack.append(dict(function='counting_por_digito',parameters={'arreglo':r['typed_observation']['helper_alias'],'n':r['typed_observation']['helper_n'],'exp':r['exp']}))
  assert stack==[{k:f[k] for k in ['function','parameters']} for f in frame['pedagogy']['call_stack']],(name,i)
  old=expected_keys
 report.append(dict(case=name,rendered_frames=len(native),all_variables_initialized_types_aliases_scopes_previous_changes_match=True,call_stack_and_actual_parameters_match=True));print(name,len(native),flush=True)
(N/'typed-rendered-report.json').write_text(json.dumps(dict(cases=report,scope='finite observer at statement/control/declaration boundaries; no order claimed inside a C expression; C _Generic checks assert presented types; source line bindings validated, not an independent compiler source map'),indent=2),encoding='utf-8')
