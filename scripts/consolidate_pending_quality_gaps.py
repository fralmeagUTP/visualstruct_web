"""Source-only actionable gap inventory; no execution/absence inference."""
from pathlib import Path
import ast,hashlib,json,re
from collections import Counter,defaultdict
from scripts.build_app_quality_bindings import functions
from scripts.build_app_quality_inventory import _control_items
R=Path(__file__).resolve().parents[1];C=R/'openspec/changes/archive/2026-10-14-resolve-didactic-stack-c1-residuals'
def main():
 baseline=C/'bindings-pending-routes-operations';pending=json.loads((baseline/'unassigned.json').read_text(encoding='utf-8'));registry=json.loads((baseline/'app-executable-bindings.json').read_text(encoding='utf-8'))
 m=json.loads((R/'docs/qa/app-coverage-manifest-v1.json').read_text(encoding='utf-8'));items={x['id']:x for x in m['items']}
 items.update({x['id']:x for x in _control_items(include_unidentified=True) if x['metadata'].get('synthetic_identifier')})
 assert len(pending)==232 and len(registry['items'])==143
 tests=[]
 for p in sorted((R/'tests').glob('test_*.py')):
  s=p.read_text(encoding='utf-8-sig');t=ast.parse(s)
  global_strings={n.value for n in ast.walk(t) if isinstance(n,ast.Constant) and isinstance(n.value,str)}
  for name,f in functions(t):
   strings={n.value for n in ast.walk(f) if isinstance(n,ast.Constant) and isinstance(n.value,str)}
   calls=[n for n in ast.walk(f) if isinstance(n,ast.Call)]
   gestures=[]
   for n in calls:
    if isinstance(n.func,ast.Attribute) and n.func.attr in {'click','fill','press','check','uncheck','select_option','focus'}:
     for a in n.args:
      if isinstance(a,ast.Constant) and isinstance(a.value,str):gestures.append((a.value,n.lineno))
     if isinstance(n.func.value,ast.Call):
      for a in n.func.value.args:
       if isinstance(a,ast.Constant) and isinstance(a.value,str):gestures.append((a.value,n.lineno))
   tests.append({'node':p.relative_to(R).as_posix()+'::'+name,'line':f.lineno,'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'strings':strings,'global_strings':global_strings,'calls':calls,'gestures':gestures,'assertions':sum(isinstance(n,ast.Assert) for n in ast.walk(f))})
 groups=defaultdict(list)
 for item in items.values():
  if item['category']=='control' and not item['metadata'].get('synthetic_identifier'):groups[item['metadata']['identifier']].append(item['id'])
 rows=[]
 for ident in pending:
  item=items[ident];cat=item['category'];meta=item['metadata'];refs=[];related=[];flags=[]
  for t in tests:
   kind=None;line=t['line']
   if cat=='control':
    identifier=meta['identifier'];attrs=meta['attributes']
    selectors=[re.compile('#'+re.escape(identifier)+r'(?![\w-])')] if not meta.get('synthetic_identifier') else []
    def selected(s):return any(p.search(s) for p in selectors) or any(k.startswith('data-') and (f'[{k}="{v}"]' in s or f"[{k}='{v}']" in s) for k,v in attrs.items())
    actions=[(s,n) for s,n in t['gestures'] if selected(s)]
    if actions:kind='LITERAL_UI_ACTION';line=actions[0][1]
    elif any(selected(s) or (not meta.get('synthetic_identifier') and s==identifier) for s in t['strings']):kind='SELECTOR_OR_RENDER_ASSERTION_ONLY'
   elif cat in {'operation','algorithm'}:
    token=meta['operation']['name'] if cat=='operation' else meta.get('algorithm',meta.get('id'))
    if token in t['strings']:kind='LITERAL_OPERATION_ARGUMENT_REQUIRES_CONTEXT'
    elif any(isinstance(n.func,ast.Attribute) and n.func.attr==token for n in t['calls']):kind='DOMAIN_METHOD_CALL_REQUIRES_ADAPTER_MAPPING'
    elif token in t['global_strings'] and t['assertions']:kind='MODULE_PARAMETER_OR_CASE_TABLE_REFERENCE'
   elif cat=='phase':
    path='/graph/graph/'+meta['phase']
    if any(path==s or path in s for s in t['strings']):kind='EXPLICIT_PHASE_URL_REQUIRES_ORACLE_MAPPING'
   elif cat=='route':
    pattern=re.sub(r'<(?:\w+:)?\w+>',r'[^/]+',meta['rule'])
    if any(re.fullmatch(pattern,s.split('?',1)[0]) for s in t['strings']):kind='LITERAL_ROUTE_REFERENCE_REQUIRES_RESPONSE_MAPPING'
    elif '<trace_id>' in meta['rule'] and any(s in t['strings'] for s in ['page_url' if meta['rule'].endswith('/page') else 'export_url']):kind='RESPONSE_DERIVED_TRACE_URL_REQUIRES_FIXTURE_MAPPING'
    elif '<phase>' in meta['rule'] and any('/graph/graph/' in s for s in t['strings']):kind='PARAMETER_ROUTE_PHASE_REFERENCE'
   if kind:refs.append({'test_node':t['node'],'line':line,'source_sha256':t['sha256'],'evidence_kind':kind,'assertions_in_function':t['assertions'],'status':'CANDIDATE_NOT_A_VALIDATED_CASE'})
  if cat=='control':
   same=groups.get(meta['identifier'],[])
   if len(same)>1:flags.append({'kind':'SHARED_SELECTOR_ACROSS_TEMPLATE_CONTEXTS_NOT_AUTOMATIC_DUPLICATE','related_items':same})
   if meta['attributes'].get('type')=='hidden':flags.append({'kind':'HIDDEN_DATA_INPUT_REQUIRES_SCOPE_JUSTIFICATION'})
  if cat=='algorithm' and item['module']=='graph':
   operation='operation:graph/graph/'+meta['algorithm']
   related=[operation] if operation in registry['items'] else []
   flags.append({'kind':'SAME_ALGORITHM_DIFFERENT_PHASE_CONTEXT_NOT_AUTOMATIC_DUPLICATE','phase':meta['phase']})
  if refs:
   strong=any(x['evidence_kind'] not in {'MODULE_PARAMETER_OR_CASE_TABLE_REFERENCE','SELECTOR_OR_RENDER_ASSERTION_ONLY'} for x in refs)
   cause='EXISTING_TEST_CONTEXT_NOT_MAPPED' if strong else 'REFERENCE_ONLY_REQUIRES_CASE_REVIEW'
  else:cause='NO_SOURCE_CASE_CANDIDATE_FOUND_ABSENCE_UNCONFIRMED'
  next_action={'EXISTING_TEST_CONTEXT_NOT_MAPPED':'Resolve fixture/helper/parameters and correlate request or gesture with concrete expected; bind only after review. Do not rerun consumed campaigns.','REFERENCE_ONLY_REQUIRES_CASE_REVIEW':'Inspect actual parametrization/setup and response assertions. Render/name reference alone is insufficient; define focal case only if semantic coverage absent.','NO_SOURCE_CASE_CANDIDATE_FOUND_ABSENCE_UNCONFIRMED':'Review dynamic selectors, helper-generated cases and existing native/QA evidence before certifying absence; then define a focused case if truly missing.'}[cause]
  rows.append({'id':ident,'category':cat,'module':item['module'],'inventory_source':item['source'],'cause':cause,'candidate_references':refs,'related_existing_bindings':related,'scope_duplicate_flags':flags,'new_binding':False,'acceptance':'PENDING_MAPPING_AND_EVIDENCE_REVIEW','next_action':next_action})
 assert len(rows)==232 and len({x['id'] for x in rows})==232
 out=C/'gap-inventory232';out.mkdir(exist_ok=True)
 counts=Counter(x['cause'] for x in rows);cross={cat:dict(Counter(x['cause'] for x in rows if x['category']==cat)) for cat in sorted({x['category'] for x in rows})}
 summary={'pending_before':232,'pending_after':232,'bindings_before':143,'bindings_after':143,'new_validated_bindings':0,'categories':dict(Counter(x['category'] for x in rows)),'causes':dict(counts),'by_category_cause':cross,'confirmed_real_absence':0,'confirmed_duplicates_or_exclusions':0,'items_with_scope_duplicate_review_flags':sum(bool(x['scope_duplicate_flags']) for x in rows),'existing_bound_source_cases_requiring_execution_or_accepted_evidence':sum(x.get('provenance',{}).get('execution')=='NOT_RUN_THIS_PHASE' for x in registry['items'].values()),'test_bodies_executed':0,'warning':'Candidates are references, not proof of relevant assertions or executable case; zero confirmed absence does not mean no missing tests.'}
 for name,data in [('items.json',rows),('summary.json',summary)]:
  (out/name).write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 print(json.dumps(summary))
if __name__=='__main__':main()
