"""Exact immediate-before BFS comparison across enter/write/free/leave scopes."""
import importlib.util
from pathlib import Path
import pytest
import test_graph_boundary_equivalence_regression as oracle
from app.domain.graph import bfs_instruction as bfs
BEFORE=Path(__file__).parents[1]/'openspec/changes/archive/2026-10-13-audit-local-quality-and-unified-controls/evidence/visible-graph-bfs-revision-cache-low/before/app/domain/graph/bfs_instruction.py'
spec=importlib.util.spec_from_file_location('app.domain.graph._revision_cache_before',BEFORE)
baseline=importlib.util.module_from_spec(spec);spec.loader.exec_module(baseline)
@pytest.mark.parametrize('case',range(len(oracle.BFS_CASES)))
def test_revision_cache_preserves_complete_before_after_and_transport(monkeypatch,case):
    monkeypatch.setitem(oracle.BASE,bfs,baseline)
    oracle.test_bfs_all_recorded_input_shapes_equal_previous_builder_without_rerunning_C(monkeypatch,case)

@pytest.mark.parametrize('value',[1.0,float('inf'),float('-inf'),float('nan')])
def test_transport_finite_marker_preserves_exact_null_policy(value):
    from app.domain.graph.snapshot_pool import SnapshotPool
    from app.routes.graph_routes import _json_safe
    import math,json
    pool=SnapshotPool();pool.intern({'sentinel':value,'nested':[True,1,None]})
    actual=_json_safe(pool.records)
    expected=_json_safe(list(pool.records))
    assert json.dumps(actual,allow_nan=False)==json.dumps(expected,allow_nan=False)
    assert (actual is pool.records)==math.isfinite(value)
