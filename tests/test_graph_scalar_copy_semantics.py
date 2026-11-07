"""Finite semantic controls for scalar copies and canonical comparison dispatch.

Only the hash-checked book source is parsed. Operator unit tests substitute
operand evaluation on its AST nodes. The unused <= dispatch branch receives
an explicitly synthetic node, not a parsed or claimed canonical C program.
"""
from __future__ import annotations

from copy import deepcopy
import operator

import pytest

from app.domain.graph import book_c_subset as book


@pytest.fixture(scope="module")
def program():
    """Parse the actual immutable source once for these isolated controls."""
    return book.Program(book.canonical_source())


def binary_node(program, operation):
    if operation == "<=":
        # The locked book source does not contain <=, although the evaluator
        # supports it. Exercise that changed branch without accepting another
        # source, mutating the shared AST, or calling it a native C oracle.
        template = binary_node(program, ">=")
        return book.Node(template.kind, template.token, template.end,
                         {**template.data, "op": "<="})
    return next(node for function in program.functions.values()
                for node in book.walk(function["body"])
                if node.kind == "binary" and node.data["op"] == operation)


@pytest.mark.parametrize("value", [None, False, True, 0, -1, -(1 << 63),
                                   (1 << 63) - 1, "NULL", book.UNINIT, "M123"])
def test_exact_atomic_values_match_deepcopy_identity(value, monkeypatch):
    expected = deepcopy(value)
    monkeypatch.setattr(book, "deepcopy", lambda value: pytest.fail("Atomic copy dispatched deepcopy"))
    assert book._copy_c_value(value) is expected is value


def test_exact_reference_preserves_pointer_target_and_lifetime_checks(program, monkeypatch):
    owner = {"_alive": True}
    cell = {"value": book.UNINIT}
    reference = book.Reference(cell, "value", "int", "caller:output", owner)
    expected = deepcopy(reference)
    monkeypatch.setattr(book, "deepcopy", lambda value: pytest.fail("Reference copied its pointee"))
    actual = book._copy_c_value(reference)
    assert actual is expected is reference
    assert actual.container is cell and actual.owner is owner
    machine = book.GraphMachine(program, [], [], record_events=False)
    with pytest.raises(ValueError, match="Uninitialized C read"):
        machine.read(actual)
    cell["value"] = 7
    assert machine.read(actual) == 7
    cell["value"] = "M-retired"
    machine.retired.append({"id": "M-retired"})
    with pytest.raises(ValueError, match="Indeterminate retired pointer read"):
        machine.read(actual)
    owner["_alive"] = False
    with pytest.raises(ValueError, match="Expired C reference"):
        machine.read(actual)


def test_nested_aggregates_keep_internal_aliases_but_independent_copies():
    reference = book.Reference({"value": 9}, "value", "int", "caller:shared")
    shared = {"items": [1, {"value": 2}], "reference": reference}
    original = {"graph": {"v": "V1", "a": "E1"}, "left": shared,
                "right": shared, "nested": [shared, {"other": [3, 4]}]}
    expected = deepcopy(original)
    first = book._copy_c_value(original)
    second = book._copy_c_value(original)
    assert first == second == expected == original
    assert first is not second and first is not original
    assert first["left"] is first["right"] is first["nested"][0]
    assert first["left"] is not original["left"] and first["left"] is not second["left"]
    assert first["left"]["reference"] is second["left"]["reference"] is reference
    first["left"]["items"][1]["value"] = 99
    first["graph"]["v"] = "changed"
    first["nested"][1]["other"].append(5)
    assert original == second == expected
    assert first["right"]["items"][1]["value"] == 99


def test_fallback_preserves_deepcopy_memo_for_cycles():
    original = {"items": []}
    original["items"].append(original)
    first = book._copy_c_value(original)
    second = book._copy_c_value(original)
    assert first is first["items"][0] and second is second["items"][0]
    assert first is not original and second is not first
    assert first["items"] is not original["items"]


def test_metaclass_equality_cannot_impersonate_an_atomic_C_type():
    class EqualToEveryType(type):
        def __eq__(cls, other):
            return True

        __hash__ = type.__hash__

    class MutableValue(metaclass=EqualToEveryType):
        def __init__(self):
            self.items = [1, 2]

    original = MutableValue()
    expected = deepcopy(original)
    actual = book._copy_c_value(original)
    assert actual is not original
    assert actual.items == expected.items
    actual.items.append(3)
    assert original.items == expected.items == [1, 2]


class IntSubclass(int):
    pass


class StringSubclass(str):
    pass


@pytest.mark.parametrize("value", [IntSubclass(7), StringSubclass("M1")])
def test_scalar_subclasses_copy_their_mutable_instance_state(value):
    value.extra = {"items": [1, 2]}
    expected = deepcopy(value)
    actual = book._copy_c_value(value)
    assert type(actual) is type(value) and actual == expected
    assert actual is not value and actual.extra == expected.extra
    actual.extra["items"].append(3)
    assert value.extra == expected.extra == {"items": [1, 2]}


class CustomCopy:
    def __deepcopy__(self, memo):
        return {"custom_copy": type(self).__name__}


class CustomInt(CustomCopy, int):
    pass


class CustomString(CustomCopy, str):
    pass


class CustomReference(CustomCopy, book.Reference):
    pass


@pytest.mark.parametrize("value", [CustomCopy(), CustomInt(7), CustomString("M1"),
    CustomReference({"value": 7}, "value", "int", "caller:custom")])
def test_unknown_types_and_subclasses_honor_custom_deepcopy(value, monkeypatch):
    expected = deepcopy(value)
    dispatched = []

    def observe(actual):
        dispatched.append(actual)
        return deepcopy(actual)

    monkeypatch.setattr(book, "deepcopy", observe)
    assert book._copy_c_value(value) == expected
    assert len(dispatched) == 1 and dispatched[0] is value


COMPARISONS = {"==": operator.eq, "!=": operator.ne, "<": operator.lt,
               ">": operator.gt, "<=": operator.le, ">=": operator.ge}


def operand_machine(program, operation, left, right):
    """Keep the real node/dispatch, replacing only its two operand providers."""
    node = binary_node(program, operation)
    machine = book.GraphMachine(program, [], [], record_events=True)
    evaluated = []

    def evaluate(child):
        if child is node.data["left"]:
            evaluated.append("left")
            return left
        assert child is node.data["right"]
        evaluated.append("right")
        if isinstance(right, Exception):
            raise right
        return right

    machine.eval = evaluate
    return machine, node, evaluated


@pytest.mark.parametrize("operation", COMPARISONS)
@pytest.mark.parametrize("left,right", [(0, 0), (-1, 0), (0, -1),
    (-(1 << 31), (1 << 31) - 1), ((1 << 63) - 1, -(1 << 63)),
    ((1 << 63) - 1, (1 << 63) - 1)])
def test_six_comparators_evaluate_once_in_order_and_return_C_int(program, operation, left, right):
    machine, node, evaluated = operand_machine(program, operation, left, right)
    result = machine._eval(node)
    assert type(result) is int
    assert result == int(COMPARISONS[operation](left, right))
    assert evaluated == ["left", "right"]


@pytest.mark.parametrize("operation", ["==", "!="])
@pytest.mark.parametrize("left,right", [(book.NULL, book.NULL), ("M1", book.NULL),
                                        ("M1", "M1"), ("M1", "M2")])
def test_symbolic_pointer_comparisons_keep_exact_equality(program, operation, left, right):
    machine, node, evaluated = operand_machine(program, operation, left, right)
    assert machine._eval(node) == int(COMPARISONS[operation](left, right))
    assert evaluated == ["left", "right"]


@pytest.mark.parametrize("operation", COMPARISONS)
def test_comparison_dispatch_runs_only_selected_operator_and_preserves_error(program, operation):
    invoked = []
    failure = ValueError("comparison sentinel")

    def comparison(name):
        def reject(self, other):
            invoked.append(name)
            raise failure
        return reject

    probe_type = type("ComparisonProbe", (), {
        "__eq__": comparison("=="), "__ne__": comparison("!="),
        "__lt__": comparison("<"), "__gt__": comparison(">"),
        "__le__": comparison("<="), "__ge__": comparison(">="),
    })
    machine, node, evaluated = operand_machine(program, operation, probe_type(), object())
    with pytest.raises(ValueError) as caught:
        machine._eval(node)
    assert caught.value is failure and invoked == [operation]
    assert evaluated == ["left", "right"]


@pytest.mark.parametrize("operation,left,skip", [("&&", 0, True), ("||", 1, True),
                                                ("&&", 1, False), ("||", 0, False)])
def test_short_circuit_skips_only_unreachable_operand_errors(program, operation, left, skip):
    failure = ValueError("right operand sentinel")
    machine, node, evaluated = operand_machine(program, operation, left, failure)
    if skip:
        assert machine._eval(node) == left
        assert evaluated == ["left"]
        assert machine.event_count == 1 and len(machine.events) == 1
        assert machine.events[0]["phase"] == "operand"
        assert machine.events[0]["name"] == program.text(node.data["left"])
    else:
        with pytest.raises(ValueError) as caught:
            machine._eval(node)
        assert caught.value is failure and evaluated == ["left", "right"]
        assert machine.event_count == 1


@pytest.mark.parametrize("left,right,expected,output", [
    ((1 << 63) - 1, 1, 0, book.UNINIT),
    (-(1 << 63), -1, 0, book.UNINIT),
    ((1 << 63) - 2, 1, 1, (1 << 63) - 1),
    (-(1 << 63) + 1, -1, 1, -(1 << 63)),
    (0, 0, 1, 0),
])
def test_actual_c_safe_sum_preserves_overflow_guard_and_output_cell(program, left, right, expected, output):
    machine = book.GraphMachine(program, [], [], record_events=True)
    cell = {"value": book.UNINIT}
    reference = book.Reference(cell, "value", "long long", "caller:sum")
    assert machine.invoke("sumar_seguro", [left, right, reference]) == expected
    assert cell["value"] == output and machine.frames == []
    writes = [event for event in machine.events if event["phase"] == "write"]
    assert bool(writes) is bool(expected)


@pytest.mark.parametrize("value", [-(1 << 31) - 1, 1 << 31])
def test_invalid_int_argument_rejected_before_any_C_transition(program, value):
    session = book.BookSession(program_cache={(book.canonical_source(), False): program})
    before = session.machine.snapshot()
    with pytest.raises(ValueError, match="C integer overflow"):
        session.call("grafo_insertar_vertice", [value])
    assert session.machine.snapshot() == before and session.machine.event_count == 0


@pytest.mark.parametrize("mode", ["quiet", "observer", "trace"])
@pytest.mark.parametrize("failure", [None, 2])
def test_real_calls_match_deepcopy_baseline_including_cleanup_and_observers(program, monkeypatch, mode, failure):
    candidate = book._copy_c_value

    def execute(copy_value):
        observed = []
        with monkeypatch.context() as patch:
            patch.setattr(book, "_copy_c_value", copy_value)
            session = book.BookSession(trace=mode == "trace", fail_allocation=failure,
                event_observer=observed.append if mode == "observer" else None,
                program_cache={(program.source, False): program})
            calls = []
            for function, arguments in [
                ("grafo_crear", []), ("grafo_insertar_vertice", [1]),
                ("grafo_insertar_arco", [1, 2, 7]), ("grafo_vertices", []),
                ("grafo_sucesores", [1]), ("grafo_costo_arco", [1, 2]),
                ("grafo_imprimir_vertices", []), ("grafo_eliminar_vertice", [1]),
                ("grafo_destruir", []),
            ]:
                result = session.call(function, arguments)
                calls.append(result)
                if result["ownership"] == "owned":
                    session.free_result(result["returned"], result["return_type"])
            return calls, session.machine.snapshot(), observed

    expected = execute(deepcopy)
    actual = execute(candidate)
    assert actual == expected
    assert actual[1]["frames"] == [] and actual[1]["heap_nodes"] == []
    assert actual[1]["allocations"] == actual[1]["frees"]
    assert actual[0][3]["ownership"] == "borrowed"
    assert actual[0][4]["ownership"] == "owned"
    assert actual[0][2]["status"] == (0 if failure is None else 1)
    assert actual[1]["console_stdout"]


def test_caller_receipt_keeps_returned_aggregate_separate_from_live_graph(program):
    session = book.BookSession(program_cache={(program.source, False): program})
    session.call("grafo_insertar_vertice", [7])
    receipt = session.machine.external["result"]["value"]
    live = session.machine.graph
    assert receipt == live and receipt is not live
    receipt["v"] = book.NULL
    assert session.graph_state()["vertices"] == [7]
