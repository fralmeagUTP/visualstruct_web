"""Read the minimal authentic 27 October evidence subset, with integrity checks."""
from pathlib import Path
import hashlib
import json
PACKAGE = Path(__file__).resolve().parents[1] / 'tests/fixtures/independent-evidence-20261027'
MANIFEST_SHA256 = '1223f1e987e0a153149fffaf4cf6dc61dc1ef9c65c37d412e8bdd3e34c0acbf3'

def independent_input_path(name, *, package=PACKAGE):
    raw = (package / 'manifest.json').read_bytes()
    if hashlib.sha256(raw).hexdigest() != MANIFEST_SHA256:
        raise ValueError('Independent evidence manifest changed')
    records = json.loads(raw)['files']
    if name not in records or Path(name).is_absolute() or '..' in Path(name).parts:
        raise ValueError('Unregistered independent evidence input')
    path = package / name
    data = path.read_bytes()
    if len(data) != records[name]['bytes'] or hashlib.sha256(data).hexdigest() != records[name]['sha256']:
        raise ValueError('Independent evidence bytes changed: ' + name)
    return path
