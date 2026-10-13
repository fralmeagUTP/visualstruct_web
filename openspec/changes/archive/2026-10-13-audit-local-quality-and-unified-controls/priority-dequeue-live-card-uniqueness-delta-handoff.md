# Priority dequeue live-card uniqueness delta: reacceptance handoff

Assignment coordination-priority-dequeue-live-card-uniqueness-delta-low-20261007; operation audit.priority-dequeue-memory-consumer. QA rejection preserved at review-priority-dequeue-legacy-memory-consumer/evidence/independent-review/review.md.

Reproduced3 coordinated duplicate live-card counterexamples before repair: tests/test_priority_dequeue_memory_oracle.py::test_coordinated_duplicate_live_card_is_rejected parametrized for unlink, value store, priority store. Each synchronizes memory.heap, heap_objects and heap_transition.after. Original helper admits all3 (new negatives3FAIL).

Minimal delta only2 files: _priority_dequeue_memory_oracle.py validates list length4 and unique IDs before dict conversion; validates before-transition length/uniqueIDs/exact reserve IDs and after-transition exact list correspondence. Reviewed other dictionary conversions: original heap already checked4 unique IDs; added explicit distinct values before by_value conversion. Derived ids uses validated unique dictionary. Release heap requires3 cards and exact3 surviving IDs; single retired card already validated. No unchecked equivalent duplicate collapse remains in these conversions. test_priority_dequeue_memory_oracle.py adds exactly3 coordinated negatives. Existing legitimate positive and13 prior cases remain.

After16PASS =1 actual route +15 pure checks, including the3 new negatives. Test XML/stdout and supervisor record exact durations separately. Hard2GiB verified before imports, cap120s. Whole runtime response equals frozen original. Product/C and historical route consumer unchanged; old38manifest differs only2 intended helper/control files, prior logs/results/QA rejection retained. Accepted Sorting9, hierarchical28, Apilar28, Lista console29 unchanged.

Independent QA reacceptance pending. Verify uniqueness before collapse and coordinated3 mutants with positive original, original13 preserved, source/response/hash isolation. No publication/global/E2E, optimizations, extra algorithms or denied-action retries.
