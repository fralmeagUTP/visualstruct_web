"""Bind literal existing HTTP/UI cases without executing their test bodies."""
from __future__ import annotations
import argparse, ast, hashlib, json, re
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]

def literal(node):
    try:return ast.literal_eval(node)
    except (ValueError,TypeError):raise ValueError("not literal")

def json_value(value):
    if isinstance(value,bytes):return {"bytes_hex":value.hex()}
    if isinstance(value,(list,tuple)):return [json_value(x) for x in value]
    if isinstance(value,dict):return {str(k):json_value(v) for k,v in value.items()}
    return value

def functions(tree):
    for node in tree.body:
        if isinstance(node,(ast.FunctionDef,ast.AsyncFunctionDef)) and node.name.startswith('test_'):yield node.name,node
        if isinstance(node,ast.ClassDef) and node.name.startswith('Test'):
            for method in node.body:
                if isinstance(method,(ast.FunctionDef,ast.AsyncFunctionDef)) and method.name.startswith('test_'):yield node.name+'::'+method.name,method

def dependent(node,names):return any(isinstance(x,ast.Name) and x.id in names for x in ast.walk(node))

def request_cases(tree,source):
    cases=[]
    for name,fn in functions(tree):
        if any(token in name.lower() for token in ['benchmark','performance','900']):continue
        if any(any(isinstance(x,ast.Attribute) and x.attr in {'skip','skipif','xfail'} for x in ast.walk(d)) for d in fn.decorator_list):continue
        if 'client' not in [x.arg for x in fn.args.args]:continue
        parents={child:parent for parent in ast.walk(fn) for child in ast.iter_child_nodes(parent)}
        calls=[]
        for call in ast.walk(fn):
            if not (isinstance(call,ast.Call) and isinstance(call.func,ast.Attribute) and isinstance(call.func.value,ast.Name) and call.func.value.id=='client' and call.func.attr in {'get','post','delete','put','patch'} and call.args):continue
            try:
                path=literal(call.args[0]);kwargs={kw.arg:literal(kw.value) for kw in call.keywords}
                if not isinstance(path,str) or not path.startswith('/'):continue
            except ValueError:continue
            calls.append((call,{'method':call.func.attr.upper(),'path':path,**json_value(kwargs)}))
        calls.sort(key=lambda pair:pair[0].lineno)
        for index,(call,request) in enumerate(calls):
            end=calls[index+1][0].lineno if index+1<len(calls) else fn.end_lineno+1
            parent=parents.get(call);names=set()
            while parent is not None and parent is not fn:
                if isinstance(parent,(ast.Assign,ast.AnnAssign)):
                    targets=parent.targets if isinstance(parent,ast.Assign) else [parent.target]
                    names.update(t.id for t in targets if isinstance(t,ast.Name));break
                parent=parents.get(parent)
            assignments=sorted((x for x in ast.walk(fn) if isinstance(x,ast.Assign) and call.lineno<=x.lineno<end),key=lambda x:x.lineno)
            for assigned in assignments:
                if dependent(assigned.value,names):names.update(t.id for t in assigned.targets if isinstance(t,ast.Name))
            assertions=[]
            for check in ast.walk(fn):
                if not isinstance(check,ast.Assert) or not call.lineno<=check.lineno<end:continue
                if not dependent(check.test,names) and call not in list(ast.walk(check.test)):continue
                values=[]
                if isinstance(check.test,ast.Compare):
                    for right in check.test.comparators:
                        try:values.append(json_value(literal(right)))
                        except ValueError:pass
                if values:assertions.append({'expression':ast.unparse(check.test),'literal_expected':values,'line':check.lineno})
            if assertions:
                cases.append({'function':name,'input':{'request':request,'preceding_literal_requests':[x[1] for x in calls[:index]],'context':'execute the referenced test function and fixtures, not an isolated replay of extracted requests'},'expected':{'assertions':assertions},'request_line':call.lineno,'function_line':fn.lineno})
    return cases

def page_path(node):
    try:value=literal(node)
    except ValueError:
        if not isinstance(node,ast.JoinedStr):return None
        parts=[]
        for i,piece in enumerate(node.values):
            if isinstance(piece,ast.Constant):parts.append(piece.value)
            elif i==0 and isinstance(piece,ast.FormattedValue) and isinstance(piece.value,ast.Name) and piece.value.id in {'base_url','server_url'}:continue
            else:return None
        value=''.join(parts)
    return value if isinstance(value,str) and value.startswith('/') else None

def ui_cases(tree,source):
    result=[]
    for name,fn in functions(tree):
        text=ast.get_source_segment(source,fn) or ''
        if 'playwright' not in text and 'playwright' not in name:continue
        assertions=[{'expression':ast.unparse(x.test),'line':x.lineno} for x in ast.walk(fn) if isinstance(x,ast.Assert)]
        if not assertions:continue
        paths=[];actions=[]
        for call in ast.walk(fn):
            if not isinstance(call,ast.Call) or not isinstance(call.func,ast.Attribute):continue
            method=call.func.attr;selector=None;args=[]
            if method=='goto' and call.args:
                path=page_path(call.args[0])
                if path:paths.append(path)
            if method not in {'click','fill','check','uncheck','select_option','press'}:continue
            value=call.func.value
            try:
                if isinstance(value,ast.Name) and value.id=='page' and call.args:
                    selector=literal(call.args[0]);args=[literal(x) for x in call.args[1:]]
                elif isinstance(value,ast.Call) and isinstance(value.func,ast.Attribute) and value.func.attr=='locator' and value.args:
                    selector=literal(value.args[0]);args=[literal(x) for x in call.args]
                else:continue
            except ValueError:continue
            if isinstance(selector,str):actions.append({'selector':selector,'action':method,'arguments':json_value(args),'line':call.lineno})
        if paths and actions:result.append({'function':name,'input':{'pages':paths,'actions':actions,'context':'complete existing E2E test, including its helpers'},'expected':{'assertions':assertions},'function_line':fn.lineno})
    return result

def matches(item,case):
    category=item['category'];module=item['module'];meta=item['metadata']
    req=case['input']['request'];path=req['path'].split('?',1)[0];body=req.get('json') or {}
    if category=='route':
        pattern=re.sub(r'<(?:\w+:)?\w+>',r'[^/]+',meta['rule'])
        return req['method'] in meta['methods'] and re.fullmatch(pattern,path) is not None
    if category=='structure':
        expected=f"/{module}/{meta['id']}" if module!='sorting' else '/sorting/visualizador'
        return req['method']=='GET' and path==expected
    if category=='operation':
        return req['method']=='POST' and path==f"/{module}/{meta['structure_id']}/operate" and isinstance(body,dict) and body.get('operation')==meta['operation']['name']
    if category=='phase':return req['method']=='GET' and path==f"/graph/graph/{meta['phase']}"
    if category=='algorithm' and module=='sorting':
        return req['method']=='POST' and path=='/api/ordenamiento/run' and isinstance(body,dict) and body.get('algorithm_id')==meta['id']
    if category=='algorithm' and module=='graph':
        phase=meta['phase'];phase_paths={x['path'] for x in case['input']['preceding_literal_requests'] if x['method']=='GET'}
        return path=='/graph/graph/operate' and isinstance(body,dict) and body.get('operation')==meta['algorithm'] and f'/graph/graph/{phase}' in phase_paths
    return False

def ui_matches(item,case):
    if item['category']!='control':return False
    attrs=item['metadata']['attributes'];identifier=item['metadata']['identifier']
    for action in case['input']['actions']:
        selector=action['selector']
        if not item['metadata'].get('synthetic_identifier') and re.search(r'#'+re.escape(identifier)+r'(?![\w-])',selector):return True
        for name,value in attrs.items():
            if name.startswith('data-') and (f'[{name}="{value}"]' in selector or f"[{name}='{value}']" in selector):return True
    return False

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--output-dir',required=True);args=parser.parse_args();out=Path(args.output_dir);out.mkdir(parents=True,exist_ok=True)
    import sys
    sys.path.insert(0,str(ROOT))
    from scripts.build_app_quality_inventory import _control_items,validate_executable_bindings
    manifest=json.loads((ROOT/'docs/qa/app-coverage-manifest-v1.json').read_text(encoding='utf-8'))
    anonymous=[x for x in _control_items(include_unidentified=True) if x['metadata'].get('synthetic_identifier')];items=manifest['items']+anonymous
    http=[];ui=[];skipped=[]
    for path in sorted((ROOT/'tests').glob('test_*.py')):
        try:source=path.read_text(encoding='utf-8-sig');tree=ast.parse(source)
        except (SyntaxError,UnicodeError) as exc:skipped.append({'source':path.relative_to(ROOT).as_posix(),'reason':type(exc).__name__});continue
        common={'test_file':path.relative_to(ROOT).as_posix(),'test_source_sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'execution':'NOT_RUN_THIS_PHASE'}
        http.extend({**common,**case} for case in request_cases(tree,source));ui.extend({**common,**case} for case in ui_cases(tree,source))
    bindings={};unassigned=[]
    for item in items:
        candidates=[x for x in http if matches(item,x)] if item['category']!='control' else [x for x in ui if ui_matches(item,x)]
        if not candidates:unassigned.append({'id':item['id'],'category':item['category'],'reason':'No conservative literal case match; requires review, helpers/parameters or new case.'});continue
        def rank(case):
            assertions=case['expected']['assertions']
            positive=any('status_code' in row['expression'] and row.get('literal_expected')==[200] for row in assertions)
            concrete_state=sum(any(isinstance(value,(list,dict)) for value in row.get('literal_expected',[])) for row in assertions)
            return (positive,concrete_state,len(assertions))
        if item['category']=='algorithm':
            candidates=[case for case in candidates if rank(case)[0]]
            if not candidates:
                unassigned.append({'id':item['id'],'category':'algorithm','reason':'Only failure/preflight case found; cannot bind as executed algorithm case.'})
                continue
        case=max(candidates,key=rank)
        bindings[item['id']]={'test_node':case['test_file']+'::'+case['function'],'layer':'e2e' if item['category']=='control' else 'api','input':case['input'],'expected':case['expected'],'provenance':{'test_source_sha256':case['test_source_sha256'],'function_line':case['function_line'],'request_line':case.get('request_line'),'status':'SOURCE_LINK_VERIFIED_ONLY','execution':'NOT_RUN_THIS_PHASE'},'oracle_scope':'listed existing assertions; not complete family, C/frame fidelity or fresh execution proof'}
    registry={'schema':'app-executable-bindings/v1','items':bindings};errors=validate_executable_bindings({'items':[x for x in items if x['id'] in bindings]},registry)
    assert not errors,errors[:5]
    (out/'app-executable-bindings.json').write_text(json.dumps(registry,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    (out/'unassigned.json').write_text(json.dumps(unassigned,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    summary={'inventory_items':len(items),'literal_http_cases':len(http),'literal_ui_cases':len(ui),'source_links_validated':len(bindings),'unassigned':len(unassigned),'test_bodies_executed':0,'gate_errors_for_assigned_subset':len(errors),'skipped_sources':skipped}
    (out/'summary.json').write_text(json.dumps(summary,indent=2)+'\n',encoding='utf-8');print(json.dumps(summary))
if __name__=='__main__':main()
