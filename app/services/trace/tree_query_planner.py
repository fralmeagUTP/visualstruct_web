"""Semantic planners for tree queries, traversals, metrics, and cleanup."""

from __future__ import annotations

from typing import Any

from app.services.trace.control_flow import ControlFlowPlanner
from app.services.trace.tree_planner import TreeAlgorithmPlanner


class TreeQueryPlanner:
    """Expand non-mutating and cleanup tree operations into source-line steps."""

    @staticmethod
    def path_to_extreme(root: dict[str, Any] | None, side: str) -> list[str]:
        keys: list[str] = []
        current = root
        normalized_side = "left" if str(side).lower() == "left" else "right"
        while isinstance(current, dict):
            keys.append(str(current.get("value")))
            current = TreeAlgorithmPlanner.child(current, normalized_side)
        return keys

    @classmethod
    def expand_extreme(
        cls,
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
        path = cls.path_to_extreme(root, side)
        if not path:
            return None

        normalized_lines = [ControlFlowPlanner.normalize_line(line) for line in lines]
        header_line = -1
        if operation_name == "minimo":
            for needle in ("avl avl_minimo(", "abbnodo* abb_encontrarminimo(", "abbnodo *abb_encontrarminimo("):
                header_line = TreeAlgorithmPlanner.find_line(normalized_lines, needle)
                if header_line >= 0:
                    break
        else:
            for needle in ("abbnodo* abb_encontrarmaximo(", "abbnodo *abb_encontrarmaximo(", "avl aux = raiz;"):
                header_line = TreeAlgorithmPlanner.find_line(normalized_lines, needle)
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
            while_line = TreeAlgorithmPlanner.find_line(normalized_lines, needle)
            if while_line >= 0:
                break
        move_line = -1
        for needle in (
            "nodo = nodo->izq;" if side == "left" else "nodo = nodo->derecho;",
            "nodo = nodo->izquierdo;" if side == "left" else "nodo = nodo->der;",
            "aux = aux->izq;" if side == "left" else "aux = aux->der;",
            "actual = actual->izquierdo;" if side == "left" else "actual = actual->derecho;",
        ):
            move_line = TreeAlgorithmPlanner.find_line(normalized_lines, needle)
            if move_line >= 0:
                break
        return_line = -1
        for needle in ("return nodo;", "return actual;", "return aux;"):
            return_line = TreeAlgorithmPlanner.find_line(normalized_lines, needle)
            if return_line >= 0:
                break
        null_guard_line = -1
        for needle in ("if (nodo == null)", "if (actual == null)", "if (aux == null)"):
            null_guard_line = TreeAlgorithmPlanner.find_line(normalized_lines, needle)
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
        return ControlFlowPlanner.limit_step_indexes(expanded)

    @classmethod
    def expand_traversal(
        cls,
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
        normalized_lines = [ControlFlowPlanner.normalize_line(line) for line in lines]

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
            fn_norm = ControlFlowPlanner.normalize_line(function_name)
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
            walk(TreeAlgorithmPlanner.child(node, "left"))

            if operation_name == "inorden":
                expanded.append(visit_line)

            expanded.append(right_call_line)
            walk(TreeAlgorithmPlanner.child(node, "right"))

            if operation_name == "postorden":
                expanded.append(visit_line)

        walk(root)
        return ControlFlowPlanner.limit_step_indexes(expanded)

    @classmethod
    def expand_metrics(
        cls,
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

        normalized_lines = [ControlFlowPlanner.normalize_line(line) for line in lines]
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

        fn_norm = ControlFlowPlanner.normalize_line(function_name) if function_name else ""
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
                    bf = TreeAlgorithmPlanner.coerce_number(node.get("balance_factor"))
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
        return ControlFlowPlanner.limit_step_indexes(expanded)

    @classmethod
    def expand_clear(
        cls,
        *,
        lines: list[str],
        before_state: dict[str, Any],
        after_state: dict[str, Any],
    ) -> list[int] | None:
        root = before_state.get("root")
        if not isinstance(root, dict):
            root = after_state.get("root")
        normalized_lines = [ControlFlowPlanner.normalize_line(line) for line in lines]

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

        fn_norm = ControlFlowPlanner.normalize_line(function_name)
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
            walk(TreeAlgorithmPlanner.child(node, "left"))
            expanded.append(right_call_line)
            walk(TreeAlgorithmPlanner.child(node, "right"))
            expanded.append(free_line)

        walk(root if isinstance(root, dict) else None)
        return ControlFlowPlanner.limit_step_indexes(expanded)
