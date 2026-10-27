"""Strict decoding boundary for complete Graph HTTP trace assertions."""
from __future__ import annotations
from app.domain.graph.snapshot_pool import expand_graph_trace


def _contains_reference(value):
    if isinstance(value, dict):
        return "$graph_ref" in value or any(_contains_reference(v) for v in value.values())
    if isinstance(value, list):
        return any(_contains_reference(v) for v in value)
    return False


def decode_graph_http_trace(wire):
    if "graph_snapshot_codec" not in wire:
        assert not _contains_reference(wire), "Undeclared Graph reference transport"
    # The decoder rejects unknown codecs and invalid/forward references.
    return expand_graph_trace(wire)
