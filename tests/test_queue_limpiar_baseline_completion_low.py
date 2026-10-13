"""Complete finite Cola cleanup evidence: UI/reload and original DOM callers."""
from pathlib import Path
import json,hashlib,re
E=Path(__file__).resolve().parents[1]/'openspec/changes/archive/2026-10-13-audit-local-quality-and-unified-controls/evidence/visible-queue-limpiar-baseline-completion-low'
M=E.parent/'visible-queue-limpiar-instructions-medium'
if (M/'caller-ownership/report.json').exists():E=M
def browser():
 path=E/'browser/report-final.json' if E==M else E/'browser/report-main-extraction-corrected.json'
 return json.loads(path.read_text(encoding='utf-8'))
def test_browser_eight_actions_both_views_replay_without_redispatch_and_five_sections():
 rows=browser();assert len(rows)==4 and sum(r['actions'] for r in rows)==8
 assert sum(r['forward_same_trace_two_views'] for r in rows)==(176 if E==M else 160) and sum(r['back_same_trace_two_views'] for r in rows)==(160 if E==M else 144)
 assert all(r['five_numbered_sections_match'] and not r['JS_errors'] and r['extra_POSTs']==0 and r['history_reload_equal'] for r in rows)
def test_reload_restores_the_exact_prepared_cleanup_trace():
 assert all(r['reload_trace_equal'] for r in browser()),'History persists but all four prepared traces disappear on reload'
def test_four_real_DOM_mains_preserve_repeated_clear_and_balance_ownership():
 rows=json.loads((E/'caller-ownership/report.json').read_text(encoding='utf-8'));assert len(rows)==4
 assert sum(r['alloc_free_live'][0] for r in rows)==sum(r['alloc_free_live'][1] for r in rows)==8 and all(r['alloc_free_live'][2]==0 for r in rows)
 assert sum(len(r['NULL_faults']) for r in rows)==8
 for r in rows:
  p=E/'actual-callers'/r['case']/'main.c';source=p.read_text(encoding='utf-8');assert hashlib.sha256(p.read_bytes()).hexdigest()==r['sha256'] and r['strict_C17_original'] and r['DOM_body_unchanged']
  assert len(re.findall(r'^    cola_vaciar\(&cola\);$',source,re.M))==2
  assert all(f['alloc_free_live'][0]==f['alloc_free_live'][1] and f['alloc_free_live'][2]==0 for f in r['NULL_faults'])
 assert all(r['main_HTTP_status']==404 and len(r['actual_main_fragments_corrected'])==1 for r in browser())
def test_Doxygen_covers_documented_actual_main_symbols_not_only_warning_count():
 x=json.loads((E/'caller-doxygen.json').read_text(encoding='utf-8'));assert x['warning_lines']==0 and len(x['main_symbols_in_XML'])==4
 assert all(m['documented'] for m in x['main_symbols_in_XML']),'All four main symbols are present but have no documentation'
