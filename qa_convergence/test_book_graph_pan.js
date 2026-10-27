const fs=require('node:fs'),vm=require('node:vm'),assert=require('node:assert/strict');const ctx=vm.createContext({document:{addEventListener(){}},window:{}});vm.runInContext(fs.readFileSync('static/js/graph.js','utf8'),ctx);
for(const count of [2,3,6,15]){
 const nodes=Array.from({length:count},(_,i)=>({id:String(i+1),label:String(i+1)})),edges=nodes.slice(1).map((n,i)=>({source:String(i+1),target:n.id,weight:1500000000}));
 const raw=ctx.renderGraphSvg({nodes,edges,directed:true},null,null),values=raw.match(/viewBox="([^"]+)"/)[1].split(' ').map(Number),box={width:values[2],height:values[3]};
 const svg={viewBox:{baseVal:box},getBoundingClientRect(){return {width:514.58,height:138.41};},style:{}};
 const stage={clientWidth:514.58,clientHeight:138.41,scrollLeft:0,scrollTop:0,classList:{toggle(name,value){stage.pan=value;}},querySelector(){return svg;},setAttribute(k,v){this[k]=v;}};
 const note={hidden:true},container={querySelector(q){return q==='.viz-stage'?stage:note;}};
 ctx.gMaintainGraphImageViewport(container,{left:37,top:88});
 const expected=Math.min(514.58/box.width,138.41/box.height)<.9;assert.equal(stage.pan,expected);assert.equal(note.hidden,!expected);
 if(expected){assert(parseFloat(svg.style.width)>=box.width);assert(parseFloat(svg.style.height)>=box.height);assert.equal(stage.scrollLeft,37);assert.equal(stage.scrollTop,88);assert.equal(stage.tabindex,'0');assert.match(stage['aria-label'],/código permanece fijo/);}
}
const source=fs.readFileSync('static/js/graph.js','utf8');assert(source.includes('gMaintainGraphImageViewport(container,imageViewport)'));assert(source.includes('left:oldStage?.scrollLeft||0,top:oldStage?.scrollTop||0'));
console.log('PASS 2/3/6/15 geometry: image-only pan below legible scale, >=1:1 glyphs, previous pan retained, keyboard access; pixel UI remains separate');
