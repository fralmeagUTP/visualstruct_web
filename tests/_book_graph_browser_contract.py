"""Complete current Graph memory/console/source contract for real browser players."""
from pathlib import Path
import json
import shutil
import subprocess
from app.domain.graph.snapshot_pool import expand_graph_trace
from _book_frame_oracle import assert_book_body
from e2e_contract_helpers import main_source


def compact(value):
    return json.dumps(value, ensure_ascii=False, separators=(',', ':'))


def teaching_value(value):
    """Expected readable memory fields, including explicit retired identities."""
    if isinstance(value, dict):
        if value.get('value_status') == 'indeterminate_after_free' and value.get('usable') is False:
            return 'valor indeterminado tras liberar; no utilizar (identidad histórica ' + str(value['historical_identity']) + ')'
        return ' · '.join(str(key) + ': ' + teaching_value(item) for key, item in value.items())
    if isinstance(value, list):
        return ', '.join(map(teaching_value, value)) if value else 'vacío'
    if value is None:
        return 'sin valor'
    if isinstance(value, bool):
        return str(value).lower()
    return str(value)


COLLECT = r'''async(count)=>{
 const p=window.auditGraphPlayer,rows=[];
 function record(index,direction){rows.push({index,direction,
 heap:[...document.querySelectorAll('[data-graph-memory-node]')].map(n=>({id:n.dataset.graphMemoryNode,kind:n.dataset.graphMemoryKind,contents:n.querySelector('code').textContent})),
 live:[...document.querySelectorAll('#graph-live-memory [data-graph-live-node]')].map(n=>n.dataset.graphLiveNode),
 liveCards:[...document.querySelectorAll('#graph-live-memory [data-graph-live-node]')].map(n=>({id:n.dataset.graphLiveNode,kind:n.querySelector('small').textContent,fields:n.querySelector(':scope > div').textContent})),
 stack:[...document.querySelectorAll('[data-graph-frame]')].map(n=>({id:n.dataset.graphFrame,text:n.textContent})),
 variables:[...document.querySelectorAll('[data-graph-variable]')].map(n=>({name:n.dataset.graphVariable,scope:n.dataset.graphScope,text:n.textContent})),
 heads:document.querySelector('[data-graph-heads]')?.textContent,
 retired:document.querySelector('[data-graph-retired]')?.textContent,
 returned:document.querySelector('[data-graph-return]')?.textContent,
 auxiliary:document.querySelector('#graph-auxiliary-view details code')?.textContent,
 traversal:[...document.querySelectorAll('#graph-traversal-view code')].map(n=>n.textContent),
 condition:document.querySelector('#graph-condition-view').textContent,
 stdout:document.querySelector('#graph-printf-console').dataset.consoleCopy,
 stdoutVisible:document.querySelector('#graph-printf-console').textContent,
 message:document.querySelector('#graph-message-box').textContent,
 highlighted:[...document.querySelectorAll('#op-pseudocode .code-line.sim-active')].map(n=>Number(n.dataset.line)),
 svgNodes:document.querySelectorAll('#graph-visual-state circle.viz-graph-node').length});}
 p.reset();record(-1,'initial');
 for(let i=0;i<count;i++){await p.step();record(i,'forward');}
 for(let i=count-2;i>=-1;i--){p.prev();record(i,'back');}
 p.seek(count-1);record(count-1,'seek');return rows;
}'''


def decoded_body(data):
    body = {**data, 'execution_trace': expand_graph_trace(data['execution_trace'])}
    assert_book_body(body)
    return body


def assert_browser_row(row, body):
    """Check actual DOM against every field it renders, including tombstones."""
    steps = body['execution_trace']['steps']; index = row['index']
    frame = steps[index]['pedagogy'] if index >= 0 else steps[0]['pedagogy']['initial_frame']
    memory = frame.get('memory_display', frame['memory_state'])
    assert row['heap'] == [{'id': n['id'], 'kind': n['kind'],
        'contents': compact(n.get('fields', n.get('items')))} for n in memory['heap_nodes']], (index, row['direction'])
    assert sorted(row['live']) == sorted(n['id'] for n in memory['heap_nodes'])
    assert sorted(row['liveCards'], key=lambda card: card['id']) == sorted([
        {'id': node['id'], 'kind': node['kind'] + (' · prestado' if node.get('borrowed') else ''),
         'fields': teaching_value(node.get('fields', node.get('items')))}
        for node in memory['heap_nodes']], key=lambda card: card['id'])
    heading = 'Cabezas del caller propietario: ' if frame['construction_operation'] else 'Grafo prestado: '
    assert row['heads'] == heading + compact(memory['graph'])
    assert row['retired'] == 'Retiradas (sólo registro histórico): ' + compact(memory['retired_objects'])
    assert row['returned'] == 'Retorno al caller: ' + compact(memory['returned'])
    assert row['stack'] == [{'id': f['frame_id'], 'text': f['function'] + ': ' + f['scope_status']} for f in frame['call_stack']]
    assert len(row['variables']) == len(frame['variables'])
    for actual, expected in zip(row['variables'], frame['variables']):
        assert actual['name'] == expected['name'] and actual['scope'] == expected['scope']
        assert actual['text'] == (expected['type'] + ' ' + expected['name'] + ' (' + expected['scope'] + '): ' +
            compact(expected['previous']) + ' → ' + compact(expected['value']))
    assert row['auxiliary'] == compact(frame['auxiliary']['items'])
    assert row['traversal'][:2] == [compact(frame['traversal']['tree_edges']), compact(frame['traversal']['discovery_order'])]
    if frame['condition']:
        assert frame['condition']['substituted'] in row['condition']
        assert str(frame['condition']['result']).lower() in row['condition']
    # C printf fragments already include delimiters and may repeat. No join/dedup.
    expected_stdout = body.get('console_prefix', '') + frame['memory_state'].get('console_stdout', '')
    assert row['stdout'] == expected_stdout
    assert row['stdoutVisible'] == (expected_stdout or '(sin salida printf en esta ruta)')
    assert row['message'] == (body['message'] if index == len(steps)-1 else
        'Operación preparada: resultado pendiente hasta completar las llamadas C.')
    state = steps[index]['state_after'] if index >= 0 else steps[0]['state_snapshot']
    assert row['svgNodes'] == len(state['nodes'])
    if index >= 0 and steps[index]['pedagogy']['instruction_event']['C_executed']:
        assert steps[index]['line_index'] in row['highlighted']
    elif index >= 0:
        assert steps[index]['line_index'] is None and steps[index]['line_text'] == ''


def verify_player(page, data, posts, vertices=None, *, player='auditGraphPlayer'):
    body = decoded_body(data); trace = body['execution_trace']; steps = trace['steps']
    assert trace['execution_started']
    page.evaluate('(name)=>window.auditGraphPlayer=window[name]', player)
    page.wait_for_function('(n)=>window.auditGraphPlayer.getTotalSteps()===n', arg=len(steps))
    page.evaluate('()=>window.auditGraphPlayer.pause()')
    before = len(posts); rows = page.evaluate(COLLECT, len(steps))
    assert len(rows) == 2 * len(steps) + 2
    for row in rows:
        assert_browser_row(row, body)
    assert len(posts) == before
    assert not steps[0]['pedagogy']['initial_frame']['memory_state']['frames']
    assert all(step['state_after']['last_result'] is None for step in steps[:-1])
    return {'C_events': len(trace['C_instruction_events']), 'steps': len(steps),
        'DOM_boundaries_verified': len(rows), 'replay_POSTs': 0,
        'stdout_event_indices': [i for i, step in enumerate(steps) if step['console']]}


def main_text(page):
    return main_source(page)


def compile_downloaded_main(context, base, directory, source, expected_stdout):
    """Compile actual downloaded C/H and compare complete chronological stdout."""
    directory = Path(directory); directory.mkdir(parents=True, exist_ok=True)
    for part, extension in [('source', 'c'), ('header', 'h')]:
        response = context.request.get(base + '/help/source/graph/' + part)
        assert response.status == 200
        content = response.body()
        assert content == (Path(__file__).resolve().parents[1] / 'docs/tads_C' / ('tad_grafo.' + extension)).read_bytes()
        (directory / ('tad_grafo.' + extension)).write_bytes(content)
    (directory / 'main.c').write_text(source, encoding='utf-8')
    compiler = shutil.which('gcc'); assert compiler
    built = subprocess.run([compiler, '-std=c17', '-Wall', '-Wextra', '-Wpedantic', '-Werror',
        str(directory / 'main.c'), str(directory / 'tad_grafo.c'), '-o', str(directory / 'main.exe')],
        capture_output=True, text=True, timeout=30)
    assert built.returncode == 0 and not built.stderr, built.stderr
    run = subprocess.run([str(directory / 'main.exe')], capture_output=True, text=True, timeout=15)
    assert run.returncode == 0 and not run.stderr, run.stderr
    assert run.stdout == expected_stdout, (run.stdout, expected_stdout)
    return run.stdout
