"""Scoped negative source controls and entered Radix lexical scopes."""
from copy import deepcopy
import pytest
from app.adapters.sorting_adapter import SortingAdapter
from app.services.c_code_service import CCodeService
from _sorting_source_oracle import assert_sorting_source_trace


def _trace(algorithm: str, values: list[int]) -> dict:
    adapter = SortingAdapter()
    adapter.create_array(values)
    adapter.select_algorithm(algorithm)
    source = CCodeService.get_structure_data("sorting_array")["operations"][algorithm]
    return adapter.run("step_by_step", source_code=source)["execution_trace"]


@pytest.mark.parametrize("values", [[2, 1], [-2, -1], [-2, 0, 1], [0]], ids=["positive", "negative", "mixed", "zero"])
def test_radix_emits_only_entered_exits_at_actual_braces_and_retires_locals(values: list[int]) -> None:
    trace = _trace("radixsort", values)
    steps = trace["steps"]
    rows = trace["source_code"].replace("\r\n", "\n").split("\n")
    for prefix, entered, next_statement, scope in [
        ("negative", any(v < 0 for v in values), "if (cant_positivos > 0)", "ordenar_radixsort/bloque_negativos"),
        ("positive", any(v >= 0 for v in values), "indice = 0;", "ordenar_radixsort/bloque_positivos"),
    ]:
        guard = next(step for step in steps if step["pedagogy"]["source"]["line_token"] == prefix + "_group_guard")
        assert guard["pedagogy"]["condition"]["result"] is entered
        exits = [step for step in steps if step["pedagogy"]["source"]["line_token"] == prefix + "_block_exit"]
        assert len(exits) == int(entered)
        if not entered:
            assert all(not any(v["scope"] == scope for v in step["pedagogy"]["variables"]) for step in steps)
            continue
        exit_step = exits[0]
        anchor = next(i for i, row in enumerate(rows) if next_statement in row)
        actual_brace = next(i for i in range(anchor - 1, -1, -1) if rows[i].strip())
        assert rows[actual_brace].strip() == "}"
        assert exit_step["line_index"] == actual_brace
        assert exit_step["line_text"] == rows[actual_brace]
        assert exit_step["pedagogy"]["source"]["function"] == "ordenar_radixsort"
        previous = steps[exit_step["step_index"] - 1]
        locals_before = {v["name"]: v for v in previous["pedagogy"]["variables"] if v["scope"] == scope}
        assert set(locals_before) == {"maximo", "exp"}
        assert all(v["initialized"] for v in locals_before.values())
        assert not any(v["scope"] == scope for v in exit_step["pedagogy"]["variables"])
        page = trace.page_source.page(exit_step["step_index"], 1)["steps"][0]
        assert page["line_index"] == exit_step["line_index"]
        assert page["state_after"] == exit_step["state_after"]
    assert trace["final_state"]["items"] == sorted(values)
    assert_sorting_source_trace(trace, values)


@pytest.mark.parametrize("corruption", ["unmapped_instruction", "wrong_text", "out_of_range", "extra_initial", "active_initial", "mutated_initial"])
def test_source_oracle_rejects_corrupted_real_or_forged_metadata_frames(corruption: str) -> None:
    trace = deepcopy(_trace("burbuja", [2, 1]))
    assert_sorting_source_trace(trace, [2, 1])
    step = next(s for s in trace["steps"] if s["pedagogy"]["source"]["line_token"] == "compare")
    if corruption == "unmapped_instruction":
        step["line_index"] = step["pedagogy"]["source"]["line_index"] = None
        step["line_text"] = step["pedagogy"]["source"]["line_text"] = ""
    elif corruption == "wrong_text":
        step["line_text"] = step["pedagogy"]["source"]["line_text"] = "instruccion_inventada();"
    elif corruption == "out_of_range":
        step["line_index"] = step["pedagogy"]["source"]["line_index"] = len(trace["source_code"].splitlines()) + 7
    elif corruption == "extra_initial":
        forged = deepcopy(trace["steps"][0]);forged["step_index"] = len(trace["steps"]);trace["steps"].append(forged)
    elif corruption == "active_initial":
        trace["steps"][0]["pedagogy"]["call_stack"] = [{"function": "ordenar_burbuja"}]
    else:
        trace["steps"][0]["state_after"]["items"] = [1, 2]
    with pytest.raises(AssertionError):
        assert_sorting_source_trace(trace, [2, 1])


@pytest.mark.parametrize("prefix,name,anchor_text", [("negative", "negativos", "if (cant_positivos > 0)"), ("positive", "positivos", "indice = 0;")])
def test_scope_source_mapping_ignores_comment_braces(prefix: str, name: str, anchor_text: str) -> None:
    from app.services.radix_trace_service import line_lookup
    source = CCodeService.get_structure_data("sorting_array")["operations"]["radixsort"]
    guard = "if (cant_" + name + " > 0) {"
    source = source.replace(guard, guard + "\n/* unmatched comment braces: {{{ */", 1)
    rows = source.replace("\r\n", "\n").split("\n")
    anchor = next(i for i, row in enumerate(rows) if anchor_text in row)
    actual_brace = next(i for i in range(anchor - 1, -1, -1) if rows[i].strip())
    assert rows[actual_brace].strip() == "}"
    assert line_lookup(source)[prefix + "_block_exit"] == actual_brace


def test_missing_group_source_never_invents_a_scope_exit_line() -> None:
    from app.services.radix_trace_service import line_lookup
    mapping = line_lookup("int ordenar_radixsort(int *arreglo, size_t n) { return ORDENAMIENTO_OK; }")
    assert mapping["negative_block_exit"] is None
    assert mapping["positive_block_exit"] is None
