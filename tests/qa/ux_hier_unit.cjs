/* Finite non-browser UX checks. Geometry assertions do not certify rendered glyphs. */
const fs = require('node:fs'), vm = require('node:vm'), assert = require('node:assert/strict');
const source = fs.readFileSync('static/js/hierarchical.js', 'utf8');
const elements = {};
const context = vm.createContext({window:{},document:{addEventListener(){},getElementById:id=>elements[id]}});
vm.runInContext(source, context);
elements['hier-level-guide'] = {textContent:''};
for (const structure of ['abb','avl','red_black','binary_heap']) {
  context.window.HIER_VIEW_MODEL = {id:structure};
  const guides = [];
  for (const level of ['basic','intermediate','advanced']) {
    context.renderHierPedagogy(null,level); // Works before any trace exists.
    guides.push(elements['hier-level-guide'].textContent);
  }
  assert.equal(new Set(guides).size,3);
  assert(guides.every(text=>text.length>80));
}
const fixtures = JSON.parse(fs.readFileSync('qa/hier_prediction_fixtures.json','utf8'));
let count = 0;
const checkGeometry = state => {
  const before = JSON.stringify(state), layout = context.layoutHierMemoryGraph(state);
  const svg = context.drawTreeSvgFromNodes(layout.graph,{fitBounds:true,avlInsertionMemory:true,showBalanceFactor:true});
  assert.equal(JSON.stringify(state),before);
  if (!layout.graph.length) return;
  const [x,y,w,h] = svg.match(/viewBox="([^"]+)"/)[1].split(/\s+/).map(Number);
  const cards = [...svg.matchAll(/<rect x="([^"]+)" y="([^"]+)" width="144" height="40"/g)].map(m=>({x:+m[1],y:+m[2]}));
  assert.equal(cards.length,layout.graph.length);
  for (const card of cards) {
    assert(card.x>=x && card.x+144<=x+w,'annotation card fits horizontal viewBox');
    assert(card.y>=y && card.y+40<=y+h,'annotation card fits vertical viewBox');
  }
  for (let i=0;i<cards.length;i++) for (let j=i+1;j<cards.length;j++) {
    const a=cards[i],b=cards[j];
    assert(!(a.x<b.x+144 && a.x+144>b.x && a.y<b.y+40 && a.y+40>b.y),'annotation boxes stay separate');
  }
  for (const match of svg.matchAll(/<text x="([^"]+)" y="([^"]+)"[^>]*class="viz-tree-fe/g)) assert(+match[2]+5<=y+h,'FE baseline stays inside viewBox');
  count++;
};
for (const item of fixtures.filter(x=>x.structure==='avl')) for (const step of item.trace.steps) {
  const state = step.pedagogy?.memory_state;
  if (state?.avl_insert_model || state?.avl_delete_model) checkGeometry(state);
}
// Include asymmetric, disconnected and cyclic memory graphs with multi-digit values.
const leaf=(id,left='NULL',right='NULL')=>({id,value:123456,left,right,parent:'N12',balance_factor:0});
for (const state of [
  {head:'N1',heap_nodes:[leaf('N1','N2'),leaf('N2','N3'),leaf('N3')]},
  {head:'N1',heap_nodes:[leaf('N1','N1'),leaf('N2'),leaf('N3'),leaf('N4'),leaf('N5')]},
  {head:'NULL',heap_nodes:[leaf('N1'),leaf('N2')]},
]) checkGeometry({...state,avl_insert_model:true});
const container={innerHTML:''};
context.renderHierState('avl',{title:'AVL',size:0,root:null,traversals:{}},container);
assert.match(container.innerHTML,/hier-traversal-empty/);
assert.match(container.innerHTML,/enlaces transitorios/);
context.renderHierState('avl',{title:'AVL',size:1,root:{value:10},traversals:{inorden:[10]}},container);
assert.match(container.innerHTML,/inorden/);assert.doesNotMatch(container.innerHTML,/hier-traversal-empty/);
// Execute the actual message selection fragments, not duplicate their logic.
const start=source.indexOf('      const hasExecutionTrace = Boolean(!finalOnly');
const end=source.indexOf('      window.ConsoleHistory?.setHistory',start);
const messages=[];
Object.assign(context,{tracePlayer:{},data:{execution_trace:{steps:[{},{}]},success:true,message:'Se insertó 25.'},current:{name:'insertar'},pageState:{modelId:'abb'},consoleState:{},showHierMessage:(text,success)=>messages.push({text,success})});
for(const finalOnly of [false,true]) {
  context.finalOnly=finalOnly;
  vm.runInContext('{'+source.slice(start,end)+'}',context);
  assert.equal(context.consoleState.resultMessage!==null,!finalOnly);
  assert.match(messages.at(-1).text,finalOnly?/Se insertó/:/resultado pendiente/);
}
context.finalOnly=false;vm.runInContext('{'+source.slice(start,end)+'}',context);
const cursorStart=source.indexOf('        if (consoleState.resultMessage) {');
const cursorEnd=source.indexOf('        if (pageState.traceAtEnd) {',cursorStart);
for(const atEnd of [false,true,false]) {
  context.pageState.traceAtEnd=atEnd;vm.runInContext(source.slice(cursorStart,cursorEnd),context);
  assert.match(messages.at(-1).text,atEnd?/Se insertó/:/resultado pendiente/);
}
console.log(`PASS UX: four level guides before trace; ${count} AVL geometry states; traversal empty/final; ABB prepared/final/backward/fast messages. Not a browser visual certification.`);
