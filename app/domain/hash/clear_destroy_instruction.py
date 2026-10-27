"""Scoped causal model of existing C clear/destroy; never follows retired pointers."""
from copy import deepcopy
from app.domain.hash.pedagogy import build_hash_frame, hash_frame_schema, HASH_LEARNING_CATALOG


def build_hash_clear_destroy_trace(*,operation_name,payload,source_code,code_title,
        before_state,after_state,success,message,null_table=False,**_):
    """Distinguish free, indeterminate pointer storage, assignment and void return."""
    lines=source_code.replace('\r\n','\n').split('\n');steps=[];variables={};functions=[];blocks=[]
    cap=int(before_state['metadata']['capacity']);size=int(before_state['metadata']['size']);initial_cap=cap
    original=deepcopy(before_state.get('buckets',[]));array_alive=cap>0;array_freed=False;root_ptr_valid=True;root_ptr='bucket-array' if array_alive else None
    cells=[{'index':b['index'],'type':'THNodo *','initialized':True,'valid':True,'value':b['entries'][0]['address'] if b['entries'] else None} for b in original]
    heap={e['address']:{'id':e['address'],'type':'THNodo','kind':'node','alive':True,'fields_valid':True,'initialized_mask':7,
        'key':e['key'],'value':e['value'],'next':None if e.get('next') in (None,'NULL','') else e['next']} for b in original for e in b['entries']}
    i=None;actual=None;saved=None;visits=0;frees=0;iteration=0;count_pending=False
    def local(scope,name,ctype,value=None,initialized=True):
        variables[scope+'.'+name]={'type':ctype,'initialized':initialized,'valid':True,'value':value if initialized else None}
    def retire(scope):
        for n in list(variables):
            if n.startswith(scope+'.'):del variables[n]
        (blocks if scope in blocks else functions).remove(scope)
    def location(token,function):
        start=next(n for n,s in enumerate(lines) if function+'(' in s and '{' in s);depth=0;end=start
        for end in range(start,len(lines)):
            depth+=lines[end].count('{')-lines[end].count('}')
            if depth==0:break
        if token=='@end':return end
        if token=='@while_end':
            free=next(n for n in range(start,end+1) if 'free(actual);' in lines[n])
            return next(n for n in range(free+1,end+1) if lines[n]=='        }')
        if token=='@for_end':return next(n for n in range(start,end+1) if lines[n]=='    }' and n>next(j for j in range(start,end+1) if 'tabla->buckets[i] = NULL;' in lines[j]))
        return next(n for n in range(start,end+1) if token in lines[n])
    def visual_state():
        state=deepcopy(before_state);buckets=[];unknown=not root_ptr_valid
        if array_alive:
            for cell in cells:
                items=[]
                if cell['valid']:
                    ptr=cell['value']
                    while ptr is not None:
                        node=heap[ptr];assert node['alive'] and node['fields_valid'];items.append({'address':ptr,'key':node['key'],'value':node['value'],'next':node['next'] or 'NULL'});ptr=node['next']
                else:unknown=True
                buckets.append({'index':cell['index'],'initialized':cell['initialized'],'pointer_valid':cell['valid'],
                    'pointer_status':'indeterminate-after-free' if not cell['valid'] else ('live' if cell['value'] else 'NULL'),
                    'entries':items,'size':len(items) if cell['valid'] else None,'collisions':max(0,len(items)-1) if cell['valid'] else None})
        lengths=[b['size'] for b in buckets];occupied=None if unknown else sum(bool(n) for n in lengths)
        state['buckets']=buckets;state['metadata'].update({'capacity':cap,'size':size,'load_factor':round(size/cap,6) if cap else 0,
            'chain_lengths':lengths,'occupied_buckets':occupied,'empty_buckets':None if unknown else len(buckets)-(occupied or 0),
            'collisions':None if unknown else sum(b['collisions'] for b in buckets),
            'max_chain_length':None if unknown else max(lengths,default=0),'is_empty':size==0})
        state['lifecycle']={'root_bucket_pointer_valid':root_ptr_valid,'root_bucket_pointer':root_ptr if root_ptr_valid else None,
            'bucket_array_alive':array_alive,'chain_statistics_available':not unknown,'count_write_pending':count_pending,
            'root_stack_object_alive':not null_table,'unknown_is_not_NULL':unknown}
        return state
    def emit(event,token,function,condition=None):
        line=location(token,function);state=visual_state();scope_ids=functions+blocks
        scopes=[{'id':scope,'function':'th_vaciar' if scope in blocks else scope,'kind':'block' if scope in blocks else 'function',
            'variables':{n.split('.',1)[1]:deepcopy(v) for n,v in variables.items() if n.startswith(scope+'.')}} for scope in scope_ids]
        actual_var=variables.get('th_vaciar.actual');array={'id':'bucket-array','type':'THNodo **','element_type':'THNodo *','alive':array_alive,
            'allocated_capacity':initial_cap,'cells':deepcopy(cells),'fields_valid':array_alive}
        root={'identity':'&tabla','type':'TablaHash','alive':not null_table,'capacidad':cap,'cantidad':size,
            'buckets':{'type':'THNodo **','initialized':root_ptr_valid,'valid':root_ptr_valid,'value':root_ptr if root_ptr_valid else None,
                'historical_identity':'bucket-array' if array_freed else None}}
        debug={'token':event,'function':function,'variables':deepcopy(variables),'call_stack':list(functions),'scopes':scopes,
            'root':root,'bucket_array':array,'heap':deepcopy(list(heap.values())),'bucket_index':i,
            'actual':actual_var['value'] if actual_var and actual_var['valid'] else None,'actual_valid':actual_var['valid'] if actual_var else None,
            'nodes_visited':visits,'allocations':0,'frees':frees,'condition_result':condition,'count_write_pending':count_pending,
            'identity_policy':'operation-local symbols; historical snapshots are never usable C pointers'}
        previous=deepcopy(steps[-1]['state_after'] if steps else before_state)
        step={'step_index':len(steps),'line_index':line,'line_text':lines[line],'event_type':event,'phase':'progress','delay_ms':100,
            'state_snapshot':previous,'state_after':state,'console':[],'debug':debug,
            'instruction_event':{'token':event,'function':function,'condition':condition}}
        frame=build_hash_frame(operation_name=operation_name,payload=payload,step=step,source_lines=lines,success=success)
        frame['source']['function']=function;frame['variables']={n:v['value'] for n,v in variables.items()}
        frame['pointers'].update({'tabla':'NULL' if null_table else '&tabla','actual':'fuera de alcance' if actual_var is None else ('indeterminado; retirado' if not actual_var['valid'] else actual_var['value'] or 'NULL'),
            'buckets':'indeterminado; array retirado' if not root_ptr_valid else root_ptr or 'NULL',
            'siguiente':saved or 'NULL' if blocks else 'fuera de alcance'})
        frame['struct_fields']={'tabla':deepcopy(root)}
        frame['memory'].update({'variables':deepcopy(variables),'call_stack':list(functions),'scopes':scopes,'heap':deepcopy(list(heap.values())),
            'allocated':[],'allocation_attempted':False,'allocation_failed':False,'initialized_fields':[],'bucket_array':array,
            'bucket_array_freed':array_freed,'bucket_array_is_null':root_ptr_valid and root_ptr is None,'root_bucket_pointer_valid':root_ptr_valid,
            'root_stack_object_alive':not null_table,'count_write_pending':count_pending,'links_changed':event=='bucket_NULL_write',
            'freed':[{'address':n['id'],'key':n['historical_fields']['key'],'value':n['historical_fields']['value'],'historical':True,'fields_valid':False} for n in sorted(heap.values(),key=lambda h:h.get('freed_at',0),reverse=True) if not n['alive']],
            'struct_fields':deepcopy(frame['struct_fields'])})
        frame['cost'].update({'nodes_visited':visits,'hash_evaluations':0,'comparisons':0,'frees':frees})
        active_cell=cells[i] if i is not None and 0<=i<len(cells) else None
        frame['chain'].update({'bucket':i,'after':None if active_cell and not active_cell['valid'] else (state['buckets'][i]['entries'] if active_cell and array_alive else []),
            'position_kind':'slot indeterminado; no seguir chain' if active_cell and not active_cell['valid'] else 'recorrido C por actual/siguiente',
            'current_pointer':debug['actual']})
        frame['condition']=None if condition is None else {'source':lines[line],'result':condition,'substituted':str(condition),'consequence':'Rama C ejecutada.'}
        if count_pending or not state['lifecycle']['chain_statistics_available']:
            frame['invariant'].update({'symbol':'?','name':'transición de vida/cantidad','status':'transient','holds':None,
                'evidence':'Cantidad C sólo cambia en su store; slots/pointers retirados no se dereferencian para contar cadenas.'})
        frame['lifecycle']=deepcopy(state['lifecycle'])
        frame['narration']['advanced']=f'{function}: {event}; free, assignment, NULL y cantidad son instrucciones distintas. Pointers indeterminados no se leen.'
        step['pedagogy']=frame;steps.append(step)
    def clear_call():
        nonlocal actual,saved,i,visits,frees,iteration,size,count_pending
        functions.append('th_vaciar');local('th_vaciar','tabla','TablaHash *',None if null_table else '&tabla')
        emit('clear_entry','void th_vaciar(','th_vaciar');invalid=null_table or root_ptr is None
        emit('clear_guard','if (!tabla || !tabla->buckets)','th_vaciar',invalid)
        if not invalid:
            i=0;local('th_vaciar','i','int',i);emit('bucket_init','for (int i =','th_vaciar')
            while True:
                emit('bucket_guard','for (int i =','th_vaciar',i<cap)
                if i>=cap:break
                assert cells[i]['valid'];actual=cells[i]['value'];local('th_vaciar','actual','THNodo *',actual)
                emit('actual_declared','THNodo *actual =','th_vaciar')
                while True:
                    assert variables['th_vaciar.actual']['valid'];emit('chain_guard','while (actual != NULL)','th_vaciar',actual is not None)
                    if actual is None:break
                    iteration+=1;block='th_vaciar_while_'+str(iteration);blocks.append(block)
                    node=heap[actual];assert node['alive'] and node['fields_valid'];saved=node['next'];visits+=1
                    local(block,'siguiente','THNodo *',saved);emit('next_saved','THNodo *siguiente =','th_vaciar')
                    retired=actual;history={k:node[k] for k in ('key','value','next')};node.update({'alive':False,'fields_valid':False,'initialized_mask':0,
                        'historical_fields':history,'historical_initialized_mask':7,'freed_at':frees+1,'key':None,'value':None,'next':None})
                    for cell in cells:
                        if cell['valid'] and cell['value']==retired:cell.update({'value':None,'initialized':False,'valid':False,'historical_value':retired})
                    variables['th_vaciar.actual'].update({'value':None,'initialized':False,'valid':False,'historical_identity':retired,'reason':'indeterminate after free'})
                    actual=None;frees+=1;count_pending=True;emit('node_free','free(actual);','th_vaciar')
                    actual=saved;local('th_vaciar','actual','THNodo *',actual);emit('actual_assigned','actual = siguiente;','th_vaciar')
                    retire(block);saved=None;emit('iteration_exit','@while_end','th_vaciar')
                cells[i].update({'value':None,'valid':True,'initialized':True});cells[i].pop('historical_value',None)
                emit('bucket_NULL_write','tabla->buckets[i] = NULL;','th_vaciar');del variables['th_vaciar.actual'];actual=None
                emit('bucket_body_exit','@for_end','th_vaciar');i+=1;local('th_vaciar','i','int',i);emit('bucket_increment','for (int i =','th_vaciar')
            del variables['th_vaciar.i'];i=None;emit('bucket_loop_exit','@for_end','th_vaciar')
            size=0;count_pending=False;emit('clear_count_zero','tabla->cantidad = 0;','th_vaciar')
        retire('th_vaciar');emit('clear_return','if (!tabla || !tabla->buckets)' if invalid else '@end','th_vaciar')
    if operation_name=='clear':clear_call()
    else:
        functions.append('th_destruir');local('th_destruir','tabla','TablaHash *',None if null_table else '&tabla')
        emit('destroy_entry','void th_destruir(','th_destruir');invalid=null_table or root_ptr is None
        emit('destroy_guard','if (!tabla || !tabla->buckets)','th_destruir',invalid)
        if not invalid:
            emit('clear_call','th_vaciar(tabla);','th_destruir');clear_call()
            array_alive=False;array_freed=True;root_ptr_valid=False;root_ptr=None;frees+=1
            for cell in cells:cell.update({'initialized':False,'valid':False,'value':None,'historical_value':None})
            emit('bucket_array_free','free(tabla->buckets);','th_destruir')
            root_ptr_valid=True;emit('root_buckets_NULL','tabla->buckets = NULL;','th_destruir')
            cap=0;emit('root_capacity_zero','tabla->capacidad = 0;','th_destruir')
            size=0;emit('destroy_count_zero','tabla->cantidad = 0;','th_destruir')
        retire('th_destruir');emit('destroy_return','if (!tabla || !tabla->buckets)' if invalid else '@end','th_destruir')
    steps[0]['phase']='start';steps[-1]['phase']='end';steps[-1]['state_after']=deepcopy(after_state);steps[-1]['pedagogy']['state_after']=deepcopy(after_state)
    return {'structure_id':'hash_table','operation_name':operation_name,'payload':deepcopy(payload),'success':success,
        'mutates':True,'message':message,'code_title':code_title,'source_code':source_code,'steps':steps,'final_state':deepcopy(after_state),
        'pedagogy_schema_version':1,'pedagogy_schema':hash_frame_schema(),'learning_profile':deepcopy(HASH_LEARNING_CATALOG),
        'instruction_scope':'th_vaciar/th_destruir mutable aliases, scope lifetimes and pointer indeterminacy'}
