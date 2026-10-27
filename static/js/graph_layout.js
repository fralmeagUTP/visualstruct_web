/* Deterministic, topology-only graph drawing. Pure presentation: never mutates graph data.
 * Heuristic multistart stress + local crossing/clearance search, not a planarity test
 * or a guarantee of the global crossing minimum. No dependencies or animation loop.
 */
(function (root) {
  'use strict';
  const {hypot,min,max,pow,cos,sin,imul,sqrt,PI}=Math;
  const cache = new Map();
  const compare = (a,b) => a.localeCompare(b, 'en', {numeric:true}) || (a < b ? -1 : a > b ? 1 : 0);
  const distance = (a,b) => hypot(a.x-b.x,a.y-b.y);
  function segmentDistance(p,a,b) {
    const dx=b.x-a.x,dy=b.y-a.y,l=dx*dx+dy*dy;
    const t=l?max(0,min(1,((p.x-a.x)*dx+(p.y-a.y)*dy)/l)):0;
    return hypot(p.x-a.x-t*dx,p.y-a.y-t*dy);
  }
  function crosses(a,b,c,d) {
    const abx=b.x-a.x,aby=b.y-a.y,cdx=d.x-c.x,cdy=d.y-c.y;
    return (abx*(c.y-a.y)-aby*(c.x-a.x))*(abx*(d.y-a.y)-aby*(d.x-a.x))<-1e-6 && (cdx*(a.y-c.y)-cdy*(a.x-c.x))*(cdx*(b.y-c.y)-cdy*(b.x-c.x))<-1e-6;
  }
  function metrics(points, links) {
    let crossings=0,nodeOverlaps=0,edgeNodeOverlaps=0,minNodeDistance=Infinity;
    for(let i=0;i<points.length;i++)for(let j=i+1;j<points.length;j++){
      const d=distance(points[i],points[j]);minNodeDistance=min(d,minNodeDistance);if(d<52-1e-6)nodeOverlaps++;
    }
    links.forEach(([a,b],i)=>{
      for(let k=0;k<points.length;k++)if(k!==a&&k!==b&&segmentDistance(points[k],points[a],points[b])<26)edgeNodeOverlaps++;
      for(let j=i+1;j<links.length;j++){const [c,d]=links[j];if(a!==c&&a!==d&&b!==c&&b!==d&&crosses(points[a],points[b],points[c],points[d]))crossings++;}
    });
    return {crossings,nodeOverlaps,edgeNodeOverlaps,minNodeDistance:Number.isFinite(minNodeDistance)?minNodeDistance:null};
  }
  function componentLayout(n,links,seed) {
    if(n===1)return [{x:0,y:0}];
    const graph=Array.from({length:n},()=>Array(n).fill(Infinity));
    for(let i=0;i<n;i++)graph[i][i]=0;
    for(const [a,b] of links)graph[a][b]=graph[b][a]=1;
    for(let k=0;k<n;k++)for(let i=0;i<n;i++)for(let j=0;j<n;j++)graph[i][j]=min(graph[i][j],graph[i][k]+graph[k][j]);
    let r=(seed+1)*9301;
    const random=()=>{r=(imul(1664525,r)+1013904223)>>>0;return r/4294967296;};
    let p=Array.from({length:n},()=>({x:(random()-.5)*300,y:(random()-.5)*300}));
    const desired=graph.map(row=>row.map(d=>130*pow(d,.78)));
    // Stress gradient relaxation uses all-pairs graph distances, not input ordering.
    for(let step=0;step<220;step++){
      const delta=p.map(()=>({x:0,y:0}));
      for(let i=0;i<n;i++)for(let j=i+1;j<n;j++){
        let dx=p[j].x-p[i].x,dy=p[j].y-p[i].y,d=hypot(dx,dy)||.01;
        let force=(d-desired[i][j])/(graph[i][j]*graph[i][j]);
        if(d<90)force-=2*(90-d);
        const f=force*.09;delta[i].x+=dx/d*f;delta[i].y+=dy/d*f;delta[j].x-=dx/d*f;delta[j].y-=dy/d*f;
      }
      p=p.map((v,i)=>({x:v.x+delta[i].x,y:v.y+delta[i].y}));
    }
    const crossingPairs=[];
    links.forEach(([a,b],i)=>{for(let j=i+1;j<links.length;j++){const [c,d]=links[j];if(a!==c&&a!==d&&b!==c&&b!==d)crossingPairs.push([a,b,c,d]);}});
    function cost(q) {
      let value=0;
      for(let i=0;i<n;i++)for(let j=i+1;j<n;j++){
        const d=distance(q[i],q[j]);value+=pow(d-desired[i][j],2)/(graph[i][j]*graph[i][j])*.12;
        if(d<100)value+=pow(100-d,2)*150;
      }
      links.forEach(([a,b],i)=>{
        for(let k=0;k<n;k++)if(k!==a&&k!==b){const d=segmentDistance(q[k],q[a],q[b]);if(d<48)value+=pow(48-d,2)*160;}

      });
      for(let k=0;k<crossingPairs.length;k++){const pair=crossingPairs[k];if(crosses(q[pair[0]],q[pair[1]],q[pair[2]],q[pair[3]]))value+=250000;}
      return value;
    }
    let best=cost(p);
    // Local movement and swaps escape many crossing-heavy stress minima.
    for(const size of [90,45,22,10,4]){
      for(let pass=0;pass<5;pass++){
        let changed=false;
        for(let i=0;i<n;i++){
          const original=p[i];let chosen=original;
          for(let k=0;k<8;k++){
            const angle=k*PI/4;p[i]={x:original.x+cos(angle)*size,y:original.y+sin(angle)*size};
            const score=cost(p);if(score<best-1e-7){best=score;chosen=p[i];changed=true;}
          }
          p[i]=chosen;
        }
        if(size>=22)for(let i=0;i<n;i++)for(let j=i+1;j<n;j++){
          [p[i],p[j]]=[p[j],p[i]];const score=cost(p);
          if(score<best-1e-7){best=score;changed=true;}else [p[i],p[j]]=[p[j],p[i]];
        }
        if(!changed)break;
      }
    }
    return {points:p,cost:best};
  }
  function compute(ids,links) {
    const n=ids.length,adj=Array.from({length:n},()=>[]);
    links.forEach(([a,b])=>{adj[a].push(b);adj[b].push(a);});
    const seen=new Set(),components=[];
    for(let i=0;i<n;i++)if(!seen.has(i)){
      const group=[i];seen.add(i);
      for(let k=0;k<group.length;k++)for(const j of adj[group[k]])if(!seen.has(j)){seen.add(j);group.push(j);}
      group.sort((a,b)=>a-b);components.push(group);
    }
    components.sort((a,b)=>b.length-a.length||a[0]-b[0]);
    const output=Array(n);let x=0,y=0,rowHeight=0;
    const rowLimit=max(500,sqrt(n)*220);
    for(const group of components){
      const local=new Map(group.map((id,i)=>[id,i]));
      const localLinks=links.filter(([a,b])=>local.has(a)&&local.has(b)).map(([a,b])=>[local.get(a),local.get(b)]);
      let best;
      if(group.length===1)best={points:[{x:0,y:0}],cost:0};
      else for(let seed=0;seed<(localLinks.length>45?4:8);seed++){const trial=componentLayout(group.length,localLinks,seed);if(!best||trial.cost<best.cost)best=trial;}
      const p=best.points;const minX=min(...p.map(q=>q.x)),minY=min(...p.map(q=>q.y));
      const w=max(...p.map(q=>q.x))-minX+140,h=max(...p.map(q=>q.y))-minY+140;
      if(x>0&&x+w>rowLimit){y+=rowHeight;x=0;rowHeight=0;}
      group.forEach((id,i)=>{output[id]={x:p[i].x-minX+x+70,y:p[i].y-minY+y+70};});
      x+=w;rowHeight=max(rowHeight,h);
    }
    return output;
  }
  function adaptive(nodes,edges) {
    const ids=[...new Set(nodes.map(n=>String(n.id)))].sort(compare),index=new Map(ids.map((id,i)=>[id,i]));
    const pairs=new Set();
    for(const e of edges){let a=index.get(String(e.source)),b=index.get(String(e.target));if(a===undefined||b===undefined||a===b)continue;if(a>b)[a,b]=[b,a];pairs.add(`${a},${b}`);}
    const links=[...pairs].sort().map(s=>s.split(',').map(Number));
    // Geometry is independent of weights, traversal flags and ordering. Reciprocal
    // arcs share the same underlying graph; the renderer separates their paths.
    const key=JSON.stringify([ids,links]);
    let points=cache.get(key);
    if(!points){points=compute(ids,links);if(cache.size>=64)cache.delete(cache.keys().next().value);cache.set(key,points);}
    const labels=new Map(nodes.map(node=>[String(node.id),node.label]));
    return new Map(ids.map((id,i)=>[id,{...points[i],label:labels.get(id)}]));
  }
  root.gAdaptiveGraphPositions=adaptive;
  if(typeof module!=='undefined'&&module.exports)module.exports={gAdaptiveGraphPositions:adaptive,gGraphLayoutMetrics:metrics};
})(typeof window!=='undefined'?window:globalThis);
