"""Merge sort: real recursive scopes and malloc auxiliary lifetime, opt-in instruction trace."""
from __future__ import annotations
from copy import deepcopy
from typing import Any
from app.domain.sorting.intercambio_instructions import instruction_pedagogy as typed_frame

def run_mergesort_trace(values: list[int]) -> dict[str,Any]:
    a=list(values);n=len(a);aux: list[int | None]=[];live=False;declared=False;reserved=False;released=False
    frames: list[dict[str,Any]]=[];stack: list[str]=[];steps: list[dict[str,Any]]=[]
    comparisons=moves=allocations=frees=0;status: int | None=None
    def emit(token: str,function: str | None,action: str,condition: bool | None=None,expression: str='',source_token: str | None=None) -> None:
        variables=[];pointers=[]
        def variable(name: str,ctype: str,value: Any,scope: str,initialized: bool=True) -> None:
            variables.append(dict(name=name,type=ctype,value=value,scope=scope,initialized=initialized))
        if stack:
            variable('arreglo','int *','arreglo del caller','ordenar_mergesort');variable('n','size_t',n,'ordenar_mergesort')
            if declared:variable('auxiliar','int *','memoria liberada; sin lectura' if released else 'auxiliar reservado' if reserved else None,'ordenar_mergesort',reserved)
        if 'arreglo_valido' in stack:
            variable('arreglo','const int *','arreglo del caller','arreglo_valido');variable('n','size_t',n,'arreglo_valido')
        for depth,f in enumerate(frames,1):
            scope=f"{f['function']}[{depth}]";variable('arreglo','int *','arreglo del caller',scope);variable('auxiliar','int *','auxiliar del wrapper',scope)
            variable('izquierda','size_t',f['izquierda'],scope);variable('derecha','size_t',f['derecha'],scope)
            if f['medio'] is not None:variable('medio','size_t',f['medio'],scope)
            if f['i'] is not None:
                for name in ['i','j','k']:variable(name,'size_t',f[name],scope)
        if stack:pointers.append(dict(name='arreglo',target='arreglo del caller',value=f'{n} enteros del caller',type='int *',scope='ordenar_mergesort'))
        if live:
            pointers.append(dict(name='auxiliar',target='reserva int[n]',value=f'{n} celdas; {sum(v is not None for v in aux)} inicializadas',type='int *',scope='ordenar_mergesort'))
            for depth,f in enumerate(frames,1):pointers.append(dict(name='auxiliar',target='misma reserva del wrapper',value=f'int[{n}] vivo',type='int *',scope=f"{f['function']}[{depth}]"))
        previous={(v['scope'],v['name']):v for v in steps[-1]['instruction_variables']} if steps else {}
        for v in variables:
            old=previous.get((v['scope'],v['name']));v['previous']=old['value'] if old else None;v['changed']=old is None or (old['value'],old['initialized'])!=(v['value'],v['initialized'])
        top=frames[-1] if frames else {};l=top.get('izquierda');r=top.get('derecha');i=top.get('i');j=top.get('j')
        compared=[i,j] if token=='merge_compare' else []
        event=dict(token=token,function=function,comparisons=comparisons,moves=moves,aux_live=live,allocations=allocations,frees=frees,frames=deepcopy(frames))
        steps.append(dict(step=len(steps)+1,line_token=token,source_line_token=source_token or token,action=action,array_snapshot=list(a),comparing_indices=compared,swapping_indices=[],sorted_indices=list(range(n)) if token=='sort_return' else [],active_range=[l,r] if frames else None,pivot_index=None,auxiliary_snapshot=list(aux) if live else None,temporaries={},pointer_indices=[],console_output='',metrics=dict(comparisons=comparisons,swaps=0,moves=moves),instruction_variables=deepcopy(variables),instruction_stack=list(stack),instruction_pointers=pointers,source_function=function,condition_result=condition,condition_expression=expression,instruction_event=event,merge_context=dict(izquierda=l,derecha=r,medio=top.get('medio'),i=i,j=j,k=top.get('k'),depth=len(frames),aux_live=live,aux_declared=declared,aux_released=released,allocations=allocations,frees=frees,status=status)))
    def merge(l: int,m: int,r: int) -> None:
        nonlocal comparisons,moves
        f=dict(function='mezclar',izquierda=l,derecha=r,medio=m,i=None,j=None,k=None);frames.append(f);stack.append('mezclar');emit('merge_entry','mezclar','Entrar en mezclar; caller recursivo suspendido, misma reserva auxiliar.')
        f.update(i=l,j=m+1,k=l);emit('merge_init','mezclar','Declarar e inicializar size_t i, j, k.')
        while True:
            left=f['i']<=m;emit('merge_left','mezclar','Evaluar i<=medio del primer operando &&.',left,f"{f['i']} <= {m}")
            right=False
            if left:right=f['j']<=r;emit('merge_right','mezclar','Evaluar j<=derecha solo si el operando izquierdo permite continuar.',right,f"{f['j']} <= {r}")
            test=left and right;emit('merge_while','mezclar','Resultado del while con cortocircuito; no leer valores fuera del rango.',test,'i <= medio && j <= derecha')
            if not test:break
            test=a[f['i']]<=a[f['j']];comparisons+=1;emit('merge_compare','mezclar','Comparar valores; <= elige izquierda al empatar.',test,f"{a[f['i']]} <= {a[f['j']]}")
            if test:
                aux[f['k']]=a[f['i']];f['k']+=1;f['i']+=1;moves+=1;emit('aux_left_write','mezclar','Completar auxiliar[k++]=arreglo[i++]; ambos efectos terminan en esta sentencia.')
            else:
                aux[f['k']]=a[f['j']];f['k']+=1;f['j']+=1;moves+=1;emit('aux_right_write','mezclar','Completar auxiliar[k++]=arreglo[j++]; no anticipar la escritura siguiente.')
        while True:
            test=f['i']<=m;emit('left_tail_test','mezclar','Evaluar el while del remanente izquierdo.',test,f"{f['i']} <= {m}")
            if not test:break
            aux[f['k']]=a[f['i']];f['k']+=1;f['i']+=1;moves+=1;emit('left_tail_write','mezclar','Completar una escritura del remanente izquierdo y sus postincrementos.')
        while True:
            test=f['j']<=r;emit('right_tail_test','mezclar','Evaluar el while del remanente derecho.',test,f"{f['j']} <= {r}")
            if not test:break
            aux[f['k']]=a[f['j']];f['k']+=1;f['j']+=1;moves+=1;emit('right_tail_write','mezclar','Completar una escritura del remanente derecho y sus postincrementos.')
        f['i']=l;emit('copy_init','mezclar','Inicializar i=izquierda para copiar de vuelta; conservar j y k.')
        while True:
            test=f['i']<=r;emit('copy_test','mezclar','Evaluar i<=derecha del for de copia.',test,f"{f['i']} <= {r}")
            if not test:break
            value=aux[f['i']];assert value is not None;a[f['i']]=value;moves+=1;emit('copy_write','mezclar','Copiar una celda inicializada auxiliar[i] al arreglo; otras posiciones conservan su estado.')
            f['i']+=1;emit('copy_increment','mezclar','Ejecutar ++i después de una copia, antes de la condición siguiente.')
        emit('merge_body_exit','mezclar','Finalizar cuerpo de mezcla; únicamente este segmento queda fusionado.')
        frames.pop();stack.pop();emit('merge_return','mezclar','Retornar void y retirar parámetros/locales de mezclar, sin liberar la reserva del wrapper.')
    def recursive(l: int,r: int) -> None:
        f=dict(function='mergesort_recursivo',izquierda=l,derecha=r,medio=None,i=None,j=None,k=None);frames.append(f);stack.append('mergesort_recursivo');emit('rec_entry','mergesort_recursivo','Entrar en activación recursiva con parámetros size_t propios.')
        test=l>=r;emit('rec_guard','mergesort_recursivo','Evaluar izquierda>=derecha; medio aún no se ha declarado.',test,f'{l} >= {r}')
        if test:
            frames.pop();stack.pop();emit('rec_return','mergesort_recursivo','Retornar por caso base y retirar solo esta activación.',source_token='rec_guard_return');return
        m=l+(r-l)//2;f['medio']=m;emit('split','mergesort_recursivo','Declarar e inicializar medio; conservar locales de ancestros.')
        emit('rec_left_call','mergesort_recursivo','Llamar al rango izquierdo; caller suspendido.');recursive(l,m);emit('rec_left_resume','mergesort_recursivo','Retomar caller tras el retorno izquierdo.')
        emit('rec_right_call','mergesort_recursivo','Llamar al rango derecho; caller suspendido.');recursive(m+1,r);emit('rec_right_resume','mergesort_recursivo','Retomar caller tras el retorno derecho.')
        emit('merge_call','mergesort_recursivo','Llamar mezclar con los dos segmentos ordenados y el mismo auxiliar.');merge(l,m,r);emit('merge_resume','mergesort_recursivo','Retomar caller después de retirar mezclar.')
        emit('rec_body_exit','mergesort_recursivo','Finalizar el cuerpo recursivo; mantener ancestros suspendidos.')
        frames.pop();stack.pop();emit('rec_return','mergesort_recursivo','Retorno void implícito; retirar solo esta activación.')
    emit('initial',None,'Antes de llamar ordenar_mergesort; ninguna instrucción C ejecutada.')
    stack.append('ordenar_mergesort');emit('sort_entry','ordenar_mergesort','Entrar en ordenar_mergesort con arreglo y n del caller.')
    declared=True;emit('aux_declare','ordenar_mergesort','Declarar int *auxiliar; puntero aún sin inicializar.')
    emit('valid_call','ordenar_mergesort','Llamar arreglo_valido antes de la guarda.');stack.append('arreglo_valido');emit('valid_entry','arreglo_valido','Entrar en arreglo_valido.')
    emit('valid_ptr','arreglo_valido','Evaluar arreglo!=NULL.',True,'arreglo != NULL');emit('valid_n','arreglo_valido','Evaluar n>0 por cortocircuito.',n>0,f'{n} > 0')
    stack.pop();emit('valid_return','arreglo_valido','Retornar validación y retirar el helper.');emit('sort_guard','ordenar_mergesort','Evaluar !arreglo_valido(arreglo,n).',n==0,'!arreglo_valido(arreglo,n)')
    if not n:
        status=0;stack.clear();declared=False;emit('guard_error','ordenar_mergesort','Retornar ORDENAMIENTO_ERROR sin reserva ni cambio del arreglo.')
    else:
        aux=[None]*n;live=reserved=True;allocations=1;emit('aux_reserve','ordenar_mergesort','Asignar malloc(n*sizeof(int)); reserva viva, todas sus celdas sin inicializar.')
        emit('allocation_guard','ordenar_mergesort','Evaluar auxiliar==NULL después de la reserva exitosa.',False,'auxiliar == NULL')
        emit('recursive_call','ordenar_mergesort','Llamar recursión incluso para n1.');recursive(0,n-1);emit('recursive_resume','ordenar_mergesort','Retomar wrapper después de toda la recursión.')
        live=False;released=True;frees=1;aux=[];emit('aux_free','ordenar_mergesort','Ejecutar free(auxiliar); termina la vida de la reserva, sin afirmar que C asignó NULL.')
        status=1;stack.clear();declared=False;emit('sort_return','ordenar_mergesort','Retornar ORDENAMIENTO_OK; retirar locales del wrapper y confirmar el resultado final.')
    return dict(steps=steps,final_state={'items':list(a)},metrics=dict(comparisons=comparisons,swaps=0,moves=moves,steps=len(steps)))

def instruction_line_lookup(source_code: str) -> dict[str,int | None]:
    import re
    rows=source_code.replace('\r\n','\n').split('\n');lookup={'initial':None}
    groups={'arreglo_valido':{'valid_entry':None,'valid_ptr':'return arreglo','valid_n':'return arreglo','valid_return':'return arreglo'},'ordenar_mergesort':{'sort_entry':None,'aux_declare':'int *auxiliar;','valid_call':'if (!arreglo_valido','sort_guard':'if (!arreglo_valido','guard_error':'if (!arreglo_valido','aux_reserve':'auxiliar =','allocation_guard':'if (auxiliar == NULL)','allocation_error':'if (auxiliar == NULL)','recursive_call':'mergesort_recursivo(arreglo','recursive_resume':'mergesort_recursivo(arreglo','aux_free':'free(auxiliar);','sort_return':'return ORDENAMIENTO_OK;'},'mergesort_recursivo':{'rec_entry':None,'rec_guard':'if (izquierda >= derecha)','rec_guard_return':'if (izquierda >= derecha)','split':'size_t medio =','rec_left_call':'mergesort_recursivo(arreglo, auxiliar, izquierda, medio);','rec_left_resume':'mergesort_recursivo(arreglo, auxiliar, izquierda, medio);','rec_right_call':'mergesort_recursivo(arreglo, auxiliar, medio + 1, derecha);','rec_right_resume':'mergesort_recursivo(arreglo, auxiliar, medio + 1, derecha);','merge_call':'mezclar(arreglo','merge_resume':'mezclar(arreglo','rec_body_exit':'}','rec_return':'}'},'mezclar':{'merge_entry':None,'merge_init':'size_t i =','merge_left':'while (i <= medio &&','merge_right':'while (i <= medio &&','merge_while':'while (i <= medio &&','merge_compare':'if (arreglo[i]','aux_left_write':'if (arreglo[i]','aux_right_write':'else auxiliar','left_tail_test':'while (i <= medio) auxiliar','left_tail_write':'while (i <= medio) auxiliar','right_tail_test':'while (j <= derecha) auxiliar','right_tail_write':'while (j <= derecha) auxiliar','copy_init':'for (i = izquierda','copy_test':'for (i = izquierda','copy_write':'for (i = izquierda','copy_increment':'for (i = izquierda','merge_body_exit':'}','merge_return':'}'}}
    for name,tokens in groups.items():
        start=next(k for k,row in enumerate(rows) if re.match(r'\s*(?:static )?(?:void|int) '+name+r'\(',row));balance=0
        for end in range(start,len(rows)):
            balance+=rows[end].count('{')-rows[end].count('}')
            if end>start and balance==0:break
        for token,pattern in tokens.items():lookup[token]=start if pattern is None else end if pattern=='}' else next(k for k in range(start,end+1) if pattern in rows[k])
    return lookup

def instruction_pedagogy(raw: dict[str,Any],line_index: int | None,line_text: str) -> dict[str,Any]:
    frame=typed_frame(raw,line_index,line_text);event=raw['instruction_event'];top=event['frames'][-1] if event['frames'] else {};calls=[];depth=0
    for name in raw['instruction_stack']:
        if name in {'mergesort_recursivo','mezclar'}:
            f=event['frames'][depth];depth+=1;params={'arreglo':'arreglo del caller','auxiliar':'reserva del wrapper','izquierda':f['izquierda']}
            if name=='mezclar':params['medio']=f['medio']
            params['derecha']=f['derecha'];continuation=f'retornar a activación {depth-1}' if depth>1 else 'retornar a ordenar_mergesort'
        else:params={'arreglo':'arreglo del caller','n':len(raw['array_snapshot'])};continuation='retornar al caller' if name=='ordenar_mergesort' else 'continuar en ordenar_mergesort'
        calls.append(dict(function=name,parameters=params,continuation=continuation))
    frame['call_stack']=calls;token=raw['line_token'];frame['loop']=None
    if top.get('function')=='mezclar' and top.get('i') is not None:
        kind='for copia' if token.startswith('copy_') else 'while remanente izquierdo' if token.startswith('left_tail_') else 'while remanente derecho' if token.startswith('right_tail_') else 'while mezcla'
        frame['loop']=dict(kind=kind,iteration=None,bounds=[top['izquierda'],top['derecha']],exit=token in {'merge_while','left_tail_test','right_tail_test','copy_test'} and raw['condition_result'] is False)
    if token=='merge_compare':frame['concept']='comparison'
    text='Cada activación conserva parámetros y locales propios; el auxiliar existe solo desde malloc hasta free y únicamente las celdas escritas tienen valores definidos.'
    if token=='merge_body_exit':text+=f" El segmento [{top['izquierda']}..{top['derecha']}] acaba de fusionarse y copiarse; no certifica el arreglo global."
    elif token=='copy_write':text+=' La copia actual modifica una sola celda del arreglo; el resto conserva su estado.'
    elif token=='aux_free':text+=' La memoria liberada no se lee ni se representa como una reserva viva.'
    frame['invariant']={'text':text,'indices':raw['sorted_indices'],'holds':True};return frame
