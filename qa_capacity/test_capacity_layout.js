const assert=require('node:assert/strict');const fs=require('fs');const {performance}=require('perf_hooks');
const {gAdaptiveGraphPositions,gGraphLayoutMetrics}=require('../static/js/graph_layout.js');
const src=fs.readFileSync('static/js/graph.js','utf8');eval(src.slice(src.indexOf('function gGraphRoutes('),src.indexOf('function renderGraphSvg(')));
for(const n of [20,30])for(const type of ['path','tree','cycle','complete','isolated']){
 const nodes=Array.from({length:n},(_,i)=>({id:String(i),label:String(i)}));
 const pairs=type==='path'?nodes.slice(1).map((_,i)=>[i,i+1]):type==='tree'?nodes.slice(1).map((_,i)=>[Math.floor(i/2),i+1]):type==='cycle'?nodes.map((_,i)=>[i,(i+1)%n]):type==='complete'?nodes.flatMap((_,i)=>nodes.slice(i+1).map((_,j)=>[i,i+1+j])):[];
 const edges=pairs.map(([a,b])=>({source:String(a),target:String(b),weight:1}));const input=JSON.stringify([nodes,edges]);let t=performance.now();
 const pos=gAdaptiveGraphPositions(nodes,edges);assert.equal(pos.size,n);for(const p of pos.values())assert(Number.isFinite(p.x)&&Number.isFinite(p.y));
 const m=gGraphLayoutMetrics(nodes.map(n=>pos.get(n.id)),pairs);assert.equal(m.nodeOverlaps,0);
 if(type==='path'||type==='tree')assert.equal(m.crossings,0);
 assert.deepEqual([...gAdaptiveGraphPositions([...nodes].reverse(),[...edges].reverse())],[...pos]);
 const labels=gPlaceGraphWeightLabels(pos,edges);assert.equal(labels.length,edges.length);assert(labels.every((x,i)=>x.edge===edges[i]));
 const cached=gPlaceGraphWeightLabels(pos,edges);assert.deepEqual(cached,labels);if(labels.length){cached[0].box.left=-999999;assert.notEqual(gPlaceGraphWeightLabels(pos,edges)[0].box.left,-999999);}
 for(let i=0;i<labels.length;i++)for(let j=i+1;j<labels.length;j++){let a=labels[i].box,b=labels[j].box;assert(!(a.left<b.right&&a.right>b.left&&a.top<b.bottom&&a.bottom>b.top));}
 assert.equal(JSON.stringify([nodes,edges]),input);const ms=performance.now()-t;assert(ms<3000,`bounded layout ${type}/${n}: ${ms}`);console.log(JSON.stringify({n,type,ms,metrics:m}));
}
console.log('10 graph capacity layouts passed');
