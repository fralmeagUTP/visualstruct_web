"""Portable, bounded fixture materialization retains all integrity checks."""
import hashlib
import json
from pathlib import Path
import zipfile
import pytest
from scripts import published_test_inputs as inputs

PREFIX='openspec/changes/archive/2026-10-13-audit-local-quality-and-unified-controls/evidence/sample/'

def package(tmp_path,monkeypatch,*,bad_file_hash=False,extra=False):
 folder=tmp_path/'package';folder.mkdir();files={PREFIX+'a.json':b'{"case":1}',PREFIX+'b.jsonl':b'{"event":"return"}\n'}
 with zipfile.ZipFile(folder/'inputs.zip','w') as archive:
  for name,raw in files.items():archive.writestr(name,raw)
  if extra:archive.writestr('undeclared.json','{}')
 manifest={'archive_sha256':hashlib.sha256((folder/'inputs.zip').read_bytes()).hexdigest(),'files':[{'path':name,'sha256':hashlib.sha256(raw).hexdigest(),'bytes':len(raw)} for name,raw in files.items()]}
 if bad_file_hash:manifest['files'][0]['sha256']='0'*64
 (folder/'manifest.json').write_text(json.dumps(manifest),encoding='utf-8')
 root=tmp_path/'checkout';root.mkdir()
 for key,value in {'ROOT':root,'PACKAGE':folder,'_manifest':None,'_registered':None,'_extracted':None,'_verified_archive':False,'_materialized':set()}.items():monkeypatch.setattr(inputs,key,value)
 return root,files

def test_one_requested_input_does_not_extract_unrelated_large_oracles(tmp_path,monkeypatch):
 root,files=package(tmp_path,monkeypatch)
 first=inputs.audit_input_path(root/(PREFIX+'a.json'))
 assert first.read_bytes()==files[PREFIX+'a.json']
 assert not (inputs._extracted/(PREFIX+'b.jsonl')).exists()
 assert (inputs.recorded_input_root()/(PREFIX+'b.jsonl')).read_bytes()==files[PREFIX+'b.jsonl']

def test_archived_alias_and_windows_separators_resolve_same_verified_bytes(tmp_path,monkeypatch):
 root,files=package(tmp_path,monkeypatch)
 old='openspec/changes/audit-local-quality-and-unified-controls/evidence/sample/a.json'
 assert inputs.audit_input_path(str(root)+'/'+old.replace('/','\\')).read_bytes()==files[PREFIX+'a.json']

@pytest.mark.parametrize('failure',['digest','file','undeclared'])
def test_integrity_failure_is_never_hidden_by_lazy_extraction(tmp_path,monkeypatch,failure):
 root,_=package(tmp_path,monkeypatch,bad_file_hash=failure=='file',extra=failure=='undeclared')
 if failure=='digest':
  with (inputs.PACKAGE/'inputs.zip').open('ab') as archive:archive.write(b'changed')
 with pytest.raises(ValueError):inputs.audit_input_path(root/(PREFIX+'a.json'))
