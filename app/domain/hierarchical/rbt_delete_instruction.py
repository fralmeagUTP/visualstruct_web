"""Deletion instruction model; lifetime-safe symbolic identities and scoped C effects."""
from copy import deepcopy
import re
from .pedagogy import build_hierarchical_frame,validate_hierarchical_frame
UNINIT="sin inicializar"

def build_rbt_delete_trace(trace,before_state,after_state):
    value=int(trace['payload']['value']);root_ref='&raiz'
    source=trace['source_code'].rstrip()+'\n\n/**\n * @brief Invoca el TAD void con la raiz prestada, sin convertir retorno en exito.\n * @param arbol Referencia escribible prestada a la raiz propiedad del caller.\n * @note La preparacion del estado previo y la liberacion final son externas a esta traza.\n * El TAD libera solo z; el llamador conserva propiedad de las reservas restantes.\n */\nvoid ejecutar_eliminacion(RBT *arbol) {\n    rbt_eliminar(arbol, '+str(value)+');\n}\n'
    lines=source.splitlines();ranges={}
    names=['colorOf','transplantar','minimo','arreglarEliminacion','rbt_rotar_dcha','rbt_rotar_izda','rbt_eliminar','ejecutar_eliminacion']
    for fn in names:
        start=next(i for i,l in enumerate(lines) if re.match(r'^(?:static\s+)?(?:void|RBT|char)\s+'+fn+r'\(.*\)\s*\{',l.strip()));depth=0
        for end in range(start,len(lines)):
            depth+=lines[end].count('{')-lines[end].count('}')
            if depth==0:break
        ranges[fn]=(start,end)
    heap=[];retired=[];frames=[];history=[];steps=[];caller=None;head='NULL';stdout='';returned=None
    def load(n,parent='NULL'):
        if n is None:return 'NULL'
        ident='N'+str(len(heap)+1);item={'id':ident,'value':n['value'],'left':'NULL','right':'NULL','parent':parent,'color':n['color'],'initialized':31,'status':'linked'};heap.append(item);item['left']=load(n['left'],ident);item['right']=load(n['right'],ident);return ident
    head=load(before_state.get('root'))
    def node(i):return next(n for n in heap if n['id']==i)
    def snapshot():
        reached=set();alive={n['id'] for n in heap}
        def project(i):
            if i not in alive or i in reached:return None
            reached.add(i);n=node(i)
            if n['initialized']!=31:return None
            return {'value':n['value'],'color':n['color'],'left':project(n['left']),'right':project(n['right'])}
        root=project(head)
        for n in heap:n['status']='linked' if n['id'] in reached else 'detached'
        def height(n):return 0 if n is None else 1+max(height(n['left']),height(n['right']))
        active=deepcopy(frames)
        for f in active:
            for section in ['parameters','locals']:
                for key,v in f[section].items():
                    if isinstance(v,str) and re.fullmatch(r'N\d+',v) and v not in alive:f[section][key]=v+' [valor indeterminado; identidad historica]'
        s=deepcopy(before_state);s.update(abb_read_model=True,rbt_read_model=True,rbt_delete_model=True,head=head,root=root,size=len(reached),reachable_count=len(reached),heap_count=len(heap),height=height(root),empty=head=='NULL',heap_nodes=deepcopy(heap),tree_frames=active,freed_nodes=deepcopy(retired),caller_frame=deepcopy(caller),console_stdout=stdout,returned=returned,validation=None,traversals={},transient_graph=True,live_visual_projection=True)
        return s
    def index(fn,text,k=0):
        a,z=ranges[fn]
        if isinstance(text,int):return text
        if text=='}':return z
        compact=lambda s:re.sub(r'\s+','',s)
        hits=[i for i in range(a,z+1) if compact(text) in compact(lines[i])]
        return hits[k]
    def vartype(name):return 'int' if name in ['key','es_izq'] else 'char' if name=='y_color_original' else 'RBT *' if name in ['arbol','r','root'] else 'RBT'
    def emit(text,phase,change=None,condition=None,expression=None,result=None,k=0):
        old=snapshot();f=frames[-1] if frames else None;fn=f['function'] if f else 'ejecutar_eliminacion';owner=f['id'] if f else 'caller'
        if change:change()
        new=snapshot()
        if phase=='enter':f=frames[-1];fn=f['function'];owner=f['id']
        ix=index(fn,text,k);step={'step_index':len(steps),'line_index':ix,'line_text':lines[ix],'event_type':'line','delay_ms':170,'console':[result] if phase=='printf' else [],'state_snapshot':old,'state_after':new,'debug':{'stage':phase}}
        if condition is not None:step['condition_result']=bool(condition)
        ped=build_hierarchical_frame(structure_id='red_black',operation_name='eliminar',payload=trace['payload'],step=step,source_lines=lines,success=True)
        added=[n for n in new['heap_nodes'] if n['id'] not in {q['id'] for q in old['heap_nodes']}]
        ped.update(concept='allocation' if added else 'output' if phase=='printf' else 'compare' if condition is not None else 'return' if phase in ['return','caller'] else 'descend' if phase in ['enter','call'] else 'assignment',case=phase,phase={'id':'eliminar-'+phase,'label':phase.title(),'goal':lines[ix] if isinstance(text,int) else text},condition=None)
        if condition is not None:ped['condition']={'source':expression or text,'substituted':expression or text,'result':bool(condition),'consequence':'Operando alcanzado por C; el cortocircuito omite los siguientes cuando corresponde.'};ped['executed_branch']='verdadero' if condition else 'falso'
        prev={(f['id'],n):v for f in old['tree_frames'] for n,v in {**f['parameters'],**f['locals']}.items()};now={(f['id'],n):v for f in new['tree_frames'] for n,v in {**f['parameters'],**f['locals']}.items()};variables=[]
        for f in history:
            for n in dict.fromkeys([name for owner,name in [*prev,*now] if owner==f['id']]):
                key=(f['id'],n)
                if key not in prev and key not in now:continue
                a=prev.get(key,'fuera de ambito');b=now.get(key,'fuera de ambito');variables.append({'name':n,'scope':f['function']+'#'+f['id'],'frame_id':f['id'],'type':vartype(n),'previous':a,'value':b,'changed':a!=b,'meaning':'Local/parametro de esta invocacion. &raiz referencia almacenamiento del caller, no una reserva; N identifica un nodo estable. Un valor sin inicializar no se lee.'})
        if old['caller_frame'] or new['caller_frame']:variables.insert(0,{'name':'arbol','scope':'ejecutar_eliminacion','frame_id':'caller','type':'RBT *','previous':root_ref if old['caller_frame'] else 'fuera de ambito','value':root_ref if new['caller_frame'] else 'fuera de ambito','changed':bool(old['caller_frame'])!=bool(new['caller_frame']),'meaning':'Referencia prestada a la variable raiz; la propiedad no se transfiere y el retorno es void.'})
        ped['variables']=variables;shown=old['tree_frames'] if phase=='return' else new['tree_frames'];stack=[]
        if old['caller_frame'] or new['caller_frame']:stack.append({'function':'ejecutar_eliminacion','frame_id':'caller','depth':-1,'parameters':{'arbol':root_ref},'locals':{},'local_root':new['head'],'local_root_address':new['head'],'return':'void' if phase=='caller' else None,'continuation':'Solo las escrituras C publican enlaces/raiz; no se publica un resultado void.'})
        for f in shown:stack.append({'function':f['function'],'frame_id':f['id'],'depth':f['depth'],'parameters':deepcopy(f['parameters']),'locals':deepcopy(f['locals']),'local_root':f['parameters'].get('n',f['parameters'].get('nodoRBT',new['head'])),'local_root_address':f['parameters'].get('n',f['parameters'].get('nodoRBT',new['head'])),'return':result if phase=='return' and f['id']==owner else None,'continuation':'La asignacion del caller sucede despues del retorno; cada alias pertenece a su propio ambito.'})
        for f in stack:f['scope_status']='terminado (contexto del retorno)' if (phase=='return' and f['frame_id']==owner) or (phase=='caller' and f['frame_id']=='caller') else 'activo' if f['frame_id']==(new['tree_frames'][-1]['id'] if new['tree_frames'] else 'caller') else 'suspendido'
        ped['call_stack']=stack
        def objects(st):return [{**n,'address':n['id'],'symbolic_identity':True,'allocated':True,'freed':False} for n in st['heap_nodes']]
        freed=[n for n in objects(old) if n['id'] not in {q['id'] for q in new['heap_nodes']}]
        unusable=[{'frame':f['id'],'name':name,'identity':v.split(' ')[0],'usable':False,'historical_identity':True} for f in new['tree_frames'] for name,v in {**f['parameters'],**f['locals']}.items() if isinstance(v,str) and 'valor indeterminado' in v]
        if freed:ped['concept']='free'
        ped['memory']={'event':'free' if freed else 'allocation' if added else 'none','objects_before':objects(old),'objects_after':objects(new),'allocated_objects':[{**n,'address':n['id'],'symbolic_identity':True,'allocated':True,'freed':False} for n in added],'freed_objects':freed,'dangling_references':[],'unusable_reference_records':unusable,'retired_objects':deepcopy(retired),'records_are_not_pointer_values':True,'stable_addresses':True,'symbolic_identities':True}
        descriptions={'selection':'Evalua solo el selector alcanzado de ?:; la otra alternativa no se lee ni llama.','free':'free termina solo la reserva original z. Sus datos son registros historicos; aliases terminados no se leen ni se convierten en NULL. El char guardado sigue valido.','scope_exit':'Termina el bloque del ciclo: los locales de esa iteracion salen de ambito; los parametros conservan sus asignaciones.','break':'Sale del ciclo sin fabricar otra iteracion o escritura.','caller_enter':'Comienza el caller equivalente sobre el estado previo; no repite la preparacion.','enter':'Entra un ambito con parametros propios, sin futuros locales.','call':'El caller queda suspendido; el inicializador declarado sigue sin valor hasta retornar.','local':'Completa la asignacion del local, sin cambiar el nodo apuntado.','declaration':'Comienza el ambito del local sin inicializar; no se lee ni se inventa un alias.','operand':'Evalua solo este operando alcanzado; NULL y cortocircuito impiden accesos omitidos.','condition':'Termina la condicion con operandos actuales; no escribe enlaces ni colores.','allocate':'Completa malloc y asigna actual. Si falla no hay nueva reserva; si obtiene memoria, sus campos siguen sin inicializar.','initialize':'Escribe solo los campos de esta instruccion antes de publicar el nodo.','link':'Escribe este enlace o raiz; una rotacion parcial puede tener fragmentos/ciclos transitorios. La vista no los convierte en NULL ni certifica un arbol final.','recolor':'Escribe solo el color indicado en la reserva real; las rotaciones no recolorean por si solas.','resume':'Retoma el caller despues del retorno void, sin otra mutacion.','return':'Completa este retorno y termina el ambito; los alias retornados son prestados y la asignacion del caller sigue pendiente.','printf':'Agrega la confirmacion C exactamente despues de reparar, no antes.','caller':'Termina el caller void; solo el TAD libero z. La limpieza del arbol restante ocurre fuera de esta traza, sin publicar un supuesto retorno de exito.'}
        ped['narration']={level:descriptions[phase] for level in ['basic','intermediate','advanced']};ped['return_propagation']={'active':phase in ['return','caller'],'value':result,'reconnects_subtree':False};ped['instruction_event']={'phase':phase,'frame_id':owner,'condition':condition,'expression':expression,'return':result if phase=='return' else None,'statement':lines[ix] if isinstance(text,int) else text};ped['state_before']=deepcopy(old);ped['state_after']=deepcopy(new);ped['memory_state']=deepcopy(new)
        ped['invariant'].update(name='Estado parcial de eliminacion',holds=None,symbol='?',explanation='Reservas/alias estables y escrituras C observadas. No certifica orden, padres, rojo-rojo ni altura negra de un grafo transitorio. Validar sigue siendo una consulta limitada.')
        validate_hierarchical_frame(ped,source_code=source);step['pedagogy']=ped;steps.append(step)
    def enter(fn,pars):
        f={'id':'F'+str(len(history)+1),'function':fn,'depth':len(frames),'parameters':pars,'locals':{}};history.append(f);emit(lines[ranges[fn][0]].strip(),'enter',lambda:frames.append(f));return f
    def leave(text='}',result='void',k=0):
        def done():
            nonlocal returned
            frames.pop();returned=result
        emit(text,'return',done,result=result,k=k);return result
    def put(f,text,name,val,phase='local',k=0):emit(text,phase,lambda:(f['parameters'] if name in f['parameters'] else f['locals']).__setitem__(name,val),k=k)
    def fields(text,i,flags=0,k=0,**values):
        def done():node(i).update(values);node(i)['initialized']|=flags
        emit(text,'initialize' if flags else 'recolor' if 'color' in values else 'link',done,k=k)
    def sethead(i):
        nonlocal head
        head=i
    def substitute(expr):
        f=frames[-1];vals={**f['parameters'],**f['locals']}
        def token(m):
            parts=m.group().split('->');name=parts[0]
            if name=='ROJO':return "'r'"
            if name=='NEGRO':return "'n'"
            if name not in vals:return m.group()
            v=vals[name]
            if name=='y_color_original':return repr(v)
            for field in parts[1:]:
                if v in ['NULL',UNINIT] or v not in {n['id'] for n in heap}:return '(acceso no evaluado)'
                v=node(v)[{'nro':'value','rbt_color':'color','padre':'parent','izq':'left','der':'right'}[field]]
            return "'r'" if v=='RED' else "'n'" if v=='BLACK' else str(v)
        rendered=re.sub(r'\b[A-Za-z_]\w*(?:->(?:nro|rbt_color|padre|izq|der))*\b',token,expr)
        # colorOf was evaluated by the reached getter, not re-invoked for explanation.
        return re.sub(r'colorOf\([^)]*\)',lambda m:repr(returned) if returned in ['r','n'] else m.group(),rendered)
    def condition(text,terms,join=None,k=0):
        results=[];rendered=[]
        for expr,getter in terms:
            v=bool(getter());results.append(v);rendered.append(substitute(expr))
            if join:
                emit(text,'operand',condition=v,expression=expr,k=k)
                steps[-1]['pedagogy']['condition']['substituted']=rendered[-1]
            if join=='&&' and not v or join=='||' and v:break
        result=all(results) if join=='&&' else any(results) if join=='||' else results[0]
        emit(text,'condition',condition=result,expression=(' '+join+' ').join(expr for expr,_ in terms) if join else terms[0][0],k=k)
        for expr,_ in terms[len(results):]:rendered.append('(omitido por cortocircuito: '+expr+')')
        steps[-1]['pedagogy']['condition']['substituted']=(' '+join+' ').join(rendered) if join else rendered[0]
        return result
    def call(text,fn,args,name=None,frame=None,declare=False,k=0):
        emit(text,'call',(lambda:frame['locals'].__setitem__(name,UNINIT)) if declare else None,k=k);v=fn(*args)
        if name:put(frame,text,name,v,k=k)
        else:emit(text,'resume',k=k)
        return v
    def rotate(fn,i):
        f=enter(fn,{'r':root_ref,'nodoRBT':i});side='left' if fn=='rbt_rotar_dcha' else 'right';other='right' if side=='left' else 'left';field='izq' if side=='left' else 'der';opposite='der' if side=='left' else 'izq'
        text=f'if (r == NULL || nodoRBT == NULL || nodoRBT->{field} == NULL) {{'
        if condition(text,[('r == NULL',lambda:root_ref=='NULL'),('nodoRBT == NULL',lambda:i=='NULL'),(f'nodoRBT->{field} == NULL',lambda:node(i)[side]=='NULL')],'||'):return leave('return;')
        parent=node(i)['parent'];b=node(i)[side];c=node(b)[other]
        for text,name,val in [('RBT padre = nodoRBT->padre;','padre',parent),('RBT A = nodoRBT;','A',i),(f'RBT B = A->{field};','B',b),(f'RBT C = B->{opposite};','C',c)]:put(f,text,name,val)
        if condition('if (padre != NULL) {',[('padre != NULL',lambda:parent!='NULL')]):
            right=condition('if (padre->der == A)',[('padre->der == A',lambda:node(parent)['right']==i)]);fields('padre->'+('der' if right else 'izq')+' = B;',parent,**{'right' if right else 'left':b})
        else:emit('*r = B;','link',lambda:sethead(b))
        fields('A->'+field+' = C;',i,**{side:c});fields('B->'+opposite+' = A;',b,**{other:i});fields('A->padre = B;',i,parent=b)
        if condition('if (C)',[('C',lambda:c!='NULL')]):fields('C->padre = A;',c,parent=i)
        fields('B->padre = padre;',b,parent=parent);return leave()
    def select(text,expr,getter):
        value=bool(getter());emit(text,'selection',condition=value,expression=expr)
        steps[-1]['pedagogy']['condition']['substituted']=substitute(expr)
        return value
    def color(n):
        enter('colorOf',{'n':n});text='return (n == NULL) ? NEGRO : n->rbt_color;'
        result='n' if select(text,'n == NULL',lambda:n=='NULL') else 'r' if node(n)['color']=='RED' else 'n'
        return leave(text,result)
    def transplant(u,v):
        enter('transplantar',{'root':root_ref,'u':u,'v':v});p=node(u)['parent']
        if condition('if (u->padre == NULL)',[('u->padre == NULL',lambda:p=='NULL')]):emit('*root = v;','link',lambda:sethead(v))
        elif condition('else if (u == u->padre->izq)',[('u == u->padre->izq',lambda:u==node(p)['left'])]):fields('u->padre->izq = v;',p,left=v)
        else:fields('u->padre->der = v;',p,right=v)
        if condition('if (v)',[('v',lambda:v!='NULL')]):fields('v->padre = u->padre;',v,parent=p)
        return leave()
    def minimum(n):
        f=enter('minimo',{'n':n})
        while condition('while (n && n->izq)',[('n',lambda:f['parameters']['n']!='NULL'),('n->izq',lambda:node(f['parameters']['n'])['left']!='NULL')],'&&'):
            put(f,'n = n->izq;','n',node(f['parameters']['n'])['left'])
        return leave('return n;',f['parameters']['n'])
    def fixup(x,parent):
        f=enter('arreglarEliminacion',{'root':root_ref,'x':x,'x_parent':parent})
        a,z=ranges['arreglarEliminacion'];split=next(i for i in range(a,z) if lines[i].strip()=='if (es_izq) {');mirror=next(i for i in range(split,z) if 'Lado derecho: casos espejo' in lines[i])
        def site(text,left=None,k=0):
            lo,hi=(a,z) if left is None else (split,mirror-1) if left else (mirror,z-3)
            compact=lambda s:re.sub(r'\s+','',s)
            return [i for i in range(lo,hi+1) if compact(text) in compact(lines[i])][k]
        def val(name):return f['parameters'].get(name,f['locals'].get(name))
        while condition('while (x != *root && colorOf(x) == NEGRO)',[('x != *root',lambda:val('x')!=head),('colorOf(x) == NEGRO',lambda:color(val('x'))=='n')],'&&'):
            if condition('if (x_parent == NULL)',[('x_parent == NULL',lambda:val('x_parent')=='NULL')]):emit('break;','break');break
            text='int es_izq = (x == (x_parent ? x_parent->izq : NULL));';put(f,text,'es_izq',UNINIT,'declaration')
            child=node(val('x_parent'))['left'] if select(text,'x_parent',lambda:val('x_parent')!='NULL') else 'NULL';put(f,text,'es_izq',int(val('x')==child))
            text='RBT w = x_parent ? (es_izq ? x_parent->der : x_parent->izq) : NULL;';put(f,text,'w',UNINIT,'declaration')
            if select(text,'x_parent',lambda:val('x_parent')!='NULL'):
                w=node(val('x_parent'))['right' if select(text,'es_izq',lambda:bool(val('es_izq'))) else 'left']
            else:w='NULL'
            put(f,text,'w',w)
            for name,side,cfield in [('w_izq','left','izq'),('w_der','right','der')]:
                text=f'RBT {name} = w ? w->{cfield} : NULL;';put(f,text,name,UNINIT,'declaration');v=node(val('w'))[side] if select(text,'w',lambda:val('w')!='NULL') else 'NULL';put(f,text,name,v)
            left=condition('if (es_izq)',[('es_izq',lambda:bool(val('es_izq')))])
            near,far=('w_izq','w_der') if left else ('w_der','w_izq');other='der' if left else 'izq';side='right' if left else 'left';rot='rbt_rotar_izda' if left else 'rbt_rotar_dcha';reverse='rbt_rotar_dcha' if left else 'rbt_rotar_izda'
            def refresh(initial=False):
                text='w = x_parent->der;' if left and initial else f'w = x_parent ? x_parent->{other} : NULL;';ix=site(text,left,0 if initial else 1 if not left else 0)
                v=node(val('x_parent'))[side] if left and initial else node(val('x_parent'))[side] if select(ix,'x_parent',lambda:val('x_parent')!='NULL') else 'NULL';put(f,ix,'w',v)
                for name,cfield,nside in [('w_izq','izq','left'),('w_der','der','right')]:
                    v=node(val('w'))[nside] if select(ix,'w',lambda:val('w')!='NULL') else 'NULL';put(f,ix,name,v)
            if condition(site('if (colorOf(w) == ROJO)',left),[('colorOf(w) == ROJO',lambda:color(val('w'))=='r')]):
                fields(site('w->rbt_color = NEGRO;',left),val('w'),color='BLACK');fields(site('x_parent->rbt_color = ROJO;',left),val('x_parent'),color='RED');call(site(rot+'(root, x_parent);',left,0),rotate,[rot,val('x_parent')]);refresh(True)
            if condition(site(f'if (colorOf({near}) == NEGRO && colorOf({far}) == NEGRO)',left),[(f'colorOf({near}) == NEGRO',lambda:color(val(near))=='n'),(f'colorOf({far}) == NEGRO',lambda:color(val(far))=='n')],'&&'):
                if condition(site('if (w)',left,0),[('w',lambda:val('w')!='NULL')]):fields(site('w->rbt_color = ROJO;',left,0),val('w'),color='RED')
                put(f,site('x = x_parent;',left),'x',val('x_parent'));ix=site('x_parent = x ? x->padre : NULL;',left);v=node(val('x'))['parent'] if select(ix,'x',lambda:val('x')!='NULL') else 'NULL';put(f,ix,'x_parent',v)
            else:
                if condition(site(f'if (colorOf({far}) == NEGRO)',left),[(f'colorOf({far}) == NEGRO',lambda:color(val(far))=='n')]):
                    if condition(site(f'if ({near})',left,0),[(near,lambda:val(near)!='NULL')]):fields(site(f'{near}->rbt_color = NEGRO;',left,0),val(near),color='BLACK')
                    if condition(site('if (w)',left,1),[('w',lambda:val('w')!='NULL')]):fields(site('w->rbt_color = ROJO;',left,1),val('w'),color='RED');call(site(reverse+'(root, w);',left),rotate,[reverse,val('w')])
                    refresh(False)
                if condition(site('if (w)',left,2),[('w',lambda:val('w')!='NULL')]):fields(site('w->rbt_color = colorOf(x_parent);',left),val('w'),color='RED' if color(val('x_parent'))=='r' else 'BLACK')
                fields(site('x_parent->rbt_color = NEGRO;',left),val('x_parent'),color='BLACK')
                if condition(site(f'if ({far})',left,0),[(far,lambda:val(far)!='NULL')]):fields(site(f'{far}->rbt_color = NEGRO;',left,0),val(far),color='BLACK')
                call(site(rot+'(root, x_parent);',left,1),rotate,[rot,val('x_parent')]);put(f,site('x = *root;',left),'x',head)
            emit(z-2,'scope_exit',lambda:f['locals'].clear())
        if condition('if (x)',[('x',lambda:val('x')!='NULL')]):fields('x->rbt_color = NEGRO;',val('x'),color='BLACK')
        return leave()
    def delete():
        f=enter('rbt_eliminar',{'arbol':root_ref,'key':value});put(f,'RBT z = *arbol;','z',head)
        def v(name):return f['locals'][name]
        while condition('while (z != NULL && z->nro != key)',[('z != NULL',lambda:v('z')!='NULL'),('z->nro != key',lambda:node(v('z'))['value']!=value)],'&&'):
            if condition('if (key < z->nro)',[('key < z->nro',lambda:value<node(v('z'))['value'])]):put(f,'z = z->izq;','z',node(v('z'))['left'])
            else:put(f,'z = z->der;','z',node(v('z'))['right'])
        if condition('if (z == NULL)',[('z == NULL',lambda:v('z')=='NULL')]):return leave('return;')
        put(f,'RBT y = z;','y',v('z'));put(f,'char y_color_original = y->rbt_color;','y_color_original','r' if node(v('y'))['color']=='RED' else 'n');put(f,'RBT x = NULL;','x','NULL');put(f,'RBT x_parent = NULL;','x_parent','NULL')
        if condition('if (z->izq == NULL)',[('z->izq == NULL',lambda:node(v('z'))['left']=='NULL')]):
            put(f,'x = z->der;','x',node(v('z'))['right']);put(f,'x_parent = z->padre;','x_parent',node(v('z'))['parent'],k=0);call('transplantar(arbol, z, z->der);',transplant,[v('z'),node(v('z'))['right']])
        elif condition('else if (z->der == NULL)',[('z->der == NULL',lambda:node(v('z'))['right']=='NULL')]):
            put(f,'x = z->izq;','x',node(v('z'))['left']);put(f,'x_parent = z->padre;','x_parent',node(v('z'))['parent'],k=1);call('transplantar(arbol, z, z->izq);',transplant,[v('z'),node(v('z'))['left']])
        else:
            call('y = minimo(z->der);',minimum,[node(v('z'))['right']],'y',f);put(f,'y_color_original = y->rbt_color;','y_color_original','r' if node(v('y'))['color']=='RED' else 'n',k=1);put(f,'x = y->der;','x',node(v('y'))['right'])
            if condition('if (y->padre == z)',[('y->padre == z',lambda:node(v('y'))['parent']==v('z'))]):put(f,'x_parent = y;','x_parent',v('y'))
            else:
                call('transplantar(arbol, y, y->der);',transplant,[v('y'),node(v('y'))['right']]);put(f,'x_parent = y->padre;','x_parent',node(v('y'))['parent']);fields('y->der = z->der;',v('y'),right=node(v('z'))['right']);fields('y->der->padre = y;',node(v('y'))['right'],parent=v('y'))
            call('transplantar(arbol, z, y);',transplant,[v('z'),v('y')]);fields('y->izq = z->izq;',v('y'),left=node(v('z'))['left']);fields('y->izq->padre = y;',node(v('y'))['left'],parent=v('y'));fields('y->rbt_color = z->rbt_color;',v('y'),color=node(v('z'))['color'])
        def release():
            obj=node(v('z'));retired.append({**deepcopy(obj),'status':'freed','historical_identity':True,'contents_are_historical':True});heap.remove(obj)
        emit('free(z);','free',release)
        if condition('if (y_color_original == NEGRO)',[('y_color_original == NEGRO',lambda:v('y_color_original')=='n')]):call('arreglarEliminacion(arbol, x, x_parent);',fixup,[v('x'),v('x_parent')])
        if condition('if (*arbol)',[('*arbol',lambda:head!='NULL')]):fields('(*arbol)->rbt_color = NEGRO;',head,color='BLACK')
        return leave()
    def caller_enter():
        nonlocal caller
        caller={'function':'ejecutar_eliminacion','parameters':{'arbol':root_ref},'locals':{},'description':'RBT *arbol: &raiz; almacenamiento prestado, no reserva.'}
    emit('void ejecutar_eliminacion(RBT *arbol) {','caller_enter',caller_enter);delete()
    def caller_exit():
        nonlocal caller
        caller=None
    emit('}','caller',caller_exit,result='void');steps[-1]['state_after']=deepcopy(after_state);steps[-1]['pedagogy']['state_after']=deepcopy(after_state)
    first=steps[0]['pedagogy'];initial=deepcopy(first);initial.update(variables=[],call_stack=[],condition=None,state_before=deepcopy(steps[0]['state_snapshot']),state_after=deepcopy(steps[0]['state_snapshot']),memory_state=deepcopy(steps[0]['state_snapshot']));initial['phase']['label']='Estado inicial';initial['narration']={k:'Estado previo, sin parametros/locales futuros, sin free repetido ni printf.' for k in ['basic','intermediate','advanced']};first['initial_frame']=initial
    trace.update(source_code=source,steps=steps,console=[]);return trace
