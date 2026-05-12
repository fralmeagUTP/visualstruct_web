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
        if text.startswith("//") or text.startswith("/*") or text.startswith("*") or text.startswith("*/"):
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
    def _filter_trace_lines_for_success(lines: list[str], executable_indexes: list[int], success: bool) -> list[int]:
        if not success:
            return executable_indexes
        keep = set(executable_indexes)
        ordered = sorted(executable_indexes)
        index_pos = 0
        while index_pos < len(ordered):
            line_index = ordered[index_pos]
            line_text = str(lines[line_index]).strip()
            if not ExecutionTraceService._is_defensive_null_if(line_text):
                index_pos += 1
                continue

            open_line_index = line_index if "{" in line_text else ExecutionTraceService._next_nonempty_line_index(lines, line_index + 1)
            if open_line_index < 0:
                index_pos += 1
                continue
            close_line_index = ExecutionTraceService._find_matching_brace_line(lines, open_line_index)
            if close_line_index < 0:
                index_pos += 1
                continue

            has_false_return = False
            for inner in range(open_line_index + 1, close_line_index + 1):
                inner_text = str(lines[inner]).strip().lower()
                if inner_text.startswith("return false"):
                    has_false_return = True
                    break
            if not has_false_return:
                index_pos += 1
                continue

            for inner in range(open_line_index + 1, close_line_index + 1):
                keep.discard(inner)
            index_pos += 1

        filtered = [index for index in executable_indexes if index in keep]
        return filtered if filtered else executable_indexes

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
    ) -> list[dict[str, Any]]:
        boundaries = total_steps + 1
        before_root = before_state.get("root")
        after_root = after_state.get("root")
        if not isinstance(before_root, dict) and before_root is not None:
            before_root = None
        if not isinstance(after_root, dict) and after_root is not None:
            after_root = None

        target_value = payload.get("value")
        value_before = set(ExecutionTraceService._collect_tree_values(before_root))
        value_after = set(ExecutionTraceService._collect_tree_values(after_root))

        keyframes: list[dict[str, Any]] = [deepcopy(before_state)]

        if operation_name == "insertar":
            inserted_values = list(value_after - value_before)
            if inserted_values:
                inserted_value = inserted_values[0]
                template_source = ExecutionTraceService._find_tree_node_by_value(after_root, inserted_value)
                template_node = ExecutionTraceService._minimal_tree_node_template(template_source, inserted_value)
                transitional = deepcopy(before_state)
                transitional["root"] = ExecutionTraceService._bst_insert_visual(
                    deepcopy(before_root) if isinstance(before_root, dict) else None,
                    inserted_value,
                    template_node,
                )
                transitional["size"] = len(ExecutionTraceService._collect_tree_values(transitional["root"]))
                transitional["empty"] = transitional["root"] is None
                keyframes.append(transitional)
        elif operation_name == "eliminar":
            removed_values = list(value_before - value_after)
            remove_target = removed_values[0] if removed_values else target_value
            if remove_target is not None:
                transitional = deepcopy(before_state)
                transitional["root"] = ExecutionTraceService._bst_delete_visual(
                    deepcopy(before_root) if isinstance(before_root, dict) else None,
                    remove_target,
                )
                transitional["size"] = len(ExecutionTraceService._collect_tree_values(transitional["root"]))
                transitional["empty"] = transitional["root"] is None
                keyframes.append(transitional)

        keyframes.append(deepcopy(after_state))
        result = ExecutionTraceService._sample_progressive_states(keyframes, boundaries)
        if not result:
            result = [deepcopy(before_state) for _ in range(boundaries)]
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
    ) -> list[dict[str, Any] | None]:
        if total_steps <= 0:
            return []
        if operation_name not in {"insertar", "eliminar", "buscar"}:
            return [None for _ in range(total_steps)]

        family = ExecutionTraceService._tree_family(after_state)
        path = ExecutionTraceService._tree_path_keys_for_value(before_state.get("root"), payload.get("value"))
        if not path:
            return [None for _ in range(total_steps)]

        rotation_hint = (
            ExecutionTraceService._maybe_avl_rotation_hint(path, payload.get("value"))
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

        if operation_name in {"run_bfs", "run_dfs"} and isinstance(result, list):
            path = [str(item) for item in result]
            for index in range(total_steps):
                count = _prefix_count(len(path), index)
                nodes = path[:count]
                edges = [[nodes[i - 1], nodes[i]] for i in range(1, len(nodes))]
                stage = "init" if index == 0 else "visit" if index < total_steps - 1 else "complete"
                note = (
                    f"Visitando {nodes[-1]}."
                    if nodes
                    else "Preparando recorrido."
                )
                debug_steps.append(
                    {
                        "stage": stage,
                        "note": note,
                        "graph_progress": {
                            "mode": "traversal",
                            "nodes": nodes,
                            "edges": edges,
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
        executable_line_indexes = [
            index
            for index, line in enumerate(lines)
            if ExecutionTraceService._is_executable_line(line, code_title)
        ]
        executable_line_indexes = ExecutionTraceService._filter_trace_lines_for_success(
            lines,
            executable_line_indexes,
            bool(success),
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
        state_kind = ExecutionTraceService._state_kind(after_state)
        if state_kind == "binary_tree":
            debug_steps = ExecutionTraceService._build_tree_debug_steps(
                operation_name=operation_name,
                payload=payload,
                before_state=before_state,
                after_state=after_state,
                success=bool(success),
                mutates=bool(mutates),
                total_steps=total_steps,
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
