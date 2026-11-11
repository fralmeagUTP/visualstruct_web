"""Ten canonical graph operations retain precise line coordinates in filtered readers."""
from app.services.graph_code_scope import graph_algorithm_code_scopes
from app.domain.graph.book_source import canonical_source
from app.services.graph_structure_service import GraphStructureService as S
import pytest

ALGORITHMS = ('bfs', 'dfs', 'dijkstra', 'bellman_ford', 'prim', 'kruskal')
HISTORY = [dict(operation='create_graph', payload={'directed': False}, source_contract='graph-book/v1'),
           dict(operation='insert_edge', payload={'origin': 1, 'target': 2, 'weight': 3}, source_contract='graph-book/v1')]

@pytest.mark.parametrize('algorithm', ALGORITHMS + ('insert_vertex','remove_vertex','insert_edge','remove_edge'))
def test_scope_covers_every_executed_c_line_without_other_algorithms(algorithm):
    op = 'run_' + algorithm if algorithm in ALGORITHMS else algorithm
    scope = graph_algorithm_code_scopes()[op]
    if algorithm in ALGORITHMS: assert 'grafo_' + algorithm in scope['functions']
    assert all('grafo_' + other not in scope['functions'] for other in ALGORITHMS if other != algorithm)
    if algorithm in ('dijkstra','bellman_ford','prim','kruskal'):
        assert 'grafo_liberar_vertices' not in scope['functions']
    payload = {'start': 1, 'end': 2, 'vertex': 1 if algorithm=='remove_vertex' else 3, 'origin':1, 'target':2, 'weight':4}
    data = S.execute_operation('graph', op, payload, HISTORY)
    trace = data['execution_trace']
    assert trace['source_code'] == canonical_source()
    lines = canonical_source().splitlines()
    executed = 0
    for step in trace['steps']:
        line = step['line_index']
        if line is not None:
            assert any(start <= line <= end for start, end in scope['ranges']), (algorithm, line, step['line_text'])
            assert lines[line] == step['line_text']
            executed += 1
    assert executed > 20

@pytest.mark.e2e
@pytest.mark.parametrize('algorithm', ALGORITHMS + ('insert_vertex','remove_vertex','insert_edge','remove_edge'))
def test_browser_filter_selection_load_and_bidirectional_steps(app, algorithm):
    import shutil, threading
    from werkzeug.serving import make_server
    from playwright.sync_api import sync_playwright
    server=make_server('127.0.0.1',0,app,threaded=True)
    thread=threading.Thread(target=server.serve_forever,daemon=True);thread.start()
    base=f'http://127.0.0.1:{server.server_port}'
    construction=algorithm not in ALGORITHMS
    phase='construccion' if construction else 'recorridos' if algorithm in ('bfs','dfs') else 'camino-minimo' if algorithm in ('dijkstra','bellman_ford') else 'expansion-minima'
    try:
        with sync_playwright() as pw:
            browser=pw.chromium.launch(executable_path=shutil.which('chromium'),args=['--no-sandbox'])
            context=browser.new_context(viewport={'width':1440,'height':1000})
            for row in HISTORY:
                response=context.request.post(base+'/graph/graph/operate',data={**row,'execution_mode':'normal'})
                assert response.status==200
            page=context.new_page(); errors=[];posts=[];page.on('pageerror',lambda e:errors.append(str(e)))
            page.on('request',lambda r:posts.append(r.url) if r.method=='POST' and r.url.endswith('/operate') else None)
            page.add_init_script("""localStorage.setItem('didactic-mode','full');
            document.addEventListener('DOMContentLoaded',()=>{
              const original=window.InterpreterRuntime.createTracePlayer;
              window.InterpreterRuntime.createTracePlayer=(options)=>{
                const callback=options.onCursorChange;
                options.onCursorChange=(event)=>{window.testTrace=event.trace;callback(event);};
                return window.testPlayer=original(options);
              };
            });""")
            page.goto(base+'/graph/graph/'+phase,wait_until='networkidle')
            select='#graph-operation-select' if construction else '#graph-algorithm-select'
            page.locator(select).select_option(algorithm if construction else 'run_'+algorithm)
            if construction:
                fields={'vertex':1 if algorithm=='remove_vertex' else 3,'origin':1,'target':2,'weight':4}
                for key,value in fields.items():
                    field=page.locator('#g-op-field-'+key)
                    if field.count():field.fill(str(value))
            if not construction and algorithm!='kruskal':page.locator('#g-alg-field-start').fill('1')
            if algorithm in ('dijkstra','bellman_ford'):page.locator('#g-alg-field-end').fill('2')
            check=r'''() => {
              const code=document.querySelector('#op-pseudocode');
              const op=code.dataset.operation,scope=GRAPH_VIEW_MODEL.didactic.operation_code_scopes[op];
              if(!scope)throw Error('missing scope');
              const rows=[...code.querySelectorAll('.code-line')];
              for(const row of rows){
                const expected=scope.ranges.some(([a,b])=>+row.dataset.line>=a&&+row.dataset.line<=b);
                if((getComputedStyle(row).display!=='none')!==expected)throw Error('visibility '+row.dataset.line);
              }
              const names=[...document.querySelectorAll('#graph-function-list button')].map(e=>e.textContent);
              if(JSON.stringify(names)!==JSON.stringify(scope.functions))throw Error('navigation mismatch '+JSON.stringify({names,expected:scope.functions}));
              return rows.length;
            }'''
            assert page.evaluate(check)>100
            page.locator('#graph-sim-step').click()
            with page.expect_response(lambda r:r.url.endswith('/operate')) as response:page.locator('#graph-sim-play').click()
            assert response.value.status==200
            page.wait_for_function("Boolean(window.testTrace)")
            page.evaluate("testPlayer.pause(true)")
            assert page.evaluate(check)>100
            initial_posts=len(posts)
            page.locator('#graph-sim-next').click()
            page.locator('#graph-sim-prev').click()
            # Exercise actual player and DOM at every instruction, in both directions.
            result=page.evaluate(r'''() => {
              const t=testTrace,p=testPlayer,rows=[...document.querySelectorAll('#op-pseudocode .code-line')];let count=0;
              for(const reverse of [false,true]){
                for(let j=0;j<t.steps.length;j++){
                  const i=reverse?t.steps.length-1-j:j,s=t.steps[i];p.seek(i);
                  const active=document.querySelector('#op-pseudocode .sim-active');
                  if(s.line_index!=null){
                    if(active!==rows[s.line_index]||getComputedStyle(active).display==='none'||active.textContent!==s.line_text)throw Error('desync '+i);
                  }else if(active)throw Error('host highlight '+i);
                  count++;
                }
              }
              p.reset();if(document.querySelector('#op-pseudocode .sim-active'))throw Error('reset highlight');
              return count;
            }''')
            assert result>40
            assert len(posts)==initial_posts
            print(algorithm, 'verified bidirectional cursors', result)
            page.locator('#graph-hide-comments').check();page.locator('#graph-hide-comments').uncheck()
            assert page.evaluate(check)>100
            other='insert_edge' if construction and algorithm!='insert_edge' else 'remove_edge' if construction else next(a for a in ALGORITHMS if a!=algorithm and (a in ('bfs','dfs'))==(algorithm in ('bfs','dfs')) and (a in ('prim','kruskal'))==(algorithm in ('prim','kruskal')))
            page.locator(select).select_option(other if construction else 'run_'+other)
            assert page.evaluate(check)>100
            assert not errors
            browser.close()
    finally:server.shutdown();thread.join(timeout=5)

@pytest.mark.parametrize('algorithm', ALGORITHMS)
def test_missing_start_or_empty_graph_keeps_only_real_c_steps(algorithm):
    op='run_'+algorithm
    scope=graph_algorithm_code_scopes()[op]
    data=S.execute_operation('graph',op,{'start':99,'end':100},HISTORY[:1])
    trace=data['execution_trace']
    for step in trace['steps']:
        line=step['line_index']
        if line is not None:
            assert any(a<=line<=b for a,b in scope['ranges'])
            assert canonical_source().splitlines()[line]==step['line_text']
