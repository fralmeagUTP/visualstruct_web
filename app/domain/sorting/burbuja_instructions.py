"""Improved-bubble instruction trace following the actual C's flag and break order."""
from __future__ import annotations
from copy import deepcopy
from typing import Any
from app.domain.sorting.intercambio_instructions import instruction_line_lookup as helper_lines
from app.domain.sorting.intercambio_instructions import instruction_pedagogy as typed_frame


def run_burbuja_trace(values: list[int]) -> dict[str, Any]:
    """Observe clauses, helper lifetimes, partial writes and early exit without new C."""
    a=list(values);n=len(a)
    pasada: int | None=None
    j: int | None=None
    hubo_intercambio: int | None=None
    temporal: int | None=None
    indices_declared=flag_declared=swap_declared=False
    aliases: tuple[int,int] | None=None
    stack: list[str]=[]
    steps: list[dict[str,Any]]=[]
    confirmed: set[int]=set()
    comparisons=swaps=moves=0

    def emit(token: str, function: str | None, action: str, condition: bool | None=None, expression: str='') -> None:
        variables=[]
        if stack:
            variables.append(dict(name='n',type='size_t',value=n,scope='ordenar_burbuja',initialized=True))
        if indices_declared and stack:
            variables.extend(dict(name=name,type='size_t',value=value,scope='ordenar_burbuja',initialized=value is not None) for name,value in [('pasada',pasada),('j',j)])
        if flag_declared and stack:
            variables.append(dict(name='hubo_intercambio',type='int',value=hubo_intercambio,scope='ordenar_burbuja',initialized=hubo_intercambio is not None))
        if swap_declared:
            variables.append(dict(name='temporal',type='int',value=temporal,scope='intercambiar',initialized=temporal is not None))
        previous={(v['scope'],v['name']):v for v in steps[-1]['instruction_variables']} if steps else {}
        for variable in variables:
            old=previous.get((variable['scope'],variable['name']))
            variable['previous']=old['value'] if old else None
            variable['changed']=old is None or old['value']!=variable['value'] or old['initialized']!=variable['initialized']
        pointers=[dict(name=name,target=f'arreglo[{index}]',index=index,value=a[index],type='int *',scope='intercambiar') for name,index in zip(('a','b'),aliases)] if aliases else []
        neighbor=[j,j+1] if j is not None and pasada is not None and j+1<n-pasada and stack else []
        steps.append({
            'step':len(steps)+1,'line_token':token,'action':action,'array_snapshot':list(a),
            'comparing_indices':neighbor if token=='compare' else [],'swapping_indices':list(aliases or []),
            'sorted_indices':sorted(confirmed),'active_range':[0,n-pasada-1] if pasada is not None and stack and token!='early_break' else None,
            'pivot_index':None,'auxiliary_snapshot':None,'temporaries':{'temporal':temporal} if temporal is not None and swap_declared else {},
            'pointer_indices':list(aliases or []),'console_output':'','metrics':dict(comparisons=comparisons,swaps=swaps,moves=moves),
            'instruction_variables':deepcopy(variables),'instruction_stack':list(stack),'instruction_pointers':pointers,
            'source_function':function,'condition_result':condition,'condition_expression':expression,
            'bubble_context':{'pasada':pasada if stack else None,'j':j if stack else None,'hubo_intercambio':hubo_intercambio if stack else None,'flag_declared':flag_declared and bool(stack),'neighbors':neighbor},
            'instruction_event':dict(token=token,function=function,pasada=pasada,j=j,hubo_intercambio=hubo_intercambio,temporal=temporal if swap_declared else None,a=aliases[0] if aliases else None,b=aliases[1] if aliases else None,comparisons=comparisons,swaps=swaps,moves=moves),
        })

    emit('initial',None,'Antes de llamar ordenar_burbuja; ninguna instrucción C ejecutada.')
    stack.append('ordenar_burbuja')
    emit('sort_entry','ordenar_burbuja','Entrar en ordenar_burbuja.')
    indices_declared=True
    emit('sort_declare_indices','ordenar_burbuja','Declarar pasada y j size_t sin inicializar.')
    flag_declared=True
    emit('sort_declare_flag','ordenar_burbuja','Declarar hubo_intercambio int sin inicializar.')
    emit('valid_call','ordenar_burbuja','Llamar arreglo_valido antes de decidir la guarda.')
    stack.append('arreglo_valido')
    emit('valid_entry','arreglo_valido','Entrar en arreglo_valido.')
    emit('valid_ptr','arreglo_valido','Evaluar arreglo != NULL.',True,'arreglo != NULL')
    emit('valid_n','arreglo_valido','Evaluar n>0 por cortocircuito.',n>0,f'{n} > 0')
    stack.pop()
    emit('valid_return','arreglo_valido','Retornar la validación y retirar scope del helper.')
    emit('sort_guard','ordenar_burbuja','Evaluar !arreglo_valido(arreglo,n).',n==0,'!arreglo_valido(arreglo,n)')
    if not n:
        stack.clear();indices_declared=flag_declared=False
        emit('guard_return','ordenar_burbuja','Retornar sin procesar arreglo vacío.')
    else:
        pasada=0
        emit('outer_init','ordenar_burbuja','Asignar pasada=0.')
        while True:
            test=pasada+1<n
            emit('outer_test','ordenar_burbuja','Evaluar pasada+1<n.',test,f'{pasada} + 1 < {n}')
            if not test:break
            hubo_intercambio=0
            emit('flag_reset','ordenar_burbuja','Asignar hubo_intercambio=0 al comenzar la pasada.')
            j=0
            emit('inner_init','ordenar_burbuja','Asignar j=0.')
            while True:
                test=j+1<n-pasada
                if not test:confirmed.add(n-pasada-1)
                emit('inner_test','ordenar_burbuja','Evaluar j+1<n-pasada.',test,f'{j} + 1 < {n} - {pasada}')
                if not test:break
                test=a[j]>a[j+1];comparisons+=1
                emit('compare','ordenar_burbuja','Comparar vecinos sin anticipar el intercambio ni la bandera.',test,f'{a[j]} > {a[j+1]}')
                if test:
                    emit('swap_call','ordenar_burbuja','Llamar intercambiar con alias de los dos vecinos.')
                    aliases=(j,j+1);stack.append('intercambiar')
                    emit('swap_entry','intercambiar','Entrar en intercambiar; el for interno del caller está suspendido.')
                    swap_declared=True;temporal=None
                    emit('swap_declare','intercambiar','Declarar temporal int sin inicializar.')
                    emit('swap_guard','intercambiar','Evaluar a==NULL || b==NULL.',False,'a == NULL || b == NULL')
                    temporal=a[j];moves+=1
                    emit('swap_temp','intercambiar','Asignar temporal=*a; conservar el arreglo.')
                    a[j]=a[j+1];moves+=1
                    emit('swap_assign_a','intercambiar','Asignar *a=*b; duplicación provisional con temporal preservado.')
                    a[j+1]=temporal;moves+=1;swaps+=1
                    emit('swap_assign_b','intercambiar','Asignar *b=temporal; completar el intercambio.')
                    stack.pop();aliases=None;swap_declared=False;temporal=None
                    emit('swap_return','intercambiar','Retorno void; retirar temporal y alias locales del helper.')
                    emit('swap_resume','ordenar_burbuja','Continuar después de intercambiar.')
                    hubo_intercambio=1
                    emit('flag_set','ordenar_burbuja','Asignar hubo_intercambio=1 después del retorno del helper.')
                j+=1
                emit('inner_increment','ordenar_burbuja','Ejecutar ++j antes de la prueba del for interno.')
            stop=not hubo_intercambio
            emit('stop_test','ordenar_burbuja','Evaluar !hubo_intercambio después de completar el for interno.',stop,f'!{hubo_intercambio}')
            if stop:
                confirmed=set(range(n))
                emit('early_break','ordenar_burbuja','Ejecutar break: salir sin incrementar pasada ni inventar otra prueba exterior.')
                break
            emit('outer_complete','ordenar_burbuja','Cerrar cuerpo exterior conservando j y la bandera en su scope de función.')
            pasada+=1
            emit('outer_increment','ordenar_burbuja','Ejecutar ++pasada antes de la prueba exterior.')
        confirmed=set(range(n));stack.clear();indices_declared=flag_declared=False
        emit('sort_return','ordenar_burbuja','Retorno void al caller; retirar locales, sin printf propio del TAD.')
    return dict(steps=steps,final_state={'items':list(a)},metrics=dict(comparisons=comparisons,swaps=swaps,moves=moves,steps=len(steps)))


def instruction_line_lookup(source_code: str) -> dict[str, int | None]:
    """Resolve all bubble/flag/helper events inside the actual function bodies."""
    import re
    lookup=helper_lines(source_code)
    rows=source_code.replace('\r\n','\n').split('\n')
    start=next(i for i,row in enumerate(rows) if re.match(r'\s*void ordenar_burbuja\(',row))
    balance=0
    for end in range(start,len(rows)):
        balance+=rows[end].count('{')-rows[end].count('}')
        if end>start and balance==0:break
    patterns={'sort_declare_indices':'size_t pasada, j;', 'sort_declare_flag':'int hubo_intercambio;', 'valid_call':'if (!arreglo_valido', 'sort_guard':'if (!arreglo_valido', 'guard_return':'if (!arreglo_valido', 'outer_init':'for (pasada =', 'outer_test':'for (pasada =', 'outer_increment':'for (pasada =', 'flag_reset':'hubo_intercambio = 0;', 'inner_init':'for (j =', 'inner_test':'for (j =', 'inner_increment':'for (j =', 'compare':'if (arreglo[j]', 'swap_call':'intercambiar(&arreglo[j]', 'swap_resume':'intercambiar(&arreglo[j]', 'flag_set':'hubo_intercambio = 1;', 'stop_test':'if (!hubo_intercambio)', 'early_break':'if (!hubo_intercambio)'}
    lookup.update({token:next(i for i in range(start,end+1) if pattern in rows[i]) for token,pattern in patterns.items()})
    lookup.update(sort_entry=start,sort_return=end,outer_complete=end-1)
    return lookup


def instruction_pedagogy(raw: dict[str, Any], line_index: int | None, line_text: str) -> dict[str, Any]:
    """Reuse typed presentation without deriving aliases or flag values from highlights."""
    presentation=dict(raw);presentation['instruction_event']={**raw['instruction_event'],'i':raw['instruction_event']['pasada']}
    frame=typed_frame(presentation,line_index,line_text)
    token=raw['line_token'];event=raw['instruction_event'];n=len(raw['array_snapshot'])
    for call in frame['call_stack']:
        call['continuation']='retornar al caller' if call['function']=='ordenar_burbuja' else 'continuar en ordenar_burbuja'
    inner=token.startswith(('inner_','swap_')) or token in {'compare','flag_set'}
    outer=token.startswith('outer_') or token in {'flag_reset','stop_test','early_break'}
    frame['loop']=None
    if inner or outer:
        frame['loop']=dict(kind=('for interno' if inner else 'for externo')+(' (caller suspendido)' if 'intercambiar' in raw['instruction_stack'] else ''),iteration=event['j'] if inner else event['pasada'],bounds=[0,n-event['pasada']] if inner else [0,n],exit=(token in {'inner_test','outer_test'} and raw['condition_result'] is False) or token=='early_break')
    frame['invariant']['text']='El sufijo de pasadas completadas contiene valores definitivos; la bandera solo cambia en sus asignaciones C.'
    if token=='swap_assign_a':frame['invariant']['text']+=' El arreglo tiene valores duplicados provisionales; temporal conserva el valor pendiente para *b.'
    return frame
