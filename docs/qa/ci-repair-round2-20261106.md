# CI repair, second review: 6 November 2026

## Scope

This is a follow-up to draft PR #7. Its base is `f1a9bebece2a0971f247b271e992ef7be5bd013c`, tree `63af79358ebd4f5c6697d04f09388936c7ee3144`. It is a diagnostic review candidate, not a deployment or a claim that all CI gates pass. Main and the VPS have not changed during this repair round.

## Exact-base CI

Remote status snapshot: 21:22 UTC on 6 November 2026. Later workflow results must be checked separately.

- [C17 and sanitizers](https://github.com/fralmeagUTP/visualstruct_web/actions/runs/42283290605): success.
- [Caller/code-reader](https://github.com/fralmeagUTP/visualstruct_web/actions/runs/42283290626): success, 57 passed.
- [E2E](https://github.com/fralmeagUTP/visualstruct_web/actions/runs/42283290621): failure. General Chromium selected 555 cases: 335 passed and 220 failed, including 22 setup failures. Graph-algorithms and Firefox succeeded.
- [Unit/Integration](https://github.com/fralmeagUTP/visualstruct_web/actions/runs/42283290588): pending final coverage result at preparation time. The four unit partitions completed with 6372 passes and 27 failures. Delivery regressions succeeded. Coverage partitions 0, 1 and 2 failed; partition 3 remained active. Partition 2 completed without timeout with 1639 passes, eight call failures and one setup error. Its nine failures map to six repaired unit cases and three already known historical gates, with no newly unclassified failure.

The comparison uses stable test IDs across all four Chromium partitions. All 516 cases from the original main run were retained. Of those, 128 changed from failed to passed, 202 still failed, 180 stayed passing, and six changed from passed to failed. The 39 newly selected cases added 27 passes and 12 failures. The six regressions are four allocation-error observer cases and two graph-neighbor observer cases; the follow-up fixes reproduced defects in these observers, while the six complete browser cases remain unverified until exact-commit CI.

## Repairs and preserved guarantees

- Allocation-error instructions explicitly expose the already generated caller stdout event mode. A missing continuation label renders a clear fallback rather than `undefined`.
- Hierarchical historical activation records remain visible without being confused with active stack frames. Records, identities, returns and root data are preserved.
- The RN illustration includes only actual NULL links from canonical memory. It does not invent NIL allocations or initialize unknown links. Memory cards and diagram are checked by identity and exact edges, including disconnected and transient states.
- Browser observers open public disclosures and inspect variables after the first executed frame, when the UI exposes them, rather than before execution. Main/code and stdout comparisons retain exact bytes and negative controls.
- Sorting and Graph test consumers follow bounded, reviewed source and rendering contracts. Hash silence checks cover raw output, not only formatted output. Exact native C17 execution rejects coordinated forged output.
- Historical text/AST adapters permit only enumerated changes to the historical expectation; they do not normalize the current observation or replace historical evidence. The separate C/H download transport check normalizes CRLF to LF on both downloaded and canonical bytes, with controls that reject content, whitespace and memory changes. Canonical C/H files are unchanged.
- BFS smoke now prepares and checks the public limit of 15 vertices rather than silently ignoring failures while attempting 30. It explicitly uses normal execution and retains the five-second bound. The 16th-vertex and step-budget rejection controls remain. This does not certify a 30-vertex workload.
- Preparation titles are consistent and descriptive. Hash retains its structure name; Sorting retains its method-specific fourth-stage title. Five stages, content and order are preserved.
- Synthetic screenshots use fresh local application contexts, loopback-only destinations and test integers. Separate PNG artifacts leave the existing machine-readable diagnostic archive layout unchanged. Capture errors preserve the original test failure, including environments without Python 3.11 exception notes.
- Educational prediction retains the next recorded condition, three progressive hints, and future-labelled evidence without moving the current cursor. Practice blocks both Next and ArrowRight before an unresolved condition and permits only manual advancement after answering or skipping. The single learning-level selector and its guides return to the code stage, preserving value and access. The four original educational browser cases remain selected.
- Cache versions for hierarchical.js, sequential.js and classroom_view.js are updated. Other asset versions remain unchanged.
- Reconstruction diagnostics emit only numeric measurements for the five named families, when explicitly enabled by CI. Private metadata and arbitrary fields are excluded. The original performance gate is unchanged.

## Finite integrated validation

The following results overlap and must not be added as a unique total:

- Final integrated regression: 440 successor, observer, source, native-output, UI, numeric-diagnostic and capture-contract controls passed in 221.77 seconds.
- All 23 specifically repaired unit failures from the base CI passed in the integrated copy.
- 43 performance and numeric-diagnostic controls passed; the actual local five-iteration run remained under 200 ms for all five families (Graph p95 127.925 ms). This does not resolve the earlier CI failure.
- 22 RN capture safety/compatibility controls passed; two learning-level capture-contract controls also passed. Python 3.10 API absence was simulated; no local Python 3.10 interpreter was available.
- The three historical Heap/Binsort gates were rerun and still fail explicitly for their missing or conflicting evidence. No xfail, skip, pin replacement or deletion was introduced to suppress them.

Complete collection contains 7529 cases, including every one of the 7156 base node IDs and 373 additions. The general Chromium selection contains 565 cases, ten more than the base, including six stage-layout, two RN and two learning-level synthetic viewport cases. All 26 canonical C/H sources match the base byte for byte. New-head CI results remain pending publication. Passing API, native C17 or jsdom checks does not certify browser layout, downloads or timing.

The RN projection checks exercise 953 canonical frames, including transient states, with up to 258 reservations and 518 circles. DOM/geometry and identity checks are finite scalability evidence, not certification of real-browser pixels or viewport usability. Independent educational replay checks cover 79 decisions and 230 frames with the actual runtime.

## Remaining evidence and performance gates

The eight C1/role-workflow provenance gates, two Heap historical preservation gates and nine archived pre-book Graph gates from the first review remain explicit. A Binsort protected-source check additionally exposes a mismatched historical DFS review binding: the expected review hash is `575ce6e9c64cadb19e1e141b1ca8a52f1eea6421e0de9bd1cf1a91a25ff64077`; the available review, also found in both authentic recovered archives, has hash `3c1d3bdda458d61d1a96df4d406cb894f4834d6fce9b4f2ce8602ec7896e448f`. This is not a line-ending difference. The expected preimage or a legitimate historical successor is still required.

The reconstruction p95 test failed in CI without exposing which family exceeded its 200 ms bound. The bound, sample count and histories must remain unchanged. Local measurements are not a substitute for the pending exact-commit CI result.

## Browser limits

Local Chromium remains blocked by the environment's socket restriction. No launch workaround or mock is reported as a browser pass. New PNGs must be downloaded and visually reviewed from CI before any merge or deployment recommendation. Production-only observations of the unchanged main build are separate evidence, not validation of this candidate.
