"""Quick sort C instruction events with recursive activations and real helper aliases."""
from __future__ import annotations
from copy import deepcopy
from typing import Any
from app.domain.sorting.intercambio_instructions import instruction_line_lookup as helper_lines
from app.domain.sorting.intercambio_instructions import instruction_pedagogy as typed_frame

def run_quicksort_trace(values: list[int]) -> dict[str,Any]:
    """Follow actual wrapper, recursive calls, scans and swap assignment order."""
    a=list(values);n=len(a);frames: list[dict[str,int | None]]=[];stack: list[str]=[];steps: list[dict[str,Any]]=[]
    aliases: tuple[int,int] | None=None
    temporal: int | None=None
    temp_declared=False
    comparisons=swaps=moves=0
    def emit(token: str,function: str | None,action: str,condition: bool | None=None,expression: str='') -> None:
        variables=[]
        if stack:variables.append(dict(name='n',type='size_t',value=n,scope='ordenar_quicksort',initialized=True))
        for depth,frame in enumerate(frames,1):
            for name,value in frame.items():
                if value is not None:variables.append(dict(name=name,type='int',value=value,scope=f'quicksort_recursivo[{depth}]',initialized=True))
        if temp_declared:variables.append(dict(name='temporal',type='int',value=temporal,scope='intercambiar',initialized=temporal is not None))
        previous={(v['scope'],v['name']):v for v in steps[-1]['instruction_variables']} if steps else {}
        for v in variables:
            old=previous.get((v['scope'],v['name']));v['previous']=old['value'] if old else None;v['changed']=old is None or old['value']!=v['value'] or old['initialized']!=v['initialized']
        top=frames[-1] if frames else {};i=top.get('i');j=top.get('j');first=top.get('primero');last=top.get('ultimo')
        pointers=[dict(name=name,target=f'arreglo[{index}]',index=index,value=a[index],type='int *',scope='intercambiar') for name,index in zip(('a','b'),aliases)] if aliases else []
        scan=[i] if token=='i_test' else [j] if token=='j_test' else []
        steps.append({'step':len(steps)+1,'line_token':token,'action':action,'array_snapshot':list(a),'comparing_indices':scan,'swapping_indices':list(aliases or []),
          'sorted_indices':list(range(n)) if token=='sort_return' else [],'active_range':[first,last] if frames else None,'pivot_index':None,'auxiliary_snapshot':None,
          'temporaries':{'temporal':temporal} if temp_declared and temporal is not None else {},'pointer_indices':list(aliases or []),'console_output':'',
          'metrics':dict(comparisons=comparisons,swaps=swaps,moves=moves),'instruction_variables':deepcopy(variables),'instruction_stack':list(stack),'instruction_pointers':pointers,
          'source_function':function,'condition_result':condition,'condition_expression':expression,
          'quick_context':{'primero':first,'ultimo':last,'i':i,'j':j,'pivote':top.get('pivote'),'depth':len(frames)},
          'instruction_event':dict(token=token,function=function,frames=deepcopy(frames),temporal=temporal if temp_declared else None,a=aliases[0] if aliases else None,b=aliases[1] if aliases else None,comparisons=comparisons,swaps=swaps,moves=moves)})
    def recursive(first: int,last: int) -> None:
        nonlocal comparisons,swaps,moves,aliases,temporal,temp_declared
        f={'primero':first,'ultimo':last,'i':None,'j':None,'pivote':None};frames.append(f);stack.append('quicksort_recursivo')
        emit('rec_entry','quicksort_recursivo','Entrar en una activacion recursiva; parametros int propios, caller suspendido.')
        f.update(i=first,j=last,pivote=a[(first+last)//2]);emit('rec_init','quicksort_recursivo','Declarar e inicializar i, j y pivote int; conservar el pivote local.')
        while True:
            test=f['i']<=f['j'];emit('outer_test','quicksort_recursivo','Evaluar i<=j del while exterior.',test,f"{f['i']} <= {f['j']}")
            if not test:break
            while True:
                test=a[f['i']]<f['pivote'];comparisons+=1;emit('i_test','quicksort_recursivo','Comparar arreglo[i] con el pivote local.',test,f"{a[f['i']]} < {f['pivote']}")
                if not test:break
                f['i']+=1;emit('i_increment','quicksort_recursivo','Ejecutar ++i del scan izquierdo.')
            while True:
                test=a[f['j']]>f['pivote'];comparisons+=1;emit('j_test','quicksort_recursivo','Comparar arreglo[j] con el pivote local.',test,f"{a[f['j']]} > {f['pivote']}")
                if not test:break
                f['j']-=1;emit('j_decrement','quicksort_recursivo','Ejecutar --j del scan derecho.')
            test=f['i']<=f['j'];comparisons+=1;emit('cross_test','quicksort_recursivo','Evaluar el if i<=j despues de los scans.',test,f"{f['i']} <= {f['j']}")
            if test:
                emit('swap_call','quicksort_recursivo','Llamar intercambiar con los alias reales; pueden apuntar al mismo entero.')
                aliases=(f['i'],f['j']);stack.append('intercambiar');emit('swap_entry','intercambiar','Entrar en intercambiar; caller recursivo suspendido.')
                temp_declared=True;temporal=None;emit('swap_declare','intercambiar','Declarar temporal int sin inicializar.')
                emit('swap_guard','intercambiar','Evaluar a==NULL || b==NULL.',False,'a == NULL || b == NULL')
                temporal=a[aliases[0]];moves+=1;emit('swap_temp','intercambiar','Asignar temporal=*a; conservar el arreglo.')
                a[aliases[0]]=a[aliases[1]];moves+=1;emit('swap_assign_a','intercambiar','Asignar *a=*b; temporal conserva el valor pendiente.')
                a[aliases[1]]=temporal;moves+=1;swaps+=1;emit('swap_assign_b','intercambiar','Asignar *b=temporal; completar incluso el auto-intercambio.')
                aliases=None;temporal=None;temp_declared=False;stack.pop();emit('swap_return','intercambiar','Retorno void; retirar temporal y alias del helper.')
                emit('swap_resume','quicksort_recursivo','Continuar en el caller despues del helper.')
                f['i']+=1;emit('cross_i_increment','quicksort_recursivo','Ejecutar ++i despues de intercambiar.')
                f['j']-=1;emit('cross_j_decrement','quicksort_recursivo','Ejecutar --j despues de intercambiar; int admite -1.')
        test=first<f['j'];emit('left_test','quicksort_recursivo','Evaluar primero<j para la llamada izquierda.',test,f"{first} < {f['j']}")
        if test:
            emit('left_call','quicksort_recursivo','Llamar al rango izquierdo; conservar locales del caller.')
            recursive(first,f['j']);emit('left_resume','quicksort_recursivo','Retomar caller tras retirar la activacion izquierda.')
        test=f['i']<last;emit('right_test','quicksort_recursivo','Evaluar i<ultimo para la llamada derecha.',test,f"{f['i']} < {last}")
        if test:
            emit('right_call','quicksort_recursivo','Llamar al rango derecho; conservar locales del caller.')
            recursive(f['i'],last);emit('right_resume','quicksort_recursivo','Retomar caller tras retirar la activacion derecha.')
        frames.pop();stack.pop();emit('rec_return','quicksort_recursivo','Retorno void recursivo; retirar solo locales de la activacion terminada.')
    emit('initial',None,'Antes de llamar ordenar_quicksort; ninguna instruccion C ejecutada.')
    stack.append('ordenar_quicksort');emit('sort_entry','ordenar_quicksort','Entrar en ordenar_quicksort.')
    emit('valid_call','ordenar_quicksort','Llamar arreglo_valido antes de decidir la guarda.')
    stack.append('arreglo_valido');emit('valid_entry','arreglo_valido','Entrar en arreglo_valido.')
    emit('valid_ptr','arreglo_valido','Evaluar arreglo != NULL.',True,'arreglo != NULL');emit('valid_n','arreglo_valido','Evaluar n>0 por cortocircuito.',n>0,f'{n} > 0')
    stack.pop();emit('valid_return','arreglo_valido','Retornar validacion y retirar el helper.')
    emit('sort_guard','ordenar_quicksort','Evaluar !arreglo_valido(arreglo,n).',n==0,'!arreglo_valido(arreglo,n)')
    if not n:
        stack.clear();emit('guard_return','ordenar_quicksort','Retornar sin entrar al helper para entrada vacia.')
    else:
        emit('rec_call','ordenar_quicksort','Llamar quicksort_recursivo(arreglo,0,(int)n-1), incluido n==1.')
        recursive(0,n-1);emit('rec_resume','ordenar_quicksort','Retomar wrapper despues de la recursion.')
        stack.clear();emit('sort_return','ordenar_quicksort','Retorno void al caller; el TAD no imprime.')
    return dict(steps=steps,final_state={'items':list(a)},metrics=dict(comparisons=comparisons,swaps=swaps,moves=moves,steps=len(steps)))

def instruction_line_lookup(source_code: str) -> dict[str,int | None]:
    """Resolve each wrapper, recursive and helper clause inside its actual function."""
    import re
    lookup=helper_lines(source_code);rows=source_code.replace('\r\n','\n').split('\n')
    groups={'ordenar_quicksort':{'sort_entry':None,'valid_call':'if (!arreglo_valido','sort_guard':'if (!arreglo_valido','guard_return':'if (!arreglo_valido','rec_call':'quicksort_recursivo(arreglo, 0','rec_resume':'quicksort_recursivo(arreglo, 0','sort_return':'}'},'quicksort_recursivo':{'rec_entry':None,'rec_init':'int i =','outer_test':'while (i <= j)','i_test':'while (arreglo[i]','i_increment':'while (arreglo[i]','j_test':'while (arreglo[j]','j_decrement':'while (arreglo[j]','cross_test':'if (i <= j)','swap_call':'intercambiar(&arreglo[i]','swap_resume':'intercambiar(&arreglo[i]','cross_i_increment':'++i; --j;','cross_j_decrement':'++i; --j;','left_test':'if (primero < j)','left_call':'if (primero < j)','left_resume':'if (primero < j)','right_test':'if (i < ultimo)','right_call':'if (i < ultimo)','right_resume':'if (i < ultimo)','rec_return':'}'}}
    for name,tokens in groups.items():
        start=next(k for k,row in enumerate(rows) if re.match(r'\s*(?:static )?void '+name+r'\(',row));balance=0
        for end in range(start,len(rows)):
            balance+=rows[end].count('{')-rows[end].count('}')
            if end>start and balance==0:break
        for token,pattern in tokens.items():lookup[token]=start if pattern is None else end if pattern=='}' else next(k for k in range(start,end+1) if pattern in rows[k])
    return lookup

def instruction_pedagogy(raw: dict[str,Any],line_index: int | None,line_text: str) -> dict[str,Any]:
    """Render separate recursive frames, signed locals, and actual alias parameters."""
    event=raw['instruction_event'];top=event['frames'][-1] if event['frames'] else {};presentation=dict(raw);presentation['instruction_event']={**event,'i':top.get('i') or 0,'j':top.get('j') or 0};frame=typed_frame(presentation,line_index,line_text)
    calls=[];depth=0
    for name in raw['instruction_stack']:
        if name=='quicksort_recursivo':
            f=event['frames'][depth];depth+=1;params={'arreglo':'arreglo del caller','primero':f['primero'],'ultimo':f['ultimo']};continuation=f'retornar a activacion {depth-1}' if depth>1 else 'retornar a ordenar_quicksort'
        elif name=='intercambiar':params={p['name']:p['target'] for p in raw['instruction_pointers']};continuation=f'continuar en quicksort_recursivo[{depth}]'
        else:params={'arreglo':'arreglo del caller','n':len(raw['array_snapshot'])};continuation='retornar al caller' if name=='ordenar_quicksort' else 'continuar en ordenar_quicksort'
        calls.append(dict(function=name,parameters=params,continuation=continuation))
    frame['call_stack']=calls;token=raw['line_token'];frame['loop']=None
    if top.get('i') is not None and (token in {'outer_test','cross_test','cross_i_increment','cross_j_decrement'} or token.startswith(('i_','j_','swap_'))):
        scan_i=token.startswith('i_');scan_j=token.startswith('j_');kind='while i' if scan_i else 'while j' if scan_j else 'while particion'
        if 'intercambiar' in raw['instruction_stack']:kind+=' (caller suspendido)'
        frame['loop']=dict(kind=kind,iteration=top['i'] if scan_i else top['j'] if scan_j else None,bounds=[top['primero'],top['ultimo']],exit=token in {'outer_test','i_test','j_test'} and raw['condition_result'] is False)
    if token in {'i_test','j_test'}:frame['concept']='comparison'
    text='Cada activacion conserva parametros y locales int propios; el pivote es su valor guardado, no el valor futuro de una celda. Solo el retorno final confirma todos los valores.'
    if token=='swap_assign_a':text+=' Temporal conserva el valor pendiente; a y b pueden aliasar el mismo entero.'
    frame['invariant']={'text':text,'indices':raw['sorted_indices'],'holds':True};return frame
