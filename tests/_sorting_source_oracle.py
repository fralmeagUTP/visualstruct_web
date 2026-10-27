"""Strict native source oracle with one precisely defined pre-call snapshot."""
def assert_sorting_source_trace(trace: dict, original_values: list[int]) -> None:
    """Admit only the exact initial metadata; require real C for every later row."""
    steps = trace["steps"]
    assert steps
    rows = trace["source_code"].replace("\r\n", "\n").split("\n")
    for position, step in enumerate(steps):
        source = step["pedagogy"]["source"]
        assert step["step_index"] == position
        assert source["line_index"] == step["line_index"]
        assert source["line_text"] == step["line_text"]
        if position == 0:
            assert source["line_token"] == "initial"
            assert source["function"] is None
            assert step["line_index"] is None
            assert step["line_text"] == ""
            assert step["pedagogy"]["concept"] == "phase"
            assert step["pedagogy"]["call_stack"] == []
            assert step["pedagogy"]["variables"] == []
            assert step["pedagogy"]["pointers"] == []
            assert step["pedagogy"]["condition"] is None
            assert step["state_snapshot"]["items"] == original_values
            assert step["state_after"]["items"] == original_values
            for counter in ("comparisons", "moves", "swaps"):
                assert step["state_after"]["metrics"][counter] == 0
        else:
            assert source["line_token"] != "initial"
            assert isinstance(source["function"], str) and source["function"]
            assert type(step["line_index"]) is int
            assert 0 <= step["line_index"] < len(rows)
            assert step["line_text"] == rows[step["line_index"]]
