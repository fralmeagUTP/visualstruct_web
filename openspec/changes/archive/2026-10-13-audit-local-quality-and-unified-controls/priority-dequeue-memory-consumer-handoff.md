# Priority dequeue legacy memory consumer: author handoff

Canonical D; assignment coordination-priority-dequeue-memory-consumer-low-20261007; operation audit.priority-dequeue-memory-consumer. Exact original node ID: tests/test_priority_queue_trace_conformance.py::test_dequeue_scans_every_node_stably_and_frees_only_after_unlink.

Before:1FAIL (0.83s) KeyError temporaries at unlink. C cp_desencolar uses strict less-than scanning, unlinks objective, copies value/priority, frees objective, then decrements count. Existing canonical dequeue_memory retains detached N2 with value20/priority1 until free; retired card uses historical_fields.valor rather than live fields.value. Frozen original response supports this contract.

Minimal change: only that historical test function plus import; obsolete temporary assertion replaced with stronger native lifetime oracle, historical freed-card assertion corrected. Existing result20/stable tie,5while/4compare,3items/unlink/free counts and final-state assertions preserved. No application/nativeC changes or closed-engine rerun.

After:13PASS (1.53s pytest; supervisor exit0/2.546s):1 actual route case and12 pure controls (1positive frozen pre-fix response,11negatives for missing/earlyfree/wrongvalue/alias/link/output/resurrection/retiredidentity/livefields/duplicate). Hard2GiB verified before imports, cap120s. Complete original and repaired runtime responses identical. AST proves only selected test function changed; C bytes unchanged. Accepted Sorting9, hierarchical28, Apilar28 and Lista-console29 frozen inputs preserved. No inference about remaining global66FAIL count.

Independent QA pending: review literal native instructions, identity/liveness and fields before free, historical-only data after free, copied outputs chronology, test isolation and rejection controls; register separate QA bindings/guards. Proposed QA change review-priority-dequeue-legacy-memory-consumer. Source files: tests/test_priority_queue_trace_conformance.py, tests/_priority_dequeue_memory_oracle.py, tests/test_priority_dequeue_memory_oracle.py. Evidence includes before copies/logs/traces, positive fixture from baseline, after logs/traces/XML, worker memory/supervisor proof, verification.json, hashes. Other priority queue operations excluded.

No commit/push/deploy, denied retries, global/E2E or optimization.
