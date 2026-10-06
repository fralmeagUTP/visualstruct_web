"""Selection-only instruction events matching the downloaded C's evaluation order."""
from copy import deepcopy
from app.domain.sorting.intercambio_instructions import instruction_line_lookup as helper_lines
from app.domain.sorting.intercambio_instructions import instruction_pedagogy as typed_frame


def run_seleccion_trace(values):
    a = list(values)
    n = len(a)
    i = j = indice_menor = temporal = None
    declared = swap_declared = searching = False
    stack, steps = [], []
    aliases = None
    confirmed = set()
    comparisons = swaps = moves = 0

    def emit(token, function, action, condition=None, expression=''):
        variables = []
        if stack:
            variables.append(dict(name='n', type='size_t', value=n, scope='ordenar_seleccion', initialized=True))
        if declared and stack:
            variables.extend(dict(name=name, type='size_t', value=value, scope='ordenar_seleccion', initialized=value is not None) for name,value in [('i',i),('j',j),('indice_menor',indice_menor)])
        if swap_declared:
            variables.append(dict(name='temporal', type='int', value=temporal, scope='intercambiar', initialized=temporal is not None))
        previous = {(v['scope'],v['name']):v for v in steps[-1]['instruction_variables']} if steps else {}
        for variable in variables:
            old = previous.get((variable['scope'],variable['name']))
            variable['previous'] = old['value'] if old else None
            variable['changed'] = old is None or old['value'] != variable['value'] or old['initialized'] != variable['initialized']
        pointers = [dict(name=name, target=f'arreglo[{index}]', index=index, value=a[index], type='int *', scope='intercambiar') for name,index in zip(('a','b'),aliases)] if aliases else []
        steps.append(dict(step=len(steps)+1, line_token=token, action=action, array_snapshot=list(a), comparing_indices=[j,indice_menor] if token=='compare_min' else [], swapping_indices=list(aliases or []), sorted_indices=sorted(confirmed), active_range=[i,n-1] if i is not None and i<n else None, pivot_index=None, auxiliary_snapshot=None, temporaries={'temporal':temporal} if temporal is not None else {}, pointer_indices=list(aliases or []), console_output='', metrics=dict(comparisons=comparisons,swaps=swaps,moves=moves), instruction_variables=deepcopy(variables), instruction_stack=list(stack), instruction_pointers=pointers, source_function=function, condition_result=condition, condition_expression=expression, selection_context={'indice_menor':indice_menor if searching else None}, instruction_event=dict(token=token,function=function,i=i,j=j,indice_menor=indice_menor,temporal=temporal if swap_declared else None,a=aliases[0] if aliases else None,b=aliases[1] if aliases else None,comparisons=comparisons,swaps=swaps,moves=moves)))

    emit('initial',None,'Antes de llamar ordenar_seleccion; no se ha ejecutado una instrucción C.')
    stack.append('ordenar_seleccion')
    emit('sort_entry','ordenar_seleccion','Entrar en ordenar_seleccion.')
    declared = True
    emit('sort_declare','ordenar_seleccion','Declarar i, j e indice_menor size_t, sin inicializar.')
    emit('valid_call','ordenar_seleccion','Llamar arreglo_valido antes de decidir la guarda.')
    stack.append('arreglo_valido')
    emit('valid_entry','arreglo_valido','Entrar en arreglo_valido.')
    emit('valid_ptr','arreglo_valido','Evaluar arreglo != NULL.',True,'arreglo != NULL')
    emit('valid_n','arreglo_valido','Evaluar n > 0 por cortocircuito.',n>0,f'{n} > 0')
    stack.pop()
    emit('valid_return','arreglo_valido','Retornar la validación; termina su scope.')
    emit('sort_guard','ordenar_seleccion','Evaluar la guarda.',n==0,'!arreglo_valido(arreglo,n)')
    if not n:
        stack.clear(); declared=False
        emit('guard_return','ordenar_seleccion','Retornar sin ordenar por entrada vacía.')
    else:
        i=0
        emit('outer_init','ordenar_seleccion','Asignar i=0.')
        while True:
            test=i+1<n
            emit('outer_test','ordenar_seleccion','Evaluar i+1<n.',test,f'{i} + 1 < {n}')
            if not test: break
            indice_menor=i; searching=True
            emit('min_init','ordenar_seleccion','Asignar indice_menor=i.')
            j=i+1
            emit('inner_init','ordenar_seleccion','Asignar j=i+1.')
            while True:
                test=j<n
                emit('inner_test','ordenar_seleccion','Evaluar j<n.',test,f'{j} < {n}')
                if not test: break
                test=a[j]<a[indice_menor]; comparisons+=1
                emit('compare_min','ordenar_seleccion','Comparar sin anticipar la asignación del mínimo.',test,f'{a[j]} < {a[indice_menor]}')
                if test:
                    indice_menor=j
                    emit('min_set','ordenar_seleccion','Asignar indice_menor=j.')
                j+=1
                emit('inner_increment','ordenar_seleccion','Incrementar j antes de evaluar el ciclo.')
            searching=False
            test=indice_menor!=i
            emit('swap_decision','ordenar_seleccion','Evaluar si el mínimo requiere intercambio.',test,f'{indice_menor} != {i}')
            if test:
                emit('swap_call','ordenar_seleccion','Llamar intercambiar con dos alias del arreglo.')
                aliases=(i,indice_menor); stack.append('intercambiar')
                emit('swap_entry','intercambiar','Entrar en intercambiar; caller suspendido.')
                swap_declared=True; temporal=None
                emit('swap_declare','intercambiar','Declarar temporal int sin inicializar.')
                emit('swap_guard','intercambiar','Evaluar a==NULL || b==NULL.',False,'a == NULL || b == NULL')
                temporal=a[i]; moves+=1
                emit('swap_temp','intercambiar','Asignar temporal=*a; conservar el arreglo.')
                a[i]=a[indice_menor]; moves+=1
                emit('swap_assign_a','intercambiar','Asignar *a=*b; duplicación provisional.')
                a[indice_menor]=temporal; moves+=1; swaps+=1
                emit('swap_assign_b','intercambiar','Asignar *b=temporal; completar el intercambio.')
                stack.pop(); aliases=None; swap_declared=False; temporal=None
                emit('swap_return','intercambiar','Retorno void; retirar scope y alias del helper.')
                emit('swap_resume','ordenar_seleccion','Continuar después de intercambiar.')
            confirmed.add(i)
            emit('outer_complete','ordenar_seleccion','Completar la pasada y confirmar la posición i.')
            i+=1
            emit('outer_increment','ordenar_seleccion','Incrementar i antes de la prueba del ciclo.')
        confirmed=set(range(n)); stack.clear(); declared=False
        emit('sort_return','ordenar_seleccion','Retorno void al caller; el TAD no ejecuta printf.')
    return dict(steps=steps,final_state={'items':list(a)},metrics=dict(comparisons=comparisons,swaps=swaps,moves=moves,steps=len(steps)))


def instruction_line_lookup(source_code):
    import re
    lookup=helper_lines(source_code)
    rows=source_code.replace('\r\n','\n').split('\n')
    start=next(i for i,row in enumerate(rows) if re.match(r'\s*void ordenar_seleccion\(',row))
    balance=0
    for end in range(start,len(rows)):
        balance+=rows[end].count('{')-rows[end].count('}')
        if end>start and balance==0: break
    patterns={'sort_declare':'size_t i, j, indice_menor;', 'valid_call':'if (!arreglo_valido', 'sort_guard':'if (!arreglo_valido', 'guard_return':'if (!arreglo_valido', 'outer_init':'for (i =', 'outer_test':'for (i =', 'outer_increment':'for (i =', 'inner_init':'for (j =', 'inner_test':'for (j =', 'inner_increment':'for (j =', 'min_init':'indice_menor = i;', 'compare_min':'if (arreglo[j]', 'min_set':'if (arreglo[j]', 'swap_decision':'if (indice_menor != i)', 'swap_call':'if (indice_menor != i)', 'swap_resume':'if (indice_menor != i)'}
    lookup.update({token:next(i for i in range(start,end+1) if pattern in rows[i]) for token,pattern in patterns.items()})
    lookup.update(sort_entry=start,sort_return=end,outer_complete=end-1)
    return lookup


def instruction_pedagogy(raw,line_index,line_text):
    frame=typed_frame(raw,line_index,line_text)
    token=raw['line_token']; event=raw['instruction_event']
    if token=='compare_min': frame['concept']='comparison'
    for call in frame['call_stack']:
        call['continuation']='retornar al caller' if call['function']=='ordenar_seleccion' else 'continuar en ordenar_seleccion'
    inner=token.startswith('inner_') or token in {'compare_min','min_set'}
    outer=token.startswith(('outer_','swap_')) or token=='min_init'
    frame['loop']=None
    if inner or outer:
        frame['loop']=dict(kind=('for interno' if inner else 'for externo')+(' (caller suspendido)' if 'intercambiar' in raw['instruction_stack'] else ''),iteration=event['j'] if inner else event['i'],bounds=[event['i']+1 if inner else 0,len(raw['array_snapshot'])],exit=token in {'inner_test','outer_test'} and raw['condition_result'] is False)
    frame['invariant']['text']='Solo el prefijo de pasadas terminadas contiene valores definitivos; indice_menor conserva el índice asignado por C.'
    if raw['selection_context']['indice_menor'] is not None:
        frame['invariant']['text']+=' El candidato cambia al ejecutar la asignación posterior a una comparación verdadera.'
    if token=='swap_assign_a':
        frame['invariant']['text']+=' Hay duplicación provisional; temporal conserva el valor pendiente de escribir en *b.'
    return frame
