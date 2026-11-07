"""Exact recovered Heap bytes plus the existing, unexpanded AST successor contract."""
import hashlib
import json
from tests._sorting_published_test_contract import assert_published_test_successor

_RECEIPT_SHA256 = '75c807245e6eba4367b7e57929f421cc6d286bbf4f1263f57ddbf1ce08bc1c4b'
_ADAPTER_SHA256 = '7b98c6855c3b801eff7f0a3655a8186d2d3fe0918c43c9510a076265f92da025'


def assert_recovered_heapsort_test_successor(root, historical_record):
    folder = root / 'tests/fixtures/sorting-history'
    receipt_raw = (folder / 'heapsort-test-migration.json').read_bytes()
    assert hashlib.sha256(receipt_raw).hexdigest() == _RECEIPT_SHA256, 'Heap recovery receipt changed'
    adapter = (root / 'tests/_sorting_published_test_contract.py').read_bytes()
    assert hashlib.sha256(adapter).hexdigest() == _ADAPTER_SHA256, 'Reviewed successor adapter changed'
    receipt = json.loads(receipt_raw)
    original = (folder / receipt['original_snapshot']).read_bytes()
    published = (folder / receipt['source']['snapshot']).read_bytes()
    assert hashlib.sha256(original).hexdigest() == historical_record['sha256'] == receipt['original_declared_sha256'], 'Heap original bytes or historical pin changed'
    assert original.replace(b'\r\n', b'\n') == published, 'Recovered original and Git source differ beyond transport'
    assert original == published.replace(b'\n', b'\r\n'), 'Recovery must use only the declared LF to CRLF transport'
    assert_published_test_successor(root, historical_record, 'heapsort')
