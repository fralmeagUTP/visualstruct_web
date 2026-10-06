"""Instruction traces of retained positional aliases and their existing C caller translation."""
from __future__ import annotations
from copy import deepcopy
from pathlib import Path
from typing import Any
import hashlib
import re

EXPECTED_BODIES = {'lista_insertar_elemento': '1ba61f785655a5190ad8fc74c93feae0033d9f05114c73f2b94f75ecb24a3afa', 'lista_eliminar_posicion': 'd71dda2acab92323aa094281ab1510edcc128eee98ab024701f832cfcf3fbb67', 'CrearNodoLista': 'b471603cf2f2e023bfbb6259e3720093707cbcdbf9ba44bb72ad2064e081e965'}
from .pedagogy import build_sequential_frame, validate_sequential_frame, sequential_frame_schema, SEQUENTIAL_FRAME_SCHEMA_VERSION

CALLER = '''/* Caller de compatibilidad: traduccion existente, no instruccion del TAD. */
void caller_compatibilidad(void) {
    Tlista *enlace = &lista;
    int posicion = 1;
    while (posicion < posicion_ui && *enlace != NULL) {
        enlace = &(*enlace)->sgte;
        posicion++;
    }
    if (posicion == posicion_ui) lista_insertar_elemento(enlace, valor_ui, 1);
    lista_insertar_elemento(&lista, valor_ui, posicion_ui);
    int eliminado;
    (void)lista_eliminar_posicion(&lista, posicion_ui - 1, &eliminado);
}'''

def build_hidden_positional_trace(*, operation_name: str, payload: dict[str, Any], source_code: str,
        code_title: str, before_state: dict[str, Any], after_state: dict[str, Any], success: bool,
        message: str) -> dict[str, Any]:
    """Trace only the three hidden aliases; preserve their accepted caller and API contracts."""
    text=(Path(__file__).resolve().parents[3]/'docs/tads_C/tad_lista.c').read_text(encoding='utf-8-sig').replace('\r\n','\n')
    def body(name: str) -> str:
        start=text.index(('int ' if name=='lista_eliminar_posicion' else 'Tlista ' if name=='CrearNodoLista' else 'void ')+name+'(')
        result=text[start:text.index('\n}',start)+2]
        tokens=' '.join(re.sub(r'/\*.*?\*/|//[^\n]*','',result,flags=re.S).split())
        if hashlib.sha256(tokens.encode()).hexdigest()!=EXPECTED_BODIES[name]:
            raise ValueError('C posicional cambiado: requiere revisar el modelo de instrucciones.')
        return result
    delete=operation_name=='eliminar_posicion'
    source=CALLER+'\n\n'+body('lista_eliminar_posicion' if delete else 'lista_insertar_elemento')
    if not delete: source+='\n\n'+body('CrearNodoLista')
    lines=source.split('\n');steps=[]
    trace={'structure_id':'linked_list','operation_name':operation_name,'payload':deepcopy(payload),
        'success':success,'mutates':True,'message':message,'source_code':source,'code_title':code_title,
        'steps':steps,'final_state':deepcopy(after_state),'hidden_positional_instruction_model':True,
        'pedagogy_schema_version':SEQUENTIAL_FRAME_SCHEMA_VERSION,'pedagogy_schema':sequential_frame_schema(),
        'caller_translation':'Existing positional compatibility caller; separate from unchanged TAD C.'}
    if not success:
        trace.update(execution_started=False,validation={'stage':'API','accepted':False,'message':message})
        return trace
    position=int(payload['position']);value=int(payload.get('value',0));relative=-1 if operation_name=='insertar_posicion' else int(payload.get('relative') or 0)
    nodes=[{'id':f'N{i+1}','value':n['value'],'next':f'N{i+2}' if i+1<len(before_state['items']) else 'NULL'} for i,n in enumerate(before_state['items'])]
    head=nodes[0]['id'] if nodes else 'NULL';variables={};freed=[];root_owner='&lista';output=None;console=[];calls=[]
    def get(n):return next(x for x in nodes if x['id']==n)
    def root():return head if root_owner=='&lista' else get(root_owner)['next']
    def publish(n):
        nonlocal head
        if root_owner=='&lista':head=n
        else:get(root_owner)['next']=n
    def snapshot():
        reachable=[];p=head
        while p!='NULL':reachable.append(p);p=get(p)['next']
        result=deepcopy(before_state)
        result.update(head=head,lista='&lista',node_ids=reachable,items=[{'value':get(n)['value']} for n in reachable],size=len(reachable),empty=not reachable,
            heap_nodes=[dict(n,status='linked' if n['id'] in reachable else 'temporary') for n in nodes],
            local_pointer_names=['q','t','actual','anterior','enlace'],**deepcopy(variables))
        result['delete_model' if delete else 'insert_model']=True
        if freed:result['freed_nodes']=deepcopy(freed)
        return result
    last=snapshot()
    def emit(function,token,event='statement',condition=None,ret=None):
        nonlocal last
        start=next(i for i,l in enumerate(lines) if (function+'(') in l and l.strip().startswith(('void ','int ','Tlista ')))
        index=(lines.index('}', start) if token == '}' else next(i for i in range(start,len(lines)) if token in lines[i]))
        after=snapshot();step={'step_index':len(steps),'line_index':index,'line_text':lines[index],'function_name':function,
            'event_type':event,'phase':'start' if event=='entry' else 'end' if event=='return' else 'progress','delay_ms':100,
            'condition_result':condition,'state_snapshot':deepcopy(last),'state_after':after,'console':deepcopy(console)}
        frame=build_sequential_frame(structure_id='linked_list',operation_name=operation_name,payload=payload,step=step,success=True)
        names=({'enlace','posicion'} if function=='caller_compatibilidad' else {'helper_q'} if function=='CrearNodoLista' else {'actual','anterior','indice'} if delete else {'q','t','i'})
        local={('q' if n=='helper_q' else n):v for n,v in variables.items() if n in names}
        shown_calls=([{'function':'caller_compatibilidad','parameters':{}}]+deepcopy(calls))
        if event=='return':shown_calls=[] if function=='caller_compatibilidad' else shown_calls[:-1]
        frame.update(memory_state=deepcopy(after),concept=event,variables=[{'name':n,'value':v,'type':'int' if isinstance(v,int) else 'Tlista','initialized':v!='sin inicializar','valid':not str(v).startswith('indeterminado'),'scope':function,'scope_state':'ended' if event=='return' else 'active'} for n,v in local.items()],
            heap_objects=deepcopy(after['heap_nodes']),call_stack=shown_calls,
            scopes=[{'id':function,'kind':'function','state':'ended' if event=='return' else 'active','variables':deepcopy(local)}],
            condition={'source':token,'result':condition} if condition is not None else None,
            heap_transition={'kind':'free' if token.startswith('free(') else 'allocate' if 'malloc(' in token else 'stable','before':deepcopy(last['heap_nodes']),'after':deepcopy(after['heap_nodes']),'freed':deepcopy(freed),'dangling_references':[]},
            hidden_alias_memory={'head':head,'root_owner':root_owner,'locals':deepcopy(variables),'output':output,'freed':deepcopy(freed),'return':ret})
        frame['source']['function']=function
        note='Caller de compatibilidad: '+token if function=='caller_compatibilidad' else token
        if event=='return':note+='; termina este ambito, sin liberar nodos adicionales.'
        frame['narration']={level:note for level in ['basic','intermediate','advanced']}
        validate_sequential_frame(frame,source_code=source);step['pedagogy']=frame
        step['debug']={'function':function,'locals':deepcopy(local),'head':head,'root_owner':root_owner,'output':output,'return':ret,'condition_result':condition}
        steps.append(step);last=deepcopy(after)
    caller='caller_compatibilidad';emit(caller,'void caller_', 'entry')
    if delete:
        emit(caller,'int eliminado;');emit(caller,'(void)lista_eliminar_posicion','call')
        fn='lista_eliminar_posicion';calls=[{'function':fn,'parameters':{'lista':'&lista','posicion':position-1,'valor':'&eliminado'}}];emit(fn,'int lista_', 'entry')
        variables.update(actual='sin inicializar',anterior='NULL');emit(fn,'Tlista actual, anterior')
        variables['indice']=0;emit(fn,'int indice')
        emit(fn,'if (lista == NULL','condition',False)
        variables['actual']=head;emit(fn,'actual = *lista;')
        while True:
            ok=variables['actual']!='NULL' and variables['indice']<position-1
            if ok:
                variables['anterior']=variables['actual'];variables['actual']=get(variables['actual'])['next'];variables['indice']+=1
            # This actual C source combines condition and three writes on one line.
            emit(fn,'while (actual != NULL','condition',ok)
            if not ok:break
        absent=variables['actual']=='NULL';emit(fn,'if (actual == NULL)','condition',absent)
        if absent:emit(fn,'if (actual == NULL)','return',ret=0)
        else:
            output=get(variables['actual'])['value'];emit(fn,'*valor = actual->nro;')
            athead=variables['anterior']=='NULL'
            if athead:head=get(variables['actual'])['next']
            else:get(variables['anterior'])['next']=get(variables['actual'])['next']
            emit(fn,'if (anterior == NULL)','condition',athead)
            freed.append(variables['actual']);nodes[:]=[n for n in nodes if n['id']!=variables['actual']];variables['actual']='indeterminado (liberado)';emit(fn,'free(actual);')
            emit(fn,'return 1;','return',ret=1)
    else:
        before=relative<0 and position!=1
        if before:
            variables['enlace']='&lista';emit(caller,'Tlista *enlace =')
            variables['posicion']=1;emit(caller,'int posicion =')
            while True:
                ok=variables['posicion']<position and root()!='NULL';emit(caller,'while (posicion <','condition',ok)
                if not ok:break
                root_owner=root();variables['enlace']='&'+root_owner+'->sgte';emit(caller,'enlace = &(*enlace)')
                variables['posicion']+=1;emit(caller,'posicion++;')
            call=variables['posicion']==position;emit(caller,'if (posicion ==','condition',call);pos=1
        else:call=True;pos=position;emit(caller,'lista_insertar_elemento(&lista','call')
        if call:
            fn='lista_insertar_elemento';calls=[{'function':fn,'parameters':{'lista':variables.get('enlace','&lista'),'valor':value,'pos':pos}}];emit(fn,'void lista_', 'entry')
            emit(fn,'if (lista == NULL','condition',False)
            helper='CrearNodoLista';calls.append({'function':helper,'parameters':{'valor':value}});emit(helper,'Tlista Crear','entry')
            q=f'N{len(nodes)+1}';nodes.append({'id':q,'value':'sin inicializar','next':'sin inicializar'});variables['helper_q']=q;emit(helper,'malloc(sizeof')
            emit(helper,'if (q == NULL)','condition',False)
            get(q)['value']=value;emit(helper,'q->nro = valor;')
            get(q)['next']='NULL';emit(helper,'q->sgte = NULL;')
            emit(helper,'return q;','return',ret=q);calls.pop();variables.pop('helper_q');variables['q']=q;emit(fn,'Tlista q = CrearNodoLista')
            emit(fn,'if (q == NULL)','condition',False);emit(fn,'if (pos == 1)','condition',pos==1)
            if pos==1:
                get(q)['next']=root();emit(fn,'q->sgte = *lista;');publish(q);emit(fn,'*lista = q;');emit(fn,'return;','return')
            else:
                variables['t']=root();emit(fn,'Tlista t = *lista;');variables['i']=1;emit(fn,'int i = 1;')
                while True:
                    ok=variables['t']!='NULL';emit(fn,'while (t != NULL)','condition',ok)
                    if not ok:break
                    eq=variables['i']==pos;emit(fn,'if (i == pos)','condition',eq)
                    if eq:
                        get(q)['next']=get(variables['t'])['next'];emit(fn,'q->sgte = t->sgte;');get(variables['t'])['next']=q;emit(fn,'t->sgte = q;');emit(fn,'return;','return');break
                    variables['t']=get(variables['t'])['next'];emit(fn,'t = t->sgte;');variables['i']+=1;emit(fn,'i++;')
                if not ok:
                    console.append('   Error...Posicion no encontrada..!');emit(fn,'printf(')
                    nodes[:]=[n for n in nodes if n['id']!=q];freed.append(q);variables['q']='indeterminado (liberado)';emit(fn,'free(q);')
    calls.clear();variables.clear();emit(caller,'}', 'return')
    if [n['value'] for n in last['items']]!=[n['value'] for n in after_state['items']]:
        raise ValueError('Caller posicional y resultado API difieren; no sintetizar estado final.')
    # Public final_state retains the API shape. The ended caller memory remains
    # in pedagogy.memory_state, so the renderer can still explain ownership.
    steps[-1]['state_after']=deepcopy(after_state)
    trace['execution_started']=True
    from app.services.trace.engine import TraceEngine
    TraceEngine.validate_legacy_trace(trace)
    return trace
