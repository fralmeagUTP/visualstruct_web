const fs = require('node:fs'), assert = require('node:assert/strict'), crypto=require('node:crypto');
const {JSDOM} = require(process.env.JSDOM_MODULE || 'jsdom');
const fixture = JSON.parse(fs.readFileSync(process.argv[2], 'utf8'));
const dom = new JSDOM('<pre id="code"></pre><div id="status"></div><div id="counter"></div><div id="visual"></div>', {url:'http://localhost/', runScripts:'outside-only'});
const w = dom.window;
w.eval(fs.readFileSync('static/js/interpreter_runtime.js','utf8'));
w.eval(fs.readFileSync('static/js/hash.js','utf8') + '\nObject.assign(window,{hashExpandInstructionTrace,renderHashState,renderHashPedagogy});');
const trace = w.hashExpandInstructionTrace(fixture.wire);
if(fixture.logical) assert.deepEqual(JSON.parse(JSON.stringify(trace)), fixture.logical);
else {assert.deepEqual(trace.steps.map(s=>s.event_type),fixture.events);assert.deepEqual(JSON.parse(JSON.stringify(trace.final_state)),fixture.final_state);}
assert.equal(w.hashExpandInstructionTrace(trace), trace);
assert.equal(Object.isFrozen(trace.steps[0].state_snapshot), true);
assert.equal(trace.steps[0].state_snapshot, trace.steps[1].state_snapshot);
function digest(t){const hash=crypto.createHash('sha256');for(const step of t.steps)hash.update(JSON.stringify(step));return hash.digest('hex');}
const before = digest(trace); let latest;
const player = w.InterpreterRuntime.createTracePlayer({codeElement:w.document.getElementById('code'),statusElement:w.document.getElementById('status'),counterElement:w.document.getElementById('counter'),renderState(state,step){w.renderHashState(state,w.document.getElementById('visual'));w.renderHashPedagogy(step.pedagogy,'intermediate');},onCursorChange(event){latest=event;}});
player.loadTrace(trace);
for(let i=0;i<trace.steps.length;i++) {assert.equal(player.seek(i),true);assert.equal(latest.step,trace.steps[i]);}
assert.equal(player.getTotalSteps(), (fixture.logical?.steps.length ?? fixture.events.length));
for(const index of [0,trace.steps.length-1,2,1,-1,trace.steps.length-1]) assert.equal(player.seek(index),true);
assert.equal(latest.step.console_stdout,trace.console_stdout);
player.reset();assert.equal(player.getCursor(),-1);
player.loadTrace(w.hashExpandInstructionTrace(JSON.parse(JSON.stringify(fixture.wire))));
assert.equal(player.seek(trace.steps.length-1),true);
assert.equal(latest.step.console_stdout,trace.console_stdout);
assert.equal(digest(trace),before);
assert.equal(JSON.stringify({frame:trace.steps.at(-1).pedagogy,state:trace.final_state}).includes('$hash_ref'),false);
player.clear();assert.equal(player.hasTrace(),false);
for(const bad of [-1,999999,true,'0']) assert.throws(()=>w.hashExpandInstructionTrace({hash_snapshot_codec:'hash-snapshot-pool/v1',hash_snapshot_pool:[[1,[{$hash_ref:bad}]]],steps:[]}));
const malformed = [ [[0,[['a',1,2]]]], [[0,[['a',1],['a',2]]]], [[1,[{$hash_ref:1}]]], [[1,[{$hash_ref:0}]]] ];
for(const records of malformed)assert.throws(()=>w.hashExpandInstructionTrace({hash_snapshot_codec:'hash-snapshot-pool/v1',hash_snapshot_pool:records,steps:[]}));
const legacy={steps:[]};assert.equal(w.hashExpandInstructionTrace(legacy),legacy);
assert.ok(process.memoryUsage().rss < 512*1024*1024, `RSS ${process.memoryUsage().rss}`);
console.log(JSON.stringify({steps:trace.steps.length,rss_bytes:process.memoryUsage().rss,heap_bytes:process.memoryUsage().heapUsed}));
dom.window.close();
console.log(`PASS Hash codec deep equality; ${trace.steps.length} real steps rendered/seeked; frozen snapshots unchanged; reload/reset/export; invalid references rejected`);
