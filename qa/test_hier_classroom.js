const fs=require('node:fs'),vm=require('node:vm'),assert=require('node:assert/strict');
const context=vm.createContext({window:{},document:{addEventListener(){}}});vm.runInContext(fs.readFileSync('static/js/hierarchical.js','utf8'),context);
const steps=JSON.parse(fs.readFileSync('qa/hier_classroom_fixtures.json','utf8'));
for(const step of steps){const state=step.state_snapshot,before=JSON.stringify(state),container={innerHTML:''};context.renderHierState('abb',state,container,null,null,null,null,null,null);const html=container.innerHTML;
 assert.equal(JSON.stringify(state),before);assert.match(html,/hier-memory-call-detail/);
 for(const node of state.heap_nodes || [])assert.ok(html.includes(`data-abb-node="${node.id}"`));
 for(const frame of state.tree_frames || [])assert.ok(html.includes(`data-abb-frame="${frame.id}"`));
 if(state.heap_nodes?.length)assert.ok(html.indexOf('data-abb-node=')<html.indexOf('<details class="hier-memory-call-detail"'));
}
const css=fs.readFileSync('static/css/contextual_help.css','utf8');assert.match(css,/hier-classroom-controls \{ position: sticky; top: 0/);assert.match(css,/hier-learning-shell \.hier-primary-workspace \{ height: clamp\(420px, 62vh, 570px\)/);assert.match(css,/hier-learning-shell #op-pseudocode \.code-line \{ width: auto/);
console.log('PASS 11 real ABB insertion frames preserve reserves, aliases and scope details, with reserves preceding optional call stack; CSS stable/wrap/sticky contracts');
const deletion=JSON.parse(fs.readFileSync('qa/hier_delete_classroom_fixtures.json','utf8'));
for(const step of deletion){const state=step.state_snapshot,before=JSON.stringify(state),container={innerHTML:''};context.renderHierState('abb',state,container,null,null,null,null,null,null);const html=container.innerHTML;
 assert.equal(JSON.stringify(state),before);
 for(const node of state.heap_nodes || [])assert.ok(html.includes(`data-abb-node="${node.id}"`));
 for(const node of state.freed_nodes || [])assert.ok(html.includes(`data-abb-retired-node="${node.id}"`));
 assert.match(html,/<details class="hier-retired-memory"><summary>Reservas terminadas:/);
 const liveIds=new Set((state.heap_nodes||[]).map(n=>n.id));const focus=[...(state.tree_frames||[])].reverse().flatMap(f=>Object.values({...f.parameters,...f.locals})).find(v=>liveIds.has(v));
 if(focus)assert.match(html,new RegExp(`is-current-memory[^>]*data-abb-node="${focus}"`));
}
console.log(`PASS ${deletion.length} real five-node deletion frames: every live/retired node preserved; nearest live frame alias prioritized without state reordering`);
// Final active stack must stay distinct from historical completed frames.
const panels={};context.document.getElementById=id=>panels[id] ||= {innerHTML:'',textContent:'',setAttribute(){}};
context.renderHierPedagogy(steps.at(-1).pedagogy,'intermediate');
assert.match(panels['hier-stack-view'].innerHTML,/Sin llamadas activas/);assert.match(panels['hier-stack-view'].innerHTML,/<details><summary>Marcos terminados/);assert.doesNotMatch(panels['hier-stack-view'].innerHTML,/pendiente|asignar la raiz solo/);
assert.match(panels['hier-invariant-view'].innerHTML,/<details><summary>Registro técnico/);assert.match(panels['hier-memory-view'].innerHTML,/sin cambios de memoria/);
console.log('PASS final live stack empty, completed frames explicitly historical without pending continuation, raw proof optional');
const five=deletion[0].state_snapshot,box={innerHTML:''};context.renderHierState('abb',five,box,null,null,null,null,null,null);
const viewBox=box.innerHTML.match(/viewBox="([^"]+)"/)[1].split(/\s+/).map(Number);assert.ok(viewBox[2]>0 && viewBox[3]>0);assert.ok(box.innerHTML.includes('hier-traversal-summary'));
assert.match(box.innerHTML,/<details class="viz-traversals hier-traversal-summary"><summary>Recorridos/);
console.log('PASS classroom viewBox uses real diagram bounds; traversal lists remain optional rather than squeezing SVG');
const rnState=JSON.parse(fs.readFileSync('qa/rn_classroom_fixture.json','utf8')),rnContainer={innerHTML:''};context.renderHierState('red_black',rnState,rnContainer,null,null,null,null,null,null);
assert.match(rnContainer.innerHTML,/<details class="hier-diagram-note"><summary>Reservas y enlaces observados; no certifica RN/);
for(const node of rnState.heap_nodes){assert.ok(rnContainer.innerHTML.includes(`data-rbt-svg-node="${node.id}"`));assert.ok(rnContainer.innerHTML.includes(`data-rbt-svg-color="${node.color}"`));}
assert.match(rnContainer.innerHTML,/color:(negro|rojo)/);assert.doesNotMatch(rnContainer.innerHTML,/color:BLACK|color:RED/);
console.log('PASS real RN state keeps every node/color enum and full caution, with compact visible warning and Spanish color labels');
const code={dataset:{rawCode:'static void intercambiar(int *a, int *b);\nstatic void intercambiar(int *a, int *b) {\n}\nstatic void heapify_up(int *a) {\n  intercambiar(a, a);\n}\nABBNodo* abb_insertar(ABBNodo* nodo, int valor) {\n  return nodo;\n}'},classList:{toggle(){}},querySelectorAll(){return [];}};
panels['op-pseudocode']=code;panels['hier-function-list']={innerHTML:'',querySelectorAll(){return [];}};
vm.runInContext(fs.readFileSync('static/js/c_code_navigation.js','utf8'),context);context.enhanceHierCodeNavigation(4);
const indexHtml=panels['hier-function-list'].innerHTML;assert.doesNotMatch(indexHtml,/>ercambiar</);assert.equal((indexHtml.match(/>intercambiar<\/button>/g)||[]).length,1);assert.match(indexHtml,/>heapify_up<\/button>/);assert.match(indexHtml,/>abb_insertar<\/button>/);
console.log('PASS hierarchical index respects complete return types, excludes call/prototype duplicates, retains pointer-return signatures');
// Layout changes coordinates only; live graph identity and C links are untouched.
const rnBefore=JSON.stringify(rnState),layout=context.layoutHierMemoryGraph(rnState);assert.equal(layout.safe,true);assert.equal(JSON.stringify(rnState),rnBefore);
for(const node of layout.graph){for(const child of [node.leftKey,node.rightKey]){const target=layout.graph.find(n=>n.id===child);if(target)assert.ok(target.y>node.y);}}
const leaf=(id,left='NULL',right='NULL')=>({id,value:Number(id.slice(1)),left,right,color:'BLACK'});
for(const sample of [{head:'N1',heap_nodes:[leaf('N1','N1')]},{head:'N1',heap_nodes:[leaf('N1','N2','N2'),leaf('N2')]},{head:'N1',heap_nodes:[leaf('N1',null)]},{head:'N1',heap_nodes:[leaf('N1','FREED')]}]){const before=JSON.stringify(sample),result=context.layoutHierMemoryGraph(sample);assert.equal(result.safe,false);assert.equal(result.graph.length,sample.heap_nodes.length);assert.equal(JSON.stringify(sample),before);assert.match(result.label,/Diagrama de memoria/);}
const detached=context.layoutHierMemoryGraph({head:'N1',heap_nodes:[leaf('N3'),leaf('N1'),leaf('N2','N3')]});assert.equal(detached.safe,true);assert.deepEqual(Array.from(detached.detached).sort(),['N2','N3']);assert.ok(detached.graph.find(n=>n.id==='N2').y>detached.graph.find(n=>n.id==='N1').y);
console.log('PASS ID-based final tree layout, detached forest, and honest cycle/shared/uninitialized/retired-reference fallbacks preserve all raw edges');
const heapSteps=JSON.parse(fs.readFileSync('qa/heap_classroom_fixtures.json','utf8'));
for(const step of heapSteps){const state=step.state_snapshot,container={innerHTML:''},before=JSON.stringify(state);context.renderHierState('binary_heap',state,container,null,null,null,null,null,null);const html=container.innerHTML;
 assert.equal(JSON.stringify(state),before);assert.match(html,/heap-classroom-canvas/);assert.match(html,/<svg/);assert.match(html,/<\/div><section class="abb-instruction-memory" data-heap-query-memory/);
 for(const cell of state.destination?.cells||[])assert.ok(html.includes(`data-heap-destination-index="${cell.index}"`));
 assert.match(html,/<details class="hier-memory-call-detail"/);
}
console.log(`PASS ${heapSteps.length} real heap copy frames: SVG retained, memory outside canvas, destination cells retained before optional frames`);
const predictions=JSON.parse(fs.readFileSync('qa/hier_prediction_fixtures.json','utf8'));let graphs=0;
for(const entry of predictions.filter(x=>['avl','red_black'].includes(x.structure)))for(const step of entry.trace.steps){const state=step.pedagogy.memory_state;if(!state?.heap_nodes)continue;const before=JSON.stringify(state),layout=context.layoutHierMemoryGraph(state);assert.equal(layout.graph.length,state.heap_nodes.length);for(const node of state.heap_nodes){const draw=layout.graph.find(n=>n.id===node.id);assert.equal(draw.leftKey,node.left);assert.equal(draw.rightKey,node.right);assert.equal(draw.color,node.color);}assert.equal(JSON.stringify(state),before);graphs++;}
console.log(`PASS ${graphs} real AVL/RN graph snapshots preserve all identities and observed edges during transient layout`);
