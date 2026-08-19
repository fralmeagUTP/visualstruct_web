"""Semantic execution planners for tree algorithms."""

from __future__ import annotations

from typing import Any

from app.services.trace.control_flow import ControlFlowPlanner


class TreeAlgorithmPlanner:
    """Expand didactic tree algorithms into deterministic source-line steps."""

    @staticmethod
    def coerce_number(value: Any) -> float | int | None:
        if isinstance(value, bool):
            return None
        if isinstance(value, (int, float)):
            return value
        try:
            number = float(str(value).strip())
            return int(number) if number.is_integer() else number
        except (TypeError, ValueError):
            return None

    @staticmethod
    def node_value(node: dict[str, Any] | None) -> Any:
        if not isinstance(node, dict):
            return None
        return next((node.get(key) for key in ("value", "valor", "key", "nro") if key in node), None)

    @staticmethod
    def child(node: dict[str, Any] | None, side: str) -> dict[str, Any] | None:
        if not isinstance(node, dict):
            return None
        child = node.get("left" if side == "left" else "right")
        return child if isinstance(child, dict) else None

    @staticmethod
    def find_line(normalized_lines: list[str], needle: str) -> int:
        target = str(needle).strip().lower()
        return next((index for index, line in enumerate(normalized_lines) if target in line), -1)

    @classmethod
    def path_keys(cls, root: dict[str, Any] | None, target: Any) -> list[str]:
        target_number = cls.coerce_number(target)
        if root is None or target_number is None:
            return []
        keys: list[str] = []
        current = root
        while isinstance(current, dict):
            value = current.get("value")
            keys.append(str(value))
            number = cls.coerce_number(value)
            if number is None or target_number == number:
                break
            current = current.get("left" if target_number < number else "right")
        return keys

    @classmethod
    def _rotation_candidate(cls, path: list[str], target: Any) -> dict[str, Any] | None:
        if len(path) < 2:
            return None
        pivot, child = path[-2], path[-1]
        pivot_number, child_number, target_number = map(cls.coerce_number, (pivot, child, target))
        if pivot_number is None or child_number is None or target_number is None:
            return None
        kind = ("L" if target_number < pivot_number else "R") + ("L" if target_number < child_number else "R")
        return {"type": kind, "pivot": str(pivot), "child": str(child), "inserted": str(target_number)}

    @classmethod
    def _parent_map(cls, root: dict[str, Any] | None, parent: str | None = None) -> dict[str, str | None]:
        if not isinstance(root, dict):
            return {}
        key = str(root.get("value"))
        result = {key: parent}
        for side in ("left", "right"):
            result.update(cls._parent_map(cls.child(root, side), key))
        return result

    @classmethod
    def infer_avl_rotation(
        cls,
        before_state: dict[str, Any],
        after_state: dict[str, Any],
        target_value: Any,
    ) -> dict[str, Any] | None:
        before_root, after_root = before_state.get("root"), after_state.get("root")
        if not isinstance(before_root, dict) or not isinstance(after_root, dict):
            return None
        candidate = cls._rotation_candidate(
            cls.path_keys(before_root, target_value), target_value
        )
        if candidate is None:
            return None
        before_parents, after_parents = cls._parent_map(before_root), cls._parent_map(after_root)
        shared = set(before_parents) & set(after_parents)
        shared.discard(str(candidate.get("inserted", "")))
        return candidate if shared and any(before_parents[key] != after_parents[key] for key in shared) else None

    @classmethod
    def expand_avl_insert(
        cls,
        *,
        lines: list[str],
        before_state: dict[str, Any],
        after_state: dict[str, Any],
        payload: dict[str, Any],
        success: bool,
    ) -> list[int] | None:
        target = cls.coerce_number(payload.get("value"))
        if target is None:
            return None

        root = before_state.get("root")
        normalized_lines = [ControlFlowPlanner.normalize_line(line) for line in lines]
        joined = "\n".join(normalized_lines)
        if "void avl_insertar(" not in joined:
            return None

        header = cls.find_line(normalized_lines, "void avl_insertar(")
        guard_raiz_null = cls.find_line(normalized_lines, "if (raiz == null)")
        return_line = cls.find_line(normalized_lines, "return;")
        init_line = cls.find_line(normalized_lines, "avl padre = null, actual = *raiz;")
        while_line = cls.find_line(normalized_lines, "while (actual != null)")
        set_padre_line = cls.find_line(normalized_lines, "padre = actual;")
        if_less_line = cls.find_line(normalized_lines, "if (x < actual->nro)")
        go_left_line = cls.find_line(normalized_lines, "actual = actual->izq;")
        else_if_greater_line = cls.find_line(normalized_lines, "else if (x > actual->nro)")
        go_right_line = cls.find_line(normalized_lines, "actual = actual->der;")
        else_return_dup_line = cls.find_line(normalized_lines, "return; // no duplicados")
        malloc_line = cls.find_line(normalized_lines, "avl nuevo = malloc(sizeof(*nuevo));")
        if_nuevo_null_line = cls.find_line(normalized_lines, "if (nuevo == null)")
        set_nro_line = cls.find_line(normalized_lines, "nuevo->nro = x;")
        set_fe_line = cls.find_line(normalized_lines, "nuevo->fe = 0;")
        set_children_line = cls.find_line(normalized_lines, "nuevo->izq = nuevo->der = null;")
        set_parent_line = cls.find_line(normalized_lines, "nuevo->padre = padre;")
        if_padre_null_line = cls.find_line(normalized_lines, "if (padre == null)")
        set_root_line = cls.find_line(normalized_lines, "*raiz = nuevo;")
        if_padre_less_line = cls.find_line(normalized_lines, "if (x < padre->nro)")
        assign_parent_left_line = cls.find_line(normalized_lines, "padre->izq = nuevo;")
        else_parent_right_line = cls.find_line(normalized_lines, "padre->der = nuevo;")
        rebalance_while_line = cls.find_line(normalized_lines, "while (padre != null)")
        update_fe_left_line = cls.find_line(normalized_lines, "if (n == padre->izq)")
        update_fe_left_apply_line = cls.find_line(normalized_lines, "padre->fe--;")
        update_fe_right_line = cls.find_line(normalized_lines, "padre->fe++;")
        if_fe_zero_break_line = cls.find_line(normalized_lines, "if (padre->fe == 0) break;")
        if_fe_neg2_line = cls.find_line(normalized_lines, "if (padre->fe == -2)")
        if_n_fe_le0_rsd_line = cls.find_line(normalized_lines, "if (n->fe <= 0)")
        call_rsd_line = cls.find_line(normalized_lines, "avl_rsd(raiz, padre);")
        else_rdd_line = cls.find_line(normalized_lines, "avl_rdd(raiz, padre);")
        if_fe_pos2_line = cls.find_line(normalized_lines, "if (padre->fe == 2)")
        if_n_fe_ge0_rsi_line = cls.find_line(normalized_lines, "if (n->fe >= 0)")
        call_rsi_line = cls.find_line(normalized_lines, "avl_rsi(raiz, padre);")
        else_rdi_line = cls.find_line(normalized_lines, "avl_rdi(raiz, padre);")
        n_equals_padre_line = cls.find_line(normalized_lines, "n = padre;")
        padre_up_line = cls.find_line(normalized_lines, "padre = padre->padre;")

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
                return ControlFlowPlanner.limit_step_indexes(expanded)
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
            return ControlFlowPlanner.limit_step_indexes(expanded)

        expanded.append(init_line)
        current = root
        duplicate = False
        while isinstance(current, dict):
            expanded.append(while_line)
            expanded.append(set_padre_line)
            node_value = cls.coerce_number(
                cls.node_value(current)
            )
            if node_value is None:
                break

            if target < node_value:
                expanded.append(if_less_line)
                if go_left_line >= 0:
                    expanded.append(go_left_line)
                current = cls.child(current, "left")
                continue

            expanded.append(if_less_line)
            expanded.append(else_if_greater_line)
            if target > node_value:
                if go_right_line >= 0:
                    expanded.append(go_right_line)
                current = cls.child(current, "right")
                continue

            duplicate = True
            if else_return_dup_line >= 0:
                expanded.append(else_return_dup_line)
            elif return_line >= 0:
                expanded.append(return_line)
            break

        if duplicate:
            return ControlFlowPlanner.limit_step_indexes(expanded)

        expanded.append(while_line)
        expanded.extend([malloc_line, if_nuevo_null_line])
        if not success and return_line >= 0:
            expanded.append(return_line)
            return ControlFlowPlanner.limit_step_indexes(expanded)

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
            value = cls.coerce_number(
                cls.node_value(parent)
            )
            if value is None:
                break
            if target < value:
                next_node = cls.child(parent, "left")
            elif target > value:
                next_node = cls.child(parent, "right")
            else:
                next_node = None
            if not isinstance(next_node, dict):
                break
            parent = next_node

        parent_value = cls.coerce_number(
            cls.node_value(parent)
        )
        if parent_value is not None and target < parent_value:
            expanded.append(if_padre_less_line)
            expanded.append(assign_parent_left_line)
        else:
            expanded.append(if_padre_less_line)
            expanded.append(else_parent_right_line)

        if rebalance_while_line >= 0:
            path = cls.path_keys(root if isinstance(root, dict) else None, target)
            rotation_hint = cls.infer_avl_rotation(
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
        return ControlFlowPlanner.limit_step_indexes(expanded)

    @classmethod
    def expand_rbt_insert(
        cls,
        *,
        lines: list[str],
        before_state: dict[str, Any],
        payload: dict[str, Any],
        success: bool,
    ) -> list[int] | None:
        target = cls.coerce_number(payload.get("value"))
        if target is None:
            return None

        normalized_lines = [ControlFlowPlanner.normalize_line(line) for line in lines]
        joined = "\n".join(normalized_lines)
        if "void rbt_insertar(" not in joined:
            return None

        def _idx(needle: str) -> int:
            return cls.find_line(normalized_lines, needle)

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
            node_value = cls.coerce_number(
                cls.node_value(current)
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
                current = cls.child(current, "left")
                continue
            expanded.append(else_if_greater)
            if target > node_value:
                expanded.append(go_right)
                current = cls.child(current, "right")
                continue
            break

        # Evaluacion final del while cuando la condicion ya es falsa.
        expanded.append(while_line)
        expanded.append(if_actual_not_null)
        if duplicate:
            if return_duplicate >= 0:
                expanded.append(return_duplicate)
            return ControlFlowPlanner.limit_step_indexes(expanded)

        expanded.extend([alloc_line, if_alloc_null])
        if not success:
            if return_alloc_fail >= 0:
                expanded.append(return_alloc_fail)
            return ControlFlowPlanner.limit_step_indexes(expanded)

        expanded.extend([set_value, set_children, set_parent, set_color, if_padre_null])
        if not isinstance(before_state.get("root"), dict):
            expanded.append(set_root)
        else:
            parent = before_state.get("root")
            while isinstance(parent, dict):
                value = cls.coerce_number(
                    cls.node_value(parent)
                )
                if value is None:
                    break
                if target < value:
                    nxt = cls.child(parent, "left")
                elif target > value:
                    nxt = cls.child(parent, "right")
                else:
                    nxt = None
                if not isinstance(nxt, dict):
                    break
                parent = nxt
            parent_value = cls.coerce_number(
                cls.node_value(parent if isinstance(parent, dict) else None)
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
            value = cls.coerce_number(node.get("value"))
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
            return cls.find_line(normalized_lines, needle)

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
        return ControlFlowPlanner.limit_step_indexes(expanded)

    @classmethod
    def expand_abb_insert(
        cls,
        *,
        lines: list[str],
        before_state: dict[str, Any],
        payload: dict[str, Any],
        success: bool,
    ) -> list[int] | None:
        root = before_state.get("root")
        target = cls.coerce_number(payload.get("value"))
        if target is None:
            return None

        normalized_lines = [ControlFlowPlanner.normalize_line(line) for line in lines]
        header_line = cls.find_line(normalized_lines, "abbnodo* abb_insertar(")
        if_null_line = cls.find_line(normalized_lines, "if (nodo == null)")
        malloc_line = cls.find_line(normalized_lines, "abbnodo* nuevo = malloc")
        if_nuevo_null_line = cls.find_line(normalized_lines, "if (nuevo == null)")
        return_null_line = cls.find_line(normalized_lines, "return null;")
        set_value_line = cls.find_line(normalized_lines, "nuevo->valor = valor;")
        set_children_line = cls.find_line(normalized_lines, "nuevo->izquierdo = nuevo->derecho = null;")
        return_nuevo_line = cls.find_line(normalized_lines, "return nuevo;")
        if_less_line = cls.find_line(normalized_lines, "if (valor < nodo->valor)")
        left_recursive_line = cls.find_line(normalized_lines, "nodo->izquierdo = abb_insertar(nodo->izquierdo, valor);")
        else_if_greater_line = cls.find_line(normalized_lines, "else if (valor > nodo->valor)")
        right_recursive_line = cls.find_line(normalized_lines, "nodo->derecho = abb_insertar(nodo->derecho, valor);")
        return_nodo_line = cls.find_line(normalized_lines, "return nodo;")

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

            node_value = cls.coerce_number(
                cls.node_value(node)
            )
            if node_value is None:
                expanded.append(return_nodo_line)
                return

            expanded.append(if_less_line)
            if target < node_value:
                expanded.append(left_recursive_line)
                walk(cls.child(node, "left"))
                expanded.append(return_nodo_line)
                return

            expanded.append(else_if_greater_line)
            if target > node_value:
                expanded.append(right_recursive_line)
                walk(cls.child(node, "right"))
            # Si es duplicado, se omite recursion y se retorna nodo.
            expanded.append(return_nodo_line)

        walk(root if isinstance(root, dict) else None)
        return ControlFlowPlanner.limit_step_indexes(expanded)

    @classmethod
    def expand_abb_delete(
        cls,
        *,
        lines: list[str],
        before_state: dict[str, Any],
        payload: dict[str, Any],
    ) -> list[int] | None:
        root = before_state.get("root")
        target = cls.coerce_number(payload.get("value"))
        if target is None:
            return None

        normalized_lines = [ControlFlowPlanner.normalize_line(line) for line in lines]
        header_line = cls.find_line(normalized_lines, "abbnodo* abb_eliminar(")
        null_guard_line = cls.find_line(normalized_lines, "if (nodo == null) return nodo;")
        if_less_line = cls.find_line(normalized_lines, "if (valor < nodo->valor)")
        left_recursive_line = cls.find_line(normalized_lines, "nodo->izquierdo = abb_eliminar(nodo->izquierdo, valor);")
        else_if_greater_line = cls.find_line(normalized_lines, "else if (valor > nodo->valor)")
        right_recursive_line = cls.find_line(normalized_lines, "nodo->derecho = abb_eliminar(nodo->derecho, valor);")
        if_left_null_line = cls.find_line(normalized_lines, "if (nodo->izquierdo == null)")
        temp_right_line = cls.find_line(normalized_lines, "abbnodo* temp = nodo->derecho;")
        else_if_right_null_line = cls.find_line(normalized_lines, "else if (nodo->derecho == null)")
        temp_left_line = cls.find_line(normalized_lines, "abbnodo* temp = nodo->izquierdo;")
        free_line = cls.find_line(normalized_lines, "free(nodo);")
        return_temp_line = cls.find_line(normalized_lines, "return temp;")
        min_line = cls.find_line(normalized_lines, "abbnodo* temp = abb_encontrarminimo(nodo->derecho);")
        copy_value_line = cls.find_line(normalized_lines, "nodo->valor = temp->valor;")
        delete_successor_line = cls.find_line(normalized_lines, "nodo->derecho = abb_eliminar(nodo->derecho, temp->valor);")
        return_nodo_line = cls.find_line(normalized_lines, "return nodo;")

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

            node_value = cls.coerce_number(
                cls.node_value(node)
            )
            if node_value is None:
                expanded.append(return_nodo_line)
                return

            expanded.append(if_less_line)
            if delete_value < node_value:
                expanded.append(left_recursive_line)
                walk(cls.child(node, "left"), delete_value)
                expanded.append(return_nodo_line)
                return

            expanded.append(else_if_greater_line)
            if delete_value > node_value:
                expanded.append(right_recursive_line)
                walk(cls.child(node, "right"), delete_value)
                expanded.append(return_nodo_line)
                return

            # Nodo encontrado: seguir la rama estructural correspondiente.
            left = cls.child(node, "left")
            right = cls.child(node, "right")
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
                    left_child = cls.child(current, "left")
                    if not isinstance(left_child, dict):
                        value = cls.coerce_number(
                            cls.node_value(current)
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
        return ControlFlowPlanner.limit_step_indexes(expanded)
