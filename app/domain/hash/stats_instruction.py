"""Finite statement model of existing C statistics; API precision stays intact."""
from copy import deepcopy
import struct
from app.domain.hash.pedagogy import build_hash_frame, hash_frame_schema, HASH_LEARNING_CATALOG

FIELDS=('capacidad','cantidad','buckets_ocupados','colisiones','factor_carga')

def cfloat(value):
    """Binary32 host model, verified against the finite native C observations."""
    return struct.unpack('!f',struct.pack('!f',value))[0]

def build_hash_stats_trace(*,operation_name,payload,source_code,code_title,before_state,
        after_state,success,message,buffer_capacity=512,caller_buffer_capacity=None,
        null_destination=False,null_table=False,**_):
    """Execute two distinct struct-return invocations and bounded formatter writes."""
    lines=source_code.replace('\r\n','\n').split('\n');steps=[];stack=['caller'];variables={}
    cap=int(before_state['metadata']['capacity']);size=int(before_state['metadata']['size'])
    buckets=before_state.get('buckets',[]);physical=buffer_capacity if caller_buffer_capacity is None else caller_buffer_capacity
    raw=bytearray(physical);prefix=0;buffer_declared=False;invocation=0;nodes=0;actual=None;i=None;return_value=None
    def local(scope,name,ctype,value=None,initialized=True):
        variables[scope+'.'+name]={'type':ctype,'value':deepcopy(value) if initialized else None,'initialized':initialized}
    def record(scope,value=None):
        local(scope,'stats','THEstadisticas',value,initialized=value is not None)
        variables[scope+'.stats'].update({'initialized_mask':31 if value is not None else 0,
            'storage_id':scope+'.stats'+(f'#{invocation}' if scope=='th_estadisticas' else ''),
            'padding':'not inspected','fields':{n:{'type':'float' if n=='factor_carga' else 'int',
                'initialized':value is not None,'value':value[n] if value is not None else None} for n in FIELDS}})
    def retire(scope):
        for n in list(variables):
            if n.startswith(scope+'.'):del variables[n]
        stack.remove(scope)
    def location(token,function):
        if token is None:return -1
        if function=='caller':return next(n for n,s in enumerate(lines) if token in s)
        start=next(n for n,s in enumerate(lines) if function+'(' in s and '{' in s);depth=0;end=start
        for end in range(start,len(lines)):
            depth+=lines[end].count('{')-lines[end].count('}')
            if depth==0:break
        if token=='@end':return end
        if token=='@table_return':
            call=next(n for n in range(start,end+1) if 'snprintf(destino,' in lines[n])
            return next(n for n in range(call+1,end+1) if 'return;' in lines[n])
        if token=='@occupied_end':
            write=next(n for n in range(start,end+1) if 'stats.colisiones +=' in lines[n])
            return next(n for n in range(write+1,end+1) if lines[n]=='        }')
        if token=='@loop_end':return next(n for n in range(start,end+1) if lines[n]=='    }' and n>next(k for k in range(start,end+1) if 'stats.colisiones +=' in lines[k]))
        reverse=token.startswith('@last:');token=token.removeprefix('@last:')
        return next(n for n in (range(end,start-1,-1) if reverse else range(start,end+1)) if token in lines[n])
    def emit(event,token,function,condition=None):
        line=location(token,function);buffer=None
        if buffer_declared:
            buffer={'id':'caller.texto','type':f'char[{physical}]','capacity':physical,'argument_capacity':buffer_capacity,
                'initialized':prefix==physical,'initialized_prefix':prefix,'initialized_ranges':[[0,prefix]] if prefix else [],
                'uninitialized_range':[prefix,physical],'bytes':list(raw[:prefix]),
                'text':bytes(raw[:prefix]).split(b'\0',1)[0].decode('ascii') if prefix else None,
                'alive':True,'uninitialized_bytes_read':False}
            variables['caller.texto'].update(buffer)
        scopes=[{'function':scope,'variables':{n.split('.',1)[1]:deepcopy(v) for n,v in variables.items() if n.startswith(scope+'.')}} for scope in stack]
        current=variables.get('th_estadisticas.stats',{}).get('value')
        representation={'C_float_load':(current or return_value or {}).get('factor_carga'),
            'API_double_load':size/cap if cap else 0.0,'API_fields':['capacity','size','load_factor'],
            'C_fields':list(FIELDS),'C_text_decimals':2,'API_message_decimals':3,'metadata_decimals':6,
            'same_numeric_representation':False,'API_semantics_changed':False}
        debug={'token':event,'function':function,'variables':deepcopy(variables),'scopes':scopes,'call_stack':list(stack),
            'stats_invocation':invocation,'stats':deepcopy(current),'returned_stats':deepcopy(return_value),
            'bucket_index':i,'actual':actual,'nodes_visited':nodes,'condition_result':condition,
            'buffer':buffer,'allocations':0,'frees':0,'representation':representation,
            'libc_boundary':'snprintf decimal formats; binary32 finite host, no ABI/padding inspection'}
        step={'step_index':len(steps),'line_index':line,'line_text':lines[line] if line>=0 else '',
            'event_type':event,'phase':'progress','delay_ms':100,'console':[],'debug':debug,
            'state_snapshot':deepcopy(before_state),'state_after':deepcopy(before_state),
            'instruction_event':{'token':event,'function':function,'condition':condition}}
        frame=build_hash_frame(operation_name=operation_name,payload=payload,step=step,source_lines=lines,success=success)
        frame['source']['function']=function;frame['variables']={n:deepcopy(v['value']) for n,v in variables.items()}
        frame['memory'].update({'variables':deepcopy(variables),'scopes':scopes,'call_stack':list(stack),
            'heap':[{'id':e['address'],'type':'THNodo','initialized_mask':7,'key':e['key'],'value':e['value'],'next':e.get('next')} for b in buckets for e in b['entries']],
            'allocated':[],'freed':[],'allocation_attempted':False,'links_changed':False})
        if buffer is not None:frame['memory']['buffer']=deepcopy(buffer)
        frame['pointers'].update({'actual':actual or 'NULL','tabla':'NULL' if null_table else '&tabla',
            'destino':('NULL' if null_destination else '&caller.texto') if 'th_formatear_estadisticas' in stack else 'fuera de alcance'})
        frame['cost'].update({'nodes_visited':nodes,'hash_evaluations':0,'stats_invocations':invocation})
        frame['condition']=None if condition is None else {'source':step['line_text'],'result':condition,'substituted':str(condition),'consequence':'Rama C ejecutada.'}
        frame['stats_representation']=representation
        frame['narration']['advanced']=f'{function}: {event}; float C y proyeccion API separados, padding no inspeccionado.'
        step['pedagogy']=frame;steps.append(step)
    def stats_call():
        nonlocal invocation,nodes,actual,i,return_value
        invocation+=1;return_value=None;stack.append('th_estadisticas')
        local('th_estadisticas','tabla','const TablaHash *',None if null_table else '&tabla')
        emit('stats_entry','THEstadisticas th_estadisticas(','th_estadisticas')
        stats={n:0.0 if n=='factor_carga' else 0 for n in FIELDS};record('th_estadisticas',stats)
        emit('stats_zero_initialized','THEstadisticas stats = {0};','th_estadisticas')
        invalid=null_table or cap<=0;emit('stats_guard','if (!tabla || !tabla->buckets','th_estadisticas',invalid)
        if not invalid:
            stats['capacidad']=cap;record('th_estadisticas',stats);emit('capacity_write','stats.capacidad =','th_estadisticas')
            stats['cantidad']=size;record('th_estadisticas',stats);emit('size_write','stats.cantidad =','th_estadisticas')
            stats['factor_carga']=cfloat(cfloat(size)/cfloat(cap));record('th_estadisticas',stats)
            emit('float_load_write','stats.factor_carga =','th_estadisticas')
            i=0;local('th_estadisticas','i','int',i);emit('bucket_init','for (int i =','th_estadisticas')
            while True:
                emit('bucket_guard','for (int i =','th_estadisticas',i<cap)
                if i>=cap:break
                chain=next((b['entries'] for b in buckets if b['index']==i),[])
                actual=chain[0]['address'] if chain else None;local('th_estadisticas','actual','THNodo *',actual)
                emit('actual_declared','THNodo *actual =','th_estadisticas');emit('occupied_guard','if (actual != NULL)','th_estadisticas',actual is not None)
                if actual is not None:
                    stats['buckets_ocupados']+=1;record('th_estadisticas',stats);emit('occupied_increment','stats.buckets_ocupados++;','th_estadisticas')
                    count=0;local('th_estadisticas','nodos_en_bucket','int',count);emit('node_count_declared','int nodos_en_bucket = 0;','th_estadisticas')
                    while True:
                        emit('chain_guard','while (actual != NULL)','th_estadisticas',actual is not None)
                        if actual is None:break
                        count+=1;nodes+=1;local('th_estadisticas','nodos_en_bucket','int',count);emit('node_count_increment','nodos_en_bucket++;','th_estadisticas')
                        actual=chain[count]['address'] if count<len(chain) else None;local('th_estadisticas','actual','THNodo *',actual)
                        emit('actual_advance','actual = actual->siguiente;','th_estadisticas')
                    emit('collision_guard','if (nodos_en_bucket > 1)','th_estadisticas',count>1)
                    if count>1:
                        stats['colisiones']+=count-1;record('th_estadisticas',stats);emit('collisions_write','stats.colisiones +=','th_estadisticas')
                    del variables['th_estadisticas.nodos_en_bucket'];emit('occupied_body_exit','@occupied_end','th_estadisticas')
                del variables['th_estadisticas.actual'];actual=None;emit('bucket_body_exit','@loop_end','th_estadisticas')
                i+=1;local('th_estadisticas','i','int',i);emit('bucket_increment','for (int i =','th_estadisticas')
            del variables['th_estadisticas.i'];i=None;emit('bucket_loop_exit','@loop_end','th_estadisticas')
        return_value=deepcopy(stats);retire('th_estadisticas')
        emit('stats_return','if (!tabla || !tabla->buckets' if invalid else '@last:return stats;','th_estadisticas')
        return stats
    def write(text):
        nonlocal prefix
        data=text.encode('ascii')[:buffer_capacity-1]+b'\0';raw[:len(data)]=data;prefix=len(data)
    record('caller');emit('caller_stats_declared','THEstadisticas stats = th_estadisticas','caller')
    emit('caller_stats_call','THEstadisticas stats = th_estadisticas','caller')
    result=stats_call();record('caller',result);emit('caller_stats_assigned','THEstadisticas stats = th_estadisticas','caller')
    buffer_declared=True;local('caller','texto',f'char[{physical}]',initialized=False)
    emit('buffer_declared','char texto[','caller');emit('formatter_call','th_formatear_estadisticas(&tabla','caller')
    stack.append('th_formatear_estadisticas');local('th_formatear_estadisticas','tabla','const TablaHash *',None if null_table else '&tabla')
    local('th_formatear_estadisticas','destino','char *',None if null_destination else '&caller.texto');local('th_formatear_estadisticas','capacidad','size_t',buffer_capacity)
    emit('formatter_entry','void th_formatear_estadisticas(','th_formatear_estadisticas')
    invalid_dest=null_destination or buffer_capacity==0;emit('destination_guard','if (!destino || capacidad == 0)','th_formatear_estadisticas',invalid_dest)
    if not invalid_dest:
        raw[0]=0;prefix=1;emit('initial_terminator','destino[0] =','th_formatear_estadisticas')
        invalid_table=null_table or cap<=0;emit('table_guard','if (!tabla || !tabla->buckets)','th_formatear_estadisticas',invalid_table)
        if invalid_table:
            write('Tabla no inicializada\n');emit('uninitialized_table_text','snprintf(destino, capacidad,','th_formatear_estadisticas')
        else:
            record('th_formatear_estadisticas');emit('formatter_stats_declared','THEstadisticas stats =','th_formatear_estadisticas')
            emit('formatter_stats_call','THEstadisticas stats =','th_formatear_estadisticas')
            result=stats_call();record('th_formatear_estadisticas',result)
            emit('formatter_stats_assigned','THEstadisticas stats =','th_formatear_estadisticas')
            write(f"Capacidad: {result['capacidad']}\nCantidad: {result['cantidad']}\nBuckets ocupados: {result['buckets_ocupados']}\nColisiones: {result['colisiones']}\nFactor de carga: {result['factor_carga']:.2f}\n")
            emit('snprintf_write','@last:snprintf(destino, capacidad,','th_formatear_estadisticas')
        retire('th_formatear_estadisticas');emit('formatter_return','@table_return' if invalid_table else '@end','th_formatear_estadisticas')
    else:
        retire('th_formatear_estadisticas');emit('formatter_return','if (!destino || capacidad == 0)','th_formatear_estadisticas')
    steps[0]['phase']='start';steps[-1]['phase']='end';steps[-1]['state_after']=deepcopy(after_state);steps[-1]['pedagogy']['state_after']=deepcopy(after_state)
    return {'structure_id':'hash_table','operation_name':operation_name,'payload':deepcopy(payload),'success':success,
        'mutates':False,'message':message,'code_title':code_title,'source_code':source_code,'steps':steps,
        'final_state':deepcopy(after_state),'pedagogy_schema_version':1,'pedagogy_schema':hash_frame_schema(),
        'learning_profile':deepcopy(HASH_LEARNING_CATALOG),'instruction_scope':'caller/th_estadisticas x2/th_formatear_estadisticas; API numeric semantics unchanged'}
