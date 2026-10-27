"""Finite actual UI, caller and measured resource evidence for priority clear."""
from pathlib import Path
import json,hashlib,re
E=Path(__file__).resolve().parents[1]/'openspec/changes/archive/2026-10-13-audit-local-quality-and-unified-controls/evidence/visible-priority-queue-limpiar-baseline-completion-low'
M=E.parent/'visible-priority-queue-limpiar-instructions-medium'
from scripts.published_test_inputs import audit_input_path
if (audit_input_path(M/'caller-ownership/report.json')).exists():E=M
def read(name):return json.loads((audit_input_path(E/name)).read_text(encoding='utf-8-sig'))
def test_eight_actions_both_views_reverse_exact_no_redispatch_and_five_sections():
 rows=read('browser/report.json');assert len(rows)==4 and sum(r['actions'] for r in rows)==8
 assert sum(r['forward_same_trace_two_views'] for r in rows)==(296 if E==M else 280) and sum(r['back_same_trace_two_views'] for r in rows)==(280 if E==M else 264)
 assert all(r['five_numbered_sections_match'] and not r['JS_errors'] and r['extra_POSTs']==0 and r['history_reload_equal'] for r in rows)
def test_reload_keeps_exact_prepared_cleanup_trace():
 assert all(r['reload_trace_equal'] for r in read('browser/report.json')),'All four prepared cleanup traces disappear after reload'
def test_four_actual_DOM_mains_C17_repeated_clear_ownership_balanced():
 rows=read('caller-ownership/report.json');assert len(rows)==4 and sum(r['alloc_free_live'][0] for r in rows)==sum(r['alloc_free_live'][1] for r in rows)==8
 for r in rows:
  p=E/'actual-callers'/r['case']/'main.c';assert r['strict_C17_original'] and r['DOM_body_unchanged'] and hashlib.sha256(audit_input_path(p).read_bytes()).hexdigest()==r['sha256']
  assert len(re.findall(r'^    cp_vaciar\(&cp\);$',audit_input_path(p).read_text(encoding='utf-8-sig'),re.M))==2 and r['alloc_free_live'][2]==0
 assert sum(len(r['NULL_faults']) for r in rows)==8
 assert all(f['alloc_free_live'][0]==f['alloc_free_live'][1] and f['alloc_free_live'][2]==0 for r in rows for f in r['NULL_faults'])
def test_caller_failed_allocation_returns_failure_without_false_applied():
 rows=read('caller-ownership/report.json');assert all(f['exit']!=0 and not f['caller_prints_applied_even_after_failed_allocation'] for r in rows for f in r['NULL_faults'])
def test_actual_main_documentation_verified_beyond_zero_warnings():
 d=read('caller-doxygen.json');assert d['warning_lines']==0 and len(d['main_symbols_in_XML'])==4
 assert all(m['documented'] for m in d['main_symbols_in_XML']),'Four actual main symbols present but undocumented'
def test_finite_instrumented_resources_have_eight_samples():
 d=read('resources.json');assert len(d['calls'])==8 and {r['case'] for r in d['calls']}=={'empty','single','multi','reinsert'}
 assert all(r['python_peak_bytes']>=r['python_current_bytes']>=0 and r['response_bytes']>0 and r['elapsed_instrumented_seconds']>0 for r in d['calls'])
