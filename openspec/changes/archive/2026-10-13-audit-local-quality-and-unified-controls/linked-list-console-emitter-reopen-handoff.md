# Lista printf LF: author handoff, QA pending

Assignment coordination-linked-list-console-emitter-reopen-low-20261007, operation audit.linked-list-console-consumers. Reopen authorization and exact historical scope: linked-list-console-emitter-reopen-decision.md. Canonical execution D:\MisProyectos\Web_VisualEstruct.

Before: two focal legacy tests FAIL (0.70s), and captured printf chunks lack final LF compared with native tad_lista.c. Original logs/traces and blocked handoff retained in parent evidence directory.

Minimal repair: execution_trace_service._printf_literal adds opt-in trailing-newline preservation. Only linked_list buscar_elemento/eliminar_repetidos opt in; every other caller retains prior default. Search formatted console now includes its native terminal LF. No native C, event/state/control-flow/algorithm changes. Consumers now expect the evaluated false not-found guard, skipped not-found printf, and confirmation at printf before void-scope exit. Existing printf counts, intermediate unlink states and three free assertions preserved.

After: 18 PASS in1.01s pytest; supervisor exit0/2.016s, hard2GiB verified before application imports, cap120s. Exactly2 real route cases plus16 checks:2 positive native-chunk fixtures,12 negative truncated/duplicated/late/missing/wrong-source/leading-LF mutations,2 literal multi-LF/no-LF preservation/default checks. Fixture source is frozen before trace with only independently C-required terminal LF restored, not generated from repaired runtime. No extra native/E2E/global campaigns.

Both complete response bodies are identical before/after after removing only console fields (verification.json); native C byte-identical. AST confirms only the2 selected functions in historical test file changed. Accepted Sorting9/9, hierarchical28/28, Apilar28/28 hashes unchanged.

QA request: independently verify native printf bytes, unchanged full responses except console, opt-in isolation, guards and printf/scope chronology, negative controls; register independent review bindings/assignment and use guards. No closure/global count claimed. Product/test files for review: app/services/execution_trace_service.py; tests/test_linked_list_trace_semantics.py; tests/_linked_list_console_oracle.py; tests/test_linked_list_console_oracle.py. Evidence here includes before copies, immutable positive fixtures, runtime traces, XML, limits/supervisor proof, verification and input hashes.

No publication or further denied action attempted.
