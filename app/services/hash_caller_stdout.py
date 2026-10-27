"""Attach executed Hash caller printf events after actual TAD return cells."""
from __future__ import annotations
from copy import deepcopy
from typing import Any
from app.services.hash_caller_program import output_program, output_lines


def table_cells(state: dict[str, Any]) -> dict[str, Any]:
    """Copy the public C fields and linked heads, preserving their stored order."""
    capacity = int(state['metadata']['capacity'])
    heads = [None] * capacity
    for bucket in state.get('buckets', []):
        following = None
        for entry in reversed(bucket['entries']):
            following = {'clave': entry['key'], 'valor': entry['value'], 'siguiente': following}
        heads[bucket['index']] = following
    return {'capacidad': capacity, 'cantidad': int(state['metadata']['size']),
            'buckets': heads if capacity else None}


def validate_listing_storage(step: dict[str, Any], state: dict[str, Any]) -> None:
    """Bind the public heads to actual trace heap cells before caller traversal."""
    heap = {node['id']: node for node in step['pedagogy']['memory']['heap']}
    for bucket in state.get('buckets', []):
        entries = bucket['entries']
        for index, entry in enumerate(entries):
            node = heap[entry['address']]
            following = entries[index+1]['address'] if index+1 < len(entries) else None
            if (node['key'], node['value']) != (entry['key'], entry['value']):
                raise ValueError('Caller projection does not match C heap cells')
            if (node.get('next') or None) not in (following, 'NULL' if following is None else following):
                raise ValueError('Caller traversal does not match C next pointer')


def attach_caller_stdout(trace: dict[str, Any], operation: str, payload: dict[str, Any],
                         state: dict[str, Any]) -> str:
    """Interpret the shared output AST; never derive formatted text from result."""
    steps = trace.get('steps', [])
    for step in steps:
        step['console_stdout'] = ''
    trace['console_mode'] = 'events'
    trace['console_stdout'] = ''
    if not steps or payload.get('simulate_allocation_failure') in (True, 'true', '1', 1):
        return ''  # Diagnostic injection is explicitly absent from downloadable main.
    debug = steps[-1].get('debug', {})
    required = {'create_table': 'init_return', 'insert': 'insert_return',
        'get': 'search_return', 'contains': 'contains_return', 'remove': 'remove_return',
        'stats': 'formatter_return', 'keys': 'formatter_return',
        'values': 'formatter_return', 'items': 'formatter_return'}
    if operation not in required or debug.get('token') != required[operation]:
        return ''  # API rejection and void cleanup do not execute a printf.
    cells = {'tabla': table_cells(state)}
    root = debug.get('root')
    if root:
        if (root['capacity'], root['size']) != (cells['tabla']['capacidad'], cells['tabla']['cantidad']):
            raise ValueError('Caller public table does not match returned C root')
        cells['tabla']['capacidad'], cells['tabla']['cantidad'] = root['capacity'], root['size']
    if operation in {'keys', 'values', 'items'}:
        validate_listing_storage(steps[-1], state)
    for key in ('key', 'value'):
        if key in payload:
            cells[key] = int(payload[key])
    if operation == 'insert': cells['ok'] = debug['return_status']
    if operation in {'get', 'contains'}:
        cells['found'] = debug['return_status']
        if operation == 'get' and cells['found']:
            output = debug['output']
            if not output['alive'] or not output['initialized']:
                raise ValueError('Caller output cell is not readable')
            cells['output'] = output['value']
    if operation == 'remove': cells['removed'] = debug['return_status']
    if operation in {'keys', 'values', 'items', 'stats'}:
        buffer = debug['buffer']
        if not buffer['alive'] or not buffer.get('bytes') or 0 not in buffer['bytes']:
            raise ValueError('Caller formatter buffer is not terminated and alive')
        # The exact initialized C buffer, not a reformatted API projection.
        text = bytes(buffer['bytes']).split(b'\0', 1)[0].decode('ascii')
        cells['texto' if operation == 'stats' else 'buffer'] = text
    if operation == 'stats':
        record = debug['variables']['caller.stats']
        if not record['initialized']:
            raise ValueError('Caller statistics record is uninitialized')
        cells['stats'] = deepcopy(record['value'])
    template = deepcopy(steps[-1])
    steps[-1]['phase'] = 'progress'
    stdout = ''
    caller_lines = output_lines(operation)
    trace['caller_source_code'] = '\n'.join(caller_lines)

    def emit(line, fragment, current):
        nonlocal stdout
        stdout += fragment
        step = deepcopy(template)
        step.update(step_index=len(steps), line_index=-1, line_text='', event_type='caller_printf',
                    phase='progress', console=[fragment], console_stdout=stdout,
                    instruction_event={'token': 'caller_printf', 'function': 'main',
                        'source_role': 'caller', 'C_executed': True, 'caller_line_text': line})
        observed = {key: deepcopy(value) for key, value in current.items() if key not in {'tabla', 'node'}}
        if current.get('node') is not None:
            observed['node'] = {key: current['node'][key] for key in ('clave', 'valor')}
        step['debug'].update(token='caller_printf', function='main', caller_line_text=line,
                             source_role='caller', caller_variables=observed)
        frame = step.get('pedagogy', {})
        frame['source'] = {'line_index': None, 'line_text': line, 'function': 'main', 'source_role': 'caller'}
        frame['narration'] = {level: 'El caller ejecuta '+line+' y agrega exactamente su fragmento a stdout.'
                              for level in ('basic', 'intermediate', 'advanced')}
        frame['caller_stdout'] = stdout
        frame['caller_variables'] = observed
        steps.append(step)

    for statement in output_program(operation):
        statement.execute(cells, emit)
    steps[-1]['phase'] = 'end'
    trace['console_stdout'] = stdout
    return stdout


def program_epilogue_stdout(state: dict[str, Any]) -> str:
    """Only standalone main's exit prints state; an interactive call does not."""
    fragments = []
    for statement in output_program('epilogue'):
        statement.execute({'tabla': table_cells(state)}, lambda line, text, cells: fragments.append(text))
    return ''.join(fragments)
