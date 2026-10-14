"""Finite E2E witness for real deferred export controls and transient anchors."""
import json
from pathlib import Path
import pytest
from _audit_js_deferred_exports import run_flows

pytestmark=pytest.mark.e2e

def test_js_deferred_real_exports(tmp_path):
 report=run_flows(tmp_path/'deferred.json')
 assert report['flows_requested']==11 and report['downloads_completed']==11
 assert all(case['status']=='OPERABLE_DOWNLOAD' and case['content_valid'] for case in report['results'])
 assert report['sibling_guard']['existing_toggle_operable']
 assert report['sibling_guard']['guard_allows_new_factory'] is False
 # Preserve the actual full report in the canonical evidence scope for bindings.
 target=Path(__file__).resolve().parents[1]/'openspec/changes/archive/2026-10-14-resolve-didactic-stack-c1-residuals/evidence/js-deferred-verified-results.json'
 target.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
