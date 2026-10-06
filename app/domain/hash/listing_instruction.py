"""Statement model of the existing C formatter; API projections stay independent."""
from copy import deepcopy
from app.domain.hash.pedagogy import build_hash_frame, hash_frame_schema, HASH_LEARNING_CATALOG


def build_hash_listing_trace(*, operation_name, payload, source_code, code_title,
        before_state, after_state, success, message, buffer_capacity=2048,
        null_destination=False, null_table=False, caller_buffer_capacity=None, **_):
    """Model finite decimal formats, opaque libc call and explicit byte lifetimes."""
    lines=source_code.replace("\r\n","\n").split("\n")
    storage_capacity=buffer_capacity if caller_buffer_capacity is None else caller_buffer_capacity
    steps=[]; variables={}; stack=['caller']; raw=bytearray(storage_capacity)
    written=set(); used=0; i=None; actual=None; nodes=0; calls=0
    buckets=before_state.get('buckets',[]); cap=int(before_state['metadata']['capacity'])
    def local(scope,name,ctype,value=None,initialized=True):
        variables[scope+'.'+name]={'type':ctype,'initialized':initialized,'value':value if initialized else None}
    def retire(scope):
        for name in list(variables):
            if name.startswith(scope+'.'):del variables[name]
        stack.remove(scope)
    def location(token,function):
        if token is None:return -1
        if function=='caller':return next(n for n,s in enumerate(lines) if token in s)
        start=next(n for n,s in enumerate(lines) if function+'(' in s and '{' in s)
        if token=='@table_return':
            call=next(n for n in range(start,len(lines)) if 'snprintf(destino,' in lines[n])
            return next(n for n in range(call+1,len(lines)) if 'return;' in lines[n])
        if token=='@bucket_end':
            call=next(n for n in range(start,len(lines)) if 'th_append_text(destino, capacidad, &usado, "NULL' in lines[n])
            return next(n for n in range(call+1,len(lines)) if lines[n]=='    }')
        if token=='@end':
            depth=0
            for n in range(start,len(lines)):
                depth+=lines[n].count('{')-lines[n].count('}')
                if depth==0:return n
        return next(n for n in range(start,len(lines)) if token in lines[n])
    def emit(event,token,function,condition=None):
        line=location(token,function)
        prefix=0
        while prefix in written:prefix+=1
        buffer={'id':'caller.buffer','type':f'char[{storage_capacity}]','capacity':storage_capacity,'argument_capacity':buffer_capacity,
            'alive':'caller' in stack,'initialized':prefix==storage_capacity,
            'initialized_prefix':prefix,'initialized_ranges':[[0,prefix]] if prefix else [],
            'uninitialized_range':[prefix,storage_capacity],
            'bytes':list(raw[:prefix]),'uninitialized_bytes_read':False,
            'text':bytes(raw[:prefix]).split(b'\0',1)[0].decode('ascii') if prefix else None}
        if 'caller.buffer' in variables:variables['caller.buffer'].update(buffer)
        scopes=[{'function':scope,'variables':{n.split('.',1)[1]:deepcopy(v) for n,v in variables.items() if n.startswith(scope+'.')}} for scope in stack]
        debug={'token':event,'function':function,'scopes':scopes,'call_stack':list(stack),
            'variables':deepcopy(variables),'buffer':buffer,'used':used if 'th_formatear.usado' in variables else None,
            'bucket_index':i,'actual':actual,'nodes_visited':nodes,'append_calls':calls,
            'condition_result':condition,'allocations':0,'frees':0,
            'libc_boundary':'vsnprintf decimal ASCII success; va_list opaque, not ABI inspection'}
        step={'step_index':len(steps),'line_index':line,'line_text':lines[line] if line>=0 else '',
            'event_type':event,'phase':'progress','delay_ms':100,'console':[],
            'state_snapshot':deepcopy(before_state),'state_after':deepcopy(before_state),
            'debug':debug,'instruction_event':{'token':event,'function':function,'condition':condition}}
        frame=build_hash_frame(operation_name=operation_name,payload=payload,step=step,source_lines=lines,success=success)
        frame['source']['function']=function;frame['variables']={n:v['value'] for n,v in variables.items()}
        frame['memory'].update({'variables':deepcopy(variables),'scopes':scopes,'call_stack':list(stack),
            'buffer':deepcopy(buffer),'heap':[{'id':n['address'],'type':'THNodo','initialized_mask':7,'key':n['key'],'value':n['value'],'next':n.get('next')} for b in buckets for n in b['entries']],'allocated':[],'freed':[],'allocation_attempted':False,'links_changed':False})
        frame['pointers'].update({'actual':actual or 'NULL','destino':'&caller.buffer' if not null_destination else 'NULL','usado':'&th_formatear.usado' if 'th_append_text' in stack else 'fuera de alcance'})
        frame['cost'].update({'nodes_visited':nodes,'append_calls':calls,'comparisons':0,'hash_evaluations':0})
        frame['condition']=None if condition is None else {'source':step['line_text'],'result':condition,'substituted':str(condition),'consequence':'Rama C ejecutada.'}
        frame['narration']['advanced']=f'{function}: {event}. Texto C de tabla completa; proyeccion API independiente.'
        frame['listing']={'operation':operation_name,'C_output':'formatted whole table text','API_output':'complete ordered projection','same_representation':False}
        step['pedagogy']=frame;steps.append(step)
    def write(offset,text):
        encoded=text.encode('ascii');remaining=buffer_capacity-offset
        if remaining>0:
            data=encoded[:remaining-1]+b'\0';raw[offset:offset+len(data)]=data;written.update(range(offset,offset+len(data)))
        return len(encoded)
    def append(text,fmt,source):
        nonlocal used,calls
        emit('append_call',source,'th_formatear');stack.append('th_append_text');calls+=1
        local('th_append_text','destino','char *','&caller.buffer');local('th_append_text','capacidad','size_t',buffer_capacity)
        local('th_append_text','usado','size_t *','&th_formatear.usado');local('th_append_text','fmt','const char *',fmt)
        emit('append_entry','static void th_append_text(','th_append_text')
        local('th_append_text','args','va_list',initialized=False);emit('args_declared','va_list args;','th_append_text')
        local('th_append_text','escritos','int',initialized=False);emit('written_declared','int escritos;','th_append_text')
        guard=used>=buffer_capacity or null_destination
        emit('append_guard','if (destino == NULL','th_append_text',guard)
        if not guard:
            local('th_append_text','args','va_list','opaque initialized');emit('va_start','va_start(args, fmt);','th_append_text')
            count=write(used,text);local('th_append_text','escritos','int',count)
            emit('vsnprintf_write','escritos = vsnprintf(','th_append_text')
            local('th_append_text','args','va_list',initialized=False);emit('va_end','va_end(args);','th_append_text')
            emit('encoding_guard','if (escritos < 0)','th_append_text',False)
            truncated=count>=buffer_capacity-used;emit('truncation_guard','if ((size_t)escritos >=','th_append_text',truncated)
            used=buffer_capacity if truncated else used+count;local('th_formatear','usado','size_t',used)
            emit('used_saturated' if truncated else 'used_advanced','*usado = capacidad;' if truncated else '*usado += (size_t)escritos;','th_append_text')
        retire('th_append_text');emit('append_return','@end' if not guard else 'return;','th_append_text')
    local('caller','buffer',f'char[{storage_capacity}]',initialized=False)
    emit('buffer_declared','char buffer[','caller');emit('formatter_call','th_formatear(&tabla','caller')
    stack.append('th_formatear');local('th_formatear','tabla','const TablaHash *',None if null_table else '&tabla')
    local('th_formatear','destino','char *',None if null_destination else '&caller.buffer');local('th_formatear','capacidad','size_t',buffer_capacity)
    emit('formatter_entry','void th_formatear(','th_formatear');guard=null_destination or buffer_capacity==0
    emit('destination_guard','if (!destino || capacidad == 0)','th_formatear',guard)
    if not guard:
        raw[0]=0;written.add(0);emit('initial_terminator',"destino[0] =",'th_formatear')
        invalid=null_table or cap==0
        emit('table_guard','if (!tabla || !tabla->buckets)','th_formatear',invalid)
        if invalid:
            write(0,'Tabla no inicializada\n');emit('uninitialized_table_text','snprintf(destino,','th_formatear')
        else:
            local('th_formatear','usado','size_t',0);emit('used_declared','size_t usado = 0;','th_formatear')
            i=0;local('th_formatear','i','int',i);emit('bucket_init','for (int i =','th_formatear')
            while True:
                proceed=i<cap and used<buffer_capacity;emit('bucket_guard','for (int i =','th_formatear',proceed)
                if not proceed:break
                append(f'[{i}] -> ','[%d] -> ','th_append_text(destino, capacidad, &usado, "[%d]')
                chain=next((b['entries'] for b in buckets if b['index']==i),[])
                actual=chain[0]['address'] if chain else None;local('th_formatear','actual','THNodo *',actual)
                emit('actual_declared','THNodo *actual =','th_formatear')
                j=0
                while True:
                    proceed=actual is not None and used<buffer_capacity;emit('chain_guard','while (actual != NULL','th_formatear',proceed)
                    if not proceed:break
                    node=chain[j];nodes+=1;append(f"({node['key']}:{node['value']}) -> ",'(%d:%d) -> ','th_append_text(destino, capacidad, &usado, "(%d:%d)')
                    j+=1;actual=chain[j]['address'] if j<len(chain) else None;local('th_formatear','actual','THNodo *',actual)
                    emit('actual_advance','actual = actual->siguiente;','th_formatear')
                emit('null_label_guard','if (usado < capacidad)','th_formatear',used<buffer_capacity)
                if used<buffer_capacity:append('NULL\n','NULL\n','th_append_text(destino, capacidad, &usado, "NULL')
                del variables['th_formatear.actual'];actual=None;emit('bucket_body_exit','@bucket_end','th_formatear')
                i+=1;local('th_formatear','i','int',i);emit('bucket_increment','for (int i =','th_formatear')
            del variables['th_formatear.i'];i=None;emit('bucket_loop_exit','@bucket_end','th_formatear')
        retire('th_formatear');emit('formatter_return','@table_return' if invalid else '@end','th_formatear')
    else:
        retire('th_formatear');emit('formatter_return','if (!destino || capacidad == 0)','th_formatear')
    # Caller has no printf in the selected teaching snippet; console remains empty.
    steps[0]['phase']='start';steps[-1]['phase']='end';steps[-1]['state_after']=deepcopy(after_state);steps[-1]['pedagogy']['state_after']=deepcopy(after_state)
    return {'structure_id':'hash_table','operation_name':operation_name,'payload':deepcopy(payload),
        'success':success,'mutates':False,'message':message,'code_title':code_title,'source_code':source_code,
        'steps':steps,'final_state':deepcopy(after_state),'pedagogy_schema_version':1,
        'pedagogy_schema':hash_frame_schema(),'learning_profile':deepcopy(HASH_LEARNING_CATALOG),
        'instruction_scope':'caller buffer/th_formatear/th_append_text; opaque vsnprintf boundary'}
