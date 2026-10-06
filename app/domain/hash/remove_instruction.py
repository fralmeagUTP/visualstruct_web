"""Causal scoped interpreter of Hash th_eliminar and its th_indice call."""
from __future__ import annotations
from copy import deepcopy
from typing import Any
from app.adapters.base_adapter import BaseAdapter
from app.domain.hash.pedagogy import build_hash_frame, hash_frame_schema, HASH_LEARNING_CATALOG


def build_hash_remove_trace(*, operation_name: str, payload: dict[str, Any], source_code: str,
        code_title: str, before_state: dict[str, Any], after_state: dict[str, Any],
        success: bool, message: str, **_: Any) -> dict[str, Any]:
    """Represent unlink, object retirement and the later count write separately."""
    lines=source_code.replace('\r\n','\n').split('\n');steps=[];state=deepcopy(before_state)
    capacity=int(state['metadata']['capacity']);size=int(state['metadata']['size'])
    stack=[];variables={};comparisons=hash_calls=frees=0
    index=helper_index=actual=previous=raw=normalized=return_value=None
    found=removed=count_pending=False;retired_actual=None;examined=[]
    entries=[e for b in state.get('buckets',[]) for e in b.get('entries',[])]
    heap={e['address']:{'id':e['address'],'kind':'node','initialized_mask':7,'key':e['key'],
        'value':e['value'],'next':None if e.get('next') in (None,'NULL','') else e['next'],
        'alive':True,'published':True,'fields_valid':True} for e in entries}

    def local(scope: str,name: str,ctype: str,value: Any=None,initialized: bool=True) -> None:
        variables[f'{scope}.{name}']={'type':ctype,'initialized':initialized,'value':value if initialized else None,'valid':True}

    def retire(scope: str) -> None:
        for name in list(variables):
            if name.startswith(scope+'.'):del variables[name]
        stack.remove(scope)

    def source_line(token: str,function: str) -> int:
        last=token.startswith('@last:');token=token.removeprefix('@last:')
        start=next(i for i,row in enumerate(lines) if function+'(' in row.replace(' ','') and '{' in row)
        for i in (range(len(lines)-1,start-1,-1) if last else range(start,len(lines))):
            if ''.join(token.split()) in ''.join(lines[i].split()):return i
        raise ValueError(f'Missing remove source {function}: {token}')

    def refresh_state() -> None:
        buckets=state['buckets']
        for bucket in buckets:
            bucket['size']=len(bucket['entries']);bucket['collisions']=max(0,bucket['size']-1)
        lengths=[b['size'] for b in buckets];occupied=sum(bool(n) for n in lengths)
        state['metadata'].update({'size':size,'capacity':capacity,'load_factor':round(size/capacity,6) if capacity else 0,
            'collisions':sum(b['collisions'] for b in buckets),'occupied_buckets':occupied,
            'empty_buckets':max(0,capacity-occupied),'max_chain_length':max(lengths,default=0),
            'chain_lengths':lengths,'is_empty':size==0})

    def emit(token: str,source: str|None,function: str,condition: bool|None=None) -> None:
        row=source_line(source,function) if source else -1
        scopes=[{'function':s,'variables':{n.split('.',1)[1]:deepcopy(v) for n,v in variables.items() if n.startswith(s+'.')}} for s in stack]
        root={'capacity':capacity,'size':size,'bucket_pointer':'bucket-array' if capacity else None}
        debug={'token':token,'function':function,'call_stack':list(stack),'scopes':scopes,'variables':deepcopy(variables),
            'root_identity':'&tabla','root':root,'indice':index,'helper_indice':helper_index,'actual':actual,'anterior':previous,
            'retired_actual':retired_actual,'actual_valid':'th_eliminar.actual' in variables and variables['th_eliminar.actual']['valid'],'condition_result':condition,
            'return_status':return_value,'comparisons':comparisons,'hash_calls':hash_calls,'allocations':0,'frees':frees,
            'heap':deepcopy(list(heap.values())),'count_write_pending':count_pending,'removed':removed,
            'bucket_array':{'id':'bucket-array','element_type':'THNodo *','alive':capacity>0,
                'cells':[{'index':b['index'],'initialized':True,'value':b['entries'][0]['address'] if b['entries'] else None} for b in state['buckets']]},
            'identity_policy':'symbolic key identity within this operation; retired fields are historical snapshots'}
        previous_state=deepcopy(steps[-1]['state_after'] if steps else before_state)
        step={'step_index':len(steps),'line_index':row,'line_text':lines[row] if row>=0 else '',
            'event_type':token,'phase':'progress','delay_ms':170,'state_snapshot':previous_state,
            'state_after':deepcopy(state),'console':[],'debug':debug,
            'instruction_event':{'token':token,'function':function,'condition':condition}}
        frame=build_hash_frame(operation_name=operation_name,payload=payload,step=step,source_lines=lines,success=success)
        frame['source']['function']=function
        frame['variables']={n:v['value'] for n,v in variables.items()}
        frame['variables'].update({'tabla->capacidad':capacity,'tabla->cantidad':size,'retorno':return_value})
        frame['struct_fields']={'tabla':{'identity':'&tabla','capacidad':capacity,'cantidad':size}}
        frame['pointers']={'tabla':'&tabla' if stack else 'fuera de alcance',
            'actual':(retired_actual or actual or 'NULL') if 'th_eliminar.actual' in variables else 'fuera de alcance',
            'actual_status':('retirado: no utilizable; identidad simbólica histórica' if retired_actual else ('vivo' if actual else 'NULL')) if 'th_eliminar.actual' in variables else 'fuera de alcance',
            'anterior':(previous or 'NULL') if 'th_eliminar.anterior' in variables else 'fuera de alcance'}
        frame['condition']=None if condition is None else {'source':step['line_text'],'result':condition,'substituted':str(condition),'consequence':'Rama C observada.'}
        frame['hash'].update({'raw_remainder':raw,'normalized_index':normalized,
            'normalization_applied':raw is not None and raw<0 and normalized is not None,
            'expression':None if raw is None else f'{payload.get("key")} % {capacity} = {raw}',
            'normalization_expression':None if normalized is None else f'Indice calculado: {normalized}'})
        selected_before=next((b['entries'] for b in before_state['buckets'] if b['index']==normalized),[])
        selected_after=next((b['entries'] for b in state['buckets'] if b['index']==normalized),[])
        frame['chain'].update({'bucket':normalized,'before':deepcopy(selected_before),'after':deepcopy(selected_after),'examined':list(examined),'found':found,'match_position':comparisons-1 if found else None,
            'position_kind':'coincidencia observada' if found else 'aún no encontrado',
            'current_index':comparisons-1 if comparisons else None,'current_pointer':actual,'previous_pointer':previous})
        frame['distribution'].update({k:state['metadata'][k] for k in ('occupied_buckets','empty_buckets','chain_lengths','max_chain_length','load_factor','collisions')})
        frame['cost'].update({'comparisons':comparisons,'nodes_visited':comparisons,'hash_evaluations':hash_calls})
        frame['memory'].update({'variables':deepcopy(variables),'call_stack':list(stack),'scopes':scopes,
            'heap':deepcopy(list(heap.values())),'allocated':[],'freed':[{'address':n['id'],'key':n['historical_fields']['key'],'value':n['historical_fields']['value'],'bucket':index,'historical':True,'fields_valid':False} for n in heap.values() if not n['alive']],
            'allocation_attempted':False,'null_checked':token=='remove_guard','initialized_fields':[],
            'links_changed':token in {'bucket_link','previous_link'},'struct_fields':deepcopy(frame['struct_fields']),
            'count_write_pending':count_pending,'retired_pointer':retired_actual,'bucket_array':deepcopy(debug['bucket_array'])})
        frame['memory']['allocation_failed']=False
        if count_pending:
            frame['invariant'].update({'symbol':'⏳','name':'cantidad-- pendiente','evidence':f'Cantidad C={size}; nodos alcanzables={sum(len(b["entries"]) for b in state["buckets"])}. Unlink/free aún no ejecuta cantidad--.','status':'transient','holds':size==sum(len(b['entries']) for b in state['buckets'])+1})
        frame['narration']['advanced']=f'{function}: {token}; unlink, free y cantidad-- son instrucciones distintas.'
        if retired_actual:frame['narration']['advanced']+=' actual no se convierte a NULL en C; su valor no es utilizable tras free.'
        step['pedagogy']=frame;steps.append(step)

    try:
        key=BaseAdapter._require_int(payload,'key','clave');valid=-2147483648<=key<=2147483647
    except (KeyError,TypeError,ValueError):valid=False
    if not valid:emit('input_rejected',None,'public_validation')
    else:
        stack.append('th_eliminar');local('th_eliminar','tabla','TablaHash *','&tabla');local('th_eliminar','clave','int',key)
        emit('remove_entry','bool th_eliminar(','th_eliminar');invalid=capacity<=0
        emit('remove_guard','if (!tabla || !tabla->buckets','th_eliminar',invalid)
        if not invalid:
            local('th_eliminar','indice','int',initialized=False);emit('index_call','int indice = th_indice(','th_eliminar')
            stack.append('th_indice');local('th_indice','tabla','const TablaHash *','&tabla');local('th_indice','clave','int',key)
            emit('index_entry','int th_indice(','th_indice');emit('index_guard','if (!tabla || tabla->capacidad <= 0)','th_indice',False)
            raw=abs(key)%capacity*(-1 if key<0 else 1);helper_index=raw;local('th_indice','indice','int',raw)
            emit('raw_modulo','int indice = clave %','th_indice');emit('negative_modulo_guard','if (indice < 0)','th_indice',raw<0)
            if raw<0:helper_index+=capacity;local('th_indice','indice','int',helper_index);emit('normalize_modulo','indice += tabla->capacidad;','th_indice')
            normalized=helper_index;return_value=helper_index;retire('th_indice');emit('index_return','return indice;','th_indice')
            index=helper_index;helper_index=None;return_value=None;hash_calls+=1;local('th_eliminar','indice','int',index)
            emit('index_assigned','int indice = th_indice(','th_eliminar')
            bucket=next(b for b in state['buckets'] if b['index']==index);actual=bucket['entries'][0]['address'] if bucket['entries'] else None
            local('th_eliminar','actual','THNodo *',actual);emit('actual_init','THNodo *actual =','th_eliminar')
            local('th_eliminar','anterior','THNodo *',None);emit('previous_init','THNodo *anterior = NULL;','th_eliminar')
            while True:
                emit('search_test','while (actual != NULL)','th_eliminar',actual is not None)
                if actual is None:break
                node=heap[actual];comparisons+=1;examined.append(node['key']);found=node['key']==key
                emit('key_compare','if (actual->clave == clave)','th_eliminar',found)
                if found:
                    emit('previous_guard','if (anterior == NULL)','th_eliminar',previous is None)
                    if previous is not None:
                        heap[previous]['next']=node['next']
                        entry=next(e for e in bucket['entries'] if e['address']==previous);entry['next']=node['next'] or 'NULL'
                    bucket['entries']=[e for e in bucket['entries'] if e['address']!=actual]
                    node['published']=False;count_pending=True;refresh_state()
                    emit('bucket_link' if previous is None else 'previous_link',
                        'tabla->buckets[indice] = actual->siguiente;' if previous is None else 'anterior->siguiente = actual->siguiente;','th_eliminar')
                    node['alive']=False;node['fields_valid']=False;node['historical_initialized_mask']=node['initialized_mask'];node['initialized_mask']=0;node['historical_fields']={k:node[k] for k in ('key','value','next')}
                    for field in ('key','value','next'):node[field]=None
                    retired_actual=actual;actual=None;frees+=1;removed=True
                    variables['th_eliminar.actual'].update({'value':None,'initialized':False,'valid':False,'historical_identity':retired_actual,'reason':'valor indeterminado tras finalizar la vida del objeto'})
                    emit('node_free','free(actual);','th_eliminar')
                    size-=1;count_pending=False;refresh_state();emit('count_decrement','tabla->cantidad--;','th_eliminar');break
                previous=actual;local('th_eliminar','anterior','THNodo *',previous);emit('previous_assign','anterior = actual;','th_eliminar')
                actual=node['next'];local('th_eliminar','actual','THNodo *',actual);emit('actual_advance','actual = actual->siguiente;','th_eliminar')
        return_value=removed;retire('th_eliminar')
        emit('remove_return','return true;' if removed else ('if (!tabla || !tabla->buckets' if invalid else '@last:return false;'),'th_eliminar')
    steps[-1]['state_after']=deepcopy(after_state);steps[-1]['pedagogy']['state_after']=deepcopy(after_state)
    steps[0]['phase']='start';steps[-1]['phase']='end'
    return {'structure_id':'hash_table','operation_name':operation_name,'payload':deepcopy(payload),'success':success,
        'mutates':True,'message':message,'code_title':code_title,'source_code':source_code,'steps':steps,
        'final_state':deepcopy(after_state),'pedagogy_schema_version':1,'pedagogy_schema':hash_frame_schema(),
        'learning_profile':deepcopy(HASH_LEARNING_CATALOG),'instruction_scope':'th_eliminar/th_indice'}
