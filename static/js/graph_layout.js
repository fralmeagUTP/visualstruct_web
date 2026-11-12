/* Incremental graph drawing with a stable mental map for each editing session.
 * Pure presentation: never mutates graph data. Initial small graphs use multistart
 * stress; later edits grow locally. Not a planarity test or global crossing minimum.
 * No dependencies or animation loop.
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
  // A persistent mental map: additions start near neighbours, never on a
  // size-triggered ring. Only presentation coordinates are retained.
  let previous = new Map();
  let previousPairs = new Set();
  let previousKey = null;
  function grow(ids, links, seedPositions) {
    const p=ids.map(id=>seedPositions.has(id)?{...seedPositions.get(id)}:null);
    const neighbours=ids.map(()=>[]);
    links.forEach(([a,b])=>{neighbours[a].push(b);neighbours[b].push(a);});
    function score(at,q) {
      let value=0;
      for(let j=0;j<p.length;j++)if(j!==at&&p[j]){
        const d=distance(q,p[j]);
        if(d<100)value+=pow(100-d,2)*10000;
        else value+=1000/(d*d);
      }
      for(const j of neighbours[at])if(p[j])value+=pow(distance(q,p[j])-130,2);
      for(const [a,b] of links){
        if(a===at||b===at||!p[a]||!p[b])continue;
        const d=segmentDistance(q,p[a],p[b]);if(d<48)value+=pow(48-d,2)*100;
        for(const j of neighbours[at])if(j!==a&&j!==b&&p[j]&&crosses(q,p[j],p[a],p[b]))value+=50000;
      }
      return value;
    }
    // Input vertex order is preserved for cold loading; existing vertices stay
    // anchored when a new vertex is inserted. IDs are never rewritten.
    for(let i=0;i<p.length;i++)if(!p[i]){
      const connected=neighbours[i].map(j=>p[j]).filter(Boolean);
      const occupied=p.filter(Boolean);
      if(!occupied.length){p[i]={x:70,y:70};continue;}
      const anchor=connected.length?{
        x:connected.reduce((v,q)=>v+q.x,0)/connected.length,
        y:connected.reduce((v,q)=>v+q.y,0)/connected.length
      }:{x:occupied[occupied.length-1].x,y:occupied[occupied.length-1].y};
      let best=null,bestCost=Infinity;
      for(let ring=1;ring<=4;ring++)for(let k=0;k<16;k++){
        const angle=k*PI/8,q={x:anchor.x+130*ring*cos(angle),y:anchor.y+130*ring*sin(angle)};
        const cost=score(i,q)+ring*ring+(connected.length?0:distance(q,{x:70,y:70})*.1);
        if(cost<bestCost){best=q;bestCost=cost;}
      }
      p[i]=best;
    }
    // A newly added link may improve its immediate neighbourhood, with a hard
    // 24 px displacement cap per existing vertex. No component-wide repacking.
    const allKnown=ids.every(id=>seedPositions.has(id));
    if(allKnown){
      const touched=new Set();
      links.forEach(([a,b])=>{const key=[ids[a],ids[b]].sort(compare).join('\u0000');if(!previousPairs.has(key)){touched.add(a);touched.add(b);}});
      for(const i of touched){
        const original=p[i];let best=original,bestCost=score(i,original);
        for(let k=0;k<16;k++){
          const q={x:original.x+24*cos(k*PI/8),y:original.y+24*sin(k*PI/8)},cost=score(i,q);
          if(cost<bestCost){best=q;bestCost=cost;}
        }
        p[i]=best;
      }
    }
    return p;
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
      else if(group.length>15)best={points:grow(group.map(i=>ids[i]),localLinks,new Map()),cost:0};
      else for(let seed=0;seed<(localLinks.length>45?4:8);seed++){const trial=componentLayout(group.length,localLinks,seed);if(!best||trial.cost<best.cost)best=trial;}
      const p=best.points;const minX=min(...p.map(q=>q.x)),minY=min(...p.map(q=>q.y));
      const w=max(...p.map(q=>q.x))-minX+140,h=max(...p.map(q=>q.y))-minY+140;
      if(x>0&&x+w>rowLimit){y+=rowHeight;x=0;rowHeight=0;}
      group.forEach((id,i)=>{output[id]={x:p[i].x-minX+x+70,y:p[i].y-minY+y+70};});
      x+=w;rowHeight=max(rowHeight,h);
    }
    return output;
  }
  function adaptive(nodes,edges,options={}) {
    const insertionIds=[...new Set(nodes.map(n=>String(n.id)))];
    const ids=[...insertionIds].sort(compare),index=new Map(ids.map((id,i)=>[id,i]));
    const pairs=new Set();
    for(const e of edges){let a=index.get(String(e.source)),b=index.get(String(e.target));if(a===undefined||b===undefined||a===b)continue;if(a>b)[a,b]=[b,a];pairs.add(`${a},${b}`);}
    const links=[...pairs].sort().map(s=>s.split(',').map(Number));
    // Geometry is independent of weights, traversal flags and ordering. Reciprocal
    // arcs share the same underlying graph; the renderer separates their paths.
    const key=JSON.stringify([ids,links]);
    // Editing must not jump to an older arrangement of the same topology.
    // Playback explicitly opts into stored snapshots; unchanged frames are stable.
    let points=key===previousKey?ids.map(id=>previous.get(id)):
      options.replay===true?cache.get(key):null;
    if(!ids.length){
      if(options.replay!==true)cache.clear();
      previous.clear();previousPairs.clear();previousKey=key;
      if(options.replay===true)cache.set(key,[]);
      return new Map();
    }
    if(!points){
      const shared=ids.some(id=>previous.has(id));
      if(shared)points=grow(ids,links,previous);
      else if(ids.length>15){
        const order=new Map(insertionIds.map((id,i)=>[id,i]));
        const orderedLinks=links.map(([a,b])=>[order.get(ids[a]),order.get(ids[b])]);
        const placed=grow(insertionIds,orderedLinks,new Map());
        points=ids.map(id=>placed[order.get(id)]);
      }else points=compute(ids,links);
      if(cache.size>=64)cache.delete(cache.keys().next().value);cache.set(key,points);
    }
    previousKey=key;
    previous=new Map(ids.map((id,i)=>[id,{...points[i]}]));
    previousPairs=new Set(links.map(([a,b])=>[ids[a],ids[b]].sort(compare).join('\u0000')));
    const labels=new Map(nodes.map(node=>[String(node.id),node.label]));
    return new Map(ids.map((id,i)=>[id,{...points[i],label:labels.get(id)}]));
  }
  // A fresh C execution owns a fresh replay cache, but keeps the editing map.
  adaptive.beginExecution = () => {
    cache.clear();
    if(previousKey!==null)cache.set(previousKey,[...previous.keys()].sort(compare).map(id=>({...previous.get(id)})));
  };
  root.gAdaptiveGraphPositions=adaptive;
  if(typeof module!=='undefined'&&module.exports)module.exports={gAdaptiveGraphPositions:adaptive,gGraphLayoutMetrics:metrics};
})(typeof window!=='undefined'?window:globalThis);
