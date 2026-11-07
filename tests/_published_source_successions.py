"""Exact historical inputs remain pinned; two authorized Graph sources succeeded them."""
import hashlib
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
RECEIPT=Path('tests/fixtures/graph-history/published-source-successions.json')
RECEIPT_SHA='f2e9f3caab431429d3e334a2a7555ce8c7e3091f47f494bf3640985b3cbd8bb7'


def assert_published_source_identity(path, historical, current, *, root=ROOT):
    """Reject every undeclared source difference; never rewrite archive bytes."""
    raw=(root/RECEIPT).read_bytes()
    assert hashlib.sha256(raw).hexdigest()==RECEIPT_SHA, 'Source-succession receipt changed'
    rows={row['path']:row for row in json.loads(raw)['sources']}
    if path in rows:
        row=rows[path]
        assert hashlib.sha256(historical).hexdigest()==row['historical_sha256'], 'Historical Graph source changed'
        assert hashlib.sha256(current).hexdigest()==row['current_sha256'], 'Canonical book Graph source changed'
    else:
        assert current.replace(b'\r\n',b'\n')==historical.replace(b'\r\n',b'\n'), 'Undeclared source change'
