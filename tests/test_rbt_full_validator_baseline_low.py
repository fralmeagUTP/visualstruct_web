"""Normative RN V3 regressions; failures expose approved pending implementation."""
import pytest
from _audit_rbt_full_validator_baseline_low import CASES,run
@pytest.fixture(scope='session')
def full_rn_report(tmp_path_factory):
 return run(tmp_path_factory.mktemp('rn-full-live-baseline'))
@pytest.mark.parametrize('index',range(len(CASES)),ids=[x[0] for x in CASES])
def test_full_rn_python_contract(full_rn_report,index):
 r=full_rn_report['cases'][index];assert r['python']==r['expected']
@pytest.mark.parametrize('index',range(len(CASES)),ids=[x[0] for x in CASES])
def test_full_rn_native_contract(full_rn_report,index):
 r=full_rn_report['cases'][index];assert r['native']==r['expected']
@pytest.mark.parametrize('index',range(len(CASES)),ids=[x[0] for x in CASES])
def test_full_rn_readonly_live_fixture(full_rn_report,index):
 r=full_rn_report['cases'][index];assert r['native_readonly'] and r['python_readonly'];assert r['native_allocations']==r['native_frees']==0
def test_full_rn_native_public_export(full_rn_report):
 assert full_rn_report['exported']
