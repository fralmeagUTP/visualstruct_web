'use strict';
const fs=require('node:fs'),vm=require('node:vm'),test=require('node:test'),assert=require('node:assert/strict');
const source=fs.readFileSync('static/js/classroom_view.js','utf8');
function fixture(){
 class Node{
  constructor(tag='div'){this.tagName=tag.toUpperCase();this.children=[];this.style={setProperty(k,v){this[k]=v}};this.attrs={};this.listeners={};this.textContent='';this.scrollLeft=0;this.scrollTop=0;const set=new Set();this.classList={add:(...x)=>x.forEach(v=>set.add(v)),contains:x=>set.has(x),remove:x=>set.delete(x)};}
  append(...ns){ns.forEach(n=>{if(n.parentElement)n.parentElement.children=n.parentElement.children.filter(x=>x!==n);this.children.push(n);n.parentElement=this;});}
  prepend(n){this.append(n);this.children.unshift(this.children.pop());}
  insertBefore(n,old){this.append(n);this.children.pop();this.children.splice(Math.max(0,this.children.indexOf(old)),0,n);}
  before(n){this.parentElement.insertBefore(n,this);}
  get firstChild(){return this.children[0]||null;}
  setAttribute(k,v){this.attrs[k]=v;} getAttribute(k){return this.attrs[k]||null;}
  addEventListener(k,fn){this.listeners[k]=fn;}
  querySelectorAll(sel){return this.children.flatMap(n=>[...((sel==='svg'&&n.tagName==='SVG')||(sel.startsWith('.')&&n.classList.contains(sel.slice(1)))?[n]:[]),...n.querySelectorAll(sel)]);}
  querySelector(sel){return this.querySelectorAll(sel)[0]||null;}
  matches(sel){return sel==='svg'&&this.tagName==='SVG';}
 }
 Node.prototype.replaceWith=function(n){const p=this.parentElement,i=p.children.indexOf(this);if(n.parentElement)n.parentElement.children=n.parentElement.children.filter(x=>x!==n);p.children[i]=n;n.parentElement=p;this.parentElement=null;};
 Node.prototype.remove=function(){if(this.parentElement)this.parentElement.children=this.parentElement.children.filter(x=>x!==this);this.parentElement=null;};
 Node.prototype.focus=function(){this.focused=true;};Node.prototype.showModal=function(){this.open=true;};Node.prototype.close=function(){this.open=false;this.listeners.close?.();};
 const root=new Node(),visual=new Node(),stage=new Node(),svg=new Node('svg');svg.attrs.viewBox='-20 5 900 450';root.append(visual);visual.append(stage);stage.append(svg);
 let mutation;const copied=[];const document={body:new Node('body'),activeElement:new Node('button'),createComment:()=>new Node('comment'),createElement:t=>new Node(t),querySelector:()=>null};
 const ctx={window:{scrollX:10,scrollY:120,scrollTo(x,y){this.restored=[x,y]}},document,navigator:{clipboard:{writeText:async t=>copied.push(t)}},queueMicrotask:fn=>fn(),MutationObserver:class{constructor(fn){mutation=fn}observe(){}disconnect(){}}};
 vm.createContext(ctx);vm.runInContext(source,ctx);return{...ctx,root,visual,stage,svg,Node,copied,mutate:records=>mutation(records),api:ctx.window.ClassroomView};
}
test('mount starts natural size; zoom and local pan survive twenty redraw/back notifications',()=>{const f=fixture(),c=f.api.mount(f);assert.equal(f.svg.style.width,'900px');c.setZoom(1.4);f.stage.scrollLeft=130;f.stage.scrollTop=40;f.stage.listeners.scroll();for(let i=0;i<20;i++){f.svg.style.width='3px';f.mutate();assert.equal(f.svg.style.width,'1260px');assert.equal(f.stage.scrollLeft,130);assert.equal(f.stage.scrollTop,40);}assert.equal(f.svg.attrs.viewBox,'-20 5 900 450');assert.equal(f.api.mount(f),c);});
test('zoom is explicit bounded and never fitted to viewport',()=>{const f=fixture();assert.equal(f.api.clampZoom(.01),.5);assert.equal(f.api.clampZoom(9),2.5);assert.equal(f.api.clampZoom(1),1);});
test('copy preserves exact raw C bytes including empty lines and Unicode comments',async()=>{const f=fixture(),text='int main(void) {\n\n  /* á */\n  return 0;\n}\n';await f.api.copyText(f.api.sourceText({textContent:text}));assert.equal(f.copied[0],text);assert.ok(!f.copied[0].includes('\u00a0'));});
test('HTML visual zoom scales only diagram content, not auxiliary memory',()=>{const f=fixture();f.stage.children=[];const item=new f.Node(),memory=new f.Node();memory.classList.add('classroom-memory');f.stage.append(item,memory);const c=f.api.mount(f);c.setZoom(1.2);assert.equal(item.style.zoom,'1.2');assert.equal(memory.style.zoom,undefined);});
test('export clone opens memory and resets zoom without touching live state',()=>{const runtime=fs.readFileSync('static/js/interpreter_runtime.js','utf8');const a=runtime.indexOf('  function prepareClassroomExportClone('),b=runtime.indexOf('  function expandHierarchicalExportClone(',a);const ctx={};vm.createContext(ctx);vm.runInContext(runtime.slice(a,b)+';this.prepare=prepareClassroomExportClone',ctx);const live={open:false,style:{zoom:'1.7'}},memory={open:false,style:{zoom:'1.7'}},toolbar={removed:false,remove(){this.removed=true}},clone={style:{zoom:'1.7'},querySelectorAll:s=>s==='details.classroom-memory, details.classroom-memory details'?[memory]:s==='*'?[memory]:[toolbar]};ctx.prepare(clone);assert.equal(memory.open,true);assert.equal(memory.style.zoom,'1');assert.equal(toolbar.removed,true);assert.equal(live.open,false);assert.equal(live.style.zoom,'1.7');});

test('enlarge and close preserve same code node, raw text, focus and document position',()=>{const f=fixture(),panel=new f.Node('pre');panel.textContent='int x;\n';f.root.append(panel);f.api.enlarge(panel,'Código');const dialog=f.document.body.children[0];assert.equal(dialog.children[2],panel);dialog.close();assert.equal(f.root.children.at(-1),panel);assert.equal(panel.textContent,'int x;\n');assert.equal(f.document.activeElement.focused,true);assert.equal(JSON.stringify(f.window.restored),'[10,120]');assert.equal(f.document.body.children.length,0);});

test('rendered code lines retain blank lines; rawCode wins byte-exact including CRLF',()=>{const f=fixture();const rendered={textContent:'int main(void) {return 0;}',querySelectorAll:()=>[{textContent:'int main(void) {'},{textContent:''},{textContent:'  return 0;'},{textContent:'}'},{textContent:''}]};assert.equal(f.api.sourceText(rendered),'int main(void) {\n\n  return 0;\n}\n');rendered.dataset={rawCode:'int x;\r\n'};assert.equal(f.api.sourceText(rendered),'int x;\r\n');});

test('explicit fit bounds scale by measured font, never inventing readability',()=>{const f=fixture();let r=f.api.fitScale(784,400,665,367,20);assert.equal(r.zoom,.84);assert.equal(r.fits,true);assert.equal(r.readable,true);r=f.api.fitScale(2000,1000,650,350,20);assert.equal(r.zoom,.7);assert.equal(r.fits,false);assert.equal(r.readable,true);r=f.api.fitScale(1000,600,650,350,10);assert.equal(r.zoom,1.4);assert.equal(r.fits,false);assert.equal(r.readable,true);r=f.api.fitScale(1000,600,650,350,4);assert.equal(r.readable,false);});
test('fit is a user button, absent from mount refresh and redraw auto paths',()=>{const f=fixture();f.api.mount(f);const tool=f.visual.children[0];assert.ok(tool.children.some(n=>n.textContent==='Encajar vista'));assert.equal(f.svg.style.width,'900px');f.mutate();assert.equal(f.svg.style.width,'900px');});

test('auxiliary memory lives outside panned stage, replaces fresh frames and clears absent memory',()=>{const f=fixture(),first=new f.Node();first.classList.add('mem');f.stage.append(first);f.api.mount({...f,memory:['.mem']});let details=f.visual.children.at(-1);assert.equal(details.className,'classroom-memory');assert.equal(first.parentElement,details);assert.notEqual(details.parentElement,f.stage);details.open=true;details.listeners.toggle();for(let i=0;i<20;i++){const fresh=new f.Node();fresh.classList.add('mem');f.stage.append(fresh);f.mutate([{target:f.stage,addedNodes:[fresh],removedNodes:[]}]);assert.equal(details.children.length,2);assert.equal(details.children[1],fresh);assert.equal(details.open,true);}const newDrawing=new f.Node();f.stage.append(newDrawing);f.mutate([{target:f.stage,addedNodes:[newDrawing],removedNodes:[]}]);assert.equal(details.parentElement,null);});
test('expanded export preserves data bar sizes and overrides important viewport constraints only in clone',()=>{
 const helper=fs.readFileSync('qa/test_export_jpg_hierarchical.js','utf8');
 const runtime=fs.readFileSync('static/js/interpreter_runtime.js','utf8');
 const ctx={source:runtime,assert,vm};vm.createContext(ctx);
 vm.runInContext(helper.slice(helper.indexOf('function fixture('),helper.indexOf("test('expands"))+';this.make=fixture;',ctx);
 const f=ctx.make();const bar=new f.canvas.constructor();bar.style.width='93px';bar.style.height='11px';bar.matches=s=>s.includes('.sorting-item-bar');f.canvas.appendChild(bar);
 const priorities={};f.canvas.style.setProperty=(k,v,p)=>{f.canvas.style[k]=v;priorities[k]=p;};
 f.expand(f.root,400);assert.equal(bar.style.width,'93px');assert.equal(bar.style.height,'11px');assert.equal(priorities.overflow,'important');assert.equal(priorities.height,'important');assert.equal(f.body.children.length,0);
});
test('export materializes closed auxiliary details as a static block retaining all evidence',()=>{
 const runtime=fs.readFileSync('static/js/interpreter_runtime.js','utf8'),a=runtime.indexOf('  function prepareClassroomExportClone('),b=runtime.indexOf('  function expandHierarchicalExportClone(',a);
 const heading={textContent:'Memoria y reservas'},evidence={textContent:'estado buffer 8/2048'};let replacement;
 const details={attributes:[{name:'class',value:'classroom-memory'},{name:'style',value:'max-height:0px'}],children:[heading,evidence],get firstChild(){return this.children[0]},replaceWith(n){replacement=n;}};
 const clone={style:{},querySelectorAll:s=>s.startsWith('details.')?[details]:s==='*'?(replacement?[replacement]:[]):[]};
 const document={createElement:tag=>({tag,attrs:{},style:{},children:[],setAttribute(k,v){this.attrs[k]=v},appendChild(n){details.children.shift();this.children.push(n)}})};
 const ctx={document};vm.createContext(ctx);vm.runInContext(runtime.slice(a,b)+';this.prepare=prepareClassroomExportClone',ctx);ctx.prepare(clone);
 assert.equal(replacement.tag,'div');assert.equal(replacement.attrs.class,'classroom-memory');assert.equal(replacement.children[0],heading);assert.equal(replacement.children[1],evidence);assert.equal(replacement.style.zoom,'1');
});
