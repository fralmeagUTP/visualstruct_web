"""Performance budget gate for 300-operation reconstruction."""

from __future__ import annotations

import pytest

from scripts.benchmark_checkpoint_reconstruction import run


@pytest.mark.performance
def test_reconstruction_p95_stays_below_200_ms_for_all_families() -> None:
    report = run(iterations=5, budget_ms=200.0)
    assert report["passed"] is True, report
    assert set(report["results"]) == {
        "sequential",
        "tree",
        "graph",
        "hash",
        "sorting",
    }
    assert all(
        result["history_operations"] == 300
        and result["replay_operations"] == 300
        and result["p95_ms"] < 200.0
        for result in report["results"].values()
    )
