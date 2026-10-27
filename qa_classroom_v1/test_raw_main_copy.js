const fs=require('fs'),vm=require('vm'),assert=require('assert'),path=require('path');
const fixtures=JSON.parse(fs.readFileSync('../qa_frontend_main/fixtures.json','utf8'));
const context=vm.createContext({window:{},document:{addEventListener(){}},console});
for(const name of ['sequential','hierarchical'])vm.runInContext(fs.readFileSync(`static/js/${name}.js`,'utf8'),context);
fs.mkdirSync('qa_classroom_v1/raw_main',{recursive:true});
for(const test of fixtures){
 const {id,module,model,operations}=test,container={dataset:{},innerHTML:''};
 if(module==='sequential'){
  const catalog=new Map(model.operations.map(o=>[o.name,o]));
  const history=operations.map(o=>context.createHistoryEntry(context.getSubroutineName(model,o.name,o.name),'',o.message,o.name,o.payload));
  context.renderActionHistory(history,container,id,catalog);
 }else{
  const history=operations.map(o=>context.createHierHistoryEntry(context.getHierSubroutineName(model,o.name,o.name),'',o.message,o.name,o.payload));
  context.renderHierHistory(history,container,id,model.didactic);
  assert.strictEqual(container.dataset.rawCode,context.buildHierMainCode(id,history,model.didactic));
 }
 const raw=container.dataset.rawCode;assert(raw.startsWith('#include'));assert(!raw.includes('\u00a0'));assert(raw.includes('\n\n'));
 fs.writeFileSync(`qa_classroom_v1/raw_main/${id}.c`,raw);
}
console.log('PASS 9 main copy sources preserve real newlines, includes and blank lines, no NBSP');
