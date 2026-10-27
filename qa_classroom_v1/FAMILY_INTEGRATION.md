# Five-family classroom integration — author evidence

Scope: only `static/js/{sorting,sequential,hierarchical,graph,hash}.js` in this v1 copy. Shared controller/CSS/base imports/export belong to runtime owner. No backend, trace producer or C/H changes. Mount after existing initialization, preserve render target IDs and event handlers; Graph old auto-fit yields to shared manual zoom.

Each family connects existing visual/code/results to shared controller. Auxiliary memory is optional; sequential TAD nodes are explicitly NOT classified as auxiliary memory. Existing source/results nodes are moved, not cloned. Console/main/TAD panels accessible without technical-toggle dependency.

Main copy reads raw generated source retained in `history.dataset.rawCode`, not concatenated span/OL text. Stack async source retains existing version guard. Copy getters read latest render, including empty/unavailable states. Console copy uses producer raw stream when available; existing line-mode uses newline-separated displayed lines (no invented final newline). Empty-console placeholder is excluded. This does not change source stdout or current renderer semantics.

## Reproducible checks
- `node --check static/js/<family>.js`: all five PASS.
- `node qa_classroom_v1/test_family_hooks.js`: all five hooks/live getters/sequence TAD visibility PASS.
- `node qa_classroom_v1/test_console_copy.js`: five line-mode renderers repeated7/3/7, empty and raw UTF8/newlines PASS.
- `node qa_classroom_v1/test_book_stdout_copy.js`: raw normal/no-trace text + copied bytes exact, empty copy excludes placeholder PASS.
- `../../visualstruct_prueba_local/.venv/bin/python qa/frontend_main_audit.py`: nine mains exact and diagnostic modes compile/execute PASS; creates local fixtures outside app in v1 parent.
- `python qa_classroom_v1/test_raw_main_compile.py`: nine actual main-history copy payloads compile C17-Wall-Wextra-Werror-pedantic and execute. This tests main.c, NOT arbitrary sidebar C snippets as standalone programs.
- Prior canonical frontend result/handler/retired-reference/label/active-field suites pass unchanged.

Old `qa_convergence/test_book_frontend_stdout.js` mock lacks DOM `dataset` and fails after new copy metadata assignment. Its identical assertions plus DOM-faithful dataset and copy assertions are retained in the v1 test; do not claim old entire suite passes. No production fallback was introduced merely to accommodate an incomplete mock.

Gate after PASS. Native browser dimensions, zoom/pan across frames and actual copy/dialog/export are independently pending auditor; author does not own CUA. No visual PASS claimed by these DOM/mocked tests.

## 11:37 iteration from measured ABB9
Description retained in optional identity disclosure; guided examples retained in optional panel (same controls/IDs), operation arguments remain primary. Results no longer inherit the old hierarchical hidden panel. Five Flask routes render200 with unique IDs and shared imports.

Lead authorized exactly two old mock corrections: only add `dataset:{}` to simulated console elements in `qa_convergence/test_book_frontend_stdout.js` and `qa/test_real_stdout.js`; assertions unchanged, byte-exact baselines at `../qa_independent/baseline_*.js`, diffs here. Canonical stdout test now PASS. Five applicable older stdout cases PASS via `node --test --test-name-pattern='host feedback|hierarchical fast|non-printing' qa/test_real_stdout.js`. Sixth old Graph-create test extracts code from the removed pre-book handler and remains incompatible; it was not changed or claimed passing. Canonical actual-handler execution test covers current create/normal behavior separately.

11:39: third authorized mock-only correction `qa/test_stdout_raw_renderer.js` adds dataset, original saved to `../qa_independent/baseline_test_stdout_raw_renderer.js`, exact diff here. Full `sh qa_convergence/run_non_graph_node.sh` exited0, log `non_graph_node.log`. Runner intentionally excludes pre-book Graph tests and selects applicable hierarchical cases from mixed stdout suite; this is not an all-tests claim. Backend `app/` and `docs/tads_C/` compared byte-identical to frozen v0 at this point (excluding Python caches).

11:43 CVUI001 Pila: move existing `section.seq-execute` outside Preparar, immediately before workspace; retains existing control nodes/handlers. New class `.classroom-execution-controls` lets shared CSS sticky bounds follow entire classroom rather than short preparation card. Existing explanatory paragraph remains in an optional control-help disclosure. Clear legacy `seq-pilot-collapsed` on results ancestors so all six sequential result tabs are available; no stdout/content change. Browser retest pending.

11:47 CVUI006 Sorting: move the existing counter/status nodes into the existing sticky execution toolbar, preserving IDs and live references. Hook test asserts identity; five sorting mutation/reset/concurrency tests PASS. Shared owner separately corrected code-layout/index CSS. Browser retest pending.

11:53 CVUI009 Hash: remove redundant Estado visual heading; filter/field-display controls retain IDs and handlers inside optional closed Opciones de representación. Minimap remains complete and visible; primary table/buckets are not hidden. Hook upgrades cached template by moving the same nodes. Shared CSS owner handles label font14 and scene budget; export owner notified new options-only wrapper may be omitted from clone. Five template and hook tests PASS; native sizing retest pending.
