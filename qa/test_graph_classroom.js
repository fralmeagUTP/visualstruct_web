const fs=require('node:fs'),vm=require('node:vm'),assert=require('node:assert/strict');
const panels={};const ctx=vm.createContext({window:{},document:{addEventListener(){},getElementById(id){return panels[id] ||= {innerHTML:''};}}});
vm.runInContext(fs.readFileSync('static/js/graph.js','utf8'),ctx);
const fixtures=JSON.parse(fs.readFileSync('qa/graph_classroom_fixtures.json','utf8'));let count=0;
for(const c of fixtures)for(const step of c.steps){const f=step.pedagogy;if(!f)continue;const before=JSON.stringify(f);ctx.renderGraphPedagogy(f,'intermediate');const html=panels['graph-live-memory'].innerHTML;
 for(const n of f.memory_state?.heap_nodes || f.memory?.objects_after || [])assert.ok(html.includes(`data-graph-live-node="${n.id}"`),`${c.operation} ${n.id}`);
 assert.doesNotMatch(html,/\[object Object\]/);assert.equal(JSON.stringify(f),before);assert.match(panels['graph-representation-view'].innerHTML,/<details><summary>Representación y memoria técnica/);count++;
 const state=step.state_snapshot;if(state?.nodes?.length){const svg=ctx.renderGraphSvg(state,null,null),box=svg.match(/viewBox="([^"]+)"/)[1].split(' ').map(Number);assert.ok(box.every(Number.isFinite));assert.ok(box[2]>0&&box[3]>0);for(const n of state.nodes)assert.ok(svg.includes(String(n.label)));}
}
const css=fs.readFileSync('static/css/contextual_help.css','utf8');assert.match(css,/\.graph-prepare-grid\.graph-phase-hidden\s*\{ display: none !important/);assert.match(css,/\.graph-code-content \.code-line \{ white-space: pre-wrap/);
assert.equal(ctx.gTeachingValue({sig:'NULL',dato:'sin inicializar'}),'sig: NULL · dato: sin inicializar');
console.log(`PASS ${count} real graph frames: reservations preserved, raw diagnostics optional, readable fields, immutable, bounded SVG and phase/layout rules`);
assert.equal(JSON.stringify(ctx.gGraphNodeFields({id:'Q1',kind:'queue',value:3,next:'NULL'})),JSON.stringify({nro:3,sgte:'NULL'}));
assert.equal(JSON.stringify(ctx.gGraphNodeFields({id:'V1',kind:'vertex',value:3,next:'NULL',mark:0})),JSON.stringify({dato:3,sig:'NULL',marcado:0}));
assert.equal(JSON.stringify(ctx.gGraphNodeFields({id:'A1',kind:'arc',origin:1,target:2,next:'NULL'})),JSON.stringify({origen:1,destino:2,sig:'NULL'}));
console.log('PASS legacy BFS field aliases displayed as canonical C fields per actual node kind, no fabricated missing cost');
let active=0;
for(const c of fixtures)for(const step of c.steps){const f=step.pedagogy;if(!f)continue;const tokens=new Set(String(f.source?.line_text||f.instruction_event?.statement||'').match(/[A-Za-z_]\w*/g)||[]);const scoped=[...new Map((f.variables||[]).map(v=>[v.name,v])).values()];const vars=scoped.filter(v=>tokens.has(v.name));const ids=new Set((f.memory_state?.heap_nodes||[]).map(n=>n.id));const relevant=vars.filter(v=>ids.has(v.value));if(!relevant.length)continue;const html=ctx.gGraphMemoryMarkup(f),first=html.match(/data-graph-live-node="([^"]+)"/)[1];assert.ok(relevant.some(v=>v.value===first)||vars.some(v=>v.value&&typeof v.value==='object'&&Object.values(v.value).includes(first)));for(const v of vars.slice(0,6))assert.ok(html.includes(`<code>${v.name}</code>`));active++;}
console.log(`PASS ${active} real active-line pointer frames prioritize relevant reservations and variables without inventing scope`);
const src=fs.readFileSync('static/js/graph.js','utf8');const invalidate=src.slice(src.indexOf('  function invalidateTrace(message) {'),src.indexOf('  function buildSelectionKey'));
const clearCtx=vm.createContext({currentPedagogyFrame:{old:true},visualState:{querySelector(){return null;}},pageState:{},gById:id=>panels[id],tracePlayer:{clear(){}},stepNavigation:{},simStep:{},updateGraphStepKind(){},refreshGraphPrintfConsole(){},setSimulationButtonsState(){}});vm.runInContext(invalidate+'\ninvalidateTrace("reset");',clearCtx);assert.equal(clearCtx.currentPedagogyFrame,null);assert.match(panels['graph-live-memory'].textContent,/Prepara una traza/);assert.equal(clearCtx.pageState.traceCursor,-1);
console.log('PASS invalidation clears stale live memory and source frame after reset/input changes');
const oldState={last_operation:{name:'remove_edge'},last_result:{result:true}};
const oldCopy=JSON.stringify(oldState);assert.doesNotMatch(ctx.gGraphPresentedResult(oldState,{operation:'run_bfs',pending:true}),/true/);assert.match(ctx.gGraphPresentedResult(oldState,{operation:'run_bfs'}),/pendiente/);
const bfsState={last_operation:{name:'run_bfs'},last_result:{result:[1,2,3]}};
assert.match(ctx.gGraphPresentedResult(bfsState,{operation:'run_bfs'}),/1 -&gt; 2 -&gt; 3/);
assert.doesNotMatch(ctx.gGraphPresentedResult(bfsState,{operation:'run_bfs',pending:true}),/1 -&gt;/);
assert.match(ctx.gGraphPresentedResult(bfsState,{operation:'run_dijkstra'}),/pendiente/);
assert.equal(JSON.stringify(oldState),oldCopy);
console.log('PASS explicit publication context: stale prior op hidden, final normal visible, back pending, phase change pending, source untouched');
for(const c of fixtures){const final=c.steps.at(-1).state_after;const before=JSON.stringify(final);const normal=ctx.gGraphPresentedResult(final,{operation:c.operation});if(final.last_result?.result!==undefined)assert.ok(!normal.includes('pendiente'));assert.match(ctx.gGraphPresentedResult(final,{operation:c.operation,pending:true}),/pendiente/);assert.equal(JSON.stringify(final),before);}
console.log('PASS all six real final state_after publication records; backward projection hides only result panel');
let duplicates=0;
for(const c of fixtures)for(const step of c.steps){const f=step.pedagogy;if(!f)continue;const vars=f.variables||[],names=vars.map(v=>v.name);if(new Set(names).size===names.length)continue;const html=ctx.gGraphMemoryMarkup(f);for(const name of new Set(names)){const count=html.split(`<code>${name}</code>`).length-1;assert.ok(count<=1);if(count&&names.filter(n=>n===name).length>1)assert.ok(html.includes(`<code>${name}</code> <small>(`));}duplicates++;}
console.log(`PASS ${duplicates} real recursive frames: compact homonyms use latest scope once, scope label visible, full raw stack retained`);
assert.doesNotMatch(ctx.gGraphPresentedResult(oldState,{idle:true}),/pendiente|true/);
assert.match(ctx.gGraphPresentedResult(oldState,{idle:true}),/Sin ejecución actual/);
console.log('PASS reset/selection invalidation is idle, not a fictitious running operation');
