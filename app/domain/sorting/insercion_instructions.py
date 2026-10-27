"""Instruction events for insertion's actual C clauses, local scopes and shifts."""
from __future__ import annotations
from copy import deepcopy
from typing import Any
from app.domain.sorting.intercambio_instructions import instruction_line_lookup as helper_lines
from app.domain.sorting.intercambio_instructions import instruction_pedagogy as typed_frame


def run_insercion_trace(values: list[int]) -> dict[str, Any]:
    """Follow C evaluation order, preserving the real array during partial shifts."""
    a=list(values); n=len(a)
    i: int | None=None
    j: int | None=None
    clave: int | None=None
    declared=False
    stack: list[str]=[]
    steps: list[dict[str, Any]]=[]
    processed: set[int]=set()
    comparisons=moves=0

    def emit(token: str, function: str | None, action: str, condition: bool | None=None, expression: str='') -> None:
        variables=[]
        if stack:
            variables.append(dict(name='n',type='size_t',value=n,scope='ordenar_insercion',initialized=True))
        if declared and stack:
            variables.append(dict(name='i',type='size_t',value=i,scope='ordenar_insercion',initialized=i is not None))
        if clave is not None:
            variables.append(dict(name='clave',type='int',value=clave,scope='ordenar_insercion:cuerpo_for',initialized=True))
        if j is not None:
            variables.append(dict(name='j',type='size_t',value=j,scope='ordenar_insercion:cuerpo_for',initialized=True))
        previous={(v['scope'],v['name']):v for v in steps[-1]['instruction_variables']} if steps else {}
        for variable in variables:
            old=previous.get((variable['scope'],variable['name']))
            variable['previous']=old['value'] if old else None
            variable['changed']=old is None or old['value']!=variable['value'] or old['initialized']!=variable['initialized']
        steps.append({
            'step':len(steps)+1,'line_token':token,'action':action,'array_snapshot':list(a),
            'comparing_indices':[j-1] if token=='while_compare' else [],'swapping_indices':[],
            # A processed insertion prefix is sorted, but may move on a later pass.
            # Reserve globally final colors for the actual final return.
            'sorted_indices':list(range(n)) if token=='sort_return' else [],
            'active_range':[0,i] if i is not None and i<n else None,'pivot_index':None,
            'auxiliary_snapshot':None,'temporaries':{'clave':clave} if clave is not None else {},
            'pointer_indices':[],'console_output':'','metrics':dict(comparisons=comparisons,swaps=0,moves=moves),
            'instruction_variables':deepcopy(variables),'instruction_stack':list(stack),'instruction_pointers':[],
            'source_function':function,'condition_result':condition,'condition_expression':expression,
            'insertion_context':{'clave':clave,'j':j,'processed_indices':sorted(processed)},
            'instruction_event':dict(token=token,function=function,i=i,j=j,clave=clave,comparisons=comparisons,moves=moves),
        })

    emit('initial',None,'Antes de llamar ordenar_insercion; ninguna instrucción C ejecutada.')
    stack.append('ordenar_insercion')
    emit('sort_entry','ordenar_insercion','Entrar en ordenar_insercion.')
    declared=True
    emit('sort_declare','ordenar_insercion','Declarar i size_t sin inicializar.')
    emit('valid_call','ordenar_insercion','Llamar arreglo_valido antes de la guarda.')
    stack.append('arreglo_valido')
    emit('valid_entry','arreglo_valido','Entrar en arreglo_valido.')
    emit('valid_ptr','arreglo_valido','Evaluar arreglo != NULL.',True,'arreglo != NULL')
    emit('valid_n','arreglo_valido','Evaluar n>0 por cortocircuito.',n>0,f'{n} > 0')
    stack.pop()
    emit('valid_return','arreglo_valido','Retornar validación y retirar scope del helper.')
    emit('sort_guard','ordenar_insercion','Evaluar !arreglo_valido(arreglo,n).',n==0,'!arreglo_valido(arreglo,n)')
    if not n:
        stack.clear();declared=False
        emit('guard_return','ordenar_insercion','Retornar sin ordenar por entrada vacía.')
    else:
        i=1;processed={0}
        emit('outer_init','ordenar_insercion','Asignar i=1; el prefijo de un elemento está ordenado.')
        while True:
            test=i<n
            emit('outer_test','ordenar_insercion','Evaluar i<n.',test,f'{i} < {n}')
            if not test:break
            clave=a[i];moves+=1
            emit('key_take','ordenar_insercion','Declarar e inicializar clave=arreglo[i]; conservar el arreglo.')
            j=i
            emit('j_init','ordenar_insercion','Declarar e inicializar j=i.')
            while True:
                left=j>0
                emit('while_left','ordenar_insercion','Evaluar primero j>0.',left,f'{j} > 0')
                test=False
                if left:
                    test=a[j-1]>clave;comparisons+=1
                    emit('while_compare','ordenar_insercion','Comparar arreglo[j-1] con clave, sin modificar índices.',test,f'{a[j-1]} > {clave}')
                emit('while_test','ordenar_insercion','Evaluar la condición compuesta; omitir acceso si j==0.',test,'j > 0 && arreglo[j - 1] > clave')
                if not test:break
                a[j]=a[j-1];moves+=1
                emit('shift','ordenar_insercion','Asignar arreglo[j]=arreglo[j-1]; duplicación provisional, clave conservada.')
                j-=1
                emit('j_decrement','ordenar_insercion','Ejecutar --j; el arreglo permanece igual.')
            a[j]=clave;moves+=1
            emit('key_write','ordenar_insercion','Asignar arreglo[j]=clave; completar la inserción.')
            processed=set(range(i+1));j=None;clave=None
            emit('body_exit','ordenar_insercion','Cerrar cuerpo del for; retirar clave/j, conservar i.')
            i+=1
            emit('outer_increment','ordenar_insercion','Ejecutar ++i antes de la prueba exterior.')
        stack.clear();declared=False
        emit('sort_return','ordenar_insercion','Retorno void al caller; el TAD no ejecuta printf.')
    return dict(steps=steps,final_state={'items':list(a)},metrics=dict(comparisons=comparisons,swaps=0,moves=moves,steps=len(steps)))


def instruction_line_lookup(source_code: str) -> dict[str, int | None]:
    """Map tokens within real C functions, including the outer lexical closing brace."""
    import re
    lookup=helper_lines(source_code)
    rows=source_code.replace('\r\n','\n').split('\n')
    start=next(i for i,row in enumerate(rows) if re.match(r'\s*void ordenar_insercion\(',row))
    balance=0
    for end in range(start,len(rows)):
        balance+=rows[end].count('{')-rows[end].count('}')
        if end>start and balance==0:break
    patterns={'sort_declare':'size_t i;', 'valid_call':'if (!arreglo_valido', 'sort_guard':'if (!arreglo_valido', 'guard_return':'if (!arreglo_valido', 'outer_init':'for (i =', 'outer_test':'for (i =', 'outer_increment':'for (i =', 'key_take':'int clave =', 'j_init':'size_t j =', 'while_left':'while (j >', 'while_compare':'while (j >', 'while_test':'while (j >', 'shift':'arreglo[j] = arreglo[j - 1];', 'j_decrement':'--j;', 'key_write':'arreglo[j] = clave;'}
    lookup.update({token:next(i for i in range(start,end+1) if pattern in rows[i]) for token,pattern in patterns.items()})
    lookup.update(sort_entry=start,sort_return=end,body_exit=end-1)
    return lookup


def instruction_pedagogy(raw: dict[str, Any], line_index: int | None, line_text: str) -> dict[str, Any]:
    """Render actual locals and distinguish the while operands from loop exit."""
    frame=typed_frame(raw,line_index,line_text)
    token=raw['line_token'];event=raw['instruction_event'];context=raw['insertion_context']
    if token=='while_compare':frame['concept']='comparison'
    for call in frame['call_stack']:
        call['continuation']='retornar al caller' if call['function']=='ordenar_insercion' else 'continuar en ordenar_insercion'
    inner=token.startswith('while_') or token in {'shift','j_decrement'}
    outer=token.startswith('outer_') or token in {'key_take','j_init','key_write','body_exit'}
    frame['loop']=None
    if inner or outer:
        frame['loop']=dict(kind='while interno' if inner else 'for externo',iteration=event['j'] if inner else event['i'],bounds=[0,event['i']] if inner else [1,len(raw['array_snapshot'])],exit=token in {'while_test','outer_test'} and raw['condition_result'] is False)
    frame['invariant']={'text':'El prefijo de pasadas terminadas está ordenado; sus valores aún pueden desplazarse por una clave futura. El arreglo mantiene valores reales, sin celda vacía ficticia.','indices':context['processed_indices'],'holds':True}
    if token in {'shift','j_decrement'}:
        frame['invariant']['text']+=' La duplicación provisional no elimina la clave: su valor permanece en el local int clave.'
    return frame
