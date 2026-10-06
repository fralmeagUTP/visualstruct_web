"""Scoped statement interpreter for the approved Hash lookup C functions."""
from __future__ import annotations
from copy import deepcopy
from typing import Any
from app.adapters.base_adapter import BaseAdapter
from app.domain.hash.pedagogy import build_hash_frame, hash_frame_schema, HASH_LEARNING_CATALOG


def build_hash_query_trace(*, operation_name: str, payload: dict[str, Any], source_code: str,
        code_title: str, before_state: dict[str, Any], after_state: dict[str, Any],
        success: bool, message: str, **_: Any) -> dict[str, Any]:
    """Execute th_buscar/th_contiene/th_indice, preserving output lifetimes."""
    operation=operation_name;lines=source_code.replace('\r\n','\n').split('\n');steps=[]
    capacity=int(before_state['metadata']['capacity']);size=int(before_state['metadata']['size'])
    stack=[];variables={};comparisons=hash_calls=0;index=None;actual=None;found=False
    output_initialized=operation=='get';output_value=123456789 if output_initialized else None
    output_alive=True;return_value=None;raw=None;normalized=None;storage_id='caller.output' if operation=='get' else 'th_contiene.dummy_valor'
    entries=[e for b in before_state.get('buckets',[]) for e in b.get('entries',[])]
    heap=[{'id':e['address'],'kind':'node','initialized_mask':7,'key':e['key'],'value':e['value'],'next':None if e.get('next') in (None,'NULL','') else e['next']} for e in entries]

    def local(scope: str,name: str,ctype: str,value: Any=None,initialized: bool=True) -> None:
        variables[f'{scope}.{name}']={'type':ctype,'initialized':initialized,'value':value if initialized else None}

    def retire(scope: str) -> None:
        for name in list(variables):
            if name.startswith(scope+'.'):del variables[name]
        stack.remove(scope)

    def line(token: str,function: str) -> int:
        last=token.startswith('@last:');token=token.removeprefix('@last:')
        start=next(i for i,row in enumerate(lines) if function+'(' in row.replace(' ','') and '{' in row)
        for i in (range(len(lines)-1,start-1,-1) if last else range(start,len(lines))):
            if ''.join(token.split()) in ''.join(lines[i].split()):return i
        raise ValueError(f'Missing query source {function}: {token}')

    def emit(token: str,source: str|None,function: str,condition: bool|None=None) -> None:
        row=line(source,function) if source else -1
        scopes=[{'function':scope,'variables':{name.split('.',1)[1]:deepcopy(item) for name,item in variables.items() if name.startswith(scope+'.')}} for scope in stack]
        debug={'token':token,'function':function,'call_stack':list(stack),'scopes':scopes,'variables':deepcopy(variables),
            'root_identity':'&tabla','root':{'capacity':capacity,'size':size,'bucket_pointer':'bucket-array' if capacity else None},
            'indice':index,'actual':actual,'condition_result':condition,'return_status':return_value,
            'comparisons':comparisons,'hash_calls':hash_calls,'heap':deepcopy(heap),
            'output':{'id':storage_id,'type':'int','initialized':output_initialized,'value':output_value if output_initialized else None,'alive':output_alive},
            'allocations':0,'frees':0,'identity_policy':'symbolic object identity within this operation'}
        previous=deepcopy(steps[-1]['state_after'] if steps else before_state)
        step={'step_index':len(steps),'line_index':row,'line_text':lines[row] if row>=0 else '',
            'event_type':token,'phase':'progress','delay_ms':170,'state_snapshot':previous,
            'state_after':deepcopy(before_state),'console':[],'debug':debug,
            'instruction_event':{'token':token,'function':function,'condition':condition}}
        frame=build_hash_frame(operation_name=operation,payload=payload,step=step,source_lines=lines,success=success)
        frame['source']['function']=function
        frame['variables']={name:item['value'] for name,item in variables.items()}
        frame['variables'].update({'tabla->capacidad':capacity,'tabla->cantidad':size,'retorno':return_value})
        frame['struct_fields']={'tabla':{'identity':'&tabla','capacidad':capacity,'cantidad':size}}
        frame['pointers']={'actual':actual or 'NULL','valor':('&'+storage_id) if 'th_buscar' in stack else 'fuera de alcance','tabla':'&tabla' if stack else 'fuera de alcance'}
        frame['condition']=None if condition is None else {'source':step['line_text'],'result':condition,'substituted':str(condition),'consequence':'Rama C ejecutada.'}
        frame['hash'].update({'raw_remainder':raw,'normalized_index':normalized,'normalization_applied':raw is not None and raw<0 and normalized is not None,'expression':None if raw is None else f'{payload.get("key")} % {capacity} = {raw}','normalization_expression':None if normalized is None else f'Indice calculado: {normalized}'})
        chain=next((b['entries'] for b in before_state.get('buckets',[]) if b['index']==normalized),[])
        frame['chain'].update({'examined':[e['key'] for e in chain[:comparisons]],'found':found,'match_position':comparisons-1 if found else None,'position_kind':'encontrado' if found else 'aún no encontrado','current_index':comparisons-1 if comparisons else None})
        frame['cost'].update({'comparisons':comparisons,'nodes_visited':comparisons,'hash_evaluations':hash_calls})
        frame['memory'].update({'variables':deepcopy(variables),'call_stack':list(stack),'scopes':scopes,'heap':deepcopy(heap),'allocated':[],'freed':[],'allocation_attempted':False,'null_checked':token=='search_guard','initialized_fields':[],'links_changed':False,'output':deepcopy(debug['output']),'struct_fields':deepcopy(frame['struct_fields'])})
        frame['narration']['advanced']=f'{function}: {token}; salida indeterminada sólo se lee si fue escrita.'
        step['pedagogy']=frame;steps.append(step)

    # Domain validation errors precede C; missing get key is a real C false return.
    try:
        key=BaseAdapter._require_int(payload,'key','clave');valid=-2147483648<=key<=2147483647
    except (KeyError,TypeError,ValueError):valid=False
    if not valid:
        emit('input_rejected',None,'public_validation')
    else:
        if operation=='contains':
            stack.append('th_contiene');local('th_contiene','tabla','const TablaHash *','&tabla');local('th_contiene','clave','int',key)
            emit('contains_entry','bool th_contiene(','th_contiene')
            local('th_contiene','dummy_valor','int',initialized=False)
            emit('dummy_declared','int dummy_valor;','th_contiene');emit('search_call','return th_buscar(','th_contiene')
        stack.append('th_buscar');local('th_buscar','tabla','const TablaHash *','&tabla');local('th_buscar','clave','int',key);local('th_buscar','valor','int *','&'+storage_id)
        emit('search_entry','bool th_buscar(','th_buscar')
        invalid=capacity<=0
        emit('search_guard','if (!tabla || !tabla->buckets','th_buscar',invalid)
        if not invalid:
            local('th_buscar','indice','int',initialized=False);emit('index_call','int indice = th_indice(','th_buscar')
            stack.append('th_indice');local('th_indice','tabla','const TablaHash *','&tabla');local('th_indice','clave','int',key)
            emit('index_entry','int th_indice(','th_indice');emit('index_guard','if (!tabla || tabla->capacidad <= 0)','th_indice',False)
            raw=abs(key)%capacity*(-1 if key<0 else 1);index=raw;local('th_indice','indice','int',raw)
            emit('raw_modulo','int indice = clave %','th_indice');emit('negative_modulo_guard','if (indice < 0)','th_indice',raw<0)
            if raw<0:index+=capacity;local('th_indice','indice','int',index);emit('normalize_modulo','indice += tabla->capacidad;','th_indice')
            normalized=index;return_value=index;retire('th_indice');emit('index_return','return indice;','th_indice')
            return_value=None;hash_calls+=1;local('th_buscar','indice','int',index);emit('index_assigned','int indice = th_indice(','th_buscar')
            chain=next((b['entries'] for b in before_state['buckets'] if b['index']==index),[])
            actual=chain[0]['address'] if chain else None;local('th_buscar','actual','THNodo *',actual)
            emit('actual_init','THNodo *actual =','th_buscar')
            while True:
                emit('search_test','while (actual != NULL)','th_buscar',actual is not None)
                if actual is None:break
                entry=next(e for e in chain if e['address']==actual);comparisons+=1;found=entry['key']==key
                emit('key_compare','if (actual->clave == clave)','th_buscar',found)
                if found:
                    output_initialized=True;output_value=entry['value']
                    if operation=='contains':local('th_contiene','dummy_valor','int',output_value)
                    emit('output_write','*valor = actual->valor;','th_buscar');break
                actual=None if entry.get('next') in (None,'NULL','') else entry['next'];local('th_buscar','actual','THNodo *',actual)
                emit('actual_advance','actual = actual->siguiente;','th_buscar')
        return_value=found;retire('th_buscar');actual=index=None
        emit('search_return','return true;' if found else ('if (!tabla || !tabla->buckets' if invalid else '@last:return false;'),'th_buscar')
        if operation=='contains':
            retire('th_contiene');output_alive=False;emit('contains_return','return th_buscar(','th_contiene')
    steps[-1]['state_after']=deepcopy(after_state);steps[-1]['pedagogy']['state_after']=deepcopy(after_state);steps[0]['phase']='start';steps[-1]['phase']='end'
    return {'structure_id':'hash_table','operation_name':operation,'payload':deepcopy(payload),'success':success,'mutates':False,'message':message,'code_title':code_title,'source_code':source_code,'steps':steps,'final_state':deepcopy(after_state),'pedagogy_schema_version':1,'pedagogy_schema':hash_frame_schema(),'learning_profile':deepcopy(HASH_LEARNING_CATALOG),'instruction_scope':'th_buscar/th_contiene/th_indice'}
