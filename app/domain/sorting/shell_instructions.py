"""Shell events following actual C clauses, lexical scopes and partial writes."""
from __future__ import annotations
from copy import deepcopy
from typing import Any
from app.domain.sorting.intercambio_instructions import instruction_line_lookup as helper_lines
from app.domain.sorting.intercambio_instructions import instruction_pedagogy as typed_frame

def run_shell_trace(values: list[int]) -> dict[str, Any]:
    """Preserve C's gap division, short circuit and live local values."""
    a=list(values);n=len(a)
    intervalo: int | None=None
    i: int | None=None
    j: int | None=None
    temporal: int | None=None
    gap_declared=i_declared=False
    stack: list[str]=[]
    steps: list[dict[str,Any]]=[]
    comparisons=moves=0
    def emit(token: str,function: str | None,action: str,condition: bool | None=None,expression: str='') -> None:
        variables=[]
        if stack: variables.append(dict(name='n',type='size_t',value=n,scope='ordenar_shell',initialized=True))
        if gap_declared and stack:variables.append(dict(name='intervalo',type='size_t',value=intervalo,scope='ordenar_shell',initialized=intervalo is not None))
        if i_declared:variables.append(dict(name='i',type='size_t',value=i,scope='ordenar_shell:cuerpo_intervalo',initialized=i is not None))
        for name,ctype,value in [('temporal','int',temporal),('j','size_t',j)]:
            if value is not None:variables.append(dict(name=name,type=ctype,value=value,scope='ordenar_shell:cuerpo_i',initialized=True))
        previous={(v['scope'],v['name']):v for v in steps[-1]['instruction_variables']} if steps else {}
        for v in variables:
            old=previous.get((v['scope'],v['name']));v['previous']=old['value'] if old else None;v['changed']=old is None or old['value']!=v['value'] or old['initialized']!=v['initialized']
        group=list(range(i%intervalo,n,intervalo)) if intervalo and i is not None and i<n and stack else []
        steps.append({'step':len(steps)+1,'line_token':token,'action':action,'array_snapshot':list(a),
          'comparing_indices':[j-intervalo] if token=='while_compare' else [],'swapping_indices':[],
          'sorted_indices':list(range(n)) if token=='sort_return' else [],'active_range':[0,n-1] if stack and intervalo else None,
          'pivot_index':None,'auxiliary_snapshot':None,'temporaries':{'temporal':temporal} if temporal is not None else {},'pointer_indices':[],'console_output':'',
          'metrics':dict(comparisons=comparisons,swaps=0,moves=moves),'instruction_variables':deepcopy(variables),'instruction_stack':list(stack),'instruction_pointers':[],
          'source_function':function,'condition_result':condition,'condition_expression':expression,
          'shell_context':{'intervalo':intervalo if stack else None,'gap_declared':gap_declared and bool(stack),'i':i,'i_declared':i_declared,'j':j,'temporal':temporal,'group':group,'gap_completed':intervalo if token=='gap_body_exit' else None},
          'instruction_event':dict(token=token,function=function,intervalo=intervalo,i=i,j=j,temporal=temporal,comparisons=comparisons,moves=moves)})
    emit('initial',None,'Antes de llamar ordenar_shell; ninguna instruccion C ejecutada.')
    stack.append('ordenar_shell');emit('sort_entry','ordenar_shell','Entrar en ordenar_shell.')
    gap_declared=True;emit('gap_declare','ordenar_shell','Declarar intervalo size_t sin inicializar.')
    emit('valid_call','ordenar_shell','Llamar arreglo_valido antes de decidir la guarda.')
    stack.append('arreglo_valido');emit('valid_entry','arreglo_valido','Entrar en arreglo_valido.')
    emit('valid_ptr','arreglo_valido','Evaluar arreglo != NULL.',True,'arreglo != NULL')
    emit('valid_n','arreglo_valido','Evaluar n>0 por cortocircuito.',n>0,f'{n} > 0')
    stack.pop();emit('valid_return','arreglo_valido','Retornar validacion y retirar el scope del helper.')
    emit('sort_guard','ordenar_shell','Evaluar !arreglo_valido(arreglo,n).',n==0,'!arreglo_valido(arreglo,n)')
    if not n:
        stack.clear();gap_declared=False;emit('guard_return','ordenar_shell','Retornar sin procesar entrada vacia.')
    else:
        intervalo=n//2;emit('gap_init','ordenar_shell','Asignar intervalo=n/2 con division entera size_t.')
        while True:
            test=intervalo>0;emit('gap_test','ordenar_shell','Evaluar intervalo>0.',test,f'{intervalo} > 0')
            if not test:break
            i_declared=True;i=None;emit('i_declare','ordenar_shell','Declarar i size_t en el cuerpo del intervalo, sin inicializar.')
            i=intervalo;emit('i_init','ordenar_shell','Asignar i=intervalo.')
            while True:
                test=i<n;emit('i_test','ordenar_shell','Evaluar i<n.',test,f'{i} < {n}')
                if not test:break
                temporal=a[i];moves+=1;emit('temp_take','ordenar_shell','Declarar e inicializar temporal=arreglo[i]; conservar el arreglo.')
                j=i;emit('j_init','ordenar_shell','Declarar e inicializar j=i.')
                while True:
                    left=j>=intervalo;emit('while_left','ordenar_shell','Evaluar primero j>=intervalo.',left,f'{j} >= {intervalo}')
                    test=False
                    if left:
                        test=a[j-intervalo]>temporal;comparisons+=1
                        emit('while_compare','ordenar_shell','Comparar arreglo[j-intervalo] con temporal.',test,f'{a[j-intervalo]} > {temporal}')
                    emit('while_test','ordenar_shell','Evaluar resultado compuesto; omitir acceso si j<intervalo.',test,'j >= intervalo && arreglo[j - intervalo] > temporal')
                    if not test:break
                    a[j]=a[j-intervalo];moves+=1;emit('shift','ordenar_shell','Asignar arreglo[j]=arreglo[j-intervalo]; duplicacion provisional, temporal conservado.')
                    j-=intervalo;emit('j_subtract','ordenar_shell','Ejecutar j-=intervalo; el arreglo permanece igual.')
                a[j]=temporal;moves+=1;emit('temp_write','ordenar_shell','Asignar arreglo[j]=temporal; completar esta insercion.')
                temporal=None;j=None;emit('inner_body_exit','ordenar_shell','Cerrar cuerpo de i; retirar temporal y j, conservar i/intervalo.')
                i+=1;emit('i_increment','ordenar_shell','Ejecutar ++i antes de su prueba.')
            i=None;i_declared=False;emit('gap_body_exit','ordenar_shell','Cerrar cuerpo del intervalo; retirar i. Los grupos por este intervalo estan ordenados.')
            intervalo//=2;emit('gap_divide','ordenar_shell','Ejecutar intervalo/=2 antes de la siguiente prueba.')
        stack.clear();gap_declared=False;emit('sort_return','ordenar_shell','Retorno void al caller; retirar intervalo, sin printf del TAD.')
    return dict(steps=steps,final_state={'items':list(a)},metrics=dict(comparisons=comparisons,swaps=0,moves=moves,steps=len(steps)))

def instruction_line_lookup(source_code: str) -> dict[str,int | None]:
    """Resolve Shell-specific clauses and closing braces inside actual C."""
    import re
    lookup=helper_lines(source_code);rows=source_code.replace('\r\n','\n').split('\n')
    start=next(i for i,row in enumerate(rows) if re.match(r'\s*void ordenar_shell\(',row));balance=0
    for end in range(start,len(rows)):
        balance+=rows[end].count('{')-rows[end].count('}')
        if end>start and balance==0:break
    patterns={'gap_declare':'size_t intervalo;', 'valid_call':'if (!arreglo_valido', 'sort_guard':'if (!arreglo_valido','guard_return':'if (!arreglo_valido', 'gap_init':'for (intervalo =', 'gap_test':'for (intervalo =', 'gap_divide':'for (intervalo =', 'i_declare':'size_t i;', 'i_init':'for (i =', 'i_test':'for (i =', 'i_increment':'for (i =', 'temp_take':'int temporal =', 'j_init':'size_t j =', 'while_left':'while (j >=', 'while_compare':'while (j >=', 'while_test':'while (j >=', 'shift':'arreglo[j] = arreglo[j - intervalo];', 'j_subtract':'j -= intervalo;', 'temp_write':'arreglo[j] = temporal;'}
    lookup.update({token:next(i for i in range(start,end+1) if pattern in rows[i]) for token,pattern in patterns.items()});lookup.update(sort_entry=start,sort_return=end,inner_body_exit=end-2,gap_body_exit=end-1);return lookup

def instruction_pedagogy(raw: dict[str,Any],line_index: int | None,line_text: str) -> dict[str,Any]:
    """Present lexical locals and distinguish operands, loops and completed groups."""
    frame=typed_frame(raw,line_index,line_text);token=raw['line_token'];event=raw['instruction_event'];n=len(raw['array_snapshot'])
    if token=='while_compare':frame['concept']='comparison'
    for call in frame['call_stack']:call['continuation']='retornar al caller' if call['function']=='ordenar_shell' else 'continuar en ordenar_shell'
    inner=token.startswith('while_') or token in {'shift','j_subtract'}
    middle=token.startswith('i_') or token in {'temp_take','j_init','temp_write','inner_body_exit'}
    outer=token.startswith('gap_') and token!='gap_declare'
    frame['loop']=None
    if inner or middle or outer:
        frame['loop']=dict(kind='while interno' if inner else 'for i' if middle else 'for intervalo',iteration=event['j'] if inner else event['i'] if middle else event['intervalo'],bounds=[event['intervalo'],event['i']] if inner else [event['intervalo'],n] if middle else [0,n//2],exit=token in {'while_test','i_test','gap_test'} and raw['condition_result'] is False)
    text='Cada insercion trabaja en un grupo por intervalo; sus valores pueden cambiar en intervalos posteriores. El arreglo muestra sus valores reales.'
    if token=='gap_body_exit':text='Todos los grupos por el intervalo completado estan ordenados; sus valores aun pueden cambiar al reducir el intervalo.'
    if token in {'shift','j_subtract'}:text+=' El duplicado provisional conserva el valor pendiente en el local int temporal.'
    frame['invariant']={'text':text,'indices':raw['shell_context']['group'],'holds':True};return frame
