"""Exercise the actual JS renderer with live graph snapshots, forwards and backwards."""
import json
import subprocess
from app.services.graph_structure_service import GraphStructureService as S

JS = r'''
const fs=require('fs'),vm=require('vm'),assert=require('assert/strict');
const rows=JSON.parse(fs.readFileSync(0,'utf8')), el={innerHTML:''};
const ctx=vm.createContext({document:{addEventListener(){},getElementById(id){return id==='graph-traversal-view'?el:null;}},window:{}});
vm.runInContext(fs.readFileSync('static/js/graph.js','utf8'),ctx);
let count=0;
for(const row of rows){
 for(const indices of [row.frames.map((_,i)=>i),row.frames.map((_,i)=>i).reverse()]){
  for(const i of indices){
   const f=row.frames[i],st=f.memory_display||f.memory_state,cell=st.external?.result;
   ctx.renderGraphPedagogy(f,'intermediate');const html=el.innerHTML;
   assert.match(html,/Resultado recibido del TAD \(celda actual\)/);
   assert.match(html,/Último retorno de función/);
   assert.doesNotMatch(html,/Retorno al caller: null/);
   if(!cell)assert.match(html,/Pendiente de recepción del TAD/);
   else assert.ok(html.includes(ctx.gEscape(ctx.gTeachingValue(cell.value))),JSON.stringify({i,row:row.name}));
   if(st.returned===null)assert.match(html,/data-graph-last-return>void \(sin valor\)/);
   if(cell?.value?.value_status==='indeterminate_after_free')assert.match(html,/no utilizar/);
   count++;
  }
 }
 const final=row.frames.at(-1);const cell=(final.memory_display||final.memory_state).external.result;
 assert.equal(cell.value,row.finalCell);
}
const malicious={book_instruction_model:true,memory_state:{returned:null,external:{result:{type:'ListaVertice',value:'<script>alert(1)</script>'}}}};
assert.doesNotMatch(ctx.gGraphReturnMarkup(malicious),/<script>/);
// A safe display identity takes precedence over the raw pointer snapshot.
const safe={memory_state:{external:{result:{value:'V99'}},returned:'V99'},memory_display:{external:{result:{value:{historical_identity:'V99',usable:false,value_status:'indeterminate_after_free'}}},returned:null}};
assert.match(ctx.gGraphReturnMarkup(safe),/no utilizar/);
console.log(JSON.stringify({framesRendered:count,reverse:true,escape:true,retiredSafe:true}));
'''

def test_live_return_frames_and_reverse_navigation():
    history=[{'operation':'create_graph','payload':{'directed':True},'source_contract':'graph-book/v1'}, {'operation':'insert_edge','payload':{'origin':11,'target':12,'weight':-1},'source_contract':'graph-book/v1'}]
    rows=[]
    for name,op,payload,h,expected in [
        ('vertices','list_vertices',{},history,'V2'),
        ('edges','list_edges',{},history,'E1'),
        ('empty_vertices','list_vertices',{},history[:1],'NULL'),
        ('empty_edges','list_edges',{},history[:1],'NULL'),
        ('owned','run_bfs',{'start':11},history,'NULL'),
    ]:
        data=S.execute_operation('graph',op,payload,h)
        frames=[data['execution_trace']['steps'][0]['pedagogy']['initial_frame']]
        frames += [s['pedagogy'] for s in data['execution_trace']['steps']]
        rows.append(dict(name=name,frames=frames,finalCell=expected))
    result=subprocess.run(['node','-e',JS],input=json.dumps(rows),text=True,capture_output=True,timeout=60)
    assert result.returncode==0,result.stdout+result.stderr
    evidence=json.loads(result.stdout)
    assert evidence['framesRendered']>100 and evidence['reverse'] and evidence['retiredSafe']
