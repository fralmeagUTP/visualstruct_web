"""API frames through real JS renderers. This does not certify Chromium E2E."""
import json
import subprocess
from pathlib import Path
from app import create_app
from app.config import Config
from e2e_sorting_stack_contract import assert_sorting_stack

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = r'''
const fs=require('fs'),vm=require('vm'),{JSDOM}=require('./qa/node_modules/jsdom');
const input=JSON.parse(fs.readFileSync(process.argv[1],'utf8'));
const dom=new JSDOM('<div id="hier-pedagogy-summary"></div><div id="hier-memory-view"></div><div id="seq-pedagogy-summary"></div><div id="sorting-pedagogy-narration"></div><div id="strategy"></div><ul id="sorting-call-stack"></ul>',{runScripts:'outside-only'});
try {
 const w=dom.window,ctx=dom.getInternalVMContext();w.structuredClone=structuredClone;
 for(const f of ['contextual_help','hierarchical','sequential','sorting'])vm.runInContext(fs.readFileSync('static/js/'+f+'.js','utf8'),ctx);
 const rows=[];
 for(const entry of input){
  const trace=entry.trace;
  for(const direction of ['forward','backward']){
   const indices=direction==='forward'?Array.from({length:trace.steps.length+1},(_,i)=>i-1):Array.from({length:trace.steps.length},(_,i)=>trace.steps.length-2-i);
   for(const index of indices){
    const step=trace.steps[Math.max(index,0)];let ped=step.pedagogy;
    if(entry.family==='abb') {if(index<0)ped=ped.initial_frame;w.renderHierPedagogy(ped,'intermediate');}
    else if(entry.family==='red_black'){if(index<0)ped=ped.initial_frame;w.renderHierPedagogy(ped,'intermediate');}
    else if(entry.family==='sublist'){
     if(index<0){
      // Execute the production initial-frame expression, not a copied fixture.
      const source=fs.readFileSync('static/js/sequential.js','utf8');
      const start=source.indexOf('currentPedagogyFrame = initialSublist ? {');
      const end=source.indexOf('} : step.pedagogy;',start);
      const expression=source.slice(start,end+1).split('initialSublist ? ')[1];
      w.step=step;ped=vm.runInContext('('+expression+')',ctx);
     }
     w.renderSequentialPedagogyFrame(ped,'intermediate');
    }else{
     w.renderSortingStrategy(index<0?step.state_snapshot:step.state_after,w.document.getElementById('strategy'));
     if(index>=0){w.document.getElementById('sorting-pedagogy-narration').textContent='';w.document.getElementById('sorting-pedagogy-narration').textContent=w.sStudentNarration(ped);}
    }
    let stackRows=[];
    if(entry.family==='sorting'){
     const source=fs.readFileSync('static/js/sorting.js','utf8');
     const start=source.indexOf('    const stack = Array.isArray(currentPedagogy.call_stack)'),end=source.indexOf('    const loop = currentPedagogy.loop;',start);
     if(start<0||end<start)throw Error('Production stack renderer missing');
     w.currentPedagogy=index<0?{call_stack:[]}:ped;w.callStack=w.document.getElementById('sorting-call-stack');
     vm.runInContext('{'+source.slice(start,end)+'}',ctx);
     stackRows=[...w.callStack.querySelectorAll(':scope > li')].map(row=>({function:row.querySelector('strong')?.textContent??null,text:row.textContent}));
    }
    const prefix=entry.family==='sublist'?'seq':entry.family==='sorting'?'sorting':'hier';
    let wrongSummary=null;
    if(entry.family==='sorting' && entry.op==='burbuja' && index===trace.steps.length-1){
     const correct=w.document.getElementById('sorting-pedagogy-narration').innerHTML;
     w.document.getElementById('sorting-pedagogy-narration').textContent=w.sStudentNarration(trace.steps[index-1].pedagogy);
     wrongSummary=w.document.getElementById('sorting-pedagogy-narration').textContent;
     w.document.getElementById('sorting-pedagogy-narration').innerHTML=correct;
    }
    rows.push({stackRows,wrongSummary,family:entry.family,op:entry.op,index,direction,summary:w.document.getElementById(prefix==='sorting'?'sorting-pedagogy-narration':prefix+'-pedagogy-summary').textContent,memory:w.document.getElementById('hier-memory-view').textContent,strategy:w.document.getElementById('strategy').textContent});
   }
  }
 }
 process.stdout.write(JSON.stringify(rows));
}finally{dom.window.close();}
'''


def test_initial_free_and_sorting_labels_follow_real_renderers(tmp_path):
    class Local(Config):
        TESTING = True
        SESSION_CACHE_DIR = str(tmp_path / 'sessions')
    entries = []
    app = create_app(Local)
    for family, route, operations in [
        ('abb','hierarchical',[('insertar',{'value':7})]),
        ('red_black','hierarchical',[('insertar',{'value':7}),('insertar',{'value':3}),('limpiar',{})]),
        ('sublist','sequential',[('insertar_padre',{'parent':7}),('insertar_hijo',{'parent':7,'child':3}),('hijos_de',{'parent':7}),('eliminar_padre',{'parent':7}),('limpiar',{})]),
    ]:
        with app.test_client() as client:
            for op, payload in operations:
                data = client.post(f'/{route}/{family}/operate',json={'operation':op,'payload':payload}).get_json()
                assert data['success']
                if family != 'red_black' or op == 'limpiar':
                    entries.append(dict(family=family,op=op,trace=data['execution_trace']))
    for algorithm in ['seleccion','insercion','burbuja','shell','quicksort','mergesort','heapsort','counting_sort','binsort','radixsort']:
        with app.test_client() as client:
            assert client.post('/api/ordenamiento/create-array',json={'values':[5,-3,0,2,1]}).status_code == 200
            data=client.post('/api/ordenamiento/run',json={'algorithm_id':algorithm,'mode':'step_by_step'}).get_json()
            assert data['success'] and data['visual_state']['items']==[-3,0,1,2,5]
            entries.append(dict(family='sorting',op=algorithm,trace=data['execution_trace']))
    path=tmp_path/'traces.json';path.write_text(json.dumps(entries))
    run=subprocess.run(['node','-e',SCRIPT,str(path)],cwd=ROOT,capture_output=True,text=True,timeout=60)
    assert run.returncode == 0,run.stderr
    rows=json.loads(run.stdout);lookup={(e['family'],e['op']):e['trace'] for e in entries}
    assert len(rows)==sum(2*len(e['trace']['steps'])+1 for e in entries)
    markers={'seleccion':'Mínimo provisional','insercion':'Clave:','burbuja':'Pasada:','shell':'Intervalo:','quicksort':'Pivote local:','mergesort':'División/fusión activa','heapsort':'hijos:','counting_sort':'Frecuencias','binsort':'Frecuencias','radixsort':'Magnitudes uint32_t'}
    for algorithm, marker in markers.items():
        trace=lookup['sorting',algorithm]
        assert any(marker in row['strategy'] and row['index']>=0 and trace['steps'][row['index']]['pedagogy']['call_stack'] for row in rows if row['family']=='sorting' and row['op']==algorithm)
        assert trace['steps'][-1]['pedagogy']['call_stack']==[]
    for row in rows:
        trace=lookup[row['family'],row['op']];index=row['index']
        if row['family']=='abb' and index<0:
            assert 'Ninguna instrucción ejecutada; raíz y reservas iniciales, sin ámbitos futuros.' in row['summary']
            assert 'Ninguna instruccion ejecutada' not in row['summary']
        if row['family']=='sublist' and index<0:
            assert 'Paso actual: Antes de comenzar' in row['summary']
            assert 'ninguna instrucción ejecutada' not in row['summary'].lower()
        if row['family']=='red_black' and index>=0:
            ped=trace['steps'][index]['pedagogy']
            if ped['instruction_event']['phase']=='free':
                expected='Liberados (identidades históricas): '+', '.join(x['address'] for x in ped['memory']['freed_objects'])
                assert expected in row['memory']
                assert 'Liberados (identidades historicas)' not in row['memory']
        if row['family']=='sorting':
            calls=trace['steps'][index]['pedagogy']['call_stack'] if index>=0 else []
            assert assert_sorting_stack(row['stackRows'],calls)==bool(calls)
        if row['family']=='sorting' and row['op']=='mergesort':
            assert 'División/fusión activa' in row['strategy']
            assert 'Division/fusion activa' not in row['strategy']
        if row['family']=='sorting' and row['op']=='burbuja' and index==len(trace['steps'])-1:
            assert row['summary'].strip()=='Retorno void a la función que llamó; retirar locales, sin printf propio del TAD.'
            assert row['summary']!=row['wrongSummary']
            assert trace['steps'][index]['state_after']['trace_token']=='sort_return'
            assert trace['steps'][index]['pedagogy']['source']['function']=='ordenar_burbuja'
            assert trace['steps'][index]['pedagogy']['source']['line_text']=='}'
            assert 'j: —' in row['strategy'] and '¿Hubo intercambio? (hubo_intercambio): —' in row['strategy']
            assert 'Retorno void al caller' not in row['strategy']
            assert trace['steps'][index]['pedagogy']['call_stack']==[]
            assert trace['steps'][index]['pedagogy']['variables']==[]
