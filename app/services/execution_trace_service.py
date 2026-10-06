"""Build interpreter-like execution traces for didactic operation playback."""

from __future__ import annotations

from copy import deepcopy
import re
from typing import Any

from app.services.trace.control_flow import ControlFlowPlanner
from app.services.trace.graph_planner import GraphAlgorithmPlanner
from app.services.trace.graph_trace_planner import GraphTracePlanner
from app.services.trace.hash_planner import HashControlFlowPlanner
from app.services.trace.tree_planner import TreeAlgorithmPlanner
from app.services.trace.tree_query_planner import TreeQueryPlanner
from app.services.trace.engine import TraceEngine
from app.services.trace.strategies import (
    GraphTraceStrategy,
    HashTraceStrategy,
    SequentialTraceStrategy,
    TraceStrategyRegistry,
    TreeTraceStrategy,
)
from app.domain.sequential.pedagogy import (
    SEQUENTIAL_FRAME_SCHEMA_VERSION,
    SEQUENTIAL_LEARNING_CATALOG,
    SEQUENTIAL_STRUCTURES,
    build_sequential_frame,
    sequential_frame_schema,
    validate_sequential_frame,
)
from app.domain.hierarchical.pedagogy import (
    HIERARCHICAL_FRAME_SCHEMA_VERSION,
    HIERARCHICAL_LEARNING_CATALOG,
    HIERARCHICAL_STRUCTURES,
    build_hierarchical_frame,
    hierarchical_frame_schema,
    validate_hierarchical_frame,
)
from app.domain.graph.pedagogy import (
    GRAPH_FRAME_SCHEMA_VERSION,
    GRAPH_LEARNING_CATALOG,
    build_graph_frame,
    graph_frame_schema,
    validate_graph_frame,
)
from app.domain.hash.pedagogy import (
    HASH_FRAME_SCHEMA_VERSION,
    HASH_LEARNING_CATALOG,
    build_hash_frame,
    hash_frame_schema,
    validate_hash_frame,
)


class ExecutionTraceService:
    """Create a normalized execution trace from didactic operation code."""

    # Aliases retained for callers of the former private API while the service
    # becomes an orchestration-only facade.
    _is_executable_line = staticmethod(ControlFlowPlanner.is_executable_line)
    _next_nonempty_line_index = staticmethod(ControlFlowPlanner.next_nonempty_line_index)
    _find_matching_brace_line = staticmethod(ControlFlowPlanner.find_matching_brace_line)
    _filter_trace_lines_by_control_flow = staticmethod(ControlFlowPlanner.filter_defensive_branches)
    _normalized_line_text = staticmethod(ControlFlowPlanner.normalize_line)
    _expand_generic_control_flow_indexes = staticmethod(ControlFlowPlanner.expand_generic)

    @staticmethod
    def _printf_literal(line_text: str) -> str | None:
        """Return a literal printf output when it can be represented exactly.

        This covers diagnostic messages such as the empty-stack guard.  Calls
        with format arguments continue to use adapter-provided console events.
        """
        match = re.search(r'printf\s*\(\s*"((?:\\.|[^"\\])*)"\s*\)', str(line_text))
        if not match:
            return None
        # Do not use ``unicode_escape`` here: it corrupts UTF-8 literals such
        # as "vacÃ­a".  The visualizer only needs the standard C escapes used
        # in its diagnostic messages.
        literal = match.group(1)
        literal = literal.replace("\\\\", "\x00")
        literal = literal.replace("\\n", "\n").replace("\\t", "\t").replace('\\"', '"')
        return literal.replace("\x00", "\\").rstrip("\n")

    @staticmethod
    def _expand_queue_execution_indexes(
        *,
        operation_name: str,
        lines: list[str],
        before_state: dict[str, Any],
        after_state: dict[str, Any],
        success: bool,
    ) -> list[int] | None:
        """Select only the C branch actually taken by the linked queue.

        The generic planner cannot infer the mutually exclusive empty/non-empty
        branches of ``cola_encolar`` and the singleton transition in
        ``cola_desencolar``.  Those branches determine the pointers learners
        must see, so they are planned explicitly here.
        """
        normalized = [ExecutionTraceService._normalized_line_text(line) for line in lines]

        def index_of(token: str) -> int | None:
            return next((index for index, line in enumerate(normalized) if token in line), None)

        def selected(tokens: list[str]) -> list[int]:
            result: list[int] = []
            for token in tokens:
                index = index_of(token)
                if index is not None and index not in result:
                    result.append(index)
            return result

        before_size = int(before_state.get("size", len(before_state.get("items") or [])) or 0)
        after_size = int(after_state.get("size", len(after_state.get("items") or [])) or 0)

        if operation_name == "encolar" and success:
            branch = "q->delante = aux" if before_size == 0 else "q->atras->sgte = aux"
            return selected([
                "void cola_encolar(",
                "if (q == null)",
                "struct nodocola *aux =",
                "if (aux == null)",
                "aux->nro = valor",
                "aux->sgte = null",
                "if (q->delante == null)",
                branch,
                "q->atras = aux",
            ])

        if operation_name == "desencolar":
            if not success:
                return selected([
                    "int cola_desencolar(",
                    "if (q == null || q->delante == null)",
                    "printf(\"cola vacÃ­a",
                    "return -1",
                ])
            tokens = [
                "int cola_desencolar(",
                "if (q == null || q->delante == null)",
                "struct nodocola *aux = q->delante",
                "int num = aux->nro",
                "q->delante = aux->sgte",
                "if (q->delante == null)",
            ]
            if after_size == 0:
                tokens.append("q->atras = null")
            tokens.extend(["free(aux)", "return num"])
            return selected(tokens)

        if operation_name == "limpiar" and success:
            prefix = selected([
                "void cola_vaciar(",
                "struct nodocola *aux",
                "if (q == null)",
            ])
            loop = index_of("while (q->delante != null)")
            take_front = index_of("aux = q->delante")
            advance_front = index_of("q->delante = aux->sgte")
            free_aux = index_of("free(aux)")
            reset_front = index_of("q->delante = null")
            reset_back = index_of("q->atras = null")
            result = list(prefix)
            count = max(0, before_size)
            for _ in range(count):
                result.extend(index for index in (loop, take_front, advance_front, free_aux) if index is not None)
            # Final false condition, followed by the two explicit normalizations.
            result.extend(index for index in (loop, reset_front, reset_back) if index is not None)
            return result

        return None

    @staticmethod
    def _expand_priority_queue_execution_indexes(
        *,
        operation_name: str,
        lines: list[str],
        before_state: dict[str, Any],
        success: bool,
    ) -> list[int] | None:
        """Expand the priority-queue C path, including every real scan iteration."""
        code_only = re.sub(r"/\*.*?\*/", lambda match: re.sub(r"[^\n]", " ", match.group()), "\n".join(lines), flags=re.DOTALL)
        normalized = [ExecutionTraceService._normalized_line_text(line.split("//", 1)[0]) for line in code_only.split("\n")]

        def find(token: str, occurrence: int = 0) -> int | None:
            matches = [index for index, line in enumerate(normalized) if token in line]
            return matches[occurrence] if occurrence < len(matches) else None

        def add(result: list[int], token: str, occurrence: int = 0) -> None:
            index = find(token, occurrence)
            if index is not None:
                result.append(index)

        items = list(before_state.get("items") or [])
        if operation_name == "encolar":
            result: list[int] = []
            add(result, "bool cp_encolar(")
            add(result, "CPNodo *nuevo;")
            add(result, "if (cola == NULL)")
            add(result, "nuevo = cp_crear_nodo(")
            if len([i for i, line in enumerate(normalized) if "static cpnodo *cp_crear_nodo(" in line]):
                add(result, "static cpnodo *cp_crear_nodo(")
                add(result, "nuevo = (cpnodo *)malloc(")
                add(result, "if (nuevo == null)", 0)
                add(result, "nuevo->valor = valor")
                add(result, "nuevo->prioridad = prioridad")
                add(result, "nuevo->sgte = null")
                # This occurrence is the allocator's return, not cp_encolar's.
                add(result, "return nuevo")
            add(result, "if (nuevo == null)", 1 if find("static cpnodo *cp_crear_nodo(") is not None else 0)
            add(result, "if (cola->delante == null)")
            if not items:
                add(result, "cola->delante = nuevo")
            else:
                add(result, "cola->atras->sgte = nuevo")
            add(result, "cola->atras = nuevo")
            add(result, "cola->cantidad++")
            add(result, "return true")
            return result

        if operation_name in {"desencolar", "frente"}:
            signature = "bool cp_desencolar(" if operation_name == "desencolar" else "bool cp_frente("
            result = []
            add(result, signature)
            declarations = ("cpnodo *actual;", "cpnodo *prev;", "cpnodo *objetivo;", "cpnodo *objetivoprev;") if operation_name == "desencolar" else ("const cpnodo *actual;", "const cpnodo *objetivo;")
            for declaration in declarations:
                add(result, declaration)
            guard = (
                "if (cola == null || cola->delante == null || valor == null || prioridad == null)"
            )
            add(result, guard)
            if not success or not items:
                add(result, "return false")
                return result

            if operation_name == "desencolar":
                for declaration in (
                    "actual = cola->delante", "prev = null", "objetivo = actual", "objetivoprev = null",
                ):
                    add(result, declaration)
                loop_start = find("while (actual != null)")
                comparison = find("if (actual->prioridad < objetivo->prioridad)")
                choose = find("objetivo = actual", 1)
                choose_prev = find("objetivoprev = prev")
                advance_prev = find("prev = actual")
                advance_actual = find("actual = actual->sgte")
                if loop_start is not None:
                    best_index = 0
                    for current_index, item in enumerate(items):
                        result.append(loop_start)
                        if comparison is not None:
                            result.append(comparison)
                        # C uses strict '<', preserving arrival order on ties.
                        candidate_priority = item.get("priority") if isinstance(item, dict) else None
                        # At i=0, actual and objetivo alias the same node: the
                        # C comparison executes and is false, not a selection.
                        if current_index > 0 and candidate_priority < items[best_index].get("priority", 0):
                            if choose is not None:
                                result.append(choose)
                            if choose_prev is not None:
                                result.append(choose_prev)
                            best_index = current_index
                        if advance_prev is not None:
                            result.append(advance_prev)
                        if advance_actual is not None:
                            result.append(advance_actual)
                    result.append(loop_start)  # Final false condition (actual == NULL).
                # Candidate index, stable by first arrival.
                target_index = min(
                    range(len(items)),
                    key=lambda i: (items[i].get("priority", 0), i),
                )
                for token in (
                    "if (objetivo == cola->delante)",
                    "cola->delante = objetivo->sgte",
                ) if target_index == 0 else (
                    "if (objetivo == cola->delante)",
                    "objetivoprev->sgte = objetivo->sgte",
                    "if (cola->atras == objetivo)",
                ):
                    add(result, token)
                if target_index > 0 and target_index == len(items) - 1:
                    add(result, "cola->atras = objetivoprev")
                if target_index == 0:
                    add(result, "if (cola->delante == null)")
                    if len(items) == 1:
                        add(result, "cola->atras = null")
                for token in (
                    "*valor = objetivo->valor", "*prioridad = objetivo->prioridad",
                    "free(objetivo)", "if (cola->cantidad > 0)", "cola->cantidad--", "return true",
                ):
                    add(result, token)
                return result

            # cp_frente uses the same stable minimum scan, but must never unlink
            # or free the selected node.
            for declaration in (
                "objetivo = cola->delante", "actual = cola->delante->sgte",
            ):
                add(result, declaration)
            loop_start = find("while (actual != null)")
            comparison = find("if (actual->prioridad < objetivo->prioridad)")
            choose = find("objetivo = actual")
            advance = find("actual = actual->sgte")
            for current_index in range(1, len(items)):
                if loop_start is not None:
                    result.append(loop_start)
                if comparison is not None:
                    result.append(comparison)
                prior_best = min(range(current_index), key=lambda i: (items[i].get("priority", 0), i))
                if items[current_index].get("priority", 0) < items[prior_best].get("priority", 0) and choose is not None:
                    result.append(choose)
                if advance is not None:
                    result.append(advance)
            if loop_start is not None:
                result.append(loop_start)
            add(result, "*valor = objetivo->valor")
            add(result, "*prioridad = objetivo->prioridad")
            add(result, "return true")
            return result

        if operation_name == "limpiar" and success:
            result = []
            for token in ("void cp_vaciar(", "cpnodo *aux;", "cpnodo *next;", "if (cola == null)", "aux = cola->delante"):
                add(result, token)
            loop_start = find("while (aux != null)")
            save_next = find("next = aux->sgte")
            advance_front = find("cola->delante = next")
            tail_check = find("if (cola->atras == aux)")
            tail_reset = find("cola->atras = null")
            release = find("free(aux)")
            count_check = find("if (cola->cantidad > 0)")
            count_decrement = find("cola->cantidad--")
            advance = find("aux = next")
            for iteration in range(len(items)):
                if loop_start is not None:
                    result.append(loop_start)
                if save_next is not None:
                    result.append(save_next)
                if advance_front is not None:
                    result.append(advance_front)
                if tail_check is not None:
                    result.append(tail_check)
                if iteration == len(items) - 1 and tail_reset is not None:
                    result.append(tail_reset)
                if release is not None:
                    result.append(release)
                if count_check is not None:
                    result.append(count_check)
                if count_decrement is not None:
                    result.append(count_decrement)
                if advance is not None:
                    result.append(advance)
            if loop_start is not None:
                result.append(loop_start)
            add(result, "cola->delante = null")
            add(result, "cola->atras = null", 1)
            add(result, "cola->cantidad = 0")
            return result
        return None

    @staticmethod
    def _expand_linked_list_execution_indexes(
        *,
        operation_name: str,
        lines: list[str],
        before_state: dict[str, Any],
        after_state: dict[str, Any],
        payload: dict[str, Any],
        success: bool,
        message: str,
    ) -> list[int] | None:
        """Plan the concrete branch of the documented singly-linked-list C code.

        A generic control-flow expansion cannot tell whether a list insertion
        took the head, traversal, or invalid-position path.  More importantly,
        it used to keep walking after a C ``return`` and displayed assignments
        from branches that never ran.  This planner keeps the didactic trace
        faithful to ``tad_lista.c`` for each visible operation.
        """
        # Doxygen may mention free(q), printf messages or guards. Select
        # executable C statements only, keeping original source line indexes.
        code_only = re.sub(r"/\*.*?\*/", lambda match: re.sub(r"[^\n]", " ", match.group()), "\n".join(lines), flags=re.DOTALL)
        normalized = [ExecutionTraceService._normalized_line_text(line.split("//", 1)[0]) for line in code_only.split("\n")]

        def find(token: str, start: int = 0) -> int | None:
            return next(
                (index for index in range(start, len(normalized)) if token in normalized[index]),
                None,
            )

        def append(result: list[int], *indexes: int | None) -> None:
            for index in indexes:
                if index is not None:
                    result.append(index)

        def indexes_for(tokens: list[str]) -> list[int]:
            result: list[int] = []
            cursor = 0
            for token in tokens:
                index = find(token, cursor)
                if index is not None:
                    result.append(index)
                    cursor = index + 1
            return result

        before_items = list(before_state.get("items") or [])
        after_items = list(after_state.get("items") or [])
        before_size = len(before_items)
        value = payload.get("value")

        if operation_name == "insertar_inicio" and success:
            result = indexes_for([
                "void lista_insertar_inicio(",
                "if (lista == null)",
                "tlista q = crearnodolista(valor)",
                "if (q == null)",
                "q->sgte = *lista",
                "*lista = q",
            ])
            append(result, next((i for i in range(len(lines)-1, -1, -1) if lines[i].strip() == "}"), None))
            return result

        if operation_name == "insertar_final" and success:
            result = indexes_for([
                "void lista_insertar_final(",
                "if (lista == null)",
                "tlista q = crearnodolista(valor)",
                "if (q == null)",
                "if (*lista == null)",
            ])
            if before_size == 0:
                append(result, find("*lista = q"))
                append(result, next((i for i in range(len(lines)-1, -1, -1) if lines[i].strip() == "}"), None))
                return result
            t_init = find("tlista t = *lista")
            loop = find("while (t->sgte != null)")
            advance = find("t = t->sgte")
            append(result, t_init)
            # One condition evaluation per visited node and one advance per
            # non-final node, followed by the false condition at the tail.
            for index in range(before_size):
                append(result, loop)
                if index < before_size - 1:
                    append(result, advance)
            append(result, find("t->sgte = q"))
            append(result, next((i for i in range(len(lines)-1, -1, -1) if lines[i].strip() == "}"), None))
            return result

        if operation_name == "lista_insertar_elemento":
            position = int(payload.get("position", 0) or 0)
            result = indexes_for([
                "void lista_insertar_elemento(",
                "if (lista == null || pos <= 0)",
                "tlista q = crearnodolista(valor)",
                "if (q == null)",
                "if (pos == 1)",
            ])
            if position == 1 and success and len(after_items) == before_size + 1:
                return result + indexes_for(["q->sgte = *lista", "*lista = q", "return;"])

            t_init = find("tlista t = *lista")
            i_init = find("int i = 1")
            loop = find("while (t != null)")
            position_check = find("if (i == pos)")
            link_q = find("q->sgte = t->sgte")
            link_t = find("t->sgte = q")
            advance_t = find("t = t->sgte")
            advance_i = find("i++")
            append(result, t_init, i_init)
            if success and len(after_items) == before_size + 1 and 1 < position <= before_size:
                for index in range(position):
                    append(result, loop, position_check)
                    if index + 1 < position:
                        append(result, advance_t, advance_i)
                append(result, link_q, link_t, find("return;", (link_t or 0) + 1))
                return result
            # C reaches NULL after testing every existing node, reports the
            # invalid position and releases the temporary q.
            for _ in range(before_size):
                append(result, loop, position_check, advance_t, advance_i)
            append(result, loop, find("error...posicion no encontrada"), find("free(q)"))
            append(result, next((i for i in range(len(lines)-1, -1, -1) if lines[i].strip() == "}"), None))
            return result

        if operation_name == "eliminar_elemento":
            result = indexes_for([
                "void lista_eliminar_elemento(",
                "if (lista == null || *lista == null)",
            ])
            empty_message = "lista vacia" in message.lower() or before_size == 0
            error_print = find("valor no encontrado o lista vacia")
            if empty_message:
                append(result, error_print, find("return;", (error_print or 0) + 1))
                return result
            p_init = find("tlista p = *lista, ant = null")
            loop = find("while (p != null)")
            value_check = find("if (p->nro == valor)")
            head_check = find("if (p == *lista)")
            set_head = find("*lista = p->sgte")
            set_previous = find("ant->sgte = p->sgte")
            free_p = find("free(p)")
            advance_ant = find("ant = p")
            advance_p = find("p = p->sgte")
            append(result, p_init)
            target = next(
                (
                    index
                    for index, item in enumerate(before_items)
                    if str(item.get("value") if isinstance(item, dict) else item) == str(value)
                ),
                -1,
            )
            if success and target >= 0 and len(after_items) == before_size - 1:
                for index in range(target + 1):
                    append(result, loop, value_check)
                    if index == target:
                        append(result, head_check, set_head if target == 0 else set_previous, free_p, find("return;", (free_p or 0) + 1))
                    else:
                        append(result, advance_ant, advance_p)
                return result
            for _ in range(before_size):
                append(result, loop, value_check, advance_ant, advance_p)
            append(result, loop, error_print)
            # No explicit return on not-found: actual closing brace ends scope.
            append(result, next((i for i in range(len(lines)-1, -1, -1) if lines[i].strip() == "}"), None))
            return result

        if operation_name == "buscar_elemento":
            result = indexes_for([
                "void lista_buscar_elemento(",
                "int i = 1, encontrado = 0",
                "tlista q = lista",
            ])
            loop = find("while (q != null)")
            match = find("if (q->nro == valor)")
            print_found = find("encontrado en la posicion")
            set_found = find("encontrado = 1")
            advance_q = find("q = q->sgte")
            advance_i = find("i++")
            for item in before_items:
                item_value = item.get("value") if isinstance(item, dict) else item
                append(result, loop, match)
                if str(item_value) == str(value):
                    append(result, print_found, set_found)
                append(result, advance_q, advance_i)
            append(result, loop)
            # C always evaluates the final guard, including its false branch.
            append(result, find("if (!encontrado)"))
            if not any(str((item.get("value") if isinstance(item, dict) else item)) == str(value) for item in before_items):
                append(result, find("numero no encontrado"))
            append(result, next((i for i in range(len(lines)-1, -1, -1) if lines[i].strip() == "}"), None))
            return result

        if operation_name == "eliminar_repetidos":
            result = indexes_for([
                "void lista_eliminar_repetidos(",
                "if (lista == null || *lista == null)",
            ])
            done_print = find("valores eliminados")
            if before_size == 0:
                append(result, done_print, find("return;", (done_print or 0) + 1))
                return result
            q_init = find("tlista q = *lista, ant = null")
            loop = find("while (q != null)")
            match = find("if (q->nro == valor)")
            temp = find("tlista temp = q")
            head_check = find("if (q == *lista)")
            set_head = find("*lista = q->sgte")
            set_q_head = find("q = *lista", (set_head or 0) + 1)
            set_previous = find("ant->sgte = q->sgte")
            set_q_previous = find("q = ant->sgte")
            free_temp = find("free(temp)")
            advance_ant = find("ant = q")
            advance_q = find("q = q->sgte")
            append(result, q_init)
            head_active = True
            for item in before_items:
                item_value = item.get("value") if isinstance(item, dict) else item
                append(result, loop, match)
                if str(item_value) == str(value):
                    append(result, temp, head_check)
                    if head_active:
                        append(result, set_head, set_q_head)
                    else:
                        append(result, set_previous, set_q_previous)
                    append(result, free_temp)
                else:
                    append(result, advance_ant, advance_q)
                    head_active = False
            append(result, loop, find("valores eliminados", (advance_q or 0) + 1))
            append(result, next((i for i in range(len(lines)-1, -1, -1) if lines[i].strip() == "}"), None))
            return result

        if operation_name == "limpiar" and success:
            direct_clear = indexes_for([
                "void lista_limpiar(",
                "if (lista == null)",
                "tlista q",
            ])
            loop = find("while (*lista != null)")
            take_head = find("q = *lista")
            advance_head = find("*lista = q->sgte")
            free_q = find("free(q)")
            if direct_clear and take_head is not None:
                result = list(direct_clear)
                for _ in range(before_size):
                    append(result, loop, take_head, advance_head, free_q)
                append(result, loop)
                # Actual closing brace: implicit void return/local scope exit.
                append(result, next((i for i in range(len(lines)-1, -1, -1) if lines[i].strip() == "}"), None))
                return result
            read_head = find("int head = (*lista)->nro")
            delete_call = find("lista_eliminar_elemento(lista, head)")
            result: list[int] = []
            for _ in range(before_size):
                append(result, loop, read_head, delete_call)
            append(result, loop)
            return result

        return None

    @staticmethod
    def _expand_circular_list_execution_indexes(
        *,
        operation_name: str,
        lines: list[str],
        before_state: dict[str, Any],
        after_state: dict[str, Any],
        payload: dict[str, Any],
        success: bool,
    ) -> list[int] | None:
        """Expand only the C branches and loop iterations taken by the circular TAD."""
        normalized = [ExecutionTraceService._normalized_line_text(line) for line in lines]

        def find(token: str, start: int = 0) -> int | None:
            return next((i for i in range(start, len(normalized)) if token in normalized[i]), None)

        def add(result: list[int], *indexes: int | None) -> None:
            result.extend(index for index in indexes if index is not None)

        before = list(before_state.get("items") or [])
        after = list(after_state.get("items") or [])
        size = len(before)
        value = str(payload.get("value"))
        values = [str(item.get("value") if isinstance(item, dict) else item) for item in before]
        result: list[int] = []

        def append_allocator() -> None:
            add(result, find("static lcirnodo *lcir_crear_nodo("), find("lcirnodo *nodo = (lcirnodo *)malloc"), find("if (nodo == null)"))
            if success:
                add(result, find("nodo->valor = valor"), find("nodo->sgte = null"), find("return nodo"))
            else:
                add(result, find("return null"))

        if operation_name in {"insertar_inicio", "insertar_final"}:
            result.extend(index for index in (find("bool lcir_insertar_inicio(" if operation_name == "insertar_inicio" else "bool lcir_insertar_final("), find("lcirnodo *nuevo;"), find("if (lista == null)")) if index is not None)
            if not success:
                add(result, find("return false;", (result[-1] + 1) if result else 0))
                return result
            append_allocator()
            # The assignment finishes after the callee returns, not before malloc.
            add(result, find("nuevo = lcir_crear_nodo(valor);"), find("if (nuevo == null)"))
            empty_check = find("if (lista->cabeza == null)")
            add(result, empty_check)
            if size == 0:
                add(result, find("nuevo->sgte = nuevo;", empty_check or 0), find("lista->cabeza = nuevo;", empty_check or 0), find("lista->cola = nuevo;", empty_check or 0), find("lista->cantidad = 1;", empty_check or 0), find("return true;", empty_check or 0))
                return result
            nonempty = find("nuevo->sgte = lista->cabeza;", empty_check or 0)
            add(result, nonempty, find("lista->cola->sgte = nuevo;", nonempty or 0))
            # Identical text in the empty branch is not the instruction executed here.
            add(result, find("lista->cabeza = nuevo;" if operation_name == "insertar_inicio" else "lista->cola = nuevo;", nonempty or 0), find("lista->cantidad++;", nonempty or 0), find("return true;", nonempty or 0))
            return result

        if operation_name in {"buscar_posiciones", "eliminar_primero"}:
            search = operation_name == "buscar_posiciones"
            start_function = find("int lcir_buscar_posiciones(" if search else "bool lcir_eliminar_primero(")
            result = [start_function] if start_function is not None else []
            if search:
                actual_decl = find("lcirnodo *actual;", start_function + 1)
                encontrados = find("int encontrados = 0;", start_function + 1)
                pos_init = find("int pos = 1;", start_function + 1)
                empty_guard = find("if (lista == null || lista->cabeza == null)", start_function + 1)
                actual_init = find("actual = lista->cabeza;", start_function + 1)
                add(result, actual_decl, encontrados, pos_init, empty_guard)
                if size == 0:
                    add(result, find("return 0;", start_function + 1))
                    return result
                add(result, actual_init)
                compare = find("if (actual->valor == valor)", start_function + 1)
                destination_guard = find("if (destino != null && encontrados < capacidad)", start_function + 1)
                save = find("destino[encontrados] = pos;", start_function + 1)
                found_inc = find("encontrados++;", start_function + 1)
                advance = find("actual = actual->sgte;", start_function + 1)
                pos_inc = find("pos++;", start_function + 1)
                loop = find("} while (actual != lista->cabeza);", start_function + 1)
                for index, item_value in enumerate(values):
                    add(result, find("do {", start_function + 1), compare)
                    if item_value == value:
                        add(result, destination_guard)
                        if len(result) >= 0 and index < max(0, int(payload.get("capacity", size) or size)):
                            add(result, save)
                        add(result, found_inc)
                    add(result, advance, pos_inc, loop)
                add(result, find("return encontrados;", start_function + 1))
                return result

            # Delete-by-value: run the circular do/while exactly through the
            # first matching node, or a complete lap when it is not present.
            start_function = result[0] if result else 0
            actual_decl = find("lcirnodo *actual;", start_function + 1)
            previous_decl = find("lcirnodo *anterior;", start_function + 1)
            empty_guard = find("if (lista == null || lista->cabeza == null)", start_function + 1)
            actual_init = find("actual = lista->cabeza;", start_function + 1)
            previous_init = find("anterior = lista->cola;", start_function + 1)
            add(result, actual_decl, previous_decl, empty_guard)
            if size == 0:
                add(result, find("return false;", start_function + 1))
                return result
            add(result, actual_init, previous_init)
            loop = find("do {", start_function + 1)
            compare = find("if (actual->valor == valor)", start_function + 1)
            one_check = find("if (actual == lista->cabeza && actual == lista->cola)", start_function + 1)
            clear_head = find("lista->cabeza = null;", start_function + 1)
            clear_tail = find("lista->cola = null;", start_function + 1)
            set_count_zero = find("lista->cantidad = 0;", start_function + 1)
            free_actual = find("free(actual);", start_function + 1)
            return_true = find("return true;", start_function + 1)
            unlink = find("anterior->sgte = actual->sgte;", start_function + 1)
            head_check = find("if (actual == lista->cabeza)", start_function + 1)
            head_update = find("lista->cabeza = actual->sgte;", start_function + 1)
            tail_check = find("if (actual == lista->cola)", start_function + 1)
            tail_update = find("lista->cola = anterior;", start_function + 1)
            count_check = find("if (lista->cantidad > 0)", start_function + 1)
            count_dec = find("lista->cantidad--;", start_function + 1)
            prev_advance = find("anterior = actual;", start_function + 1)
            actual_advance = find("actual = actual->sgte;", start_function + 1)
            loop_check = find("} while (actual != lista->cabeza);", start_function + 1)
            target = next((i for i, item_value in enumerate(values) if item_value == value), None)
            for index, _ in enumerate(values[: (target + 1) if target is not None else size]):
                add(result, loop, compare)
                if target == index:
                    add(result, one_check)
                    if size == 1:
                        add(result, clear_head, clear_tail, set_count_zero, free_actual, return_true)
                    else:
                        add(result, unlink, head_check)
                        if index == 0:
                            add(result, head_update)
                        add(result, tail_check)
                        if index == size - 1:
                            add(result, tail_update)
                        add(result, count_check, count_dec,
                            find("free(actual);", unlink + 1),
                            find("return true;", unlink + 1))
                    return result
                add(result, prev_advance, actual_advance, loop_check)
            add(result, find("return false;", loop_check + 1))
            return result

        if operation_name == "eliminar_inicio":
            start = find("bool lcir_eliminar_inicio(")
            add(result, start, find("lcirnodo *actual;", (start or 0) + 1), find("if (lista == null || lista->cabeza == null)", (start or 0) + 1))
            if size == 0:
                add(result, find("return false;", (start or 0) + 1))
                return result
            add(result, find("actual = lista->cabeza;", (start or 0) + 1), find("if (lista->cabeza == lista->cola)", (start or 0) + 1))
            if size == 1:
                add(result, find("lista->cabeza = null;", (start or 0) + 1), find("lista->cola = null;", (start or 0) + 1), find("lista->cantidad = 0;", (start or 0) + 1), find("free(actual);", (start or 0) + 1), find("return true;", (start or 0) + 1))
                return result
            add(result, find("lista->cabeza = actual->sgte;", (start or 0) + 1), find("lista->cola->sgte = lista->cabeza;", (start or 0) + 1), find("if (lista->cantidad > 0)", (start or 0) + 1), find("lista->cantidad--;", (start or 0) + 1), find("free(actual);", (find("lista->cabeza = actual->sgte;", (start or 0) + 1) or start or 0) + 1), find("return true;", (find("lista->cabeza = actual->sgte;", (start or 0) + 1) or start or 0) + 1))
            return result

        if operation_name == "invertir":
            start = find("void lcir_invertir(")
            add(result, start, find("lcirnodo *prev;", (start or 0) + 1), find("lcirnodo *curr;", (start or 0) + 1), find("lcirnodo *next;", (start or 0) + 1), find("lcirnodo *old_head;", (start or 0) + 1), find("if (lista == null || lista->cabeza == null || lista->cabeza == lista->cola)", (start or 0) + 1))
            if size <= 1:
                add(result, find("return;", (start or 0) + 1))
                return result
            prev_init = find("prev = lista->cola;", (start or 0) + 1)
            curr_init = find("curr = lista->cabeza;", (start or 0) + 1)
            loop = find("do {", (start or 0) + 1)
            save_next = find("next = curr->sgte;", (start or 0) + 1)
            reverse_link = find("curr->sgte = prev;", (start or 0) + 1)
            prev_update = find("prev = curr;", (start or 0) + 1)
            curr_update = find("curr = next;", (start or 0) + 1)
            loop_check = find("} while (curr != lista->cabeza);", (start or 0) + 1)
            add(result, prev_init, curr_init)
            for _ in range(size):
                add(result, loop, save_next, reverse_link, prev_update, curr_update, loop_check)
            add(result, find("old_head = lista->cabeza;", (start or 0) + 1), find("lista->cabeza = lista->cola;", (start or 0) + 1), find("lista->cola = old_head;", (start or 0) + 1), max(i for i,line in enumerate(lines) if line.strip()=="}"))
            return result

        if operation_name == "limpiar":
            start = find("void lcir_destruir(")
            add(result, start, find("lcirnodo *actual;", (start or 0) + 1), find("lcirnodo *next;", (start or 0) + 1), find("if (lista == null || lista->cabeza == null)", (start or 0) + 1))
            if size == 0:
                add(result, find("return;", (start or 0) + 1))
                return result
            add(result, find("actual = lista->cabeza;", (start or 0) + 1), find("if (lista->cabeza == lista->cola)", (start or 0) + 1))
            if size == 1:
                add(result, find("lista->cabeza = null;", (start or 0) + 1), find("lista->cola = null;", (start or 0) + 1), find("lista->cantidad = 0;", (start or 0) + 1), find("free(actual);", (start or 0) + 1), find("return;", (start or 0) + 1))
                return result
            loop = find("while (actual != lista->cola)", (start or 0) + 1)
            next_line = find("next = actual->sgte;", (start or 0) + 1)
            head_update = find("lista->cabeza = next;", (start or 0) + 1)
            close_cycle = find("lista->cola->sgte = lista->cabeza;", (start or 0) + 1)
            count_guard = find("if (lista->cantidad > 0)", (start or 0) + 1)
            count_dec = find("lista->cantidad--;", (start or 0) + 1)
            free_line = find("free(actual);", loop + 1)
            advance = find("actual = next;", (start or 0) + 1)
            for _ in range(size - 1):
                add(result, loop, next_line, head_update, close_cycle, count_guard, count_dec, free_line, advance)
            add(result, loop, find("lista->cabeza = null;", advance + 1), find("lista->cola = null;", advance + 1), find("lista->cantidad = 0;", advance + 1), find("free(actual);", advance + 1), max(i for i,line in enumerate(lines) if line.strip()=="}"))
            return result

        return None

    @staticmethod
    def _expand_sublist_execution_indexes(
        *, operation_name: str, lines: list[str], before_state: dict[str, Any],
        payload: dict[str, Any], success: bool,
    ) -> list[int] | None:
        """Follow only the C calls, branches and loop iterations for a sublist operation."""
        normalized = [ExecutionTraceService._normalized_line_text(line) for line in lines]
        items = list(before_state.get("items") or [])
        result: list[int] = []

        def find(token: str, start: int = 0) -> int | None:
            needle = ExecutionTraceService._normalized_line_text(token)
            return next((i for i in range(start, len(normalized)) if needle in normalized[i]), None)

        def add(*indexes: int | None) -> None:
            result.extend(index for index in indexes if index is not None)

        def expand_parent_search(value: Any) -> bool:
            start = find("Nodo *sublista_buscar_padre(")
            if start is None:
                return False
            add(start, find("Nodo *actual = lista;", start + 1))
            target = next((i for i, item in enumerate(items) if str(item.get("parent")) == str(value)), None)
            loop = find("while (actual != NULL)", start + 1)
            compare = find("if (actual->nro == valor_padre)", start + 1)
            advance = find("actual = actual->sgte;", start + 1)
            return_node = find("return actual;", start + 1)
            return_null = find("return NULL;", start + 1)
            for index, _item in enumerate(items if target is None else items[:target + 1]):
                add(loop, compare)
                if target == index:
                    add(return_node)
                    return True
                add(advance)
            add(loop, return_null)
            return target is not None

        def expand_allocator(function_name: str, value_field: str, value: Any) -> None:
            start = find(f"static {'Nodo' if function_name == 'crear_padre' else 'Sublista'} *{function_name}(")
            if start is None:
                return
            add(start, find("malloc(sizeof(", start + 1), find("if (nuevo == NULL)", start + 1))
            add(find(f"nuevo->{value_field} = valor", start + 1))
            if function_field := find("nuevo->sgte = NULL;", start + 1):
                add(function_field)
            if function_name == "crear_padre":
                add(find("nuevo->sub = NULL;", start + 1))
            add(find("return nuevo;", start + 1))

        if operation_name == "insertar_padre":
            start = find("Nodo *sublista_insertar_padre_final(")
            add(start, find("Nodo *nuevo;", start or 0), find("Nodo *actual;", start or 0), find("if (lista == NULL)", start or 0), find("nuevo = crear_padre(valor_padre);", start or 0))
            expand_allocator("crear_padre", "nro", payload.get("parent"))
            add(find("nuevo = crear_padre(valor_padre);", start or 0))
            add(find("if (nuevo == NULL)", start or 0))
            empty = not items
            add(find("if (*lista == NULL)", start or 0))
            if empty:
                add(find("*lista = nuevo;", start or 0), find("return nuevo;", start or 0))
            else:
                add(find("actual = *lista;", start or 0))
                loop = find("while (actual->sgte != NULL)", start or 0)
                advance = find("actual = actual->sgte;", start or 0)
                for _ in range(max(0, len(items) - 1)):
                    add(loop, advance)
                add(loop, find("actual->sgte = nuevo;", start or 0), find("return nuevo;", find("actual->sgte = nuevo;", start or 0) or start or 0))
            return result

        if operation_name == "insertar_hijo":
            start = find("bool sublista_insertar_hijo(")
            add(start, find("Nodo *padre = sublista_buscar_padre(", start or 0))
            parent_found = expand_parent_search(payload.get("parent"))
            add(find("Nodo *padre = sublista_buscar_padre(", start or 0))
            add(find("if (padre == NULL)", start or 0))
            if not parent_found:
                add(find("return false;", start or 0))
                return result
            add(find("return sublista_insertar_hijo_final(", start or 0))
            insert = find("bool sublista_insertar_hijo_final(")
            add(insert, find("Sublista *nuevo;", insert or 0), find("Sublista *actual;", insert or 0), find("if (padre == NULL)", insert or 0), find("nuevo = crear_hijo(valor_hijo);", insert or 0))
            expand_allocator("crear_hijo", "nro", payload.get("child"))
            add(find("nuevo = crear_hijo(valor_hijo);", insert or 0))
            add(find("if (nuevo == NULL)", insert or 0), find("if (padre->sub == NULL)", insert or 0))
            children = next((item.get("children", []) for item in items if str(item.get("parent")) == str(payload.get("parent"))), [])
            if not children:
                add(find("padre->sub = nuevo;", insert or 0), find("return true;", insert or 0))
            else:
                add(find("actual = padre->sub;", insert or 0))
                loop = find("while (actual->sgte != NULL)", insert or 0)
                advance = find("actual = actual->sgte;", insert or 0)
                for _ in range(max(0, len(children) - 1)):
                    add(loop, advance)
                add(loop, find("actual->sgte = nuevo;", insert or 0), find("return true;", find("actual->sgte = nuevo;", insert or 0) or insert or 0))
            add(find("return sublista_insertar_hijo_final(", start or 0))
            return result

        if operation_name == "eliminar_padre":
            start = find("bool sublista_eliminar_padre_primero(")
            add(start, find("Nodo *actual;", start or 0), find("Nodo *anterior = NULL;", start or 0), find("if (lista == NULL || *lista == NULL)", start or 0))
            if not items:
                add(find("return false;", start or 0))
                return result
            target = next((i for i, item in enumerate(items) if str(item.get("parent")) == str(payload.get("parent"))), None)
            if target is None:
                add(find("actual = *lista;", start or 0))
                loop = find("while (actual != NULL)", start or 0)
                compare = find("if (actual->nro == valor_padre)", start or 0)
                for _ in items:
                    add(loop, compare, find("anterior = actual;", start or 0), find("actual = actual->sgte;", start or 0))
                parent_end = ExecutionTraceService._find_matching_brace_line(lines, start) if start is not None else len(normalized)-1
                false_returns = [i for i in range((start or 0) + 1, parent_end + 1) if "return false;" in normalized[i]]
                add(loop, false_returns[-1] if false_returns else None)
                return result
            add(find("actual = *lista;", start or 0))
            loop, compare = find("while (actual != NULL)", start or 0), find("if (actual->nro == valor_padre)", start or 0)
            for index in range(target + 1):
                add(loop, compare)
                if index < target:
                    add(find("anterior = actual;", start or 0), find("actual = actual->sgte;", start or 0))
            add(find("if (anterior == NULL)", start or 0))
            if target == 0:
                add(find("*lista = actual->sgte;", start or 0))
            else:
                add(find("anterior->sgte = actual->sgte;", start or 0))
            add(find("destruir_hijos(&actual->sub);", start or 0))
            helper = find("static void destruir_hijos(")
            if helper is not None:
                add(helper, find("Sublista *actual;", helper + 1), find("Sublista *next;", helper + 1), find("if (lista_hijos == NULL)", helper + 1), find("actual = *lista_hijos;", helper + 1))
                children = list(items[target].get("children", []))
                loop_child = find("while (actual != NULL)", helper + 1)
                for _ in children:
                    add(loop_child, find("next = actual->sgte;", helper + 1), find("*lista_hijos = next;", helper + 1), find("free(actual);", helper + 1), find("actual = next;", helper + 1))
                # A void helper reaches its closing brace; its NULL-address guard did not return.
                helper_end = ExecutionTraceService._find_matching_brace_line(lines, helper)
                add(loop_child, helper_end)
                add(find("destruir_hijos(&actual->sub);", start or 0))
            add(find("free(actual);", start or 0), find("return true;", start or 0))
            return result

        if operation_name == "eliminar_hijo":
            start = find("bool sublista_eliminar_hijo(")
            add(start, find("Nodo *padre = sublista_buscar_padre(", start or 0))
            parent_found = expand_parent_search(payload.get("parent"))
            # The assignment completes only after the search helper returns.
            add(find("Nodo *padre = sublista_buscar_padre(", start or 0))
            add(find("if (padre == NULL)", start or 0))
            if not parent_found:
                add(find("return false;", start or 0))
                return result
            add(find("return sublista_eliminar_hijo_primero(", start or 0))
            remove = find("bool sublista_eliminar_hijo_primero(")
            children = next((list(item.get("children", [])) for item in items if str(item.get("parent")) == str(payload.get("parent"))), [])
            target = next((i for i, value in enumerate(children) if str(value) == str(payload.get("child"))), None)
            add(remove, find("Sublista *actual;", remove or 0), find("Sublista *anterior = NULL;", remove or 0), find("if (padre == NULL || padre->sub == NULL)", remove or 0))
            guard = find("if (padre == NULL || padre->sub == NULL)", remove or 0)
            if not children:
                add(find("return false;", guard or 0))
                add(find("return sublista_eliminar_hijo_primero(", start or 0))
                return result
            add(find("actual = padre->sub;", remove or 0))
            loop = find("while (actual != NULL)", remove or 0)
            compare = find("if (actual->nro == valor_hijo)", remove or 0)
            for index in range(len(children)):
                add(loop, compare)
                if index == target:
                    add(find("if (anterior == NULL)", remove or 0))
                    add(find("padre->sub = actual->sgte;" if index == 0 else "anterior->sgte = actual->sgte;", remove or 0))
                    add(find("free(actual);", remove or 0), find("return true;", remove or 0))
                    add(find("return sublista_eliminar_hijo_primero(", start or 0))
                    return result
                add(find("anterior = actual;", remove or 0), find("actual = actual->sgte;", remove or 0))
            # The absent-child return follows the completed loop, not the empty guard.
            advance = find("actual = actual->sgte;", remove or 0)
            add(loop, find("return false;", advance or 0))
            add(find("return sublista_eliminar_hijo_primero(", start or 0))
            return result

        if operation_name == "hijos_de":
            start = find("int sublista_obtener_hijos(")
            add(start, find("Nodo *padre = sublista_buscar_padre(", start or 0))
            parent_found = expand_parent_search(payload.get("parent"))
            add(find("Nodo *padre = sublista_buscar_padre(", start or 0))
            add(find("if (padre == NULL)", start or 0))
            if not parent_found:
                add(find("return -1;", start or 0))
                return result
            add(find("return sublista_copiar_hijos(", start or 0))
            copy = find("int sublista_copiar_hijos(")
            children = next((list(item.get("children", [])) for item in items if str(item.get("parent")) == str(payload.get("parent"))), [])
            add(copy, find("int usados = 0;", copy or 0), find("const Sublista *actual;", copy or 0), find("if (padre == NULL || destino == NULL || capacidad <= 0)", copy or 0))
            # Valid padre/destino/capacidad do not return early for an empty branch.
            add(find("actual = padre->sub;", copy or 0))
            loop = find("while (actual != NULL && usados < capacidad)", copy or 0)
            for _ in children[:1024]:
                add(loop, find("destino[usados] = actual->nro;", copy or 0), find("usados++;", copy or 0), find("actual = actual->sgte;", copy or 0))
            add(loop)
            add(find("return usados;", copy or 0))
            add(find("return sublista_copiar_hijos(", start or 0))
            return result

        if operation_name == "limpiar":
            start = find("void sublista_destruir(")
            helper = find("static void destruir_hijos(")
            add(start, find("Nodo *actual;", start or 0), find("Nodo *next;", start or 0), find("if (lista == NULL)", start or 0))
            add(find("actual = *lista;", start or 0))
            parent_loop = find("while (actual != NULL)", start or 0)
            for item in items:
                add(parent_loop, find("next = actual->sgte;", start or 0), find("destruir_hijos(&actual->sub);", start or 0))
                children = list(item.get("children", []))
                if helper is not None:
                    add(helper, find("Sublista *actual;", helper + 1), find("Sublista *next;", helper + 1), find("if (lista_hijos == NULL)", helper + 1), find("actual = *lista_hijos;", helper + 1))
                    child_loop = find("while (actual != NULL)", helper + 1)
                    for _ in children:
                        add(child_loop, find("next = actual->sgte;", helper + 1), find("*lista_hijos = next;", helper + 1), find("free(actual);", helper + 1), find("actual = next;", helper + 1))
                    add(child_loop, ExecutionTraceService._find_matching_brace_line(lines, helper))
                    add(find("destruir_hijos(&actual->sub);", start or 0))
                add(find("*lista = next;", start or 0), find("free(actual);", start or 0), find("actual = next;", start or 0))
            add(parent_loop, ExecutionTraceService._find_matching_brace_line(lines, start))
            return result

        return None

    @staticmethod
    def _get_operation_source(
        didactic_data: dict[str, Any],
        operation_name: str,
    ) -> tuple[str, str]:
        code_title = str(didactic_data.get("code_title", "Codigo C"))
        operation_map = didactic_data.get("operations", {})
        if not isinstance(operation_map, dict):
            operation_map = {}
        source = str(
            operation_map.get(
                operation_name,
                didactic_data.get(
                    "default_operation",
                    "/* Codigo no disponible para esta operacion. */",
                ),
            )
        )
        return source, code_title

    @staticmethod
    def _state_kind(state: dict[str, Any]) -> str:
        return str(state.get("kind") or state.get("structure") or "").strip().lower()

    @staticmethod
    def _tree_family(state: dict[str, Any]) -> str:
        title = str(state.get("title", "")).lower()
        if "avl" in title:
            return "avl"
        if "rojo" in title or "red-black" in title or "negro" in title:
            return "red_black"
        return "abb"


    _build_graph_debug_steps = staticmethod(GraphTracePlanner._build_graph_debug_steps)
    _expand_graph_control_flow_indexes = staticmethod(GraphTracePlanner._expand_graph_control_flow_indexes)
    _expand_graph_kruskal_indexes = staticmethod(GraphAlgorithmPlanner.expand_kruskal)
    _expand_graph_dijkstra_indexes = staticmethod(GraphAlgorithmPlanner.expand_dijkstra)
    _expand_graph_bfs_indexes = staticmethod(GraphAlgorithmPlanner.expand_bfs)
    _expand_graph_bellman_ford_indexes = staticmethod(GraphAlgorithmPlanner.expand_bellman_ford)
    _expand_recursive_graph_dfs_indexes = staticmethod(GraphAlgorithmPlanner.expand_dfs)
    _extract_tree_node_value = staticmethod(TreeAlgorithmPlanner.node_value)
    _tree_child = staticmethod(TreeAlgorithmPlanner.child)
    _find_line_index_by_contains = staticmethod(GraphAlgorithmPlanner.find_line)
    _expand_recursive_abb_insert_indexes = staticmethod(TreeAlgorithmPlanner.expand_abb_insert)
    _expand_recursive_abb_delete_indexes = staticmethod(TreeAlgorithmPlanner.expand_abb_delete)
    _expand_avl_insert_indexes = staticmethod(TreeAlgorithmPlanner.expand_avl_insert)
    _expand_rbt_insert_indexes = staticmethod(TreeAlgorithmPlanner.expand_rbt_insert)
    _expand_rbt_delete_indexes = staticmethod(TreeAlgorithmPlanner.expand_rbt_delete)
    _expand_tree_extreme_indexes = staticmethod(TreeQueryPlanner.expand_extreme)
    _expand_recursive_bst_traversal_indexes = staticmethod(TreeQueryPlanner.expand_traversal)
    _expand_recursive_tree_metrics_indexes = staticmethod(TreeQueryPlanner.expand_metrics)
    _expand_recursive_tree_clear_indexes = staticmethod(TreeQueryPlanner.expand_clear)

    @staticmethod
    def _expand_recursive_abb_indexes(
        *,
        operation_name: str,
        lines: list[str],
        before_state: dict[str, Any],
        after_state: dict[str, Any],
        payload: dict[str, Any],
        success: bool,
    ) -> list[int] | None:
        if operation_name == "limpiar":
            expanded_clear = ExecutionTraceService._expand_recursive_tree_clear_indexes(
                lines=lines,
                before_state=before_state,
                after_state=after_state,
            )
            if expanded_clear is not None:
                return expanded_clear

        if operation_name in {"minimo", "maximo"}:
            return ExecutionTraceService._expand_tree_extreme_indexes(
                operation_name=operation_name,
                lines=lines,
                before_state=before_state,
                after_state=after_state,
            )

        normalized_join = "\n".join(ExecutionTraceService._normalized_line_text(line) for line in lines)
        if (
            "abb_insertar(" not in normalized_join
            and "abb_eliminar(" not in normalized_join
            and "_inorden(" not in normalized_join
            and "_preorden(" not in normalized_join
            and "_postorden(" not in normalized_join
            and "abb_altura(" not in normalized_join
            and "avl_altura(" not in normalized_join
            and "rbt_altura(" not in normalized_join
            and "abb_contarhojas(" not in normalized_join
            and "avl_validar_fes(" not in normalized_join
            and "rbt_validar(" not in normalized_join
            and "abb_validar_" not in normalized_join
            and "void avl_insertar(" not in normalized_join
            and "void rbt_insertar(" not in normalized_join
            and "void rbt_eliminar(" not in normalized_join
        ):
            return None

        if operation_name == "insertar" and "void avl_insertar(" in normalized_join:
            return ExecutionTraceService._expand_avl_insert_indexes(
                lines=lines,
                before_state=before_state,
                after_state=after_state,
                payload=payload,
                success=success,
            )
        if operation_name == "insertar" and "void rbt_insertar(" in normalized_join:
            return ExecutionTraceService._expand_rbt_insert_indexes(
                lines=lines,
                before_state=before_state,
                payload=payload,
                success=success,
            )
        if operation_name == "eliminar" and "void rbt_eliminar(" in normalized_join:
            return ExecutionTraceService._expand_rbt_delete_indexes(
                lines=lines,
                before_state=before_state,
                payload=payload,
            )
        if operation_name == "insertar" and "abb_insertar(" in normalized_join:
            return ExecutionTraceService._expand_recursive_abb_insert_indexes(
                lines=lines,
                before_state=before_state,
                payload=payload,
                success=success,
            )
        if operation_name == "eliminar" and "abb_eliminar(" in normalized_join:
            return ExecutionTraceService._expand_recursive_abb_delete_indexes(
                lines=lines,
                before_state=before_state,
                payload=payload,
            )
        if operation_name in {"altura", "contar_hojas", "validar"}:
            expanded_metrics = ExecutionTraceService._expand_recursive_tree_metrics_indexes(
                operation_name=operation_name,
                lines=lines,
                before_state=before_state,
                after_state=after_state,
            )
            if expanded_metrics is not None:
                return expanded_metrics
        return ExecutionTraceService._expand_recursive_bst_traversal_indexes(
            operation_name=operation_name,
            lines=lines,
            before_state=before_state,
            after_state=after_state,
        )

    _expand_tree_extreme_indexes = staticmethod(TreeQueryPlanner.expand_extreme)
    _expand_recursive_bst_traversal_indexes = staticmethod(TreeQueryPlanner.expand_traversal)
    _expand_recursive_tree_metrics_indexes = staticmethod(TreeQueryPlanner.expand_metrics)
    _expand_recursive_tree_clear_indexes = staticmethod(TreeQueryPlanner.expand_clear)

    @staticmethod
    def _build_boundaries(
        structure_id: str,
        before_state: dict[str, Any],
        after_state: dict[str, Any],
        total_steps: int,
        mutates: bool,
        operation_name: str,
        payload: dict[str, Any],
        step_lines: list[str],
    ) -> list[dict[str, Any]]:
        boundaries = total_steps + 1
        if boundaries <= 1:
            return [deepcopy(before_state), deepcopy(after_state)]
        priority_peek = structure_id == "priority_queue" and operation_name == "frente"
        sublist_trace = structure_id == "sublist"
        linked_search = structure_id == "linked_list" and operation_name == "buscar_elemento"
        circular_delete_head = structure_id == "circular_list" and operation_name in {"eliminar_inicio", "buscar_posiciones", "eliminar_primero", "limpiar", "invertir"}
        if (not mutates and not priority_peek and not sublist_trace and not linked_search and not circular_delete_head) or (before_state == after_state and structure_id != "linked_list" and not priority_peek and not sublist_trace and not circular_delete_head):
            states = [deepcopy(before_state) for _ in range(boundaries)]
            states[-1] = deepcopy(after_state)
            return states

        state_kind = ExecutionTraceService._state_kind(after_state)
        if state_kind in {"linear", "circular", "sublist", "priority"}:
            strategy = TraceStrategyRegistry.resolve(structure_id)
            if not isinstance(strategy, SequentialTraceStrategy):
                raise TypeError(f"La estrategia de '{structure_id}' no es secuencial.")
            return strategy.build_boundaries(before_state, after_state, total_steps, step_lines, payload=payload)
        if state_kind == "heap":
            strategy = TraceStrategyRegistry.resolve(structure_id)
            if not isinstance(strategy, TreeTraceStrategy):
                raise TypeError(f"La estrategia de '{structure_id}' no es de Ã¡rbol.")
            return strategy.build_heap_boundaries(before_state, after_state, total_steps, step_lines)
        if state_kind == "binary_tree":
            strategy = TraceStrategyRegistry.resolve(structure_id)
            if not isinstance(strategy, TreeTraceStrategy):
                raise TypeError(f"La estrategia de '{structure_id}' no es de Ã¡rbol.")
            return strategy.build_boundaries(
                before_state,
                after_state,
                total_steps,
                operation_name,
                payload,
                step_lines,
            )
        if state_kind == "graph":
            strategy = TraceStrategyRegistry.resolve(structure_id)
            if not isinstance(strategy, GraphTraceStrategy):
                raise TypeError(f"La estrategia de '{structure_id}' no es de grafo.")
            return strategy.build_boundaries(before_state, after_state, total_steps, step_lines)
        if state_kind == "hash_table":
            strategy = TraceStrategyRegistry.resolve(structure_id)
            if not isinstance(strategy, HashTraceStrategy):
                raise TypeError(f"La estrategia de '{structure_id}' no es hash.")
            return strategy.build_boundaries(before_state, after_state, total_steps, step_lines)

        states = [deepcopy(before_state) for _ in range(boundaries)]
        switch_index = max(1, int(boundaries * 0.7))
        for index in range(switch_index, boundaries):
            states[index] = deepcopy(after_state)
        states[0] = deepcopy(before_state)
        states[-1] = deepcopy(after_state)
        return states

    @staticmethod
    def build_trace(
        *,
        structure_id: str,
        operation_name: str,
        payload: dict[str, Any],
        didactic_data: dict[str, Any],
        before_state: dict[str, Any],
        after_state: dict[str, Any],
        success: bool,
        message: str,
        mutates: bool,
        console_events: list[str] | None = None,
    ) -> dict[str, Any]:
        """Build one execution trace consumable by frontend animation runtimes."""
        source_code, code_title = ExecutionTraceService._get_operation_source(
            didactic_data=didactic_data,
            operation_name=operation_name.removeprefix("cp_") if structure_id == "priority_queue" else operation_name,
        )
        if structure_id == "linked_list" and operation_name in {"eliminar_inicio", "eliminar_final", "mostrar", "primero"}:
            from app.domain.sequential.hidden_list_terminal_instruction import build_hidden_terminal_trace
            return build_hidden_terminal_trace(operation_name=operation_name, payload=payload,
                source_code=source_code, code_title=code_title, before_state=before_state,
                after_state=after_state, success=success, message=message)
        if structure_id == "linked_list" and operation_name == "ultimo":
            from app.domain.sequential.linked_last_instruction import build_linked_last_trace
            return build_linked_last_trace(payload=payload, source_code=source_code,
                code_title=code_title, before_state=before_state, after_state=after_state,
                success=success, message=message)
        if structure_id == "linked_list" and operation_name in {"insertar_elemento", "insertar_posicion", "eliminar_posicion"}:
            from app.domain.sequential.hidden_positional_instruction import build_hidden_positional_trace
            return build_hidden_positional_trace(operation_name=operation_name, payload=payload,
                source_code=source_code, code_title=code_title, before_state=before_state,
                after_state=after_state, success=success, message=message)
        if structure_id == "graph" and operation_name in {
                "create_graph", "clear_graph", "insert_edge", "remove_edge", "exists_vertex",
                "exists_edge", "edge_weight", "list_vertices", "list_edges", "generate_random_graph"}:
            from app.domain.graph.construction_instruction import build_graph_construction_trace
            return build_graph_construction_trace(operation_name=operation_name, payload=payload,
                source_code=source_code, code_title=code_title, before_state=before_state,
                after_state=after_state, success=success, message=message)
        if structure_id == "graph" and operation_name == "neighbors":
            from app.domain.graph.neighbor_instruction import build_graph_neighbor_trace
            return build_graph_neighbor_trace(payload=payload, source_code=source_code,
                code_title=code_title, before_state=before_state, after_state=after_state,
                success=success, message=message)
        if structure_id == "graph" and operation_name in {"insert_vertex", "remove_vertex"}:
            from app.domain.graph.vertex_instruction import build_graph_vertex_trace
            return build_graph_vertex_trace(operation_name=operation_name, payload=payload,
                source_code=source_code, code_title=code_title, before_state=before_state,
                after_state=after_state, success=success, message=message,
                translate_incident_arcs=operation_name == "remove_vertex")
        if structure_id == "graph" and operation_name in {"run_dijkstra", "run_bellman_ford", "run_prim", "run_kruskal"}:
            from app.domain.graph.numeric_instruction import build_graph_numeric_trace
            trace = build_graph_numeric_trace(operation_name=operation_name, payload=payload,
                source_code=source_code, code_title=code_title, before_state=before_state,
                after_state=after_state, success=success, message=message)
            # The numeric builder validates each legacy conversion and all
            # engine boundaries before compacting its exact snapshot transport.
            return trace
        if structure_id == "priority_queue" and operation_name.removeprefix("cp_") in {
                "inicializar", "vacia", "contar", "copiar_items", "formatear"}:
            from app.domain.sequential.priority_queue_helpers_instruction import build_priority_helper_trace
            return build_priority_helper_trace(operation_name=operation_name, payload=payload,
                source_code=source_code, code_title=code_title, before_state=before_state,
                after_state=after_state, success=success, message=message)
        if structure_id in {"stack", "queue"} and operation_name == "mostrar":
            from app.domain.sequential.show_instruction import build_show_trace
            return build_show_trace(structure_id=structure_id, payload=payload, source_code=source_code,
                code_title=code_title, before_state=before_state, after_state=after_state, success=success, message=message)
        if structure_id == "priority_queue" and operation_name == "frente" and (success or not before_state.get("items")):
            from app.domain.sequential.priority_queue_front_instruction import build_priority_queue_front_trace
            return build_priority_queue_front_trace(payload=payload, source_code=source_code, code_title=code_title,
                before_state=before_state, after_state=after_state, success=success, message=message)
        if structure_id == "priority_queue" and operation_name == "desencolar" and (success or not before_state.get("items")):
            from app.domain.sequential.priority_queue_dequeue_instruction import build_priority_queue_dequeue_trace
            return build_priority_queue_dequeue_trace(payload=payload, source_code=source_code, code_title=code_title,
                before_state=before_state, after_state=after_state, success=success, message=message)
        if structure_id == "priority_queue" and operation_name == "encolar" and success:
            from app.domain.sequential.priority_queue_enqueue_instruction import build_priority_queue_enqueue_trace
            return build_priority_queue_enqueue_trace(payload=payload, source_code=source_code, code_title=code_title,
                before_state=before_state, after_state=after_state, success=success, message=message)
        if structure_id == "queue" and operation_name in {"frente", "final"}:
            from app.domain.sequential.queue_query_instruction import build_queue_query_trace
            return build_queue_query_trace(operation_name=operation_name, payload=payload, source_code=source_code,
                code_title=code_title, before_state=before_state, after_state=after_state, success=success, message=message)
        if structure_id == "queue" and operation_name == "desencolar" and (success or not before_state.get("items")):
            from app.domain.sequential.queue_dequeue_instruction import build_queue_dequeue_trace
            return build_queue_dequeue_trace(payload=payload, source_code=source_code, code_title=code_title,
                before_state=before_state, after_state=after_state, success=success, message=message)
        if structure_id == "queue" and operation_name == "encolar" and success:
            from app.domain.sequential.queue_enqueue_instruction import build_queue_enqueue_trace
            return build_queue_enqueue_trace(payload=payload, source_code=source_code, code_title=code_title,
                before_state=before_state, after_state=after_state, success=success, message=message)
        if structure_id == "stack" and operation_name == "cima":
            from app.domain.sequential.stack_top_instruction import build_stack_top_trace
            return build_stack_top_trace(payload=payload, source_code=source_code, code_title=code_title,
                before_state=before_state, after_state=after_state, success=success, message=message)
        if structure_id == "stack" and operation_name == "apilar" and success:
            from app.domain.sequential.stack_push_instruction import build_stack_push_trace
            return build_stack_push_trace(payload=payload,source_code=source_code,code_title=code_title,
                before_state=before_state,after_state=after_state,success=bool(success),message=str(message))
        if structure_id == "stack" and operation_name == "limpiar" and success:
            from app.domain.sequential.stack_cleanup_instruction import build_stack_cleanup_trace
            return build_stack_cleanup_trace(payload=payload, source_code=source_code,
                code_title=code_title, before_state=before_state, after_state=after_state,
                success=bool(success), message=str(message))
        if structure_id == "queue" and operation_name == "limpiar" and success:
            from app.domain.sequential.queue_cleanup_instruction import build_queue_cleanup_trace
            return build_queue_cleanup_trace(payload=payload, source_code=source_code,
                code_title=code_title, before_state=before_state, after_state=after_state,
                success=bool(success), message=str(message))
        if structure_id == "priority_queue" and operation_name == "limpiar" and success:
            from app.domain.sequential.priority_queue_cleanup_instruction import build_priority_queue_cleanup_trace
            return build_priority_queue_cleanup_trace(payload=payload, source_code=source_code,
                code_title=code_title, before_state=before_state, after_state=after_state,
                success=bool(success), message=str(message))
        if structure_id == "hash_table" and operation_name in {"clear", "destroy_table"}:
            from app.domain.hash.clear_destroy_instruction import build_hash_clear_destroy_trace
            return build_hash_clear_destroy_trace(operation_name=operation_name, payload=payload,
                source_code=source_code, code_title=code_title, before_state=before_state,
                after_state=after_state, success=bool(success), message=str(message))
        if structure_id == "hash_table" and operation_name == "stats":
            from app.domain.hash.stats_instruction import build_hash_stats_trace
            return build_hash_stats_trace(operation_name=operation_name, payload=payload,
                source_code=source_code, code_title=code_title, before_state=before_state,
                after_state=after_state, success=bool(success), message=str(message))
        if structure_id == "hash_table" and operation_name in {"keys", "values", "items"}:
            from app.domain.hash.listing_instruction import build_hash_listing_trace
            return build_hash_listing_trace(operation_name=operation_name, payload=payload,
                source_code=source_code, code_title=code_title, before_state=before_state,
                after_state=after_state, success=bool(success), message=str(message))
        if structure_id == "hash_table" and operation_name == "remove":
            from app.domain.hash.remove_instruction import build_hash_remove_trace
            return build_hash_remove_trace(operation_name=operation_name, payload=payload,
                source_code=source_code, code_title=code_title, before_state=before_state,
                after_state=after_state, success=bool(success), message=str(message))
        if structure_id == "hash_table" and operation_name in {"get", "contains"}:
            from app.domain.hash.query_instruction import build_hash_query_trace
            return build_hash_query_trace(operation_name=operation_name, payload=payload,
                source_code=source_code, code_title=code_title, before_state=before_state,
                after_state=after_state, success=bool(success), message=str(message))
        if structure_id == "hash_table" and operation_name in {"create_table", "insert"}:
            from app.domain.hash.creation_insert_instruction import build_hash_instruction_trace
            return build_hash_instruction_trace(operation_name=operation_name, payload=payload,
                source_code=source_code, code_title=code_title, before_state=before_state,
                after_state=after_state, success=bool(success), message=str(message))
        lines = source_code.replace("\r\n", "\n").split("\n")
        state_kind = ExecutionTraceService._state_kind(after_state)
        executable_line_indexes = [
            index
            for index, line in enumerate(lines)
            if ExecutionTraceService._is_executable_line(line, code_title)
        ]
        executable_line_indexes = ExecutionTraceService._filter_trace_lines_by_control_flow(
            lines,
            executable_line_indexes,
            bool(success),
            str(message),
            state_kind,
        )
        recursive_tree_indexes = None
        if state_kind == "binary_tree":
            recursive_tree_indexes = ExecutionTraceService._expand_recursive_abb_indexes(
                operation_name=operation_name,
                lines=lines,
                before_state=before_state,
                after_state=after_state,
                payload=payload,
                success=bool(success),
            )
        hash_indexes = None
        if state_kind == "hash_table":
            hash_indexes = HashControlFlowPlanner.expand(
                operation_name=operation_name,
                lines=lines,
                before_state=before_state,
                payload=payload,
                message=str(message),
            )
        if hash_indexes is not None:
            executable_line_indexes = hash_indexes
        elif recursive_tree_indexes is not None:
            executable_line_indexes = recursive_tree_indexes
        elif state_kind != "graph":
            executable_line_indexes = ExecutionTraceService._expand_generic_control_flow_indexes(
                operation_name=operation_name,
                lines=lines,
                executable_line_indexes=executable_line_indexes,
                before_state=before_state,
                after_state=after_state,
                success=bool(success),
                message=str(message),
                payload=payload,
            )

        if structure_id == "queue":
            queue_indexes = ExecutionTraceService._expand_queue_execution_indexes(
                operation_name=operation_name,
                lines=lines,
                before_state=before_state,
                after_state=after_state,
                success=bool(success),
            )
            if queue_indexes is not None:
                executable_line_indexes = queue_indexes
        elif structure_id == "priority_queue":
            priority_indexes = ExecutionTraceService._expand_priority_queue_execution_indexes(
                operation_name=operation_name,
                lines=lines,
                before_state=before_state,
                success=bool(success),
            )
            if priority_indexes is not None:
                executable_line_indexes = priority_indexes
        elif structure_id == "linked_list":
            linked_list_indexes = ExecutionTraceService._expand_linked_list_execution_indexes(
                operation_name=operation_name,
                lines=lines,
                before_state=before_state,
                after_state=after_state,
                payload=payload,
                success=bool(success),
                message=str(message),
            )
            if linked_list_indexes is not None:
                executable_line_indexes = linked_list_indexes
        elif structure_id == "circular_list":
            circular_list_indexes = ExecutionTraceService._expand_circular_list_execution_indexes(
                operation_name=operation_name,
                lines=lines,
                before_state=before_state,
                after_state=after_state,
                payload=payload,
                success=bool(success),
            )
            if circular_list_indexes is not None:
                executable_line_indexes = circular_list_indexes
        elif structure_id == "sublist":
            sublist_indexes = ExecutionTraceService._expand_sublist_execution_indexes(
                operation_name=operation_name,
                lines=lines,
                before_state=before_state,
                payload=payload,
                success=bool(success),
            )
            if sublist_indexes is not None:
                executable_line_indexes = sublist_indexes
        elif state_kind == "graph":
            executable_line_indexes = ExecutionTraceService._expand_graph_control_flow_indexes(
                operation_name=operation_name,
                lines=lines,
                executable_line_indexes=executable_line_indexes,
                before_state=before_state,
                after_state=after_state,
                success=bool(success),
                message=str(message),
                payload=payload,
            )

        if not executable_line_indexes and lines:
            executable_line_indexes = [0]
        step_lines = [lines[index] if 0 <= index < len(lines) else "" for index in executable_line_indexes]

        steps: list[dict[str, Any]] = []
        total_steps = len(executable_line_indexes)
        boundary_states = ExecutionTraceService._build_boundaries(
            structure_id=structure_id,
            before_state=before_state,
            after_state=after_state,
            total_steps=total_steps,
            mutates=bool(mutates and success),
            operation_name=operation_name,
            payload=payload,
            step_lines=step_lines,
        )
        if state_kind == "binary_tree":
            strategy = TraceStrategyRegistry.resolve(structure_id)
            if not isinstance(strategy, TreeTraceStrategy):
                raise TypeError(f"La estrategia de '{structure_id}' no es de Ã¡rbol.")
            debug_steps = strategy.build_debug_steps(
                operation_name=operation_name,
                payload=payload,
                before_state=before_state,
                after_state=after_state,
                success=bool(success),
                mutates=bool(mutates),
                total_steps=total_steps,
                step_lines=step_lines,
            )
        elif state_kind == "graph":
            debug_steps = ExecutionTraceService._build_graph_debug_steps(
                operation_name=operation_name,
                after_state=after_state,
                total_steps=total_steps,
            )
        else:
            debug_steps = [None for _ in range(total_steps)]
        linked_search_hits: list[int] = []
        if structure_id == "linked_list" and operation_name == "buscar_elemento":
            requested_value = str(payload.get("value"))
            for position, item in enumerate(before_state.get("items") or [], start=1):
                item_value = item.get("value") if isinstance(item, dict) else item
                if str(item_value) == requested_value:
                    linked_search_hits.append(position)
        linked_search_hit_cursor = 0
        for step_index, line_index in enumerate(executable_line_indexes):
            line_text = lines[line_index] if 0 <= line_index < len(lines) else ""
            is_first = step_index == 0
            is_last = step_index == total_steps - 1

            step: dict[str, Any] = {
                "step_index": step_index,
                "line_index": line_index,
                "line_text": line_text,
                "event_type": "line",
                "phase": (
                    "start"
                    if is_first and not is_last
                    else "end"
                    if is_last and not is_first
                    else "single"
                    if is_first and is_last
                    else "progress"
                ),
                "delay_ms": 170,
                "state_snapshot": deepcopy(boundary_states[step_index]),
                "state_after": deepcopy(boundary_states[step_index + 1]),
            }
            if not is_first:
                step.pop("phase", None)
                step["phase"] = "progress" if not is_last else "end"
            if step_index < len(debug_steps) and isinstance(debug_steps[step_index], dict):
                step["debug"] = debug_steps[step_index]
            literal_output = ExecutionTraceService._printf_literal(line_text)
            if (
                structure_id == "linked_list"
                and operation_name == "buscar_elemento"
                and "encontrado en la posicion %d" in line_text.lower()
                and linked_search_hit_cursor < len(linked_search_hits)
            ):
                step["console"] = [
                    f"\n Encontrado en la posicion {linked_search_hits[linked_search_hit_cursor]}"
                ]
                linked_search_hit_cursor += 1
            else:
                step["console"] = (
                    [literal_output]
                    if literal_output is not None
                    else list(console_events or []) if is_last else []
                )
            steps.append(step)

        if not steps:
            steps = [
                {
                    "step_index": 0,
                    "line_index": 0,
                    "line_text": "",
                    "event_type": "noop",
                    "phase": "single",
                    "delay_ms": 100,
                    "state_snapshot": deepcopy(before_state),
                    "state_after": deepcopy(after_state),
                }
            ]

        if structure_id in SEQUENTIAL_STRUCTURES:
            for index, step in enumerate(steps):
                pedagogical_step = dict(step)
                line_index = int(step.get("line_index", 0))
                current_function = operation_name
                for source_row in reversed(lines[: line_index + 1]):
                    function_match = re.search(r"\b([A-Za-z_]\w*)\s*\([^;]*\)\s*\{\s*$", source_row)
                    if function_match and function_match.group(1) not in {"if", "while", "for", "switch"}:
                        current_function = function_match.group(1)
                        break
                pedagogical_step["function_name"] = current_function
                line_text = str(step.get("line_text") or "").lstrip()
                if line_text.startswith(("if ", "if(", "while ", "while(", "} while ", "} while(")):
                    next_index = steps[index + 1].get("line_index") if index + 1 < len(steps) else None
                    if line_text.startswith("} while"):
                        next_line_text = str(steps[index + 1].get("line_text") or "").strip() if index + 1 < len(steps) else ""
                        pedagogical_step["condition_result"] = next_line_text == "do {"
                    else:
                        expected_body = ExecutionTraceService._next_nonempty_line_index(lines, line_index + 1)
                        pedagogical_step["condition_result"] = next_index == expected_body
                pedagogical = build_sequential_frame(
                    structure_id=structure_id,
                    operation_name=operation_name,
                    payload=payload,
                    step=pedagogical_step,
                    success=bool(success),
                )
                validate_sequential_frame(pedagogical, source_code=source_code)
                step["pedagogy"] = pedagogical

        if structure_id in HIERARCHICAL_STRUCTURES:
            for index, step in enumerate(steps):
                pedagogical_step = dict(step)
                line_index = int(step.get("line_index", 0))
                line_text = str(step.get("line_text") or "").lstrip()
                if line_text.startswith(("if ", "if(", "while ", "while(")):
                    next_index = steps[index + 1].get("line_index") if index + 1 < len(steps) else None
                    expected_body = ExecutionTraceService._next_nonempty_line_index(lines, line_index + 1)
                    pedagogical_step["condition_result"] = next_index == expected_body
                frame = build_hierarchical_frame(
                    structure_id=structure_id,
                    operation_name=operation_name,
                    payload=payload,
                    step=pedagogical_step,
                    source_lines=lines,
                    success=bool(success),
                )
                validate_hierarchical_frame(frame, source_code=source_code)
                step["pedagogy"] = frame

        if structure_id == "graph":
            for index, step in enumerate(steps):
                pedagogical_step = dict(step)
                line_index = int(step.get("line_index", 0))
                line_text = str(step.get("line_text") or "").lstrip()
                if line_text.startswith(("if ", "if(", "while ", "while(", "for ", "for(")):
                    next_index = steps[index + 1].get("line_index") if index + 1 < len(steps) else None
                    expected_body = ExecutionTraceService._next_nonempty_line_index(lines, line_index + 1)
                    pedagogical_step["condition_result"] = next_index == expected_body
                frame = build_graph_frame(operation_name=operation_name,payload=payload,step=pedagogical_step,source_lines=lines,success=bool(success))
                validate_graph_frame(frame,source_code=source_code)
                step["pedagogy"] = frame

        if structure_id == "hash_table":
            hash_visit_index = 0
            hash_initial_state = deepcopy(steps[0].get("state_snapshot", before_state))
            lifecycle_keys = [
                int(entry.get("key"))
                for bucket in hash_initial_state.get("buckets", [])
                if isinstance(bucket, dict)
                for entry in bucket.get("entries", [])
                if isinstance(entry, dict)
            ]
            lifecycle_free_index = 0
            for index, step in enumerate(steps):
                pedagogical_step = dict(step)
                pedagogical_step["hash_initial_state"] = hash_initial_state
                line_index = int(step.get("line_index", 0))
                line_text = str(step.get("line_text") or "").lstrip()
                if line_text.startswith(("if ", "if(", "while ", "while(", "for ", "for(")):
                    next_index = steps[index + 1].get("line_index") if index + 1 < len(steps) else None
                    expected_body = ExecutionTraceService._next_nonempty_line_index(lines, line_index + 1)
                    pedagogical_step["condition_result"] = next_index == expected_body
                if "actual->clave == clave" in line_text or "actual = actual->siguiente" in line_text or "while (actual != NULL)" in line_text:
                    pedagogical_step["hash_visit_index"] = hash_visit_index
                if "actual = actual->siguiente" in line_text:
                    hash_visit_index += 1
                if "free(actual)" in line_text and operation_name in {"clear", "destroy_table"} and lifecycle_free_index < len(lifecycle_keys):
                    pedagogical_step["hash_lifecycle_free_key"] = lifecycle_keys[lifecycle_free_index]
                    lifecycle_free_index += 1
                frame = build_hash_frame(operation_name=operation_name, payload=payload, step=pedagogical_step, source_lines=lines, success=bool(success))
                validate_hash_frame(frame, source_code=source_code)
                step["pedagogy"] = frame

        trace = {
            "structure_id": structure_id,
            "operation_name": operation_name,
            "payload": deepcopy(payload),
            "success": bool(success),
            "mutates": bool(mutates),
            "message": str(message),
            "code_title": code_title,
            "source_code": source_code,
            "steps": steps,
            "final_state": deepcopy(after_state),
        }
        if structure_id in SEQUENTIAL_STRUCTURES:
            trace["pedagogy_schema_version"] = SEQUENTIAL_FRAME_SCHEMA_VERSION
            trace["pedagogy_schema"] = sequential_frame_schema()
            trace["learning_profile"] = deepcopy(SEQUENTIAL_LEARNING_CATALOG[structure_id])
        if structure_id in HIERARCHICAL_STRUCTURES:
            trace["pedagogy_schema_version"] = HIERARCHICAL_FRAME_SCHEMA_VERSION
            trace["pedagogy_schema"] = hierarchical_frame_schema()
            trace["learning_profile"] = deepcopy(HIERARCHICAL_LEARNING_CATALOG[structure_id])
        if structure_id == "graph":
            trace["pedagogy_schema_version"] = GRAPH_FRAME_SCHEMA_VERSION
            trace["pedagogy_schema"] = graph_frame_schema()
            trace["learning_profile"] = deepcopy(GRAPH_LEARNING_CATALOG.get(operation_name,GRAPH_LEARNING_CATALOG["construction"]))
        if structure_id == "hash_table":
            trace["pedagogy_schema_version"] = HASH_FRAME_SCHEMA_VERSION
            trace["pedagogy_schema"] = hash_frame_schema()
            trace["learning_profile"] = deepcopy(HASH_LEARNING_CATALOG)
        if structure_id == "graph" and operation_name == "run_bfs":
            from app.domain.graph.bfs_instruction import build_bfs_trace, build_bfs_rejection_trace
            trace = (build_bfs_trace if success else build_bfs_rejection_trace)(trace, before_state, after_state)
        if structure_id == "graph" and operation_name == "run_dfs":
            from app.domain.graph.dfs_instruction import build_dfs_trace, build_dfs_rejection_trace
            trace = (build_dfs_trace if success else build_dfs_rejection_trace)(trace, before_state, after_state)
        if structure_id == "abb" and operation_name == "insertar" and success:
            from app.domain.hierarchical.abb_instruction import build_abb_insert_trace
            trace = build_abb_insert_trace(trace, before_state, after_state)
        if structure_id == "abb" and operation_name in {"inorden", "preorden", "postorden"} and success:
            from app.domain.hierarchical.abb_traversal_instruction import build_abb_traversal_trace
            trace = build_abb_traversal_trace(trace, before_state, after_state)
        if structure_id == "abb" and operation_name in {"minimo", "maximo"} and (success or message == "El arbol esta vacio."):
            from app.domain.hierarchical.abb_extreme_instruction import build_abb_extreme_trace
            trace = build_abb_extreme_trace(trace, before_state, after_state)
        if structure_id == "abb" and operation_name == "buscar" and success:
            from app.domain.hierarchical.abb_search_instruction import build_abb_search_trace
            trace = build_abb_search_trace(trace, before_state, after_state)
        if structure_id == 'abb' and operation_name == 'altura' and success:
            from app.domain.hierarchical.abb_height_instruction import build_abb_height_trace
            trace = build_abb_height_trace(trace, before_state, after_state)
        if structure_id == 'abb' and operation_name == 'contar_hojas' and success:
            from app.domain.hierarchical.abb_leaves_instruction import build_abb_leaves_trace
            trace = build_abb_leaves_trace(trace, before_state, after_state)
        if structure_id == 'abb' and operation_name == 'limpiar' and success:
            from app.domain.hierarchical.abb_clear_instruction import build_abb_clear_trace
            trace = build_abb_clear_trace(trace, before_state, after_state)
        if structure_id == 'abb' and operation_name == 'eliminar' and success:
            from app.domain.hierarchical.abb_delete_instruction import build_abb_delete_trace
            trace = build_abb_delete_trace(trace, before_state, after_state)
        if structure_id == 'red_black' and operation_name == 'insertar':
            from app.domain.hierarchical.rbt_insert_instruction import build_rbt_insert_trace,build_rbt_insert_rejection_trace
            trace = (build_rbt_insert_trace if success else build_rbt_insert_rejection_trace)(trace, before_state, after_state)
        if structure_id == 'red_black' and operation_name == 'eliminar' and success:
            from app.domain.hierarchical.rbt_delete_instruction import build_rbt_delete_trace
            trace = build_rbt_delete_trace(trace, before_state, after_state)
        if structure_id == 'red_black' and operation_name == 'eliminar' and not success:
            from app.domain.hierarchical.rbt_delete_rejection import build_rbt_delete_rejection_trace
            trace = build_rbt_delete_rejection_trace(trace, before_state, after_state)
        if structure_id == 'red_black' and operation_name == 'limpiar' and success:
            from app.domain.hierarchical.rbt_clear_instruction import build_rbt_clear_trace
            trace = build_rbt_clear_trace(trace, before_state, after_state)
        if structure_id == 'avl' and operation_name == 'limpiar' and success:
            from app.domain.hierarchical.avl_clear_instruction import build_avl_clear_trace
            trace = build_avl_clear_trace(trace, before_state, after_state)
        if structure_id == 'avl' and operation_name in {'minimo', 'maximo'} and (success or message == 'El arbol esta vacio.'):
            from app.domain.hierarchical.avl_extreme_instruction import build_avl_extreme_trace
            trace = build_avl_extreme_trace(trace, before_state, after_state)
        if structure_id == 'avl' and operation_name == 'inorden' and success:
            from app.domain.hierarchical.avl_inorden_instruction import build_avl_inorden_trace
            trace = build_avl_inorden_trace(trace, before_state, after_state)
        if structure_id == 'avl' and operation_name == 'buscar' and success:
            from app.domain.hierarchical.avl_search_instruction import build_avl_search_trace
            trace = build_avl_search_trace(trace, before_state, after_state)
        if structure_id == 'avl' and operation_name == 'altura' and success:
            from app.domain.hierarchical.avl_height_instruction import build_avl_height_trace
            trace = build_avl_height_trace(trace, before_state, after_state)
        if structure_id == 'binary_heap' and operation_name in {'raiz', 'a_lista'}:
            from app.domain.hierarchical.heap_query_instruction import build_heap_query_trace
            trace = build_heap_query_trace(trace, before_state, after_state)
        if structure_id == 'binary_heap' and operation_name == 'limpiar' and success:
            from app.domain.hierarchical.heap_clear_instruction import build_heap_clear_trace
            trace = build_heap_clear_trace(trace, before_state, after_state)
        if structure_id == 'binary_heap' and operation_name == 'insertar':
            from app.domain.hierarchical.heap_insert_instruction import build_heap_insert_trace, INSERT_RESERVE_ERROR
            if success or message == INSERT_RESERVE_ERROR:
                trace = build_heap_insert_trace(trace, before_state, after_state)
        if structure_id == 'binary_heap' and operation_name == 'extraer_raiz':
            from app.domain.hierarchical.heap_extract_instruction import build_heap_extract_trace
            trace = build_heap_extract_trace(trace, before_state, after_state)
        if structure_id == 'abb' and operation_name == 'validar' and success:
            from app.domain.hierarchical.abb_validate_instruction import build_abb_validate_trace
            trace = build_abb_validate_trace(trace, before_state, after_state)
        if structure_id == 'avl' and operation_name == 'validar' and success:
            from app.domain.hierarchical.avl_validate_instruction import build_avl_validate_trace
            trace = build_avl_validate_trace(trace, before_state, after_state)
        if structure_id == 'avl' and operation_name == 'insertar' and success:
            from app.domain.hierarchical.avl_insert_instruction import build_avl_insert_trace
            trace = build_avl_insert_trace(trace, before_state, after_state)
        if structure_id == 'avl' and operation_name == 'eliminar':
            from app.domain.hierarchical.avl_delete_instruction import build_avl_delete_trace,build_avl_delete_rejection_trace
            trace = (build_avl_delete_trace if success else build_avl_delete_rejection_trace)(trace, before_state, after_state)
        if structure_id == 'red_black' and operation_name in {'buscar', 'inorden', 'altura', 'validar'} and success:
            from app.domain.hierarchical.rbt_query_instruction import build_rbt_query_trace
            trace = build_rbt_query_trace(trace, before_state, after_state, native_projection=didactic_data.get("_rn_validation_projection") if operation_name == "validar" else None)
        if structure_id == "graph":
            # Semantic views are discarded after synchronous, read-only checks.
            TraceEngine.validate_legacy_trace(trace, copy_value=lambda value: value)
        else:
            TraceEngine.validate_legacy_trace(trace)
        return trace
