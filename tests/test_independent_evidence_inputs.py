"""Negative controls for authentic recovered inputs and bounded display migration."""
from copy import deepcopy
from pathlib import Path
import json
import shutil
import unicodedata
import pytest
from qa.independent_inputs import PACKAGE, independent_input_path
from qa.reviewed_spelling import CORRECTIONS, current_display_spelling


def test_every_recovered_file_is_bound_to_original_bytes():
    rows = json.loads((PACKAGE / 'manifest.json').read_text())['files']
    assert len(rows) == 6
    for name in rows:
        assert independent_input_path(name).is_file()


@pytest.mark.parametrize('mutation', ['manifest', 'input', 'unregistered', 'escape'])
def test_recovered_input_reader_fails_closed(tmp_path, mutation):
    package = tmp_path / 'evidence'
    shutil.copytree(PACKAGE, package)
    name = 'heap-query-return-baseline.py'
    if mutation == 'manifest':
        path = package / 'manifest.json'
        path.write_bytes(path.read_bytes() + b' ')
    elif mutation == 'input':
        path = package / name
        path.write_bytes(path.read_bytes() + b' ')
    elif mutation == 'unregistered':
        name = 'invented.py'
    else:
        name = '../heap-query-return-baseline.py'
    with pytest.raises(ValueError):
        independent_input_path(name, package=package)


def test_spelling_allowlist_is_only_exact_diacritic_changes():
    def plain(value):
        return ''.join(c for c in unicodedata.normalize('NFD', value) if not unicodedata.combining(c))
    assert len(CORRECTIONS) == 44
    for old, new in CORRECTIONS.items():
        assert old != new and plain(old) == plain(new)
        assert current_display_spelling(old) == new
    assert current_display_spelling('fuera de ambito distinto') == 'fuera de ambito distinto'


def test_spelling_migration_never_changes_source_or_computational_state():
    original = {'source_code': 'fuera de ambito', 'line_text': 'fuera de ambito',
                'caller_source_code': 'fuera de ambito', 'count': 5,
                'heap': [{'key': 2, 'next': 'N2'}], 'scope': 'F1',
                'variables': [{'meaning': 'fuera de ambito'}]}
    migrated = current_display_spelling(original)
    assert migrated['variables'][0]['meaning'] == 'fuera de ámbito'
    for key in ['source_code', 'line_text', 'caller_source_code', 'count', 'heap', 'scope']:
        assert migrated[key] == original[key]
    for key, bad in [('count', 4), ('heap', []), ('scope', 'F2')]:
        mutated = deepcopy(original); mutated[key] = bad
        assert current_display_spelling(mutated) != migrated
