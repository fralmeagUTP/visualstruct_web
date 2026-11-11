const fs=require('node:fs'),vm=require('node:vm'),assert=require('node:assert/strict');
const ctx=vm.createContext({document:{addEventListener(){}},window:{}});
vm.runInContext(fs.readFileSync('static/js/graph_layout.js','utf8'),ctx);
ctx.gAdaptiveGraphPositions=ctx.window.gAdaptiveGraphPositions;
vm.runInContext(fs.readFileSync('static/js/graph.js','utf8'),ctx);
const nodes=[1,2,3].map(id=>({id:String(id),label:String(id)}));
const edges=[[1,2,1],[2,3,2],[1,3,5]].map(([a,b,w])=>({source:String(a),target:String(b),weight:w}));
function edge(svg,a,b){return svg.match(new RegExp(`<path data-graph-source="${a}" data-graph-target="${b}"[^>]+>`))[0];}
for(const op of ['run_prim','run_kruskal']){
 const state={nodes,edges,directed:false,last_operation:{name:op},last_result:{result:{mst_edges:[[1,2,1],[2,3,2]]}}};
 let svg=ctx.renderGraphSvg(state,null,null);
 assert.match(edge(svg,1,2),/class="viz-graph-edge mst"/);
 assert.match(edge(svg,2,3),/class="viz-graph-edge mst"/);
 assert.match(edge(svg,1,3),/class="viz-graph-edge"/);
 for(const accepted of [[],[[1,2]],[[1,2],[2,3]],[[1,2]],[]]){
  svg=ctx.renderGraphSvg(state,null,{graph_progress:{mode:'mst',nodes:[],edges:accepted}});
  assert.equal((svg.match(/class="viz-graph-edge mst"/g)||[]).length,accepted.length);
 }
 state.last_result.result.mst_edges=[];
 assert.equal((ctx.renderGraphSvg(state,null,null).match(/class="viz-graph-edge mst"/g)||[]).length,0);
}
const css=fs.readFileSync('static/css/styles.css','utf8');
assert.match(css,/\.viz-graph-edge\.mst\s*\{[^}]*stroke:\s*#f2c500;/);
assert.match(css,/\.viz-graph-edge\s*\{[^}]*stroke:\s*#245f9d;/);
assert.match(fs.readFileSync('templates/graph/structure.html','utf8'),/Árbol de expansión mínima \(amarillo\)/);
console.log('PASS Prim/Kruskal final, forward/back/empty trace, failed result and yellow/blue legend contract');
