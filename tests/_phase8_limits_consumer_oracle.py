"""Functional trace integrity and explicitly historical metrics; no truncation."""
import json
from app.services.trace import TraceEngine

def assert_complete_trace_json(body):
    assert body["success"] is True
    trace = body["execution_trace"]
    assert trace["success"] is True and trace["steps"]
    assert trace["final_state"] == body["visual_state"]
    assert TraceEngine.validate_legacy_trace(trace)
    encoded = json.dumps(trace, ensure_ascii=False).encode("utf-8")
    restored = json.loads(encoded)
    assert len(restored["steps"]) == len(trace["steps"])
    assert json.dumps(restored, ensure_ascii=False).encode("utf-8") == encoded
    return encoded

def metric(structure_id, service_ms, serialization_ms, trace_bytes):
    assert service_ms >= 0 and serialization_ms >= 0 and trace_bytes > 0
    return dict(structure_id=structure_id, service_generation_ms=service_ms,
                integrity_validation_and_serialization_ms=serialization_ms,
                trace_bytes_expanded_utf8=trace_bytes, historical_size_budget_bytes=1_000_000,
                historical_size_exceeded=trace_bytes >= 1_000_000,
                historical_service_budget_ms=2000, historical_service_budget_exceeded=service_ms >= 2000,
                native_C_timing_measured=False, visual_playback_timing_measured=False)
