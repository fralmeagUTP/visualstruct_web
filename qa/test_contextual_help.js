const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');
const nodes = new Map();
for (const prefix of ['hier','seq','graph','hash','sorting']) {
 const id=prefix==='sorting'?'sorting-pedagogy-narration':`${prefix}-pedagogy-summary`;
 nodes.set(id,{innerHTML:''});
}
const panel={parentElement:{tagName:'SECTION',hidden:false}};nodes.set('hier-variables-view',panel);
const window={};vm.runInNewContext(fs.readFileSync('static/js/contextual_help.js','utf8'),{window,document:{getElementById:id=>nodes.get(id)}});
const help=window.ContextualHelp;
let checks=0;
function test(name,fn){fn();checks++;console.log('PASS',name);}
test('ABB insertion concise and operation-specific',()=>{
 help.operation('hier',{id:'abb',name:'ABB',operations:[{name:'insertar',label:'Insertar'}]},'insertar');
 const html=nodes.get('hier-pedagogy-summary').innerHTML;
 assert.equal((html.match(/<li>/g)||[]).length,3);assert.match(html,/izquierda/);assert.doesNotMatch(html,/eliminar|altura|recorrido/);assert.ok(html.length<650);assert.equal(panel.parentElement.hidden,true);
});
test('Changing operation replaces explanation, not appends',()=>{
 help.operation('hier',{id:'abb',operations:[{name:'altura',label:'Altura'}]},'altura');
 const html=nodes.get('hier-pedagogy-summary').innerHTML;assert.match(html,/Calcular la altura/);assert.doesNotMatch(html,/Ubicar el valor/);
});
test('Frame uses current changes and retains complete explanation',()=>{
 help.frame('hier',{phase:{label:'Asignar'},narration:{basic:'Se cambia la raíz. El enlace conserva el árbol. Detalle completo adicional.'},variables:[{name:'raiz',previous:1,value:2,changed:true}]},'basic');
 const html=nodes.get('hier-pedagogy-summary').innerHTML;assert.match(html,/raiz: 1 → 2/);assert.match(html,/<details/);assert.match(html,/Detalle completo adicional/);assert.equal(panel.parentElement.hidden,false);
});
test('Reset drops stale step and returns selected operation',()=>{
 help.frame('hier',null);const html=nodes.get('hier-pedagogy-summary').innerHTML;assert.match(html,/Calcular la altura/);assert.doesNotMatch(html,/raiz: 1/);assert.equal(panel.parentElement.hidden,true);
});
test('All five modules receive scoped notes',()=>{
 for(const [prefix,id,operation] of [['seq','stack','apilar'],['graph','graph','run_bfs'],['hash','hash_table','insert'],['sorting','sorting_array','burbuja']]){
  help.operation(prefix,{id,operations:[],algorithms:[{id:operation,label:'ALGORITMO'}]},operation);
  const target=nodes.get(prefix==='sorting'?'sorting-pedagogy-narration':`${prefix}-pedagogy-summary`);assert.match(target.innerHTML,/<ul/);assert.match(target.innerHTML,/ALGORITMO/);
  help.frame(prefix,{phase:{label:'Paso uno'},narration:{basic:'Primera acción. Su razón.'}},'basic');assert.match(target.innerHTML,/Primera acción/);
 }
});
test('Untrusted labels, variables and explanation escaped',()=>{
 help.frame('hash',{phase:{label:'<img src=x>'},narration:{basic:'<script>evil</script>'},variables:[{name:'<b>x</b>',value:'<svg>',changed:true}]},'basic');
 const html=nodes.get('hash-pedagogy-summary').innerHTML;assert.doesNotMatch(html,/<script|<img|<svg|<b>/);assert.match(html,/&lt;/);
});
test('Priority queue scans minimum priority and preserves FIFO ties',()=>{
 const model={id:'priority_queue',operations:[{name:'desencolar',label:'Desencolar'}]};
 help.operation('seq',model,'desencolar');let html=nodes.get('seq-pedagogy-summary').innerHTML;
 assert.match(html,/menor número de prioridad/);assert.match(html,/aunque esté en medio/);assert.match(html,/primero que llegó/);assert.match(html,/FIFO/);assert.doesNotMatch(html,/Retirar el frente/);
 help.operation('seq',model,'encolar');html=nodes.get('seq-pedagogy-summary').innerHTML;
 assert.match(html,/final en orden de llegada/);assert.match(html,/sin ordenar físicamente/);
 help.operation('seq',model,'frente');html=nodes.get('seq-pedagogy-summary').innerHTML;
 assert.match(html,/sin retirarlo/);assert.match(html,/menor número/);
});
test('Min-heap insertion and extraction use array and sift directions',()=>{
 help.operation('hier',{id:'binary_heap'},'insertar');let html=nodes.get('hier-pedagogy-summary').innerHTML;
 assert.match(html,/final del arreglo y subir/);assert.match(html,/menor o igual/);assert.doesNotMatch(html,/menores van a la izquierda/);
 help.operation('hier',{id:'binary_heap'},'extraer_raiz');html=nodes.get('hier-pedagogy-summary').innerHTML;
 assert.match(html,/último valor a la raíz y bajarlo/);
});
test('Every inventoried operation and algorithm has explicit help',()=>{
 const inventory=JSON.parse(fs.readFileSync('qa/inventory.json','utf8'));
 const prefixes={sequential:'seq',hierarchical:'hier',graph:'graph',hash:'hash',sorting:'sorting'};
 let operationCount=0,algorithmCount=0;
 for(const [module,structures] of Object.entries(inventory)){
  for(const [id,data] of Object.entries(structures)){
   for(const operation of [...data.operations,...(data.algorithms||[])]){
    const prefix=prefixes[module], name=operation.name||operation.id;
    help.operation(prefix,{id,...data},name);
    const html=nodes.get(prefix==='sorting'?'sorting-pedagogy-narration':`${prefix}-pedagogy-summary`).innerHTML;
    assert.doesNotMatch(html,/observar su resultado y los pasos necesarios/,`${id}.${name} uses vague fallback`);
    assert.equal((html.match(/<li>/g)||[]).length,3,`${id}.${name}`);
    if(operation.name)operationCount++;else algorithmCount++;
   }
  }
 }
 assert.equal(operationCount,109);assert.equal(algorithmCount,11);
});
console.log(`${checks} contextual help tests passed`);

for (const field of ['sgte','izquierdo','derecho','izq','der','padre']) {
 assert.equal(help.phaseLabel({concept:'link',phase:{label:'Link'},source:{line_text:`nodo->${field} = nuevo;`}}),'Actualizar un enlace');
}
assert.equal(help.phaseLabel({concept:'link',phase:{label:'Link'},source:{line_text:'nodo->valor = valor;'}}),'Actualizar un dato del nodo');
console.log('PASS scalar store distinguished from all canonical tree link field names');
