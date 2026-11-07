# CI repair round 6 Graph interpreter replay

This candidate reduces redundant interpreter work while preserving the existing 200 ms reconstruction gate. The integrated semantic checks pass locally, but performance on the new CI head remains to be measured. This is a product change in the shared Graph interpreter, which also serves the Sorting caller; it is not merely a benchmark adjustment.

Base commit: `87d547cf17110e53f91f886cab6f06c952872f0b`.
Base tree: `772f0eb0c1feca868938c1d3b8d8c41da3af08de`.

## Results from the exact base commit

- General Chromium: 568/568 PASS, with 1,704 complete official events. The dedicated Graph and Firefox jobs, C17/sanitizers, Caller, delivery checks and Python 3.12 allocation checks also passed.
- Unit: 6,875 PASS and four failures across 6,879 IDs. Three are preserved historical gates; the fourth is Graph reconstruction p95 at 217.598 ms, above the unchanged 200 ms limit. Median was 215.587 ms.
- Coverage: 7,052 call PASS, 18 call FAIL and two setup failures across 7,072 IDs. These are exactly the 20 historical gates. The aggregate coverage gate was skipped, not approved.
- The Graph visible-operation consumer and both deterministic fixture controls added in round 5 passed in unit and coverage.
- All twelve streams agree with their summaries, with complete non-overlapping unions. All 24 synthetic screenshots match bytes previously inspected from actual pixels; no new visual change was found.

Exact-head runs: [Unit and Integration](https://github.com/fralmeagUTP/visualstruct_web/actions/runs/42332839370), [E2E](https://github.com/fralmeagUTP/visualstruct_web/actions/runs/42332839421), [Caller](https://github.com/fralmeagUTP/visualstruct_web/actions/runs/42332839244), and [C17](https://github.com/fralmeagUTP/visualstruct_web/actions/runs/42332839282). These results belong to the base, not to the candidate that follows.

## Diagnosis and bounded change

The performance failure is retained as a real failure of the existing gate. It is not evidence of a product regression introduced by round 5: product bytes were unchanged, and all five family medians rose by approximately 1.37–1.44 times relative to 39b. Profiles retain the same work counts across those runs. The result shows insufficient margin on this runner; it is not discarded as noise.

Only `app/domain/graph/book_c_subset.py` changes product implementation:

1. Four value-copy sites bypass `deepcopy` only for exact `int`, `str`, `bool`, `None` and `Reference` values whose existing copy semantics are identity. Aggregates, subclasses and unknown types still use `deepcopy`, including its memo, cycles and custom methods. Type checks use identity, not equality.
2. Six comparison operators execute directly, without constructing six lambdas and a dictionary on every comparison. Operand order and evaluation count are preserved.
3. Reading a pointer does not construct a retired-pointer search when the retired list is empty. Nonempty-list, expired-reference and uninitialized-read checks remain.

The canonical C algorithms, all source C/H files, ASTs, snapshots, emitted operations, event budgets, replay policy and caches are unchanged. The helper adds no mutable global state. Sorting is included because its caller machine inherits from this interpreter.

The existing `source_contract` remains the literal `graph-book/v1`. The separate `source_sha256` derives from the unchanged canonical C source. Sessions retain commands rather than interpreter objects; no persistent signature or session format is changed. The review found no active byte pin on this Python module. No historical approval receipt or pin was updated to admit the change.

## Measurements and uncertainty

The existing benchmark remains byte-identical: five measured iterations per family, 300 history operations, 300 replay operations and a 200 ms threshold. Five final base/candidate pairs used fresh processes and alternating order on local Python 3.12.14:

| Pair | Base Graph p95 ms | Candidate Graph p95 ms | Reduction |
|---|---:|---:|---:|
| 0 | 93.248 | 94.431 | -1.27% |
| 1 | 105.767 | 84.778 | 19.84% |
| 2 | 113.242 | 94.492 | 16.56% |
| 3 | 114.483 | 89.610 | 21.73% |
| 4 | 106.037 | 96.571 | 8.93% |

The median paired reduction is 16.56%, but one pair worsened. All pairs are retained. The local host and Python version differ from CI, so this percentage is not extrapolated to the failing 217.598 ms result. The final integrated local gate passed with Graph median 86.425 ms and p95 87.632 ms; this is not a CI margin claim.

The instrumented profile shows 22,300 fewer `deepcopy` dispatches, from 190,525 to 168,225, while retaining 130,890 recursive copy calls and all other approved work counters. Instrumented profile times are not used to decide the performance gate.

## Integrated semantic verification

- 273 distinct tests passed together in 187.52 seconds. The real partition plugin, a relative diagnostics directory and an unset `NODE_PATH` produced exactly 819 ordered official events, identical to the summary. The benchmark ran without coverage instrumentation.
- The 88 new controls also passed under pytest-cov, with 264 complete events. These are a repeated subset of the 273, not additional unique cases.
- Coverage includes scalar/reference identity, nested aggregates and aliasing, cycles, custom copy methods and adversarial metaclasses, all comparators, evaluation order, short circuiting, errors, allocation failures, ownership, callbacks, trace and observer modes, six Graph algorithms, Sorting callers, checkpoints, HTTP history preservation and concurrent sessions.
- Existing C17 checks for Graph vertices/DFS/main and Sorting caller stdout remain in the selected suites. Finite interpreter-to-interpreter comparisons are not presented as additional independent compiled-C proof.
- Independent integration review ran 103 checks, compared 115 base/candidate scenarios and rejected five deliberately incorrect mutations. Those checks overlap other evidence and are not added to the integrated count.
- Full collection retains every one of the 7,649 base IDs and adds 88, for 7,737. The exact general Chromium selection remains the same 568 IDs. Existing tests, workflows, benchmark and thresholds are unchanged. All 73 C/H files in the base tree are byte-identical, including the 26 canonical teaching files.
- An existing retirement test regenerated a fixture. Its generated bytes and pre/post hashes were retained for review, then the exact base fixture was restored. It is not part of this patch.

The two-file implementation tree is `e99e47ece34813dbd936abb2244a34e689374827`; this report adds documentation only. Local runtime is Python 3.12.14. Python 3.10 syntax was checked; runtime validation requires the new exact-head CI.

## Remaining limits

Local Chromium remains not run. The candidate needs its own CI, including both consumers and the unchanged timing gate. No CI run was cancelled or repeated to obtain a favorable result. If the new head still exceeds the limit, that result remains a failure to diagnose. The 20 historical evidence/contract gates remain intact, so this candidate does not claim globally green CI, merge approval or a VPS deployment.
