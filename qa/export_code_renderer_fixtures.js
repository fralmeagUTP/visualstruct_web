const fs=require('node:fs'),vm=require('node:vm');const c=vm.createContext({window:{},document:{readyState:'loading',addEventListener(){}}});for(const file of ['sequential','hierarchical','graph','help_code_highlight','interpreter_runtime'])vm.runInContext(fs.readFileSync(`static/js/${file}.js`,'utf8'),c);
const raw='#include <stdio.h>\n\n#define SUM(a,b) \\\n  ((a) + (b))\n\nint main(void) {\n  return SUM(1,2) == 3 ? 0 : 1;\n}\n';
const results=[];function pre(){return {dataset:{},innerHTML:'',textContent:raw,querySelector(){return null;},querySelectorAll(){return [];}};}
for(const title of ['Codigo C','plain']){
 let p=pre();c.renderDidacticCode(p,raw,title);results.push({name:'sequential-'+title,html:p.innerHTML});
 results.push({name:'hierarchical-'+title,html:c.buildHierHighlightedCodeHtml(raw,title)});
 results.push({name:'graph-'+title,html:c.buildGraphHighlightedCodeHtml(raw,title)});
 p=pre();c.window.InterpreterRuntime.renderCode(p,raw,title);results.push({name:'runtime-'+title,html:p.innerHTML});
}
let p=pre();c.highlightHelpCodeBlock(p);results.push({name:'help',html:p.innerHTML});p=pre();c.window.InterpreterRuntime.ensureCodeLines(p);results.push({name:'runtime-ensure',html:p.innerHTML});
fs.mkdirSync('../qa_hier_dom_main',{recursive:true});fs.writeFileSync('../qa_hier_dom_main/renderers.json',JSON.stringify({raw,results}));
