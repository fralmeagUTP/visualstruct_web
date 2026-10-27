# Graph browser test migration, 2026-10-27

The historical BFS, DFS, Bellman-Ford, numeric algorithm and Prim caller browser
tests now exercise the active `graph-book/v1` application. The original case
inventories remain: eight BFS cases, eight DFS cases, three DFS caller cases,
three Bellman-Ford caller cases, four numeric algorithm cases and one Prim
symmetry test with both directed and undirected sessions (27 tests).

The shared browser contract in `tests/_canonical_graph_browser_contract.py`
checks every declared forward frame, every reverse frame, reset and final seek
for the instruction tests. It compares actual DOM source highlighting, complete
heap contents, each mirrored live-memory pane, variables and live call scopes,
auxiliary data, retired-object display, console output, graph projection and
pending/final messages with the canonical trace. Completed call scopes must be
disjoint from live scopes. The technical panels preserve the raw diagnostics
inside `details`; the test reads those descendants without changing product UI.

Replay and two reloads must make no operation POST. The visible `main.c del
historial` tab must match the current no-store HTTP source, and the real browser
download must match those bytes. Queries which execute C and return a failure
remain in history, including a missing start vertex, negative cycle, disconnected
Prim graph and asymmetric Prim graph. Repeated queries remain repeated calls.

Native evidence is separate from model evidence. The unchanged canonical C/H
download is hash checked, compiled with strict C17 warnings as errors, and run.
A second build adds translation-unit-only allocation wrappers and asserts
balanced allocations/frees and zero live owned allocations after cleanup.
Traversal endpoint status, order and graph marks are also compared against an
independent native harness. These checks do **not** claim native per-instruction
instrumentation or parity. Protected C/H, application runtime and CI gates are
unchanged by this migration.

## Validation

- Initial bounded run: Dijkstra passed; BFS/DFS exposed mirrored-memory and
  wrapped auxiliary selector assumptions in the new test helper; Prim exposed
  generated `estado_N` names and the canonical removal signature. The helper
  expectations were corrected after inspecting the actual renderer and C API.
- Corrected bounded run: BFS singleton and both Prim symmetry sessions passed,
  **2 tests in 65.47 seconds** (`traversal-e2e-bounded2.log` in the task directory).
- Full browser run: **27 passed in 1630.41 seconds (27 minutes 10 seconds)**,
  exit status zero (`traversal-e2e-full.log` in the task directory). It ran the
  six owned browser test files together, once, with isolated headless Chromium
  sessions. The run's per-case reports and downloaded callers are in
  `C:\Users\fralm\AppData\Local\Temp\pytest-of-fralm\pytest-91`.

Command (from the review checkout):

```text
python -m pytest -q tests/test_graph_bfs_instruction_e2e.py tests/test_graph_dfs_instruction_e2e.py tests/test_graph_dfs_caller_e2e.py tests/test_graph_bellman_ford_caller_e2e.py tests/test_graph_four_instruction_e2e.py tests/test_graph_prim_main_symmetry.py --tb=short
```

This is local audit-branch validation. It does not assert that these later test
changes are included in the frozen delivery commit, that remote CI ran them, or
that a VPS deployment happened. No additional test sweep followed this run.

This migration does not resolve or replace any historical audit-document hash
whose authentic bytes remain unavailable. Its functional browser/native
evidence is independent of that documentary integrity check.
