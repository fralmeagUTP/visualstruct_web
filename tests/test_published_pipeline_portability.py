"""Integrity and coverage properties of publication packaging, not product campaigns."""
from types import SimpleNamespace
import hashlib
import json
from pathlib import Path
import zipfile
import pytest
from scripts.pytest_e2e_partition import partition

ROOT = Path(__file__).resolve().parents[1]

def test_partitions_preserve_all_cases_once_and_ignore_collection_order():
    items = [SimpleNamespace(nodeid=f"tests/test_scope.py::test_case[{index}]") for index in range(101)]
    shards = [partition(items,index,4) for index in range(4)]
    actual = [item.nodeid for group in shards for item in group]
    assert sorted(actual) == sorted(item.nodeid for item in items)
    assert len(actual) == len(set(actual)) == 101
    assert max(map(len,shards))-min(map(len,shards)) <= 1
    assert [[i.nodeid for i in partition(list(reversed(items)),index,4)] for index in range(4)] == [[i.nodeid for i in group] for group in shards]

@pytest.mark.parametrize("index,count",[(-1,4),(4,4),(0,0),(True,4)])
def test_invalid_partition_does_not_silently_drop_cases(index,count):
    with pytest.raises(ValueError): partition([],index,count)

def test_packaged_inputs_have_exact_declared_bytes_and_no_private_stores():
    folder = ROOT/"tests/fixtures/published-audit-inputs"
    manifest = json.loads((folder/"manifest.json").read_text(encoding="utf-8"))
    archive = folder/"inputs.zip"
    assert hashlib.sha256(archive.read_bytes()).hexdigest() == manifest["archive_sha256"]
    with zipfile.ZipFile(archive) as package:
        assert len(package.infolist()) == len(manifest["files"])
        assert set(package.namelist()) == {row["path"] for row in manifest["files"]}
        for row in manifest["files"]:
            assert not any(part in row["path"] for part in [".flask_session",".env","source-package"])
            assert ".." not in Path(row["path"]).parts
            digest = hashlib.sha256(); size = 0
            with package.open(row["path"]) as source:
                for chunk in iter(lambda:source.read(65536),b""):
                    digest.update(chunk); size += len(chunk)
            assert digest.hexdigest() == row["sha256"] and size == row["bytes"]
            current = ROOT / row["path"]
            if "/evidence/" not in row["path"] and current.is_file():
                assert current.read_bytes().replace(b"\r\n",b"\n") == package.read(row["path"]).replace(b"\r\n",b"\n")
