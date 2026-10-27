"""Bind authentic published tests and permit only declared portability adapters."""
import ast
import hashlib
import json

class _FixturePathAdapter(ast.NodeTransformer):
    def visit_Constant(self,node):
        if isinstance(node.value,str):
            node.value=node.value.replace("openspec/changes/audit-local-quality-and-unified-controls/evidence/","openspec/changes/archive/2026-10-13-audit-local-quality-and-unified-controls/evidence/")
        return node
    def visit_ImportFrom(self,node):
        if node.module=='scripts.published_test_inputs' and len(node.names)==1 and node.names[0].name=='audit_input_path' and node.names[0].asname is None:
            return None
        return self.generic_visit(node)
    def visit_Call(self,node):
        if isinstance(node.func,ast.Attribute) and node.func.attr=="replace" and len(node.args)==2 and not node.keywords and all(isinstance(a,ast.Constant) for a in node.args) and [a.value for a in node.args]==[b"\r\n",b"\n"] and isinstance(node.func.value,ast.Call) and isinstance(node.func.value.func,ast.Attribute) and node.func.value.func.attr=="read_bytes" and not node.func.value.args and not node.func.value.keywords:
            return self.visit(node.func.value)
        if isinstance(node.func,ast.Name) and node.func.id=='audit_input_path' and len(node.args)==1 and not node.keywords:
            return self.visit(node.args[0])
        return self.generic_visit(node)

def assert_published_test_successor(root,historical_record,algorithm="mergesort"):
    folder=root/'tests/fixtures/sorting-history'
    receipt=json.loads((folder/(algorithm+'-test-migration.json')).read_text(encoding='utf-8'))
    assert historical_record['sha256']==receipt['original_declared_sha256']
    assert isinstance(receipt['original_preimage_available'],bool)
    if receipt['original_preimage_available']:
        assert hashlib.sha256((folder/receipt['original_snapshot']).read_bytes()).hexdigest()==receipt['original_declared_sha256']
    assert historical_record['path'].replace('\\','/')==receipt['source']['path']
    raw=(folder/receipt['source']['snapshot']).read_bytes()
    assert hashlib.sha256(raw).hexdigest()==receipt['source']['sha256']
    assert hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest()==receipt['source']['blob_sha1']
    baseline=ast.parse(raw.decode('utf-8-sig'))
    current=ast.parse((root/receipt['source']['path']).read_text(encoding='utf-8-sig'))
    normalize=lambda tree:ast.dump(_FixturePathAdapter().visit(tree),include_attributes=False)
    assert normalize(current)==normalize(baseline),'Published sorting cases/assertions changed beyond the declared fixture portability adapters'

assert_published_mergesort_test_successor=assert_published_test_successor

