"""Execute real sorting caller output over its accepted algorithm memory journal.

The existing bounded C AST/VM evaluates main and the canonical print helper.
Only sorting calls use already accepted memory effects, so GET never sorts again.
There is no array-to-text renderer or compiler dependency in this module.
"""
from __future__ import annotations

from copy import deepcopy
from functools import lru_cache
import re
from typing import Any

from app.domain.graph.book_c_subset import GraphMachine, Program
from app.domain.sorting import SORTING_ALGORITHMS
from app.services.c_code_service import CCodeService
from app.services.caller_printf import c_printf
from app.services.sorting_main_program import build_sorting_main


_SORT_CALLS = {a['c_function']: a['id'] for a in SORTING_ALGORITHMS}


@lru_cache(maxsize=128)
def _program(source: str, name: str) -> Program:
    """Adapt only C parameter/automatic-array storage to the VM's typed pointer ABI."""
    adapted = re.sub(r'\bconst\s+int\s+arreglo\[\s*\]', 'const int *arreglo', source)
    if name == 'main':
        adapted = adapted.replace('int main(void)', 'int caller_output(int *storage)')
        declaration = 'int arreglo[80] = {0};'
        if adapted.count(declaration) != 1:
            raise ValueError('Unsupported sorting caller array declaration.')
        adapted = adapted.replace(declaration, 'int *arreglo = storage;')
    else:
        adapted, count = re.subn(r'(\b(?:int|void)\s+)' + re.escape(name) + r'(?=\s*\()',
                                 r'\1caller_output', adapted, count=1)
        if count != 1:
            raise ValueError('Missing actual sorting print helper.')
    parsed = Program(adapted, caller_output=True)
    function = parsed.functions.pop('caller_output')
    function['name'] = name
    parsed.functions[name] = function
    return parsed


class _CallerMachine(GraphMachine):
    """Reuse C expressions/statements/memory; dispatch printf through the actual CRT."""

    def __init__(self, main: str, effects: list[dict[str, Any]], helper_source: str):
        self.actual_sources = {'main': main}
        self.source_line_offsets = {'main': 0}
        self.programs = {'main': _program(main, 'main')}
        for name in ('arreglo_valido', 'imprimir_arreglo'):
            source = CCodeService._extract_function_with_comment(helper_source, name)
            if not source:
                raise ValueError('Missing canonical sorting output function: ' + name)
            self.actual_sources[name] = source
            self.source_line_offsets[name] = helper_source[:helper_source.index(source)].count('\n')
            self.programs[name] = _program(source, name)
        super().__init__(self.programs['main'], [], [], record_events=False, event_limit=200_000)
        self.heap['caller_array'] = dict(id='caller_array', kind='int', element_type='int',
                                         items=[0] * 80, alive=True, borrowed=True, bytes=320)
        self.effects = iter(effects)
        self.calls: list[dict[str, Any]] = []
        self.output_events: list[dict[str, Any]] = []

    def emit(self, node, phase, name='', value=None, change=None):
        # This is a caller-output evaluator, not a second algorithm trace builder.
        self._count_event()
        if change:
            change()

    def invoke(self, function, args):
        previous = self.program
        self.program = self.programs[function]
        try:
            return super().invoke(function, args)
        finally:
            self.program = previous

    def _eval(self, node):
        if node.kind == 'name' and node.data['name'] == 'ORDENAMIENTO_OK':
            return 1
        if node.kind != 'call':
            return super()._eval(node)
        function = node.data['function'].data['name']
        args = [self.eval(arg) for arg in node.data['args']]
        if function == 'printf':
            text = c_printf(args[0], args[1:])
            active = self.frames[-1]['function']
            self.output_events.append(dict(kind='stdout', text=text, source_role='caller',
                source_file='main.c' if active == 'main' else 'tad_ordenamiento.c',
                function=active, callee='printf', line_index=self.source_line_offsets[active] + node.token.line,
                line_text=self.actual_sources[active].splitlines()[node.token.line]))
            self.stdout += text
            return len(text.encode('utf-8'))
        if function in _SORT_CALLS:
            effect = next(self.effects)
            pointer, size = args
            memory = self.heap[pointer]['items']
            if effect['algorithm'] != _SORT_CALLS[function] or memory[:size] != effect['input']:
                raise ValueError('Sorting caller memory journal does not match its real call.')
            self.calls.append(dict(function=function, stdout_before=self.stdout,
                                   event_offset=len(self.output_events), source_role='accepted-algorithm-effect'))
            memory[:size] = list(effect['output'])
            # Only successfully accepted runs occur in build_sorting_main. The
            # int-returning canonical calls commit ORDENAMIENTO_OK on this path.
            return 1
        if function in self.programs:
            return self.invoke(function, args)
        raise ValueError('Unsupported sorting caller function: ' + function)


def execute_sorting_caller(history: list[dict[str, Any]]) -> dict[str, Any]:
    """Interpret actual accepted caller C; consume effects without algorithm replay."""
    if not any(e.get('operation') in {'create_array', 'generate_random_array'} for e in history):
        return dict(stdout='', events=[], calls=[])
    main = build_sorting_main(history)
    source = (CCodeService._DOCS_TADS_C / 'tad_ordenamiento.c').read_text(encoding='utf-8-sig')
    effects = [dict(algorithm=e['payload']['algorithm_id'], **e['array_effect'])
               for e in history if e['operation'] == 'run']
    machine = _CallerMachine(main, effects, source)
    status = machine.invoke('main', ['caller_array'])
    if status != 0 or next(machine.effects, None) is not None:
        raise ValueError('Sorting caller did not finish its accepted memory journal.')
    return dict(stdout=machine.stdout, events=machine.output_events, calls=machine.calls)


def _decorate_frame(frame: dict[str, Any], final_index: int, suffix: str, events: list[dict[str, Any]]) -> dict[str, Any]:
    frame['console_stdout'] = suffix if frame['step_index'] == final_index else ''
    frame['caller_console_events'] = deepcopy(events) if frame['step_index'] == final_index else []
    return frame


class _CallerPageSource:
    """Add caller stdout to dense/sparse transport without changing native tape events."""

    def __init__(self, source, prefix: str, suffix: str, events: list[dict[str, Any]]):
        self.source, self.prefix, self.suffix, self.events = source, prefix, suffix, events
        from app.services.counting_trace_service import deep_size
        self.retained_bytes = source.retained_bytes + deep_size([prefix, suffix, events])

    def __getattr__(self, name):
        return getattr(self.source, name)

    def frame(self, index, dense=False):
        return _decorate_frame(self.source.frame(index, dense=dense), len(self.source.tape)-1, self.suffix, self.events)

    def page(self, start, limit=64):
        page = self.source.page(start, limit)
        for frame in page['steps']:
            _decorate_frame(frame, len(self.source.tape)-1, self.suffix, self.events)
        page['console_prefix'] = self.prefix
        return page

    def trace(self):
        trace = self.source.trace()
        _decorate_trace(trace, self.prefix, self.suffix, self.events)
        trace.page_source = self
        return trace

    def compact_export(self):
        result = self.source.compact_export()
        result.update(console_prefix=self.prefix, caller_console_suffix=self.suffix,
                      caller_console_events=deepcopy(self.events))
        return result


def _decorate_trace(trace, prefix, suffix, events):
    trace['console_prefix'] = prefix
    trace['console_output'] = prefix + suffix
    trace['caller_console_source'] = 'accepted-main-c-ast/v1'
    final_index = trace.get('step_count', len(trace.get('steps', []))) - 1
    for frame in trace.get('steps', []):
        _decorate_frame(frame, final_index, suffix, events)
    for frame in trace.get('initial_page', {}).get('steps', []):
        _decorate_frame(frame, final_index, suffix, events)


def attach_sorting_caller_console(response: dict[str, Any], *, before_history: list[dict[str, Any]], operation: str) -> None:
    """Attach actual caller output and its last-call cursor boundary to an API result."""
    history = response.get('history', before_history)
    executed = execute_sorting_caller(history)
    previous = execute_sorting_caller(before_history)
    response['console_output'] = executed['stdout']
    response['console_prefix'] = previous['stdout']
    response['console_stdout'] = executed['stdout'][len(previous['stdout']):]
    trace = response.get('execution_trace')
    if not trace:
        return
    prefix, suffix, events = executed['stdout'], '', []
    if operation in {'run', 'step'} and response.get('success') and executed['calls']:
        call = executed['calls'][-1]
        prefix = call['stdout_before']
        suffix = executed['stdout'][len(prefix):]
        events = executed['events'][call['event_offset']:]
    if hasattr(trace, 'page_source'):
        wrapper = _CallerPageSource(trace.page_source, prefix, suffix, events)
        response['execution_trace'] = trace = wrapper.trace()
    else:
        _decorate_trace(trace, prefix, suffix, events)
    if response.get('step') is not None:
        frame = response['step']
        count = response.get('total_steps', len(trace.get('steps', [])))
        _decorate_frame(frame, count-1, suffix, events)
