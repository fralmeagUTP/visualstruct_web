'use strict';
const fs=require('node:fs'),vm=require('node:vm'),test=require('node:test'),assert=require('node:assert/strict');
const source=fs.readFileSync('static/js/classroom_view.js','utf8');
function fixture(){
 const autoMutations=arguments[0] || false;
 const pendingRecords=[], microtasks=[], observed=[];
 function record(target,addedNodes,removedNodes){
  if(!autoMutations)return;
  if(observed.some(root=>{for(let n=target;n;n=n.parentElement)if(n===root)return true;return false;})) pendingRecords.push({target,addedNodes,removedNodes});
 }
 class Node{
  constructor(tag='div'){this.tagName=tag.toUpperCase();this.children=[];this.style={setProperty(k,v){this[k]=v}};this.attrs={};this.listeners={};this.textContent='';this.scrollLeft=0;this.scrollTop=0;const set=new Set();this.classList={add:(...x)=>x.forEach(v=>set.add(v)),contains:x=>set.has(x),remove:x=>set.delete(x)};}
  append(...ns){ns.forEach(n=>{if(n.parentElement){const old=n.parentElement;old.children=old.children.filter(x=>x!==n);record(old,[],[n]);}this.children.push(n);n.parentElement=this;record(this,[n],[]);});}
  prepend(n){this.append(n);this.children.unshift(this.children.pop());}
  insertBefore(n,old){this.append(n);this.children.pop();this.children.splice(Math.max(0,this.children.indexOf(old)),0,n);}
  before(n){this.parentElement.insertBefore(n,this);}
  after(n){const p=this.parentElement;p.append(n);p.children.pop();p.children.splice(p.children.indexOf(this)+1,0,n);}
  replaceChildren(...ns){const old=[...this.children];for(const n of old)n.parentElement=null;this.children=[];if(old.length)record(this,[],old);this.append(...ns);}
  get firstChild(){return this.children[0]||null;}
  setAttribute(k,v){this.attrs[k]=v;} getAttribute(k){return this.attrs[k]||null;}
  addEventListener(k,fn){this.listeners[k]=fn;}
  querySelectorAll(sel){const selectors=sel.split(',').map(s=>s.trim());return this.children.flatMap(n=>[...(selectors.some(s=>(s==='svg'&&n.tagName==='SVG')||(s.startsWith('.')&&n.classList.contains(s.slice(1))))?[n]:[]),...n.querySelectorAll(sel)]);}
  querySelector(sel){return this.querySelectorAll(sel)[0]||null;}
  matches(sel){return sel==='svg'&&this.tagName==='SVG';}
 }
 Node.prototype.replaceWith=function(n){const p=this.parentElement,i=p.children.indexOf(this);if(n.parentElement)n.parentElement.children=n.parentElement.children.filter(x=>x!==n);p.children[i]=n;n.parentElement=p;this.parentElement=null;};
 Node.prototype.remove=function(){if(this.parentElement)this.parentElement.children=this.parentElement.children.filter(x=>x!==this);this.parentElement=null;};
 Node.prototype.focus=function(){this.focused=true;};Node.prototype.showModal=function(){this.open=true;};Node.prototype.close=function(){this.open=false;this.listeners.close?.();};
 const root=new Node(),visual=new Node(),stage=new Node(),svg=new Node('svg');svg.attrs.viewBox='-20 5 900 450';root.append(visual);visual.append(stage);stage.append(svg);
 let mutation;const copied=[];const document={body:new Node('body'),activeElement:new Node('button'),createComment:()=>new Node('comment'),createElement:t=>new Node(t),querySelector:()=>null};
 const ctx={window:{scrollX:10,scrollY:120,scrollTo(x,y){this.restored=[x,y]}},document,navigator:{clipboard:{writeText:async t=>copied.push(t)}},queueMicrotask:fn=>autoMutations?microtasks.push(fn):fn(),MutationObserver:class{constructor(fn){mutation=fn}observe(node){observed.push(node)}disconnect(){observed.length=0}}};
 vm.createContext(ctx);vm.runInContext(source,ctx);return{...ctx,root,visual,stage,svg,Node,copied,mutate:records=>mutation(records),flush:()=>{let turns=0;while(pendingRecords.length||microtasks.length){assert.ok(++turns<50,'observer must settle');if(pendingRecords.length)mutation(pendingRecords.splice(0));while(microtasks.length)microtasks.shift()();}},api:ctx.window.ClassroomView};
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

test('auxiliary memory lives outside panned stage, replaces fresh frames and clears absent memory',()=>{const f=fixture(),first=new f.Node();first.classList.add('mem');f.stage.append(first);f.api.mount({...f,memory:['.mem']});let details=f.visual.children.at(-1);assert.equal(details.className,'classroom-memory didactic-technical');assert.equal(first.parentElement,details);assert.notEqual(details.parentElement,f.stage);details.open=true;details.listeners.toggle();for(let i=0;i<20;i++){const fresh=new f.Node();fresh.classList.add('mem');f.stage.append(fresh);f.mutate([{target:f.stage,addedNodes:[fresh],removedNodes:[]}]);assert.equal(details.children.length,2);assert.equal(details.children[1],fresh);assert.equal(details.open,true);}const newDrawing=new f.Node();f.stage.append(newDrawing);f.mutate([{target:f.stage,addedNodes:[newDrawing],removedNodes:[]}]);assert.equal(details.parentElement,null);});
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

test('inline operation results share the visual panel without its zoom/pan, preserve nodes, and clear on reset',()=>{
 for(const cls of ['viz-out','hier-traversal-summary','hier-current-result']) {
  const f=fixture(),r=new f.Node(cls.includes('summary')?'details':'p');r.classList.add(cls);r.textContent=Array.from({length:30},(_,i)=>i+1).join(' -> ');r.open=true;f.stage.append(r);
  const c=f.api.mount(f),panel=f.visual.children.find(n=>n.className==='classroom-inline-results');
  assert.equal(r.parentElement,panel);assert.equal(panel.parentElement,f.visual);assert.equal(panel.children.length,1);assert.equal(r.textContent.endsWith('30'),true);assert.equal(r.open,true);
  c.setZoom(1.5);assert.equal(r.style.zoom,undefined);f.stage.scrollLeft=99;f.stage.listeners.scroll();
  const next=new f.Node('p');next.classList.add(cls);next.textContent='Segundo resultado';f.stage.append(next);f.mutate([{target:f.stage,addedNodes:[next],removedNodes:[]}]);
  assert.equal(panel.children.length,1);assert.equal(panel.children[0],next);assert.equal(f.stage.scrollLeft,99);
  f.mutate([{target:f.stage,addedNodes:[f.svg],removedNodes:[]}]);assert.equal(panel.children.length,0);assert.equal(panel.hidden,true);
 }
});
test('printf panels across all families grow naturally; C source readers retain scrolling',()=>{
 for(const key of ['graph','hierarchical','sequential','hash','sorting']) {
  const f=fixture(),panel=new f.Node('section'),out=new f.Node('pre');out.textContent='Salida larga\n'.repeat(100);panel.append(out);f.root.append(panel);
  f.api.mount({...f,key,results:[{label:'Consola C (printf)',panel,code:out,getText:()=>out.textContent}]});
  assert.ok(panel.classList.contains('classroom-output-panel'));assert.ok(!out.classList.contains('classroom-code-scroll'));assert.equal(out.textContent.split('\n').length,101);
 }
 const css=fs.readFileSync('static/css/classroom_view.css','utf8');
 assert.match(css,/\.classroom-output-panel\s*\{\s*height: auto; max-height: none; overflow: visible/);
 assert.match(css,/\.classroom-inline-results\s*\{[\s\S]*?height: auto; max-height: none; overflow: visible/);
 assert.match(css,/\.classroom-code-scroll\s*\{[\s\S]*?overflow-x: auto !important; overflow-y: auto !important/);
});
test('moved results remain hidden for all existing concealed practice-stage classes',()=>{
 const css=fs.readFileSync('static/css/classroom_view.css','utf8');
 for(const cls of ['graph-practice-hidden','hier-practice-hidden','seq-practice-hidden'])
  assert.ok(css.includes(`.classroom-visual:has(> .${cls}) > .classroom-inline-results`));
 assert.match(css,/\.classroom-visual:has\(> \.seq-practice-hidden\) > \.classroom-inline-results\s*\{\s*display: none !important/);
});

// Deliver mutations produced by DOM transfers themselves, not just renderer notifications.
test('observer delivery after direct and nested result transfers preserves output and real resets',()=>{
 for(const nested of [false,true])for(const cls of ['viz-out','hier-traversal-summary','hier-current-result']){
  const f=fixture(true),r=new f.Node();r.classList.add(cls);r.textContent='Complete result';
  const wrapper=new f.Node();if(nested){wrapper.append(r);f.stage.append(wrapper);}else f.stage.append(r);
  f.api.mount(f);f.flush();
  const panel=f.visual.children.find(n=>n.className==='classroom-inline-results');
  assert.equal(panel.children[0],r);assert.equal(panel.hidden,false);
  // A second renderer frame, followed by its own observer transfer delivery.
  const next=new f.Node();next.classList.add(cls);next.textContent='Replacement';
  const frame=new f.Node();frame.append(new f.Node('svg'));if(nested)frame.append(next);
  f.stage.replaceChildren(frame,...(nested?[]:[next]));f.flush();
  assert.equal(panel.children.length,1);assert.equal(panel.children[0],next);assert.equal(panel.hidden,false);
  f.stage.replaceChildren(new f.Node('svg'));f.flush();
  assert.equal(panel.children.length,0);assert.equal(panel.hidden,true);
 }
});
