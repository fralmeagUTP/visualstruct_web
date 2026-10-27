"""Finite independent C17 oracles for the shared Hash caller-output AST."""
from pathlib import Path
import hashlib
import shutil
import struct
import subprocess
import pytest
from app.services.caller_printf import c_printf
from app.services.hash_caller_stdout import program_epilogue_stdout

ROOT = Path(__file__).resolve().parents[1]


def native(tmp_path, source):
    for name in ('tad_tabla_hash.c', 'tad_tabla_hash.h'):
        shutil.copyfile(ROOT / 'docs/tads_C' / name, tmp_path / name)
    (tmp_path / 'main.c').write_text(source, encoding='utf8')
    compiler = shutil.which('gcc')
    assert compiler, 'This independent oracle requires a native C17 compiler'
    built = subprocess.run([compiler, '-std=c17', '-Wall', '-Wextra', '-Wpedantic', '-Werror',
                            str(tmp_path / 'main.c'), str(tmp_path / 'tad_tabla_hash.c'), '-o', str(tmp_path / 'caller.exe')],
                           capture_output=True, text=True, timeout=30)
    assert built.returncode == 0, built.stderr
    result = subprocess.run([str(tmp_path / 'caller.exe')], capture_output=True, text=True, timeout=15)
    assert result.returncode == 0, result.stderr
    return result.stdout


@pytest.mark.parametrize('operations', [
    [('create_table', {'capacity': 3}), ('insert', {'key': 1, 'value': 10}),
     ('insert', {'key': 4, 'value': 20}), ('insert', {'key': -2, 'value': -2147483648}),
     ('insert', {'key': 1, 'value': -17}), ('get', {'key': 1}), ('get', {'key': 1}),
     ('get', {'key': 99}), ('contains', {'key': -2}), ('contains', {'key': 99}),
     ('keys', {}), ('values', {}), ('items', {}), ('stats', {}),
     ('remove', {'key': 4}), ('remove', {'key': 99}), ('stats', {}),
     ('clear', {}), ('keys', {}), ('stats', {}), ('destroy_table', {}),
     ('get', {'key': 1}), ('contains', {'key': 1}), ('items', {}), ('stats', {})],
    [('create_table', {'capacity': 64}), ('keys', {}), ('stats', {}),
     ('insert', {'key': -2147483648, 'value': 2147483647}),
     ('get', {'key': -2147483648}), ('values', {}), ('stats', {})],
])
def test_hash_journal_stdout_matches_native_c17(client, tmp_path, operations):
    hashes = {name: hashlib.sha256((ROOT / 'docs/tads_C' / name).read_bytes()).hexdigest()
              for name in ('tad_tabla_hash.c', 'tad_tabla_hash.h')}
    complete = ''
    for operation, payload in operations:
        response = client.post('/hash/hash_table/operate', json={'operation': operation, 'payload': payload})
        data = response.get_json()
        assert response.status_code in (200, 400) and not data.get('preserve_session'), data
        assert data['console_prefix'] == complete
        trace = data['execution_trace']
        assert trace['console_prefix'] == complete
        fragments = ''.join(fragment for step in trace['steps'] for fragment in step['console'])
        assert fragments == data['console_stdout']
        if operation in {'clear', 'destroy_table'}:
            assert fragments == ''
        if operation == 'get' and payload['key'] == 99:
            assert fragments == 'get:99:0\n'
            assert '123456789' not in fragments
        emitted = ''
        for step in trace['steps']:
            emitted += ''.join(step['console'])
            assert step['console_stdout'] == emitted
            if step['console']:
                assert step['event_type'] == 'caller_printf'
                assert step['instruction_event']['source_role'] == 'caller'
                assert step['line_index'] == -1
        # Seeking reads a snapshot; it never emits/duplicates another printf.
        for cursor in [len(trace['steps'])-1, 0, len(trace['steps'])//2, len(trace['steps'])-1]:
            assert fragments.startswith(trace['steps'][cursor]['console_stdout'])
        complete += fragments
        assert data['console_output'] == complete
    expected = complete + program_epilogue_stdout(data['visual_state'])
    assert native(tmp_path, data['main_c']) == expected
    page = client.get('/hash/hash_table').get_data(as_text=True)
    assert 'console_output' in page
    with client.session_transaction() as session:
        from app.services.hash_journal_service import KEY
        entries = session[KEY]['hash::hash_table']['entries']
        assert len(entries) == len(operations)
        assert ''.join(entry['caller_stdout'] for entry in entries) == complete
    for name, expected_hash in hashes.items():
        assert hashlib.sha256((ROOT / 'docs/tads_C' / name).read_bytes()).hexdigest() == expected_hash


def test_c_printf_native_promotions_and_formats(tmp_path):
    source = '#include <stdio.h>\nint main(void) { printf("%d|%.9g|%.17g|%s|%%", (-2147483647-1), (double)((float)1 / 3), 1.0/3.0, "buffer\\n"); return 0; }\n'
    cfloat = struct.unpack('f', struct.pack('f', 1/3))[0]
    assert c_printf('%d|%.9g|%.17g|%s|%%', [-2147483648, cfloat, 1/3, 'buffer\n']) == native(tmp_path, source)


@pytest.mark.parametrize('fmt,args', [('%n', [0]), ('%x', [1]), ('%d', []),
    ('%d', [1, 2]), ('%d', [2147483648]), ('%s', ['bad\0text']), ('literal\0ignored', [])])
def test_printf_rejects_unsupported_or_invalid_boundary(fmt, args):
    with pytest.raises(ValueError):
        c_printf(fmt, args)


def test_absent_output_cell_is_not_read():
    from app.services.hash_structure_service import HashStructureService as Service
    from app.services.hash_caller_stdout import attach_caller_stdout
    data = Service._execute_operation('hash_table', 'get', {'key': 99}, [])
    trace = data['execution_trace']
    trace['steps'][-1]['debug']['output'].update(initialized=False, value=None)
    assert attach_caller_stdout(trace, 'get', {'key': 99}, data['visual_state']) == 'get:99:0\n'
