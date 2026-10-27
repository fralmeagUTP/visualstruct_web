# Sorting test reconciliation, 2026-10-27

All changes in this scope are tests, test observers and ordinary test fixtures. No sorting production code or protected C/H was changed. Historical native observations, failure injection, memory ownership, exact states/events, history/replay and downloaded caller checks remain required.

## Portability and current UI contracts

- Recorded OpenSpec inputs use the verified fixture resolver instead of assuming an unarchived checkout path.
- Direct C/H transport comparisons normalize only CRLF versus LF; historical source digest guards remain in place.
- Windows subprocesses explicitly emit UTF-8. The archived main prototype receives the real repository/test import roots without editing the archived script.
- Browser observers select the classroom history/main tab before downloading its actual caller, and count the existing controls across their current classroom containers.
- Sorting help retains its glossary concepts and now presents eleven collapsible algorithm cards, each with four pedagogical sections.

## Preserve tests while removing repeated work

The original radix 24 parameterized checks still cover all eight original inputs and the same native/result/event/metric assertions. Their module fixture lazily shares one real run per selected input instead of repeating it three times.

The native/API baseline still checks eleven algorithms times ten original inputs (110 cases), strict C17 compilation, both API modes and state/history after GET. Each selected algorithm is observed lazily, keeping the existing 120-second subprocess limit. The previous unconditional 110-case fixture took 112 seconds in one run and timed out in another; the full selected-algorithm validation passed all eleven parameters in 171.67 seconds, with radix alone taking 82.77 seconds. No extreme case or timeout gate was removed.

## Traceable historical-test successors

`tests/fixtures/sorting-history/*-test-migration.json` bind exact published Git sources from commit `dde0d95691482e7c6db1922d0983ef287479dacf`, including Git blob identity and SHA-256. Snapshots end in `.py.snapshot` and cannot be discovered as pytest modules.

Original declared hashes remain unchanged. Where the declared preimage was not recovered (mergesort, counting and heapsort), the receipt explicitly says so and identifies the distinct authentic published source. Burbuja, quicksort and shell additionally bind authentic archived-before snapshots. The successor guard compares the entire AST, allowing only the declared fixture import/read adapters, exact known OpenSpec archive relocation and exact CRLF/LF read comparison adapters. All cases, assertions and other behavior must remain the same. Positive and tampering-negative controls cover all six successors.

## Evidence

Logs are retained in the parent task workspace. Counts below overlap and must not be added together.

| Validation | Result | Log |
| --- | --- | --- |
| All eleven native/API algorithm parameters / 110 original cases | 11 passed, 171.67 s | `sorting-lazy-baseline-final.log` |
| Shared radix native/result/control/value-max checks | 24 passed | `radix-shared-observation-validation.log` |
| Actual downloaded main/C/H, eleven methods and empty/reset | 12 passed | `sorting-all-main-current.log` |
| Actual Intercambio/Selection forward/reverse replay and native state | 12 passed | `sorting-live-native-replay.log` |
| Actual coarse browser runs/reload/no extra POST | 3 passed | `sorting-coarse-browser-final.log` |
| Six provenance successors, negative controls, quicksort/shell instruction tests | 40 passed | `sorting-tail-provenance-final.log` |
| Heapsort baseline native/ownership/source checks | 26 passed | `sorting-heapsort-final.log` |
| Remaining downloaded C/H and Doxygen transport checks | 4 passed | `sorting-tail-eol-final.log` |
| Current sorting routes and eleven pedagogical help cards | 7 passed, 1.24 s | `sorting-routes-final2.log` |
| Heapsort instruction/native observer preservation after authentic fixture recovery | 14 passed, 5.83 s | `sorting-heap-instructions-final.log` |

Initial failures remain in `sorting-native-initial.log`, `sorting-additional-current.log`, `sorting-final-remaining.log` and `sorting-tail-current.log`. Later focused logs supersede their repaired failures; these are not claims that the initial batches were green.

The global historical `review.md` reference mismatch remains strict and is owned by integration. A sorting test run is not a substitute for complete CI on the final published commit.

The fixture owner recovered the authentic `visible-sorting-heapsort-baseline-low/native-final-second/native.jsonl` (198,774 bytes, SHA-256 `8f6e3871ce0d2511673c79c1885518889da7d0305cc239455b5a8fc11bab5921`). The strict mechanical observer preservation check and all fourteen heapsort instruction tests passed in a fresh process after extraction. No replacement oracle was generated.
