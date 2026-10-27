# Canonical book graph engine — bounded verification

## Source and API
Only new `book_source.py`, `book_c_subset.py`, `book_trace.py` and owned QA were implemented. Legacy engine remains untouched. Canonical C/H SHA256 remain `13c1bd9a...` / `b7bc7f3a...`; loader checks exact bytes. Parser covers all44book functions, known enum/struct ABI, compound literals, aggregate/declarator semantics, unevaluated sizeof expressions, longlong, pointer/reference lifetimes, malloc/calloc/free and control flow. It rejects noncanonical source and never calls a fallback graph algorithm.

`BookSession(vertices,arcs,marks,trace=False,callback=None,fail_allocation=None)` seeds insertion order. `.call('grafo_...', arguments)` materializes returned lists and returns status/output/ownership, exact source, memory and graph_after in C HEAD order. `.free_result` is explicit caller action and rejects graph-borrowed lists. Private helpers are testable through machine.invoke. Normal and trace share evaluator. Integer snapshots above2^53 use `{'exact_integer':'decimal'}`, calculations remain checked integers.

`BookTraceCollector(operation_name,payload,before_state,source_code=None)` exposes `.callback(event,before,after)` and `.finish(after_state,success,message,compact=False,result=None)`. With `BookSession(trace=False,callback=collector.callback)`, no duplicate raw transitions/events remain in session. Full steps are interned and GraphLogicalTrace/snapshot_pool transport preserved. Host prepare/receipt and final API publication have no canonical line (None in steps, -1 in engine event), never invented C. Source C lines remain literal canonical bytes. Trabajo/arrays/conditions/memory are projected from real snapshots; raw directed arcs and asymmetric undirected intermediate states are retained, not completed by invented inverse arcs.

## Verification
- Owner engine14tests PASS, including ABI static assertions compiled with C17 warnings-as-errors, atomic failure of every allocation reachable in selected fixtures, cleanup/ownership, states0..6, NULL+OK, longlong/safe-sum boundaries, source closure, reference lifetime, normal/trace equality and multicall continuity.
- Independent oracle313cases PASS:72base +241malloc/calloc failures; compares state/output/list order/marks/graph state/attempts/alloc/free/live. Native final cleanup0.
- Independent direct sumar_seguro6cases PASS. **GRAFO_RANGO is not claimed as public end-to-end covered** for finite small graphs.
- Independent14traces/4882transitions +multicall1772transitions PASS with source coordinates and normal/trace agreement; cleanup14PASS.
- Reviewer found235initial discontinuities (frame removal/allocation attempts); fixed actual mutation placement with explicit function_exit and allocate events. Before evidence retained by auditor.
- Wrapper5tests PASS:8operations stream/replay equivalence, pool wire roundtrip, source/memory/state continuity, pre-C rejection vs executed C error, longlong Trabajo projection and no invented reverse arc after caller second-call failure. Separate independent wrapper review in progress.

## Resource evidence / not yet certified
Streaming5vertex sparse Dijkstra:1263steps,2.204s,4.43MBwire,93.8MiBpeakRSS.
Streaming8vertex sparse Dijkstra:2553steps,5.639s,8.67MBwire,149.7MiBpeakRSS.
Both retain0raw transitions/events in session. These are bounded probes, not all-graph performance certification.
Count-only15vertex/210rawarc Kruskal:255403Cevents,2.04s,0retained event log. Full snapshots were intentionally NOT constructed: monolithic extrapolation is unsafe. Parent notified: dense paging/storage or explicit pre-capture pedagogical budget is necessary; do not sample/truncate events or call15vertices universally safe.

No server/browser action, C/H edit or old-copy modification performed.

## Authorized preflight budget extension
`BookSession(event_limit=4000, trace=False)` provides a disposable, no-snapshot/no-event-log preflight. It raises `BookEventLimitExceeded(limit, attempted_events=4001)` before the next event's mutation. Earlier mutations exist only on the disposable model; callers MUST discard it on limit. All host and canonical events count. Accepted calls expose cumulative `event_count` and per-call `call_event_count`; `memory=None` in this budget-only mode avoids even a final snapshot. Optional `event_observer(event)` receives events without snapshots. Trace/callback sessions still capture complete states normally. No source C or algorithm semantics changed.
Budget4tests PASS: observer equivalence, zero snapshot calls, inclusive limit, multicall boundaries, and dense15/210Kruskal safely rejected at4001 with no retained logs. Lead integrates the guard on an adapter clone: step rejection preserves actual state/history; normal can execute without trace with explicit warning. No event truncation is a successful trace.

## Retired-pointer presentation correction (GB07)
Independent review found a live local `actual` still displayed `E2` as usable after `free(actual)`. Fixed only the projection: values now carry `historical_identity`, `usable:false`, `value_status:indeterminate_after_free`; cell scope remains alive until actual scope exit. `retired_references` lists only currently-live cells, not dead scopes. `dangling_references_checked:false` prevents certification of zero invalid aliases. Raw memory/instruction snapshots remain unchanged; `memory_display` gives safe heads/fields/return records for UI. Initial display uses the actual pre-instruction memory, with no future caller output cell.
Baseline dedicated test fails1/1; repaired passes. Independent3traces/698steps have unchanged raw states, memory, events and source, with102live-cell retired alias observations correctly labelled. Frontend owner confirmed actual fixture rendering and no false dangling0. Combined25tests PASS46.720s; final retired/budget5tests PASS0.475s. Independent review: `../qa_independent/INTEGRATION_REVIEW.md` (final source manifest refresh requested after two display-only consistency fields).
Updated8vertex sparse resource probe:2553steps,8.82s,8.82MBwire,150940KiBpeakRSS,0duplicate raw logs. Budget remains explicit4000events; no dense snapshots attempted.

Final independent display retest10:26 verified initial memory_display has no future caller cell and14BFS returned-retired observations are historical only. `integration-sources.json` wrapper SHA `a53220dce9fd8c33b8c4f65a142ee3518d4834f8ac01c9e186e57dc8dc0f71a6` matches current file (verified10:29). Engine/collector/budget/projection scope released; UI and package acceptance remain separate.
