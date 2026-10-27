/* Extract the actual UI main builders without running the browser UI. */
const fs=require('node:fs'),vm=require('node:vm'),path=require('node:path');
const root=process.argv[2]||'.', fixture=JSON.parse(fs.readFileSync(process.argv[3],'utf8')),out=process.argv[4];fs.mkdirSync(out,{recursive:true});
const context=vm.createContext({window:{},document:{addEventListener(){}},console});
for(const f of ['sequential','hierarchical']) vm.runInContext(fs.readFileSync(path.join(root,`static/js/${f}.js`),'utf8'),context);
// Leave code generation intact; bypass only syntax-coloring markup for text capture.
context.highlightCLine=(line,state)=>({html:line.replaceAll('&','&amp;').replaceAll('<','&lt;').replaceAll('>','&gt;'),state});
for(const test of fixture){
 const {id,module,model,operations}=test;
 let source;
 if(module==='sequential'){
  const catalog=new Map(model.operations.map(o=>[o.name,o]));
  const history=operations.map(o=>context.createHistoryEntry(context.getSubroutineName(model,o.name,o.name),Object.entries(o.payload).map(([k,v])=>`${k}=${v}`).join(','),o.message,o.name,o.payload));
  const container={dataset:{},innerHTML:''};context.renderActionHistory(history,container,id,catalog);
  source=[...container.innerHTML.matchAll(/<span class="code-line" data-line="\d+">([\s\S]*?)<\/span>/g)].map(m=>m[1].replaceAll('&lt;','<').replaceAll('&gt;','>').replaceAll('&amp;','&')).join('\n');
 }else{
  const history=operations.map(o=>context.createHierHistoryEntry(context.getHierSubroutineName(model,o.name,o.name),'',o.message,o.name,o.payload));
  source=context.buildHierMainCode(id,history,model.didactic);
 }
 fs.writeFileSync(path.join(out,`${test.case_name || id}.c`),source+'\n');
}
