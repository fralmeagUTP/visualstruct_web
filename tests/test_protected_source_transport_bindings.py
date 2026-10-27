"""CRLF transport is allowed; changed C and approval content remain rejected."""
import hashlib,json
import pytest
import _audit_approved_source_supersessions as bindings

def digest(raw):return hashlib.sha256(raw).hexdigest()

@pytest.fixture
def source_binding(tmp_path,monkeypatch):
    relative='docs/tads_C/probe.c';source=tmp_path/relative;source.parent.mkdir(parents=True)
    source.write_bytes(b'int value;\r\n')
    approval=tmp_path/'approval.md';approval.write_bytes(b'Approved version.\r\n')
    authority=tmp_path/'downloads.json';accepted=digest(b'int value;\n')
    authority.write_text(json.dumps([{'filename':'probe.c','sha256':accepted}]),encoding='utf-8')
    row={'allowed_historical_sha256':['historical-exact-version'],'accepted_current_sha256':accepted,
         'reference_bindings':{'approval.md':digest(b'Approved version.\n')},
         'authority':{'path':'downloads.json','kind':'downloads','filename':'probe.c'}}
    monkeypatch.setattr(bindings,'SUPERSESSIONS',{relative:row})
    return tmp_path,relative,source,approval,authority

def test_exact_crlf_transport_preserves_source_and_approval_bindings(source_binding):
    root,path,*_=source_binding
    bindings.assert_historical_protected_hash(root,path,'historical-exact-version')

@pytest.mark.parametrize('corruption',['source','approval','authority','historical'])
def test_nontransport_changes_fail_closed(source_binding,corruption):
    root,path,source,approval,authority=source_binding
    expected='historical-exact-version'
    if corruption=='source':source.write_bytes(b'int changed;\r\n')
    elif corruption=='approval':approval.write_bytes(b'Unapproved version.\r\n')
    elif corruption=='authority':authority.write_text(json.dumps([{'filename':'probe.c','sha256':'different'}]))
    else:expected='unknown-historical-version'
    with pytest.raises(AssertionError):bindings.assert_historical_protected_hash(root,path,expected)
