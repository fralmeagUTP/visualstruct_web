"""Finite source-only review of pending route/operation bindings."""
from __future__ import annotations
import ast,copy,hashlib,json
from pathlib import Path
from scripts.build_app_quality_bindings import request_cases,matches,literal
from scripts.build_app_quality_inventory import validate_executable_bindings
ROOT=Path(__file__).resolve().parents[1]
CHANGE=ROOT/'openspec/changes/archive/2026-10-14-resolve-didactic-stack-c1-residuals'

class HelpConstants(ast.NodeTransformer):
    """Expand only the documented literal help-path loop; never execute code."""
    def visit_For(self,node):
        if not isinstance(node.target,ast.Name) or node.target.id!='path':return node
        try:paths=literal(node.iter)
        except ValueError:return node
        if not isinstance(paths,tuple) or not all(isinstance(p,str) and p.startswith('/help/') for p in paths):return node
        expanded=[]
        for path in paths:
            class Replace(ast.NodeTransformer):
                def visit_Name(self,n):return ast.copy_location(ast.Constant(path),n) if n.id=='path' and isinstance(n.ctx,ast.Load) else n
            expanded.extend(Replace().visit(copy.deepcopy(x)) for x in node.body)
        return expanded
    def visit_Call(self,node):
        self.generic_visit(node)
        if isinstance(node.func,ast.Attribute) and node.func.attr=='encode' and isinstance(node.func.value,ast.Constant) and isinstance(node.func.value.value,str) and len(node.args)==1 and isinstance(node.args[0],ast.Constant) and node.args[0].value=='utf-8' and not node.keywords:
            return ast.copy_location(ast.Constant(node.func.value.value.encode('utf-8')),node)
        return node

def concrete(case):
    for row in case['expected']['assertions']:
        expr=row['expression']
        if 'status_code' in expr or "['success']" in expr or 'message' in expr:continue
        check=ast.parse(expr,mode='eval').body
        if not isinstance(check,ast.Compare) or not all(isinstance(op,(ast.Eq,ast.In)) for op in check.ops):continue
        if row.get('literal_expected'):return True
    return False

def main():
    baseline=CHANGE/'bindings-js-runtime';out=CHANGE/'bindings-pending-routes-operations';out.mkdir(exist_ok=True)
    registry=json.loads((baseline/'app-executable-bindings.json').read_text(encoding='utf-8'))
    pending=json.loads((baseline/'unassigned.json').read_text(encoding='utf-8'))
    manifest=json.loads((ROOT/'docs/qa/app-coverage-manifest-v1.json').read_text(encoding='utf-8'))
    items={x['id']:x for x in manifest['items']};targets=[items[x] for x in pending if x in items and items[x]['category'] in {'route','operation'}]
    cases=[]
    for path in sorted((ROOT/'tests').glob('test_*.py')):
        source=path.read_text(encoding='utf-8-sig');tree=ast.parse(source)
        if path.name=='test_app_routes.py':
            # Only this known finite loop is expanded; line evidence stays original.
            for f in tree.body:
                if isinstance(f,ast.FunctionDef) and f.name=='test_help_module_pages_reference_user_manual':
                    f.body=[y for x in f.body for y in ((lambda z:z if isinstance(z,list) else [z])(HelpConstants().visit(x)))]
                    f.body=[HelpConstants().visit(x) for x in f.body]
        for case in request_cases(tree,source):
            cases.append({**case,'test_file':path.relative_to(ROOT).as_posix(),'test_source_sha256':hashlib.sha256(path.read_bytes()).hexdigest()})
    # Explicitly preserve the finite help loop: membership assertion has its
    # literal on the left, which the historical extractor does not collect.
    help_path=ROOT/'tests/test_app_routes.py'
    help_source=help_path.read_text(encoding='utf-8-sig')
    help_fn=next(f for f in ast.parse(help_source).body if isinstance(f,ast.FunctionDef) and f.name=='test_help_module_pages_reference_user_manual')
    loop=next(x for x in help_fn.body if isinstance(x,ast.For))
    assert ast.unparse(loop.target)=='path'
    request=next(x for x in ast.walk(loop) if isinstance(x,ast.Call) and ast.unparse(x.func)=='client.get')
    assert ast.unparse(request.args[0])=='path'
    expected=next(x for x in loop.body if isinstance(x,ast.Assert) and isinstance(x.test,ast.Compare) and isinstance(x.test.ops[0],ast.In))
    assert ast.unparse(expected.test.comparators[0])=='response.data'
    encoded=expected.test.left
    assert isinstance(encoded,ast.Call) and isinstance(encoded.func,ast.Attribute) and encoded.func.attr=='encode' and literal(encoded.args[0])=='utf-8'
    content=literal(encoded.func.value).encode('utf-8')
    for path in literal(loop.iter):
        cases.append({'function':help_fn.name,'test_file':help_path.relative_to(ROOT).as_posix(),'test_source_sha256':hashlib.sha256(help_path.read_bytes()).hexdigest(),'input':{'request':{'method':'GET','path':path},'preceding_literal_requests':[],'context':'Run complete referenced test and fixtures; finite literal help loop.'},'expected':{'assertions':[{'expression':ast.unparse(expected.test),'literal_expected':[{'bytes_hex':content.hex()}],'line':expected.lineno}]},'request_line':request.lineno,'function_line':help_fn.lineno})
    # Derive dedicated sorting dispatch from real decorators and _execute literals.
    route_source=ROOT/'app/routes/sorting_routes.py';dispatch={}
    for f in ast.parse(route_source.read_text(encoding='utf-8-sig')).body:
        if not isinstance(f,ast.FunctionDef):continue
        paths=[d.args[0].value for d in f.decorator_list if isinstance(d,ast.Call) and isinstance(d.func,ast.Attribute) and isinstance(d.func.value,ast.Name) and d.func.value.id=='sorting_api_bp' and d.func.attr=='post' and d.args and isinstance(d.args[0],ast.Constant)]
        ops=[n.args[0].value for n in ast.walk(f) if isinstance(n,ast.Call) and isinstance(n.func,ast.Name) and n.func.id=='_execute' and n.args and isinstance(n.args[0],ast.Constant)]
        if len(paths)==1 and len(ops)==1:dispatch[ops[0]]='/api/ordenamiento'+paths[0]
    classifications=[];added=[]
    for item in targets:
        candidates=[]
        for case in cases:
            matched=matches(item,case)
            if item['category']=='operation' and item['module']=='sorting':
                req=case['input']['request'];matched=req['method']=='POST' and req['path']==dispatch.get(item['metadata']['operation']['name'])
            if matched:candidates.append(case)
        good=[x for x in candidates if concrete(x) and not any(token in x['function'] for token in ('provider','fallback','preprocessor'))]
        if good:
            case=max(good,key=lambda x:len(x['expected']['assertions']))
            registry['items'][item['id']]={'test_node':case['test_file']+'::'+case['function'],'layer':'api','input':case['input'],'expected':case['expected'],'provenance':{'test_source_sha256':case['test_source_sha256'],'request_line':case['request_line'],'function_line':case['function_line'],'status':'SOURCE_LINK_VERIFIED_ONLY','execution':'NOT_RUN_THIS_PHASE'},'oracle_scope':'Concrete existing assertions; referenced whole test required; no new execution or full operation fidelity.'}
            added.append(item['id']);status='EFFECTIVELY_LINKED_REQUIRES_EXECUTION'
        else:status='NO_CONCRETE_TEST_RECOVERED' if not candidates else 'GENERIC_CASE_REQUIRES_REVIEW'
        classifications.append({'id':item['id'],'classification':status,'literal_candidates':len(candidates),'concrete_candidates':len(good),'candidate_test_nodes':sorted({x['test_file']+'::'+x['function'] for x in candidates})})
    # Existing anonymous controls were validated previously; validate all new links.
    errors=validate_executable_bindings({'items':[items[x] for x in added]}, {'schema':registry['schema'],'items':{x:registry['items'][x] for x in added}},project_root=ROOT)
    assert not errors,errors
    remaining=[x for x in pending if x not in added]
    summary={'before_links':len(registry['items'])-len(added),'before_pending':len(pending),'reviewed_route_operations':len(targets),'new_links':len(added),'after_links':len(registry['items']),'after_pending':len(remaining),'source_linked_requires_execution':len(added),'generic_case_requires_review':sum(x['classification']=='GENERIC_CASE_REQUIRES_REVIEW' for x in classifications),'no_concrete_test_recovered':sum(x['classification']=='NO_CONCRETE_TEST_RECOVERED' for x in classifications),'application_tests_executed':0,'gate_errors':len(errors),'sorting_dispatch':dispatch,'sorting_route_source_sha256':hashlib.sha256(route_source.read_bytes()).hexdigest(),'limit':'No-concrete-test-recovered is limited to conservative literal extraction; helpers and parameterized tests are not certified absent.'}
    for name,value in [('app-executable-bindings.json',registry),('unassigned.json',remaining),('classification.json',classifications),('summary.json',summary)]:
        (out/name).write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(summary))
if __name__=='__main__':main()
