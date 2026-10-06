"""Instruction events for only the actual direct-interchange C implementation."""
from __future__ import annotations
from copy import deepcopy
from typing import Any


def run_intercambio_trace(values: list[int]) -> dict[str, Any]:
    """Execute the C order, including false tests and each partial swap write."""
    a = list(values)
    n = len(a)
    i: int | None = None
    j: int | None = None
    temporal: int | None = None
    declared = False
    swap_declared = False
    stack: list[str] = []
    steps: list[dict[str, Any]] = []
    comparisons = swaps = moves = 0
    aliases: tuple[int, int] | None = None
    confirmed: set[int] = set()

    def emit(token: str, function: str | None, text: str, condition: bool | None = None, expression: str = "") -> None:
        variables: list[dict[str, Any]] = []
        if stack:
            variables.append({'name':'n','type':'size_t','value':n,'scope':'ordenar_intercambio','initialized':True})
        if declared and stack:
            variables.extend({'name':name,'type':'size_t','value':value,'scope':'ordenar_intercambio','initialized':value is not None} for name,value in [('i',i),('j',j)])
        if swap_declared:
            variables.append({'name':'temporal','type':'int','value':temporal,'scope':'intercambiar','initialized':temporal is not None})
        pointers = []
        if aliases is not None:
            pointers = [{'name':name,'target':f'arreglo[{index}]','index':index,'value':a[index],'type':'int *','scope':'intercambiar'} for name,index in zip(('a','b'),aliases)]
        previous = { (v['scope'],v['name']):v for v in (steps[-1].get('instruction_variables',[]) if steps else []) }
        for variable in variables:
            old = previous.get((variable['scope'],variable['name']))
            variable['previous'] = old['value'] if old else None
            variable['changed'] = old is None or old['value'] != variable['value'] or old['initialized'] != variable['initialized']
        indices = [i,j] if i is not None and j is not None and i < n and j < n else []
        steps.append({'step':len(steps)+1,'line_token':token,'action':text,'array_snapshot':list(a),'comparing_indices':indices if token=='compare' else [],'swapping_indices':list(aliases or []) if token.startswith('swap_') else [],'sorted_indices':sorted(confirmed),'active_range':[i,n-1] if i is not None and i < n else None,'pivot_index':None,'auxiliary_snapshot':None,'temporaries':{'temporal':temporal} if temporal is not None else {},'pointer_indices':list(aliases or []),'console_output':'','metrics':{'comparisons':comparisons,'swaps':swaps,'moves':moves},'instruction_variables':deepcopy(variables),'instruction_stack':list(stack),'instruction_pointers':pointers,'source_function':function,'condition_result':condition,'condition_expression':expression,'instruction_event':{'token':token,'function':function,'i':i,'j':j,'temporal':temporal if swap_declared else None,'a':aliases[0] if aliases else None,'b':aliases[1] if aliases else None,'comparisons':comparisons,'swaps':swaps,'moves':moves}})

    emit('initial',None,'Antes de llamar ordenar_intercambio; no se ejecutó una instrucción C.')
    stack.append('ordenar_intercambio')
    emit('sort_entry','ordenar_intercambio','Entrar en ordenar_intercambio.')
    declared = True
    emit('sort_declare','ordenar_intercambio','Declarar i y j como size_t; aún no inicializados.')
    emit('valid_call','ordenar_intercambio','Llamar arreglo_valido antes de decidir la guarda.')
    stack.append('arreglo_valido')
    emit('valid_entry','arreglo_valido','Entrar en arreglo_valido con el mismo arreglo y n.')
    emit('valid_ptr','arreglo_valido','Evaluar arreglo != NULL.',True,'arreglo != NULL')
    emit('valid_n','arreglo_valido','Evaluar n > 0 por cortocircuito.',n>0,f'{n} > 0')
    stack.pop()
    emit('valid_return','arreglo_valido','Retornar el resultado de la validación; termina su scope.')
    emit('sort_guard','ordenar_intercambio','Evaluar !arreglo_valido(arreglo,n).',n==0,'!arreglo_valido(arreglo,n)')
    if n == 0:
        stack.clear();declared=False
        emit('guard_return','ordenar_intercambio','Retornar sin ordenar por entrada vacía.')
    else:
        i = 0
        emit('outer_init','ordenar_intercambio','Asignar i=0.')
        while True:
            test = i + 1 < n
            emit('outer_test','ordenar_intercambio','Evaluar i+1<n.',test,f'{i} + 1 < {n}')
            if not test:
                break
            j = i + 1
            emit('inner_init','ordenar_intercambio','Asignar j=i+1.')
            while True:
                test = j < n
                emit('inner_test','ordenar_intercambio','Evaluar j<n.',test,f'{j} < {n}')
                if not test:
                    confirmed.add(i)
                    break
                test = a[i] > a[j]
                comparisons += 1
                emit('compare','ordenar_intercambio','Comparar elementos sin cambiar el arreglo.',test,f'{a[i]} > {a[j]}')
                if test:
                    emit('swap_call','ordenar_intercambio','Llamar intercambiar con dos alias del arreglo.')
                    aliases=(i,j);stack.append('intercambiar')
                    emit('swap_entry','intercambiar','Entrar en intercambiar; a y b apuntan al arreglo original.')
                    swap_declared=True;temporal=None
                    emit('swap_declare','intercambiar','Declarar temporal int, todavía no inicializado.')
                    emit('swap_guard','intercambiar','Evaluar a==NULL || b==NULL.',False,'a == NULL || b == NULL')
                    temporal=a[i];moves+=1
                    emit('swap_temp','intercambiar','Asignar temporal=*a; el arreglo se conserva.')
                    a[i]=a[j];moves+=1
                    emit('swap_assign_a','intercambiar','Asignar *a=*b; las dos posiciones pueden coincidir provisionalmente.')
                    a[j]=temporal;moves+=1;swaps+=1
                    emit('swap_assign_b','intercambiar','Asignar *b=temporal y completar el intercambio.')
                    stack.pop();aliases=None;swap_declared=False;temporal=None
                    emit('swap_return','intercambiar','Retorno void: termina el scope y sus alias locales.')
                    emit('swap_resume','ordenar_intercambio','Continuar después de la llamada a intercambiar.')
                j += 1
                emit('inner_increment','ordenar_intercambio','Incrementar j, incluso hasta n antes de la prueba falsa.')
            i += 1
            emit('outer_increment','ordenar_intercambio','Incrementar i antes de evaluar otra pasada.')
        confirmed=set(range(n));stack.clear();declared=False
        emit('sort_return','ordenar_intercambio','Retorno void al caller; ninguna salida printf en el TAD.')
    return {'steps':steps,'final_state':{'items':list(a)},'metrics':{'comparisons':comparisons,'swaps':swaps,'moves':moves,'steps':len(steps)}}


def instruction_line_lookup(source_code: str) -> dict[str, int | None]:
    """Resolve within actual function bodies, including implicit void returns."""
    import re
    rows = source_code.replace("\r\n", "\n").split("\n")
    bodies = {}
    for name in ('ordenar_intercambio', 'arreglo_valido', 'intercambiar'):
        start = next((idx for idx, row in enumerate(rows) if re.match(r"\s*(?:static\s+)?(?:void|int)\s+" + name + r"\(", row)), None)
        if start is None:
            continue
        balance = 0
        for end in range(start, len(rows)):
            balance += rows[end].count('{') - rows[end].count('}')
            if end > start and balance == 0:
                bodies[name] = (start, end)
                break
    groups = {
        'ordenar_intercambio': {'sort_entry':None,'sort_declare':'size_t i, j;', 'valid_call':'if (!arreglo_valido', 'sort_guard':'if (!arreglo_valido', 'guard_return':'if (!arreglo_valido', 'outer_init':'for (i =', 'outer_test':'for (i =', 'outer_increment':'for (i =', 'inner_init':'for (j =', 'inner_test':'for (j =', 'inner_increment':'for (j =', 'compare':'if (arreglo[i]', 'swap_call':'if (arreglo[i]', 'swap_resume':'if (arreglo[i]', 'sort_return':'}'},
        'arreglo_valido': {'valid_entry':None,'valid_ptr':'return arreglo', 'valid_n':'return arreglo', 'valid_return':'return arreglo'},
        'intercambiar': {'swap_entry':None, 'swap_declare':'int temporal;', 'swap_guard':'if (a == NULL', 'swap_temp':'temporal = *a;', 'swap_assign_a':'*a = *b;', 'swap_assign_b':'*b = temporal;', 'swap_return':'}'},
    }
    lookup = {'initial':None}
    for name, tokens in groups.items():
        bounds = bodies.get(name)
        for token, pattern in tokens.items():
            if bounds is None:
                lookup[token] = None
            else:
                start, end = bounds
                lookup[token] = start if pattern is None else end if pattern == '}' else next((idx for idx in range(start, end+1) if pattern in rows[idx]), None)
    return lookup


def instruction_pedagogy(raw: dict[str, Any], line_index: int | None, line_text: str) -> dict[str, Any]:
    """Present observed locals; do not reconstruct indices from highlights."""
    token = raw['line_token']
    condition = raw['condition_result']
    concept = 'condition' if condition is not None else 'return' if token.endswith('return') else 'call' if token.endswith(('call','entry','resume')) else 'phase' if token == 'initial' else 'assignment'
    if token == 'compare':
        concept = 'comparison'
    variables = deepcopy(raw['instruction_variables'])
    for variable in variables:
        variable['meaning'] = variable['scope'] + ('; sin inicializar' if not variable['initialized'] else '; valor tras la instrucción')
    array = raw['array_snapshot']
    stack = []
    for function in raw['instruction_stack']:
        parameters = {'arreglo':'arreglo del caller','n':len(array)} if function != 'intercambiar' else {p['name']:p['target'] for p in raw['instruction_pointers']}
        stack.append({'function':function,'parameters':parameters,'continuation':'retornar al caller' if function=='ordenar_intercambio' else 'continuar en ordenar_intercambio'})
    event = raw['instruction_event']
    inner = token.startswith('inner_') or token == 'compare' or token.startswith('swap_')
    loop = None
    if inner or token.startswith('outer_'):
        suspended = 'intercambiar' in raw['instruction_stack']
        loop = {
            'kind':('for interno' if inner else 'for externo') + (' (caller suspendido)' if suspended else ''),
            'iteration':event['j'] if inner else event['i'],
            'bounds':[event['i']+1 if inner else 0,len(array)],
            'exit':token in {'inner_test','outer_test'} and condition is False,
        }
    action = raw['action']
    invariant = 'El prefijo confirmado conserva sus valores definitivos.'
    if token=='swap_assign_a':
        invariant += ' El arreglo tiene una duplicación provisional; temporal conserva el valor que falta hasta *b=temporal.'
    return {'schema_version':1,'concept':concept,'phase':{'id':token,'label':token.replace('_',' '),'goal':action},'condition':None if condition is None else {'expression':raw['condition_expression'],'result':condition,'consequence':'Continuar por la rama verdadera.' if condition else 'Continuar por la rama falsa.'},'variables':variables,'call_stack':stack,'loop':loop,'pointers':deepcopy(raw['instruction_pointers']),'invariant':{'text':invariant,'indices':raw['sorted_indices'],'holds':True},'narration':{'basic':action,'intermediate':action + ' Los valores corresponden a esta transición, sin anticipar la siguiente.','advanced':action + ' C: '+ (line_text.strip() or 'antes de la llamada; sin instrucción C ejecutada')},'source':{'line_token':token,'line_index':line_index,'line_text':line_text,'function':raw['source_function']}}
