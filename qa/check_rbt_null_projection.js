/* Actual RN renderer and ClassroomView in jsdom. No pixel/layout certification. */
'use strict';
const fs=require('node:fs'),vm=require('node:vm'),assert=require('node:assert/strict'),{JSDOM}=require('jsdom');
const input=JSON.parse(fs.readFileSync(process.argv[2],'utf8'));
(async()=>{
 const dom=new JSDOM('<main id="root"><div id="region"><div id="visual"></div></div></main>',{runScripts:'outside-only'}),w=dom.window,ctx=dom.getInternalVMContext();
 try{
  for(const f of ['static/js/hierarchical.js','static/js/classroom_view.js'])vm.runInContext(fs.readFileSync(f,'utf8'),ctx);
  const d=w.document,box=d.getElementById('visual');const ui=w.ClassroomView.mount({root:'#root',visual:'#region',stage:'#visual',memory:['.abb-instruction-memory','.hier-retired-memory']});
  let frames=0,maxCircles=0,collisions=[],controlsSet=false;
  for(const entry of input){
   const state=entry.state,before=JSON.stringify(state);w.renderHierState('red_black',state,box);await Promise.resolve();await Promise.resolve();
   if(process.argv[3]==='omit-null')d.querySelector('.viz-tree-node.nil')?.remove();
   if(process.argv[3]==='invent-null'){const node=d.querySelector('.viz-tree-node.nil');if(node)node.after(node.cloneNode(true));}
   if(process.argv[3]==='drop-node')d.querySelector('[data-rbt-svg-node]')?.remove();
   if(process.argv[3]==='duplicate-edge'){const edge=d.querySelector('[data-rbt-svg-from]');if(edge)edge.after(edge.cloneNode(true));}
   if(process.argv[3]==='repoint-card')d.querySelector('[data-abb-node]').dataset.abbLeft='FORGED';
   assert.equal(JSON.stringify(state),before,'renderer cannot alter state');
   const cards=[...d.querySelectorAll('[data-abb-node]')],svg=[...d.querySelectorAll('[data-rbt-svg-node]')];
   assert.equal(cards.length,state.heap_nodes.length);assert.equal(svg.length,state.heap_nodes.length);
   const live=new Set(state.heap_nodes.map(n=>n.id));assert.equal(live.size,state.heap_nodes.length);
   const edges=state.heap_nodes.flatMap(n=>['left','right'].filter(side=>live.has(n[side])||n[side]==='NULL').map(side=>({from:n.id,to:n[side],side})));
   const observed=[...d.querySelectorAll('[data-rbt-svg-from]')].map(n=>({from:n.dataset.rbtSvgFrom,to:n.dataset.rbtSvgTo,side:n.dataset.rbtSvgSide}));
   const sorted=xs=>xs.map(x=>JSON.stringify(x)).sort();assert.deepEqual(sorted(observed),sorted(edges),entry.label);
   assert.equal(d.querySelectorAll('.viz-tree-node.nil').length,edges.filter(e=>e.to==='NULL').length);
   const nullByPoint=new Map();
   for(const node of d.querySelectorAll('.viz-tree-node.nil')){const point=node.getAttribute('cx')+','+node.getAttribute('cy');if(!nullByPoint.has(point))nullByPoint.set(point,[]);nullByPoint.get(point).push(node);}
   for(const edge of d.querySelectorAll('[data-rbt-svg-to="NULL"]')){
    const leaves=nullByPoint.get(edge.getAttribute('x2')+','+(+edge.getAttribute('y2')+14))||[];
    assert.equal(leaves.length,1,'each NULL link ends at one explicit NULL marker');
    assert.equal(leaves[0].nextElementSibling.textContent,'NULL');
   }
   assert.equal(d.querySelectorAll('[data-abb-node="NULL"]').length,0,'NULL is not an allocated object');
   const cardMap=new Map(cards.map(e=>[e.dataset.abbNode,e])),svgMap=new Map(svg.map(e=>[e.dataset.rbtSvgNode,e]));
   assert.equal(cardMap.size,cards.length);assert.equal(svgMap.size,svg.length);
   for(const n of state.heap_nodes){
    const card=[cardMap.get(n.id)],node=[svgMap.get(n.id)];assert.ok(card[0]&&node[0]);
    for(const side of ['left','right'])assert.equal(card[0].dataset['abb'+side[0].toUpperCase()+side.slice(1)],String(n[side]));
    assert.equal(node[0].dataset.rbtSvgColor,n.color);assert.equal(node[0].dataset.rbtSvgParent,n.parent);
   }
   const drawing=d.querySelector('svg'),circles=[...d.querySelectorAll('circle.viz-tree-node')].map(e=>({x:+e.getAttribute('cx'),y:+e.getAttribute('cy'),r:+e.getAttribute('r')}));
   if(drawing){
    const [x,y,width,height]=drawing.getAttribute('viewBox').split(/\s+/).map(Number);assert.ok([x,y,width,height].every(Number.isFinite)&&width>0&&height>0);
    for(const c of circles)assert.ok(c.x-c.r>=x&&c.x+c.r<=x+width&&c.y-c.r>=y&&c.y+c.r<=y+height,'all circles included in viewBox');
    for(let a=0;a<circles.length;a++)for(let b=0;b<a;b++)if(Math.hypot(circles[a].x-circles[b].x,circles[a].y-circles[b].y)<circles[a].r+circles[b].r)collisions.push({label:entry.label,a,b});
    // One real public zoom/scroll choice must survive every subsequent frame.
    if(!controlsSet){controlsSet=true;
     const plus=[...d.querySelectorAll('.classroom-view-tools button')].find(e=>e.textContent==='+');plus.click();
     box.scrollLeft=73;box.scrollTop=41;box.dispatchEvent(new w.Event('scroll'));
    }
    assert.equal(ui.getState().zoom,1.1);assert.equal(ui.getState().panX,73);assert.equal(ui.getState().panY,41);assert.equal(box.scrollLeft,73);assert.equal(box.scrollTop,41);
    if(entry===input.at(-1)){
     const reset=[...d.querySelectorAll('.classroom-view-tools button')].find(e=>e.textContent==='100%');reset.click();assert.equal(ui.getState().zoom,1);
    }
    assert.deepEqual(sorted([...d.querySelectorAll('[data-rbt-svg-from]')].map(n=>({from:n.dataset.rbtSvgFrom,to:n.dataset.rbtSvgTo,side:n.dataset.rbtSvgSide}))),sorted(edges));
   }
   maxCircles=Math.max(maxCircles,circles.length);frames++;
  }
  process.stdout.write(JSON.stringify({frames,maxCircles,collisions}));
 }finally{w.close();}
})().catch(e=>{console.error(e);process.exitCode=1;});
