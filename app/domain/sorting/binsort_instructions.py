"""Binsort's actual delegating C wrapper over the unchanged sparse Counting core."""
from __future__ import annotations
from copy import deepcopy
from app.domain.sorting.counting_sparse_tape import CountingTape
from app.domain.sorting.counting_sparse_instructions import run_counting_sparse_trace, CountingExecutionFailure
class BinsortExecutionFailure(CountingExecutionFailure):
    """Failed wrapper return with a partial, immutable delegated tape."""
class BinsortTape(CountingTape):
    def __init__(self, delegate: CountingTape, status: int):
        super().__init__()
        self.native_status = status
        self._emit(delegate[0], 'initial', active=False)
        self._emit(delegate[0], 'binsort_entry', active=True)
        self._emit(delegate[0], 'binsort_delegate', active=True)
        start = 0
        for record, end in zip(delegate.records, delegate.ends):
            if start:
                if record['kind'] == 'zero_span':
                    self.append_zero(record['start'], record['end'])
                else:
                    self._emit(delegate[start], active=True)
            start = end
        self._emit(delegate[-1], 'binsort_return', active=False)
    def _emit(self, base, token=None, *, active):
        row = deepcopy(base)
        if token:
            row['line_token'] = token
            row['instruction_event']['token'] = token
            row['instruction_event'].pop('native_status', None)
            row['condition_result'] = row['instruction_event']['condition'] = None
            row['condition_expression'] = ''
            row['instruction_variables'] = []
            row['instruction_stack'] = []
            row['instruction_pointers'] = []
            row.pop('source_line_token', None)
            row['source_function'] = 'ordenar_binsort' if token != 'initial' else None
            row['action'] = {
                'initial':'Antes de llamar ordenar_binsort; ninguna instruccion ejecutada.',
                'binsort_entry':'Entrar a ordenar_binsort con los parametros arreglo/n.',
                'binsort_delegate':'Evaluar ordenar_counting_sort(arreglo,n); mismos arreglo/n, wrapper suspendido.',
                'binsort_return':f'Retornar {"ORDENAMIENTO_OK (1)" if self.native_status else "ORDENAMIENTO_ERROR (0)"} del delegado y retirar parametros de ordenar_binsort.',
            }[token]
        if active:
            parent = [
                dict(name='arreglo',type='int *',value='arreglo del caller',scope='ordenar_binsort',initialized=True),
                dict(name='n',type='size_t',value=len(row['array_snapshot']),scope='ordenar_binsort',initialized=True),
            ]
            row['instruction_variables'] = parent + row['instruction_variables']
            row['instruction_stack'] = ['ordenar_binsort'] + row['instruction_stack']
            row['instruction_pointers'].insert(0,dict(name='arreglo',type='int *',scope='ordenar_binsort',target='arreglo del caller',value='alias compartido con ordenar_counting_sort.arreglo'))
        previous = {(v['scope'],v['name']):v for v in self._last['instruction_variables']} if self._last else {}
        for v in row['instruction_variables']:
            old = previous.get((v['scope'],v['name']))
            v['previous'] = old['value'] if old else None
            v['changed'] = old is None or (old['value'],old['initialized']) != (v['value'],v['initialized'])
        row['binsort_context'] = dict(active=active,return_status=self.native_status if token=='binsort_return' else None,delegated_function='ordenar_counting_sort',same_array_alias=True)
        row['step'] = len(self)+1
        self.append(row)
def run_binsort_sparse_trace(values, *, allocator=None):
    try:
        result = run_counting_sparse_trace(values, allocator=allocator)
    except CountingExecutionFailure as error:
        wrapped = BinsortTape(error.steps, 0)
        metrics = {**error.metrics, "steps": len(wrapped)}
        raise BinsortExecutionFailure(str(error),wrapped,metrics,error.error_info) from error
    result['steps'] = BinsortTape(result['steps'], 1)
    result['metrics']['steps'] = len(result['steps'])
    return result
