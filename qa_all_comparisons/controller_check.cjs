/* Runs the actual comparison controller with a minimal DOM and controlled fetch.
   It does not claim browser layout, SVG rendering or accessibility coverage. */
const fs=require('node:fs'),path=require('node:path'),vm=require('node:vm'),assert=require('node:assert/strict');
class Element {
  constructor(value=''){this.value=value;this.max='0';this.disabled=false;this.dataset={};this.listeners={};this.attributes={};this.textContent='';this.innerHTML='';}
  addEventListener(event,callback){(this.listeners[event] ||= []).push(callback);}
  setAttribute(name,value){this.attributes[name]=value;}
  removeAttribute(name){delete this.attributes[name];}
  async emit(event){for(const callback of this.listeners[event]||[]) await callback();}
}
const ids=['hier-compare-prev','hier-compare-next','hier-compare-position-label'];
const els=Object.fromEntries(ids.map(id=>[id,new Element()]));
const env={AbortController,console,compareSection:new Element(),compareKind:new Element('abb-all'),compareValues:new Element('9, 3, 7'),compareRun:new Element(),compareProgress:new Element(),compareInput:new Element(),compareGrid:new Element(),compareConclusion:new Element(),announcer:new Element(),hierarchicalComparison:null,hById:id=>els[id],hEscape:String,
  renderHierComparisonState:(side,step)=>`[${side.structure}:${step.step}:${step.inserted}]`,renderHierComparisonShape:()=>({html:'<shape>'})};
env.compareSection.dataset.compareUrl='/hierarchical/compare';
const idsByAlias={abb:'abb',avl:'avl','red-black':'red_black',heap:'binary_heap'};
const cases=[];for(const [alias,id] of Object.entries(idsByAlias)){
 for(const [other,otherId] of Object.entries(idsByAlias))if(other!==alias) cases.push([alias+'-'+other,[id,otherId]]);
 cases.push([alias+'-all',[id,...Object.values(idsByAlias).filter(other=>other!==id)]]);
}
function response(kind,selected=['abb','avl'],values=[9,3,7]){
 const sides=selected.map(structure=>({structure,timeline:values.map((inserted,index)=>({step:index+1,inserted,state:{}}))}));
 return {ok:true,json:async()=>({success:true,kind,input:values,sides,conclusion:'test'})};
}
let calls=0,pending;
env.fetch=async(url,request)=>{calls++;const {kind,values}=JSON.parse(request.body);return response(kind,cases.find(row=>row[0]===kind)?.[1],values);};
const source=fs.readFileSync(path.resolve(__dirname,'../static/js/hierarchical.js'),'utf8');
const block=source.slice(source.indexOf('  let comparisonRequestVersion ='),source.indexOf('  exportImage?.addEventListener',source.indexOf('  let comparisonRequestVersion =')));
vm.runInNewContext(block,env);
(async()=>{
 for(const [kind,selected] of cases){
  env.compareKind.value=kind;await env.compareKind.emit('change');await env.compareRun.emit('click');
  assert.equal(env.compareProgress.max,'2');assert.equal(env.compareProgress.value,'0');assert.equal(els['hier-compare-prev'].disabled,true);
  const initial=env.compareGrid.innerHTML;for(const id of selected) assert(initial.includes(`[${id}:1:9]`));
  const n=calls;await els['hier-compare-next'].emit('click');for(const id of selected) assert(env.compareGrid.innerHTML.includes(`[${id}:2:3]`));
  await els['hier-compare-prev'].emit('click');assert.equal(env.compareGrid.innerHTML,initial);assert.equal(calls,n);
 }
 env.fetch=async()=>({ok:true,json:async()=>({kind:'traversals',success:true,input:[1],state:{},traversals:[{name:'inorden',stack_rule:'left first',values:[1]}],conclusion:'test'})});
 await env.compareRun.emit('click');assert(env.compareGrid.innerHTML.startsWith('<shape>'));assert.equal(els['hier-compare-next'].disabled,true);
 // Retain an in-flight response without implementing abort to test the version guard independently.
 env.fetch=()=>{calls++;return new Promise(resolve=>{pending=resolve;});};
 const old=env.compareRun.emit('click');assert.equal(env.compareRun.disabled,true);const n=calls;
 await env.compareRun.emit('click');assert.equal(calls,n);
 env.compareKind.value='heap-all';await env.compareKind.emit('change');assert.equal(env.compareRun.disabled,false);assert.equal(env.hierarchicalComparison,null);
 pending(response('abb-avl'));await old;assert.equal(env.hierarchicalComparison,null);assert(!env.compareGrid.innerHTML.includes('[abb:'));
 const oldInput=env.compareRun.emit('click');env.compareValues.value='8';await env.compareValues.emit('input');pending(response('heap-all'));await oldInput;assert.equal(env.hierarchicalComparison,null);
 // A late old error cannot clear or re-enable controls owned by a newer request.
 const first=env.compareRun.emit('click'),resolveFirst=pending;await env.compareKind.emit('change');const second=env.compareRun.emit('click'),resolveSecond=pending;
 resolveFirst({ok:false,json:async()=>({success:false,message:'old error'})});await first;assert.equal(env.compareRun.disabled,true);assert.equal(env.compareConclusion.textContent,'');
 resolveSecond(response('heap-all',['binary_heap','abb','avl','red_black'],[8]));await second;assert.equal(env.compareRun.disabled,false);assert.equal(els['hier-compare-next'].disabled,true);
 env.fetch=async()=>({ok:false,json:async()=>({success:false,message:'Entrada no válida'})});await env.compareRun.emit('click');
 assert.equal(env.compareConclusion.textContent,'Entrada no válida');assert.equal(env.compareInput.textContent,'');assert.equal(env.hierarchicalComparison,null);assert.equal(els['hier-compare-next'].disabled,true);assert.equal(env.compareRun.disabled,false);
 console.log('PASS: 16 comparison modes, cached navigation, traversal, invalidation, repeated clicks, response races and error recovery.');
})().catch(error=>{console.error(error);process.exitCode=1;});
