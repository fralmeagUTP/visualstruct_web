const fs=require('node:fs'),vm=require('node:vm'),assert=require('node:assert/strict');
const panels={};const ctx=vm.createContext({window:{},document:{addEventListener(){},getElementById(id){return panels[id]||null;}}});
const source=fs.readFileSync('static/js/hash.js','utf8');vm.runInContext(source,ctx);
for(const id of ['hash-live-memory','hash-memory-view','hash-pointers-view','hash-chain-view','hash-formula-view','hash-cost-view','hash-invariant-view','hash-minimap'])panels[id]={innerHTML:'',textContent:''};
const fixtures=JSON.parse(fs.readFileSync('qa/hash_classroom_fixtures.json','utf8'));let count=0;
for(const c of fixtures)for(const step of c.steps){const f=step.pedagogy,before=JSON.stringify(f);ctx.renderHashPedagogy(f,'intermediate');const html=panels['hash-live-memory'].innerHTML;for(const node of f.memory?.heap||[])assert.ok(html.includes(`data-hash-live-node="${node.id}"`));assert.doesNotMatch(html,/\[object Object\]/);assert.equal(JSON.stringify(f),before);assert.match(panels['hash-memory-view'].innerHTML,/<details><summary>Registro técnico completo/);if(!Object.keys(f.memory?.variables||{}).length)assert.match(panels['hash-pointers-view'].innerHTML,/Sin variables locales activas/);count++;}
const suspended={suspended:true,suspension_reason:'Capacidad histórica 129',metadata:{capacity:129}};const before=JSON.stringify(suspended),container={innerHTML:''};ctx.renderHashState(suspended,container);assert.match(container.innerHTML,/129/);assert.match(container.innerHTML,/no se reconstruye/);assert.doesNotMatch(container.innerHTML,/Tamano:|No hay buckets/);assert.equal(JSON.stringify(suspended),before);assert.equal(panels['hash-minimap'].innerHTML,'');
const uninit=ctx.hashLiveMemoryMarkup({memory:{heap:[{id:'N',initialized_mask:0,key:null,value:null,next:null}]}});assert.match(uninit,/clave: sin inicializar/);assert.match(uninit,/siguiente: sin inicializar/);
const initialized=ctx.hashLiveMemoryMarkup({memory:{heap:[{id:'N',initialized_mask:7,key:0,value:0,next:null}]}});assert.match(initialized,/siguiente: NULL/);
const dead=ctx.hashLiveMemoryMarkup({memory:{heap:[{id:'N',alive:false,initialized_mask:0,historical_fields:{key:3}}]}});assert.match(dead,/reserva liberada; no leer campos/);assert.doesNotMatch(dead,/clave: 3/);
console.log(`PASS ${count} real Hash frames immutable, every live/retired ID retained, masks interpreted, no invented final local NULL; suspended legacy never fake empty`);
(async()=>{
const a=source.indexOf('  async function executeOperationAndLoadTrace('),b=source.indexOf('  async function ensureTraceForCurrentSelection',a);let fetches=0;
const old={suspended:false,metadata:{capacity:5,size:1}},oldTrace={steps:[1]};const env=vm.createContext({pendingExecution:false,visualState:old,consoleState:{trace:oldTrace},traceSelectionKey:'old',window:{confirm(){return true;}},showHashMessage(){},setSimulationButtonsEnabled(){},resetButton:{},form:{dataset:{operateUrl:'/local'}},fetch:async()=>{fetches++;return {ok:false,json:async()=>({success:false,preserve_session:true,execution_trace:{steps:[],execution_started:false}})}}});
vm.runInContext(source.slice(a,b),env);const op={name:'create_table',inputs:[{name:'capacity',min:1,max:128}]};
await env.executeOperationAndLoadTrace(op,{capacity:129},'new',{});assert.equal(fetches,0);assert.equal(env.visualState,old);assert.equal(env.consoleState.trace,oldTrace);
await env.executeOperationAndLoadTrace(op,{capacity:128},'new',{});assert.equal(fetches,1);assert.equal(env.visualState,old);assert.equal(env.consoleState.trace,oldTrace);assert.equal(env.traceSelectionKey,'old');assert.equal(env.pendingExecution,false);
console.log('PASS capacity preflight and server preserve_session reject without clearing trace/state; no fetch for129');
})().catch(e=>{console.error(e);process.exitCode=1;});
const buffers=JSON.parse(fs.readFileSync('qa/hash_buffer_fixture.json','utf8'));let partial=0;
for(const step of buffers){const f=step.pedagogy,before=JSON.stringify(f);ctx.renderHashPedagogy(f,'intermediate');const b=f.memory?.buffer;if(b?.initialized_prefix>0&&b.initialized_prefix<b.capacity){assert.match(panels['hash-pointers-view'].innerHTML,new RegExp(`${b.initialized_prefix} de ${b.capacity} bytes inicializados`));assert.match(panels['hash-pointers-view'].innerHTML,/resto indeterminado/);partial++;}assert.equal(JSON.stringify(f),before);}
console.log(`PASS ${partial} real partial-buffer frames: initialized prefix distinct from indeterminate tail, no false wholly-uninitialized label`);
const failure=JSON.parse(fs.readFileSync('qa/hash_failure_fixtures.json','utf8'))[0].response.execution_trace.steps.at(-1).pedagogy;
assert.match(ctx.hashLiveMemoryMarkup(failure),/valor previo del llamador; th_buscar no lo escribió/);
assert.match(ctx.hashLiveMemoryMarkup(failure),/123456789/);
const arbitrary=JSON.parse(JSON.stringify(failure));arbitrary.memory.output.value=0;assert.match(ctx.hashLiveMemoryMarkup(arbitrary),/no lo escribió/);assert.match(ctx.hashLiveMemoryMarkup(arbitrary),/: 0<\/p>/);
const beforeReturn=JSON.parse(JSON.stringify(arbitrary));beforeReturn.source.line_text='actual = actual->siguiente;';assert.doesNotMatch(ctx.hashLiveMemoryMarkup(beforeReturn),/no lo escribió/);
console.log('PASS failed get caption derives from actual false return, preserves any caller value, no premature no-write claim');
const freed=fixtures.find(c=>c.operation==='remove').steps.find(s=>/free\(actual\)/.test(s.pedagogy.source.line_text)).pedagogy;
const removed=Object.values(freed.memory.variables).find(v=>v.valid===false&&v.historical_identity);assert.ok(removed);assert.match(ctx.hashVariableValue(removed),/puntero no utilizable; identidad histórica/);assert.ok(ctx.hashVariableValue(removed).includes(removed.historical_identity));assert.doesNotMatch(ctx.hashVariableValue(removed),/sin inicializar/);
console.log('PASS real free(actual) distinguishes invalid retired pointer from never-initialized storage, retaining historical identity only');

assert.match(ctx.hashLiveMemoryMarkup(buffers.at(-1).pedagogy),/70 de 2048 bytes inicializados/);

assert.match(fs.readFileSync('templates/hash/structure.html','utf8'),/class="hash-live-memory-panel"[^>]*>[\s\S]*?Identidades simbólicas; no son direcciones reales\.[\s\S]*?id="hash-live-memory"/);
console.log('PASS permanent symbolic-identity note inside exported memory region, independent of removed toolbar');
assert.equal(ctx.hashLoadFactorFormula({capacity:0,size:0,load_factor:0}),'Capacidad 0: factor 0 por convención del TAD, sin dividir.');
assert.match(ctx.hashLoadFactorFormula({capacity:5,size:2,load_factor:.4}),/2 \/ 5 = 0.4/);
assert.equal(ctx.hashBucketPointerLabel({root_bucket_pointer_valid:true,root_bucket_pointer:null,bucket_array_alive:false}),'buckets = NULL (sin arreglo).');
assert.doesNotMatch(ctx.hashBucketPointerLabel({root_bucket_pointer_valid:false,root_bucket_pointer:null,bucket_array_alive:false}),/= NULL/);
const destroy=JSON.parse(fs.readFileSync('qa/hash_destroy_fixture.json','utf8'));for(const step of destroy){const st=step.state_after||step.state_snapshot;const snapshot=JSON.stringify(st);const el={innerHTML:'',querySelector(){return null;}};ctx.renderHashState(st,el);if(st.metadata.capacity===0)assert.doesNotMatch(el.innerHTML,/0 \/ 0/);assert.equal(JSON.stringify(st),snapshot);}
console.log('PASS destroy states distinguish guarded factor0 from division0/0, and known NULL from indeterminate freed pointer');
