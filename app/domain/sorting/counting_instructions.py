"""Instruction trace for canonical Counting sort; automatic scopes and calloc lifetime."""
from __future__ import annotations
from copy import deepcopy
from typing import Any
from app.domain.sorting.intercambio_instructions import instruction_pedagogy as typed_frame
from app.domain.sorting.tad_ordenamiento import SortingExecutionError,ORDENAMIENTO_RANGO_MAX

def run_counting_trace(values: list[int]) -> dict[str,Any]:
    a=list(values);n=len(a);steps=[];stack=[];declared=False;helper_declared=False
    minimum=maximum=wi=hi=rng=output=None;counts=None;pointer_defined=False;released=False
    comparisons=moves=allocs=frees=filled=consumed=written=0;phase=None
    def emit(token: str,condition: bool | None=None,expression: str='') -> None:
        variables=[];pointers=[]
        def var(name,ctype,value,scope,initialized=True):variables.append(dict(name=name,type=ctype,value=value,scope=scope,initialized=initialized))
        if stack:
            var('arreglo','int *','arreglo del caller','ordenar_counting_sort');var('n','size_t',n,'ordenar_counting_sort')
            if declared:
                for name,value in [('minimo',minimum),('maximo',maximum)]:var(name,'int',value,'ordenar_counting_sort',value is not None)
                for name,value in [('rango',rng),('i',wi),('indice',output)]:var(name,'size_t',value,'ordenar_counting_sort',value is not None)
                var('conteo','int *','memoria liberada; sin lectura' if released else 'reserva conteo' if counts is not None else None,'ordenar_counting_sort',pointer_defined)
        if 'obtener_minimo_maximo' in stack:
            scope='obtener_minimo_maximo';var('arreglo','const int *','arreglo del caller',scope);var('n','size_t',n,scope)
            for name,value in [('minimo',minimum),('maximo',maximum)]:
                target=f'&{name} (ordenar_counting_sort)';var(name,'int *',target,scope);pointers.append(dict(name=name,type='int *',target=target,value=value if value is not None else 'sin inicializar',scope=scope))
            if helper_declared:var('i','size_t',hi,scope,hi is not None)
        if 'arreglo_valido' in stack:
            var('arreglo','const int *','arreglo del caller','arreglo_valido');var('n','size_t',n,'arreglo_valido')
        if counts is not None:pointers.append(dict(name='conteo',type='int *',scope='ordenar_counting_sort',target='reserva calloc int[rango]',value=f'{rng} celdas inicializadas; suma {sum(counts)}'))
        previous={(v['scope'],v['name']):v for v in steps[-1]['instruction_variables']} if steps else {}
        for v in variables:
            old=previous.get((v['scope'],v['name']));v['previous']=old['value'] if old else None;v['changed']=old is None or (old['value'],old['initialized'])!=(v['value'],v['initialized'])
        function=stack[-1] if stack else 'ordenar_counting_sort' if token=='sort_return' else None
        if token=='minmax_return':function='obtener_minimo_maximo'
        event=dict(token=token,condition=condition,array=list(a),minimo=minimum,maximo=maximum,i=wi,helper_i=hi,rango=rng,indice=output,conteo=list(counts) if counts is not None else None,comparisons=comparisons,moves=moves,allocations=allocs,frees=frees)
        compared=[hi] if token in ('min_compare','max_compare') else []
        pending=written-consumed
        context=dict(wrapper_active=bool(stack),helper_active='obtener_minimo_maximo' in stack,helper_declared=helper_declared,minimo=minimum,maximo=maximum,rango=rng,i=wi,helper_i=hi,indice=output,phase=phase,live=counts is not None,declared=declared,released=released,allocations=allocs,frees=frees,filled=filled,written=written,consumed=consumed,pending_decrement=pending,buckets=[dict(index=k,value=minimum+k,count=v) for k,v in enumerate(counts)] if counts is not None else [])
        action={'initial':'Antes de llamar ordenar_counting_sort; ninguna instruccion ejecutada.','declare':'Declarar locales C; valores y puntero aun sin inicializar.','count_init':'calloc reserva y pone todas las frecuencias a cero.','array_write':'Completar arreglo[indice++]=(int)i+minimo; frecuencia aun sin decrementar.','count_write':'Ejecutar --conteo[i] despues de la escritura; consumir una frecuencia.','count_free':'Ejecutar free(conteo); retirar reserva sin asignar NULL al puntero C.','sort_return':'Retornar ORDENAMIENTO_OK y retirar parametros/locales.','min_init':'Escribir *minimo=arreglo[0] en el local del wrapper.','max_init':'Escribir *maximo=arreglo[0] en el local del wrapper.'}.get(token,token.replace('_',' '))
        steps.append(dict(step=len(steps)+1,line_token=token,action=action,array_snapshot=list(a),comparing_indices=compared,swapping_indices=[],sorted_indices=list(range(n)) if token=='sort_return' else [],active_range=None,pivot_index=None,auxiliary_snapshot=list(counts) if counts is not None else None,temporaries={},pointer_indices=[],console_output='',metrics=dict(comparisons=comparisons,moves=moves,swaps=0),instruction_variables=variables,instruction_stack=list(stack),instruction_pointers=pointers,source_function=function,condition_result=condition,condition_expression=expression,instruction_event=event,counting_context=context))
    def valid():
        stack.append('arreglo_valido');emit('valid_entry');emit('valid_ptr',True,'arreglo != NULL');emit('valid_n',n>0,f'{n} > 0');stack.pop();return n>0
    emit('initial');stack.append('ordenar_counting_sort');emit('sort_entry');declared=True;emit('declare');emit('valid_call');ok=valid();emit('sort_guard',not ok,'!arreglo_valido(arreglo,n)')
    if not ok:raise SortingExecutionError('El arreglo no puede estar vacio.')
    emit('minmax_call');stack.append('obtener_minimo_maximo');emit('minmax_entry');helper_declared=True;emit('helper_i_declare');ok=valid();emit('minmax_guard',not ok,'!arreglo_valido(arreglo,n) || minimo == NULL || maximo == NULL')
    minimum=a[0];emit('min_init');maximum=a[0];emit('max_init');hi=1;phase='scan';emit('scan_init')
    while True:
        emit('scan_test',hi<n,f'{hi} < {n}')
        if hi>=n:break
        test=a[hi]<minimum;comparisons+=1;emit('min_compare',test,f'{a[hi]} < {minimum}')
        if test:minimum=a[hi];emit('min_assign')
        test=a[hi]>maximum;comparisons+=1;emit('max_compare',test,f'{a[hi]} > {maximum}')
        if test:maximum=a[hi];emit('max_assign')
        hi+=1;emit('scan_increment')
    hi=None;helper_declared=False;stack.pop();phase=None;emit('minmax_return');emit('minmax_status',False,'!obtener_minimo_maximo(arreglo,n,&minimo,&maximo)')
    rng=maximum-minimum+1;emit('range_compute');too_wide=rng>ORDENAMIENTO_RANGO_MAX;emit('range_limit',too_wide,f'{rng} > {ORDENAMIENTO_RANGO_MAX}')
    if not too_wide:emit('size_guard',False,'rango > SIZE_MAX / sizeof(int) [size_t64]')
    emit('range_guard',too_wide,'rango > ORDENAMIENTO_RANGO_MAX || rango > SIZE_MAX / sizeof(int)')
    if too_wide:raise SortingExecutionError(f'El rango de conteo ({rng}) supera el maximo permitido ({ORDENAMIENTO_RANGO_MAX}).')
    counts=[0]*rng;pointer_defined=True;allocs=1;emit('count_init');emit('allocation_guard',False,'conteo == NULL');wi=0;phase='fill';emit('fill_init')
    while True:
        emit('fill_test',wi<n,f'{wi} < {n}')
        if wi>=n:break
        counts[a[wi]-minimum]+=1;filled+=1;moves+=1;emit('count_fill');wi+=1;emit('fill_increment')
    output=0;emit('output_init');wi=0;phase='rebuild';emit('rebuild_init')
    while True:
        emit('rebuild_test',wi<rng,f'{wi} < {rng}')
        if wi>=rng:break
        while True:
            test=counts[wi]>0;emit('bucket_test',test,f'{counts[wi]} > 0')
            if not test:break
            a[output]=wi+minimum;output+=1;written+=1;moves+=1;emit('array_write');counts[wi]-=1;consumed+=1;moves+=1;emit('count_write')
        wi+=1;emit('rebuild_increment')
    counts=None;released=True;frees=1;phase=None;emit('count_free')
    stack.clear();declared=False;wi=rng=output=minimum=maximum=None;emit('sort_return')
    return dict(steps=steps,final_state={'items':list(a)},metrics=dict(comparisons=comparisons,moves=moves,swaps=0,steps=len(steps)))

def instruction_line_lookup(source_code: str) -> dict[str,int | None]:
    import re
    rows=source_code.replace('\r\n','\n').split('\n');lookup={'initial':None}
    groups={'arreglo_valido':{'valid_entry':None,'valid_ptr':'return arreglo','valid_n':'return arreglo'},'obtener_minimo_maximo':{'minmax_entry':None,'helper_i_declare':'size_t i;','minmax_guard':'if (!arreglo_valido','min_init':'*minimo = arreglo[0]','max_init':'*minimo = arreglo[0]','scan_init':'for (i = 1;','scan_test':'for (i = 1;','scan_increment':'for (i = 1;','min_compare':'if (arreglo[i] <','min_assign':'if (arreglo[i] <','max_compare':'if (arreglo[i] >','max_assign':'if (arreglo[i] >','minmax_return':'return ORDENAMIENTO_OK;'},'ordenar_counting_sort':{'sort_entry':None,'declare':'int minimo, maximo;','valid_call':'if (!arreglo_valido','sort_guard':'if (!arreglo_valido','minmax_call':'if (!obtener_minimo_maximo','minmax_status':'if (!obtener_minimo_maximo','range_compute':'rango =','range_limit':'if (rango >','size_guard':'if (rango >','range_guard':'if (rango >','count_init':'conteo =','allocation_guard':'if (conteo == NULL)','fill_init':'for (i = 0; i < n;','fill_test':'for (i = 0; i < n;','count_fill':'for (i = 0; i < n;','fill_increment':'for (i = 0; i < n;','output_init':'indice = 0;','rebuild_init':'for (i = 0; i < rango;','rebuild_test':'for (i = 0; i < rango;','rebuild_increment':'for (i = 0; i < rango;','bucket_test':'while (conteo[i] > 0)','array_write':'while (conteo[i] > 0)','count_write':'while (conteo[i] > 0)','count_free':'free(conteo);','sort_return':'return ORDENAMIENTO_OK;'}}
    for name,tokens in groups.items():
        start=next(k for k,row in enumerate(rows) if re.match(r'\s*(?:static )?int '+name+r'\(',row));balance=0
        for end in range(start,len(rows)):
            balance+=rows[end].count('{')-rows[end].count('}')
            if end>start and balance==0:break
        for token,pattern in tokens.items():lookup[token]=start if pattern is None else next(k for k in range(start,end+1) if pattern in rows[k])
    return lookup

def instruction_pedagogy(raw: dict[str,Any],line_index: int | None,line_text: str) -> dict[str,Any]:
    presentation=deepcopy(raw);presentation['instruction_event']={**raw['instruction_event'],'i':0,'j':0};frame=typed_frame(presentation,line_index,line_text);calls=[]
    for name in raw['instruction_stack']:
        params={'arreglo':'arreglo del caller','n':len(raw['array_snapshot'])}
        if name=='obtener_minimo_maximo':params.update(minimo='&minimo (ordenar_counting_sort)',maximo='&maximo (ordenar_counting_sort)')
        calls.append(dict(function=name,parameters=params,continuation='retornar al caller conservando sus locales'))
    frame['call_stack']=calls;ctx=raw['counting_context'];frame['loop']=None;phase=ctx['phase']
    if phase:
        iteration=ctx['helper_i'] if phase=='scan' else ctx['i'];bound=len(raw['array_snapshot']) if phase!='rebuild' else ctx['rango']
        frame['loop']=dict(kind='for minimo/maximo' if phase=='scan' else 'while frecuencia' if raw['line_token'] in ('bucket_test','array_write','count_write') else 'for conteo' if phase=='fill' else 'for reconstruccion',iteration=iteration,bounds=[1 if phase=='scan' else 0,bound],exit=raw['line_token'] in ('scan_test','fill_test','rebuild_test','bucket_test') and raw['condition_result'] is False)
    if raw['line_token'] in ('min_compare','max_compare'):frame['concept']='comparison'
    holds=ctx['written']==ctx['consumed']+ctx['pending_decrement'] and (sum(v['count'] for v in ctx['buckets'])==ctx['filled']-ctx['consumed'] if ctx['live'] else True)
    text=f"Frecuencias escritas {ctx['filled']}; consumidas {ctx['consumed']}; valores reconstruidos {ctx['written']}."
    if ctx['pending_decrement']:text+=' La escritura ya termino; falta --conteo[i], no anticipar su efecto.'
    text+=' Reserva calloc viva y cero inicializada.' if ctx['live'] else ' Reserva liberada; no leer memoria.' if ctx['released'] else 'No hay reserva activa.'
    frame['invariant']=dict(text=text,indices=raw['sorted_indices'],holds=holds);return frame
