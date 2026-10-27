const fs=require('node:fs'),vm=require('node:vm'),assert=require('node:assert/strict');const ctx=vm.createContext({document:{addEventListener(){}},window:{}});vm.runInContext(fs.readFileSync('static/js/graph.js','utf8'),ctx);
const nodes=[{id:'1',label:'1'},{id:'2',label:'2'},{id:'3',label:'3'}],positions=new Map(nodes.map((n,i)=>[n.id,{x:360+50*Math.cos(2*Math.PI*i/3-Math.PI/2),y:180+50*Math.sin(2*Math.PI*i/3-Math.PI/2)}]));
function overlaps(a,b){return a.left<b.right&&a.right>b.left&&a.top<b.bottom&&a.bottom>b.top;}
for(const weights of [[1500000000,1500000000,2147483647],[-2147483648,-1500000000,0],[1,-1,1000000000]]){
 const edges=[[1,2],[2,3],[3,1]].map(([s,t],i)=>({source:String(s),target:String(t),weight:weights[i]})),before=JSON.stringify(edges),labels=ctx.gPlaceGraphWeightLabels(positions,edges);
 assert.equal(labels.length,3);for(let i=0;i<labels.length;i++){const label=labels[i];assert.equal(label.edge,edges[i]);for(const node of positions.values())assert(!overlaps(label.box,{left:node.x-26,right:node.x+26,top:node.y-26,bottom:node.y+26}));for(let j=0;j<i;j++)assert(!overlaps(label.box,labels[j].box));}
 const svg=ctx.renderGraphSvg({nodes,edges,directed:true},null,null);for(const w of weights)assert(svg.includes(`>${w}</text>`));const bounds=svg.match(/viewBox="([^"]+)"/)[1].split(' ').map(Number);assert(bounds[3]<=152);for(const label of labels){assert(label.box.left>=bounds[0]);assert(label.box.right<=bounds[0]+bounds[2]);assert(svg.includes(`data-weight-source="${label.edge.source}" data-weight-target="${label.edge.target}"`));}assert.equal(JSON.stringify(edges),before);
}
for(const directed of [false,true]){
 const state={nodes:[{id:'7',label:'7'}],edges:[{source:'7',target:'7',weight:-2147483648}],directed};const svg=ctx.renderGraphSvg(state,null,null);assert.match(svg,/<path data-graph-self-loop="7" d="M [^\"]+ C /);const path=svg.match(/<path data-graph-self-loop[^>]+>/)[0];assert.equal(path.includes('marker-end'),directed);assert.match(svg,/>-2147483648<\/text>/);assert.match(svg,/Costo del arco 7 → 7: -2147483648/);const b=svg.match(/viewBox="([^"]+)"/)[1].split(' ').map(Number);assert(b[2]>=162);assert.equal(b[3],76);
}
console.log('PASS three long/negative/zero weight matrices: no node/label collisions, exact digits and edge association; directed/undirected self-loop curves and export bounds');
