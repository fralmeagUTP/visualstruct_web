const fs=require('node:fs'),vm=require('node:vm'),assert=require('node:assert/strict');
const context=vm.createContext({window:{},document:{addEventListener(){}}});vm.runInContext(fs.readFileSync('static/js/sequential.js','utf8'),context);
const frames=JSON.parse(fs.readFileSync('qa/sublist_classroom_fixtures.json','utf8'));
for(const [index,state] of frames.entries()){
 const before=JSON.stringify(state),html=context.renderSublistDeletionState(state,true),main=html.split('<details')[0];
 assert.equal(JSON.stringify(state),before);
 assert.match(html,/<details class="seq-sublist-call-detail"><summary>Pila de llamadas: \d+ marco/);
 for(const frame of state.sublist_frames || [])assert.match(html,new RegExp(`data-sublist-frame="${frame.function}"`));
 for(const node of state.heap_nodes || [])assert.ok(main.includes(`data-sublist-node="${node.id}"`),`node ${node.id} frame${index}`);
 for(const [i,value] of (state.buffer_values || []).entries())assert.ok(main.includes(`destino[${i}] = ${value}`));
 assert.doesNotMatch(main,/<ol>/);
}
const state=frames[19],html=context.renderSublistDeletionState(state,false);
assert.match(html,/destino\[0\] = 3/);assert.match(html,/data-sublist-value="4"/);
assert.ok(html.indexOf('data-sublist-buffer-capacity')<html.indexOf('data-sublist-node='));
assert.equal(context.renderSublistDeletionState(frames.at(-1),true),context.renderSublistDeletionState(frames.at(-1),true));
console.log(`PASS ${frames.length} real Sublist query frames: all nodes/copied cells retained before optional call stack; no data mutation`);
