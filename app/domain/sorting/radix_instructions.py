"""Radix C-equivalent instruction model for the whole public int32 domain."""
from __future__ import annotations
from copy import deepcopy
from typing import Any,Callable
from app.domain.sorting.radix_tape import RadixTape
from app.domain.sorting.tad_ordenamiento import SortingExecutionError

class SimulatedRadixAllocationFailure(MemoryError):
    """Private TESTING allocator marker; never selected by a request field."""

class RadixExecutionFailure(SortingExecutionError):
    """Failed modeled C call and partial immutable tape; no accepted mutation."""
    def __init__(self,message:str,steps:RadixTape,metrics:dict,error_info:dict):
        super().__init__(message);self.steps=steps;self.metrics=metrics;self.error_info=error_info;self.execution_trace=None

class RadixInstructionEngine:
    """Explicit wrapper/helper control flow, uint32 magnitudes and masked mallocs."""
    def __init__(self,values:list[int],allocator:Callable | None=None):
        self.a=list(values);self.n=len(values);self.tape=RadixTape();self.allocator=allocator;self.failure=None;self.attempts=0
        self.s=dict(wrapper_active=False,wrapper_declared=False,helper_active=False,helper_declared=False,valid_active=False,
                    ng=0,pg=0,wi=None,di=None,indice=None,block=None,maximo=None,exp=None,valor=None,digito=None,magnitud=None,
                    helper_n=0,helper_exp=None,group=None,counts=None,phase=None,
                    buffers={k:dict(capacity=self.n if k!='output' else 0,status='undeclared',live=False,cells=None) for k in ['negative','positive','output']},
                    allocations=0,frees=0,max_value_comparisons=0,sign_tests=0,work_writes=0,count_writes=0,digit_output_writes=0,caller_writes=0)
    def metrics(self) -> dict:
        return dict(comparisons=self.s['max_value_comparisons'],moves=sum(self.s[k] for k in ['work_writes','count_writes','digit_output_writes','caller_writes']),swaps=0,steps=len(self.tape))
    def event(self,token:str,condition:bool | None,status:int | None) -> dict:
        s=self.s;b=s['buffers']
        return dict(token=token,condition=condition,array=list(self.a),negative=list(b['negative']['cells'][:s['ng']]) if b['negative']['live'] else None,
                    positive=list(b['positive']['cells'][:s['pg']]) if b['positive']['live'] else None,digit_output=deepcopy(b['output']['cells']) if b['output']['live'] else None,
                    counts=list(s['counts']) if s['helper_active'] and s['counts'] is not None else None,
                    wrapper_active=s['wrapper_active'],helper_active=s['helper_active'],valid_active=s['valid_active'],wrapper_i=s['wi'],helper_i=s['di'],maximo=s['maximo'],exp=s['exp'],valor=s['valor'],digito=s['digito'],
                    negative_count=s['ng'],positive_count=s['pg'],caller_output_index=s['indice'] or 0,allocations=s['allocations'],frees=s['frees'],live=s['allocations']-s['frees'],
                    **{k:s[k] for k in ['max_value_comparisons','sign_tests','work_writes','count_writes','digit_output_writes','caller_writes']},return_status=status)
    def emit(self,token:str,condition:bool | None=None,expression:str='',*,status:int | None=None,source_hint:str | None=None) -> None:
        function='arreglo_valido' if token.startswith('valid_') else 'counting_por_digito' if token.startswith('digit_') else None if token=='initial' else 'ordenar_radixsort'
        actions={'initial':'Antes de llamar ordenar_radixsort; ninguna instruccion C ejecutada.',
                 'radix_declare':'Declarar punteros y escalares; cant_negativos/cant_positivos inicializados en cero.',
                 'digit_declare':'Inicializar conteo[10] automatico a cero; salida e i aun sin inicializar.',
                 'digit_allocate':'malloc reserva salida sin inicializar sus celdas.' if self.s['buffers']['output']['live'] else 'malloc devuelve NULL; ninguna celda de salida existe.',
                 'negative_allocate':'Evaluar malloc para negativos; reserva indeterminada o NULL.',
                 'positive_allocate':'Evaluar malloc para positivos; reserva indeterminada o NULL.',
                 'digit_output_write':'Escribir salida[conteo[digito]-1]=valor; aun falta decrementar frecuencia.',
                 'digit_frequency_decrement':'Decrementar conteo[digito] despues de escribir salida.',
                 'digit_free':'Ejecutar free(salida); retirar reserva sin leerla ni asignar NULL al puntero C.',
                 'negative_free':'Ejecutar free(negativos), incluido NULL; no leer reserva retirada.',
                 'positive_free':'Ejecutar free(positivos), incluido NULL; no leer reserva retirada.',
                 'negative_caller_write':'Recomponer magnitud, proteger INT_MIN y completar arreglo[indice++].',
                 'positive_caller_write':'Completar arreglo[indice++]=(int)positivos[i].',
                 'radix_return':f'Retornar ORDENAMIENTO_{"OK" if status else "ERROR"} ({status}) y retirar parametros/locales del wrapper.',
                 'digit_return':f'Retornar ORDENAMIENTO_{"OK" if status else "ERROR"} ({status}); retirar locales del helper y recuperar caller.'}
        self.tape.append(dict(step=len(self.tape)+1,line_token=token,source_hint=source_hint,source_function=function,condition_result=condition,condition_expression=expression or token.replace('_',' '),action=actions.get(token,token.replace('_',' ')),array_snapshot=list(self.a),radix_context=deepcopy(self.s),console_output='',metrics={k:v for k,v in self.metrics().items() if k!='steps'},instruction_event=self.event(token,condition,status)))
    def cond(self,token:str,value:bool,expression:str='') -> bool:
        if token.endswith('max_compare'):self.s['max_value_comparisons']+=1
        if token=='sign_test':self.s['sign_tests']+=1
        self.emit(token,value,expression);return value
    def reserve(self,name:str,capacity:int) -> None:
        b=self.s['buffers'][name];b.update(capacity=capacity,status='NULL',live=False,cells=None);self.attempts+=1
        try:
            if self.allocator:self.allocator(name,capacity,self.attempts)
            cells=[None]*capacity
        except MemoryError as error:
            sim=isinstance(error,SimulatedRadixAllocationFailure)
            self.failure=dict(code='allocation-null',origin='qa-injection' if sim else 'python-model-allocation',simulated=sim,real_c_execution=False,native_status=0,label='Fallo simulado de malloc para QA; no agotamiento real de memoria.' if sim else 'Fallo de reserva del modelo Python; ruta C equivalente, no allocator C real.',message='No se pudo reservar memoria para Radix.')
        else:
            b.update(status='live',live=True,cells=cells);self.s['allocations']+=1
    def free(self,name:str,token:str,hint:str) -> None:
        b=self.s['buffers'][name]
        if b['live']:self.s['frees']+=1;b.update(live=False,status='freed',cells=None)
        self.emit(token,source_hint=hint)
    def valid(self) -> bool:
        self.s['valid_active']=True;self.emit('valid_entry');ok=self.cond('valid_ptr',True,'arreglo != NULL') and self.cond('valid_n',self.n>0,f'{self.n} > 0')
        self.s['valid_active']=False;self.emit('valid_return',status=int(ok));return ok
    def retire_helper(self,status:int) -> None:
        self.s.update(helper_active=False,helper_declared=False,counts=None,di=None,valor=None,digito=None)
        self.emit('digit_return',status=status,source_hint='digit_error' if not status else None)
    def finish(self,status:int,hint:str | None=None) -> dict:
        self.s.update(wrapper_active=False,wrapper_declared=False,wi=None,block=None,maximo=None,exp=None,magnitud=None)
        self.emit('radix_return',status=status,source_hint=hint)
        if not status:
            info=self.failure or dict(code='invalid-array',origin='native-semantic-guard',simulated=False,real_c_execution=False,native_status=0,label='Entrada rechazada por el contrato C.',message='El arreglo no puede estar vacio.')
            raise RadixExecutionFailure(info['message'],self.tape,self.metrics(),info)
        return dict(steps=self.tape,metrics=self.metrics(),final_state={'items':list(self.a)})
    def counting_digit(self,arr:list[int | None],exp:int) -> int:
        s=self.s;n=s['ng'] if s['group']=='negative' else s['pg'];s.update(helper_active=True,helper_declared=False,helper_n=n,helper_exp=exp,counts=None,di=None,valor=None,digito=None)
        self.emit('digit_entry');s.update(helper_declared=True,counts=[0]*10);s['buffers']['output'].update(capacity=n,status='uninitialized',live=False,cells=None);self.emit('digit_declare')
        self.reserve('output',n);self.emit('digit_allocate')
        if self.cond('digit_allocation_guard',not s['buffers']['output']['live'],'salida == NULL'):
            self.retire_helper(0);return 0
        counts=s['counts'];out=s['buffers']['output']['cells'];s['di']=0;self.emit('digit_fill_init')
        while self.cond('digit_fill_test',s['di']<n,f'{s["di"]} < {n}'):
            digit=(arr[s['di']]//exp)%10;counts[digit]+=1;s['count_writes']+=1;self.emit('digit_frequency_write');s['di']+=1;self.emit('digit_fill_increment')
        s['di']=1;self.emit('digit_prefix_init')
        while self.cond('digit_prefix_test',s['di']<10,f'{s["di"]} < 10'):
            counts[s['di']]+=counts[s['di']-1];s['count_writes']+=1;self.emit('digit_prefix_write');s['di']+=1;self.emit('digit_prefix_increment')
        s['di']=n;self.emit('digit_reverse_init')
        while self.cond('digit_reverse_test',s['di']>0,f'{s["di"]} > 0'):
            s['valor']=arr[s['di']-1];s['digito']=None;self.emit('digit_value_read');s['digito']=(s['valor']//exp)%10;self.emit('digit_select')
            pos=counts[s['digito']]-1;assert 0<=pos<n;out[pos]=s['valor'];s['digit_output_writes']+=1;self.emit('digit_output_write');counts[s['digito']]-=1;s['count_writes']+=1;self.emit('digit_frequency_decrement')
            s['di']-=1;s['valor']=s['digito']=None;self.emit('digit_reverse_decrement')
        s['di']=0;self.emit('digit_copy_init')
        while self.cond('digit_copy_test',s['di']<n,f'{s["di"]} < {n}'):
            assert out[s['di']] is not None;arr[s['di']]=out[s['di']];s['work_writes']+=1;self.emit('digit_work_copy');s['di']+=1;self.emit('digit_copy_increment')
        self.free('output','digit_free','digit_free');self.retire_helper(1);return 1
    def run(self,digit_executor:Callable) -> dict:
        s=self.s;self.emit('initial');s['wrapper_active']=True;self.emit('radix_entry');s['wrapper_declared']=True
        for name in ['negative','positive']:s['buffers'][name]['status']='uninitialized'
        self.emit('radix_declare')
        if self.cond('radix_invalid_guard',not self.valid(),'!arreglo_valido(arreglo,n)'):return self.finish(0,'radix_invalid_guard')
        self.reserve('negative',self.n);self.emit('negative_allocate');self.reserve('positive',self.n);self.emit('positive_allocate')
        invalid=self.cond('negative_null',not s['buffers']['negative']['live'],'negativos == NULL') or self.cond('positive_null',not s['buffers']['positive']['live'],'positivos == NULL')
        if self.cond('split_reserve_guard',invalid,'negativos == NULL || positivos == NULL'):
            self.free('negative','negative_free','split_cleanup');self.free('positive','positive_free','split_cleanup');return self.finish(0,'split_cleanup')
        s['wi']=0;s['phase']='split';self.emit('split_init')
        while self.cond('split_test',s['wi']<self.n,f'{s["wi"]} < {self.n}'):
            value=self.a[s['wi']]
            if self.cond('sign_test',value<0,f'{value} < 0'):
                s['buffers']['negative']['cells'][s['ng']]=(-value)&0xffffffff;s['ng']+=1;s['work_writes']+=1;self.emit('negative_write')
            else:
                s['buffers']['positive']['cells'][s['pg']]=value;s['pg']+=1;s['work_writes']+=1;self.emit('positive_write')
            s['wi']+=1;self.emit('split_increment')
        for group,key in [('negative','ng'),('positive','pg')]:
            prefix=group;size=s[key]
            if self.cond(prefix+'_group_guard',size>0,f'cant_{"negativos" if group=="negative" else "positivos"} > 0'):
                s.update(block=group,group=group,phase=group+' digits',maximo=s['buffers'][group]['cells'][0],exp=1);self.emit(prefix+'_max_exp_init')
                s['wi']=1;self.emit(prefix+'_scan_init')
                while self.cond(prefix+'_scan_test',s['wi']<size,f'{s["wi"]} < {size}'):
                    value=s['buffers'][group]['cells'][s['wi']]
                    if self.cond(prefix+'_max_compare',value>s['maximo'],f'{value} > {s["maximo"]}'):
                        s['maximo']=value;self.emit(prefix+'_max_assign')
                    s['wi']+=1;self.emit(prefix+'_scan_increment')
                execute=group=='negative' or self.cond('positive_nonzero_guard',s['maximo']>0,f'{s["maximo"]} > 0')
                if execute:
                    while True:
                        self.emit(prefix+'_digit_call');status=digit_executor(s['buffers'][group]['cells'],s['exp'])
                        if self.cond(prefix+'_digit_status',not status,f'!counting_por_digito({"negativos, cant_negativos" if group=="negative" else "positivos, cant_positivos"}, exp)'):
                            hint=prefix+'_helper_cleanup';self.free('negative','negative_free',hint);self.free('positive','positive_free',hint);return self.finish(0,hint)
                        if self.cond(prefix+'_exp_guard',s['exp']>s['maximo']//10,f'{s["exp"]} > {s["maximo"]}//10'):
                            self.emit(prefix+'_break');break
                        s['exp']*=10;self.emit(prefix+'_exp_multiply')
            s.update(block=None,maximo=None,exp=None);self.emit(prefix+'_block_exit')
        s['indice']=0;s['phase']='recombine';self.emit('caller_index_init');s['wi']=s['ng'];self.emit('negative_join_init')
        while self.cond('negative_join_test',s['wi']>0,f'{s["wi"]} > 0'):
            s['magnitud']=s['buffers']['negative']['cells'][s['wi']-1];self.emit('negative_magnitude_read')
            special=self.cond('INT_MIN_magnitude_guard',s['magnitud']==2147483648,'magnitud == (uint32_t)INT_MAX + 1U')
            self.a[s['indice']]=-2147483648 if special else -s['magnitud'];s['indice']+=1;s['caller_writes']+=1;self.emit('negative_caller_write');s['wi']-=1;s['magnitud']=None;self.emit('negative_join_decrement')
        s['wi']=0;self.emit('positive_join_init')
        while self.cond('positive_join_test',s['wi']<s['pg'],f'{s["wi"]} < {s["pg"]}'):
            self.a[s['indice']]=s['buffers']['positive']['cells'][s['wi']];s['indice']+=1;s['caller_writes']+=1;self.emit('positive_caller_write');s['wi']+=1;self.emit('positive_join_increment')
        self.free('negative','negative_free','final_cleanup');self.free('positive','positive_free','final_cleanup');return self.finish(1)
