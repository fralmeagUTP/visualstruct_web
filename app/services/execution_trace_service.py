"""Build interpreter-like execution traces for didactic operation playback."""

from __future__ import annotations

from copy import deepcopy
from difflib import SequenceMatcher
import json
from typing import Any


class ExecutionTraceService:
    """Create a normalized execution trace from didactic operation code."""

    @staticmethod
    def _is_executable_line(line: str, code_title: str) -> bool:
        text = str(line).strip()
        if not text:
            return False
        if text.startswith("//") or text.startswith("/*") or text.startswith("*/"):
            return False
        # Solo ignorar lineas de continuacion de comentario bloque: "* comentario".
        if text == "*" or (text.startswith("*") and len(text) > 1 and text[1].isspace()):
            return False
        if text in {"{", "}"}:
            return False
        if "codigo c" in str(code_title).lower() and text.startswith("#"):
            return False
        return True

    @staticmethod
    def _next_nonempty_line_index(lines: list[str], from_index: int) -> int:
        for index in range(from_index, len(lines)):
            if str(lines[index]).strip():
                return index
        return -1

    @staticmethod
    def _find_matching_brace_line(lines: list[str], open_line_index: int) -> int:
        depth = 0
        for line_index in range(open_line_index, len(lines)):
            line = str(lines[line_index])
            for char in line:
                if char == "{":
                    depth += 1
                elif char == "}":
                    depth -= 1
                    if depth == 0:
                        return line_index
        return -1

    @staticmethod
    def _is_defensive_null_if(line_text: str) -> bool:
        text = str(line_text).strip().lower()
        if not text.startswith("if"):
            return False
        return "== null" in text or "==nullptr" in text

    @staticmethod
    def _is_defensive_early_exit_line(line_text: str) -> bool:
        text = str(line_text).strip().lower()
        if not text:
            return False
        return (
            text.startswith("return")
            or text.startswith("break")
            or text.startswith("continue")
        )

    @staticmethod
    def _message_matches_defensive_block(message: str, block_text: str) -> bool:
        msg = str(message or "").lower()
        block = str(block_text or "").lower()
        if not msg or not block:
            return False
        if "no inicializada" in msg and "no inicializada" in block:
            return True
        if ("no se pudo" in msg or "asignar memoria" in msg) and ("no se pudo" in block or "asignar memoria" in block):
            return True
        if ("vacia" in msg or "vacía" in msg) and ("vacia" in block or "vacía" in block):
            return True
        return False

    @staticmethod
    def _filter_trace_lines_by_control_flow(
        lines: list[str],
        executable_indexes: list[int],
        success: bool,
        message: str,
        state_kind: str | None = None,
    ) -> list[int]:
        if not executable_indexes:
            return executable_indexes
        if str(state_kind or "").strip().lower() in {"binary_tree", "heap"}:
            return list(executable_indexes)

        ordered = list(executable_indexes)
        blocks: list[dict[str, Any]] = []

        for line_index in ordered:
            line_text = str(lines[line_index]).strip()
            if not ExecutionTraceService._is_defensive_null_if(line_text):
                continue

            open_line_index = (
                line_index
                if "{" in line_text
                else ExecutionTraceService._next_nonempty_line_index(lines, line_index + 1)
            )
            if open_line_index < 0:
                continue
            close_line_index = ExecutionTraceService._find_matching_brace_line(lines, open_line_index)
            if close_line_index < 0:
                continue

            inner_indexes = [idx for idx in ordered if open_line_index < idx <= close_line_index]
            early_exit_indexes = [
                idx
                for idx in inner_indexes
                if ExecutionTraceService._is_defensive_early_exit_line(lines[idx])
            ]
            if not early_exit_indexes:
                continue

            block_text = "\n".join(str(lines[idx]) for idx in [line_index, *inner_indexes])
            blocks.append(
                {
                    "start": line_index,
                    "close": close_line_index,
                    "inner": inner_indexes,
                    "early_exit": early_exit_indexes,
                    "text": block_text,
                }
            )

        if not blocks:
            return ordered

        if success:
            skip = set()
            for block in blocks:
                skip.update(block["inner"])
            filtered = [idx for idx in ordered if idx not in skip]
            return filtered if filtered else ordered

        taken_block = next(
            (
                block
                for block in blocks
                if ExecutionTraceService._message_matches_defensive_block(message, block["text"])
            ),
            None,
        )
        if taken_block is None:
            return ordered

        result: list[int] = []
        skip_inner = set()
        for block in blocks:
            if block is not taken_block:
                skip_inner.update(block["inner"])

        for idx in ordered:
            if idx in skip_inner:
                continue
            result.append(idx)
            if idx == taken_block["start"]:
                for inner_idx in taken_block["inner"]:
                    if inner_idx in skip_inner:
                        continue
                    result.append(inner_idx)
                    if inner_idx in taken_block["early_exit"]:
                        return result
        return result if result else ordered

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

    @staticmethod
    def _coerce_number(value: Any) -> float | int | None:
        if isinstance(value, (int, float)):
            return value
        if value is None:
            return None
        text = str(value).strip()
        if not text:
            return None
        try:
            number = float(text)
            if number.is_integer():
                return int(number)
            return number
        except ValueError:
            return None

    @staticmethod
    def _tree_path_keys_for_value(root: dict[str, Any] | None, target: Any) -> list[str]:
        coerced_target = ExecutionTraceService._coerce_number(target)
        if root is None or coerced_target is None:
            return []

        keys: list[str] = []
        current = root
        while isinstance(current, dict):
            value = current.get("value")
            keys.append(str(value))
            node_number = ExecutionTraceService._coerce_number(value)
            if node_number is None:
                break
            if coerced_target == node_number:
                break
            if coerced_target < node_number:
                current = current.get("left")
            else:
                current = current.get("right")
        return keys

    @staticmethod
    def _tree_path_keys_to_extreme(root: dict[str, Any] | None, side: str) -> list[str]:
        if not isinstance(root, dict):
            return []
        keys: list[str] = []
        current: dict[str, Any] | None = root
        normalized_side = "left" if str(side).lower() == "left" else "right"
        while isinstance(current, dict):
            keys.append(str(current.get("value")))
            current = ExecutionTraceService._tree_child(current, normalized_side)
        return keys

    @staticmethod
    def _find_tree_node_by_value(root: dict[str, Any] | None, target: Any) -> dict[str, Any] | None:
        coerced_target = ExecutionTraceService._coerce_number(target)
        if root is None or coerced_target is None:
            return None
        current = root
        while isinstance(current, dict):
            value = current.get("value")
            node_number = ExecutionTraceService._coerce_number(value)
            if node_number is None:
                return None
            if coerced_target == node_number:
                return current
            if coerced_target < node_number:
                current = current.get("left")
            else:
                current = current.get("right")
        return None

    @staticmethod
    def _collect_tree_values(root: dict[str, Any] | None) -> list[Any]:
        if root is None:
            return []
        values: list[Any] = []
        stack = [root]
        while stack:
            node = stack.pop()
            if not isinstance(node, dict):
                continue
            values.append(node.get("value"))
            right = node.get("right")
            left = node.get("left")
            if isinstance(right, dict):
                stack.append(right)
            if isinstance(left, dict):
                stack.append(left)
        return values

    @staticmethod
    def _maybe_avl_rotation_hint(path: list[str], target_value: Any) -> dict[str, Any] | None:
        if len(path) < 2:
            return None
        pivot_raw = path[-2]
        child_raw = path[-1]
        pivot_num = ExecutionTraceService._coerce_number(pivot_raw)
        child_num = ExecutionTraceService._coerce_number(child_raw)
        target_num = ExecutionTraceService._coerce_number(target_value)
        if pivot_num is None or child_num is None or target_num is None:
            return None

        first = "L" if target_num < pivot_num else "R"
        second = "L" if target_num < child_num else "R"
        rotation_type = f"{first}{second}"
        if rotation_type not in {"LL", "LR", "RL", "RR"}:
            return None

        return {
            "type": rotation_type,
            "pivot": str(pivot_raw),
            "child": str(child_raw),
            "inserted": str(target_num),
        }

    @staticmethod
    def _tree_parent_map(
        root: dict[str, Any] | None,
        parent_key: str | None = None,
        acc: dict[str, str | None] | None = None,
    ) -> dict[str, str | None]:
        out = acc if isinstance(acc, dict) else {}
        if not isinstance(root, dict):
            return out
        key = str(root.get("value"))
        out[key] = parent_key
        left = root.get("left")
        right = root.get("right")
        if isinstance(left, dict):
            ExecutionTraceService._tree_parent_map(left, key, out)
        if isinstance(right, dict):
            ExecutionTraceService._tree_parent_map(right, key, out)
        return out

    @staticmethod
    def _infer_real_avl_insert_rotation_hint(
        before_state: dict[str, Any],
        after_state: dict[str, Any],
        target_value: Any,
    ) -> dict[str, Any] | None:
        before_root = before_state.get("root")
        after_root = after_state.get("root")
        if not isinstance(before_root, dict) or not isinstance(after_root, dict):
            return None

        path = ExecutionTraceService._tree_path_keys_for_value(before_root, target_value)
        candidate = ExecutionTraceService._maybe_avl_rotation_hint(path, target_value)
        if not isinstance(candidate, dict):
            return None

        inserted_key = str(candidate.get("inserted", ""))
        before_parents = ExecutionTraceService._tree_parent_map(before_root)
        after_parents = ExecutionTraceService._tree_parent_map(after_root)
        shared = set(before_parents.keys()) & set(after_parents.keys())
        if inserted_key in shared:
            shared.remove(inserted_key)
        if not shared:
            return None

        rotated = any(before_parents.get(key) != after_parents.get(key) for key in shared)
        return candidate if rotated else None

    @staticmethod
    def _avl_rotation_message(rotation_hint: dict[str, Any] | None) -> str:
        if not isinstance(rotation_hint, dict):
            return ""
        rotation_type = str(rotation_hint.get("type", "")).upper()
        pivot = str(rotation_hint.get("pivot", "")).strip()
        child = str(rotation_hint.get("child", "")).strip()
        if rotation_type == "LL":
            return f"Rotacion AVL LL: rotacion a la derecha en {pivot}."
        if rotation_type == "RR":
            return f"Rotacion AVL RR: rotacion a la izquierda en {pivot}."
        if rotation_type == "LR":
            return f"Rotacion AVL LR: izquierda en {child} y luego derecha en {pivot}."
        if rotation_type == "RL":
            return f"Rotacion AVL RL: derecha en {child} y luego izquierda en {pivot}."
        return "Rotacion AVL detectada."

    @staticmethod
    def _minimal_tree_node_template(source_node: dict[str, Any] | None, fallback_value: Any) -> dict[str, Any]:
        if not isinstance(source_node, dict):
            return {"value": fallback_value, "left": None, "right": None}
        template = {"value": source_node.get("value", fallback_value), "left": None, "right": None}
        if "color" in source_node:
            template["color"] = source_node.get("color")
        if "height" in source_node:
            template["height"] = source_node.get("height")
        if "balance_factor" in source_node:
            template["balance_factor"] = source_node.get("balance_factor")
        return template

    @staticmethod
    def _bst_insert_visual(root: dict[str, Any] | None, value: Any, template_node: dict[str, Any]) -> dict[str, Any]:
        if root is None:
            return deepcopy(template_node)

        node_value = ExecutionTraceService._coerce_number(root.get("value"))
        target_value = ExecutionTraceService._coerce_number(value)
        if node_value is None or target_value is None:
            return deepcopy(root)
        if target_value < node_value:
            left = root.get("left")
            root["left"] = ExecutionTraceService._bst_insert_visual(left if isinstance(left, dict) else None, value, template_node)
        elif target_value > node_value:
            right = root.get("right")
            root["right"] = ExecutionTraceService._bst_insert_visual(right if isinstance(right, dict) else None, value, template_node)
        return root

    @staticmethod
    def _bst_extract_min_visual(root: dict[str, Any]) -> tuple[dict[str, Any] | None, dict[str, Any]]:
        left = root.get("left")
        if not isinstance(left, dict):
            return (root.get("right") if isinstance(root.get("right"), dict) else None, root)
        new_left, min_node = ExecutionTraceService._bst_extract_min_visual(left)
        root["left"] = new_left
        return root, min_node

    @staticmethod
    def _bst_delete_visual(root: dict[str, Any] | None, value: Any) -> dict[str, Any] | None:
        if root is None:
            return None
        node_value = ExecutionTraceService._coerce_number(root.get("value"))
        target_value = ExecutionTraceService._coerce_number(value)
        if node_value is None or target_value is None:
            return deepcopy(root)
        if target_value < node_value:
            left = root.get("left")
            root["left"] = ExecutionTraceService._bst_delete_visual(left if isinstance(left, dict) else None, value)
            return root
        if target_value > node_value:
            right = root.get("right")
            root["right"] = ExecutionTraceService._bst_delete_visual(right if isinstance(right, dict) else None, value)
            return root

        left = root.get("left") if isinstance(root.get("left"), dict) else None
        right = root.get("right") if isinstance(root.get("right"), dict) else None
        if left is None:
            return right
        if right is None:
            return left

        new_right, successor = ExecutionTraceService._bst_extract_min_visual(right)
        successor_copy = deepcopy(successor)
        successor_copy["left"] = left
        successor_copy["right"] = new_right
        return successor_copy

    @staticmethod
    def _heap_root_from_array(values: list[Any], index: int = 0) -> dict[str, Any] | None:
        if index >= len(values):
            return None
        return {
            "value": values[index],
            "left": ExecutionTraceService._heap_root_from_array(values, 2 * index + 1),
            "right": ExecutionTraceService._heap_root_from_array(values, 2 * index + 2),
        }

    @staticmethod
    def _build_list_transition_states(before_items: list[Any], after_items: list[Any]) -> list[list[Any]]:
        working = deepcopy(before_items)
        states: list[list[Any]] = [deepcopy(working)]
        before_tokens = [ExecutionTraceService._stable_token(item) for item in before_items]
        after_tokens = [ExecutionTraceService._stable_token(item) for item in after_items]
        matcher = SequenceMatcher(a=before_tokens, b=after_tokens, autojunk=False)
        offset = 0

        for tag, i1, i2, j1, j2 in matcher.get_opcodes():
            if tag in {"delete", "replace"}:
                remove_count = i2 - i1
                for _ in range(remove_count):
                    remove_at = i1 + offset
                    if 0 <= remove_at < len(working):
                        working.pop(remove_at)
                        states.append(deepcopy(working))
                offset -= remove_count

            if tag in {"insert", "replace"}:
                insert_chunk = after_items[j1:j2]
                for chunk_index, item in enumerate(insert_chunk):
                    insert_at = i1 + offset + chunk_index
                    working.insert(insert_at, deepcopy(item))
                    states.append(deepcopy(working))
                offset += len(insert_chunk)

        if not states or states[-1] != after_items:
            states.append(deepcopy(after_items))
        return states

    @staticmethod
    def _stable_token(value: Any) -> str:
        try:
            return json.dumps(value, ensure_ascii=False, sort_keys=True)
        except TypeError:
            return repr(value)

    @staticmethod
    def _sample_progressive_states(states: list[Any], total_frames: int) -> list[Any]:
        if total_frames <= 0:
            return []
        if not states:
            return [None for _ in range(total_frames)]
        if len(states) == 1:
            return [deepcopy(states[0]) for _ in range(total_frames)]

        sampled: list[Any] = []
        max_index = len(states) - 1
        frame_span = total_frames - 1 if total_frames > 1 else 1
        for frame_index in range(total_frames):
            if total_frames == 1:
                sampled_index = max_index
            else:
                sampled_index = round((max_index * frame_index) / frame_span)
            sampled.append(deepcopy(states[sampled_index]))
        return sampled

    @staticmethod
    def _line_is_assignment_mutation(line_text: str) -> bool:
        text = str(line_text or "").strip().lower()
        if not text:
            return False
        if text.startswith("if ") or text.startswith("if("):
            return False
        if text.startswith("return"):
            return False
        if text in {"{", "}"}:
            return False
        if "=" not in text:
            return False
        comparison_tokens = ("==", "!=", "<=", ">=")
        if any(token in text for token in comparison_tokens):
            return False
        return True

    @staticmethod
    def _mutation_anchor_index(step_lines: list[str], fallback_total_steps: int) -> int:
        for index, line_text in enumerate(step_lines):
            if ExecutionTraceService._line_is_assignment_mutation(line_text):
                return index
        if fallback_total_steps <= 0:
            return 0
        return max(0, fallback_total_steps - 1)

    @staticmethod
    def _tree_mutation_anchor_index(
        operation_name: str,
        step_lines: list[str],
        fallback_total_steps: int,
    ) -> int:
        normalized_lines = [ExecutionTraceService._normalized_line_text(line) for line in step_lines]
        joined = "\n".join(normalized_lines)
        op = str(operation_name or "").lower()

        high_priority_patterns: list[str] = []
        if op == "insertar":
            if "abb_insertar(" in joined:
                high_priority_patterns = [
                    "nuevo->valor = valor;",
                    "nodo->izquierdo = abb_insertar",
                    "nodo->derecho = abb_insertar",
                ]
            elif "void avl_insertar(" in joined:
                high_priority_patterns = [
                    "*raiz = nuevo;",
                    "if (x < padre->nro) padre->izq = nuevo;",
                    "else padre->der = nuevo;",
                    "padre->izq = nuevo;",
                    "padre->der = nuevo;",
                ]
            elif "void rbt_insertar(" in joined:
                high_priority_patterns = [
                    "*arbol = actual;",
                    "padre->izq = actual;",
                    "padre->der = actual;",
                ]
            else:
                high_priority_patterns = [
                    "*raiz = nuevo;",
                    "nodo->izq = ",
                    "nodo->der = ",
                ]
        elif op in {"eliminar", "desapilar", "desencolar"}:
            high_priority_patterns = [
                "free(",
                "return temp;",
                "nodo->valor = temp->valor;",
                "nodo->derecho = abb_eliminar",
            ]

        for pattern in high_priority_patterns:
            pattern_norm = ExecutionTraceService._normalized_line_text(pattern)
            for index, line in enumerate(normalized_lines):
                if pattern_norm and pattern_norm in line:
                    return index

        return ExecutionTraceService._mutation_anchor_index(step_lines, fallback_total_steps)

    @staticmethod
    def _align_progressive_states_with_anchor(
        progressive_states: list[Any],
        boundaries: int,
        anchor_step_index: int,
    ) -> list[Any]:
        if boundaries <= 0:
            return []
        if not progressive_states:
            return [None for _ in range(boundaries)]

        if boundaries == 1:
            return [deepcopy(progressive_states[-1])]

        start_state = deepcopy(progressive_states[0])
        end_state = deepcopy(progressive_states[-1])
        max_state_index = len(progressive_states) - 1
        start_boundary = max(1, min(boundaries - 1, anchor_step_index + 1))

        result: list[Any] = []
        for boundary_index in range(boundaries):
            if boundary_index < start_boundary:
                result.append(deepcopy(start_state))
                continue

            remaining_boundaries = boundaries - start_boundary
            if remaining_boundaries <= 1:
                result.append(deepcopy(end_state))
                continue
            offset = boundary_index - start_boundary
            sampled_index = round((max_state_index * offset) / (remaining_boundaries - 1))
            sampled_index = max(0, min(max_state_index, sampled_index))
            result.append(deepcopy(progressive_states[sampled_index]))

        result[0] = deepcopy(start_state)
        result[-1] = deepcopy(end_state)
        return result

    @staticmethod
    def _build_linear_boundaries(
        before_state: dict[str, Any],
        after_state: dict[str, Any],
        total_steps: int,
        step_lines: list[str],
    ) -> list[dict[str, Any]]:
        boundaries = total_steps + 1
        before_items = list(before_state.get("items") or [])
        after_items = list(after_state.get("items") or [])
        progressive_lists_raw = ExecutionTraceService._sample_progressive_states(
            ExecutionTraceService._build_list_transition_states(before_items, after_items),
            boundaries,
        )
        anchor = ExecutionTraceService._mutation_anchor_index(step_lines, total_steps)
        progressive_lists = ExecutionTraceService._align_progressive_states_with_anchor(
            progressive_lists_raw,
            boundaries,
            anchor,
        )

        result: list[dict[str, Any]] = []
        for items in progressive_lists:
            current = deepcopy(before_state)
            current["items"] = items if isinstance(items, list) else []
            current["size"] = len(current["items"])
            current["empty"] = len(current["items"]) == 0
            current["title"] = after_state.get("title", current.get("title"))
            current["kind"] = after_state.get("kind", current.get("kind"))
            result.append(current)

        result[0] = deepcopy(before_state)
        result[-1] = deepcopy(after_state)
        return result

    @staticmethod
    def _build_heap_boundaries(
        before_state: dict[str, Any],
        after_state: dict[str, Any],
        total_steps: int,
        step_lines: list[str],
    ) -> list[dict[str, Any]]:
        boundaries = total_steps + 1
        before_array = list(before_state.get("array") or [])
        after_array = list(after_state.get("array") or [])
        progressive_arrays_raw = ExecutionTraceService._sample_progressive_states(
            ExecutionTraceService._build_list_transition_states(before_array, after_array),
            boundaries,
        )
        anchor = ExecutionTraceService._mutation_anchor_index(step_lines, total_steps)
        progressive_arrays = ExecutionTraceService._align_progressive_states_with_anchor(
            progressive_arrays_raw,
            boundaries,
            anchor,
        )

        result: list[dict[str, Any]] = []
        for array in progressive_arrays:
            array_values = array if isinstance(array, list) else []
            current = deepcopy(before_state)
            current["array"] = array_values
            current["root"] = ExecutionTraceService._heap_root_from_array(array_values, 0)
            current["size"] = len(array_values)
            current["empty"] = len(array_values) == 0
            current["title"] = after_state.get("title", current.get("title"))
            current["kind"] = after_state.get("kind", current.get("kind"))
            result.append(current)

        result[0] = deepcopy(before_state)
        result[-1] = deepcopy(after_state)
        return result

    @staticmethod
    def _build_graph_boundaries(
        before_state: dict[str, Any],
        after_state: dict[str, Any],
        total_steps: int,
        step_lines: list[str],
    ) -> list[dict[str, Any]]:
        boundaries = total_steps + 1
        before_nodes = list(before_state.get("nodes") or [])
        after_nodes = list(after_state.get("nodes") or [])
        before_edges = list(before_state.get("edges") or [])
        after_edges = list(after_state.get("edges") or [])
        node_states_raw = ExecutionTraceService._sample_progressive_states(
            ExecutionTraceService._build_list_transition_states(before_nodes, after_nodes),
            boundaries,
        )
        edge_states_raw = ExecutionTraceService._sample_progressive_states(
            ExecutionTraceService._build_list_transition_states(before_edges, after_edges),
            boundaries,
        )
        anchor = ExecutionTraceService._mutation_anchor_index(step_lines, total_steps)
        node_states = ExecutionTraceService._align_progressive_states_with_anchor(
            node_states_raw,
            boundaries,
            anchor,
        )
        edge_states = ExecutionTraceService._align_progressive_states_with_anchor(
            edge_states_raw,
            boundaries,
            anchor,
        )

        result: list[dict[str, Any]] = []
        for index in range(boundaries):
            current = deepcopy(before_state)
            nodes = node_states[index] if isinstance(node_states[index], list) else []
            edges = edge_states[index] if isinstance(edge_states[index], list) else []
            current["nodes"] = nodes
            current["edges"] = edges
            directed = bool(after_state.get("directed", before_state.get("directed", False)))
            weighted = any(float(edge.get("weight", 1)) != 1.0 for edge in edges if isinstance(edge, dict))
            current["directed"] = directed
            current["weighted"] = weighted
            current["metadata"] = {
                "vertices_count": len(nodes),
                "edges_count": len(edges),
                "is_empty": len(nodes) == 0,
            }
            current["last_operation"] = deepcopy(after_state.get("last_operation", current.get("last_operation")))
            current["last_result"] = deepcopy(after_state.get("last_result", current.get("last_result")))
            result.append(current)

        result[0] = deepcopy(before_state)
        result[-1] = deepcopy(after_state)
        return result

    @staticmethod
    def _build_hash_boundaries(
        before_state: dict[str, Any],
        after_state: dict[str, Any],
        total_steps: int,
        step_lines: list[str],
    ) -> list[dict[str, Any]]:
        boundaries = total_steps + 1
        before_buckets = list(before_state.get("buckets") or [])
        after_buckets = list(after_state.get("buckets") or [])
        bucket_states_raw = ExecutionTraceService._sample_progressive_states(
            ExecutionTraceService._build_list_transition_states(before_buckets, after_buckets),
            boundaries,
        )
        anchor = ExecutionTraceService._mutation_anchor_index(step_lines, total_steps)
        bucket_states = ExecutionTraceService._align_progressive_states_with_anchor(
            bucket_states_raw,
            boundaries,
            anchor,
        )

        result: list[dict[str, Any]] = []
        for buckets in bucket_states:
            current_buckets = deepcopy(buckets if isinstance(buckets, list) else [])
            total_size = 0
            total_collisions = 0
            for bucket in current_buckets:
                if not isinstance(bucket, dict):
                    continue
                entries = list(bucket.get("entries") or [])
                bucket["entries"] = entries
                bucket["size"] = len(entries)
                bucket["collisions"] = max(0, len(entries) - 1)
                total_size += bucket["size"]
                total_collisions += bucket["collisions"]

            capacity = len(current_buckets) if current_buckets else int(after_state.get("metadata", {}).get("capacity", 0))
            load_factor = (float(total_size) / float(capacity)) if capacity > 0 else 0.0
            current = deepcopy(before_state)
            current["buckets"] = current_buckets
            current["metadata"] = {
                "size": total_size,
                "capacity": capacity,
                "load_factor": round(load_factor, 6),
                "collisions": total_collisions,
                "is_empty": total_size == 0,
                "resized": bool(after_state.get("metadata", {}).get("resized", False)),
                "resize_event": deepcopy(after_state.get("metadata", {}).get("resize_event")),
            }
            current["last_operation"] = deepcopy(after_state.get("last_operation", current.get("last_operation")))
            current["last_result"] = deepcopy(after_state.get("last_result", current.get("last_result")))
            current["title"] = after_state.get("title", current.get("title"))
            current["structure"] = after_state.get("structure", current.get("structure"))
            result.append(current)

        result[0] = deepcopy(before_state)
        result[-1] = deepcopy(after_state)
        return result

    @staticmethod
    def _build_tree_debug_boundaries(
        before_state: dict[str, Any],
        after_state: dict[str, Any],
        total_steps: int,
        operation_name: str,
        payload: dict[str, Any],
        step_lines: list[str],
    ) -> list[dict[str, Any]]:
        boundaries = total_steps + 1
        before_root = before_state.get("root")
        after_root = after_state.get("root")
        if not isinstance(before_root, dict) and before_root is not None:
            before_root = None
        if not isinstance(after_root, dict) and after_root is not None:
            after_root = None

        # En trazas recursivas de arbol usamos transicion discreta before->after
        # para respetar el paso exacto donde ocurre la mutacion en el codigo C.
        anchor = ExecutionTraceService._tree_mutation_anchor_index(
            operation_name=operation_name,
            step_lines=step_lines,
            fallback_total_steps=total_steps,
        )
        mutation_boundary = max(1, min(boundaries - 1, anchor + 1))

        # Caso AVL insertar con rotacion: exponer estado intermedio
        # (nodo insertado aun sin reequilibrar) y luego estado final rotado.
        family = ExecutionTraceService._tree_family(after_state if isinstance(after_state, dict) else before_state)
        if family == "avl" and str(operation_name or "").lower() == "insertar":
            target = ExecutionTraceService._coerce_number(payload.get("value"))
            before_root_dict = before_root if isinstance(before_root, dict) else None
            inserted_template = ExecutionTraceService._minimal_tree_node_template(
                ExecutionTraceService._find_tree_node_by_value(after_root if isinstance(after_root, dict) else None, target),
                target,
            )
            if target is not None:
                raw_mid_root = ExecutionTraceService._bst_insert_visual(
                    deepcopy(before_root_dict) if isinstance(before_root_dict, dict) else None,
                    target,
                    inserted_template,
                )
                if isinstance(raw_mid_root, dict):
                    rotation_step_index = -1
                    for index, line in enumerate(step_lines):
                        normalized = ExecutionTraceService._normalized_line_text(line)
                        if (
                            "avl_rsd(" in normalized
                            or "avl_rsi(" in normalized
                            or "avl_rdd(" in normalized
                            or "avl_rdi(" in normalized
                        ):
                            rotation_step_index = index
                            break
                    rotation_boundary = rotation_step_index + 1 if rotation_step_index >= 0 else -1
                    if rotation_boundary > mutation_boundary and rotation_boundary < boundaries:
                        mid_state = deepcopy(after_state)
                        mid_state["root"] = raw_mid_root
                        result_mid: list[dict[str, Any]] = []
                        for boundary_index in range(boundaries):
                            if boundary_index < mutation_boundary:
                                result_mid.append(deepcopy(before_state))
                            elif boundary_index < rotation_boundary:
                                result_mid.append(deepcopy(mid_state))
                            else:
                                result_mid.append(deepcopy(after_state))
                        result_mid[0] = deepcopy(before_state)
                        result_mid[-1] = deepcopy(after_state)
                        return result_mid

        # Caso Rojo-Negro insertar: estado intermedio luego de enlazar el nodo
        # y antes del fix-up (recoloreo/rotaciones).
        if family == "red_black" and str(operation_name or "").lower() == "insertar":
            target = ExecutionTraceService._coerce_number(payload.get("value"))
            before_root_dict = before_root if isinstance(before_root, dict) else None
            if target is not None:
                inserted_template = {"value": target, "color": "RED", "left": None, "right": None}
                raw_mid_root = ExecutionTraceService._bst_insert_visual(
                    deepcopy(before_root_dict) if isinstance(before_root_dict, dict) else None,
                    target,
                    inserted_template,
                )
                if isinstance(raw_mid_root, dict):
                    fixup_step_index = -1
                    for index, line in enumerate(step_lines):
                        normalized = ExecutionTraceService._normalized_line_text(line)
                        if "rbt_insercion_caso1(" in normalized:
                            fixup_step_index = index
                            break
                    fixup_boundary = fixup_step_index + 1 if fixup_step_index >= 0 else -1
                    if fixup_boundary > mutation_boundary and fixup_boundary < boundaries:
                        mid_state = deepcopy(after_state)
                        mid_state["root"] = raw_mid_root
                        result_mid: list[dict[str, Any]] = []
                        for boundary_index in range(boundaries):
                            if boundary_index < mutation_boundary:
                                result_mid.append(deepcopy(before_state))
                            elif boundary_index < fixup_boundary:
                                result_mid.append(deepcopy(mid_state))
                            else:
                                result_mid.append(deepcopy(after_state))
                        result_mid[0] = deepcopy(before_state)
                        result_mid[-1] = deepcopy(after_state)
                        return result_mid

        result: list[dict[str, Any]] = []
        for boundary_index in range(boundaries):
            if boundary_index < mutation_boundary:
                result.append(deepcopy(before_state))
            else:
                result.append(deepcopy(after_state))
        result[0] = deepcopy(before_state)
        result[-1] = deepcopy(after_state)
        return result

    @staticmethod
    def _build_tree_debug_steps(
        operation_name: str,
        payload: dict[str, Any],
        before_state: dict[str, Any],
        after_state: dict[str, Any],
        success: bool,
        mutates: bool,
        total_steps: int,
        step_lines: list[str],
    ) -> list[dict[str, Any] | None]:
        if total_steps <= 0:
            return []
        if operation_name not in {"insertar", "eliminar", "buscar", "minimo", "maximo"}:
            return [None for _ in range(total_steps)]

        family = ExecutionTraceService._tree_family(after_state)
        if operation_name in {"minimo", "maximo"}:
            root_for_path = before_state.get("root")
            if not isinstance(root_for_path, dict):
                root_for_path = after_state.get("root")
            side = "left" if operation_name == "minimo" else "right"
            path = ExecutionTraceService._tree_path_keys_to_extreme(
                root_for_path if isinstance(root_for_path, dict) else None,
                side,
            )
        else:
            path = ExecutionTraceService._tree_path_keys_for_value(before_state.get("root"), payload.get("value"))
        if not path:
            return [None for _ in range(total_steps)]

        rotation_hint = (
            ExecutionTraceService._infer_real_avl_insert_rotation_hint(
                before_state=before_state,
                after_state=after_state,
                target_value=payload.get("value"),
            )
            if family == "avl" and operation_name == "insertar" and success and mutates
            else None
        )
        pivot_key = path[-2] if len(path) >= 2 else path[-1]
        child_key = path[-1]

        debug_steps: list[dict[str, Any] | None] = []
        rebalance_op = operation_name in {"insertar", "eliminar"} and mutates and success and family in {"avl", "red_black"}
        search_steps_end = max(1, int(total_steps * 0.55))
        pre_fix_step = max(search_steps_end, min(total_steps - 2, search_steps_end))
        fix_step = max(pre_fix_step + 1, min(total_steps - 1, int(total_steps * 0.75)))
        denominator = max(1, total_steps - 1)
        for index in range(total_steps):
            path_index = round(((len(path) - 1) * index) / denominator)
            path_index = max(0, min(len(path) - 1, path_index))
            stage = "search"
            active_keys: list[str] = []
            note = ""
            normalized_line = (
                ExecutionTraceService._normalized_line_text(step_lines[index])
                if index < len(step_lines)
                else ""
            )

            if family == "avl" and operation_name in {"insertar", "eliminar"}:
                active_keys = [str(path[path_index])]
                if (
                    "while (padre != null)" in normalized_line
                    or "if (padre->fe ==" in normalized_line
                    or "if (n == padre->izq)" in normalized_line
                    or "padre->fe--;" in normalized_line
                    or "padre->fe++;" in normalized_line
                    or "if (n->fe <= 0)" in normalized_line
                    or "if (n->fe >= 0)" in normalized_line
                ):
                    stage = "pre_rebalance" if rotation_hint else "rebalance_scan"
                    active_keys = [str(pivot_key)]
                    if rotation_hint:
                        note = f"Nodo desbalanceado detectado en {pivot_key}."
                    else:
                        note = "Actualizando factor de equilibrio (FE)."
                if (
                    "avl_rsd(" in normalized_line
                    or "avl_rsi(" in normalized_line
                    or "avl_rdd(" in normalized_line
                    or "avl_rdi(" in normalized_line
                ):
                    stage = "rebalance"
                    active_keys = [str(pivot_key), str(child_key)]
                    rotation_note = ExecutionTraceService._avl_rotation_message(rotation_hint)
                    note = rotation_note or "Aplicando ajuste AVL."
                if (
                    "*raiz = nuevo;" in normalized_line
                    or "padre->izq = nuevo;" in normalized_line
                    or "padre->der = nuevo;" in normalized_line
                ):
                    stage = "apply"
                    active_keys = [str(path[-1])]
                    note = "Aplicando cambio final sobre el arbol."
                debug_payload: dict[str, Any] = {
                    "path_keys": deepcopy(path),
                    "path_index": path_index,
                    "stage": stage,
                }
                if active_keys:
                    debug_payload["active_keys"] = active_keys
                if note:
                    debug_payload["note"] = note
                if rotation_hint and stage in {"pre_rebalance", "rebalance", "post_rebalance"}:
                    debug_payload["rotation_hint"] = deepcopy(rotation_hint)
                    debug_payload["unbalanced_key"] = str(pivot_key)
                    rotation_message = ExecutionTraceService._avl_rotation_message(rotation_hint)
                    if rotation_message:
                        debug_payload["rotation_message"] = rotation_message
                debug_steps.append(debug_payload)
                continue

            if family == "red_black" and operation_name in {"insertar", "eliminar"}:
                active_keys = [str(path[path_index])]
                if "while (actual != null && dato != actual->nro)" in normalized_line:
                    stage = "search"
                    note = "Recorriendo el arbol para ubicar la posicion de insercion."
                elif (
                    "*arbol = actual;" in normalized_line
                    or "padre->izq = actual;" in normalized_line
                    or "padre->der = actual;" in normalized_line
                ):
                    stage = "apply"
                    active_keys = [str(path[-1])]
                    note = "Nodo enlazado al arbol (insercion BST)."
                elif "actual->rbt_color = rojo;" in normalized_line:
                    stage = "pre_fixup"
                    note = "Nodo nuevo nace rojo antes del ajuste RN."
                elif "rbt_insercion_caso1(" in normalized_line:
                    stage = "fixup"
                    active_keys = [str(path[-1])]
                    note = "Aplicando fix-up Rojo-Negro (recoloreos/rotaciones)."
                elif "printf(" in normalized_line:
                    stage = "post_fixup"
                    note = "Insercion Rojo-Negro completada."
                debug_payload = {
                    "path_keys": deepcopy(path),
                    "path_index": path_index,
                    "stage": stage,
                    "active_keys": active_keys,
                }
                if note:
                    debug_payload["note"] = note
                debug_steps.append(debug_payload)
                continue

            if operation_name in {"minimo", "maximo"}:
                debug_payload = {
                    "path_keys": deepcopy(path),
                    "path_index": path_index,
                    "stage": "search" if index < total_steps - 1 else "result",
                    "active_keys": [str(path[path_index])],
                    "note": (
                        "Descendiendo por izquierda para encontrar el minimo."
                        if operation_name == "minimo"
                        else "Descendiendo por derecha para encontrar el maximo."
                    ),
                }
                if index == total_steps - 1:
                    debug_payload["note"] = (
                        f"Minimo encontrado en {path[-1]}."
                        if operation_name == "minimo"
                        else f"Maximo encontrado en {path[-1]}."
                    )
                debug_steps.append(debug_payload)
                continue

            if rebalance_op and index >= pre_fix_step:
                if family == "avl":
                    if index < fix_step:
                        stage = "pre_rebalance"
                        active_keys = [str(pivot_key)]
                        note = "Nodo pivote detectado para reequilibrio AVL."
                    elif index == fix_step:
                        stage = "rebalance"
                        active_keys = [str(pivot_key), str(child_key)]
                        note = "Aplicando rotacion AVL."
                    else:
                        stage = "post_rebalance"
                        active_keys = [str(child_key)]
                        note = "Reequilibrio AVL aplicado."
                elif family == "red_black":
                    if index < fix_step:
                        stage = "pre_fixup"
                        active_keys = [str(pivot_key)]
                        note = "Preparando ajuste de colores/rotaciones RN."
                    elif index == fix_step:
                        stage = "fixup"
                        active_keys = [str(pivot_key), str(child_key)]
                        note = "Aplicando fix-up de Rojo-Negro."
                    else:
                        stage = "post_fixup"
                        active_keys = [str(child_key)]
                        note = "Fix-up Rojo-Negro completado."
            elif index == total_steps - 1 and operation_name in {"insertar", "eliminar"}:
                stage = "apply"
                active_keys = [str(path[-1])]
                note = "Aplicando cambio final sobre el arbol."

            debug_payload: dict[str, Any] = {
                "path_keys": deepcopy(path),
                "path_index": path_index,
                "stage": stage,
            }
            if active_keys:
                debug_payload["active_keys"] = active_keys
            if note:
                debug_payload["note"] = note
            if rotation_hint and stage in {"pre_rebalance", "rebalance", "post_rebalance"}:
                debug_payload["rotation_hint"] = deepcopy(rotation_hint)

            debug_steps.append(debug_payload)
        return debug_steps

    @staticmethod
    def _build_graph_debug_steps(
        operation_name: str,
        after_state: dict[str, Any],
        total_steps: int,
    ) -> list[dict[str, Any] | None]:
        if total_steps <= 0:
            return []

        result_wrapper = after_state.get("last_result") if isinstance(after_state, dict) else None
        result = result_wrapper.get("result") if isinstance(result_wrapper, dict) else None
        debug_steps: list[dict[str, Any] | None] = []
        edges_state = after_state.get("edges") if isinstance(after_state.get("edges"), list) else []

        def _sample_timeline(timeline: list[dict[str, Any]]) -> list[dict[str, Any] | None]:
            if total_steps <= 0:
                return []
            if not timeline:
                return [None for _ in range(total_steps)]
            if len(timeline) == 1:
                return [deepcopy(timeline[0]) for _ in range(total_steps)]
            if total_steps == 1:
                return [deepcopy(timeline[-1])]

            sampled: list[dict[str, Any]] = []
            max_index = len(timeline) - 1
            for index in range(total_steps):
                pick = round((max_index * index) / (total_steps - 1))
                pick = max(0, min(max_index, pick))
                sampled.append(deepcopy(timeline[pick]))
            return sampled

        def _prefix_count(length: int, index: int) -> int:
            if length <= 0:
                return 0
            return max(1, min(length, round((length * (index + 1)) / total_steps)))

        if operation_name == "run_bfs" and isinstance(result, list):
            path = [str(item) for item in result]
            adjacency = ExecutionTraceService._graph_adjacency_from_state(after_state)
            bfs_tree_edges = ExecutionTraceService._derive_bfs_tree_edges(path, adjacency)
            seen_nodes: set[str] = set()
            staged_nodes: list[str] = []
            staged_edges: list[list[str]] = []
            for index in range(total_steps):
                count = _prefix_count(len(path), index)
                prefix = path[:count]
                if prefix:
                    current = prefix[-1]
                    if current not in seen_nodes:
                        seen_nodes.add(current)
                        staged_nodes.append(current)
                    staged_edges = []
                    for edge in bfs_tree_edges:
                        if edge[1] in seen_nodes:
                            staged_edges.append([edge[0], edge[1]])
                else:
                    current = None
                stage = "init" if index == 0 else "visit" if index < total_steps - 1 else "complete"
                note = (
                    f"Visitando {current}."
                    if current is not None
                    else "Preparando recorrido."
                )
                debug_steps.append(
                    {
                        "stage": stage,
                        "note": note,
                        "graph_progress": {
                            "mode": "traversal",
                            "nodes": deepcopy(staged_nodes),
                            "edges": deepcopy(staged_edges),
                        },
                    }
                )
            return debug_steps

        if operation_name == "run_dfs" and isinstance(result, list):
            path = [str(item) for item in result]
            adjacency = ExecutionTraceService._graph_adjacency_from_state(after_state)
            dfs_tree_edges = ExecutionTraceService._derive_dfs_tree_edges(path, adjacency)
            seen_nodes: set[str] = set()
            staged_nodes: list[str] = []
            staged_edges: list[list[str]] = []

            for index in range(total_steps):
                count = _prefix_count(len(path), index)
                prefix = path[:count]
                if prefix:
                    current = prefix[-1]
                    if current not in seen_nodes:
                        seen_nodes.add(current)
                        staged_nodes.append(current)
                    staged_edges = []
                    for edge in dfs_tree_edges:
                        if edge[1] in seen_nodes:
                            staged_edges.append([edge[0], edge[1]])
                    stage = "init" if index == 0 else "visit" if index < total_steps - 1 else "complete"
                    note = (
                        f"Llamada DFS en {current}."
                        if stage != "complete"
                        else f"DFS completado. Ultimo retorno en {current}."
                    )
                else:
                    stage = "init"
                    note = "Preparando recorrido DFS."

                debug_steps.append(
                    {
                        "stage": stage,
                        "note": note,
                        "graph_progress": {
                            "mode": "traversal",
                            "nodes": deepcopy(staged_nodes),
                            "edges": deepcopy(staged_edges),
                        },
                    }
                )
            return debug_steps

        if operation_name in {"run_dijkstra", "run_bellman_ford"} and isinstance(result, dict):
            path = [str(item) for item in (result.get("path") or [])]
            origin = str(result.get("start")) if result.get("start") is not None else ""
            destination = str(result.get("end")) if result.get("end") is not None else ""
            reachable = bool(result.get("reachable", False))
            has_negative_cycle = bool(result.get("has_negative_cycle", False))

            if operation_name == "run_bellman_ford" and has_negative_cycle:
                timeline: list[dict[str, Any]] = []
                timeline.append(
                    {
                        "stage": "init",
                        "note": f"Iniciando Bellman-Ford desde {origin}.",
                        "graph_progress": {"mode": "shortest", "nodes": [origin] if origin else [], "edges": []},
                    }
                )
                sample_edges = []
                for edge in edges_state:
                    if not isinstance(edge, dict):
                        continue
                    source = str(edge.get("source"))
                    target = str(edge.get("target"))
                    sample_edges.append([source, target])
                    if len(sample_edges) >= 4:
                        break
                if not sample_edges:
                    sample_edges = [[origin, destination]] if origin and destination else []
                for pass_index, edge in enumerate(sample_edges, start=1):
                    timeline.append(
                        {
                            "stage": "relax_edge",
                            "note": f"Pasada {pass_index}: relajando {edge[0]} -> {edge[1]}.",
                            "graph_progress": {
                                "mode": "shortest",
                                "nodes": [edge[0], edge[1]],
                                "edges": [edge],
                            },
                        }
                    )
                timeline.append(
                    {
                        "stage": "detect_negative_cycle",
                        "note": "Se detecto ciclo negativo: aun hay relajacion tras |V|-1 pasadas.",
                        "graph_progress": {"mode": "shortest", "nodes": [], "edges": sample_edges},
                    }
                )
                timeline.append(
                    {
                        "stage": "complete",
                        "note": "Bellman-Ford finalizo con ciclo negativo.",
                        "graph_progress": {"mode": "shortest", "nodes": [], "edges": sample_edges},
                    }
                )
                return _sample_timeline(timeline)

            if not path or not reachable:
                timeline = [
                    {
                        "stage": "init",
                        "note": f"Iniciando desde {origin} y buscando ruta a {destination}.",
                    },
                    {
                        "stage": "detect_unreachable",
                        "note": "No existe ruta entre inicio y destino.",
                    },
                    {
                        "stage": "complete",
                        "note": "Ejecucion finalizada sin ruta alcanzable.",
                    },
                ]
                return _sample_timeline(timeline)

            timeline = [
                {
                    "stage": "init",
                    "note": f"Iniciando en {path[0]}.",
                    "graph_progress": {"mode": "shortest", "nodes": [path[0]], "edges": []},
                }
            ]
            for i in range(1, len(path)):
                from_node = path[i - 1]
                to_node = path[i]
                prefix_nodes = path[: i + 1]
                prefix_edges = [[path[j - 1], path[j]] for j in range(1, i + 1)]
                timeline.append(
                    {
                        "stage": "extract_min",
                        "note": f"Extrayendo nodo candidato {from_node} de la cola de prioridad.",
                        "graph_progress": {
                            "mode": "shortest",
                            "nodes": path[:i],
                            "edges": [[path[j - 1], path[j]] for j in range(1, i)],
                        },
                    }
                )
                timeline.append(
                    {
                        "stage": "relax_edge",
                        "note": f"Relajando arista {from_node} -> {to_node}.",
                        "graph_progress": {
                            "mode": "shortest",
                            "nodes": prefix_nodes,
                            "edges": prefix_edges,
                        },
                    }
                )
                timeline.append(
                    {
                        "stage": "update_distance",
                        "note": f"Actualizando distancia tentativa de {to_node}.",
                        "graph_progress": {
                            "mode": "shortest",
                            "nodes": prefix_nodes,
                            "edges": prefix_edges,
                        },
                    }
                )
            timeline.append(
                {
                    "stage": "complete",
                    "note": f"Ruta minima consolidada hacia {path[-1]}.",
                    "graph_progress": {
                        "mode": "shortest",
                        "nodes": path,
                        "edges": [[path[j - 1], path[j]] for j in range(1, len(path))],
                    },
                }
            )
            return _sample_timeline(timeline)

        if operation_name in {"run_prim", "run_kruskal"} and isinstance(result, dict):
            mst_edges_raw = result.get("mst_edges")
            if not isinstance(mst_edges_raw, list):
                return [None for _ in range(total_steps)]
            mst_edges = [
                [str(edge[0]), str(edge[1])]
                for edge in mst_edges_raw
                if isinstance(edge, (list, tuple)) and len(edge) >= 2
            ]
            for index in range(total_steps):
                count = _prefix_count(len(mst_edges), index)
                edges = mst_edges[:count]
                nodes_set = set()
                for edge in edges:
                    nodes_set.add(edge[0])
                    nodes_set.add(edge[1])
                nodes = sorted(nodes_set, key=lambda item: item)
                stage = "init" if index == 0 else "expand_mst" if index < total_steps - 1 else "complete"
                if edges:
                    last_edge = edges[-1]
                    note = f"Agregando arista MST {last_edge[0]} - {last_edge[1]}."
                else:
                    note = "Preparando arbol de expansion minima."
                debug_steps.append(
                    {
                        "stage": stage,
                        "note": note,
                        "graph_progress": {
                            "mode": "mst",
                            "nodes": nodes,
                            "edges": edges,
                        },
                    }
                )
            return debug_steps

        for index in range(total_steps):
            stage = "execute" if index < total_steps - 1 else "complete"
            debug_steps.append({"stage": stage, "note": "Ejecutando paso del algoritmo."})
        return debug_steps

    @staticmethod
    def _normalized_line_text(line_text: str) -> str:
        return " ".join(str(line_text or "").strip().lower().split())

    @staticmethod
    def _graph_out_degree_map(after_state: dict[str, Any]) -> dict[str, int]:
        edges = after_state.get("edges")
        if not isinstance(edges, list):
            return {}
        directed = bool(after_state.get("directed", False))
        degree_map: dict[str, int] = {}
        for edge in edges:
            if not isinstance(edge, dict):
                continue
            source = str(edge.get("source"))
            target = str(edge.get("target"))
            degree_map[source] = degree_map.get(source, 0) + 1
            if not directed:
                degree_map[target] = degree_map.get(target, 0) + 1
        return degree_map

    @staticmethod
    def _graph_adjacency_from_state(state: dict[str, Any]) -> dict[str, list[str]]:
        adjacency: dict[str, list[str]] = {}
        nodes = state.get("nodes")
        if isinstance(nodes, list):
            for node in nodes:
                if isinstance(node, dict):
                    node_id = str(node.get("id", ""))
                    if node_id:
                        adjacency.setdefault(node_id, [])

        directed = bool(state.get("directed", False))
        edges = state.get("edges")
        if not isinstance(edges, list):
            return adjacency

        def _append_unique(src: str, dst: str) -> None:
            lst = adjacency.setdefault(src, [])
            if dst not in lst:
                lst.append(dst)

        for edge in edges:
            if not isinstance(edge, dict):
                continue
            src = str(edge.get("source", ""))
            dst = str(edge.get("target", ""))
            if not src or not dst:
                continue
            _append_unique(src, dst)
            if not directed:
                _append_unique(dst, src)
        return adjacency

    @staticmethod
    def _derive_dfs_tree_edges(path: list[str], adjacency: dict[str, list[str]]) -> list[list[str]]:
        if not path:
            return []

        children: dict[str, list[str]] = {}
        stack: list[str] = [path[0]]
        visited: set[str] = {path[0]}

        for node in path[1:]:
            parent: str | None = None
            while stack:
                candidate = stack[-1]
                if node in adjacency.get(candidate, []):
                    parent = candidate
                    break
                stack.pop()
            if parent is None:
                for candidate in reversed(path[: max(1, len(visited))]):
                    if node in adjacency.get(candidate, []):
                        parent = candidate
                        break
            if parent is not None:
                children.setdefault(parent, []).append(node)
            stack.append(node)
            visited.add(node)

        ordered_edges: list[list[str]] = []

        def walk(current: str) -> None:
            for child in children.get(current, []):
                ordered_edges.append([current, child])
                walk(child)

        walk(path[0])
        return ordered_edges

    @staticmethod
    def _derive_bfs_tree_edges(path: list[str], adjacency: dict[str, list[str]]) -> list[list[str]]:
        if not path:
            return []

        root = path[0]
        order_index = {node: idx for idx, node in enumerate(path)}
        distance: dict[str, int] = {root: 0}
        queue: list[str] = [root]

        while queue:
            current = queue.pop(0)
            for neighbor in adjacency.get(current, []):
                if neighbor in distance:
                    continue
                distance[neighbor] = distance[current] + 1
                queue.append(neighbor)

        edges: list[list[str]] = []
        for node in path[1:]:
            level = distance.get(node)
            if level is None:
                continue
            parent_candidates: list[str] = []
            for candidate in path:
                if candidate == node:
                    break
                if distance.get(candidate) == level - 1 and node in adjacency.get(candidate, []):
                    parent_candidates.append(candidate)
            if not parent_candidates:
                continue
            parent = min(parent_candidates, key=lambda candidate: order_index.get(candidate, 10**9))
            edges.append([parent, node])
        return edges

    @staticmethod
    def _is_condition_line(line_text: str) -> bool:
        normalized = ExecutionTraceService._normalized_line_text(line_text)
        return (
            normalized.startswith("if ")
            or normalized.startswith("if(")
            or normalized.startswith("else if")
            or normalized.startswith("switch ")
            or normalized.startswith("switch(")
            or normalized.startswith("case ")
            or normalized.startswith("default:")
        )

    @staticmethod
    def _limit_step_indexes(indexes: list[int], max_steps: int = 260) -> list[int]:
        if len(indexes) <= max_steps:
            return indexes
        if max_steps <= 0:
            return indexes[:1]
        sampled: list[int] = []
        max_index = len(indexes) - 1
        for step in range(max_steps):
            pick = round((max_index * step) / max(1, max_steps - 1))
            pick = max(0, min(max_index, pick))
            sampled.append(indexes[pick])
        return sampled

    @staticmethod
    def _prioritize_graph_condition_steps(indexes: list[int], lines: list[str]) -> list[int]:
        if len(indexes) < 2:
            return indexes
        reordered = list(indexes)
        for _ in range(3):
            changed = False
            for pos in range(len(reordered) - 1):
                current_idx = reordered[pos]
                next_idx = reordered[pos + 1]
                current_text = lines[current_idx] if 0 <= current_idx < len(lines) else ""
                next_text = lines[next_idx] if 0 <= next_idx < len(lines) else ""
                if (
                    ExecutionTraceService._line_is_assignment_mutation(current_text)
                    and ExecutionTraceService._is_condition_line(next_text)
                ):
                    reordered[pos], reordered[pos + 1] = reordered[pos + 1], reordered[pos]
                    changed = True
            if not changed:
                break
        return reordered

    @staticmethod
    def _graph_control_repeat_count(
        *,
        operation_name: str,
        normalized_line: str,
        after_state: dict[str, Any],
    ) -> int:
        result_wrapper = after_state.get("last_result") if isinstance(after_state, dict) else None
        result = result_wrapper.get("result") if isinstance(result_wrapper, dict) else None
        nodes = after_state.get("nodes")
        edges = after_state.get("edges")
        node_count = len(nodes) if isinstance(nodes, list) else 0
        edge_count = len(edges) if isinstance(edges, list) else 0

        if operation_name in {"run_bfs", "run_dfs"} and isinstance(result, list):
            path = [str(item) for item in result]
            visit_count = max(1, len(path))
            degree_map = ExecutionTraceService._graph_out_degree_map(after_state)
            neighbor_checks = sum(max(1, degree_map.get(node, 0)) for node in path)
            neighbor_checks = max(visit_count, neighbor_checks)
            if "while (" in normalized_line and ("frente < atras" in normalized_line or "tope > 0" in normalized_line):
                return visit_count + 1
            if "for (" in normalized_line and "cant_sucesores" in normalized_line:
                return max(1, (neighbor_checks + visit_count - 1) // visit_count)
            if "if (!visitado[sucesores[i]])" in normalized_line:
                return max(1, (neighbor_checks + visit_count - 1) // visit_count)
            return 1

        if operation_name == "run_dijkstra" and isinstance(result, dict):
            path_edges = result.get("path_edges")
            path_edge_count = len(path_edges) if isinstance(path_edges, list) else 0
            vertices_span = max(1, node_count)
            outer_passes = max(1, min(vertices_span, path_edge_count + 1 if path_edge_count > 0 else vertices_span))

            if "for (i = 0; i < n_vertices; i++)" in normalized_line:
                return outer_passes
            if "for (j = 0; j < n_vertices; j++)" in normalized_line:
                return vertices_span
            if "for (j = 0; j < cant; j++)" in normalized_line:
                relax_total = max(1, path_edge_count * 2 if path_edge_count > 0 else max(1, edge_count))
                return max(1, min((relax_total + outer_passes - 1) // outer_passes, 20))
            if "while (actual != -1" in normalized_line:
                return max(1, path_edge_count + 1)
            return 1

        if operation_name == "run_bellman_ford":
            passes = max(1, min(max(1, node_count - 1), 16))
            relax_edges = max(1, min(passes * max(1, edge_count), 140))
            if "for (i = 1; i < n_vertices; i++)" in normalized_line:
                return passes
            if "for (j = 0; j < n_vertices; j++)" in normalized_line:
                return max(1, node_count)
            if "for (k = 0; k < cant; k++)" in normalized_line:
                per_pass = max(1, (relax_edges + passes - 1) // passes)
                per_vertex = max(1, (per_pass + max(1, node_count) - 1) // max(1, node_count))
                return max(1, min(per_vertex, 20))
            if "while (actual != -1" in normalized_line:
                return max(1, min(node_count, 30))
            return 1

        if operation_name == "run_prim":
            mst_edges = []
            if isinstance(result, dict) and isinstance(result.get("mst_edges"), list):
                mst_edges = result["mst_edges"]
            mst_count = len(mst_edges)
            if "for (i = 0; i < n; i++)" in normalized_line:
                return max(1, min(max(node_count, mst_count + 1), 30))
            if "for (j = 0; j < n; j++)" in normalized_line:
                return max(1, node_count)
            if "for (j = 0; j < cant; j++)" in normalized_line:
                outer = max(1, min(max(node_count, mst_count + 1), 30))
                total = max(1, min(max(mst_count * 2, 2), 120))
                return max(1, min((total + outer - 1) // outer, 20))
            return 1

        if operation_name == "run_kruskal":
            if "for (size_t j = i + 1; j < m; j++)" in normalized_line:
                return max(1, min(max(1, edge_count // 2), 20))
            if "for (size_t i = 0; i < m && resultado.cantidad < n - 1; i++)" in normalized_line:
                return max(1, min(edge_count, 120))
            if "for (size_t i = 0; i < m; i++)" in normalized_line:
                return max(1, min(edge_count, 120))
            if "for (size_t i = 0; i < n; i++)" in normalized_line:
                return max(1, min(node_count, 40))
            return 1

        return 1

    @staticmethod
    def _extract_state_size(state: dict[str, Any]) -> int:
        raw_size = state.get("size")
        if isinstance(raw_size, int):
            return max(0, raw_size)
        if isinstance(raw_size, float):
            return max(0, int(raw_size))
        metadata = state.get("metadata")
        if isinstance(metadata, dict):
            for key in ("size", "vertices_count", "cantidad"):
                value = metadata.get(key)
                if isinstance(value, (int, float)):
                    return max(0, int(value))
        items = state.get("items")
        if isinstance(items, list):
            return len(items)
        nodes = state.get("nodes")
        if isinstance(nodes, list):
            return len(nodes)
        buckets = state.get("buckets")
        if isinstance(buckets, list):
            total = 0
            for bucket in buckets:
                if isinstance(bucket, list):
                    total += len(bucket)
            return total
        root = state.get("root")
        if isinstance(root, dict):
            return len(ExecutionTraceService._collect_tree_values(root))
        return 0

    @staticmethod
    def _is_if_header(normalized_line: str) -> bool:
        return normalized_line.startswith("if ") or normalized_line.startswith("if(")

    @staticmethod
    def _is_else_header(normalized_line: str) -> bool:
        return normalized_line.startswith("else")

    @staticmethod
    def _is_loop_header(normalized_line: str) -> bool:
        return (
            normalized_line.startswith("while ")
            or normalized_line.startswith("while(")
            or normalized_line.startswith("for ")
            or normalized_line.startswith("for(")
        )

    @staticmethod
    def _is_return_statement(normalized_line: str) -> bool:
        return normalized_line.startswith("return")

    @staticmethod
    def _estimate_generic_loop_iterations(
        *,
        normalized_line: str,
        operation_name: str,
        before_state: dict[str, Any],
        after_state: dict[str, Any],
    ) -> int:
        before_size = ExecutionTraceService._extract_state_size(before_state)
        after_size = ExecutionTraceService._extract_state_size(after_state)
        op = str(operation_name or "").lower()

        if "!= null" in normalized_line or "!= nullptr" in normalized_line:
            if op in {"limpiar", "clear", "vaciar"}:
                return max(0, before_size)
            if "desencolar" in op or "desapilar" in op or "eliminar" in op:
                return max(1, before_size)
            return max(0, before_size)

        if normalized_line.startswith("for ") or normalized_line.startswith("for("):
            estimated = max(before_size, after_size)
            if estimated <= 0:
                estimated = 3
            return max(1, min(estimated, 40))

        return 1

    @staticmethod
    def _evaluate_generic_condition(
        *,
        normalized_line: str,
        success: bool,
        message: str,
        before_state: dict[str, Any],
        after_state: dict[str, Any],
        payload: dict[str, Any] | None = None,
    ) -> bool:
        msg = str(message or "").lower()
        before_size = ExecutionTraceService._extract_state_size(before_state)
        after_size = ExecutionTraceService._extract_state_size(after_state)
        root_value = None
        root = before_state.get("root") if isinstance(before_state, dict) else None
        if isinstance(root, dict):
            root_value = ExecutionTraceService._coerce_number(root.get("value"))
        raw_pos = None if payload is None else payload.get("position")
        pos_ui: int | None = None
        raw_value = None if payload is None else payload.get("value")
        value_ui = ExecutionTraceService._coerce_number(raw_value)
        if raw_pos is not None and str(raw_pos).strip() != "":
            try:
                pos_ui = int(raw_pos)
            except (TypeError, ValueError):
                pos_ui = None

        if "pos <= 0" in normalized_line:
            return bool(pos_ui is not None and pos_ui <= 0)
        if "pos < 1" in normalized_line:
            return bool(pos_ui is not None and pos_ui < 1)
        if "pos == 1" in normalized_line or "pos==1" in normalized_line:
            return bool(pos_ui == 1)
        if "i == pos" in normalized_line or "i==pos" in normalized_line:
            # En inserciones por posicion, si la operacion termino en exito
            # se asume que eventualmente se alcanzara la igualdad.
            return bool(success and pos_ui is not None and pos_ui > 1)

        if "nodo == null" in normalized_line:
            return before_size == 0
        if "valor < nodo->valor" in normalized_line and value_ui is not None and root_value is not None:
            return value_ui < root_value
        if "valor > nodo->valor" in normalized_line and value_ui is not None and root_value is not None:
            return value_ui > root_value
        if "x < actual->nro" in normalized_line and value_ui is not None and root_value is not None:
            return value_ui < root_value
        if "x > actual->nro" in normalized_line and value_ui is not None and root_value is not None:
            return value_ui > root_value

        if "== null" in normalized_line or "==nullptr" in normalized_line:
            if success:
                return False
            if any(token in msg for token in ("no inicializada", "no se pudo", "vacia", "vacía")):
                return True
            return before_size == 0 and after_size == 0

        if "!= null" in normalized_line or "!= nullptr" in normalized_line:
            return before_size > 0 or after_size > 0

        if "vacia" in normalized_line or "vacía" in normalized_line:
            if "!" in normalized_line:
                return before_size > 0
            return before_size == 0

        if "!existe" in normalized_line:
            return (not success) or ("no existe" in msg)
        if "dist[destino] >= inf" in normalized_line or "dist[destino]>=inf" in normalized_line:
            return "no existe ruta" in msg
        if (
            "dist[idx_llegada] == int_max" in normalized_line
            or "dist[idx_llegada]==int_max" in normalized_line
        ):
            return "no existe ruta" in msg
        if "nodo == null" in normalized_line:
            return before_size == 0
        if "valor < nodo->valor" in normalized_line and value_ui is not None and root_value is not None:
            return value_ui < root_value
        if "valor > nodo->valor" in normalized_line and value_ui is not None and root_value is not None:
            return value_ui > root_value
        if "x < actual->nro" in normalized_line and value_ui is not None and root_value is not None:
            return value_ui < root_value
        if "x > actual->nro" in normalized_line and value_ui is not None and root_value is not None:
            return value_ui > root_value

        if normalized_line.startswith("if "):
            return False
        if normalized_line.startswith("if("):
            return False
        return True

    @staticmethod
    def _expand_generic_control_flow_indexes(
        *,
        operation_name: str,
        lines: list[str],
        executable_line_indexes: list[int],
        before_state: dict[str, Any],
        after_state: dict[str, Any],
        success: bool,
        message: str,
        payload: dict[str, Any] | None = None,
    ) -> list[int]:
        if not executable_line_indexes:
            return executable_line_indexes

        sorted_exec = sorted(executable_line_indexes)

        def _next_pos_after_line(from_pos: int, line_limit: int) -> int:
            for candidate in range(from_pos, len(sorted_exec)):
                if sorted_exec[candidate] > line_limit:
                    return candidate
            return len(sorted_exec)

        def _expand_segment(start_pos: int, end_pos: int) -> tuple[list[int], bool]:
            segment: list[int] = []
            pos = start_pos
            while pos < end_pos:
                line_index = sorted_exec[pos]
                line_text = lines[line_index] if 0 <= line_index < len(lines) else ""
                normalized_line = ExecutionTraceService._normalized_line_text(line_text)

                if ExecutionTraceService._is_if_header(normalized_line):
                    segment.append(line_index)
                    cond_true = ExecutionTraceService._evaluate_generic_condition(
                        normalized_line=normalized_line,
                        success=success,
                        message=message,
                        before_state=before_state,
                        after_state=after_state,
                        payload=payload,
                    )
                    if "{" not in line_text:
                        close_paren = line_text.rfind(")")
                        trailing_stmt = line_text[close_paren + 1 :].strip() if close_paren >= 0 else ""
                        if trailing_stmt:
                            if cond_true and trailing_stmt.lower().startswith("return"):
                                return segment, True
                            pos += 1
                            continue
                        next_pos = pos + 1
                        if next_pos < end_pos:
                            next_line_index = sorted_exec[next_pos]
                            next_line_text = lines[next_line_index] if 0 <= next_line_index < len(lines) else ""
                            next_norm = ExecutionTraceService._normalized_line_text(next_line_text)
                            if cond_true and not ExecutionTraceService._is_else_header(next_norm):
                                segment.append(next_line_index)
                                if ExecutionTraceService._is_return_statement(next_norm):
                                    return segment, True
                                pos = next_pos + 1
                                # Saltar rama else/else-if complementaria de un if sin llaves.
                                if pos < end_pos:
                                    else_line_index = sorted_exec[pos]
                                    else_line_text = lines[else_line_index] if 0 <= else_line_index < len(lines) else ""
                                    else_norm = ExecutionTraceService._normalized_line_text(else_line_text)
                                    if ExecutionTraceService._is_else_header(else_norm):
                                        pos += 1
                                        if pos < end_pos:
                                            after_else_norm = ExecutionTraceService._normalized_line_text(
                                                lines[sorted_exec[pos]] if 0 <= sorted_exec[pos] < len(lines) else ""
                                            )
                                            if not ExecutionTraceService._is_else_header(after_else_norm):
                                                pos += 1
                                continue
                            if not cond_true and not ExecutionTraceService._is_else_header(next_norm):
                                pos = next_pos + 1
                                continue
                    open_line_index = (
                        line_index
                        if "{" in line_text
                        else ExecutionTraceService._next_nonempty_line_index(lines, line_index + 1)
                    )
                    close_line_index = (
                        ExecutionTraceService._find_matching_brace_line(lines, open_line_index)
                        if open_line_index >= 0
                        else -1
                    )
                    if close_line_index < 0 or close_line_index <= line_index:
                        cond_true = ExecutionTraceService._evaluate_generic_condition(
                            normalized_line=normalized_line,
                            success=success,
                            message=message,
                            before_state=before_state,
                            after_state=after_state,
                            payload=payload,
                        )
                        if cond_true and "return" in normalized_line:
                            return segment, True
                        pos += 1
                        continue

                    block_end_pos = _next_pos_after_line(pos + 1, close_line_index)
                    body_start_pos = pos + 1
                    body_end_pos = block_end_pos

                    else_pos = block_end_pos if block_end_pos < end_pos else -1
                    else_close_line = -1
                    else_block_end_pos = -1
                    else_has_block = False
                    if else_pos >= 0:
                        else_index = sorted_exec[else_pos]
                        else_text = lines[else_index] if 0 <= else_index < len(lines) else ""
                        else_norm = ExecutionTraceService._normalized_line_text(else_text)
                        if ExecutionTraceService._is_else_header(else_norm):
                            else_has_block = True
                            else_open_line = (
                                else_index
                                if "{" in else_text
                                else ExecutionTraceService._next_nonempty_line_index(lines, else_index + 1)
                            )
                            else_close_line = (
                                ExecutionTraceService._find_matching_brace_line(lines, else_open_line)
                                if else_open_line >= 0
                                else -1
                            )
                            else_block_end_pos = (
                                _next_pos_after_line(else_pos + 1, else_close_line)
                                if else_close_line >= else_index
                                else else_pos + 1
                            )

                    if cond_true:
                        nested, did_return = _expand_segment(body_start_pos, body_end_pos)
                        segment.extend(nested)
                        if did_return:
                            return segment, True
                    elif else_has_block:
                        segment.append(sorted_exec[else_pos])
                        else_line_index = sorted_exec[else_pos]
                        else_line_text = lines[else_line_index] if 0 <= else_line_index < len(lines) else ""
                        else_norm = ExecutionTraceService._normalized_line_text(else_line_text)
                        if "{" not in else_line_text and "return" in else_norm:
                            return segment, True
                        nested, did_return = _expand_segment(else_pos + 1, else_block_end_pos)
                        segment.extend(nested)
                        if did_return:
                            return segment, True

                    if else_has_block and else_block_end_pos > 0:
                        pos = else_block_end_pos
                    else:
                        pos = block_end_pos
                    continue

                if ExecutionTraceService._is_loop_header(normalized_line):
                    open_line_index = (
                        line_index
                        if "{" in line_text
                        else ExecutionTraceService._next_nonempty_line_index(lines, line_index + 1)
                    )
                    close_line_index = (
                        ExecutionTraceService._find_matching_brace_line(lines, open_line_index)
                        if open_line_index >= 0
                        else -1
                    )
                    if close_line_index < 0 or close_line_index <= line_index:
                        segment.append(line_index)
                        pos += 1
                        continue

                    block_end_pos = _next_pos_after_line(pos + 1, close_line_index)
                    body_start_pos = pos + 1
                    body_end_pos = block_end_pos

                    repeat_count = ExecutionTraceService._estimate_generic_loop_iterations(
                        normalized_line=normalized_line,
                        operation_name=operation_name,
                        before_state=before_state,
                        after_state=after_state,
                    )
                    repeat_count = max(0, min(repeat_count, 180))
                    if repeat_count <= 0:
                        segment.append(line_index)
                    else:
                        nested_body, nested_returns = _expand_segment(body_start_pos, body_end_pos)
                        for _ in range(repeat_count):
                            segment.append(line_index)
                            segment.extend(nested_body)
                            if nested_returns:
                                return segment, True
                        segment.append(line_index)
                    pos = block_end_pos
                    continue

                if ExecutionTraceService._is_else_header(normalized_line):
                    if "return" in normalized_line:
                        segment.append(line_index)
                        return segment, True
                    pos += 1
                    continue

                segment.append(line_index)
                if ExecutionTraceService._is_return_statement(normalized_line):
                    return segment, True
                pos += 1

            return segment, False

        expanded, _ = _expand_segment(0, len(sorted_exec))
        return ExecutionTraceService._limit_step_indexes(expanded)

    @staticmethod
    def _expand_graph_control_flow_indexes(
        *,
        operation_name: str,
        lines: list[str],
        executable_line_indexes: list[int],
        before_state: dict[str, Any],
        after_state: dict[str, Any],
        success: bool,
        message: str,
        payload: dict[str, Any] | None = None,
    ) -> list[int]:
        if not executable_line_indexes:
            return executable_line_indexes
        if not operation_name.startswith("run_"):
            return executable_line_indexes
        if operation_name == "run_bfs":
            bfs_indexes = ExecutionTraceService._expand_graph_bfs_indexes(
                lines=lines,
                after_state=after_state,
                success=success,
                message=message,
                payload=payload or {},
            )
            if bfs_indexes is not None:
                return bfs_indexes
        if operation_name == "run_dijkstra":
            dijkstra_indexes = ExecutionTraceService._expand_graph_dijkstra_indexes(
                lines=lines,
                after_state=after_state,
                success=success,
                message=message,
            )
            if dijkstra_indexes is not None:
                return dijkstra_indexes
        if operation_name == "run_bellman_ford":
            bellman_indexes = ExecutionTraceService._expand_graph_bellman_ford_indexes(
                lines=lines,
                after_state=after_state,
                success=success,
                message=message,
            )
            if bellman_indexes is not None:
                return bellman_indexes
        if operation_name == "run_kruskal":
            kruskal_indexes = ExecutionTraceService._expand_graph_kruskal_indexes(
                lines=lines,
                before_state=before_state,
                after_state=after_state,
                success=success,
                message=message,
            )
            if kruskal_indexes is not None:
                return kruskal_indexes
        if operation_name == "run_dfs":
            dfs_indexes = ExecutionTraceService._expand_recursive_graph_dfs_indexes(
                lines=lines,
                before_state=before_state,
                after_state=after_state,
                payload=payload or {},
                success=success,
            )
            if dfs_indexes is not None:
                return dfs_indexes

        sorted_exec = sorted(executable_line_indexes)

        def _next_pos_after_line(from_pos: int, line_limit: int) -> int:
            for candidate in range(from_pos, len(sorted_exec)):
                if sorted_exec[candidate] > line_limit:
                    return candidate
            return len(sorted_exec)

        def _expand_segment(start_pos: int, end_pos: int) -> tuple[list[int], bool]:
            segment: list[int] = []
            pos = start_pos
            while pos < end_pos:
                line_index = sorted_exec[pos]
                line_text = lines[line_index] if 0 <= line_index < len(lines) else ""
                normalized_line = ExecutionTraceService._normalized_line_text(line_text)

                if ExecutionTraceService._is_if_header(normalized_line):
                    segment.append(line_index)
                    if "{" not in line_text:
                        close_paren = line_text.rfind(")")
                        trailing_stmt = line_text[close_paren + 1 :].strip() if close_paren >= 0 else ""
                        if trailing_stmt:
                            cond_true = ExecutionTraceService._evaluate_generic_condition(
                                normalized_line=normalized_line,
                                success=success,
                                message=message,
                                before_state=before_state,
                                after_state=after_state,
                                payload=payload,
                            )
                            if cond_true and trailing_stmt.lower().startswith("return"):
                                return segment, True
                            pos += 1
                            continue
                    open_line_index = (
                        line_index
                        if "{" in line_text
                        else ExecutionTraceService._next_nonempty_line_index(lines, line_index + 1)
                    )
                    close_line_index = (
                        ExecutionTraceService._find_matching_brace_line(lines, open_line_index)
                        if open_line_index >= 0
                        else -1
                    )
                    cond_true = ExecutionTraceService._evaluate_generic_condition(
                        normalized_line=normalized_line,
                        success=success,
                        message=message,
                        before_state=before_state,
                        after_state=after_state,
                        payload=payload,
                    )
                    if close_line_index < 0 or close_line_index <= line_index:
                        if cond_true and "return" in normalized_line:
                            return segment, True
                        pos += 1
                        continue

                    block_end_pos = _next_pos_after_line(pos + 1, close_line_index)
                    body_start_pos = pos + 1
                    body_end_pos = block_end_pos

                    else_pos = block_end_pos if block_end_pos < end_pos else -1
                    else_close_line = -1
                    else_block_end_pos = -1
                    else_has_block = False
                    if else_pos >= 0:
                        else_index = sorted_exec[else_pos]
                        else_text = lines[else_index] if 0 <= else_index < len(lines) else ""
                        else_norm = ExecutionTraceService._normalized_line_text(else_text)
                        if ExecutionTraceService._is_else_header(else_norm):
                            else_has_block = True
                            else_open_line = (
                                else_index
                                if "{" in else_text
                                else ExecutionTraceService._next_nonempty_line_index(lines, else_index + 1)
                            )
                            else_close_line = (
                                ExecutionTraceService._find_matching_brace_line(lines, else_open_line)
                                if else_open_line >= 0
                                else -1
                            )
                            else_block_end_pos = (
                                _next_pos_after_line(else_pos + 1, else_close_line)
                                if else_close_line >= else_index
                                else else_pos + 1
                            )

                    if cond_true:
                        nested, did_return = _expand_segment(body_start_pos, body_end_pos)
                        segment.extend(nested)
                        if did_return:
                            return segment, True
                    elif else_has_block:
                        segment.append(sorted_exec[else_pos])
                        nested, did_return = _expand_segment(else_pos + 1, else_block_end_pos)
                        segment.extend(nested)
                        if did_return:
                            return segment, True

                    if else_has_block and else_block_end_pos > 0:
                        pos = else_block_end_pos
                    else:
                        pos = block_end_pos
                    continue

                is_loop_header = (
                    normalized_line.startswith("while ")
                    or normalized_line.startswith("while(")
                    or normalized_line.startswith("for ")
                    or normalized_line.startswith("for(")
                )
                if not is_loop_header:
                    if ExecutionTraceService._is_else_header(normalized_line):
                        pos += 1
                        continue
                    segment.append(line_index)
                    if ExecutionTraceService._is_return_statement(normalized_line):
                        return segment, True
                    pos += 1
                    continue

                open_line_index = line_index if "{" in line_text else ExecutionTraceService._next_nonempty_line_index(lines, line_index + 1)
                close_line_index = (
                    ExecutionTraceService._find_matching_brace_line(lines, open_line_index)
                    if open_line_index >= 0
                    else -1
                )
                if close_line_index < 0 or close_line_index <= line_index:
                    segment.append(line_index)
                    pos += 1
                    continue

                block_end_pos = _next_pos_after_line(pos + 1, close_line_index)
                if block_end_pos <= pos + 1:
                    segment.append(line_index)
                    pos += 1
                    continue

                repeat_count = ExecutionTraceService._graph_control_repeat_count(
                    operation_name=operation_name,
                    normalized_line=normalized_line,
                    after_state=after_state,
                )
                repeat_count = max(1, min(repeat_count, 180))
                nested_body, nested_returns = _expand_segment(pos + 1, block_end_pos)
                for _ in range(repeat_count):
                    segment.append(line_index)
                    segment.extend(nested_body)
                    if nested_returns:
                        return segment, True
                pos = block_end_pos
            return segment, False

        expanded, _ = _expand_segment(0, len(sorted_exec))
        return ExecutionTraceService._limit_step_indexes(expanded)

    @staticmethod
    def _expand_graph_kruskal_indexes(
        *,
        lines: list[str],
        before_state: dict[str, Any],
        after_state: dict[str, Any],
        success: bool,
        message: str,
    ) -> list[int] | None:
        normalized = [ExecutionTraceService._normalized_line_text(line) for line in lines]

        header = ExecutionTraceService._find_line_index_by_contains(normalized, "listaarco grafo_kruskal(")
        guard_nm = ExecutionTraceService._find_line_index_by_contains(normalized, "if (n <= 0 || m <= 0)")
        return_null = ExecutionTraceService._find_line_index_by_contains(normalized, "return null;")
        allocs = ExecutionTraceService._find_line_index_by_contains(normalized, "conjuntos.padre = malloc")
        alloc_guard = ExecutionTraceService._find_line_index_by_contains(
            normalized, "if (conjuntos.padre == null || vertices == null || aristas == null)"
        )
        init_vertices_guard = ExecutionTraceService._find_line_index_by_contains(
            normalized, "if (!inicializarvectorvertices(g, vertices, n))"
        )
        init_parent_loop = ExecutionTraceService._find_line_index_by_contains(
            normalized, "for (i = 0; i < n; i++) conjuntos.padre[i] = i;"
        )
        while_collect = ExecutionTraceService._find_line_index_by_contains(
            normalized, "while (a != null && i < m)"
        )
        assign_collect = ExecutionTraceService._find_line_index_by_contains(normalized, "aristas[i++] = a;")
        next_collect = ExecutionTraceService._find_line_index_by_contains(normalized, "a = a->sig;")
        for_x = ExecutionTraceService._find_line_index_by_contains(normalized, "for (int x = 0; x < i - 1; x++)")
        for_y = ExecutionTraceService._find_line_index_by_contains(normalized, "for (int y = 0; y < i - x - 1; y++)")
        if_swap = ExecutionTraceService._find_line_index_by_contains(
            normalized, "if (aristas[y]->costo > aristas[y+1]->costo)"
        )
        swap_tmp = ExecutionTraceService._find_line_index_by_contains(normalized, "listaarco tmp = aristas[y];")
        swap_a = ExecutionTraceService._find_line_index_by_contains(normalized, "aristas[y] = aristas[y+1];")
        swap_b = ExecutionTraceService._find_line_index_by_contains(normalized, "aristas[y+1] = tmp;")
        for_j = ExecutionTraceService._find_line_index_by_contains(normalized, "for (int j = 0; j < i; j++)")
        idx_u = ExecutionTraceService._find_line_index_by_contains(
            normalized, "int u = indicevertice(vertices, n, aristas[j]->origen);"
        )
        idx_v = ExecutionTraceService._find_line_index_by_contains(
            normalized, "int v = indicevertice(vertices, n, aristas[j]->destino);"
        )
        if_take = ExecutionTraceService._find_line_index_by_contains(
            normalized,
            "if (u != -1 && v != -1 && grafo_encontrar_conjunto(&conjuntos, u) != grafo_encontrar_conjunto(&conjuntos, v))",
        )
        union_line = ExecutionTraceService._find_line_index_by_contains(
            normalized, "grafo_unir_conjuntos(&conjuntos, u, v);"
        )
        new_decl = ExecutionTraceService._find_line_index_by_contains(
            normalized, "listaarco nuevo = malloc(sizeof(struct nodoa));"
        )
        if_new_null = ExecutionTraceService._find_line_index_by_contains(normalized, "if (nuevo == null)")
        liberar_mst = ExecutionTraceService._find_line_index_by_contains(normalized, "liberarlistaarcos(mst);")
        set_mst_null = ExecutionTraceService._find_line_index_by_contains(normalized, "mst = null;")
        break_line = ExecutionTraceService._find_line_index_by_contains(normalized, "break;")
        set_origen = ExecutionTraceService._find_line_index_by_contains(normalized, "nuevo->origen = aristas[j]->origen;")
        set_destino = ExecutionTraceService._find_line_index_by_contains(normalized, "nuevo->destino = aristas[j]->destino;")
        set_costo = ExecutionTraceService._find_line_index_by_contains(normalized, "nuevo->costo = aristas[j]->costo;")
        set_sig = ExecutionTraceService._find_line_index_by_contains(normalized, "nuevo->sig = mst;")
        set_mst = ExecutionTraceService._find_line_index_by_contains(normalized, "mst = nuevo;")
        free_aristas = ExecutionTraceService._find_line_index_by_contains(normalized, "free(aristas);")
        free_padre = ExecutionTraceService._find_line_index_by_contains(normalized, "free(conjuntos.padre);")
        free_vertices = ExecutionTraceService._find_line_index_by_contains(normalized, "free(vertices);")
        return_mst = ExecutionTraceService._find_line_index_by_contains(normalized, "return mst;")

        required = [
            header,
            guard_nm,
            allocs,
            alloc_guard,
            init_vertices_guard,
            for_j,
            idx_u,
            idx_v,
            if_take,
            return_mst,
        ]
        if any(i < 0 for i in required):
            return None

        out: list[int] = []

        def _a(idx: int) -> None:
            if idx >= 0:
                out.append(idx)

        msg = str(message or "").lower()
        result_wrapper = after_state.get("last_result") if isinstance(after_state, dict) else None
        result = result_wrapper.get("result") if isinstance(result_wrapper, dict) else None
        mst_edges = result.get("mst_edges") if isinstance(result, dict) else None
        mst_count = len(mst_edges) if isinstance(mst_edges, list) else 0
        edge_count = len(after_state.get("edges")) if isinstance(after_state.get("edges"), list) else 0

        _a(header)
        _a(guard_nm)
        if not success and ("vacio" in msg or "vac" in msg):
            _a(return_null)
            return ExecutionTraceService._limit_step_indexes(out)

        _a(allocs)
        _a(alloc_guard)
        if not success and "malloc" in msg:
            _a(return_null)
            return ExecutionTraceService._limit_step_indexes(out)

        _a(init_vertices_guard)
        if not success and "vertices" in msg:
            _a(return_null)
            return ExecutionTraceService._limit_step_indexes(out)

        _a(init_parent_loop)
        _a(while_collect)
        collect_iters = max(1, min(edge_count, 20))
        for _ in range(collect_iters):
            _a(assign_collect)
            _a(next_collect)
        _a(while_collect)

        if for_x >= 0 and for_y >= 0 and if_swap >= 0:
            bubble_outer = max(1, min(max(edge_count // 2, 1), 4))
            for x in range(bubble_outer):
                _a(for_x)
                inner = max(1, min(max(edge_count // 3, 1), 5))
                for _ in range(inner):
                    _a(for_y)
                    _a(if_swap)
                    if swap_tmp >= 0 and swap_a >= 0 and swap_b >= 0 and (x == 0 or edge_count <= 4):
                        _a(swap_tmp)
                        _a(swap_a)
                        _a(swap_b)
                _a(for_y)
            _a(for_x)

        _a(for_j)
        j_iters = max(1, min(edge_count, 80))
        selected = 0
        for j in range(j_iters):
            _a(idx_u)
            _a(idx_v)
            _a(if_take)
            take_edge = selected < mst_count
            if take_edge:
                selected += 1
                _a(union_line)
                _a(new_decl)
                _a(if_new_null)
                if not success and "nuevo" in msg:
                    _a(liberar_mst)
                    _a(set_mst_null)
                    _a(break_line)
                    break
                _a(set_origen)
                _a(set_destino)
                _a(set_costo)
                _a(set_sig)
                _a(set_mst)
            if j < j_iters - 1:
                _a(for_j)

        _a(free_aristas)
        _a(free_padre)
        _a(free_vertices)
        _a(return_mst)
        return ExecutionTraceService._limit_step_indexes(out)

    @staticmethod
    def _expand_graph_dijkstra_indexes(
        *,
        lines: list[str],
        after_state: dict[str, Any],
        success: bool,
        message: str,
    ) -> list[int] | None:
        normalized = [ExecutionTraceService._normalized_line_text(line) for line in lines]

        header = ExecutionTraceService._find_line_index_by_contains(normalized, "listaarco grafo_dijkstra(")
        guard_n = ExecutionTraceService._find_line_index_by_contains(normalized, "if (n <= 0)")
        return_null = ExecutionTraceService._find_line_index_by_contains(normalized, "return null;")
        alloc_dist = ExecutionTraceService._find_line_index_by_contains(normalized, "dist = malloc(sizeof(int) * n);")
        alloc_guard = ExecutionTraceService._find_line_index_by_contains(
            normalized, "if (dist == null || prev == null || visitado == null || vertices == null)"
        )
        init_vertices_guard = ExecutionTraceService._find_line_index_by_contains(
            normalized, "if (!inicializarvectorvertices(g, vertices, n))"
        )
        init_loop = ExecutionTraceService._find_line_index_by_contains(normalized, "for (i = 0; i < n; i++)")
        init_dist = ExecutionTraceService._find_line_index_by_contains(normalized, "dist[i] = int_max;")
        init_prev = ExecutionTraceService._find_line_index_by_contains(normalized, "prev[i] = -1;")
        idx_inicio = ExecutionTraceService._find_line_index_by_contains(normalized, "idx_inicio = indicevertice(vertices, n, inicio);")
        idx_llegada = ExecutionTraceService._find_line_index_by_contains(normalized, "idx_llegada = indicevertice(vertices, n, llegada);")
        idx_guard = ExecutionTraceService._find_line_index_by_contains(normalized, "if (idx_inicio == -1 || idx_llegada == -1)")
        dist_start = ExecutionTraceService._find_line_index_by_contains(normalized, "dist[idx_inicio] = 0;")
        main_loop = ExecutionTraceService._find_line_index_by_contains(normalized, "for (i = 0; i < n; i++)")
        for_j = ExecutionTraceService._find_line_index_by_contains(normalized, "for (j = 0; j < n; j++)")
        if_pick = ExecutionTraceService._find_line_index_by_contains(normalized, "if (!visitado[j] && dist[j] < min)")
        set_min = ExecutionTraceService._find_line_index_by_contains(normalized, "min = dist[j];")
        set_u = ExecutionTraceService._find_line_index_by_contains(normalized, "u = j;")
        if_u_minus = ExecutionTraceService._find_line_index_by_contains(normalized, "if (u == -1)")
        break_line = ExecutionTraceService._find_line_index_by_contains(normalized, "break;")
        set_visit = ExecutionTraceService._find_line_index_by_contains(normalized, "visitado[u] = 1;")
        suces_decl = ExecutionTraceService._find_line_index_by_contains(normalized, "suces = grafo_sucesores(g, vertices[u]);")
        while_suces = ExecutionTraceService._find_line_index_by_contains(normalized, "while (suces != null)")
        v_idx = ExecutionTraceService._find_line_index_by_contains(normalized, "int v = indicevertice(vertices, n, suces->dato);")
        if_v_ok = ExecutionTraceService._find_line_index_by_contains(normalized, "if (v != -1 && !visitado[v])")
        costo_line = ExecutionTraceService._find_line_index_by_contains(normalized, "int costo = grafo_costo_arco(g, vertices[u], vertices[v]);")
        if_overflow = ExecutionTraceService._find_line_index_by_contains(
            normalized, "if (costo >= 0 && dist[u] != int_max && dist[u] <= int_max - costo)"
        )
        nueva_dist = ExecutionTraceService._find_line_index_by_contains(normalized, "int nueva_dist = dist[u] + costo;")
        if_relax = ExecutionTraceService._find_line_index_by_contains(normalized, "if (nueva_dist < dist[v])")
        set_dist = ExecutionTraceService._find_line_index_by_contains(normalized, "dist[v] = nueva_dist;")
        set_prev = ExecutionTraceService._find_line_index_by_contains(normalized, "prev[v] = u;")
        tmp_line = ExecutionTraceService._find_line_index_by_contains(normalized, "listavertice temp = suces;")
        next_suces = ExecutionTraceService._find_line_index_by_contains(normalized, "suces = suces->sig;")
        free_temp = ExecutionTraceService._find_line_index_by_contains(normalized, "free(temp);")
        if_unreachable = ExecutionTraceService._find_line_index_by_contains(normalized, "if (dist[idx_llegada] == int_max)")
        while_prev = ExecutionTraceService._find_line_index_by_contains(normalized, "while (prev[destino] != -1)")
        new_arc = ExecutionTraceService._find_line_index_by_contains(normalized, "listaarco nuevo = malloc(sizeof(struct nodoa));")
        if_new_null = ExecutionTraceService._find_line_index_by_contains(normalized, "if (nuevo == null)")
        liberar_camino = ExecutionTraceService._find_line_index_by_contains(normalized, "liberarlistaarcos(camino);")
        set_camino_null = ExecutionTraceService._find_line_index_by_contains(normalized, "camino = null;")
        set_origen = ExecutionTraceService._find_line_index_by_contains(normalized, "nuevo->origen = vertices[prev[destino]];")
        set_destino = ExecutionTraceService._find_line_index_by_contains(normalized, "nuevo->destino = vertices[destino];")
        set_costo_arc = ExecutionTraceService._find_line_index_by_contains(normalized, "nuevo->costo = grafo_costo_arco(g, nuevo->origen, nuevo->destino);")
        set_sig = ExecutionTraceService._find_line_index_by_contains(normalized, "nuevo->sig = camino;")
        set_camino = ExecutionTraceService._find_line_index_by_contains(normalized, "camino = nuevo;")
        set_dest = ExecutionTraceService._find_line_index_by_contains(normalized, "destino = prev[destino];")
        free_dist = ExecutionTraceService._find_line_index_by_contains(normalized, "free(dist);")
        free_prev = ExecutionTraceService._find_line_index_by_contains(normalized, "free(prev);")
        free_vis = ExecutionTraceService._find_line_index_by_contains(normalized, "free(visitado);")
        free_vertices = ExecutionTraceService._find_line_index_by_contains(normalized, "free(vertices);")
        return_camino = ExecutionTraceService._find_line_index_by_contains(normalized, "return camino;")

        required = [header, guard_n, alloc_dist, alloc_guard, init_vertices_guard, idx_guard, main_loop, for_j, if_pick, if_u_minus, return_camino]
        if any(i < 0 for i in required):
            return None

        out: list[int] = []
        def _a(idx: int) -> None:
            if idx >= 0:
                out.append(idx)

        result_wrapper = after_state.get("last_result") if isinstance(after_state, dict) else None
        result = result_wrapper.get("result") if isinstance(result_wrapper, dict) else None
        distances = result.get("distances") if isinstance(result, dict) else {}
        path_edges = result.get("path_edges") if isinstance(result, dict) else []
        reachable = bool(result.get("reachable", False)) if isinstance(result, dict) else False
        node_count = len(after_state.get("nodes")) if isinstance(after_state.get("nodes"), list) else max(1, len(distances) if isinstance(distances, dict) else 1)
        edge_count = len(after_state.get("edges")) if isinstance(after_state.get("edges"), list) else 1
        finite_count = 0
        if isinstance(distances, dict):
            for value in distances.values():
                if value is None:
                    continue
                text = str(value).lower()
                if "inf" not in text:
                    finite_count += 1

        _a(header)
        _a(guard_n)
        if not success and "n <= 0" in str(message or "").lower():
            _a(return_null)
            return ExecutionTraceService._limit_step_indexes(out)

        _a(alloc_dist)
        _a(alloc_guard)
        _a(init_vertices_guard)
        _a(init_loop)
        init_iters = max(1, min(node_count, 20))
        for _ in range(init_iters):
            _a(init_dist)
            _a(init_prev)
        _a(init_loop)

        _a(idx_inicio)
        _a(idx_llegada)
        _a(idx_guard)
        _a(dist_start)

        outer_iters = max(1, min(node_count, 24))
        neighbor_per_outer = max(1, min(max(edge_count // max(1, node_count), 1), 3))
        disconnected_break = isinstance(distances, dict) and finite_count < max(1, node_count)
        for oi in range(outer_iters):
            _a(main_loop)
            _a(for_j)
            for _ in range(max(1, min(node_count, 20))):
                _a(if_pick)
                _a(set_min)
                _a(set_u)
            _a(for_j)
            _a(if_u_minus)
            if disconnected_break and oi >= max(0, finite_count - 1):
                _a(break_line)
                break
            _a(set_visit)
            _a(suces_decl)
            _a(while_suces)
            for _ in range(neighbor_per_outer):
                _a(v_idx)
                _a(if_v_ok)
                _a(costo_line)
                _a(if_overflow)
                _a(nueva_dist)
                _a(if_relax)
                _a(set_dist)
                _a(set_prev)
                _a(tmp_line)
                _a(next_suces)
                _a(free_temp)
                _a(while_suces)
        _a(main_loop)

        _a(if_unreachable)
        if not reachable:
            _a(free_dist)
            _a(free_prev)
            _a(free_vis)
            _a(free_vertices)
            _a(return_null)
            return ExecutionTraceService._limit_step_indexes(out)

        _a(while_prev)
        path_len = len(path_edges) if isinstance(path_edges, list) else 0
        for _ in range(max(1, min(path_len, 40))):
            _a(new_arc)
            _a(if_new_null)
            if not success and "camino" in str(message or "").lower():
                _a(liberar_camino)
                _a(set_camino_null)
                _a(break_line)
                break
            _a(set_origen)
            _a(set_destino)
            _a(set_costo_arc)
            _a(set_sig)
            _a(set_camino)
            _a(set_dest)
            _a(while_prev)

        _a(free_dist)
        _a(free_prev)
        _a(free_vis)
        _a(free_vertices)
        _a(return_camino)
        return ExecutionTraceService._limit_step_indexes(out)

    @staticmethod
    def _expand_graph_bfs_indexes(
        *,
        lines: list[str],
        after_state: dict[str, Any],
        success: bool,
        message: str,
        payload: dict[str, Any],
    ) -> list[int] | None:
        normalized = [ExecutionTraceService._normalized_line_text(line) for line in lines]

        header = ExecutionTraceService._find_line_index_by_contains(normalized, "listavertice grafo_bfs(")
        desmarcar = ExecutionTraceService._find_line_index_by_contains(normalized, "g = grafo_desmarcar(g);")
        cola_decl = ExecutionTraceService._find_line_index_by_contains(normalized, "struct cola cola = {null, null};")
        rec_decl = ExecutionTraceService._find_line_index_by_contains(normalized, "listavertice recorrido = null;")
        v_decl = ExecutionTraceService._find_line_index_by_contains(normalized, "listavertice v = g.v;")
        existe_decl = ExecutionTraceService._find_line_index_by_contains(normalized, "int existe = 0;")
        while_v = ExecutionTraceService._find_line_index_by_contains(normalized, "while (v != null)")
        if_v_eq = ExecutionTraceService._find_line_index_by_contains(normalized, "if (v->dato == inicio)")
        set_existe = ExecutionTraceService._find_line_index_by_contains(normalized, "existe = 1;")
        break_line = ExecutionTraceService._find_line_index_by_contains(normalized, "break;")
        v_next = ExecutionTraceService._find_line_index_by_contains(normalized, "v = v->sig;")
        if_not_exists_return = ExecutionTraceService._find_line_index_by_contains(normalized, "if (!existe) return null;")
        encolar_inicio = ExecutionTraceService._find_line_index_by_contains(normalized, "cola_encolar(&cola, inicio);")
        marcar_inicio = ExecutionTraceService._find_line_index_by_contains(normalized, "g = grafo_marcar_vertice(g, inicio);")
        while_cola = ExecutionTraceService._find_line_index_by_contains(normalized, "while (cola.delante != null)")
        actual_decl = ExecutionTraceService._find_line_index_by_contains(normalized, "int actual = cola_desencolar(&cola);")
        if_actual_minus = ExecutionTraceService._find_line_index_by_contains(normalized, "if (actual == -1)")
        tmp_decl = ExecutionTraceService._find_line_index_by_contains(normalized, "listavertice tmp = (listavertice) malloc(sizeof(struct nodov));")
        if_tmp_null = ExecutionTraceService._find_line_index_by_contains(normalized, "if (tmp == null) continue;")
        tmp_dato = ExecutionTraceService._find_line_index_by_contains(normalized, "tmp->dato = actual;")
        tmp_mark = ExecutionTraceService._find_line_index_by_contains(normalized, "tmp->marcado = 0;")
        tmp_sig = ExecutionTraceService._find_line_index_by_contains(normalized, "tmp->sig = recorrido;")
        rec_set = ExecutionTraceService._find_line_index_by_contains(normalized, "recorrido = tmp;")
        suces_decl = ExecutionTraceService._find_line_index_by_contains(normalized, "listavertice suces = grafo_sucesores(g, actual);")
        while_suces = ExecutionTraceService._find_line_index_by_contains(normalized, "while (suces != null)")
        if_unmarked = ExecutionTraceService._find_line_index_by_contains(normalized, "if (!grafo_marcado_vertice(g, suces->dato))")
        encolar_suces = ExecutionTraceService._find_line_index_by_contains(normalized, "cola_encolar(&cola, suces->dato);")
        marcar_suces = ExecutionTraceService._find_line_index_by_contains(normalized, "g = grafo_marcar_vertice(g, suces->dato);")
        temp_decl = ExecutionTraceService._find_line_index_by_contains(normalized, "listavertice temp = suces;")
        suces_next = ExecutionTraceService._find_line_index_by_contains(normalized, "suces = suces->sig;")
        free_temp = ExecutionTraceService._find_line_index_by_contains(normalized, "free(temp);")
        return_rec = ExecutionTraceService._find_line_index_by_contains(normalized, "return recorrido;")

        required = [
            header,
            desmarcar,
            cola_decl,
            rec_decl,
            while_v,
            if_not_exists_return,
            while_cola,
            actual_decl,
            if_actual_minus,
            tmp_decl,
            while_suces,
            return_rec,
        ]
        if any(i < 0 for i in required):
            return None

        out: list[int] = []
        def _a(idx: int) -> None:
            if idx >= 0:
                out.append(idx)

        result_wrapper = after_state.get("last_result") if isinstance(after_state, dict) else None
        result = result_wrapper.get("result") if isinstance(result_wrapper, dict) else None
        path = [str(item) for item in result] if isinstance(result, list) else []
        node_ids = [str(node.get("id")) for node in after_state.get("nodes", []) if isinstance(node, dict)]
        adjacency = ExecutionTraceService._graph_adjacency_from_state(after_state)
        start = str(payload.get("start", "")).strip()
        exists = bool(path) and success
        if not start and path:
            start = path[0]
        if not exists and start:
            exists = start in node_ids

        _a(header)
        _a(desmarcar)
        _a(cola_decl)
        _a(rec_decl)
        _a(v_decl)
        _a(existe_decl)

        # Busqueda lineal del vertice inicial en g.v (while + if + break)
        search_iters = 1
        if node_ids and start:
            try:
                search_iters = max(1, node_ids.index(start) + 1)
            except ValueError:
                search_iters = max(1, len(node_ids))
        for i in range(max(1, min(search_iters, 60))):
            _a(while_v)
            _a(if_v_eq)
            if start and i == search_iters - 1 and exists:
                _a(set_existe)
                _a(break_line)
                break
            _a(v_next)
        _a(while_v)
        _a(if_not_exists_return)

        if not exists:
            return ExecutionTraceService._limit_step_indexes(out)

        _a(encolar_inicio)
        _a(marcar_inicio)

        visit_count = max(1, len(path))
        for node in path:
            _a(while_cola)
            _a(actual_decl)
            _a(if_actual_minus)
            _a(tmp_decl)
            _a(if_tmp_null)
            _a(tmp_dato)
            _a(tmp_mark)
            _a(tmp_sig)
            _a(rec_set)
            _a(suces_decl)

            neighbors = adjacency.get(node, [])
            if not neighbors:
                _a(while_suces)
                continue

            for _ in neighbors:
                _a(while_suces)
                _a(if_unmarked)
                _a(encolar_suces)
                _a(marcar_suces)
                _a(temp_decl)
                _a(suces_next)
                _a(free_temp)
            _a(while_suces)

        _a(while_cola)
        _a(return_rec)
        return ExecutionTraceService._limit_step_indexes(out)

    @staticmethod
    def _expand_graph_bellman_ford_indexes(
        *,
        lines: list[str],
        after_state: dict[str, Any],
        success: bool,
        message: str,
    ) -> list[int] | None:
        normalized = [ExecutionTraceService._normalized_line_text(line) for line in lines]

        header = ExecutionTraceService._find_line_index_by_contains(normalized, "listaarco grafo_bellman_ford(")
        guard_n = ExecutionTraceService._find_line_index_by_contains(normalized, "if (n <= 0)")
        return_null = ExecutionTraceService._find_line_index_by_contains(normalized, "return null;")
        alloc_dist = ExecutionTraceService._find_line_index_by_contains(normalized, "dist = malloc(sizeof(int) * n);")
        alloc_guard = ExecutionTraceService._find_line_index_by_contains(normalized, "if (dist == null || prev == null || vertices == null)")
        init_vertices_guard = ExecutionTraceService._find_line_index_by_contains(normalized, "if (!inicializarvectorvertices(g, vertices, n))")
        init_loop = ExecutionTraceService._find_line_index_by_contains(normalized, "for (i = 0; i < n; i++)")
        init_dist = ExecutionTraceService._find_line_index_by_contains(normalized, "dist[i] = int_max;")
        init_prev = ExecutionTraceService._find_line_index_by_contains(normalized, "prev[i] = -1;")
        idx_inicio = ExecutionTraceService._find_line_index_by_contains(normalized, "idx_inicio = indicevertice(vertices, n, inicio);")
        idx_llegada = ExecutionTraceService._find_line_index_by_contains(normalized, "idx_llegada = indicevertice(vertices, n, llegada);")
        idx_guard = ExecutionTraceService._find_line_index_by_contains(normalized, "if (idx_inicio == -1 || idx_llegada == -1)")
        dist_start = ExecutionTraceService._find_line_index_by_contains(normalized, "dist[idx_inicio] = 0;")
        pass_loop = ExecutionTraceService._find_line_index_by_contains(normalized, "for (i = 0; i < n - 1; i++)")
        a_decl = ExecutionTraceService._find_line_index_by_contains(normalized, "listaarco a = grafo_arcos(g);")
        while_a = ExecutionTraceService._find_line_index_by_contains(normalized, "while (a != null)")
        idx_u = ExecutionTraceService._find_line_index_by_contains(normalized, "int u = indicevertice(vertices, n, a->origen);")
        idx_v = ExecutionTraceService._find_line_index_by_contains(normalized, "int v = indicevertice(vertices, n, a->destino);")
        if_uv = ExecutionTraceService._find_line_index_by_contains(normalized, "if (u != -1 && v != -1 && dist[u] != int_max)")
        cand_decl = ExecutionTraceService._find_line_index_by_contains(normalized, "long long cand = (long long)dist[u] + (long long)a->costo;")
        if_relax = ExecutionTraceService._find_line_index_by_contains(normalized, "if (cand >= int_min && cand <= int_max && (int)cand < dist[v])")
        set_dist = ExecutionTraceService._find_line_index_by_contains(normalized, "dist[v] = (int)cand;")
        set_prev = ExecutionTraceService._find_line_index_by_contains(normalized, "prev[v] = u;")
        next_a = ExecutionTraceService._find_line_index_by_contains(normalized, "a = a->sig;")
        print_neg = ExecutionTraceService._find_line_index_by_contains(normalized, "printf(\"se detecto un ciclo negativo.\\n\");")
        if_unreachable = ExecutionTraceService._find_line_index_by_contains(normalized, "if (dist[idx_llegada] == int_max)")
        while_prev = ExecutionTraceService._find_line_index_by_contains(normalized, "while (prev[destino] != -1)")
        new_arc = ExecutionTraceService._find_line_index_by_contains(normalized, "listaarco nuevo = malloc(sizeof(struct nodoa));")
        if_new_null = ExecutionTraceService._find_line_index_by_contains(normalized, "if (nuevo == null)")
        liberar_camino = ExecutionTraceService._find_line_index_by_contains(normalized, "liberarlistaarcos(camino);")
        set_camino_null = ExecutionTraceService._find_line_index_by_contains(normalized, "camino = null;")
        break_line = ExecutionTraceService._find_line_index_by_contains(normalized, "break;")
        set_origen = ExecutionTraceService._find_line_index_by_contains(normalized, "nuevo->origen = vertices[prev[destino]];")
        set_destino = ExecutionTraceService._find_line_index_by_contains(normalized, "nuevo->destino = vertices[destino];")
        set_costo = ExecutionTraceService._find_line_index_by_contains(normalized, "nuevo->costo = grafo_costo_arco(g, nuevo->origen, nuevo->destino);")
        set_sig = ExecutionTraceService._find_line_index_by_contains(normalized, "nuevo->sig = camino;")
        set_camino = ExecutionTraceService._find_line_index_by_contains(normalized, "camino = nuevo;")
        set_dest = ExecutionTraceService._find_line_index_by_contains(normalized, "destino = prev[destino];")
        free_dist = ExecutionTraceService._find_line_index_by_contains(normalized, "free(dist);")
        free_prev = ExecutionTraceService._find_line_index_by_contains(normalized, "free(prev);")
        free_vertices = ExecutionTraceService._find_line_index_by_contains(normalized, "free(vertices);")
        return_camino = ExecutionTraceService._find_line_index_by_contains(normalized, "return camino;")

        required = [header, guard_n, alloc_dist, alloc_guard, init_vertices_guard, idx_guard, pass_loop, while_a, if_uv, if_relax, return_camino]
        if any(i < 0 for i in required):
            return None

        out: list[int] = []
        def _a(idx: int) -> None:
            if idx >= 0:
                out.append(idx)

        result_wrapper = after_state.get("last_result") if isinstance(after_state, dict) else None
        result = result_wrapper.get("result") if isinstance(result_wrapper, dict) else None
        node_count = len(after_state.get("nodes")) if isinstance(after_state.get("nodes"), list) else 1
        edge_count = len(after_state.get("edges")) if isinstance(after_state.get("edges"), list) else 1
        has_negative_cycle = bool(result.get("has_negative_cycle", False)) if isinstance(result, dict) else False
        reachable = bool(result.get("reachable", False)) if isinstance(result, dict) else False
        path_edges = result.get("path_edges") if isinstance(result, dict) else []

        _a(header)
        _a(guard_n)
        _a(alloc_dist)
        _a(alloc_guard)
        _a(init_vertices_guard)

        _a(init_loop)
        init_iters = max(1, min(node_count, 20))
        for _ in range(init_iters):
            _a(init_dist)
            _a(init_prev)
        _a(init_loop)

        _a(idx_inicio)
        _a(idx_llegada)
        _a(idx_guard)
        _a(dist_start)

        passes = max(1, min(max(1, node_count - 1), 6))
        edge_iters = max(1, min(edge_count, 4))
        for _ in range(passes):
            _a(pass_loop)
            _a(a_decl)
            _a(while_a)
            for _ in range(edge_iters):
                _a(idx_u)
                _a(idx_v)
                _a(if_uv)
                _a(cand_decl)
                _a(if_relax)
                _a(set_dist)
                _a(set_prev)
                _a(next_a)
                _a(while_a)
        _a(pass_loop)

        # Verificacion de ciclo negativo
        _a(a_decl)
        _a(while_a)
        for _ in range(edge_iters):
            _a(idx_u)
            _a(idx_v)
            _a(if_uv)
            _a(cand_decl)
            _a(if_relax)
            if has_negative_cycle:
                _a(print_neg)
                _a(free_dist)
                _a(free_prev)
                _a(free_vertices)
                _a(return_null)
                return ExecutionTraceService._limit_step_indexes(out)
            _a(next_a)
            _a(while_a)

        _a(if_unreachable)
        if not reachable:
            _a(free_dist)
            _a(free_prev)
            _a(free_vertices)
            _a(return_null)
            return ExecutionTraceService._limit_step_indexes(out)

        _a(while_prev)
        path_len = len(path_edges) if isinstance(path_edges, list) else 0
        for _ in range(max(1, min(path_len, 40))):
            _a(new_arc)
            _a(if_new_null)
            if not success and "camino" in str(message or "").lower():
                _a(liberar_camino)
                _a(set_camino_null)
                _a(break_line)
                break
            _a(set_origen)
            _a(set_destino)
            _a(set_costo)
            _a(set_sig)
            _a(set_camino)
            _a(set_dest)
            _a(while_prev)

        _a(free_dist)
        _a(free_prev)
        _a(free_vertices)
        _a(return_camino)
        return ExecutionTraceService._limit_step_indexes(out)

    @staticmethod
    def _expand_recursive_graph_dfs_indexes(
        *,
        lines: list[str],
        before_state: dict[str, Any],
        after_state: dict[str, Any],
        payload: dict[str, Any],
        success: bool,
    ) -> list[int] | None:
        normalized_lines = [ExecutionTraceService._normalized_line_text(line) for line in lines]

        header_dfs = ExecutionTraceService._find_line_index_by_contains(
            normalized_lines, "listavertice grafo_dfs("
        )
        if_exists = ExecutionTraceService._find_line_index_by_contains(
            normalized_lines, "if (!grafo_existe_vertice(g, inicio))"
        )
        desmarcar = ExecutionTraceService._find_line_index_by_contains(
            normalized_lines, "g = grafo_desmarcar(g);"
        )
        recorrido_decl = ExecutionTraceService._find_line_index_by_contains(
            normalized_lines, "listavertice recorrido = null;"
        )
        dfs_call = ExecutionTraceService._find_line_index_by_contains(
            normalized_lines, "grafo_dfs_recursivo(g, inicio, &recorrido);"
        )
        return_recorrido = ExecutionTraceService._find_line_index_by_contains(
            normalized_lines, "return recorrido;"
        )
        return_null = ExecutionTraceService._find_line_index_by_contains(
            normalized_lines, "return null;"
        )

        header_rec = ExecutionTraceService._find_line_index_by_contains(
            normalized_lines, "void grafo_dfs_recursivo("
        )
        if_recorrido_null = ExecutionTraceService._find_line_index_by_contains(
            normalized_lines, "if (recorrido == null)"
        )
        mark_line = ExecutionTraceService._find_line_index_by_contains(
            normalized_lines, "g = grafo_marcar_vertice(g, actual);"
        )
        tmp_decl = ExecutionTraceService._find_line_index_by_contains(
            normalized_lines, "listavertice tmp = (listavertice) malloc"
        )
        if_tmp_null = ExecutionTraceService._find_line_index_by_contains(
            normalized_lines, "if (tmp == null) return;"
        )
        tmp_set_data = ExecutionTraceService._find_line_index_by_contains(
            normalized_lines, "tmp->dato = actual;"
        )
        tmp_set_mark = ExecutionTraceService._find_line_index_by_contains(
            normalized_lines, "tmp->marcado = 0;"
        )
        tmp_set_sig = ExecutionTraceService._find_line_index_by_contains(
            normalized_lines, "tmp->sig = *recorrido;"
        )
        set_recorrido = ExecutionTraceService._find_line_index_by_contains(
            normalized_lines, "*recorrido = tmp;"
        )
        suces_decl = ExecutionTraceService._find_line_index_by_contains(
            normalized_lines, "listavertice suces = grafo_sucesores(g, actual);"
        )
        while_suces = ExecutionTraceService._find_line_index_by_contains(
            normalized_lines, "while (suces)"
        )
        if_unmarked = ExecutionTraceService._find_line_index_by_contains(
            normalized_lines, "if (!grafo_marcado_vertice(g, suces->dato))"
        )
        recursive_call = ExecutionTraceService._find_line_index_by_contains(
            normalized_lines, "grafo_dfs_recursivo(g, suces->dato, recorrido);"
        )
        temp_decl = ExecutionTraceService._find_line_index_by_contains(
            normalized_lines, "listavertice temp = suces;"
        )
        suces_next = ExecutionTraceService._find_line_index_by_contains(
            normalized_lines, "suces = suces->sig;"
        )
        free_temp = ExecutionTraceService._find_line_index_by_contains(
            normalized_lines, "free(temp);"
        )

        required = [
            header_dfs,
            if_exists,
            desmarcar,
            recorrido_decl,
            dfs_call,
            return_recorrido,
            header_rec,
            mark_line,
            tmp_decl,
            suces_decl,
            while_suces,
            recursive_call,
        ]
        if any(idx < 0 for idx in required):
            return None

        expanded: list[int] = []

        def _append(idx: int) -> None:
            if idx >= 0:
                expanded.append(idx)

        # Wrapper grafo_dfs
        _append(header_dfs)
        _append(if_exists)
        if not success:
            _append(return_null)
            return ExecutionTraceService._limit_step_indexes(expanded)

        _append(desmarcar)
        _append(recorrido_decl)
        _append(dfs_call)

        result_wrapper = after_state.get("last_result") if isinstance(after_state, dict) else None
        result = result_wrapper.get("result") if isinstance(result_wrapper, dict) else None
        visit_order = [str(item) for item in result] if isinstance(result, list) else []
        if not visit_order:
            start = payload.get("start")
            if start is not None and str(start).strip():
                visit_order = [str(start)]

        adjacency = ExecutionTraceService._graph_adjacency_from_state(after_state)
        children_edges = ExecutionTraceService._derive_dfs_tree_edges(visit_order, adjacency)
        children_map: dict[str, list[str]] = {}
        for src, dst in children_edges:
            children_map.setdefault(src, []).append(dst)

        def walk(node_id: str) -> None:
            _append(header_rec)
            _append(if_recorrido_null)
            _append(mark_line)
            _append(tmp_decl)
            _append(if_tmp_null)
            _append(tmp_set_data)
            _append(tmp_set_mark)
            _append(tmp_set_sig)
            _append(set_recorrido)
            _append(suces_decl)

            child_nodes = children_map.get(node_id, [])
            if not child_nodes:
                _append(while_suces)
                return

            for child in child_nodes:
                _append(while_suces)
                _append(if_unmarked)
                _append(recursive_call)
                walk(child)
                _append(temp_decl)
                _append(suces_next)
                _append(free_temp)
            _append(while_suces)

        if visit_order:
            walk(visit_order[0])
        _append(return_recorrido)
        return ExecutionTraceService._limit_step_indexes(expanded)

    @staticmethod
    def _extract_tree_node_value(node: dict[str, Any] | None) -> Any:
        if not isinstance(node, dict):
            return None
        for key in ("value", "valor", "key", "nro"):
            if key in node:
                return node.get(key)
        return None

    @staticmethod
    def _tree_child(node: dict[str, Any] | None, side: str) -> dict[str, Any] | None:
        if not isinstance(node, dict):
            return None
        if side == "left":
            return node.get("left") if isinstance(node.get("left"), dict) else None
        return node.get("right") if isinstance(node.get("right"), dict) else None

    @staticmethod
    def _find_line_index_by_contains(normalized_lines: list[str], needle: str) -> int:
        normalized_needle = str(needle).strip().lower()
        for index, line in enumerate(normalized_lines):
            if normalized_needle in line:
                return index
        return -1

    @staticmethod
    def _expand_recursive_abb_insert_indexes(
        *,
        lines: list[str],
        before_state: dict[str, Any],
        payload: dict[str, Any],
        success: bool,
    ) -> list[int] | None:
        root = before_state.get("root")
        target = ExecutionTraceService._coerce_number(payload.get("value"))
        if target is None:
            return None

        normalized_lines = [ExecutionTraceService._normalized_line_text(line) for line in lines]
        header_line = ExecutionTraceService._find_line_index_by_contains(normalized_lines, "abbnodo* abb_insertar(")
        if_null_line = ExecutionTraceService._find_line_index_by_contains(normalized_lines, "if (nodo == null)")
        malloc_line = ExecutionTraceService._find_line_index_by_contains(normalized_lines, "abbnodo* nuevo = malloc")
        if_nuevo_null_line = ExecutionTraceService._find_line_index_by_contains(normalized_lines, "if (nuevo == null)")
        return_null_line = ExecutionTraceService._find_line_index_by_contains(normalized_lines, "return null;")
        set_value_line = ExecutionTraceService._find_line_index_by_contains(normalized_lines, "nuevo->valor = valor;")
        set_children_line = ExecutionTraceService._find_line_index_by_contains(normalized_lines, "nuevo->izquierdo = nuevo->derecho = null;")
        return_nuevo_line = ExecutionTraceService._find_line_index_by_contains(normalized_lines, "return nuevo;")
        if_less_line = ExecutionTraceService._find_line_index_by_contains(normalized_lines, "if (valor < nodo->valor)")
        left_recursive_line = ExecutionTraceService._find_line_index_by_contains(normalized_lines, "nodo->izquierdo = abb_insertar(nodo->izquierdo, valor);")
        else_if_greater_line = ExecutionTraceService._find_line_index_by_contains(normalized_lines, "else if (valor > nodo->valor)")
        right_recursive_line = ExecutionTraceService._find_line_index_by_contains(normalized_lines, "nodo->derecho = abb_insertar(nodo->derecho, valor);")
        return_nodo_line = ExecutionTraceService._find_line_index_by_contains(normalized_lines, "return nodo;")

        required = [
            header_line,
            if_null_line,
            if_less_line,
            left_recursive_line,
            else_if_greater_line,
            right_recursive_line,
            return_nodo_line,
        ]
        if any(index < 0 for index in required):
            return None
        if any(index < 0 for index in (malloc_line, if_nuevo_null_line, set_value_line, set_children_line, return_nuevo_line)):
            return None
        if not success and return_null_line < 0:
            return None

        expanded: list[int] = []

        def walk(node: dict[str, Any] | None) -> None:
            expanded.append(header_line)
            expanded.append(if_null_line)
            if not isinstance(node, dict):
                expanded.append(malloc_line)
                expanded.append(if_nuevo_null_line)
                # Cuando la operacion falla por memoria, esta rama hace return NULL.
                if not success and return_null_line >= 0:
                    expanded.append(return_null_line)
                    return
                expanded.append(set_value_line)
                expanded.append(set_children_line)
                expanded.append(return_nuevo_line)
                return

            node_value = ExecutionTraceService._coerce_number(
                ExecutionTraceService._extract_tree_node_value(node)
            )
            if node_value is None:
                expanded.append(return_nodo_line)
                return

            expanded.append(if_less_line)
            if target < node_value:
                expanded.append(left_recursive_line)
                walk(ExecutionTraceService._tree_child(node, "left"))
                expanded.append(return_nodo_line)
                return

            expanded.append(else_if_greater_line)
            if target > node_value:
                expanded.append(right_recursive_line)
                walk(ExecutionTraceService._tree_child(node, "right"))
            # Si es duplicado, se omite recursion y se retorna nodo.
            expanded.append(return_nodo_line)

        walk(root if isinstance(root, dict) else None)
        return ExecutionTraceService._limit_step_indexes(expanded)

    @staticmethod
    def _expand_recursive_abb_delete_indexes(
        *,
        lines: list[str],
        before_state: dict[str, Any],
        payload: dict[str, Any],
    ) -> list[int] | None:
        root = before_state.get("root")
        target = ExecutionTraceService._coerce_number(payload.get("value"))
        if target is None:
            return None

        normalized_lines = [ExecutionTraceService._normalized_line_text(line) for line in lines]
        header_line = ExecutionTraceService._find_line_index_by_contains(normalized_lines, "abbnodo* abb_eliminar(")
        null_guard_line = ExecutionTraceService._find_line_index_by_contains(normalized_lines, "if (nodo == null) return nodo;")
        if_less_line = ExecutionTraceService._find_line_index_by_contains(normalized_lines, "if (valor < nodo->valor)")
        left_recursive_line = ExecutionTraceService._find_line_index_by_contains(normalized_lines, "nodo->izquierdo = abb_eliminar(nodo->izquierdo, valor);")
        else_if_greater_line = ExecutionTraceService._find_line_index_by_contains(normalized_lines, "else if (valor > nodo->valor)")
        right_recursive_line = ExecutionTraceService._find_line_index_by_contains(normalized_lines, "nodo->derecho = abb_eliminar(nodo->derecho, valor);")
        if_left_null_line = ExecutionTraceService._find_line_index_by_contains(normalized_lines, "if (nodo->izquierdo == null)")
        temp_right_line = ExecutionTraceService._find_line_index_by_contains(normalized_lines, "abbnodo* temp = nodo->derecho;")
        else_if_right_null_line = ExecutionTraceService._find_line_index_by_contains(normalized_lines, "else if (nodo->derecho == null)")
        temp_left_line = ExecutionTraceService._find_line_index_by_contains(normalized_lines, "abbnodo* temp = nodo->izquierdo;")
        free_line = ExecutionTraceService._find_line_index_by_contains(normalized_lines, "free(nodo);")
        return_temp_line = ExecutionTraceService._find_line_index_by_contains(normalized_lines, "return temp;")
        min_line = ExecutionTraceService._find_line_index_by_contains(normalized_lines, "abbnodo* temp = abb_encontrarminimo(nodo->derecho);")
        copy_value_line = ExecutionTraceService._find_line_index_by_contains(normalized_lines, "nodo->valor = temp->valor;")
        delete_successor_line = ExecutionTraceService._find_line_index_by_contains(normalized_lines, "nodo->derecho = abb_eliminar(nodo->derecho, temp->valor);")
        return_nodo_line = ExecutionTraceService._find_line_index_by_contains(normalized_lines, "return nodo;")

        required = [
            header_line,
            null_guard_line,
            if_less_line,
            left_recursive_line,
            else_if_greater_line,
            right_recursive_line,
            return_nodo_line,
        ]
        if any(index < 0 for index in required):
            return None

        expanded: list[int] = []

        def walk(node: dict[str, Any] | None, delete_value: int | float) -> None:
            expanded.append(header_line)
            expanded.append(null_guard_line)
            if not isinstance(node, dict):
                return

            node_value = ExecutionTraceService._coerce_number(
                ExecutionTraceService._extract_tree_node_value(node)
            )
            if node_value is None:
                expanded.append(return_nodo_line)
                return

            expanded.append(if_less_line)
            if delete_value < node_value:
                expanded.append(left_recursive_line)
                walk(ExecutionTraceService._tree_child(node, "left"), delete_value)
                expanded.append(return_nodo_line)
                return

            expanded.append(else_if_greater_line)
            if delete_value > node_value:
                expanded.append(right_recursive_line)
                walk(ExecutionTraceService._tree_child(node, "right"), delete_value)
                expanded.append(return_nodo_line)
                return

            # Nodo encontrado: seguir la rama estructural correspondiente.
            left = ExecutionTraceService._tree_child(node, "left")
            right = ExecutionTraceService._tree_child(node, "right")
            if left is None and if_left_null_line >= 0:
                if temp_right_line >= 0:
                    expanded.append(if_left_null_line)
                    expanded.append(temp_right_line)
                    if free_line >= 0:
                        expanded.append(free_line)
                    if return_temp_line >= 0:
                        expanded.append(return_temp_line)
                return

            if right is None and else_if_right_null_line >= 0:
                if temp_left_line >= 0:
                    expanded.append(else_if_right_null_line)
                    expanded.append(temp_left_line)
                    if free_line >= 0:
                        expanded.append(free_line)
                    if return_temp_line >= 0:
                        expanded.append(return_temp_line)
                return

            if min_line >= 0 and copy_value_line >= 0 and delete_successor_line >= 0:
                expanded.append(min_line)
                expanded.append(copy_value_line)
                expanded.append(delete_successor_line)
                # Recurre para eliminar el sucesor en subárbol derecho.
                successor_value = delete_value
                current = right
                while isinstance(current, dict):
                    left_child = ExecutionTraceService._tree_child(current, "left")
                    if not isinstance(left_child, dict):
                        value = ExecutionTraceService._coerce_number(
                            ExecutionTraceService._extract_tree_node_value(current)
                        )
                        if value is not None:
                            successor_value = value
                        break
                    current = left_child
                walk(right, successor_value)
                expanded.append(return_nodo_line)
                return

            expanded.append(return_nodo_line)

        walk(root if isinstance(root, dict) else None, target)
        return ExecutionTraceService._limit_step_indexes(expanded)

    @staticmethod
    def _expand_avl_insert_indexes(
        *,
        lines: list[str],
        before_state: dict[str, Any],
        after_state: dict[str, Any],
        payload: dict[str, Any],
        success: bool,
    ) -> list[int] | None:
        target = ExecutionTraceService._coerce_number(payload.get("value"))
        if target is None:
            return None

        root = before_state.get("root")
        normalized_lines = [ExecutionTraceService._normalized_line_text(line) for line in lines]
        joined = "\n".join(normalized_lines)
        if "void avl_insertar(" not in joined:
            return None

        header = ExecutionTraceService._find_line_index_by_contains(normalized_lines, "void avl_insertar(")
        guard_raiz_null = ExecutionTraceService._find_line_index_by_contains(normalized_lines, "if (raiz == null)")
        return_line = ExecutionTraceService._find_line_index_by_contains(normalized_lines, "return;")
        init_line = ExecutionTraceService._find_line_index_by_contains(normalized_lines, "avl padre = null, actual = *raiz;")
        while_line = ExecutionTraceService._find_line_index_by_contains(normalized_lines, "while (actual != null)")
        set_padre_line = ExecutionTraceService._find_line_index_by_contains(normalized_lines, "padre = actual;")
        if_less_line = ExecutionTraceService._find_line_index_by_contains(normalized_lines, "if (x < actual->nro)")
        go_left_line = ExecutionTraceService._find_line_index_by_contains(normalized_lines, "actual = actual->izq;")
        else_if_greater_line = ExecutionTraceService._find_line_index_by_contains(normalized_lines, "else if (x > actual->nro)")
        go_right_line = ExecutionTraceService._find_line_index_by_contains(normalized_lines, "actual = actual->der;")
        else_return_dup_line = ExecutionTraceService._find_line_index_by_contains(normalized_lines, "return; // no duplicados")
        malloc_line = ExecutionTraceService._find_line_index_by_contains(normalized_lines, "avl nuevo = malloc(sizeof(*nuevo));")
        if_nuevo_null_line = ExecutionTraceService._find_line_index_by_contains(normalized_lines, "if (nuevo == null)")
        set_nro_line = ExecutionTraceService._find_line_index_by_contains(normalized_lines, "nuevo->nro = x;")
        set_fe_line = ExecutionTraceService._find_line_index_by_contains(normalized_lines, "nuevo->fe = 0;")
        set_children_line = ExecutionTraceService._find_line_index_by_contains(normalized_lines, "nuevo->izq = nuevo->der = null;")
        set_parent_line = ExecutionTraceService._find_line_index_by_contains(normalized_lines, "nuevo->padre = padre;")
        if_padre_null_line = ExecutionTraceService._find_line_index_by_contains(normalized_lines, "if (padre == null)")
        set_root_line = ExecutionTraceService._find_line_index_by_contains(normalized_lines, "*raiz = nuevo;")
        if_padre_less_line = ExecutionTraceService._find_line_index_by_contains(normalized_lines, "if (x < padre->nro)")
        assign_parent_left_line = ExecutionTraceService._find_line_index_by_contains(normalized_lines, "padre->izq = nuevo;")
        else_parent_right_line = ExecutionTraceService._find_line_index_by_contains(normalized_lines, "padre->der = nuevo;")
        rebalance_while_line = ExecutionTraceService._find_line_index_by_contains(normalized_lines, "while (padre != null)")
        update_fe_left_line = ExecutionTraceService._find_line_index_by_contains(normalized_lines, "if (n == padre->izq)")
        update_fe_left_apply_line = ExecutionTraceService._find_line_index_by_contains(normalized_lines, "padre->fe--;")
        update_fe_right_line = ExecutionTraceService._find_line_index_by_contains(normalized_lines, "padre->fe++;")
        if_fe_zero_break_line = ExecutionTraceService._find_line_index_by_contains(normalized_lines, "if (padre->fe == 0) break;")
        if_fe_neg2_line = ExecutionTraceService._find_line_index_by_contains(normalized_lines, "if (padre->fe == -2)")
        if_n_fe_le0_rsd_line = ExecutionTraceService._find_line_index_by_contains(normalized_lines, "if (n->fe <= 0)")
        call_rsd_line = ExecutionTraceService._find_line_index_by_contains(normalized_lines, "avl_rsd(raiz, padre);")
        else_rdd_line = ExecutionTraceService._find_line_index_by_contains(normalized_lines, "avl_rdd(raiz, padre);")
        if_fe_pos2_line = ExecutionTraceService._find_line_index_by_contains(normalized_lines, "if (padre->fe == 2)")
        if_n_fe_ge0_rsi_line = ExecutionTraceService._find_line_index_by_contains(normalized_lines, "if (n->fe >= 0)")
        call_rsi_line = ExecutionTraceService._find_line_index_by_contains(normalized_lines, "avl_rsi(raiz, padre);")
        else_rdi_line = ExecutionTraceService._find_line_index_by_contains(normalized_lines, "avl_rdi(raiz, padre);")
        n_equals_padre_line = ExecutionTraceService._find_line_index_by_contains(normalized_lines, "n = padre;")
        padre_up_line = ExecutionTraceService._find_line_index_by_contains(normalized_lines, "padre = padre->padre;")

        required = [
            header,
            guard_raiz_null,
            init_line,
            while_line,
            set_padre_line,
            if_less_line,
            else_if_greater_line,
            malloc_line,
            if_nuevo_null_line,
            set_nro_line,
            set_fe_line,
            set_children_line,
            set_parent_line,
            if_padre_null_line,
            set_root_line,
            if_padre_less_line,
            assign_parent_left_line,
            else_parent_right_line,
        ]
        if any(index < 0 for index in required):
            return None

        expanded: list[int] = [header, guard_raiz_null]
        if not isinstance(root, dict):
            expanded.extend([init_line, while_line, malloc_line, if_nuevo_null_line])
            if not success and return_line >= 0:
                expanded.append(return_line)
                return ExecutionTraceService._limit_step_indexes(expanded)
            expanded.extend(
                [
                    set_nro_line,
                    set_fe_line,
                    set_children_line,
                    set_parent_line,
                    if_padre_null_line,
                    set_root_line,
                ]
            )
            if return_line >= 0:
                expanded.append(return_line)
            return ExecutionTraceService._limit_step_indexes(expanded)

        expanded.append(init_line)
        current = root
        duplicate = False
        while isinstance(current, dict):
            expanded.append(while_line)
            expanded.append(set_padre_line)
            node_value = ExecutionTraceService._coerce_number(
                ExecutionTraceService._extract_tree_node_value(current)
            )
            if node_value is None:
                break

            if target < node_value:
                expanded.append(if_less_line)
                if go_left_line >= 0:
                    expanded.append(go_left_line)
                current = ExecutionTraceService._tree_child(current, "left")
                continue

            expanded.append(if_less_line)
            expanded.append(else_if_greater_line)
            if target > node_value:
                if go_right_line >= 0:
                    expanded.append(go_right_line)
                current = ExecutionTraceService._tree_child(current, "right")
                continue

            duplicate = True
            if else_return_dup_line >= 0:
                expanded.append(else_return_dup_line)
            elif return_line >= 0:
                expanded.append(return_line)
            break

        if duplicate:
            return ExecutionTraceService._limit_step_indexes(expanded)

        expanded.append(while_line)
        expanded.extend([malloc_line, if_nuevo_null_line])
        if not success and return_line >= 0:
            expanded.append(return_line)
            return ExecutionTraceService._limit_step_indexes(expanded)

        expanded.extend(
            [
                set_nro_line,
                set_fe_line,
                set_children_line,
                set_parent_line,
                if_padre_null_line,
            ]
        )

        parent = root
        while isinstance(parent, dict):
            value = ExecutionTraceService._coerce_number(
                ExecutionTraceService._extract_tree_node_value(parent)
            )
            if value is None:
                break
            if target < value:
                next_node = ExecutionTraceService._tree_child(parent, "left")
            elif target > value:
                next_node = ExecutionTraceService._tree_child(parent, "right")
            else:
                next_node = None
            if not isinstance(next_node, dict):
                break
            parent = next_node

        parent_value = ExecutionTraceService._coerce_number(
            ExecutionTraceService._extract_tree_node_value(parent)
        )
        if parent_value is not None and target < parent_value:
            expanded.append(if_padre_less_line)
            expanded.append(assign_parent_left_line)
        else:
            expanded.append(if_padre_less_line)
            expanded.append(else_parent_right_line)

        if rebalance_while_line >= 0:
            path = ExecutionTraceService._tree_path_keys_for_value(root if isinstance(root, dict) else None, target)
            rotation_hint = ExecutionTraceService._infer_real_avl_insert_rotation_hint(
                before_state=before_state,
                after_state=after_state,
                target_value=target,
            )

            expanded.append(rebalance_while_line)
            if update_fe_left_line >= 0:
                expanded.append(update_fe_left_line)
            if update_fe_left_apply_line >= 0:
                expanded.append(update_fe_left_apply_line)
            if update_fe_right_line >= 0:
                expanded.append(update_fe_right_line)
            if if_fe_zero_break_line >= 0:
                expanded.append(if_fe_zero_break_line)

            rotation_type = str((rotation_hint or {}).get("type", "")).upper()
            if rotation_type in {"LL", "LR"}:
                if if_fe_neg2_line >= 0:
                    expanded.append(if_fe_neg2_line)
                if rotation_type == "LL" and if_n_fe_le0_rsd_line >= 0:
                    expanded.append(if_n_fe_le0_rsd_line)
                    if call_rsd_line >= 0:
                        expanded.append(call_rsd_line)
                elif rotation_type == "LR":
                    if if_n_fe_le0_rsd_line >= 0:
                        expanded.append(if_n_fe_le0_rsd_line)
                    if else_rdd_line >= 0:
                        expanded.append(else_rdd_line)
            elif rotation_type in {"RR", "RL"}:
                if if_fe_pos2_line >= 0:
                    expanded.append(if_fe_pos2_line)
                if rotation_type == "RR" and if_n_fe_ge0_rsi_line >= 0:
                    expanded.append(if_n_fe_ge0_rsi_line)
                    if call_rsi_line >= 0:
                        expanded.append(call_rsi_line)
                elif rotation_type == "RL":
                    if if_n_fe_ge0_rsi_line >= 0:
                        expanded.append(if_n_fe_ge0_rsi_line)
                    if else_rdi_line >= 0:
                        expanded.append(else_rdi_line)
            else:
                if n_equals_padre_line >= 0:
                    expanded.append(n_equals_padre_line)
                if padre_up_line >= 0:
                    expanded.append(padre_up_line)
        return ExecutionTraceService._limit_step_indexes(expanded)

    @staticmethod
    def _expand_rbt_insert_indexes(
        *,
        lines: list[str],
        before_state: dict[str, Any],
        payload: dict[str, Any],
        success: bool,
    ) -> list[int] | None:
        target = ExecutionTraceService._coerce_number(payload.get("value"))
        if target is None:
            return None

        normalized_lines = [ExecutionTraceService._normalized_line_text(line) for line in lines]
        joined = "\n".join(normalized_lines)
        if "void rbt_insertar(" not in joined:
            return None

        def _idx(needle: str) -> int:
            return ExecutionTraceService._find_line_index_by_contains(normalized_lines, needle)

        def _next_return(after_index: int) -> int:
            for pos in range(max(0, after_index + 1), len(normalized_lines)):
                if normalized_lines[pos].startswith("return"):
                    return pos
            return -1

        header = _idx("void rbt_insertar(")
        if_arbol_null = _idx("if (arbol == null)")
        init_padre = _idx("rbt padre = null;")
        init_actual = _idx("rbt actual = *arbol;")
        while_line = _idx("while (actual != null && dato != actual->nro)")
        set_padre = _idx("padre = actual;")
        if_less = _idx("if (dato < actual->nro)")
        go_left = _idx("actual = actual->izq;")
        else_if_greater = _idx("else if (dato > actual->nro)")
        go_right = _idx("actual = actual->der;")
        if_actual_not_null = _idx("if (actual != null)")
        alloc_line = _idx("actual = malloc(sizeof(struct nodorbt));")
        if_alloc_null = _idx("if (actual == null)")
        set_value = _idx("actual->nro = dato;")
        set_children = _idx("actual->izq = actual->der = null;")
        set_parent = _idx("actual->padre = padre;")
        set_color = _idx("actual->rbt_color = rojo;")
        if_padre_null = _idx("if (padre == null)")
        set_root = _idx("*arbol = actual;")
        else_if_padre_left = _idx("else if (dato < padre->nro)")
        set_padre_left = _idx("padre->izq = actual;")
        else_if_padre_right = _idx("else if (dato > padre->nro)")
        set_padre_right = _idx("padre->der = actual;")
        fixup_call = _idx("rbt_insercion_caso1(actual, arbol);")
        printf_line = _idx("printf(")

        return_guard = _next_return(if_arbol_null)
        return_duplicate = _next_return(if_actual_not_null)
        return_alloc_fail = _next_return(if_alloc_null)

        required = [
            header,
            if_arbol_null,
            init_padre,
            init_actual,
            while_line,
            set_padre,
            if_less,
            go_left,
            else_if_greater,
            go_right,
            if_actual_not_null,
            alloc_line,
            if_alloc_null,
            set_value,
            set_children,
            set_parent,
            set_color,
            if_padre_null,
            set_root,
            else_if_padre_left,
            set_padre_left,
            else_if_padre_right,
            set_padre_right,
            fixup_call,
        ]
        if any(index < 0 for index in required):
            return None

        expanded: list[int] = [header, if_arbol_null]

        expanded.extend([init_padre, init_actual])
        current = before_state.get("root")
        duplicate = False
        while isinstance(current, dict):
            node_value = ExecutionTraceService._coerce_number(
                ExecutionTraceService._extract_tree_node_value(current)
            )
            expanded.append(while_line)
            if node_value is None:
                break
            if target == node_value:
                duplicate = True
                break
            expanded.append(set_padre)
            expanded.append(if_less)
            if target < node_value:
                expanded.append(go_left)
                current = ExecutionTraceService._tree_child(current, "left")
                continue
            expanded.append(else_if_greater)
            if target > node_value:
                expanded.append(go_right)
                current = ExecutionTraceService._tree_child(current, "right")
                continue
            break

        # Evaluacion final del while cuando la condicion ya es falsa.
        expanded.append(while_line)
        expanded.append(if_actual_not_null)
        if duplicate:
            if return_duplicate >= 0:
                expanded.append(return_duplicate)
            return ExecutionTraceService._limit_step_indexes(expanded)

        expanded.extend([alloc_line, if_alloc_null])
        if not success:
            if return_alloc_fail >= 0:
                expanded.append(return_alloc_fail)
            return ExecutionTraceService._limit_step_indexes(expanded)

        expanded.extend([set_value, set_children, set_parent, set_color, if_padre_null])
        if not isinstance(before_state.get("root"), dict):
            expanded.append(set_root)
        else:
            parent = before_state.get("root")
            while isinstance(parent, dict):
                value = ExecutionTraceService._coerce_number(
                    ExecutionTraceService._extract_tree_node_value(parent)
                )
                if value is None:
                    break
                if target < value:
                    nxt = ExecutionTraceService._tree_child(parent, "left")
                elif target > value:
                    nxt = ExecutionTraceService._tree_child(parent, "right")
                else:
                    nxt = None
                if not isinstance(nxt, dict):
                    break
                parent = nxt
            parent_value = ExecutionTraceService._coerce_number(
                ExecutionTraceService._extract_tree_node_value(parent if isinstance(parent, dict) else None)
            )
            if parent_value is not None and target < parent_value:
                expanded.extend([else_if_padre_left, set_padre_left])
            else:
                expanded.extend([else_if_padre_right, set_padre_right])

        expanded.append(fixup_call)

        # Expande la ejecucion de subrutinas RN (casos y rotaciones)
        # para una simulacion fiel del control de flujo llamado por insertar.
        class _RBNode:
            __slots__ = ("value", "color", "parent", "left", "right")

            def __init__(self, value: int, color: str = "BLACK") -> None:
                self.value = int(value)
                self.color = str(color or "BLACK").upper()
                self.parent: "_RBNode | None" = None
                self.left: "_RBNode | None" = None
                self.right: "_RBNode | None" = None

        def _build_model(node: dict[str, Any] | None, parent: _RBNode | None = None) -> _RBNode | None:
            if not isinstance(node, dict):
                return None
            value = ExecutionTraceService._coerce_number(node.get("value"))
            if value is None:
                return None
            current = _RBNode(int(value), str(node.get("color", "BLACK")))
            current.parent = parent
            current.left = _build_model(node.get("left") if isinstance(node.get("left"), dict) else None, current)
            current.right = _build_model(node.get("right") if isinstance(node.get("right"), dict) else None, current)
            return current

        def _grand(node: _RBNode | None) -> _RBNode | None:
            if node is None or node.parent is None:
                return None
            return node.parent.parent

        def _uncle(node: _RBNode | None) -> _RBNode | None:
            g = _grand(node)
            if g is None or node is None or node.parent is None:
                return None
            return g.right if node.parent is g.left else g.left

        def _rot_left(root_ref: list[_RBNode | None], x: _RBNode | None) -> None:
            if x is None or x.right is None:
                return
            p = x.parent
            b = x.right
            c = b.left
            if p is not None:
                if p.right is x:
                    p.right = b
                else:
                    p.left = b
            else:
                root_ref[0] = b
            x.right = c
            b.left = x
            x.parent = b
            if c is not None:
                c.parent = x
            b.parent = p

        def _rot_right(root_ref: list[_RBNode | None], x: _RBNode | None) -> None:
            if x is None or x.left is None:
                return
            p = x.parent
            b = x.left
            c = b.right
            if p is not None:
                if p.right is x:
                    p.right = b
                else:
                    p.left = b
            else:
                root_ref[0] = b
            x.left = c
            b.right = x
            x.parent = b
            if c is not None:
                c.parent = x
            b.parent = p

        def _idx(needle: str) -> int:
            return ExecutionTraceService._find_line_index_by_contains(normalized_lines, needle)

        def _append(index: int) -> None:
            if index >= 0:
                expanded.append(index)

        case1_header = _idx("void rbt_insercion_caso1(")
        case1_if_parent_null = _idx("if (n->padre == null)")
        case1_set_black = _idx("n->rbt_color = negro;")
        case1_call_case2 = _idx("rbt_insercion_caso2(n, arbol);")

        case2_header = _idx("void rbt_insercion_caso2(")
        case2_if_parent_black = _idx("if (n->padre->rbt_color == negro)")
        case2_return = _next_return(case2_if_parent_black)
        case2_call_case3 = _idx("rbt_insercion_caso3(n, arbol);")

        case3_header = _idx("void rbt_insercion_caso3(")
        case3_t_assign = _idx("rbt t = rbt_tio(n);")
        case3_if_uncle_red = _idx("if ((t != null) && (t->rbt_color == rojo))")
        case3_parent_black = _idx("n->padre->rbt_color = negro;")
        case3_uncle_black = _idx("t->rbt_color = negro;")
        case3_a_assign = _idx("a = rbt_abuelo(n);")
        case3_a_red = _idx("a->rbt_color = rojo;")
        case3_call_case1a = _idx("rbt_insercion_caso1(a, arbol);")
        case3_call_case4 = _idx("rbt_insercion_caso4(n, arbol);")

        case4_header = _idx("void rbt_insercion_caso4(")
        case4_a_assign = _idx("rbt a = rbt_abuelo(n);")
        case4_nuevo_assign = _idx("rbt nuevo_n = n;")
        case4_if_lr = _idx("if ((n == n->padre->der) && (n->padre == a->izq))")
        case4_else_if_rl = _idx("else if ((n == n->padre->izq) && (n->padre == a->der))")
        case4_rot_left_parent = _idx("rbt_rotar_izda(arbol, n->padre);")
        case4_set_nuevo_left = _idx("nuevo_n = n->izq;")
        case4_rot_right_parent = _idx("rbt_rotar_dcha(arbol, n->padre);")
        case4_set_nuevo_right = _idx("nuevo_n = n->der;")
        case4_call_case5 = _idx("rbt_insercion_caso5(nuevo_n, arbol);")

        case5_header = _idx("void rbt_insercion_caso5(")
        case5_a_assign = _idx("rbt a = rbt_abuelo(n);")
        case5_parent_black = _idx("n->padre->rbt_color = negro;")
        case5_a_red = _idx("a->rbt_color = rojo;")
        case5_if_ll = _idx("if ((n == n->padre->izq) && (n->padre == a->izq))")
        case5_rot_right_a = _idx("rbt_rotar_dcha(arbol, a);")
        case5_rot_left_a = _idx("rbt_rotar_izda(arbol, a);")

        rot_left_header = _idx("void rbt_rotar_izda(")
        rot_left_guard = _idx("if (r == null || nodorbt == null || nodorbt->der == null)")
        rot_left_core_a = _idx("a->der = c;")
        rot_left_core_b = _idx("b->izq = a;")
        rot_left_core_c = _idx("a->padre = b;")
        rot_left_core_d = _idx("b->padre = padre;")

        rot_right_header = _idx("void rbt_rotar_dcha(")
        rot_right_guard = _idx("if (r == null || nodorbt == null || nodorbt->izq == null)")
        rot_right_core_a = _idx("a->izq = c;")
        rot_right_core_b = _idx("b->der = a;")
        rot_right_core_c = _idx("a->padre = b;")
        rot_right_core_d = _idx("b->padre = padre;")

        root_model = _build_model(before_state.get("root") if isinstance(before_state.get("root"), dict) else None)
        root_ref_model: list[_RBNode | None] = [root_model]
        current_model = root_model
        parent_model: _RBNode | None = None
        duplicate_model = False
        while current_model is not None:
            parent_model = current_model
            if target < current_model.value:
                current_model = current_model.left
            elif target > current_model.value:
                current_model = current_model.right
            else:
                duplicate_model = True
                break

        if not duplicate_model:
            inserted = _RBNode(int(target), "RED")
            inserted.parent = parent_model
            if parent_model is None:
                root_ref_model[0] = inserted
            elif target < parent_model.value:
                parent_model.left = inserted
            else:
                parent_model.right = inserted

            def _trace_rot_left() -> None:
                _append(rot_left_header)
                _append(rot_left_guard)
                _append(rot_left_core_a)
                _append(rot_left_core_b)
                _append(rot_left_core_c)
                _append(rot_left_core_d)

            def _trace_rot_right() -> None:
                _append(rot_right_header)
                _append(rot_right_guard)
                _append(rot_right_core_a)
                _append(rot_right_core_b)
                _append(rot_right_core_c)
                _append(rot_right_core_d)

            def _case1(n: _RBNode | None) -> None:
                if n is None:
                    return
                _append(case1_header)
                _append(case1_if_parent_null)
                if n.parent is None:
                    _append(case1_set_black)
                    n.color = "BLACK"
                    return
                _append(case1_call_case2)
                _case2(n)

            def _case2(n: _RBNode | None) -> None:
                if n is None or n.parent is None:
                    return
                _append(case2_header)
                _append(case2_if_parent_black)
                if n.parent.color == "BLACK":
                    _append(case2_return)
                    return
                _append(case2_call_case3)
                _case3(n)

            def _case3(n: _RBNode | None) -> None:
                if n is None or n.parent is None:
                    return
                _append(case3_header)
                _append(case3_t_assign)
                _append(case3_if_uncle_red)
                t = _uncle(n)
                if t is not None and t.color == "RED":
                    _append(case3_parent_black)
                    _append(case3_uncle_black)
                    _append(case3_a_assign)
                    a = _grand(n)
                    if a is None:
                        return
                    n.parent.color = "BLACK"
                    t.color = "BLACK"
                    _append(case3_a_red)
                    a.color = "RED"
                    _append(case3_call_case1a)
                    _case1(a)
                    return
                _append(case3_call_case4)
                _case4(n)

            def _case4(n: _RBNode | None) -> None:
                if n is None or n.parent is None:
                    return
                _append(case4_header)
                _append(case4_a_assign)
                _append(case4_nuevo_assign)
                a = _grand(n)
                if a is None:
                    return
                nuevo_n = n
                _append(case4_if_lr)
                if n is n.parent.right and n.parent is a.left:
                    _append(case4_rot_left_parent)
                    _trace_rot_left()
                    _rot_left(root_ref_model, n.parent)
                    if n.left is not None:
                        _append(case4_set_nuevo_left)
                        nuevo_n = n.left
                else:
                    _append(case4_else_if_rl)
                    if n is n.parent.left and n.parent is a.right:
                        _append(case4_rot_right_parent)
                        _trace_rot_right()
                        _rot_right(root_ref_model, n.parent)
                        if n.right is not None:
                            _append(case4_set_nuevo_right)
                            nuevo_n = n.right
                _append(case4_call_case5)
                _case5(nuevo_n)

            def _case5(n: _RBNode | None) -> None:
                if n is None or n.parent is None:
                    return
                a = _grand(n)
                if a is None:
                    return
                _append(case5_header)
                _append(case5_a_assign)
                _append(case5_parent_black)
                n.parent.color = "BLACK"
                _append(case5_a_red)
                a.color = "RED"
                _append(case5_if_ll)
                if n is n.parent.left and n.parent is a.left:
                    _append(case5_rot_right_a)
                    _trace_rot_right()
                    _rot_right(root_ref_model, a)
                else:
                    _append(case5_rot_left_a)
                    _trace_rot_left()
                    _rot_left(root_ref_model, a)

            _case1(inserted)

        if printf_line >= 0:
            expanded.append(printf_line)
        return ExecutionTraceService._limit_step_indexes(expanded)

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

    @staticmethod
    def _expand_tree_extreme_indexes(
        *,
        operation_name: str,
        lines: list[str],
        before_state: dict[str, Any],
        after_state: dict[str, Any],
    ) -> list[int] | None:
        if operation_name not in {"minimo", "maximo"}:
            return None

        root = before_state.get("root")
        if not isinstance(root, dict):
            root = after_state.get("root")
        if not isinstance(root, dict):
            return None

        side = "left" if operation_name == "minimo" else "right"
        path = ExecutionTraceService._tree_path_keys_to_extreme(root, side)
        if not path:
            return None

        normalized_lines = [ExecutionTraceService._normalized_line_text(line) for line in lines]
        header_line = -1
        if operation_name == "minimo":
            for needle in ("avl avl_minimo(", "abbnodo* abb_encontrarminimo(", "abbnodo *abb_encontrarminimo("):
                header_line = ExecutionTraceService._find_line_index_by_contains(normalized_lines, needle)
                if header_line >= 0:
                    break
        else:
            for needle in ("abbnodo* abb_encontrarmaximo(", "abbnodo *abb_encontrarmaximo(", "avl aux = raiz;"):
                header_line = ExecutionTraceService._find_line_index_by_contains(normalized_lines, needle)
                if header_line >= 0:
                    break
        while_line = -1
        for needle in (
            "while (nodo->izquierdo != null)" if side == "left" else "while (nodo != null && nodo->derecho != null)",
            "while (nodo != null && nodo->izquierdo != null)" if side == "left" else "while (nodo->derecho != null)",
            "while (nodo->izq != null)" if side == "left" else "while (nodo->der != null)",
            "while (nodo->izq)" if side == "left" else "while (nodo->der)",
            "while (aux != null && aux->izq != null)" if side == "left" else "while (aux != null && aux->der != null)",
            "while (actual != null && actual->izquierdo != null)" if side == "left" else "while (actual != null && actual->derecho != null)",
        ):
            while_line = ExecutionTraceService._find_line_index_by_contains(normalized_lines, needle)
            if while_line >= 0:
                break
        move_line = -1
        for needle in (
            "nodo = nodo->izq;" if side == "left" else "nodo = nodo->derecho;",
            "nodo = nodo->izquierdo;" if side == "left" else "nodo = nodo->der;",
            "aux = aux->izq;" if side == "left" else "aux = aux->der;",
            "actual = actual->izquierdo;" if side == "left" else "actual = actual->derecho;",
        ):
            move_line = ExecutionTraceService._find_line_index_by_contains(normalized_lines, needle)
            if move_line >= 0:
                break
        return_line = -1
        for needle in ("return nodo;", "return actual;", "return aux;"):
            return_line = ExecutionTraceService._find_line_index_by_contains(normalized_lines, needle)
            if return_line >= 0:
                break
        null_guard_line = -1
        for needle in ("if (nodo == null)", "if (actual == null)", "if (aux == null)"):
            null_guard_line = ExecutionTraceService._find_line_index_by_contains(normalized_lines, needle)
            if null_guard_line >= 0:
                break

        required = [while_line, move_line, return_line]
        if any(index < 0 for index in required):
            return None

        expanded: list[int] = []
        if header_line >= 0:
            expanded.append(header_line)
        if null_guard_line >= 0:
            expanded.append(null_guard_line)
        for index, _key in enumerate(path):
            expanded.append(while_line)
            if index < len(path) - 1:
                expanded.append(move_line)
        expanded.append(return_line)
        return ExecutionTraceService._limit_step_indexes(expanded)

    @staticmethod
    def _expand_recursive_bst_traversal_indexes(
        *,
        operation_name: str,
        lines: list[str],
        before_state: dict[str, Any],
        after_state: dict[str, Any],
    ) -> list[int] | None:
        if operation_name not in {"inorden", "preorden", "postorden"}:
            return None

        root = after_state.get("root")
        if not isinstance(root, dict):
            root = before_state.get("root")
        if not isinstance(root, dict):
            return None

        function_name = ""
        normalized_lines = [ExecutionTraceService._normalized_line_text(line) for line in lines]

        func_line = -1
        if_line = -1
        left_call_line = -1
        right_call_line = -1
        visit_line = -1

        for index, normalized in enumerate(normalized_lines):
            if func_line < 0 and f"_{operation_name}(" in normalized and ("void " in normalized or "int " in normalized):
                func_line = index
                signature = str(lines[index]).strip()
                before_paren = signature.split("(", 1)[0].strip()
                function_name = before_paren.split()[-1] if before_paren else ""
                continue

        if function_name:
            fn_norm = ExecutionTraceService._normalized_line_text(function_name)
            for index, normalized in enumerate(normalized_lines):
                if if_line < 0 and normalized.startswith("if ") and ("== null" in normalized or "!= null" in normalized):
                    if_line = index
                    continue
                if left_call_line < 0 and f"{fn_norm}(" in normalized and any(token in normalized for token in ("->izquierdo", "->izq", "->rbt_izq")):
                    left_call_line = index
                    continue
                if right_call_line < 0 and f"{fn_norm}(" in normalized and any(token in normalized for token in ("->derecho", "->der", "->rbt_der")):
                    right_call_line = index
                    continue
                if visit_line < 0 and "printf(" in normalized and ("->valor" in normalized or "->nro" in normalized or "->rbt_dato" in normalized):
                    visit_line = index

        required = [func_line, if_line, left_call_line, right_call_line, visit_line]
        if any(index < 0 for index in required):
            return None

        expanded: list[int] = []

        def walk(node: dict[str, Any] | None) -> None:
            expanded.append(func_line)
            expanded.append(if_line)
            if not isinstance(node, dict):
                return

            if operation_name == "preorden":
                expanded.append(visit_line)

            expanded.append(left_call_line)
            walk(ExecutionTraceService._tree_child(node, "left"))

            if operation_name == "inorden":
                expanded.append(visit_line)

            expanded.append(right_call_line)
            walk(ExecutionTraceService._tree_child(node, "right"))

            if operation_name == "postorden":
                expanded.append(visit_line)

        walk(root)
        return ExecutionTraceService._limit_step_indexes(expanded)

    @staticmethod
    def _expand_recursive_tree_metrics_indexes(
        *,
        operation_name: str,
        lines: list[str],
        before_state: dict[str, Any],
        after_state: dict[str, Any],
    ) -> list[int] | None:
        if operation_name not in {"altura", "contar_hojas", "validar"}:
            return None

        root = after_state.get("root")
        if not isinstance(root, dict):
            root = before_state.get("root")
        if not isinstance(root, dict):
            return None

        normalized_lines = [ExecutionTraceService._normalized_line_text(line) for line in lines]
        func_line = -1
        if_null_line = -1
        return_zero_line = -1
        return_one_line = -1
        left_call_line = -1
        right_call_line = -1
        final_return_line = -1
        leaf_if_line = -1
        invalid_if_line = -1

        function_name = ""
        for index, normalized in enumerate(normalized_lines):
            if func_line < 0 and "(" in normalized and ("int " in normalized or "bool " in normalized):
                if operation_name == "altura" and "_altura(" in normalized:
                    func_line = index
                elif operation_name == "contar_hojas" and "contarhojas(" in normalized:
                    func_line = index
                elif operation_name == "validar" and ("validar(" in normalized or "validar_fes(" in normalized or "validar_" in normalized):
                    func_line = index
                if func_line >= 0:
                    signature = str(lines[index]).strip()
                    before_paren = signature.split("(", 1)[0].strip()
                    function_name = before_paren.split()[-1] if before_paren else ""
                    continue

        if func_line < 0:
            return None

        fn_norm = ExecutionTraceService._normalized_line_text(function_name) if function_name else ""
        for index, normalized in enumerate(normalized_lines):
            if if_null_line < 0 and normalized.startswith("if ") and "== null" in normalized:
                if_null_line = index
                continue
            if return_zero_line < 0 and normalized.startswith("return 0"):
                return_zero_line = index
                continue
            if return_one_line < 0 and normalized.startswith("return 1"):
                return_one_line = index
                continue
            if leaf_if_line < 0 and operation_name == "contar_hojas" and "->izquierdo == null" in normalized and "->derecho == null" in normalized:
                leaf_if_line = index
                continue
            if invalid_if_line < 0 and operation_name == "validar" and normalized.startswith("if ") and ("< -1" in normalized or "> 1" in normalized or "!= negro" in normalized):
                invalid_if_line = index
                continue
            if fn_norm and f"{fn_norm}(" in normalized:
                if left_call_line < 0 and any(token in normalized for token in ("->izquierdo", "->izq", "->rbt_izq")):
                    left_call_line = index
                if right_call_line < 0 and any(token in normalized for token in ("->derecho", "->der", "->rbt_der")):
                    right_call_line = index

        for index in range(len(normalized_lines) - 1, -1, -1):
            normalized = normalized_lines[index]
            if normalized.startswith("return ") and not normalized.startswith("return 0") and not normalized.startswith("return 1"):
                final_return_line = index
                break

        if if_null_line < 0:
            return None
        if operation_name == "altura" and any(i < 0 for i in (left_call_line, right_call_line, final_return_line)):
            return None
        if operation_name == "contar_hojas" and any(i < 0 for i in (leaf_if_line, left_call_line, right_call_line)):
            return None
        if operation_name == "validar" and any(i < 0 for i in (left_call_line, right_call_line)):
            return None

        expanded: list[int] = []

        def walk(node: dict[str, Any] | None, is_root: bool = False) -> bool:
            expanded.append(func_line)
            expanded.append(if_null_line)
            if not isinstance(node, dict):
                if operation_name == "validar":
                    if return_one_line >= 0:
                        expanded.append(return_one_line)
                elif return_zero_line >= 0:
                    expanded.append(return_zero_line)
                return True

            if operation_name == "contar_hojas":
                expanded.append(leaf_if_line)
                left_is_node = isinstance(node.get("left"), dict)
                right_is_node = isinstance(node.get("right"), dict)
                if not left_is_node and not right_is_node:
                    if return_one_line >= 0:
                        expanded.append(return_one_line)
                    return True
                if final_return_line >= 0:
                    expanded.append(final_return_line)
                walk(node.get("left"))
                walk(node.get("right"))
                return True

            if operation_name == "validar":
                if invalid_if_line >= 0:
                    expanded.append(invalid_if_line)

                if if_null_line >= 0 and "validar_fes" in fn_norm:
                    bf = ExecutionTraceService._coerce_number(node.get("balance_factor"))
                    if bf is not None and (bf < -1 or bf > 1):
                        if return_zero_line >= 0:
                            expanded.append(return_zero_line)
                        return False

                if is_root and "rbt_validar" in fn_norm and str(node.get("color", "")).upper() != "BLACK":
                    if return_zero_line >= 0:
                        expanded.append(return_zero_line)
                    return False

                expanded.append(left_call_line)
                if not walk(node.get("left")):
                    if return_zero_line >= 0:
                        expanded.append(return_zero_line)
                    return False

                expanded.append(right_call_line)
                if not walk(node.get("right")):
                    if return_zero_line >= 0:
                        expanded.append(return_zero_line)
                    return False

                if return_one_line >= 0:
                    expanded.append(return_one_line)
                elif final_return_line >= 0:
                    expanded.append(final_return_line)
                return True

            # altura
            expanded.append(left_call_line)
            walk(node.get("left"))
            expanded.append(right_call_line)
            walk(node.get("right"))
            if final_return_line >= 0:
                expanded.append(final_return_line)
            return True

        walk(root, is_root=True)
        return ExecutionTraceService._limit_step_indexes(expanded)

    @staticmethod
    def _expand_recursive_tree_clear_indexes(
        *,
        lines: list[str],
        before_state: dict[str, Any],
        after_state: dict[str, Any],
    ) -> list[int] | None:
        root = before_state.get("root")
        if not isinstance(root, dict):
            root = after_state.get("root")
        normalized_lines = [ExecutionTraceService._normalized_line_text(line) for line in lines]

        func_line = -1
        function_name = ""
        for index, normalized in enumerate(normalized_lines):
            if "void " in normalized and "liberar" in normalized and "(" in normalized:
                func_line = index
                signature = str(lines[index]).strip()
                before_paren = signature.split("(", 1)[0].strip()
                function_name = before_paren.split()[-1] if before_paren else ""
                break
        if func_line < 0 or not function_name:
            return None

        fn_norm = ExecutionTraceService._normalized_line_text(function_name)
        if_null_line = -1
        return_line = -1
        left_call_line = -1
        right_call_line = -1
        free_line = -1

        for index, normalized in enumerate(normalized_lines):
            if if_null_line < 0 and normalized.startswith("if ") and (" null" in normalized or "== null" in normalized or "!" in normalized):
                if_null_line = index
                continue
            if return_line < 0 and normalized.startswith("return"):
                return_line = index
                continue
            if free_line < 0 and "free(" in normalized:
                free_line = index
                continue
            if fn_norm and f"{fn_norm}(" in normalized:
                if left_call_line < 0 and any(token in normalized for token in ("->izquierdo", "->izq", "->rbt_izq")):
                    left_call_line = index
                if right_call_line < 0 and any(token in normalized for token in ("->derecho", "->der", "->rbt_der")):
                    right_call_line = index

        if any(index < 0 for index in (if_null_line, left_call_line, right_call_line, free_line)):
            return None

        expanded: list[int] = []

        def walk(node: dict[str, Any] | None) -> None:
            expanded.append(func_line)
            expanded.append(if_null_line)
            if not isinstance(node, dict):
                if return_line >= 0:
                    expanded.append(return_line)
                return
            expanded.append(left_call_line)
            walk(ExecutionTraceService._tree_child(node, "left"))
            expanded.append(right_call_line)
            walk(ExecutionTraceService._tree_child(node, "right"))
            expanded.append(free_line)

        walk(root if isinstance(root, dict) else None)
        return ExecutionTraceService._limit_step_indexes(expanded)

    @staticmethod
    def _build_boundaries(
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
        if not mutates or before_state == after_state:
            states = [deepcopy(before_state) for _ in range(boundaries)]
            states[-1] = deepcopy(after_state)
            return states

        state_kind = ExecutionTraceService._state_kind(after_state)
        if state_kind in {"linear", "circular", "sublist"}:
            return ExecutionTraceService._build_linear_boundaries(before_state, after_state, total_steps, step_lines)
        if state_kind == "heap":
            return ExecutionTraceService._build_heap_boundaries(before_state, after_state, total_steps, step_lines)
        if state_kind == "binary_tree":
            return ExecutionTraceService._build_tree_debug_boundaries(
                before_state,
                after_state,
                total_steps,
                operation_name,
                payload,
                step_lines,
            )
        if state_kind == "graph":
            return ExecutionTraceService._build_graph_boundaries(before_state, after_state, total_steps, step_lines)
        if state_kind == "hash_table":
            return ExecutionTraceService._build_hash_boundaries(before_state, after_state, total_steps, step_lines)

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
    ) -> dict[str, Any]:
        """Build one execution trace consumable by frontend animation runtimes."""
        source_code, code_title = ExecutionTraceService._get_operation_source(
            didactic_data=didactic_data,
            operation_name=operation_name,
        )
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
        if recursive_tree_indexes is not None:
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
            before_state=before_state,
            after_state=after_state,
            total_steps=total_steps,
            mutates=bool(mutates and success),
            operation_name=operation_name,
            payload=payload,
            step_lines=step_lines,
        )
        if state_kind == "binary_tree":
            debug_steps = ExecutionTraceService._build_tree_debug_steps(
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

        return {
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
