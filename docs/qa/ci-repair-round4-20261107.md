# CI consumer follow-up: 7 November 2026

## Exact scope

This test-only follow-up is based on `cf7b2e7e07991dc358b912fcb8f8f4a1132ad1eb`, tree `42291f4115b995c9a4ea77a2689dd5d1b4d772d9`, in draft PR #7. It changes four browser-test consumers, their new full-controller regression support, and one workflow-budget assertion. Application code, templates, assets, canonical C/H, workflow selection, time budgets and performance thresholds are unchanged by this follow-up. It is not a merge or deployment approval.

## Evidence behind the changes

The earlier [48b E2E run](https://github.com/fralmeagUTP/visualstruct_web/actions/runs/42311207175) reached a terminal cancelled result. General Chromium recorded 554 call passes, four failures and ten cases without a call result after one partition was cut off. Its cancelled partition had 132 passes, no recorded failures, one setup-only case and nine cases not started. Its approximately ten-minute preparation and thirty-minute test execution coincide with the original forty-minute job budget; the log says cancelled rather than explicitly diagnosing its cause. The final setup occurred only 4.49 seconds before the cut, so there is no basis for calling that case hung.

The separately reviewed budget-only commit cf7 changed the four general Chromium budgets from forty to sixty minutes, preserving the Graph-specific forty, Firefox twenty, parallelism and every selected case. Its [E2E run](https://github.com/fralmeagUTP/visualstruct_web/actions/runs/42316780367) completed its first two general partitions with 284 passes and exact diagnostic streams, including the original Pila case and nine cases that had not started in the cancelled partition. Its third general partition then completed with 140 passes and the same ABB insertion and Sublista clear-query failures. The final general partition was not yet included in this preparation snapshot. Firefox and Graph succeeded. This does not attribute the difference solely to the larger budget or certify unreported partitions.

The four remaining failures in the terminal 48b run are ABB insertion and the three Sublista insertion/parent/clear-query consumers. They fail when replay returns to cursor -1. The complete Flask HTML and actual scripts reproduce the cause: after the structural renderer runs, the controller calls `ContextualHelp.frame(prefix, null)`, restoring the selected operation card. That card identifies the concrete operation, states its rule, and correctly says that no instruction has executed. The earlier renderer-only strings are not the final UI state. Memory projection, active scopes and cursor behavior remained correct.

The earlier local presentation regression omitted that controller step and did not certify the full browser circuit. This follow-up replaces only the stale initial-summary assertions with a literal, operation-specific card contract independent of the observed DOM. ABB's four initial assertions are also split onto separate lines for clearer diagnostics. All subsequent replay, scopes, heap, native caller, ownership, stdout and download assertions remain intact, as do the four original browser node IDs. Sorting and RN consumers are unchanged.

The larger budget also exposed a missed existing consumer: `test_ci_job_separation.py` still required forty minutes for general Chromium. Its complete module reproduced one failure and three passes before the change. This follow-up changes only that expectation to the approved sixty; Graph, Firefox and all other assertions remain unchanged. The prior budget preparation's ten focused checks had not covered this module. A search of tracked text found no other executable expectation of the general Chromium budget. The corrected real test accepted the valid workflow and rejected sixteen bounded mutations.

## Regression support and limits

The new regression loads real Flask HTML, all local page scripts, the actual controls and the complete API-produced traces in jsdom. It covers the selected operation card on preparation, full forward/backward replay to -1, and changing the selected operation and returning. It checks the exact state delivered to the renderer, DOM scopes and the DOM projection of current/linked modes. It does not claim complete heap-DOM verification or a new C-to-trace equivalence proof; those existing browser/native assertions are retained separately.

Independent review caught two observer gaps before publication: invalid fetch attempts could be caught without being counted, and clicking a view button did not prove that the mode changed. The reviewed increment records every request attempt before validation and requires exactly one throughout replay and operation changes. It also checks mode state, ARIA, active controls and rendered mode-specific content, including return from linked to current. The exact prior attacks now fail with the expected transport/view diagnostics. Seven added negatives cover extra or invalid requests, absent view handlers and frozen DOM despite a changed mode, in addition to four negatives that omit contextual help or its controller reset.

The final independent controller reproduction passed twelve tests across thirty-four fixtures: twenty-nine successful traces, five expected rejected operations and 2,295 observed states. Geometry-only browser APIs are shimmed and operation responses are supplied from the real Flask fixture. This is API/jsdom evidence, not Chromium navigation, rendering or network certification.

## Integrated checks

- Final integrated regression: 210 tests passed in 217.28 seconds under Python 3.12, with pytest-cov and the real partition plugin. The relative official directory contains exactly 630 events, identical in order and content to the summary, with setup/call/teardown passed for every selected ID. NODE_PATH was unset. Local packages use the pinned qa dependency layout already verified in the previous round; this is not a fresh Actions installation.
- The eight implementation/support paths match their independently reviewed final hashes. All 283 application/template/static/C-source paths, including all 26 canonical C/H files, match the published cf7 base byte for byte. Changed Python files parse as Python 3.10 syntax and the new Node harness passes syntax checking.
- Full collection retains all 7,635 base IDs and adds twelve new controller regressions, for 7,647 total. The 568 general Chromium IDs are exactly unchanged, including the four repaired consumers. Collection is not browser execution.
- The corrected workflow-consumer module passed all four tests in the integrated copy, and its independent review rejected sixteen changes to the real workflow contract. These checks overlap with the integrated regression and are not additive unique suite totals.

This document is added after the tested eight-path implementation snapshot and introduces no runtime behavior.

## Remaining gates and CI

The terminal [48b unit/coverage run](https://github.com/fralmeagUTP/visualstruct_web/actions/runs/42311207190) contains 6,862 unit passes and three historical failures across 6,865 IDs, and 7,038 coverage call passes, eighteen call failures and two setup failures across 7,058 IDs. All eight diagnostic streams match their execution summaries and cover every selected ID. The historical failures remain in the preserved inventory; no protected preimage, pin, assertion or test was removed or fabricated.

Graph passed the unchanged five-iteration, 300-operation, 200 ms gate in both observed runs: p95 176.711 ms on 48b and 189.491 ms on cf7. There was no performance implementation change, and runner variation remains relevant. The cf7 unit suite contains 6,861 passes and four failures: the three historical gates plus the stale budget expectation addressed here. Its other results must be read against that exact commit, not inferred from this local follow-up.

All twenty-four synthetic PNGs from 48b were checked: twenty are byte-identical to previously inspected base images and four were newly inspected. No new blocking visual issue was found. The known finite-viewport/panning limits remain, and screenshots do not replace failed or unexecuted browser cases.

New exact-head CI is required after publication of this follow-up. The twenty historical coverage/evidence gates remain explicit, and no global green or completed deployment is claimed. Local Chromium remains unavailable under the environment restriction; no workaround is reported as a browser pass. Main and the VPS remain unchanged by this work.
