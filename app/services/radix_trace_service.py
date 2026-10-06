"""Radix-only typed presentation over the lossless immutable instruction tape."""
from __future__ import annotations
from bisect import bisect_right
from copy import deepcopy
from app.services.counting_trace_service import CountingTrace, deep_size
from app.domain.sorting.pedagogy import (validate_pedagogical_frame, pedagogical_frame_schema, learning_profile, theory_profile)


def line_lookup(source: str) -> dict:
    """Bind tokens inside actual C function spans; unexecuted boundaries have no line."""
    lines=source.replace('\r\n','\n').split('\n');result={}
    def find(text,start=0):
        return next((i for i in range(start or 0,len(lines)) if text in lines[i]),None)
    helper=find('static int counting_por_digito(');wrapper=find('int ordenar_radixsort(');valid=find('static int arreglo_valido(')
    def bind(tokens,text,start):
        for token in tokens.split():result[token]=find(text,start or 0)
    result.update(initial=None,negative_block_exit=None,positive_block_exit=None,radix_entry=wrapper,digit_entry=helper,valid_entry=valid)
    bind('valid_ptr valid_n valid_return','return arreglo != NULL && n > 0;',valid)
    bind('radix_declare','uint32_t *negativos, *positivos;',wrapper)
    bind('radix_invalid_guard','if (!arreglo_valido(arreglo, n))',wrapper)
    bind('negative_allocate','negativos = (uint32_t *)malloc',wrapper)
    bind('positive_allocate','positivos = (uint32_t *)malloc',wrapper)
    bind('negative_null positive_null split_reserve_guard split_cleanup','if (negativos == NULL || positivos == NULL)',wrapper)
    bind('split_init split_test split_increment','for (i = 0; i < n; ++i)',wrapper)
    bind('sign_test negative_write','if (arreglo[i] < 0)',wrapper)
    bind('positive_write','else positivos[cant_positivos++]',wrapper)
    for prefix,name in [('negative','negativos'),('positive','positivos')]:
        start=find('if (cant_'+name+' > 0)',wrapper)
        bind(prefix+'_group_guard','if (cant_'+name+' > 0)',wrapper)
        bind(prefix+'_max_exp_init','uint32_t maximo = '+name+'[0], exp = 1U;',start)
        bind(' '.join(prefix+'_'+t for t in ['scan_init','scan_test','max_compare','max_assign','scan_increment']),'for (i = 1; i < cant_'+name+'; ++i)',start)
        bind(prefix+'_digit_call '+prefix+'_digit_status '+prefix+'_helper_cleanup','if (!counting_por_digito('+name+',',start)
        bind(prefix+'_exp_guard '+prefix+'_break','if (exp > maximo / 10U) break;',start)
        bind(prefix+'_exp_multiply','exp *= 10U;',start)
    bind('positive_nonzero_guard','if (maximo > 0U)',wrapper)
    bind('caller_index_init','indice = 0;',wrapper)
    bind('negative_join_init negative_join_test negative_join_decrement','for (i = cant_negativos; i > 0; --i)',wrapper)
    bind('negative_magnitude_read','uint32_t magnitud = negativos[i - 1];',wrapper)
    bind('INT_MIN_magnitude_guard negative_caller_write','arreglo[indice++] = magnitud ==',wrapper)
    bind('positive_join_init positive_join_test positive_caller_write positive_join_increment','for (i = 0; i < cant_positivos; ++i)',wrapper)
    result['final_cleanup']=next((i for i in range(wrapper or 0,len(lines)) if lines[i].strip()=='free(negativos); free(positivos);'),None)
    bind('radix_return','return ORDENAMIENTO_OK;',result['final_cleanup'])
    bind('digit_declare','size_t conteo[10] = {0};',helper)
    bind('digit_allocate','salida = (uint32_t *)malloc',helper)
    bind('digit_allocation_guard digit_error','if (salida == NULL)',helper)
    bind('digit_fill_init digit_fill_test digit_frequency_write digit_fill_increment','for (i = 0; i < n; ++i) ++conteo',helper)
    bind('digit_prefix_init digit_prefix_test digit_prefix_write digit_prefix_increment','for (i = 1; i < 10; ++i)',helper)
    bind('digit_reverse_init digit_reverse_test digit_reverse_decrement','for (i = n; i > 0; --i)',helper)
    bind('digit_value_read','uint32_t valor = arreglo[i - 1];',helper)
    bind('digit_select','uint32_t digito = (valor / exp)',helper)
    bind('digit_output_write','salida[conteo[digito] - 1] = valor;',helper)
    bind('digit_frequency_decrement','--conteo[digito];',helper)
    bind('digit_copy_init digit_copy_test digit_work_copy digit_copy_increment','for (i = 0; i < n; ++i) arreglo[i] = salida[i];',helper)
    bind('digit_free','free(salida);',helper)
    bind('digit_return','return ORDENAMIENTO_OK;',helper)
    return result


def typed_variables(ctx: dict,n: int) -> list[dict]:
    """Show declared active locals, masked cells and symbolic aliases, never addresses."""
    result=[];b=ctx['buffers']
    def var(name,kind,value,scope,initialized=True):
        result.append(dict(name=name,type=kind,value=deepcopy(value) if initialized else None,scope=scope,initialized=initialized))
    def pointer(name,target,scope):
        buf=b[target];initialized=buf['status'] not in {'undeclared','uninitialized'}
        value='NULL' if buf['status']=='NULL' else {'alias':target,'status':buf['status'],'capacity':buf['capacity'],'cells':deepcopy(buf['cells']) if buf['live'] else None}
        var(name,'uint32_t *',value,scope,initialized)
    scope='ordenar_radixsort'
    if ctx['wrapper_active']:
        var('arreglo','int *',{'alias':'caller'},scope);var('n','size_t',n,scope)
        if ctx['wrapper_declared']:
            pointer('negativos','negative',scope);pointer('positivos','positive',scope)
            var('cant_negativos','size_t',ctx['ng'],scope);var('cant_positivos','size_t',ctx['pg'],scope)
            var('i','size_t',ctx['wi'],scope,ctx['wi'] is not None);var('indice','size_t',ctx['indice'],scope,ctx['indice'] is not None)
        if ctx['block']:
            sub=scope+'/bloque_'+('negativos' if ctx['block']=='negative' else 'positivos')
            var('maximo','uint32_t',ctx['maximo'],sub);var('exp','uint32_t',ctx['exp'],sub)
        if ctx['magnitud'] is not None:var('magnitud','uint32_t',ctx['magnitud'],scope+'/recomponer_negativos')
    if ctx['valid_active']:
        var('arreglo','const int *',{'alias':'caller'},'arreglo_valido');var('n','size_t',n,'arreglo_valido')
    if ctx['helper_active']:
        scope='counting_por_digito'
        var('arreglo','uint32_t *',{'alias':ctx['group'],'cells':deepcopy(b[ctx['group']]['cells'][:ctx['helper_n']])},scope)
        var('n','size_t',ctx['helper_n'],scope);var('exp','uint32_t',ctx['helper_exp'],scope)
        if ctx['helper_declared']:
            var('conteo','size_t[10]',ctx['counts'],scope);pointer('salida','output',scope)
            var('i','size_t',ctx['di'],scope,ctx['di'] is not None)
        if ctx['valor'] is not None:
            sub=scope+'/distribucion_inversa';var('valor','uint32_t',ctx['valor'],sub)
            if ctx['digito'] is not None:var('digito','uint32_t',ctx['digito'],sub)
    return result


class RadixPageSource:
    """Serve immutable Radix frames through the shared bounded page/ownership protocol."""
    def __init__(self,tape,source_code,*,error_info=None,accepted_state=None):
        self.tape=tape;self.source_code=source_code;self.lines=source_code.replace('\r\n','\n').split('\n');self.lookup=line_lookup(source_code)
        self.error_info=deepcopy(error_info);self.accepted_state=deepcopy(accepted_state)
        self.final_state=self.state(tape[-1]);self.final_state['last_operation']=dict(name='radixsort',status='error' if error_info else 'success',message=error_info['message'] if error_info else 'Ordenamiento finalizado.')
        self.concepts={};self.done_masks=[];mask=0
        for i in range(len(tape)):
            row=tape[i];concept=self.concept(row);self.concepts.setdefault(concept,[]).append(i);self.done_masks.append(mask)
            line=self.lookup.get(row.get('source_hint') or row['line_token'])
            if line is not None:mask |= 1<<line
        self.retained_bytes=deep_size([tape.records,tape._last,tape._decoded,self.lines,self.lookup,self.final_state,self.concepts,self.done_masks,self.error_info,self.accepted_state])
    @staticmethod
    def concept(row):
        token=row['line_token']
        return 'comparison' if token.endswith('max_compare') else 'condition' if row['condition_result'] is not None else 'return' if token.endswith('return') else 'call' if token.endswith(('entry','call')) else 'phase' if token=='initial' or token.endswith('block_exit') else 'assignment'
    @staticmethod
    def state(row):
        from app.adapters.sorting_adapter import SortingAdapter
        state=SortingAdapter._build_visual_state_from_step(None,row,algorithm_id='radixsort');ctx=deepcopy(row['radix_context'])
        out=ctx['buffers']['output'];ctx['digit_output_initialized']=[v is not None for v in (out['cells'] or [])]
        for buf in ctx['buffers'].values():buf['initialized']=[v is not None for v in (buf['cells'] or [])]
        state['radix_context']=ctx
        if row['instruction_event']['return_status']==1 and row['line_token']=='radix_return':state['sorted_indices']=list(range(len(state['items'])))
        return state
    def frame(self,index,dense=False):
        prev=self.tape[max(0,index-1)];row=self.tape[index];ctx=row['radix_context'];token=row['line_token'];line=self.lookup.get(row.get('source_hint') or token);text=self.lines[line] if line is not None else ''
        vars=typed_variables(ctx,len(row['array_snapshot']));old={(v['scope'],v['name']):v for v in typed_variables(prev['radix_context'],len(prev['array_snapshot']))} if index else {}
        for v in vars:
            prior=old.get((v['scope'],v['name']));v.update(previous=deepcopy(prior['value']) if prior and prior['initialized'] else None,changed=prior is None or prior['initialized']!=v['initialized'] or prior['value']!=v['value'],meaning=v['scope']+('; valor tras instruccion' if v['initialized'] else '; sin inicializar'))
        stack=[]
        if ctx['wrapper_active']:stack.append(dict(function='ordenar_radixsort',parameters={'arreglo':'caller','n':len(row['array_snapshot'])},continuation='retornar al caller'))
        if ctx['valid_active']:stack.append(dict(function='arreglo_valido',parameters={'arreglo':'caller','n':len(row['array_snapshot'])},continuation='evaluar guarda del wrapper'))
        if ctx['helper_active']:stack.append(dict(function='counting_por_digito',parameters={'arreglo':ctx['group'],'n':ctx['helper_n'],'exp':ctx['helper_exp']},continuation='evaluar estado y guarda de exp en wrapper'))
        pointers=[dict(name=v['name'],type=v['type'],target=v['value'],scope=v['scope']) for v in vars if '*' in v['type']]
        condition=None if row['condition_result'] is None else dict(expression=row['condition_expression'],result=row['condition_result'],consequence='Seguir rama verdadera.' if row['condition_result'] else 'Seguir rama falsa.')
        action=row['action'];concept=self.concept(row)
        loop=None
        if token.endswith(('init','test','increment','decrement')):
            upper=10 if token.startswith('digit_prefix_') else ctx['helper_n'] if ctx['helper_active'] else ctx['ng'] if token.startswith(('negative_scan_','negative_join_')) else ctx['pg'] if token.startswith(('positive_scan_','positive_join_')) else len(row['array_snapshot'])
            lower=1 if token.startswith(('digit_prefix_','negative_scan_','positive_scan_')) else 0
            loop=dict(kind=token.rsplit('_',1)[0],iteration=ctx['di'] if ctx['helper_active'] else ctx['wi'],bounds=[lower,upper],exit=token.endswith('test') and row['condition_result'] is False)
        pedagogy=dict(schema_version=1,concept=concept,phase=dict(id=token,label=token.replace('_',' '),goal=action),condition=condition,variables=vars,call_stack=stack,loop=loop,pointers=pointers,invariant=dict(text='Sólo se leen celdas inicializadas de reservas vivas; el caller se recompone al final.',indices=[],holds=True),narration=dict(basic=action,intermediate=action+' Valores del modelo tras esta transición.',advanced=action+' C: '+(text.strip() or 'frontera de ejecución sin sentencia C resaltada')),source=dict(line_token=token,line_index=line,line_text=text,function=row['source_function']))
        validate_pedagogical_frame(pedagogy,source_code=self.source_code)
        frame=dict(step_index=index,line_index=line,line_text=text,event_type='line',phase='start' if index==0 else 'end' if index==len(self.tape)-1 else 'progress',delay_ms=160,state_snapshot=self.state(prev),state_after=deepcopy(self.final_state) if index==len(self.tape)-1 else self.state(row),debug=dict(stage='sorting',note=action,instruction_event=deepcopy(row['instruction_event']),console_events=[]),pedagogy=pedagogy)
        if not dense:
            frame['concept_occurrence']=bisect_right(self.concepts[concept],index);mask=self.done_masks[index];frame['done_lines']=[i for i in range(len(self.lines)) if mask>>i&1]
        return frame
    def page(self,start,limit=64):
        if not 1<=limit<=128:raise ValueError('El limite de pagina debe ser 1..128.')
        if not 0<=start<len(self.tape):raise ValueError('El indice esta fuera de la traza.')
        end=min(len(self.tape),start+limit)
        return dict(schema='counting-trace-page/v1',start=start,end=end,step_count=len(self.tape),steps=[self.frame(i) for i in range(start,end)])
    def locate(self,concept,occurrence):
        if occurrence<1:raise ValueError('La ocurrencia debe ser positiva.')
        positions=self.concepts.get(concept,[])
        return positions[min(occurrence,len(positions))-1] if positions else None
    def trace(self):
        trace=CountingTrace(structure_id='sorting',operation_name='radixsort',payload={},success=not bool(self.error_info),mutates=not bool(self.error_info),message=self.error_info['message'] if self.error_info else 'Ordenamiento ejecutado correctamente.',code_title='Codigo C',source_code=self.source_code,final_state=deepcopy(self.final_state),pedagogy_schema_version=1,pedagogy_schema=pedagogical_frame_schema(),learning_profile=learning_profile('radixsort'),theory_profile=theory_profile('radixsort'),native_status=0 if self.error_info else 1,metric_policy=dict(comparisons='max_value_comparisons',moves=['work_writes','count_writes','digit_output_writes','caller_writes'],guards_excluded=True,allocator_initialization_excluded=True),execution_origin='python-c-equivalent-model')
        if self.error_info:trace.update(error=deepcopy(self.error_info),accepted_state=deepcopy(self.accepted_state))
        n=len(self.tape[0]['array_snapshot']);estimate=len(self.tape)*(4*n+80)*96
        if len(self.tape)<=2048 and estimate<=32*1024*1024:
            trace['steps']=[self.frame(i,dense=True) for i in range(len(self.tape))]
            from app.services.trace.engine import TraceEngine
            TraceEngine.validate_legacy_trace(trace)
        else:trace.update(schema='counting-paged-trace/v1',step_count=len(self.tape),manifest={**self.tape.manifest(),'retained_bytes':self.retained_bytes},initial_page=self.page(0,16))
        trace.page_source=self
        return trace
    def compact_export(self):
        result=dict(schema='radix-compact-export/v1',operation_name='radixsort',codec='radix-delta-tape/v1',source_code=self.source_code,records=deepcopy(self.tape.records),step_count=len(self.tape),final_state=deepcopy(self.final_state),success=not bool(self.error_info),native_status=0 if self.error_info else 1,execution_origin='python-c-equivalent-model')
        if self.error_info:result.update(error=deepcopy(self.error_info),accepted_state=deepcopy(self.accepted_state),mutates=False)
        return result
