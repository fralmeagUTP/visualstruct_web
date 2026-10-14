"""DOM census of control generation flows, no operation/algorithm executions."""
import json
from pathlib import Path
import pytest
from test_residual58_focal_cases import residual58_app
from test_controls40_real_flows import controls40_page
GROUPS={
 'sequential':[(f'/sequential/{name}','SEQ_VIEW_MODEL','#operation-select','field','seq-function-list') for name in ['stack','queue','priority_queue','linked_list','circular_list','sublist']],
 'hierarchical':[(f'/hierarchical/{name}','HIER_VIEW_MODEL','#operation-select','h-field','hier-function-list') for name in ['abb','avl','red_black','binary_heap']],
 'hash':[('/hash/hash_table','HASH_VIEW_MODEL','#hash-operation-select','hash-field','hash-function-list')],
 'graph':[(f'/graph/graph/{phase}','GRAPH_VIEW_MODEL','#graph-operation-select','g-op-field','graph-function-list') for phase in ['construccion','recorridos','camino-minimo','expansion-minima']],
 'sorting':[('/sorting/visualizador','SORTING_VIEW_MODEL',None,None,'sorting-function-list')],
}
OBSERVER="""(()=>{window.__dynamicCreated=[];window.__dynamicScrolled=[];const scrollTop=Object.getOwnPropertyDescriptor(Element.prototype,'scrollTop');if(scrollTop?.set)Object.defineProperty(Element.prototype,'scrollTop',{...scrollTop,set:function(value){window.__dynamicScrolled.push({tag:this.tagName,kind:'scrollTop',value});return scrollTop.set.call(this,value);}});const create=document.createElement.bind(document);document.createElement=function(tag,...args){const node=create(tag,...args);if(['button','input','select','textarea','a','summary','details'].includes(String(tag).toLowerCase()))window.__dynamicCreated.push({node,tag,stack:new Error().stack});return node;};const scroll=Element.prototype.scrollIntoView;Element.prototype.scrollIntoView=function(...args){window.__dynamicScrolled.push({tag:this.tagName,line:this.dataset.line,codeLine:this.dataset.codeLine});return scroll.apply(this,args);};})();"""
@pytest.mark.parametrize('group',list(GROUPS))
def test_dynamic_fields_code_links_and_workspace_creator_flows(controls40_page,tmp_path,group):
 page,context,base=controls40_page;page.add_init_script(OBSERVER);posts=[];errors=[];page.on('request',lambda r:posts.append(r.url) if r.method=='POST' else None);page.on('pageerror',lambda e:errors.append(str(e)));flows=[]
 for route,model_name,selector,prefix,function_list in GROUPS[group]:
  page.goto(base+route,wait_until='networkidle');selected=[]
  if selector:
   operations=page.evaluate('(name)=>window[name].operations',model_name);catalog={op['name']:op for op in operations}
   options=page.locator(selector+' option').evaluate_all('(ns)=>ns.map(n=>n.value).filter(Boolean)')
   for op in options:
    page.select_option(selector,op);fields=[]
    for field in catalog[op].get('inputs',[]):
     target=page.locator('#'+prefix+'-'+field['name']);assert target.count()==1
     assert target.get_attribute('name')==field['name'];assert page.locator('label[for="'+prefix+'-'+field['name']+'"]').count()==1
     expected_tag='SELECT' if field.get('type')=='select' and field.get('options') else 'INPUT';assert target.evaluate('(n)=>n.tagName')==expected_tag
     if expected_tag=='INPUT':
      if target.get_attribute('type')=='checkbox':target.check();assert target.is_checked()
      else:target.fill('7');assert target.input_value()=='7'
     else:
      values=target.locator('option').evaluate_all('(ns)=>ns.map(n=>n.value)');assert values;target.select_option(values[-1])
     fields.append({'name':field['name'],'id':target.get_attribute('id'),'tag':expected_tag,'value_changed':True})
    selected.append({'operation':op,'fields':fields})
  if group=='graph':
   algorithm_selector=page.locator('#graph-algorithm-select');names=algorithm_selector.locator('option').evaluate_all('(ns)=>ns.map(n=>n.value).filter(Boolean)')
   for name in names:
    algorithm_selector.select_option(name)
    for field in catalog[name].get('inputs',[]):assert page.locator('#g-alg-field-'+field['name']).count()==1
    selected.append({'algorithm':name,'fields':[field['name'] for field in catalog[name].get('inputs',[])]})
  buttons=page.locator('#'+function_list+' button');count=buttons.count();navigation=[]
  for index in sorted(set([0,count-1])) if count else []:
   target=buttons.nth(index);line=target.get_attribute('data-line') or target.get_attribute('data-code-line');assert line is not None
   before=len(page.evaluate('window.__dynamicScrolled'));target.click(force=True);assert len(page.evaluate('window.__dynamicScrolled'))>before
   navigation.append({'line':line,'scroll_called':True,'accepted_scroll_contract':'scrollIntoView or stackpilot scrollTop setter','force_used_for_potential_collapsed_container':True})
  visible=page.locator('button,input,select,textarea,a,summary').evaluate_all("(nodes)=>nodes.filter(n=>n.getClientRects().length&&getComputedStyle(n).display!=='none').map(n=>({tag:n.tagName,id:n.id,name:n.name||null,type:n.type||null,action:n.dataset.line||n.dataset.codeLine||n.dataset.answer||null}))")
  creators=page.evaluate("window.__dynamicCreated.map(x=>({tag:x.tag,id:x.node.id,name:x.node.name||null,connected:x.node.isConnected,visible:Boolean(x.node.getClientRects().length),stack:x.stack}))")
  flows.append({'route':route,'selectors':selected,'code_navigation':navigation,'visible_controls':visible,'creators':creators})
 assert not posts and not errors
 (tmp_path/'dynamic-flow-proof.json').write_text(json.dumps({'group':group,'flows':flows,'POSTs':posts,'JS_errors':errors,'limits':'Fieldgeneration/descriptorbinding andcode-navigation scroll;nooperationexecution. Sourceinventory plus existing exercisedtraces/downloads coverdeferredfactories;forceclickdoesnotprovepublicvisibility.'},ensure_ascii=False,indent=2),encoding='utf-8')
