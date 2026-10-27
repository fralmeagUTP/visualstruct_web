"""Heap sort instruction trace, opt-in; C automatic recursive storage and void contract."""
from copy import deepcopy
from app.domain.sorting.intercambio_instructions import instruction_pedagogy as typed_frame

def run_heapsort_trace(values):
    a=list(values);n=len(a);frames=[];stack=[];steps=[];i=None;declared=False;phase=None
    comparisons=swaps=moves=0;aliases=None;td=False;temp=None;heap_n=n;confirmed=set()
    def emit(token,function,condition=None,expression=''):
        variables=[];pointers=[]
        def var(name,type,value,scope,initialized=True):
            variables.append(dict(name=name,type=type,value=value,scope=scope,initialized=initialized))
        if stack:
            var('arreglo','int *','arreglo del caller','ordenar_heapsort');var('n','size_t',n,'ordenar_heapsort')
            if declared:var('i','size_t',i,'ordenar_heapsort',i is not None)
        if 'arreglo_valido' in stack:
            var('arreglo','const int *','arreglo del caller','arreglo_valido');var('n','size_t',n,'arreglo_valido')
        for depth,f in enumerate(frames,1):
            scope=f'heapify[{depth}]';var('arreglo','int *','arreglo del caller',scope)
            for key,value in f.items():
                if key in ('n','raiz') or value is not None:var(key,'size_t',value,scope)
        if aliases is not None:
            for name,index in zip(('a','b'),aliases):
                target=f'arreglo[{index}]';var(name,'int *',target,'intercambiar')
                pointers.append(dict(name=name,type='int *',scope='intercambiar',target=target,value=a[index]))
            if td:var('temporal','int',temp,'intercambiar',temp is not None)
        previous={(v['scope'],v['name']):v for v in steps[-1]['instruction_variables']} if steps else {}
        for v in variables:
            old=previous.get((v['scope'],v['name']));v['previous']=old['value'] if old else None;v['changed']=old is None or (old['value'],old['initialized'])!=(v['value'],v['initialized'])
        top=frames[-1] if frames else {};indices=[]
        if token in ('left_compare','right_compare'):indices=[top['izquierdo' if token=='left_compare' else 'derecho'],top['mayor']]
        event=dict(token=token,function=function,i=i,phase=phase,comparisons=comparisons,swaps=swaps,moves=moves,a=aliases[0] if aliases else None,b=aliases[1] if aliases else None,temporal_declared=td,temporal=temp,frames=deepcopy(frames))
        nodes=[dict(index=k,value=a[k],children=[c for c in (2*k+1,2*k+2) if c<heap_n]) for k in range(heap_n)]
        max_heap=all(a[(k-1)//2]>=a[k] for k in range(1,heap_n))
        context=dict(heap_n=heap_n,wrapper_n=n,i=i,phase=phase,depth=len(frames),raiz=top.get('raiz'),mayor=top.get('mayor'),izquierdo=top.get('izquierdo'),derecho=top.get('derecho'),nodes=nodes,suffix=[dict(index=k,value=a[k]) for k in sorted(confirmed)],max_heap=max_heap)
        action=token.replace('_',' ') + (': '+expression if expression else '')
        steps.append(dict(step=len(steps)+1,line_token=token,action=action,array_snapshot=list(a),comparing_indices=indices,swapping_indices=list(aliases) if aliases else [],sorted_indices=sorted(confirmed),active_range=[0,heap_n-1] if heap_n else None,pivot_index=None,auxiliary_snapshot=None,temporaries={'temporal':temp} if temp is not None else {},pointer_indices=list(aliases) if aliases else [],console_output='',metrics=dict(comparisons=comparisons,swaps=swaps,moves=moves),instruction_variables=variables,instruction_stack=list(stack),instruction_pointers=pointers,source_function=function,condition_result=condition,condition_expression=expression,instruction_event=event,heap_context=context))
    def swap(x,y):
        nonlocal aliases,td,temp,moves,swaps
        aliases=(x,y);stack.append('intercambiar');emit('swap_entry','intercambiar')
        td=True;emit('swap_declare','intercambiar')
        emit('swap_a_null','intercambiar',False,'a == NULL');emit('swap_b_null','intercambiar',False,'b == NULL');emit('swap_guard','intercambiar',False,'a == NULL || b == NULL')
        temp=a[x];moves+=1;emit('swap_temp','intercambiar')
        a[x]=a[y];moves+=1;emit('swap_assign_a','intercambiar')
        a[y]=temp;moves+=1;swaps+=1;emit('swap_assign_b','intercambiar')
        aliases=None;td=False;temp=None;stack.pop();emit('swap_return','intercambiar')
    def heap(size,root):
        nonlocal comparisons
        f=dict(n=size,raiz=root,mayor=None,izquierdo=None,derecho=None);frames.append(f);stack.append('heapify');emit('heap_entry','heapify')
        f.update(mayor=root,izquierdo=2*root+1,derecho=2*root+2);emit('heap_init','heapify')
        for side in ('left','right'):
            child=f['izquierdo' if side=='left' else 'derecho'];bound=child<size;emit(side+'_bound','heapify',bound,f'{child} < {size}')
            compare=False
            if bound:
                compare=a[child]>a[f['mayor']];comparisons+=1;emit(side+'_compare','heapify',compare,f"{a[child]} > {a[f['mayor']]}")
            result=bound and compare;emit(side+'_test','heapify',result,('izquierdo' if side=='left' else 'derecho')+' < n && arreglo['+('izquierdo' if side=='left' else 'derecho')+'] > arreglo[mayor]')
            if result:f['mayor']=child;emit('largest_'+side,'heapify')
        result=f['mayor']!=root;emit('root_test','heapify',result,f"{f['mayor']} != {root}")
        if result:
            emit('heap_swap_call','heapify');swap(root,f['mayor']);emit('heap_swap_resume','heapify')
            emit('heap_rec_call','heapify');heap(size,f['mayor']);emit('heap_rec_resume','heapify')
        frames.pop();stack.pop();emit('heap_return','heapify')
    emit('initial',None);stack.append('ordenar_heapsort');emit('sort_entry','ordenar_heapsort');declared=True;emit('i_declare','ordenar_heapsort')
    emit('valid_call','ordenar_heapsort');stack.append('arreglo_valido');emit('valid_entry','arreglo_valido');emit('valid_ptr','arreglo_valido',True,'arreglo != NULL');emit('valid_n','arreglo_valido',n>0,f'{n} > 0');stack.pop();emit('valid_return','arreglo_valido');emit('sort_guard','ordenar_heapsort',n==0,'!arreglo_valido(arreglo,n)')
    if n:
        i=n//2;phase='build';emit('build_init','ordenar_heapsort')
        while True:
            emit('build_test','ordenar_heapsort',i>0,f'{i} > 0')
            if i==0:break
            emit('build_call','ordenar_heapsort');heap(n,i-1);emit('build_resume','ordenar_heapsort');i-=1;emit('build_decrement','ordenar_heapsort')
        i=n;phase='extract';emit('extract_init','ordenar_heapsort')
        while True:
            emit('extract_test','ordenar_heapsort',i>1,f'{i} > 1')
            if i<=1:break
            emit('extract_swap_call','ordenar_heapsort');swap(0,i-1);heap_n=i-1;confirmed.add(i-1);emit('extract_swap_resume','ordenar_heapsort')
            emit('extract_heap_call','ordenar_heapsort');heap(i-1,0);emit('extract_heap_resume','ordenar_heapsort');i-=1;emit('extract_decrement','ordenar_heapsort')
        stack.clear();declared=False;i=None;phase=None;heap_n=0;confirmed=set(range(n));emit('sort_return','ordenar_heapsort')
    else:
        stack.clear();declared=False;emit('guard_return','ordenar_heapsort')
    return dict(steps=steps,final_state={'items':a},metrics=dict(comparisons=comparisons,swaps=swaps,moves=moves,steps=len(steps)))

def instruction_line_lookup(source_code):
    import re
    rows=source_code.replace('\r\n','\n').split('\n');lookup={'initial':None}
    groups={
        'arreglo_valido':{'valid_entry':None,'valid_ptr':'return arreglo','valid_n':'return arreglo','valid_return':'return arreglo'},
        'ordenar_heapsort':{'sort_entry':None,'i_declare':'size_t i;','valid_call':'if (!arreglo_valido','sort_guard':'if (!arreglo_valido','guard_return':'if (!arreglo_valido','sort_return':'}'},
        'heapify':{'heap_entry':None,'heap_init':'size_t mayor =','root_test':'if (mayor != raiz)','heap_return':'}'},
        'intercambiar':{'swap_entry':None,'swap_declare':'int temporal;','swap_temp':'temporal = *a;','swap_assign_a':'*a = *b;','swap_assign_b':'*b = temporal;','swap_return':'}'}}
    for token in ('build_init','build_test','build_decrement','build_call','build_resume'):groups['ordenar_heapsort'][token]='for (i = n / 2;'
    for token in ('extract_init','extract_test','extract_decrement'):groups['ordenar_heapsort'][token]='for (i = n;'
    for token in ('extract_swap_call','extract_swap_resume'):groups['ordenar_heapsort'][token]='intercambiar(&arreglo[0]'
    for token in ('extract_heap_call','extract_heap_resume'):groups['ordenar_heapsort'][token]='heapify(arreglo, i - 1, 0);'
    for side,child in [('left','izquierdo'),('right','derecho')]:
        for token in (side+'_bound',side+'_compare',side+'_test','largest_'+side):groups['heapify'][token]=f'if ({child} < n'
    for token in ('heap_swap_call','heap_swap_resume'):groups['heapify'][token]='intercambiar(&arreglo[raiz]'
    for token in ('heap_rec_call','heap_rec_resume'):groups['heapify'][token]='heapify(arreglo, n, mayor);'
    for token in ('swap_a_null','swap_b_null','swap_guard'):groups['intercambiar'][token]='if (a == NULL'
    for name,tokens in groups.items():
        start=next(k for k,row in enumerate(rows) if re.match(r'\s*(?:static )?(?:void|int) '+name+r'\(',row));balance=0
        for end in range(start,len(rows)):
            balance+=rows[end].count('{')-rows[end].count('}')
            if end>start and balance==0:break
        for token,pattern in tokens.items():lookup[token]=start if pattern is None else end if pattern=='}' else next(k for k in range(start,end+1) if pattern in rows[k])
    return lookup

def instruction_pedagogy(raw,line_index,line_text):
    presentation=deepcopy(raw);event=raw['instruction_event'];presentation['instruction_event']={**event,'i':event['i'] or 0,'j':0}
    frame=typed_frame(presentation,line_index,line_text);calls=[];depth=0
    for name in raw['instruction_stack']:
        params={'arreglo':'arreglo del caller','n':len(raw['array_snapshot'])}
        if name=='heapify':
            f=event['frames'][depth];depth+=1;params={'arreglo':'arreglo del caller','n':f['n'],'raiz':f['raiz']}
        elif name=='intercambiar':params={p['name']:p['target'] for p in raw['instruction_pointers']}
        calls.append(dict(function=name,parameters=params,continuation='retornar al caller conservando sus locales'))
    frame['call_stack']=calls;context=raw['heap_context'];phase=context['phase'];frame['loop']=None
    if phase:
        frame['loop']=dict(kind=('for construccion' if phase=='build' else 'for extraccion')+(' (caller suspendido)' if len(calls)>1 else ''),iteration=event['i'],bounds=[0 if phase=='build' else 1,len(raw['array_snapshot'])],exit=raw['line_token'] in ('build_test','extract_test') and raw['condition_result'] is False)
    if raw['line_token'] in ('left_compare','right_compare'):frame['concept']='comparison'
    text='Propiedad max-heap del prefijo activo: '+('cumple' if context['max_heap'] else 'no cumple')+'. Estado observado; la construccion parcial no certifica el heap global. El sufijo separado contiene solo extracciones terminadas.'
    if raw['line_token']=='swap_assign_a':text+=' Duplicacion provisional; temporal conserva el valor pendiente de *b=temporal.'
    frame['invariant']=dict(text=text,indices=raw['sorted_indices'],holds=context['max_heap']);return frame
