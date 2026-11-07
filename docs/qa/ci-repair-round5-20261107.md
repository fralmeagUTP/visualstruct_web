# CI repair round 5: deterministic Graph fixture

Base commit: `39b16851719217fdb00d348e5f6a097338bf7e05`.
Base tree: `3c58851586521b685887049cb697c884d7f3c1bf`.

## Exact-head CI findings

The base run exposed an intermittent failure in `tests/test_interpreter_subroutines_cross_module.py::test_trace_contract_all_visible_graph_methods`. The same stable test ID passed on cf7 and 48b. Its fixture generated a random six-vertex graph without an explicit seed, then required a complete step-mode trace from every visible operation.

The CI record retained the TypeError location, but not the chosen seed or the absent-trace reason. The following local reproduction explains the failure mechanism; it does not establish the seed used by CI or attribute the failure to the preceding controller tests.

The base E2E run completed successfully: all 568 general Chromium cases passed, with 1,704 official events and a complete, non-overlapping union. The 30 earlier browser failures now pass, including all four initial-card consumers repaired in round 4. The dedicated Graph and Firefox jobs also passed. All 24 synthetic screenshots were reviewed: 23 match previously inspected bytes and one new narrow-stack image received an actual-pixel review, without a new blocking visual finding.

The unit union completed with 6,873 PASS and four failures: the three preserved historical gates and the random Graph consumer described here. C17/sanitizers, Caller (57 cases), the Python 3.12 allocation check (26 cases), and delivery checks (7 cases) passed. Graph reconstruction p95 was 150.742 ms; the 200 ms threshold, five measured iterations per family, and 300-operation histories/replays across all five families were unchanged. Coverage completed with 7,049 call PASS, 19 call FAIL and two setup failures across 7,070 selected IDs. Its 21 failed IDs are exactly the 20 preserved historical gates plus the same random Graph consumer. The unit total is 6,877 selected IDs. All 12 unit/coverage/general-Chromium streams match their summaries, and each union is complete and non-overlapping. The budget expectation passes in unit and coverage. The aggregate coverage gate remains skipped because the underlying tests are not all green; no global green result is claimed.

Exact-head runs: [E2E](https://github.com/fralmeagUTP/visualstruct_web/actions/runs/42323750000), [Unit/Integration](https://github.com/fralmeagUTP/visualstruct_web/actions/runs/42323749993), [Caller](https://github.com/fralmeagUTP/visualstruct_web/actions/runs/42323750041), and [C17/sanitizers](https://github.com/fralmeagUTP/visualstruct_web/actions/runs/42323750116). These results belong to the base commit, not to this unexecuted follow-up head.

## Reproduction and repair

Seed 26 leaves 18 arcs before Kruskal and emits 4,570 events. The unchanged service rejects the step-mode capture above its 4,000-event limit, preserving the previous history and visual state and returning no execution trace. The unmodified test then indexes that absent trace in `_book_frame_oracle.py:48` and raises TypeError.

The repair changes only two test files. The original consumer specifies seed 0 and checks trace availability with an operation-specific diagnostic before invoking the unchanged oracle. It retains all 19 visible operations, the original payload adjustments, history updates and six-vertex fixture. The remaining AST is unchanged. The same-process before/after reproduction forces the ambient RNG to 26: the original consumer fails, whereas the repaired consumer executes all 19 visible operations, makes 25 service calls including setup, and does not consult the ambient RNG.

Two added tests cover all six algorithm families under seed 0 and preserve the dense seed 26 rejection. The latter checks the 4,000 limit, actual 4,570-event overflow, absent trace, and exact state/history preservation. The fixture has an isolated vertex, so Prim/Kruskal retain the disconnected result rather than inventing a successful spanning tree. The normal-mode comparison uses the same canonical interpreter through the adapter; it is not new independent validation against compiled C.

## Integrated validation

- 26 tests passed in 349.61 seconds in the final isolated implementation copy, including all 12 controller regressions from round 4, the complete cross-module module, both new Graph tests and existing capture/engine budget controls.
- The real partition plugin and pytest-cov produced exactly 78 official events. Every selected ID has one passing setup, call and teardown event, and the ordered JSONL equals the execution summary. The diagnostics directory was relative and `NODE_PATH` was unset.
- Full collection contains 7,649 IDs, retaining all 7,647 base IDs. The exact general Chromium workflow selection remains the same 568 IDs.
- All 289 protected application, C/H, workflow, partitioner and oracle paths are byte-identical to the base. No product code, browser budget, event limit or historical gate changed.
- The author and independent reviewers separately reproduced the failure and checked the narrow patch. Their counts overlap the integrated run and are not added to it.
- Local execution used Python 3.12.14. Python 3.10 syntax was checked separately; runtime confirmation on Python 3.10 requires the new exact-head CI.

The two-file implementation tree is `0da85dc0a08f16d1ddcc4344643e8d10ce76f74b`. This report adds documentation only.

## Limits

Local Chromium remains not run. API/jsdom and interpreter checks are not browser or independent native-C certification. The 20 historical evidence/contract gates remain intact and do not become approved merely because this fixture is reproducible. A new exact-head CI run is required. This review update does not merge the draft PR or deploy to the VPS.
