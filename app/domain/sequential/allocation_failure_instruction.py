"""Translate a denied node constructor into its unchanged canonical C NULL path."""
from __future__ import annotations
from copy import deepcopy
import dis
from functools import lru_cache
from importlib import import_module
import re
from typing import Any
from app.services.c_code_service import CCodeService
from app.domain.sequential.pedagogy import SEQUENTIAL_FRAME_SCHEMA_VERSION, sequential_frame_schema, validate_sequential_frame

MESSAGE = "No se pudo reservar memoria. La estructura no cambió."
ERROR = {"code": "allocation_failed", "stage": "operation", "object_created": False}
_TARGETS = {
 ('stack','apilar'):('tad_pila','pila_apilar','NodoPila'),
 ('queue','encolar'):('tad_cola','cola_encolar','NodoCola'),
 ('priority_queue','encolar'):('tad_cola_prioridad','cp_encolar','CPNodo'),
 ('linked_list','insertar_inicio'):('tad_lista','lista_insertar_inicio','NodoLista'),
 ('linked_list','insertar_final'):('tad_lista','lista_insertar_final','NodoLista'),
 ('linked_list','lista_insertar_elemento'):('tad_lista','lista_insertar_elemento','NodoLista'),
 ('circular_list','insertar_inicio'):('tad_lista_circular','lcir_insertar_inicio','LCirNodo'),
 ('circular_list','insertar_final'):('tad_lista_circular','lcir_insertar_final','LCirNodo'),
 ('sublist','insertar_padre'):('tad_sublista','sublista_insertar_padre_final','Nodo'),
 ('sublist','insertar_hijo'):('tad_sublista','sublista_insertar_hijo_final','Sublista'),
}

@lru_cache(maxsize=16)
def _constructor_calls(code: Any, name: str) -> frozenset[int]:
 """Identify actual constructor CALLs; do not relabel later metadata/replay errors."""
 pending=False;offsets=set()
 for instruction in dis.get_instructions(code):
  if instruction.opname in {'LOAD_GLOBAL','LOAD_NAME'} and instruction.argval==name:pending=True
  elif pending and instruction.opname.startswith('CALL'):
   offsets.add(instruction.offset);pending=False
 return frozenset(offsets)

def is_node_allocation_failure(error: MemoryError, structure_id: str, operation: str) -> bool:
 target=_TARGETS.get((structure_id,operation))
 if target is None:return False
 module,function,name=target;code=getattr(import_module('app.domain.sequential.'+module),function).__code__
 current=error.__traceback__
 while current is not None:
  if current.tb_frame.f_code is code and current.tb_lasti in _constructor_calls(code,name):return True
  current=current.tb_next
 return False

class _NullPath:
 """Only existing objects and executed NULL branches, with explicit C call scopes."""
 def __init__(self, family: str, operation: str, payload: dict, source: str, before: dict) -> None:
  self.family=family;self.operation=operation;self.payload=payload;self.source=source;self.lines=source.splitlines();self.before=deepcopy(before);self.frames=[];self.types={};self.steps=[];self.heap=[]
  items=before.get('items',[])
  if family=='sublist':
   for i,item in enumerate(items,1):
    children=item.get('children',[]);self.heap.append({'id':f'P{i}','kind':'parent','value':item['parent'],'next':f'P{i+1}' if i<len(items) else 'NULL','sub':f'H{i}.1' if children else 'NULL','status':'linked'})
    for j,value in enumerate(children,1):self.heap.append({'id':f'H{i}.{j}','kind':'child','value':value,'next':f'H{i}.{j+1}' if j<len(children) else 'NULL','status':'linked'})
   self.head='P1' if items else 'NULL'
  else:
   for i,item in enumerate(items,1):self.heap.append({'id':f'N{i}','value':item['value'],'next':f'N{i+1}' if i<len(items) else ('N1' if family=='circular_list' else 'NULL'),'status':'linked'})
   self.head='N1' if items else 'NULL'
  self.last=self.snapshot()
 def index(self, fn: str, token: str, after: str | None = None) -> int:
  start=next(i for i,l in enumerate(self.lines) if re.search(r'\b'+re.escape(fn)+r'\s*\(',l) and l.rstrip().endswith('{'))
  depth=0;end=start
  for i in range(start,len(self.lines)):
   depth+=self.lines[i].count('{')-self.lines[i].count('}');end=i
   if depth==0:break
  if after:start=next(i+1 for i in range(start,end+1) if after in self.lines[i])
  return next(i for i in range(start,end+1) if token in self.lines[i])
 def snapshot(self) -> dict:
  m=deepcopy(self.before);m.update(head=self.head,heap_nodes=deepcopy(self.heap),allocation_failure_model=True)
  if self.family=='sublist':
   m.update(sublist_delete_model=True,sublist_frames=deepcopy(self.frames))
  elif self.family=='circular_list':
   m.update(circular_insert_model=True,cabeza=self.head,cola=f'N{len(self.heap)}' if self.heap else 'NULL',cantidad=len(self.heap),cola_sgte=self.head,cycle_target=self.head,reachable_count=len(self.heap),lista='&lc',node_ids=[n['id'] for n in self.heap],active_function=self.frames[-1]['function'] if self.frames else '')
   if self.frames:
    active=self.frames[-1];m.update(active['locals'])
  else:
   m.update(insert_model=True,lista='&cabeza',node_ids=[n['id'] for n in self.heap],local_pointer_names=['q'])
   if self.frames and 'q' in self.frames[-1]['locals']:m['q']=self.frames[-1]['locals']['q']
  if not self.frames:m['scope_ended']=True
  return m
 def objects(self) -> list[dict]:
  objects=[]
  for n in self.heap:
   fields={'nro' if self.family!='circular_list' else 'valor':n['value'],'sgte':n['next']}
   if n.get('kind')=='parent':fields['sub']=n['sub']
   objects.append({'id':n['id'],'address':n['id'],'type':'Nodo' if n.get('kind')=='parent' else 'Sublista' if n.get('kind')=='child' else 'LCirNodo' if self.family=='circular_list' else 'struct NodoLista','alive':True,'allocated':True,'freed':False,'status':'linked','initialized_mask':(1<<len(fields))-1,'fields_valid':True,'field_validity':{k:True for k in fields},'fields':fields})
  return objects
 def push(self, fn: str, params: dict, types: dict) -> None:
  self.frames.append({'function':fn,'parameters':params,'locals':{}});self.types[fn]=types
 def local(self, name: str, value: Any, ctype: str) -> None:
  self.frames[-1]['locals'][name]=value;self.types[self.frames[-1]['function']][name]=ctype
 def emit(self, fn: str, token: str, event: str='line', condition: bool | None=None, after: str | None=None, returning: bool=False, return_value: Any=None) -> None:
  index=self.index(fn,token,after);stack=deepcopy(self.frames)
  if returning:
   stack[-1]['return']=return_value;self.frames.pop()
  m=self.snapshot();variables=[];pointers=[]
  current={f['function']:f for f in self.frames}
  for frame in stack:
   scope=frame['function'];remaining=current.get(scope)
   for name,value in {**frame['parameters'],**frame['locals']}.items():
    initialized=value!='indeterminado; no leer';active=remaining is not None;shown=value if active else 'fuera de ámbito';ctype=self.types[scope][name]
    variable={'name':name,'scope':scope,'type':ctype,'value':shown,'initialized':initialized,'valid':initialized and active,'scope_state':'active' if active else 'fuera de ámbito','changed':False};variables.append(variable)
    if '*' in ctype or ctype=='Tlista':pointers.append({**variable,'target':shown,'previous_target':shown,'dangling':False})
  heap=self.objects();line=self.lines[index]
  clean=line.strip();expression=clean[clean.find('(')+1:clean.rfind(')')] if condition is not None else ''
  substituted=expression
  if condition is not None:
   active=stack[-1] if stack else None
   values={**active['parameters'],**active['locals']} if active else {}
   for node in self.heap:
    for name,value in values.items():
     if value==node['id']:
      substituted=substituted.replace(name+'->nro',str(node['value']))
   for name,value in sorted(values.items(),key=lambda pair:-len(pair[0])):
    substituted=re.sub(r'\b'+re.escape(name)+r'\b',lambda match:str(value),substituted)
  console=[]
  if line.strip().startswith('printf('):
   from app.services.execution_trace_service import ExecutionTraceService
   output=ExecutionTraceService._printf_literal(line,preserve_trailing_newlines=True)
   if output is not None:console=[output]
  step={'step_index':len(self.steps),'line_index':index,'line_text':line,'event_type':event,'phase':'progress','delay_ms':100,'state_snapshot':deepcopy(self.last),'state_after':deepcopy(m),'console':console,'condition_result':condition,'function_name':fn,'debug':{'stage':event,'allocator_result':'NULL','object_created':False}}
  description='La reserva falló: NULL no es un objeto; raíz, enlaces y objetos existentes se conservan.'
  frame={'schema_version':SEQUENTIAL_FRAME_SCHEMA_VERSION,'structure':self.family,'operation':self.operation,'concept':'return' if returning else 'condition' if condition is not None else 'console' if console else 'call' if event=='call' else 'allocation' if 'allocator' in event else 'assignment','phase':{'id':event,'label':fn,'goal':description},'condition':None if condition is None else {'source':expression,'substituted':substituted,'result':condition,'consequence':'Rama C alcanzada.'},'variables':variables,'pointers':pointers,'heap_objects':deepcopy(heap),'heap_transition':{'kind':'allocation_failure' if 'allocator' in event else 'stable','before':deepcopy(heap),'after':deepcopy(heap),'freed':[],'dangling_references':[]},'call_stack':stack,'call_stack_after':deepcopy(self.frames),'loop':{'active':False,'condition':None,'exit':None},'state_changes':[],'invariant':{'holds':True,'symbol':'✓','text':'Ninguna reserva nueva se publicó.','evidence':f'{len(heap)} objetos existentes; cero objetos creados o liberados.'},'narration':{level:description for level in ['basic','intermediate','advanced']},'source':{'line_index':index,'line_text':line,'function':fn},'memory_state':deepcopy(m),'allocation_failure_memory':deepcopy(m)}
  validate_sequential_frame(frame,source_code=self.source);step['pedagogy']=frame;self.steps.append(step);self.last=m
 def allocator(self, helper: str, name: str, ctype: str, value: int) -> None:
  self.push(helper,{'valor':value},{'valor':'int'})
  self.emit(helper,helper+'(',event='call');self.local(name,'indeterminado; no leer',ctype)
  self.emit(helper,'malloc(',event='allocator_enter');self.local(name,'NULL',ctype);self.emit(helper,'malloc(',event='allocator_NULL_return')
  self.emit(helper,'if ('+name+' == NULL)',condition=True)
  if self.family=='linked_list':self.emit(helper,'printf(',event='stdout')
  self.emit(helper,'return NULL;',returning=True,return_value='NULL')
 def build(self) -> dict:
  f=self.family;op=self.operation;p=self.payload
  if f=='linked_list':
   fn='lista_'+op if not op.startswith('lista_') else op;params={'lista':'&cabeza','valor':int(p['value'])};types={'lista':'Tlista *','valor':'int'}
   if op=='lista_insertar_elemento':params['pos']=int(p['position']);types['pos']='int'
   self.push(fn,params,types);self.emit(fn,fn+'(',event='call');self.emit(fn,'if (lista == NULL',condition=False);self.local('q','indeterminado; no leer','Tlista');self.emit(fn,'CrearNodoLista(valor)',event='call');self.allocator('CrearNodoLista','q','Tlista',params['valor']);self.local('q','NULL','Tlista');self.emit(fn,'CrearNodoLista(valor)');self.emit(fn,'if (q == NULL)',condition=True);self.emit(fn,'return;',after='if (q == NULL)',returning=True)
  elif f=='circular_list':
   fn='lcir_'+op;self.push(fn,{'lista':'&lc','valor':int(p['value'])},{'lista':'ListaCircular *','valor':'int'});self.emit(fn,fn+'(',event='call');self.local('nuevo','indeterminado; no leer','LCirNodo *');self.emit(fn,'LCirNodo *nuevo;');self.emit(fn,'if (lista == NULL)',condition=False);self.emit(fn,'nuevo = lcir_crear_nodo',event='call');self.allocator('lcir_crear_nodo','nodo','LCirNodo *',int(p['value']));self.local('nuevo','NULL','LCirNodo *');self.emit(fn,'nuevo = lcir_crear_nodo');self.emit(fn,'if (nuevo == NULL)',condition=True);self.emit(fn,'return false;',after='if (nuevo == NULL)',returning=True,return_value=False)
  elif op=='insertar_padre':
   fn='sublista_insertar_padre_final';self.push(fn,{'lista':'&lista','valor_padre':int(p['parent'])},{'lista':'Nodo **','valor_padre':'int'});self.emit(fn,fn+'(',event='call')
   for name in ['nuevo','actual']:self.local(name,'indeterminado; no leer','Nodo *');self.emit(fn,'Nodo *'+name+';')
   self.emit(fn,'if (lista == NULL)',condition=False);self.emit(fn,'nuevo = crear_padre',event='call');self.allocator('crear_padre','nuevo','Nodo *',int(p['parent']));self.local('nuevo','NULL','Nodo *');self.emit(fn,'nuevo = crear_padre');self.emit(fn,'if (nuevo == NULL)',condition=True);self.emit(fn,'return NULL;',after='if (nuevo == NULL)',returning=True,return_value='NULL')
  else:
   outer='sublista_insertar_hijo';finder='sublista_buscar_padre';inner='sublista_insertar_hijo_final';parent=int(p['parent']);child=int(p['child'])
   self.push(outer,{'lista':self.head,'valor_padre':parent,'valor_hijo':child},{'lista':'Nodo *','valor_padre':'int','valor_hijo':'int'});self.emit(outer,outer+'(',event='call');self.local('padre','indeterminado; no leer','Nodo *');self.emit(outer,'sublista_buscar_padre(lista',event='call');self.push(finder,{'lista':self.head,'valor_padre':parent},{'lista':'Nodo *','valor_padre':'int'});self.emit(finder,finder+'(',event='call');actual=self.head;self.local('actual',actual,'Nodo *');self.emit(finder,'Nodo *actual = lista;')
   while actual!='NULL':
    node=next(n for n in self.heap if n['id']==actual);self.emit(finder,'while (actual != NULL)',condition=True);found=node['value']==parent;self.emit(finder,'if (actual->nro == valor_padre)',condition=found)
    if found:break
    actual=node['next'];self.local('actual',actual,'Nodo *');self.emit(finder,'actual = actual->sgte;')
   if actual=='NULL':raise ValueError('El padre validado no está en el estado previo.')
   self.emit(finder,'return actual;',returning=True,return_value=actual);self.local('padre',actual,'Nodo *');self.emit(outer,'sublista_buscar_padre(lista');self.emit(outer,'if (padre == NULL)',condition=False);self.emit(outer,'return sublista_insertar_hijo_final',event='call');self.push(inner,{'padre':actual,'valor_hijo':child},{'padre':'Nodo *','valor_hijo':'int'});self.emit(inner,inner+'(',event='call')
   for name in ['nuevo','actual']:self.local(name,'indeterminado; no leer','Sublista *');self.emit(inner,'Sublista *'+name+';')
   self.emit(inner,'if (padre == NULL)',condition=False);self.emit(inner,'nuevo = crear_hijo',event='call');self.allocator('crear_hijo','nuevo','Sublista *',child);self.local('nuevo','NULL','Sublista *');self.emit(inner,'nuevo = crear_hijo');self.emit(inner,'if (nuevo == NULL)',condition=True);self.emit(inner,'return false;',after='if (nuevo == NULL)',returning=True,return_value=False);self.emit(outer,'return sublista_insertar_hijo_final',returning=True,return_value=False)
  self.steps[0]['phase']='start';self.steps[-1]['phase']='end';self.steps[-1]['state_after']=deepcopy(self.before)
  return {'structure_id':f,'operation_name':op,'payload':deepcopy(p),'source_code':self.source,'code_title':'Codigo C','success':False,'message':MESSAGE,'mutates':False,'steps':self.steps,'final_state':deepcopy(self.before),'pedagogy_schema_version':SEQUENTIAL_FRAME_SCHEMA_VERSION,'pedagogy_schema':sequential_frame_schema()}

def build_allocation_failure_trace(*, structure_id: str, operation_name: str, payload: dict, didactic_data: dict, before_state: dict) -> dict:
 from app.services.execution_trace_service import ExecutionTraceService
 source,title=ExecutionTraceService._get_operation_source(didactic_data,operation_name)
 kwargs={'payload':payload,'source_code':source,'code_title':title,'before_state':before_state,'after_state':before_state,'success':False,'message':MESSAGE,'allocation_failure':True}
 if structure_id=='stack':
  from app.domain.sequential.stack_push_instruction import build_stack_push_trace
  trace=build_stack_push_trace(**kwargs)
 elif structure_id=='queue':
  from app.domain.sequential.queue_enqueue_instruction import build_queue_enqueue_trace
  trace=build_queue_enqueue_trace(**kwargs)
 elif structure_id=='priority_queue':
  from app.domain.sequential.priority_queue_enqueue_instruction import build_priority_queue_enqueue_trace
  trace=build_priority_queue_enqueue_trace(**kwargs)
 else:
  if structure_id=='linked_list':
   text=CCodeService._safe_read(CCodeService._DOCS_TADS_C/'tad_lista.c');helper=CCodeService._extract_function_with_comment(text,'CrearNodoLista');source+='\n\n'+helper
  trace=_NullPath(structure_id,operation_name,payload,source,before_state).build()
 # Public console contains reached printf chunks, not an exception or cumulative future output.
 for step in trace['steps']:
  literal=ExecutionTraceService._printf_literal(step['line_text'],preserve_trailing_newlines=True) if step['line_text'].strip().startswith('printf(') else None
  step['console']=[literal] if literal is not None else []
 trace.update(success=False,mutates=False,message=MESSAGE,error=deepcopy(ERROR),allocation_failure=True,execution_started=True,c_return={'type':'void','value':None} if structure_id in {'stack','queue','linked_list'} else {'type':'Nodo *','value':'NULL'} if structure_id=='sublist' and operation_name=='insertar_padre' else {'type':'bool','value':False})
 from app.services.trace.engine import TraceEngine
 TraceEngine.validate_legacy_trace_readonly(trace)
 return trace
