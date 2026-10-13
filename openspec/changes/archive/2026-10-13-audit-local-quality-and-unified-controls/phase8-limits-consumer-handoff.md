# Phase8 limits consumer: author handoff, independent QA pending

Only original tests/test_phase8_visual_integration.py::test_trace_size_latency_and_session_limits corrected; all imports, SCENARIOS inputs/order and other functions raw-byte identical. No product/C/algorithm/trace/threshold increase/optimization. Historical1000000bytes and2000ms preserved as explicit reported metrics; exceedances recorded in layer-results.json/JUnit. Author instruction explicitly approves consumer separation based on provenance, not passing by raising a limit.

Final11PASS6.01s:1original ID +10focal controls (1saved RN positive,6functional corruptions,3strict historical boundary probes). Earlier1originalPASS4.63s overlaps, not counted again. Intermediate10PASS1FAIL6.29s: own negative used nonexistent state_before instead of real state_snapshot; fixed test control only, original already passed. Logs retained. Supervisor7.093s; Jobeffective2GiB/120s before imports, exit0.

Functional layer: original13service scenarios/22calls remain, success/nonempty/source/continuous trace validated through existing TraceEngine, final state equality and lossless complete JSON roundtrip. This consumer is not a new nativeC/semantic-all-paths certificate; accepted/pending semantic lots remain unchanged. Expanded JSON size and service-generation/validation-serialization timings separated, no nativeC/UI times claimed.

Transport layer: actual FlaskHTTP RN10,5,1 threePOSTs200, full decoded execution_trace exactly equals direct original service RN trace after JSON normalization, no frames dropped. HTTPresponse byte count in layer-results.json. Backend server-side operations history equals service history, GETreload200 and history unchanged; insertion trace is not persisted in session. No browser/proxy/network/concurrency certificate or all13HTTP campaign. No artifact-only transport claim.

Session layer: actual SessionService.save_history301distinct synthetic operations ->last300, actual app.session_interface.save_session and subsequent new request cookie opens same persisted300entries. Does not run301algorithms. Configuration positive<=300. Functional truncation/backend retrieval shown; p95reconstruction300benchmark remains separate unchanged obligation and not claimed by thisID.

Historical size excesses and measurements follow. No runtime failure concealed or oldlogconverted. All prior24manifests preserved with exact source SHA chain, only authorized last function shared delta. Balance derived66distinct originals:27accepted39locallycorrectedpendingQA0otherpending; new controls excluded, remote66failurecount remains historical. NOindependentQAacceptance/globalclosure/publication. Originalauthorcorrection complete for these bounded obligations, awaiting coordinator's separate independent review.

{
  "historical_excesses": [
    {
      "structure_id": "avl",
      "service_generation_ms": 377.61560000217287,
      "integrity_validation_and_serialization_ms": 258.92229999954,
      "trace_bytes_expanded_utf8": 1286708,
      "historical_size_budget_bytes": 1000000,
      "historical_size_exceeded": true,
      "historical_service_budget_ms": 2000,
      "historical_service_budget_exceeded": false,
      "native_C_timing_measured": false,
      "visual_playback_timing_measured": false
    },
    {
      "structure_id": "red_black",
      "service_generation_ms": 576.4801000004809,
      "integrity_validation_and_serialization_ms": 416.2518999983149,
      "trace_bytes_expanded_utf8": 2119908,
      "historical_size_budget_bytes": 1000000,
      "historical_size_exceeded": true,
      "historical_service_budget_ms": 2000,
      "historical_service_budget_exceeded": false,
      "native_C_timing_measured": false,
      "visual_playback_timing_measured": false
    }
  ],
  "maximum_measured_service_ms": 576.4801000004809,
  "rn_wire_response_bytes": "1947408"
}
