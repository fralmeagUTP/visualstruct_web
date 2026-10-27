"""Read-only Rojo-Negro queries: completed instruction boundaries and scoped calls.

Validar follows the exported native full validator, including black height and
parent identity. Native malformed-object projections are internal QA inputs.
"""
from copy import deepcopy
from .pedagogy import build_hierarchical_frame,validate_hierarchical_frame

def build_rbt_query_trace(trace,before_state,after_state,*,native_projection=None):
 op=trace['operation_name'];assert op in {'buscar','inorden','altura','validar'}
 source=trace['source_code'].rstrip();fn='rbt_'+op
 ret={'buscar':'RBT','inorden':'void','altura':'int','validar':'int'}[op]
 value=int(trace['payload'].get('value',trace['payload'].get('valor',0)))
 signature=f'{ret} ejecutar_{op}(RBT raiz'+(', int dato' if op=='buscar' else '')+') {'
 call=fn+'(raiz'+(', dato' if op=='buscar' else '')+');'
 source+='\n\n/**\n * @brief Llamador equivalente de la consulta; no modifica ni libera el arbol.\n * @param raiz Raiz prestada; NULL admitido.\n'+(' * @param dato Entero buscado.\n' if op=='buscar' else '')+(' * @return Alias prestado o NULL.\n' if op=='buscar' else ' * @return Entero calculado por la consulta.\n' if ret=='int' else '')+' */\n'+signature+'\n    '+('return ' if ret!='void' else '')+call+'\n}\n'
 lines=source.splitlines();heap=[];frames=[];history=[];steps=[];stdout='';wrapper=None;returned=None
 def load(n,parent='NULL'):
  if n is None:return 'NULL'
  ident='N'+str(len(heap)+1);h={'id':ident,'value':n['value'],'left':'NULL','right':'NULL','parent':parent,'color':n['color'],'status':'linked'};heap.append(h);h['left']=load(n['left'],ident);h['right']=load(n['right'],ident);return ident
 if native_projection is None:
  head=load(before_state.get('root'))
 else:
  assert op=='validar'
  heap=deepcopy(native_projection['heap_nodes']);head=native_projection['head']
 def node(i):return next(n for n in heap if n['id']==i)
 def snapshot():
  s=deepcopy(before_state);s.update(rbt_validation_graph=native_projection is not None and native_projection.get("graph_view",True),abb_read_model=True,rbt_read_model=True,rbt_validate_model=op=='validar',head=head,heap_nodes=deepcopy(heap),tree_frames=deepcopy(frames),caller_frame=None,console_stdout=stdout,wrapper_result=wrapper,returned=returned,validation=None if wrapper is None or op!='validar' else bool(wrapper),validator_contract='cinco reglas RN, orden estricto, altura negra y enlaces por identidad');return s
 def idx(text,function=None):
  f=function or (frames[-1]['function'] if frames else 'ejecutar_'+op)
  start=next(i for i,l in enumerate(lines) if '(' in l and l.strip().startswith(('static int '+f+'(','int '+f+'(','void '+f+'(','RBT '+f+'(')))
  end=next((i for i in range(start+1,len(lines)) if lines[i].startswith('}')),len(lines)-1)
  return next(i for i in range(start,end+1) if text in lines[i].strip())
 def emit(text,phase,mutate=None,result=None,condition=None,expression=None,function=None,fragment='',line_override=None):
  old=snapshot();owner=frames[-1]['id'] if frames else None;index=idx(text,function) if line_override is None else line_override
  if mutate:mutate()
  new=snapshot();owner=new['tree_frames'][-1]['id'] if phase=='enter' else owner
  step={'step_index':len(steps),'line_index':index,'line_text':lines[index],'event_type':'line','delay_ms':170,'console':[fragment] if fragment else [],'state_snapshot':old,'state_after':new,'debug':{'stage':phase}}
  if condition is not None:step['condition_result']=condition
  ped=build_hierarchical_frame(structure_id='red_black',operation_name=op,payload=trace['payload'],step=step,source_lines=lines,success=True)
  ped.update(concept='return' if phase=='return' else 'output' if phase=='printf' else 'compare' if condition is not None else 'descend',case=phase,phase={'id':op+'-'+phase,'label':phase,'goal':lines[index]},condition=None,executed_branch=None)
  if condition is not None:
   ped['condition']={'source':text,'substituted':expression,'result':condition,'consequence':'Solo la rama/operando registrado se ejecuta; los operandos omitidos no tienen efecto.'};ped['executed_branch']='verdadero' if condition else 'falso'
  prev={(f['id'],k):v for f in old['tree_frames'] for k,v in {**f['parameters'],**f['locals']}.items()};now={(f['id'],k):v for f in new['tree_frames'] for k,v in {**f['parameters'],**f['locals']}.items()}
  numeric={'dato','tieneMin','minimo','tieneMax','maximo','altIzq','altDer','bhIzq','bhDer'}
  ped['variables']=[{'name':k,'scope':f['function']+'#'+f['id'],'frame_id':f['id'],'type':'int' if k in numeric else 'RBT','previous':prev.get((f['id'],k),'fuera de ámbito'),'value':now.get((f['id'],k),'fuera de ámbito'),'changed':prev.get((f['id'],k))!=now.get((f['id'],k)),'meaning':'Parametro/local de esta invocacion; alias prestado por valor o entero, no reserva nueva.'} for f in history for k in [*f['parameters'],*f['locals']] if (f['id'],k) in prev or (f['id'],k) in now]
  shown=old['tree_frames'] if phase=='return' else new['tree_frames'];ped['call_stack']=[{'function':f['function'],'frame_id':f['id'],'depth':f['depth'],'parameters':deepcopy(f['parameters']),'locals':deepcopy(f['locals']),'local_root':next((v for k,v in f['parameters'].items() if k not in numeric),'NULL'),'local_root_address':next((v for k,v in f['parameters'].items() if k not in numeric),'NULL'),'return':result if phase=='return' and f['id']==owner else None,'scope_status':'terminado (contexto del retorno)' if phase=='return' and f['id']==owner else 'activo' if new['tree_frames'] and f['id']==new['tree_frames'][-1]['id'] else 'suspendido','continuation':'Retorno de consulta: no reconecta enlaces ni libera reservas.'} for f in shown]
  objs=[{'id':n['id'],'address':n['id'],'symbolic_identity':True,'value':n['value'],'left':n['left'],'right':n['right'],'parent':n['parent'],'color':n['color'],'allocated':True,'freed':False} for n in heap]
  ped['memory']={'event':'none','objects_before':deepcopy(objs),'objects_after':deepcopy(objs),'allocated_objects':[],'freed_objects':[],'dangling_references':[],'stable_addresses':True,'symbolic_identities':True}
  descriptions={'enter':'Entra este ambito con sus parametros propios; los llamadores quedan suspendidos.','call':'Comienza la llamada indicada. El resultado aun no existe; un local declarador permanece sin inicializar.','resume':'La llamada termino; retoma el llamador sin mutar enlaces ni repetir printf.','assignment':'Completa la asignacion con el valor disponible; no cambia la reserva apuntada.','condition':'Evalua solo los operandos alcanzados por C. NULL y cortocircuito impiden accesos omitidos.','operand':'El operando izquierdo de && termino. Si es cero se omite la llamada derecha; no es una variable C nueva.','printf':'printf agrega exactamente los caracteres de esta instruccion; no modifica el arbol.','return':'Termina solo este ambito y entrega void, entero o alias prestado. No reserva/libera ni reconecta enlaces.'}
  description=descriptions[phase]+(' Validar comprueba altura negra y enlaces nativos sin reparar.' if op=='validar' else '')
  ped['narration']={k:description for k in ['basic','intermediate','advanced']};ped['return_propagation']={'active':phase=='return','value':result,'reconnects_subtree':False};ped['state_before']=deepcopy(old);ped['state_after']=deepcopy(new);ped['memory_state']=deepcopy(new);ped['instruction_event']={'phase':phase,'frame_id':owner,'condition':condition,'return':result};ped['invariant'].update(explanation='Solo lectura: se conservan todas las reservas y enlaces; validez completa sólo al retornar el validador.',holds=None,symbol='?');validate_hierarchical_frame(ped,source_code=source);step['pedagogy']=ped;steps.append(step)
 def enter(function,parameters):
  f={'id':'F'+str(len(history)+1),'function':function,'depth':len(frames),'parameters':parameters,'locals':{}};history.append(f)
  emit(function+'(','enter',lambda:frames.append(f),function=function);return f
 def leave(text,result):
  function=frames[-1]['function']
  def done():
   nonlocal returned,wrapper
   frames.pop();returned=result
   if function=='ejecutar_'+op:wrapper=result
  emit(text,'return',done,result=result);return result
 def cond(text,result,expr):emit(text,'condition',condition=bool(result),expression=expr);return result
 def output(text,fragment):
  def done():
   nonlocal stdout
   stdout+=fragment
  emit(text,'printf',done,fragment=fragment)
 def rec_inorder(i):
  enter('rbt_inorden',{'nodo':i})
  if cond('if (nodo == NULL)',i=='NULL',i+' == NULL'):return leave('return;','void')
  for field,side in [('izq','left'),('der','right')]:
   text='rbt_inorden(nodo->'+field+');';emit(text,'call');rec_inorder(node(i)[side]);emit(text,'resume')
   if side=='left':output('printf(',str(node(i)['value'])+' ')
  return leave('}','void')
 def rec_height(i):
  f=enter('rbt_altura',{'nodo':i})
  if cond('if (nodo == NULL)',i=='NULL',i+' == NULL'):return leave('return 0;',0)
  for name,field,side in [('altIzq','izq','left'),('altDer','der','right')]:
   text='int '+name+' = rbt_altura(nodo->'+field+');';emit(text,'call',lambda:f['locals'].__setitem__(name,'sin inicializar'));v=rec_height(node(i)[side]);emit(text,'assignment',lambda:f['locals'].__setitem__(name,v))
  l,r=f['locals']['altIzq'],f['locals']['altDer'];text='return (altIzq > altDer ? altIzq : altDer) + 1;';cond(text,l>r,f'{l} > {r}');return leave(text,max(l,r)+1)
 def rec_black_height(i,parent,has_min,low,has_max,high):
  f=enter('rbt_validar_altura_negra',{'nodo':i,'padreEsperado':parent,'tieneMin':has_min,'minimo':low,'tieneMax':has_max,'maximo':high})
  if cond('if (nodo == NULL)',i=='NULL',i+' == NULL'):return leave('return 1;',1)
  n=node(i)
  if cond('if (nodo->padre',n['parent']!=parent,n['parent']+' != '+parent):return leave('if (nodo->padre',0)
  if cond('if (nodo->rbt_color !=',n['color'] not in ('RED','BLACK'),str(n['color'])+' != ROJO && '+str(n['color'])+' != NEGRO'):return leave('if (nodo->rbt_color !=',0)
  if cond('if (tieneMin',has_min and n['value']<=low,f'{has_min} && '+(f'{n["value"]} <= {low}' if has_min else '(limite omitido)')):return leave('if (tieneMin',0)
  if cond('if (tieneMax',has_max and n['value']>=high,f'{has_max} && '+(f'{n["value"]} >= {high}' if has_max else '(limite omitido)')):return leave('if (tieneMax',0)
  red=n['color']=='RED';left_red=n['left']!='NULL' and node(n['left'])['color']=='RED'
  bad=red and (left_red or (n['right']!='NULL' and node(n['right'])['color']=='RED'))
  expr=str(n['color'])+' == ROJO && '+('(hijos omitidos)' if not red else '(izquierdo rojo; derecho omitido)' if left_red else '(izquierdo no rojo; derecho evaluado)')
  if cond('if (nodo->rbt_color == ROJO',bad,expr):return leave('(nodo->der != NULL',0)
  text='int bhIzq = rbt_validar_altura_negra';emit(text,'call',lambda:f['locals'].__setitem__('bhIzq','sin inicializar'));l=rec_black_height(n['left'],i,has_min,low,1,n['value']);emit(text,'assignment',lambda:f['locals'].__setitem__('bhIzq',l))
  if cond('if (bhIzq == 0)',l==0,f'{l} == 0'):return leave('if (bhIzq == 0)',0)
  text='int bhDer = rbt_validar_altura_negra';emit(text,'call',lambda:f['locals'].__setitem__('bhDer','sin inicializar'));r=rec_black_height(n['right'],i,1,n['value'],has_max,high);emit(text,'assignment',lambda:f['locals'].__setitem__('bhDer',r))
  if cond('if (bhDer == 0',r==0 or l!=r,f'{r} == 0 || '+('(comparacion omitida)' if r==0 else f'{l} != {r}')):return leave('if (bhDer == 0',0)
  black=n['color']=='BLACK'
  if cond('if (nodo->rbt_color == NEGRO',black and l==2147483647,str(n['color'])+' == NEGRO && '+(f'{l} == INT_MAX' if black else '(altura omitida)')):return leave('if (nodo->rbt_color == NEGRO',0)
  text='return bhIzq +';cond(text,black,str(n['color'])+' == NEGRO');return leave(text,l+int(black))
 def rec_validate(i):
  enter('rbt_validar',{'raiz':i})
  if cond('if (raiz == NULL)',i=='NULL',i+' == NULL'):return leave('return 1;',1)
  if cond('if (raiz->rbt_color',node(i)['color']!='BLACK',str(node(i)['color'])+" != NEGRO ('n')"):return leave('if (raiz->rbt_color',0)
  text='return rbt_validar_altura_negra';emit(text,'call');v=rec_black_height(i,'NULL',0,0,0,0);emit(text,'resume');return leave(text,int(v!=0))
 def rec_search(i):
  f=enter('rbt_buscar',{'nodoRBT':i,'dato':value});emit('RBT actual = nodoRBT;','assignment',lambda:f['locals'].__setitem__('actual',i))
  if cond('if (nodoRBT == NULL)',i=='NULL',i+' == NULL'):
   output('printf("\\n\\tEl arbol esta vacio','\n\tEl arbol esta vacio\n\n');return leave('return NULL;','NULL')
  while cond('while (actual != NULL)',f['locals']['actual']!='NULL',f['locals']['actual']+' != NULL'):
   j=f['locals']['actual'];n=node(j)
   if cond('if (dato == actual->nro)',value==n['value'],f'{value} == {n["value"]}'):
    output('printf("\\n\\tEl numero %d existe',f'\n\tEl numero {value} existe en el arbol\n');return leave('return actual;',j)
   if cond('else if (dato < actual->nro)',value<n['value'],f'{value} < {n["value"]}'):emit('actual = actual->izq;','assignment',lambda:f['locals'].__setitem__('actual',n['left']))
   elif cond('else if (dato > actual->nro)',value>n['value'],f'{value} > {n["value"]}'):emit('actual = actual->der;','assignment',lambda:f['locals'].__setitem__('actual',n['right']))
  output('printf("\\n\\tEl numero %d NO existe',f'\n\tEl numero {value} NO existe en el arbol\n')
  # The final return NULL is distinct from the empty-tree return on the same text.
  def done():
   nonlocal returned
   frames.pop();returned='NULL'
  # Last occurrence, avoid highlighting the early return.
  emit('return NULL;','return',done,result='NULL',line_override=max(i for i,l in enumerate(lines) if l.strip()=='return NULL;'))
  return 'NULL'
 enter('ejecutar_'+op,{'raiz':head,**({'dato':value} if op=='buscar' else {})});text=('return ' if ret!='void' else '')+call;emit(text,'call')
 result={'inorden':rec_inorder,'altura':rec_height,'validar':rec_validate,'buscar':rec_search}[op](head);emit(text,'resume');leave(text if ret!='void' else '}',result)
 assert not frames
 steps[-1]['state_after']=deepcopy(after_state);steps[-1]['pedagogy']['state_after']=deepcopy(after_state)
 initial=deepcopy(steps[0]['pedagogy']);initial.update(variables=[],call_stack=[],condition=None,memory_state=deepcopy(steps[0]['state_snapshot']),state_after=deepcopy(steps[0]['state_snapshot']));initial['phase']['label']='Estado inicial';initial['narration']={k:'Ninguna instruccion ejecutada; consola vacia y parametros/resultados aun inexistentes.' for k in ['basic','intermediate','advanced']};steps[0]['pedagogy']['initial_frame']=initial
 trace.update(source_code=source,steps=steps);return trace
