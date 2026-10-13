# QuickSort comparison consumers

Only two original QuickSort comparison consumers, unchanged [1,2,3] fixture. Reproduce legacy move_i/move_j,pivot_index/comparing_indices expectations; contrast actual C conditions and memory locals before minimal consumer repair. Strict pure causal condition/alias controls from frozen originals. Preserve accepted27 and pending16 including shared function bytes. No engine expansion, deniedQA records/retry, formalQA substitution, publication/global/E2E/optimization.

- tests/test_phase7_trace_contract_remediation.py::test_quicksort_emits_true_and_false_condition_evaluations
- tests/test_didactic_qa_findings.py::test_sort_001_reproduces_unshown_quicksort_failed_comparisons

- [ ] quicksort-comparison-consumers: focal evidence and independent QA handoff.

Author:2 original FAIL ->21 unique PASS (2 original+19 pure), independent QA pending. Balance27/18/21; see quicksort-comparison-consumers-handoff.md.
