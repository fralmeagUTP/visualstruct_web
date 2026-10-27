const fs=require('node:fs'),vm=require('node:vm'),assert=require('node:assert/strict');const ctx=vm.createContext({document:{addEventListener(){}},window:{}});vm.runInContext(fs.readFileSync('static/js/graph.js','utf8'),ctx);
function freeze(v){if(v&&typeof v==='object'){Object.values(v).forEach(freeze);Object.freeze(v);}return v;}
const frame=freeze(JSON.parse(fs.readFileSync('qa_convergence/book_active_fields_fixture.json','utf8'))),before=JSON.stringify(frame),html=ctx.gGraphMemoryMarkup(frame),ids=[...html.matchAll(/data-graph-live-node="([^"]+)"/g)].map(m=>m[1]);
const t=frame.variables.filter(v=>v.name==='t'&&v.value&&typeof v.value==='object').at(-1).value;
assert.deepEqual(ids.slice(0,3),[t.usado,t.alcanzable,t.dist]);assert.deepEqual([...ids].sort(),frame.memory_state.heap_nodes.map(n=>n.id).sort());assert.equal(JSON.stringify(frame),before);
const inline=html.split('class="graph-live-variables"')[1].split('class="graph-live-cards"')[0];assert(inline.includes('usado:'));assert(inline.includes('alcanzable:'));assert(inline.includes('dist:'));assert(!inline.includes('vertices:'));
const arrow=JSON.parse(before);arrow.source.line_text='if (t->dist[j] < t->dist[u])';arrow.condition=null;const ah=ctx.gGraphMemoryMarkup(arrow);assert.equal([...ah.matchAll(/data-graph-live-node="([^"]+)"/g)][0][1],t.dist);
console.log('PASS real Dijkstra field-specific card priority usado/alcanzable/dist, exact tokens dot/arrow, all IDs retained and source immutable');
