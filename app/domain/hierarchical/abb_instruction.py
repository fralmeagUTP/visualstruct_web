"""ABB insertion instruction states: allocations, recursive invocations and caller.

Models the downloaded abb_insertar C. The displayed caller is a small C adapter
for the root assignment performed by the application, not a new TAD operation.
"""
from copy import deepcopy
import re
from .pedagogy import build_hierarchical_frame,validate_hierarchical_frame

def build_abb_insert_trace(trace,before_state,after_state):
 value=int(trace['payload']['value']);source=trace['source_code'].rstrip()
 source+='\n\n/* Llamador equivalente a la asignacion de raiz de la aplicacion; no es otro metodo del TAD. */\nvoid ejecutar_insercion(ABBNodo **arbol) {\n    *arbol = abb_insertar(*arbol, '+str(value)+');\n}\n'
 lines=source.splitlines();heap=[];frames=[];history=[];caller=None;head='NULL';returned=None;steps=[]
 def load(node):
  if not isinstance(node,dict):return 'NULL'
  identity='N'+str(len(heap)+1);item={'id':identity,'value':node['value'],'left':'NULL','right':'NULL','status':'linked'};heap.append(item);item['left']=load(node.get('left'));item['right']=load(node.get('right'));return identity
 head=load(before_state.get('root'))
 def byid(identity):return next(n for n in heap if n['id']==identity)
 def subtree(identity):
  if identity=='NULL':return None
  item=byid(identity);assert item['value']!='sin inicializar' and item['left']!='sin inicializar' and item['right']!='sin inicializar'
  return {'value':item['value'],'left':subtree(item['left']),'right':subtree(item['right'])}
 def snapshot():
  state=deepcopy(before_state);root=subtree(head);reached=set()
  def walk(identity):
   if identity=='NULL':return
   reached.add(identity);item=byid(identity);walk(item['left']);walk(item['right'])
  walk(head)
  for item in heap:item['status']='linked' if item['id'] in reached else 'detached'
  def height(n):return 0 if n is None else 1+max(height(n['left']),height(n['right']))
  def traversal(n,mode):
   if n is None:return []
   left=traversal(n['left'],mode);right=traversal(n['right'],mode);v=[n['value']]
   return v+left+right if mode=='preorden' else left+v+right if mode=='inorden' else left+right+v
  state.update(abb_insert_model=True,head=head,root=root,heap_nodes=deepcopy(heap),tree_frames=deepcopy(frames),caller_frame=deepcopy(caller),returned=returned,size=len(reached),empty=not reached,height=height(root),traversals={mode:traversal(root,mode) for mode in ['inorden','preorden','postorden']})
  return state
 def index(text):
  return next(i for i,line in enumerate(lines) if line.strip()==text)
 def objects(state):return [{'id':n['id'],'address':n['id'],'symbolic_identity':True,'value':n['value'],'left':n['left'],'right':n['right'],'status':n['status'],'allocated':True,'freed':False} for n in state['heap_nodes']]
 def annotate(step,old,new,event):
  frame=build_hierarchical_frame(structure_id='abb',operation_name='insertar',payload=trace['payload'],step=step,source_lines=lines,success=True)
  phase=event['phase'];concept={'condition':'compare','allocation':'allocation','call':'descend','enter':'descend','return':'return','link':'link','caller':'link','caller_enter':'invariant','caller_exit':'return'}.get(phase,'assignment')
  frame['concept']=concept;frame['case']=phase;frame['phase']={'id':'insertar-'+phase,'label':phase.title(),'goal':step['line_text']};frame['condition']=None
  previous={(f['id'],name):v for f in old['tree_frames'] for name,v in {**f['parameters'],**f['locals']}.items()}
  current={(f['id'],name):v for f in new['tree_frames'] for name,v in {**f['parameters'],**f['locals']}.items()}
  variables=[]
  for invocation in history:
   for name in dict.fromkeys([*invocation['parameters'],*invocation['locals']]):
    key=(invocation['id'],name);a=previous.get(key,'fuera de ámbito');b=current.get(key,'fuera de ámbito')
    # No future declaration: a variable appears only after its actual introduction.
    if key not in previous and key not in current:continue
    variables.append({'name':name,'scope':invocation['function']+'#'+invocation['id'],'frame_id':invocation['id'],'type':'int' if name=='valor' else 'ABBNodo *','previous':a,'value':b,'changed':a!=b,'meaning':'Parametro/local del ambito '+invocation['id']+'; identidad simbolica de reserva para punteros.'})
  if old['caller_frame'] or new['caller_frame']:
   variables.insert(0,{'name':'arbol','scope':'ejecutar_insercion','frame_id':'caller','type':'ABBNodo **','previous':'&raiz' if old['caller_frame'] else 'fuera de ámbito','value':'&raiz' if new['caller_frame'] else 'fuera de ámbito','changed':bool(old['caller_frame'])!=bool(new['caller_frame']),'meaning':'Direccion de la raiz del llamador; *arbol='+new['head']})
  frame['variables']=variables
  shown=old['tree_frames'] if phase=='return' else new['tree_frames'];frame['call_stack']=[]
  if old['caller_frame'] or new['caller_frame']:frame['call_stack'].append({'function':'ejecutar_insercion','frame_id':'caller','depth':-1,'parameters':{'arbol':'&raiz'},'local_root':new['head'],'local_root_address':new['head'],'return':None,'continuation':'asignar la raiz solo al completar abb_insertar'})
  for f in shown:
   frame['call_stack'].append({'function':f['function'],'frame_id':f['id'],'depth':f['depth'],'parameters':deepcopy(f['parameters']),'locals':deepcopy(f['locals']),'local_root':f['parameters']['nodo'],'local_root_address':f['parameters']['nodo'],'return':event.get('return') if phase=='return' and f['id']==event['frame_id'] else None,'continuation':'el retorno aun no escribe el enlace del llamador' if phase=='return' else 'la invocacion conserva su propio nodo/valor/nuevo'})
  oldobj=objects(old);newobj=objects(new);oldids={n['id'] for n in oldobj};frame['memory']={'event':concept if concept in {'allocation','link'} else 'none','objects_before':oldobj,'objects_after':newobj,'allocated_objects':[n for n in newobj if n['id'] not in oldids],'freed_objects':[],'dangling_references':[],'stable_addresses':True,'symbolic_identities':True}
  if phase=='condition':
   expr=step['line_text'];active=old['tree_frames'][-1];pointer=active['parameters']['nodo'];expr=re.sub(r'\bvalor\b(?!\s*;)',str(value),expr) if 'nodo->valor' not in expr else expr.replace('valor <',str(value)+' <').replace('valor >',str(value)+' >').replace('nodo->valor',str(byid(pointer)['value']))
   expr=re.sub(r'\bnodo\b',pointer,expr);expr=re.sub(r'\bnuevo\b',str(active['locals'].get('nuevo','sin inicializar')),expr)
   frame['condition']={'source':step['line_text'].strip(),'substituted':expr.strip(),'result':event['condition'],'consequence':'cuerpo' if event['condition'] else 'salida/else'};frame['executed_branch']='cuerpo' if event['condition'] else 'salida/else'
  text={'caller_enter':'Entra al llamador equivalente: arbol apunta a la variable raiz; todavia no llama al TAD.','call':'Inicia la llamada. La asignacion de su retorno queda pendiente; no publica un enlace ni cambia la raiz.','enter':'Entra a una nueva invocacion recursiva con sus propios parametros. Las anteriores conservan sus ambitos suspendidos.','condition':'Evalua la condicion una vez con los parametros y alias de esta invocacion; no cambia la estructura.','allocation':'malloc reserva un nodo de identidad estable. valor, izquierdo y derecho siguen sin inicializar; la raiz no incorpora esta reserva.','assignment':'Inicializa solo los campos escritos por esta instruccion; el nodo permanece desconectado.','return':'Retorna el puntero a la misma reserva y termina este ambito. El llamador aun debe asignar el resultado; no se libera memoria.','link':'La llamada recursiva ya retorno: ahora escribe el enlace izquierdo o derecho de este nodo, conservando todas las identidades.','caller':'La llamada exterior ya retorno: esta asignacion del llamador publica la raiz. No atribuirla a malloc ni a la inicializacion de campos.','caller_exit':'Termina el ambito del llamador; las reservas del arbol siguen vivas.'}[phase]
  frame['narration']={level:text for level in ['basic','intermediate','advanced']};frame['return_propagation']={'active':phase in {'return','link','caller'},'value':event.get('return',new['returned']),'reconnects_subtree':phase in {'link','caller'}};frame['state_before']=deepcopy(old);frame['state_after']=deepcopy(new);frame['memory_state']=deepcopy(new);frame['instruction_event']=deepcopy(event)
  frame['invariant'].update(explanation='Orden del arbol alcanzable; reservas sin publicar se muestran separadas. Las identidades no dependen del valor. malloc no inicializa campos y return no libera.',holds=True,symbol='✓')
  validate_hierarchical_frame(frame,source_code=source);return frame
 def emit(text,phase,mutate=None,condition=None,result=None):
  old=snapshot();owner=frames[-1]['id'] if frames else 'caller'
  if mutate:mutate()
  new=snapshot();event={'phase':phase,'frame_id':owner,'condition':condition,'return':result}
  idx=index(text);step={'step_index':len(steps),'line_index':idx,'line_text':lines[idx],'event_type':'line','delay_ms':170,'console':[],'state_snapshot':old,'state_after':new,'debug':{'path_keys':[str(byid(f['parameters']['nodo'])['value']) for f in frames if f['parameters']['nodo']!='NULL'],'path_index':len(frames)-1,'stage':phase}}
  if phase=='condition':step['condition_result']=condition
  step['pedagogy']=annotate(step,old,new,event);steps.append(step)
 def rec(identity):
  f={'id':'F'+str(len(history)+1),'function':'abb_insertar','depth':len(frames),'parameters':{'nodo':identity,'valor':value},'locals':{}};history.append(f)
  emit(next(line.strip() for line in lines if re.match(r'ABBNodo\s*\*\s*abb_insertar\(',line.strip())),'enter',lambda:frames.append(f))
  emit('if (nodo == NULL) {','condition',condition=identity=='NULL')
  if identity=='NULL':
   allocated='N'+str(len(heap)+1)
   def allocate():heap.append({'id':allocated,'value':'sin inicializar','left':'sin inicializar','right':'sin inicializar','status':'detached'});f['locals']['nuevo']=allocated
   emit('ABBNodo* nuevo = malloc(sizeof *nuevo);','allocation',allocate)
   emit('if (nuevo == NULL) {','condition',condition=False)
   emit('nuevo->valor = valor;','assignment',lambda:byid(allocated).update(value=value))
   emit('nuevo->izquierdo = nuevo->derecho = NULL;','assignment',lambda:byid(allocated).update(left='NULL',right='NULL'))
   pointer=allocated;text='return nuevo;'
  else:
   node=byid(identity);emit('if (valor < nodo->valor)','condition',condition=value<node['value'])
   side='left' if value<node['value'] else 'right' if value>node['value'] else None
   if side!='left':emit('else if (valor > nodo->valor)','condition',condition=side=='right')
   if side:
    text='nodo->'+('izquierdo' if side=='left' else 'derecho')+' = abb_insertar(nodo->'+('izquierdo' if side=='left' else 'derecho')+', valor);'
    emit(text,'call');child=rec(node[side]);emit(text,'link',lambda:node.update({side:child}),result=child)
   pointer=identity;text='return nodo;'
  def leave():
   nonlocal returned
   frames.pop();returned=pointer
  emit(text,'return',leave,result=pointer);return pointer
 def enter_caller():
  nonlocal caller
  caller={'function':'ejecutar_insercion','parameters':{'arbol':'&raiz'}}
 emit('void ejecutar_insercion(ABBNodo **arbol) {','caller_enter',enter_caller)
 call='*arbol = abb_insertar(*arbol, '+str(value)+');';emit(call,'call');result=rec(head)
 def publish():
  nonlocal head
  head=result
 emit(call,'caller',publish,result=result)
 def leave_caller():
  nonlocal caller
  caller=None
 # There are other closing braces in C; use the caller's physical closing line.
 old=snapshot();leave_caller();new=snapshot();last={'step_index':len(steps),'line_index':len(lines)-1,'line_text':lines[-1],'event_type':'line','delay_ms':170,'console':[],'state_snapshot':old,'state_after':deepcopy(after_state),'debug':{'stage':'caller_exit'}}
 last['pedagogy']=annotate(last,old,new,{'phase':'caller_exit','frame_id':'caller','condition':None,'return':result});last['pedagogy']['state_after']=deepcopy(after_state);steps.append(last)
 initial=deepcopy(steps[0]['pedagogy']);initial['variables']=[];initial['call_stack']=[];initial['condition']=None;initial['memory_state']=deepcopy(steps[0]['state_snapshot']);initial['state_after']=deepcopy(steps[0]['state_snapshot']);initial['memory']['allocated_objects']=[];initial['phase']['label']='Estado inicial';initial['narration']={level:'Ninguna instruccion ejecutada; raiz y reservas iniciales, sin ambitos futuros.' for level in ['basic','intermediate','advanced']};steps[0]['pedagogy']['initial_frame']=initial
 trace.update(source_code=source,steps=steps);return trace
