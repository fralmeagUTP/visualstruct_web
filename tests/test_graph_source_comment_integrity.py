"""The authorized comment revision does not relax canonical source integrity."""
import hashlib
from pathlib import Path
import pytest
from app.domain.graph import book_source


def test_comment_revision_still_rejects_any_source_drift(tmp_path, monkeypatch):
    source = book_source.canonical_source()
    book_source.verify_source(source)
    assert hashlib.sha256(source.encode('utf-8')).hexdigest() == book_source.HASHES['tad_grafo.c']
    assert book_source.HASHES['tad_grafo.h'] == '8381b5d31af769826d08b4158c7057934fd7e2739e3e34dbc9a4fcce374556f7'
    with pytest.raises(ValueError, match='Only byte-exact canonical'):
        book_source.verify_source(source + ' ')
    directory = tmp_path / 'docs' / 'tads_C'
    directory.mkdir(parents=True)
    for name in book_source.HASHES:
        (directory / name).write_bytes((book_source.ROOT / 'docs' / 'tads_C' / name).read_bytes())
    (directory / 'tad_grafo.c').write_bytes(source.encode('utf-8') + b' ')
    monkeypatch.setattr(book_source, 'ROOT', tmp_path)
    with pytest.raises(ValueError, match='Book graph source drift: tad_grafo.c'):
        book_source.canonical_source()
