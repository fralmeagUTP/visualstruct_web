const fs=require('node:fs'),vm=require('node:vm'),assert=require('node:assert/strict');
const context=vm.createContext({window:{},document:{addEventListener(){}}});vm.runInContext(fs.readFileSync('static/js/sorting.js','utf8'),context);
const frames=JSON.parse(fs.readFileSync('qa/radix_compact_memory_fixtures.json','utf8'));
const rows=Object.fromEntries(frames.map(({display_step,frame})=>[display_step,Array.from(context.sCompactMemoryRows(frame)).join('\n')]));
for(const step of [9,10,50])assert.match(rows[step],/reservado, capacidad 4/,`step ${step}`);
assert.match(rows[135],/salida.*liberado; no acceder/);
assert.match(rows[158],/negativos.*liberado; no acceder/);assert.match(rows[158],/positivos.*reservado/);
assert.match(rows[159],/negativos.*liberado; no acceder/);assert.match(rows[159],/positivos.*liberado; no acceder/);
assert.equal(context.sMemoryValue({alias:'caller'}),'alias de arreglo original (prestado)');
assert.match(context.sMemoryValue({alias:'positive',cells:[1,2]}),/alias de bloque positivos/);
assert.match(context.sMemoryValue({alias:'negative',status:'undeclared',capacity:4}),/no reservado/);
assert.equal(context.sMemoryValue(null,{type:'uint32_t *',initialized:false}),'sin inicializar');
assert.equal(context.sMemoryValue(null,{type:'uint32_t *',initialized:true}),'NULL (sin bloque asociado)');
assert.match(context.sMemoryValue([0,0,2,3,4,4,4,4,4,4]),/^10 celdas \[0, 0, 2, 3, 4, 4, …\]$/);
const controls=JSON.parse(fs.readFileSync('qa/sorting_memory_control_fixtures.json','utf8'));let count=0;
for(const algorithm of controls){for(const frame of algorithm.frames){const output=context.sCompactMemoryRows(frame);assert.ok(output.length<=6);for(const row of output){assert.doesNotMatch(row,/\[object Object\]|\{"alias"|"cells":/,`${algorithm.algorithm} ${frame.source.line_token}`);}count++;}}
assert.equal(controls.length,11);assert.equal(count,1065);
console.log(`PASS real Radix allocate/free/alias fixtures and ${count} real frames across all 11 algorithms`);
for(const [step,text] of Object.entries(rows))console.log('STEP',step,text.replaceAll('\n',' | '));
// Execute the actual full-detail renderer with its UI dependencies represented by inert nodes.
const source=fs.readFileSync('static/js/sorting.js','utf8');const start=source.indexOf('  function renderPedagogy(frame) {'),end=source.indexOf('  function renderCountingOutcome()',start);
Object.assign(context,{currentPedagogy:null,renderLiveMemory(){},currentLearningLevel:()=> 'intermediate',pedagogyPhase:null,pedagogyObjective:null,pedagogyNarration:null,conditionView:null,variableTable:{innerHTML:''},callStack:null,loopView:null,pointerView:{innerHTML:''},invariantText:null});
vm.runInContext(source.slice(start,end),context);
for(const {display_step,frame} of frames){context.renderPedagogy(frame);assert.doesNotMatch(context.variableTable.innerHTML+context.pointerView.innerHTML,/\[object Object\]/,`full detail step ${display_step}`);assert.match(context.variableTable.innerHTML,/reservado|liberado/);}
console.log('PASS actual full Comprender variable/pointer renderer on six real Radix fixtures');
// A target alias does not imply a dereferenced value was recorded.
context.renderPedagogy(frames[0].frame);
assert.match(context.pointerView.innerHTML,/arreglo original \(prestado\)/);
assert.doesNotMatch(context.pointerView.innerHTML,/ = sin valor/);
context.renderPedagogy({variables:[],pointers:[{name:'p',target:'a[0]',value:0}]});
assert.match(context.pointerView.innerHTML,/ = 0/);
const strategy={innerHTML:''};
for(const [status,label] of Object.entries({undeclared:'aún no declarado',uninitialized:'sin inicializar',live:'reservado',freed:'liberado; no acceder',failed:'reserva fallida'})){
 context.renderSortingStrategy({algorithm:'radixsort',radix_context:{buffers:{negative:{capacity:4,status,live:status==='live',cells:[null,1,2,3]},positive:{capacity:4,status,live:false}}}},strategy);
 assert.match(strategy.innerHTML,new RegExp(label));
 assert.match(strategy.innerHTML,/negativos: uint32_t\[4\]/);assert.match(strategy.innerHTML,/positivos: uint32_t\[4\]/);
 assert.doesNotMatch(strategy.innerHTML,/>negative:|>positive:|— live|— undeclared/);
}
console.log('PASS pointer alias without invented dereference; Spanish Radix buffer labels and lifetimes');
