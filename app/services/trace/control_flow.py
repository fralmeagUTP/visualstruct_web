"""Shared planning rules for executable C lines and defensive branches."""

from __future__ import annotations

from typing import Any


class ControlFlowPlanner:
    """Select executable lines according to simple, observable control flow."""

    @staticmethod
    def normalize_line(line_text: str) -> str:
        return " ".join(str(line_text or "").strip().lower().split())

    @staticmethod
    def limit_step_indexes(indexes: list[int], max_steps: int = 260) -> list[int]:
        if len(indexes) <= max_steps:
            return indexes
        if max_steps <= 0:
            return indexes[:1]
        last = len(indexes) - 1
        return [
            indexes[max(0, min(last, round((last * step) / max(1, max_steps - 1))))]
            for step in range(max_steps)
        ]

    @staticmethod
    def _coerce_number(value: Any) -> float | int | None:
        if isinstance(value, bool):
            return None
        if isinstance(value, (int, float)):
            return value
        try:
            number = float(str(value).strip())
            return int(number) if number.is_integer() else number
        except (TypeError, ValueError):
            return None

    @classmethod
    def state_size(cls, state: dict[str, Any]) -> int:
        raw_size = state.get("size")
        if isinstance(raw_size, (int, float)) and not isinstance(raw_size, bool):
            return max(0, int(raw_size))
        metadata = state.get("metadata")
        if isinstance(metadata, dict):
            for key in ("size", "vertices_count", "cantidad"):
                value = metadata.get(key)
                if isinstance(value, (int, float)) and not isinstance(value, bool):
                    return max(0, int(value))
        for key in ("items", "nodes"):
            values = state.get(key)
            if isinstance(values, list):
                return len(values)
        buckets = state.get("buckets")
        if isinstance(buckets, list):
            return sum(len(bucket) for bucket in buckets if isinstance(bucket, list))

        def _tree_count(node: Any) -> int:
            if not isinstance(node, dict):
                return 0
            return 1 + _tree_count(node.get("left")) + _tree_count(node.get("right"))

        return _tree_count(state.get("root"))

    @staticmethod
    def is_if_header(line: str) -> bool:
        return line.startswith("if ") or line.startswith("if(")

    @staticmethod
    def is_else_header(line: str) -> bool:
        return line.startswith("else")

    @staticmethod
    def is_loop_header(line: str) -> bool:
        return line.startswith(("while ", "while(", "for ", "for("))

    @staticmethod
    def is_return_statement(line: str) -> bool:
        return line.startswith("return")

    @classmethod
    def estimate_loop_iterations(
        cls, *, normalized_line: str, operation_name: str,
        before_state: dict[str, Any], after_state: dict[str, Any]
    ) -> int:
        before_size = cls.state_size(before_state)
        after_size = cls.state_size(after_state)
        operation = str(operation_name or "").lower()
        if "!= null" in normalized_line or "!= nullptr" in normalized_line:
            if operation in {"limpiar", "clear", "vaciar"}:
                return before_size
            if any(token in operation for token in ("desencolar", "desapilar", "eliminar")):
                return max(1, before_size)
            return before_size
        if normalized_line.startswith(("for ", "for(")):
            return max(1, min(max(before_size, after_size) or 3, 40))
        return 1

    @classmethod
    def evaluate_condition(
        cls, *, normalized_line: str, success: bool, message: str,
        before_state: dict[str, Any], after_state: dict[str, Any],
        payload: dict[str, Any] | None = None,
    ) -> bool:
        msg = str(message or "").lower()
        before_size = cls.state_size(before_state)
        after_size = cls.state_size(after_state)
        root = before_state.get("root") if isinstance(before_state, dict) else None
        root_value = cls._coerce_number(root.get("value")) if isinstance(root, dict) else None
        raw_pos = None if payload is None else payload.get("position")
        value = cls._coerce_number(None if payload is None else payload.get("value"))
        try:
            position = int(raw_pos) if raw_pos is not None and str(raw_pos).strip() else None
        except (TypeError, ValueError):
            position = None

        checks = (
            ("pos <= 0", position is not None and position <= 0),
            ("pos < 1", position is not None and position < 1),
            ("pos == 1", position == 1), ("pos==1", position == 1),
            ("i == pos", success and position is not None and position > 1),
            ("i==pos", success and position is not None and position > 1),
        )
        for token, result in checks:
            if token in normalized_line:
                return bool(result)
        if "nodo == null" in normalized_line:
            return before_size == 0
        comparisons = (
            ("valor < nodo->valor", lambda: value < root_value),
            ("valor > nodo->valor", lambda: value > root_value),
            ("x < actual->nro", lambda: value < root_value),
            ("x > actual->nro", lambda: value > root_value),
        )
        if value is not None and root_value is not None:
            for token, comparison in comparisons:
                if token in normalized_line:
                    return comparison()
        if "== null" in normalized_line or "==nullptr" in normalized_line:
            if success:
                return False
            if any(token in msg for token in ("no inicializada", "no se pudo", "vacia", "vacía")):
                return True
            return before_size == 0 and after_size == 0
        if "!= null" in normalized_line or "!= nullptr" in normalized_line:
            return before_size > 0 or after_size > 0
        if "vacia" in normalized_line or "vacía" in normalized_line:
            return before_size > 0 if "!" in normalized_line else before_size == 0
        if "!existe" in normalized_line:
            return (not success) or "no existe" in msg
        if "dist[destino] >= inf" in normalized_line or "dist[destino]>=inf" in normalized_line:
            return "no existe ruta" in msg
        if "dist[idx_llegada] == int_max" in normalized_line or "dist[idx_llegada]==int_max" in normalized_line:
            return "no existe ruta" in msg
        return not cls.is_if_header(normalized_line)

    @staticmethod
    def is_executable_line(line: str, code_title: str) -> bool:
        text = str(line).strip()
        if not text:
            return False
        if text.startswith("//") or text.startswith("/*") or text.startswith("*/"):
            return False
        if text == "*" or (text.startswith("*") and len(text) > 1 and text[1].isspace()):
            return False
        if text in {"{", "}"}:
            return False
        if "codigo c" in str(code_title).lower() and text.startswith("#"):
            return False
        return True

    @staticmethod
    def next_nonempty_line_index(lines: list[str], from_index: int) -> int:
        for index in range(from_index, len(lines)):
            if str(lines[index]).strip():
                return index
        return -1

    @staticmethod
    def find_matching_brace_line(lines: list[str], open_line_index: int) -> int:
        depth = 0
        for line_index in range(open_line_index, len(lines)):
            for char in str(lines[line_index]):
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
        return text.startswith("if") and ("== null" in text or "==nullptr" in text)

    @staticmethod
    def _is_defensive_early_exit_line(line_text: str) -> bool:
        text = str(line_text).strip().lower()
        return bool(text) and text.startswith(("return", "break", "continue"))

    @staticmethod
    def _message_matches_defensive_block(message: str, block_text: str) -> bool:
        msg = str(message or "").lower()
        block = str(block_text or "").lower()
        if not msg or not block:
            return False
        return (
            ("no inicializada" in msg and "no inicializada" in block)
            or (("no se pudo" in msg or "asignar memoria" in msg) and ("no se pudo" in block or "asignar memoria" in block))
            or (("vacia" in msg or "vacía" in msg) and ("vacia" in block or "vacía" in block))
        )

    @classmethod
    def filter_defensive_branches(
        cls,
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
            if not cls._is_defensive_null_if(line_text):
                continue
            open_line_index = line_index if "{" in line_text else cls.next_nonempty_line_index(lines, line_index + 1)
            if open_line_index < 0:
                continue
            close_line_index = cls.find_matching_brace_line(lines, open_line_index)
            if close_line_index < 0:
                continue
            inner_indexes = [idx for idx in ordered if open_line_index < idx <= close_line_index]
            early_exit_indexes = [idx for idx in inner_indexes if cls._is_defensive_early_exit_line(lines[idx])]
            if early_exit_indexes:
                blocks.append({"start": line_index, "inner": inner_indexes, "early_exit": early_exit_indexes, "text": "\n".join(str(lines[idx]) for idx in [line_index, *inner_indexes])})

        if not blocks:
            return ordered
        if success:
            skipped = {idx for block in blocks for idx in block["inner"]}
            filtered = [idx for idx in ordered if idx not in skipped]
            return filtered if filtered else ordered

        taken = next((block for block in blocks if cls._message_matches_defensive_block(message, block["text"])), None)
        if taken is None:
            return ordered
        skipped = {idx for block in blocks if block is not taken for idx in block["inner"]}
        result: list[int] = []
        for idx in ordered:
            if idx in skipped:
                continue
            result.append(idx)
            if idx == taken["start"]:
                for inner_idx in taken["inner"]:
                    if inner_idx not in skipped:
                        result.append(inner_idx)
                        if inner_idx in taken["early_exit"]:
                            return result
        return result if result else ordered

    @classmethod
    def expand_generic(
        cls,
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
                normalized_line = cls.normalize_line(line_text)

                if cls.is_if_header(normalized_line):
                    segment.append(line_index)
                    cond_true = cls.evaluate_condition(
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
                            next_norm = cls.normalize_line(next_line_text)
                            if cond_true and not cls.is_else_header(next_norm):
                                segment.append(next_line_index)
                                if cls.is_return_statement(next_norm):
                                    return segment, True
                                pos = next_pos + 1
                                # Saltar rama else/else-if complementaria de un if sin llaves.
                                if pos < end_pos:
                                    else_line_index = sorted_exec[pos]
                                    else_line_text = lines[else_line_index] if 0 <= else_line_index < len(lines) else ""
                                    else_norm = cls.normalize_line(else_line_text)
                                    if cls.is_else_header(else_norm):
                                        pos += 1
                                        if pos < end_pos:
                                            after_else_norm = cls.normalize_line(
                                                lines[sorted_exec[pos]] if 0 <= sorted_exec[pos] < len(lines) else ""
                                            )
                                            if not cls.is_else_header(after_else_norm):
                                                pos += 1
                                continue
                            if not cond_true and not cls.is_else_header(next_norm):
                                pos = next_pos + 1
                                continue
                    open_line_index = (
                        line_index
                        if "{" in line_text
                        else cls.next_nonempty_line_index(lines, line_index + 1)
                    )
                    close_line_index = (
                        cls.find_matching_brace_line(lines, open_line_index)
                        if open_line_index >= 0
                        else -1
                    )
                    if close_line_index < 0 or close_line_index <= line_index:
                        cond_true = cls.evaluate_condition(
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
                        else_norm = cls.normalize_line(else_text)
                        if cls.is_else_header(else_norm):
                            else_has_block = True
                            else_open_line = (
                                else_index
                                if "{" in else_text
                                else cls.next_nonempty_line_index(lines, else_index + 1)
                            )
                            else_close_line = (
                                cls.find_matching_brace_line(lines, else_open_line)
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
                        else_norm = cls.normalize_line(else_line_text)
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

                if cls.is_loop_header(normalized_line):
                    open_line_index = (
                        line_index
                        if "{" in line_text
                        else cls.next_nonempty_line_index(lines, line_index + 1)
                    )
                    close_line_index = (
                        cls.find_matching_brace_line(lines, open_line_index)
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

                    repeat_count = cls.estimate_loop_iterations(
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

                if cls.is_else_header(normalized_line):
                    if "return" in normalized_line:
                        segment.append(line_index)
                        return segment, True
                    pos += 1
                    continue

                segment.append(line_index)
                if cls.is_return_statement(normalized_line):
                    return segment, True
                pos += 1

            return segment, False

        expanded, _ = _expand_segment(0, len(sorted_exec))
        return cls.limit_step_indexes(expanded)
