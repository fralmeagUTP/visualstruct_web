"""Actual browser transport and caller checks for graph-book/v1.

The native program proves status/result/ownership. Browser checks prove the
model's source/event/memory transport and actual rendered UI, not a claim of
native per-statement instrumentation.
"""
from pathlib import Path
import hashlib,json,re,shutil,subprocess,threading
from contextlib import contextmanager
from app import create_app
from app.config import Config
from werkzeug.serving import make_server
from _graph_trace_contract import decode_graph_http_trace
from _book_frame_oracle import assert_book_body
from _traversal_caller_contract import TRACK

COLLECT=r'''async(count)=>{
 const p=window.auditGraphPlayer,rows=[];
 function record(index,direction){rows.push({index,direction,
 heap:[...document.querySelectorAll('[data-graph-memory-node]')].map(n=>({id:n.dataset.graphMemoryNode,kind:n.dataset.graphMemoryKind,contents:n.querySelector('code').textContent})),
 cards:[...document.querySelectorAll('.graph-live-cards')].map(panel=>[...panel.querySelectorAll('[data-graph-live-node]')].map(n=>n.dataset.graphLiveNode)),
 stack:[...document.querySelectorAll('[data-graph-frame]')].map(n=>({id:n.dataset.graphFrame,text:n.textContent})),
 variables:[...document.querySelectorAll('[data-graph-variable]')].map(n=>({name:n.dataset.graphVariable,scope:n.dataset.graphScope,text:n.textContent})),
 heads:document.querySelector('[data-graph-heads]')?.textContent,retired:document.querySelector('[data-graph-retired]')?.textContent,
 condition:document.querySelector('#graph-condition-view').textContent,
 stdout:document.querySelector('#graph-printf-console').textContent,message:document.querySelector('#graph-message-box').textContent,
 auxiliary:document.querySelector('#graph-auxiliary-view code')?.textContent,
 highlighted:[...document.querySelectorAll('#op-pseudocode .code-line.sim-active')].map(n=>Number(n.dataset.line)),
 svgNodes:document.querySelectorAll('#graph-visual-state circle.viz-graph-node').length});}
 p.reset();record(-1,'initial');
 for(let i=0;i<count;i++){await p.step();record(i,'forward');}
 for(let i=count-2;i>=-1;i--){p.prev();record(i,'back');}
 p.seek(count-1);record(count-1,'seek');return rows;
}'''

@contextmanager
def private_server(tmp_path):
    class Private(Config):
        TESTING=True;APP_ENV='testing';SECRET_KEY='bounded-browser-contract'
        SESSION_CACHE_DIR=str(tmp_path/'sessions');SESSION_COOKIE_NAME='canonical_browser_contract'
    app=create_app(Private);server=make_server('127.0.0.1',0,app,threaded=True)
    thread=threading.Thread(target=server.serve_forever,daemon=True);thread.start()
    try:yield f'http://127.0.0.1:{server.server_port}'
    finally:server.shutdown();thread.join(timeout=5);assert not thread.is_alive()

def install_player_capture(page):
    page.add_init_script("document.addEventListener('DOMContentLoaded',()=>{const old=window.InterpreterRuntime.createTracePlayer;window.InterpreterRuntime.createTracePlayer=function(options){const player=old(options);window.auditGraphPlayer=player;return player;};});")

def seed(context,base,vertices,arcs,directed=True):
    operations=[('create_graph',{'directed':directed})]
    operations += [('insert_vertex',{'vertex':v}) for v in vertices]
    operations += [('insert_edge',{'origin':a,'target':b,'weight':w}) for a,b,w in arcs]
    for operation,payload in operations:
        response=context.request.post(base+'/graph/graph/operate',data={'operation':operation,'payload':payload,'execution_mode':'normal'})
        body=response.json();assert response.status==200 and body['success'],body

def operate_ui(page,operation,payload):
    page.select_option('#graph-algorithm-select',operation)
    for key,value in payload.items():page.locator('#g-alg-field-'+key).fill(str(value))
    page.evaluate("()=>{const b=document.querySelector('#graph-step-toggle');b.checked=true;b.dispatchEvent(new Event('change'));}")
    with page.expect_response(lambda r:r.url.endswith('/graph/graph/operate') and r.request.method=='POST') as pending:
        page.click('#graph-sim-play')
    body=pending.value.json();assert body['source_contract']=='graph-book/v1'
    trace=decode_graph_http_trace(body['execution_trace']);body['execution_trace']=trace
    page.wait_for_function('(n)=>window.auditGraphPlayer.getTotalSteps()===n',arg=len(trace['steps']))
    page.evaluate('()=>window.auditGraphPlayer.pause()')
    return body,pending.value.status

def verify_player(page,body,posts,*,collector=COLLECT):
    trace=body['execution_trace'];assert trace['book_instruction_model'];assert_book_body(body)
    steps=trace['steps'];before=len(posts);rows=page.evaluate(collector,len(steps))
    compact=lambda value:json.dumps(value,ensure_ascii=False,separators=(',',':'))
    assert len(rows)==2*len(steps)+2
    for row in rows:
        index=row['index'];ped=steps[index]['pedagogy'] if index>=0 else steps[0]['pedagogy']['initial_frame']
        memory=ped.get('memory_display',ped['memory_state'])
        assert row['heap']==[{'id':n['id'],'kind':n['kind'],'contents':compact(n.get('fields',n.get('items')))} for n in memory['heap_nodes']],(index,row['direction'])
        if 'cards' in row:
            assert row['cards'],(index,row['direction'])
            for panel in row['cards']:
                assert sorted(panel)==sorted(n['id'] for n in memory['heap_nodes']),(index,row['direction'],panel,memory['heap_nodes'])
        assert row['heads']=='Grafo prestado: '+compact(memory['graph'])
        assert row['retired']=='Retiradas (sólo registro histórico): '+compact(memory['retired_objects'])
        assert row['stack']==[{'id':f['frame_id'],'text':f['function']+': '+f['scope_status']} for f in ped['call_stack']]
        assert len(row['variables'])==len(ped['variables'])
        for got,variable in zip(row['variables'],ped['variables']):
            assert got['scope']==variable['scope'] and got['name']==variable['name']
            assert compact(variable['previous']) in got['text'] and compact(variable['value']) in got['text']
        live={f['frame_id'] for f in ped['call_stack']}
        assert live.isdisjoint(f['frame_id'] for f in ped.get('completed_call_stack',[]))
        if 'auxiliary' in row:assert row['auxiliary']==compact(ped['auxiliary']['items']),(index,row['direction'],row['auxiliary'],ped['auxiliary'])
        if ped['condition']:
            assert ped['condition']['substituted'] in row['condition']
            assert str(ped['condition']['result']).lower() in row['condition']
        stdout='\n'.join(line for step in steps[:index+1] for line in step['console']) if index>=0 else ''
        assert row['stdout']==(stdout or '(sin salida printf en esta ruta)')
        assert row['message']==(body['message'] if index==len(steps)-1 else 'Operación preparada: resultado pendiente hasta completar las llamadas C.')
        expected=steps[index]['state_after'] if index>=0 else steps[0]['state_snapshot']
        assert row['svgNodes']==len(expected['nodes'])
        if index>=0 and ped['instruction_event']['C_executed']:assert steps[index]['line_index'] in row['highlighted']
        else:assert row['highlighted']==[]
    assert len(posts)==before
    assert trace['steps'][-1]['pedagogy']['memory_state']['frames']==[]
    return {'steps':len(steps),'DOM_boundaries_verified':len(rows),'replay_POSTs':0,'source_sha256':trace['source_sha256']}

def current_main(page,context,base):
    response=context.request.get(base+'/help/source/graph/main');assert response.status==200
    text=response.body().decode('utf-8');assert response.headers['cache-control']=='private, no-store'
    page.wait_for_function('(main)=>document.querySelector("#action-history").dataset.rawCode===main',arg=text)
    assert page.locator('#action-history').get_attribute('data-raw-code')==text
    return text

def reload_main_twice(page,context,base,posts):
    before=len(posts);programs=[]
    for _ in range(2):
        page.reload(wait_until='networkidle');programs.append(current_main(page,context,base))
    assert programs[0]==programs[1] and len(posts)==before
    page.get_by_role('tab',name='main.c del historial',exact=True).click()
    with page.expect_download() as pending:
        page.locator('a[href="/help/source/graph/main"]').click()
    assert Path(pending.value.path()).read_bytes()==programs[0].encode('utf-8')
    assert len(posts)==before
    return programs[0]

def compile_downloaded_main(context,base,text,out,*,optimize=False):
    out=Path(out);out.mkdir(parents=True,exist_ok=True)
    from app.domain.graph.book_source import HASHES
    for kind,ext in [('source','c'),('header','h')]:
        response=context.request.get(base+'/help/source/graph/'+kind);assert response.status==200
        raw=response.body();assert hashlib.sha256(raw).hexdigest()==HASHES['tad_grafo.'+ext]
        (out/('tad_grafo.'+ext)).write_bytes(raw)
    (out/'main.c').write_text(text,encoding='utf-8');(out/'track.c').write_text(TRACK,encoding='utf-8')
    compiler=shutil.which('gcc');assert compiler
    common=[compiler,'-std=c17','-Wall','-Wextra','-Wpedantic','-Werror','-I',str(out)]
    if optimize:common.append('-O2')
    original=out/'main.exe';obj=out/'owned-graph.o';observed=out/'owned.exe'
    commands=[common+[str(out/'main.c'),str(out/'tad_grafo.c'),'-o',str(original)],
              common+['-Dmalloc=owned_malloc','-Dcalloc=owned_calloc','-Dfree=owned_free','-c',str(out/'tad_grafo.c'),'-o',str(obj)],
              common+[str(out/'main.c'),str(out/'track.c'),str(obj),'-o',str(observed)]]
    for command in commands:
        built=subprocess.run(command,capture_output=True,text=True,timeout=45);assert built.returncode==0,built.stderr
    run=subprocess.run([str(original)],capture_output=True,text=True,timeout=15);assert run.returncode==0,run.stderr
    instrumented=subprocess.run([str(observed)],capture_output=True,text=True,timeout=15);assert instrumented.returncode==0,instrumented.stderr
    match=re.search(r'OWNERSHIP (\d+) (\d+) 0',instrumented.stdout);assert match and match[1]==match[2]
    assert instrumented.stdout.split('OWNERSHIP ')[0]==run.stdout
    return {'stdout':run.stdout,'allocations':int(match[1]),'frees':int(match[2]),'live':0,'strict_c17':True}

def traversal_browser_case(tmp_path,algorithm,case,native,*,all_frames=True):
    from playwright.sync_api import sync_playwright
    from _audit_graph_bfs_native_observer import CASES
    record=CASES[case];operation='run_'+algorithm;title=algorithm.upper()
    with private_server(tmp_path) as base,sync_playwright() as pw:
        browser=pw.chromium.launch();context=browser.new_context(viewport={'width':1366,'height':1000});page=context.new_page()
        errors=[];posts=[];page.on('pageerror',lambda error:errors.append(str(error)))
        page.on('request',lambda request:posts.append(request.url) if request.method=='POST' else None)
        seed(context,base,record['vertices'],[(a,b,1) for a,b in record['edges']])
        install_player_capture(page);page.goto(base+'/graph/graph/recorridos',wait_until='networkidle')
        body,status=operate_ui(page,operation,{'start':record['start']})
        assert status==200 and body['success'] and body['c_status']==native['status']==0
        assert body['result']==native['order']
        assert {int(n['id']):n['marked'] for n in body['visual_state']['nodes']}==dict(native['marks'])
        if all_frames:report=verify_player(page,body,posts)
        else:
            assert_book_body(body);before=len(posts)
            page.evaluate('()=>{const p=window.auditGraphPlayer;p.reset();p.seek(p.getTotalSteps()-1);p.prev();p.seek(p.getTotalSteps()-1);}')
            assert len(posts)==before;report={'replay_POSTs':0,'steps':len(body['execution_trace']['steps'])}
        second=context.request.post(base+'/graph/graph/operate',data={'operation':operation,'payload':{'start':record['start']},'execution_mode':'normal'}).json()
        assert second['success'] and second['result']==body['result']
        failed=context.request.post(base+'/graph/graph/operate',data={'operation':operation,'payload':{'start':999},'execution_mode':'normal'}).json()
        assert not failed['success'] and failed['c_status']==2
        assert failed['history'][:-1]==second['history'] and failed['history'][-1]['source_contract']=='graph-book/v1'
        program=reload_main_twice(page,context,base,posts)
        assert program.count('= grafo_'+algorithm+'(')==3
        assert program.count('grafo_liberar_vertices(&lista_')==3
        native_program=compile_downloaded_main(context,base,program,tmp_path/'download')
        expected=title+': estado=0'+''.join(' '+str(v) for v in body['result'])
        assert native_program['stdout'].splitlines().count(expected)==2
        assert native_program['stdout'].splitlines().count(title+': estado=2')==1
        if all_frames and case==1:
            rejected,rejected_status=operate_ui(page,operation,{'start':999})
            assert rejected_status==400 and rejected['c_status']==2 and rejected['execution_started']
            assert rejected['history'][:-1]==failed['history']
            verify_player(page,rejected,posts)
            error_program=reload_main_twice(page,context,base,posts)
            assert error_program.count('= grafo_'+algorithm+'(')==4
        assert not errors
        report.update(case=case,algorithm=algorithm,source_contract='graph-book/v1',successful_calls=2,
                      failed_C_call_retained=True,native_order_marks_and_cleanup=True,downloaded_main=native_program,page_errors=errors)
        (tmp_path/'browser-report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
        context.close();browser.close()
