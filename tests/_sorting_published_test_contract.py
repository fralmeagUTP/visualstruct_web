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


class _CurrentSortingAssertionAdapter(_FixturePathAdapter):
    """Project only the three explicit checked successors to their old assertions.

    Every case, condition, expected value and remaining assertion must still be
    identical. The replacement helpers have independent adversarial tests.
    """
    _IMPORTS = {
        'tests._sorting_text_source_contract': 'assert_sorting_text_source_continuity',
        '_audit_sorting_c_source': 'assert_source_transport_identity',
        'tests._sorting_trace_text_contract': 'current_swap_display',
    }
    # Only these three complete assertions may adapt the authentic old display.
    # In particular, the current result must never be normalized: doing so would
    # hide a regression back to the old unaccented product text.
    _SWAP_ASSERTIONS = {
        'test_default_shared_helper_keeps_original_behavior_without_running_closed_methods': (
            'assert current_swap_display(old._steps) == current._steps and old.values == current.values and old.metrics.moves == current.metrics.moves == 0',
            'assert old._steps == current._steps and old.values == current.values and old.metrics.moves == current.metrics.moves == 0',
        ),
        'test_shared_helper_default_unchanged_without_running_closed_methods': (
            'assert current_swap_display(old._steps) == now._steps and old.values == now.values and old.metrics.moves == now.metrics.moves == 0',
            'assert old._steps == now._steps and old.values == now.values and old.metrics.moves == now.metrics.moves == 0',
        ),
        'test_shared_swap_default_preserved_and_heap_optin_no_fake_TAD_console': (
            "assert current_swap_display(old) == {'values': p.values, 'steps': p._steps, 'metrics': vars(p.metrics)}",
            "assert old == {'values': p.values, 'steps': p._steps, 'metrics': vars(p.metrics)}",
        ),
    }

    def __init__(self):
        super().__init__()
        self._function_names = []

    def visit_FunctionDef(self, node):
        self._function_names.append(node.name)
        try:
            return self.generic_visit(node)
        finally:
            self._function_names.pop()

    def visit_Assert(self, node):
        function = self._function_names[-1] if self._function_names else None
        pair = self._SWAP_ASSERTIONS.get(function)
        if pair and ast.dump(node, include_attributes=False) == ast.dump(ast.parse(pair[0]).body[0], include_attributes=False):
            return ast.copy_location(ast.parse(pair[1]).body[0], node)
        return self.generic_visit(node)

    def visit_ImportFrom(self,node):
        if node.module in self._IMPORTS and len(node.names)==1 and node.names[0].name==self._IMPORTS[node.module] and node.names[0].asname is None:
            return None
        return super().visit_ImportFrom(node)
    def visit_Expr(self,node):
        call=node.value
        if isinstance(call,ast.Call) and isinstance(call.func,ast.Name) and not call.keywords:
            if call.func.id=='assert_source_transport_identity' and len(call.args)==2:
                return ast.Assert(test=ast.Compare(left=self.visit(call.args[0]),ops=[ast.Eq()],comparators=[self.visit(call.args[1])]),msg=None)
            if call.func.id=='assert_sorting_text_source_continuity' and len(call.args)==3:
                root,relative,expected=[self.visit(arg) for arg in call.args]
                path=ast.BinOp(left=root,op=ast.Div(),right=relative)
                raw=ast.Call(func=ast.Attribute(value=path,attr='read_bytes',ctx=ast.Load()),args=[],keywords=[])
                digest=ast.Call(func=ast.Attribute(value=ast.Call(func=ast.Attribute(value=ast.Name(id='hashlib',ctx=ast.Load()),attr='sha256',ctx=ast.Load()),args=[raw],keywords=[]),attr='hexdigest',ctx=ast.Load()),args=[],keywords=[])
                return ast.Assert(test=ast.Compare(left=digest,ops=[ast.Eq()],comparators=[expected]),msg=None)
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
    normalize=lambda tree:ast.dump(_CurrentSortingAssertionAdapter().visit(tree),include_attributes=False)
    assert normalize(current)==normalize(baseline),'Published sorting cases/assertions changed beyond declared path, transport, spelling and protected-source adapters'

assert_published_mergesort_test_successor=assert_published_test_successor

def assert_archived_quicksort_test_portability(root):
    """Preserve the exact recovered Quick tests apart from existing path adapters."""
    from scripts.published_test_inputs import audit_input_path
    snapshot = root / ('openspec/changes/archive/2026-10-13-audit-local-quality-and-unified-controls/'
                       'evidence/visible-sorting-quicksort-instructions/before/tests/'
                       'test_sorting_quicksort_baseline_low.py')
    raw = audit_input_path(snapshot).read_bytes()
    assert hashlib.sha256(raw).hexdigest() == '3c719f717ad85e03fd1f307834fa6bf84333a1f80e3724fbe20269c82917a1d7', 'Quick historical snapshot changed'
    historical = ast.parse(raw.decode('utf-8-sig'))
    current = ast.parse((root/'tests/test_sorting_quicksort_baseline_low.py').read_text(encoding='utf-8-sig'))
    normalize = lambda tree: ast.dump(_CurrentSortingAssertionAdapter().visit(tree), include_attributes=False)
    assert normalize(current) == normalize(historical), 'Quick historical cases/assertions changed beyond declared path, transport, spelling and protected-source adapters'



def _assert_archived_baseline_portability(root, algorithm, expected_sha):
    """Bind a genuine old baseline and compare every case/assertion after adapters."""
    from scripts.published_test_inputs import audit_input_path
    path=f'tests/test_sorting_{algorithm}_baseline_low.py'
    snapshot=root / ('openspec/changes/archive/2026-10-13-audit-local-quality-and-unified-controls/'
                     f'evidence/visible-sorting-{algorithm}-instructions/before/{path}')
    raw=audit_input_path(snapshot).read_bytes()
    assert hashlib.sha256(raw).hexdigest()==expected_sha, 'Historical baseline snapshot changed'
    historical=ast.parse(raw.decode('utf-8-sig'))
    current=ast.parse((root/path).read_text(encoding='utf-8-sig'))
    normalize=lambda tree:ast.dump(_CurrentSortingAssertionAdapter().visit(tree),include_attributes=False)
    assert normalize(current)==normalize(historical), 'Historical baseline cases/assertions changed beyond declared adapters'


def assert_archived_shell_test_portability(root):
    _assert_archived_baseline_portability(root,'shell','ff9ec14319d71df3d2618cea9f2dbcb5f84b6ec5127b1e2dd024f23b4cbb011f')


def assert_archived_burbuja_test_portability(root):
    _assert_archived_baseline_portability(root,'burbuja','bd2817341ac806e9386f27be3a428553a4db44ce88391fb5c8141353aa2a2d1a')
