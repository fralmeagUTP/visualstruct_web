# Verification of recovered Sorting text continuity

## Completed

Recovered historical Shell, Quick and Heap instruction sources from the user-uploaded `visualstruct_web-main.zip` (archive filename and ZIP SHA-256 are preserved in `tests/fixtures/sorting-source-history/recovered-sources.json`). The three source hashes match the original archived protected manifests exactly. No historical file was reconstructed.

Compared complete ASTs against the already delivered orthographic successor sources. The only changes are 9 Shell, 15 Quick and 4 Heap string literals, each listed by exact AST location and before/after value. All are accents in narration or presentation labels. Code, numeric values, token IDs, source-code literals and all other AST fields remain identical.

The contract pins the old hash, current hash, original snapshot and complete reviewed delta. An unrelated future edit, including another orthographic edit, fails until separately reviewed; there is no global text-normalization escape hatch. This is source continuity evidence, not a retrospective functional approval.

Quick's original baseline test exists as an authenticated archived snapshot (SHA-256 `3c719f717ad85e03fd1f307834fa6bf84333a1f80e3724fbe20269c82917a1d7`). Its current version is checked with the pre-existing fixture-path portability adapter, without expanding that adapter. Cases and assertions remain intact.

Counting and Heap generated-observer comparisons now admit only CRLF versus LF transport. Complete normalized Counting observer/native-log and Heap observer bytes were compared before this change. C/H authority checks remain in place and no C/H file was edited.

## Tests

- 39 focused checks passed: 37 positive/negative contract tests plus the existing Counting and Quick preservation gates.
- Final combined run: **78 passed, 2 failed** in 10.68 seconds. It ran the two new contract test files and Counting, Quick and Heap instruction suites.
- Negative controls reject operators, numbers, removed code, altered narration, accent changes in technical tokens, changed manifests/snapshots, unknown source bytes, unknown original hashes and weakened historical test assertions/cases.
- These are local finite checks and native-C/recorded-evidence tests. They are not a claim that actual browser coverage ran or that all CI passed.

## Preserved blockers

1. `visible-sorting-heapsort-baseline-low/native-final-second/native.jsonl` is absent from the published inputs and the inspected historical packages. The unchanged historical-oracle comparison still fails when it reaches that input.
2. The original Heap baseline test declares SHA-256 `8a59530b549cf79ed726e9be3f5d5311b47a5bbea46882e2d038f3361007b637`, but its present bytes are `b38dcd5db85d876db1c227496de659b221348db9be23c7c52b0f9c7c6b61b448`. No authentic preimage was found. This gate remains failing.

No missing report was synthesized, no expected historical hash was overwritten, no test was disabled, and no product/C/H source or remote state was changed.
