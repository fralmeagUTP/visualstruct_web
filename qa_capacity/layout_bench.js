const fs=require('fs');
const {performance}=require('perf_hooks');
const {gAdaptiveGraphPositions,gGraphLayoutMetrics}=require('../static/js/graph_layout.js');
const src=fs.readFileSync('static/js/graph.js','utf8');eval(src.slice(src.indexOf('function gGraphRoutes('),src.indexOf('function renderGraphSvg(')));
const n=Number(process.argv[2]),topology=process.argv[3];
const nodes=Array.from({length:n},(_,i)=>({id:String(i),label:String(i)}));
const pairs=topology==='chain'?Array.from({length:n-1},(_,i)=>[i,i+1]):nodes.flatMap((_,i)=>nodes.slice(i+1).map((_,j)=>[i,i+1+j]));
const edges=pairs.map(([i,j])=>({source:String(i),target:String(j),weight:1}));
let t=performance.now();const positions=gAdaptiveGraphPositions(nodes,edges);const layoutMs=performance.now()-t;
t=performance.now();const routes=gGraphRoutes(positions,edges);const labels=gPlaceGraphWeightLabels(positions,edges,26,routes);const labelsMs=performance.now()-t;
const points=nodes.map(n=>positions.get(n.id));const metrics=gGraphLayoutMetrics(points,pairs);
const geometry=[...points,...labels.flatMap(l=>[{x:l.box.left,y:l.box.top},{x:l.box.right,y:l.box.bottom}])];
let labelOverlaps=0;for(let i=0;i<labels.length;i++)for(let j=i+1;j<labels.length;j++){const a=labels[i].box,b=labels[j].box;if(a.left<b.right&&a.right>b.left&&a.top<b.bottom&&a.bottom>b.top)labelOverlaps++;}
console.log(JSON.stringify({n,topology,edges:edges.length,layoutMs,labelsMs,metrics,labelOverlaps,width:Math.max(...geometry.map(p=>p.x))-Math.min(...geometry.map(p=>p.x))+100,height:Math.max(...geometry.map(p=>p.y))-Math.min(...geometry.map(p=>p.y))+100,rss_mib:process.memoryUsage().rss/1024/1024}));
