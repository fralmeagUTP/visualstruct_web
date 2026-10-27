const fs=require('node:fs'),vm=require('node:vm'),assert=require('node:assert/strict');
const source=fs.readFileSync('static/js/graph.js','utf8'),fixtures=JSON.parse(fs.readFileSync('qa_convergence/book_frontend_fixtures.json','utf8'));
function freeze(x){if(x&&typeof x==='object'){Object.values(x).forEach(freeze);Object.freeze(x);}return x;}
freeze(fixtures);
const elements=new Map(),events=new Map();
function el(id){const e={id,innerHTML:'',textContent:'',disabled:false,dataset:{},classList:{toggle(){}},getAttribute(k){return this[k];},setAttribute(k,v){this[k]=v;},removeAttribute(k){delete this[k];},addEventListener(k,fn){events.set(id+':'+k,fn);},querySelector(){return null;},querySelectorAll(){return [];}};elements.set(id,e);return e;}
let request,download,reloaded=false,confirm=true;
const ctx=vm.createContext({console,Set,Map,Blob,URL:{createObjectURL(){return 'blob:test'},revokeObjectURL(){}},document:{addEventListener(){},getElementById(id){return elements.get(id)||null;},querySelectorAll(){return [...elements.values()];},createElement(){return {click(){download=this.download;}};}},window:{confirm(){return confirm;},location:{reload(){reloaded=true;}},requestAnimationFrame(fn){fn();}},fetch:async(url,options)=>{request={url,options};return {ok:true,json:async()=>({success:true,history:[{original:'unchanged'}]})};}});
vm.runInContext(source,ctx);
for(const state of fixtures.states){const before=JSON.stringify(state),html=ctx.formatGraphResult(state);assert(!html.includes('[object Object]'));assert(html.includes('Contrato C'));assert.equal(JSON.stringify(state),before);if(state.last_result.c_status>0)assert(!html.includes('<strong>Peso total:'));}
assert.match(ctx.formatGraphResult(fixtures.states[1]),/Costo escrito:<\/strong> 0/);
assert.match(ctx.formatGraphResult(fixtures.states[2]),/salida no escrita/);
assert.match(ctx.formatGraphResult(fixtures.states[3]),/resultado vacío válido/);assert.match(ctx.formatGraphResult(fixtures.states[3]),/No hay nodos devueltos que liberar/);assert(!ctx.formatGraphResult(fixtures.states[3]).includes('libera los nodos después')); 
assert.match(ctx.formatGraphResult(fixtures.states[3]),/Peso total:<\/strong> 0/);
for(const [operation,symbol] of Object.entries(fixtures.model.didactic.operation_functions)){const code=fixtures.model.didactic.operations[operation];const index=ctx.gBookFunctionLine(code,symbol);assert(index>=0,symbol);assert(code.split('\n')[index].includes(symbol+'('));}
for(const frame of fixtures.frames){const before=JSON.stringify(frame),html=ctx.gGraphMemoryMarkup(frame);assert(!html.includes('[object Object]'));for(const n of frame.memory_state.heap_nodes)assert(html.includes(`data-graph-live-node="${n.id}"`));assert.equal(JSON.stringify(frame),before);}
const main=el('graph-download-main');main.href='/main';ctx.gUpdateBookMainAvailability({main_unavailable_reason:'Fallo diagnóstico no reproducible con libc'});assert.equal(main.href,undefined);assert.match(main.textContent,/Fallo diagnóstico/);ctx.gUpdateBookMainAvailability({});assert.equal(main.href,'/main');
const history=el('history');ctx.renderGraphHistory([],history,fixtures.model.didactic,fixtures.model.main_c);assert.match(history.innerHTML,/Programa principal/);assert(!history.innerHTML.includes('&nbsp;'));
assert.equal(ctx.gGraphPhaseLabel({book_instruction_model:true,instruction_event:{phase:'write'}}),'Escribir un valor');
const container=el('test');ctx.renderGraphState({suspended:true,suspension_reason:'versión anterior'},container);assert.match(container.innerHTML,/no es un grafo vacío/);assert(!container.innerHTML.includes('Vértices: 0'));
const controls=el('graph-controls');controls.dataset={historyUrl:'/graph/graph/history',resetUrl:'/reset',operateUrl:'/operate'};
for(const id of ['graph-visual-state','graph-live-memory','action-history','graph-download-main','graph-message-box','graph-export-summary','graph-reset-button','graph-sim-next'])el(id);
ctx.initGraphPage({suspended:true,visual_state:{suspended:true,suspension_reason:'historial anterior'},history:[{old:1}],main_unavailable_reason:'Contrato anterior'});
assert.equal(elements.get('graph-sim-next').disabled,true);assert.equal(elements.get('graph-export-summary').disabled,false);assert.equal(elements.get('graph-download-main')['aria-disabled'],'true');
(async()=>{
 await events.get('graph-export-summary:click')();assert.equal(request.url,'/graph/graph/history');assert.equal(download,'graph-history-original.json');
 confirm=false;request=null;await events.get('graph-reset-button:click')();assert.equal(request,null);assert.equal(reloaded,false);
 confirm=true;await events.get('graph-reset-button:click')();assert.equal(request.options.method,'POST');assert.equal(reloaded,true);
 await ctx.executeGraphOperation(controls,'list_vertices',{},'normal');assert.equal(JSON.parse(request.options.body).execution_mode,'normal');
 await ctx.executeGraphOperation(controls,'list_vertices',{},'step');assert.equal(JSON.parse(request.options.body).execution_mode,'step');
 console.log(`PASS 8 canonical results, 19 source function targets, ${fixtures.frames.length} immutable memory frames, suspended export/reset and explicit modes`);
})().catch(e=>{console.error(e);process.exitCode=1;});
