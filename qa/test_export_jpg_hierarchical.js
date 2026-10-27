'use strict';
const fs=require('node:fs'),vm=require('node:vm'),test=require('node:test'),assert=require('node:assert/strict');
const source=fs.readFileSync(process.argv[2]||'static/js/interpreter_runtime.js','utf8');
function fixture(throwMeasure=false, viewBox="0 0 900 500"){
 const all=[];let mounted=false;
 class HTMLElement{
  constructor(tag='div',rect={left:0,top:0,right:400,bottom:200,width:400,height:200}){this.tagName=tag;this.style={};this.rect=rect;this.children=[];this.scrollWidth=400;this.scrollHeight=200;this.attrs={};all.push(this);}
  appendChild(n){this.children.push(n);n.parent=this;}
  remove(){if(this.parent)this.parent.children=this.parent.children.filter(x=>x!==this);this.parent=null;}
  querySelectorAll(){return this.children.flatMap(c=>[c,...c.querySelectorAll()]);}
  getBoundingClientRect(){assert.ok(mounted,'measure detached clone');if(throwMeasure)throw Error('layout failure');return this.rect;}
  setAttribute(k,v){this.attrs[k]=v;}
 }
 const root=new HTMLElement(),canvas=new HTMLElement();root.appendChild(canvas);root.scrollHeight=520;
 const svg={tagName:'svg',style:{height:'100%',maxHeight:'100%'},getAttribute:()=> viewBox,querySelectorAll:()=>[],getBoundingClientRect:()=>({right:920,bottom:540}),remove(){}};canvas.appendChild(svg);
 const memory=new HTMLElement('div',{left:0,top:540,right:940,bottom:860,width:940,height:320});root.appendChild(memory);
 const body=new HTMLElement();body.appendChild=function(n){mounted=true;this.children.push(n);n.parent=this;};
 const document={body,createElement:()=>new HTMLElement()};
 const begin=source.indexOf('  function expandHierarchicalExportClone('),end=source.indexOf('  async function exportVisualStateAsJpg(',begin);
 assert.ok(begin>=0,'missing clone expansion');const ctx={document,HTMLElement};vm.createContext(ctx);vm.runInContext(source.slice(begin,end)+';this.expand=expandHierarchicalExportClone',ctx);
 return{root,canvas,svg,memory,body,expand:ctx.expand};
}
test('expands only detached descendants and measures content beyond original viewport',()=>{const f=fixture(),r=f.expand(f.root,400);assert.equal(r.width,948);assert.equal(r.height,860);assert.equal(f.svg.style.width,'900px');assert.equal(f.svg.style.height,'500px');assert.equal(f.canvas.style.overflow,'visible');assert.equal(f.memory.style.height,'auto');assert.equal(f.body.children.length,0);assert.equal(f.root.parent,null);});
test('temporary measurement DOM always removed on layout failure',()=>{const f=fixture(true);assert.throws(()=>f.expand(f.root,400),/layout failure/);assert.equal(f.body.children.length,0);assert.equal(f.root.parent,null);});
test('hierarchical expansion is scoped to region and descendant target, not other families',()=>{assert.match(source,/target\.id === "hier-visual-region" \|\| target\.closest\?\.\("#hier-visual-region"\)/);assert.match(source,/\(\{ width, height \} = expandHierarchicalExportClone\(cloned, width\)\)/);});

test('nonzero SVG viewBox origin stays intact while width/height are restored',()=>{const f=fixture(false,"-120 45 900 500");f.expand(f.root,400);assert.equal(f.svg.getAttribute("viewBox"),"-120 45 900 500");assert.equal(f.svg.style.width,"900px");assert.equal(f.svg.style.height,"500px");});
