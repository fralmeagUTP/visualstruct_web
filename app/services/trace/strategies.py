"""Trace strategy contracts and family registry."""

from __future__ import annotations

from abc import ABC, abstractmethod
from copy import deepcopy
from difflib import SequenceMatcher
import json
from typing import Any

from app.services.trace.models import TraceStep


class TraceStrategy(ABC):
    """Convert family-specific raw steps into the common semantic contract."""

    family = "generic"

    @abstractmethod
    def normalize_steps(self, raw_steps: list[dict[str, Any]]) -> list[TraceStep]:
        """Return validated semantic steps without changing their order."""


class LegacyTraceStrategy(TraceStrategy):
    """Compatibility strategy used while family logic is extracted incrementally."""

    def normalize_steps(self, raw_steps: list[dict[str, Any]]) -> list[TraceStep]:
        return [TraceStep.from_legacy(step) for step in raw_steps]


class SequentialTraceStrategy(LegacyTraceStrategy):
    """Build progressive visual states for linear sequential structures."""

    family = "sequential"

    @staticmethod
    def _stable_token(value: Any) -> str:
        try:
            return json.dumps(value, ensure_ascii=False, sort_keys=True)
        except TypeError:
            return repr(value)

    @classmethod
    def _transition_states(cls, before: list[Any], after: list[Any]) -> list[list[Any]]:
        working = deepcopy(before)
        states = [deepcopy(working)]
        matcher = SequenceMatcher(
            a=[cls._stable_token(item) for item in before],
            b=[cls._stable_token(item) for item in after],
            autojunk=False,
        )
        offset = 0
        for tag, i1, i2, j1, j2 in matcher.get_opcodes():
            if tag in {"delete", "replace"}:
                count = i2 - i1
                for _ in range(count):
                    position = i1 + offset
                    if 0 <= position < len(working):
                        working.pop(position)
                        states.append(deepcopy(working))
                offset -= count
            if tag in {"insert", "replace"}:
                for index, item in enumerate(after[j1:j2]):
                    working.insert(i1 + offset + index, deepcopy(item))
                    states.append(deepcopy(working))
                offset += j2 - j1
        if states[-1] != after:
            states.append(deepcopy(after))
        return states

    @staticmethod
    def _sample(states: list[Any], frames: int) -> list[Any]:
        if frames <= 0:
            return []
        if len(states) == 1:
            return [deepcopy(states[0]) for _ in range(frames)]
        maximum = len(states) - 1
        span = max(1, frames - 1)
        return [deepcopy(states[round(maximum * index / span)]) for index in range(frames)]

    @staticmethod
    def _is_assignment(line: str) -> bool:
        text = str(line or "").strip().lower()
        return bool(
            text
            and not text.startswith(("if ", "if(", "return"))
            and text not in {"{", "}"}
            and "=" in text
            and not any(token in text for token in ("==", "!=", "<=", ">="))
        )

    @classmethod
    def _anchor(cls, lines: list[str], total_steps: int) -> int:
        return next((index for index, line in enumerate(lines) if cls._is_assignment(line)), max(0, total_steps - 1))

    @staticmethod
    def _align(states: list[Any], boundaries: int, anchor: int) -> list[Any]:
        start = deepcopy(states[0])
        end = deepcopy(states[-1])
        start_boundary = max(1, min(boundaries - 1, anchor + 1))
        result: list[Any] = []
        for boundary in range(boundaries):
            if boundary < start_boundary:
                result.append(deepcopy(start))
                continue
            remaining = boundaries - start_boundary
            if remaining <= 1:
                result.append(deepcopy(end))
                continue
            sampled = round((len(states) - 1) * (boundary - start_boundary) / (remaining - 1))
            result.append(deepcopy(states[max(0, min(len(states) - 1, sampled))]))
        result[0] = start
        result[-1] = end
        return result

    def build_boundaries(
        self,
        before_state: dict[str, Any],
        after_state: dict[str, Any],
        total_steps: int,
        step_lines: list[str],
    ) -> list[dict[str, Any]]:
        """Return one state boundary per step plus the initial boundary."""
        boundaries = total_steps + 1
        sampled = self._sample(
            self._transition_states(
                list(before_state.get("items") or []),
                list(after_state.get("items") or []),
            ),
            boundaries,
        )
        progressive = self._align(sampled, boundaries, self._anchor(step_lines, total_steps))
        result: list[dict[str, Any]] = []
        for items in progressive:
            current = deepcopy(before_state)
            current["items"] = items if isinstance(items, list) else []
            current["size"] = len(current["items"])
            current["empty"] = not current["items"]
            current["title"] = after_state.get("title", current.get("title"))
            current["kind"] = after_state.get("kind", current.get("kind"))
            result.append(current)
        result[0] = deepcopy(before_state)
        result[-1] = deepcopy(after_state)
        return result


class TreeTraceStrategy(LegacyTraceStrategy):
    """Build mutation boundaries for ABB, AVL and red-black trees."""

    family = "tree"

    @classmethod
    def _heap_root(cls, values: list[Any], index: int = 0) -> dict[str, Any] | None:
        if index >= len(values):
            return None
        return {
            "value": values[index],
            "left": cls._heap_root(values, 2 * index + 1),
            "right": cls._heap_root(values, 2 * index + 2),
        }

    def build_heap_boundaries(
        self,
        before_state: dict[str, Any],
        after_state: dict[str, Any],
        total_steps: int,
        step_lines: list[str],
    ) -> list[dict[str, Any]]:
        boundaries = total_steps + 1
        raw_states = SequentialTraceStrategy._sample(
            SequentialTraceStrategy._transition_states(
                list(before_state.get("array") or []),
                list(after_state.get("array") or []),
            ),
            boundaries,
        )
        arrays = SequentialTraceStrategy._align(
            raw_states,
            boundaries,
            SequentialTraceStrategy._anchor(step_lines, total_steps),
        )
        result: list[dict[str, Any]] = []
        for array in arrays:
            values = array if isinstance(array, list) else []
            current = deepcopy(before_state)
            current["array"] = values
            current["root"] = self._heap_root(values)
            current["size"] = len(values)
            current["empty"] = not values
            current["title"] = after_state.get("title", current.get("title"))
            current["kind"] = after_state.get("kind", current.get("kind"))
            result.append(current)
        result[0] = deepcopy(before_state)
        result[-1] = deepcopy(after_state)
        return result

    @staticmethod
    def _number(value: Any) -> float | int | None:
        if isinstance(value, (int, float)):
            return value
        try:
            number = float(str(value).strip())
            return int(number) if number.is_integer() else number
        except (TypeError, ValueError):
            return None

    @staticmethod
    def _normalized(line: str) -> str:
        return " ".join(str(line).strip().lower().split())

    @classmethod
    def _find_node(cls, root: dict[str, Any] | None, target: Any) -> dict[str, Any] | None:
        target_number = cls._number(target)
        current = root
        while isinstance(current, dict) and target_number is not None:
            value = cls._number(current.get("value"))
            if value is None or value == target_number:
                return current if value == target_number else None
            current = current.get("left") if target_number < value else current.get("right")
        return None

    @classmethod
    def _insert(cls, root: dict[str, Any] | None, value: Any, template: dict[str, Any]) -> dict[str, Any]:
        if root is None:
            return deepcopy(template)
        node_value = cls._number(root.get("value"))
        target = cls._number(value)
        if node_value is None or target is None:
            return deepcopy(root)
        if target < node_value:
            root["left"] = cls._insert(root.get("left") if isinstance(root.get("left"), dict) else None, value, template)
        elif target > node_value:
            root["right"] = cls._insert(root.get("right") if isinstance(root.get("right"), dict) else None, value, template)
        return root

    @staticmethod
    def _template(source: dict[str, Any] | None, value: Any) -> dict[str, Any]:
        if not isinstance(source, dict):
            return {"value": value, "left": None, "right": None}
        template = {"value": source.get("value", value), "left": None, "right": None}
        for key in ("color", "height", "balance_factor"):
            if key in source:
                template[key] = source.get(key)
        return template

    @staticmethod
    def _family(state: dict[str, Any]) -> str:
        title = str(state.get("title", "")).lower()
        if "avl" in title:
            return "avl"
        if "rojo" in title or "red-black" in title or "negro" in title:
            return "red_black"
        return "abb"

    @classmethod
    def _anchor(cls, operation: str, lines: list[str], total_steps: int) -> int:
        normalized = [cls._normalized(line) for line in lines]
        joined = "\n".join(normalized)
        patterns: list[str] = []
        if str(operation).lower() == "insertar":
            if "abb_insertar(" in joined:
                patterns = ["nuevo->valor = valor;", "nodo->izquierdo = abb_insertar", "nodo->derecho = abb_insertar"]
            elif "void avl_insertar(" in joined:
                patterns = ["*raiz = nuevo;", "padre->izq = nuevo;", "padre->der = nuevo;"]
            elif "void rbt_insertar(" in joined:
                patterns = ["*arbol = actual;", "padre->izq = actual;", "padre->der = actual;"]
        elif str(operation).lower() == "eliminar":
            patterns = ["free(", "return temp;", "nodo->valor = temp->valor;", "nodo->derecho = abb_eliminar"]
        for pattern in patterns:
            needle = cls._normalized(pattern)
            for index, line in enumerate(normalized):
                if needle in line:
                    return index
        return next((index for index, line in enumerate(lines) if SequentialTraceStrategy._is_assignment(line)), max(0, total_steps - 1))

    def build_boundaries(
        self,
        before_state: dict[str, Any],
        after_state: dict[str, Any],
        total_steps: int,
        operation_name: str,
        payload: dict[str, Any],
        step_lines: list[str],
    ) -> list[dict[str, Any]]:
        boundaries = total_steps + 1
        anchor = self._anchor(operation_name, step_lines, total_steps)
        mutation_boundary = max(1, min(boundaries - 1, anchor + 1))
        family = self._family(after_state)
        target = self._number(payload.get("value"))
        before_root = before_state.get("root") if isinstance(before_state.get("root"), dict) else None
        after_root = after_state.get("root") if isinstance(after_state.get("root"), dict) else None

        if family in {"avl", "red_black"} and operation_name == "insertar" and target is not None:
            source = self._find_node(after_root, target)
            template = (
                {"value": target, "color": "RED", "left": None, "right": None}
                if family == "red_black"
                else self._template(source, target)
            )
            middle_root = self._insert(deepcopy(before_root), target, template)
            marker = "rbt_insercion_caso1(" if family == "red_black" else "avl_r"
            transition_index = next(
                (index for index, line in enumerate(step_lines) if marker in self._normalized(line)),
                -1,
            )
            transition_boundary = transition_index + 1
            if transition_boundary > mutation_boundary and transition_boundary < boundaries:
                middle = deepcopy(after_state)
                middle["root"] = middle_root
                result = [
                    deepcopy(before_state) if index < mutation_boundary
                    else deepcopy(middle) if index < transition_boundary
                    else deepcopy(after_state)
                    for index in range(boundaries)
                ]
                result[0] = deepcopy(before_state)
                result[-1] = deepcopy(after_state)
                return result

        result = [
            deepcopy(before_state) if index < mutation_boundary else deepcopy(after_state)
            for index in range(boundaries)
        ]
        result[0] = deepcopy(before_state)
        result[-1] = deepcopy(after_state)
        return result


    @classmethod
    def _path(cls, root: dict[str, Any] | None, target: Any) -> list[str]:
        target_number = cls._number(target)
        path: list[str] = []
        current = root
        while isinstance(current, dict) and target_number is not None:
            value = current.get("value")
            path.append(str(value))
            node_number = cls._number(value)
            if node_number is None or node_number == target_number:
                break
            current = current.get("left") if target_number < node_number else current.get("right")
        return path

    @staticmethod
    def _extreme_path(root: dict[str, Any] | None, side: str) -> list[str]:
        path: list[str] = []
        current = root
        while isinstance(current, dict):
            path.append(str(current.get("value")))
            current = current.get(side) if isinstance(current.get(side), dict) else None
        return path

    @classmethod
    def _parent_map(cls, root: dict[str, Any] | None, parent: str | None = None) -> dict[str, str | None]:
        if not isinstance(root, dict):
            return {}
        key = str(root.get("value"))
        result = {key: parent}
        result.update(cls._parent_map(root.get("left") if isinstance(root.get("left"), dict) else None, key))
        result.update(cls._parent_map(root.get("right") if isinstance(root.get("right"), dict) else None, key))
        return result

    @classmethod
    def _rotation_hint(cls, before: dict[str, Any], after: dict[str, Any], target: Any) -> dict[str, Any] | None:
        before_root = before.get("root") if isinstance(before.get("root"), dict) else None
        after_root = after.get("root") if isinstance(after.get("root"), dict) else None
        path = cls._path(before_root, target)
        if len(path) < 2:
            return None
        pivot, child = path[-2], path[-1]
        pivot_number, child_number, target_number = cls._number(pivot), cls._number(child), cls._number(target)
        if pivot_number is None or child_number is None or target_number is None:
            return None
        rotation_type = ("L" if target_number < pivot_number else "R") + ("L" if target_number < child_number else "R")
        before_parents = cls._parent_map(before_root)
        after_parents = cls._parent_map(after_root)
        shared = set(before_parents) & set(after_parents)
        if not any(before_parents.get(key) != after_parents.get(key) for key in shared):
            return None
        return {"type": rotation_type, "pivot": pivot, "child": child, "inserted": str(target_number)}

    @staticmethod
    def _rotation_message(hint: dict[str, Any] | None) -> str:
        if not hint:
            return ""
        kind, pivot, child = str(hint.get("type", "")).upper(), hint.get("pivot"), hint.get("child")
        messages = {
            "LL": f"Rotacion AVL LL: rotacion a la derecha en {pivot}.",
            "RR": f"Rotacion AVL RR: rotacion a la izquierda en {pivot}.",
            "LR": f"Rotacion AVL LR: izquierda en {child} y luego derecha en {pivot}.",
            "RL": f"Rotacion AVL RL: derecha en {child} y luego izquierda en {pivot}.",
        }
        return messages.get(kind, "Rotacion AVL detectada.")

    def build_debug_steps(
        self,
        operation_name: str,
        payload: dict[str, Any],
        before_state: dict[str, Any],
        after_state: dict[str, Any],
        success: bool,
        mutates: bool,
        total_steps: int,
        step_lines: list[str],
    ) -> list[dict[str, Any] | None]:
        """Build traversal, rebalance and fix-up metadata for tree playback."""
        if total_steps <= 0:
            return []
        if operation_name not in {"insertar", "eliminar", "buscar", "minimo", "maximo"}:
            return [None for _ in range(total_steps)]
        family = self._family(after_state)
        if operation_name in {"minimo", "maximo"}:
            root = before_state.get("root") if isinstance(before_state.get("root"), dict) else after_state.get("root")
            path = self._extreme_path(root if isinstance(root, dict) else None, "left" if operation_name == "minimo" else "right")
        else:
            root = before_state.get("root") if isinstance(before_state.get("root"), dict) else None
            path = self._path(root, payload.get("value"))
        if not path:
            return [None for _ in range(total_steps)]
        hint = self._rotation_hint(before_state, after_state, payload.get("value")) if family == "avl" and operation_name == "insertar" and success and mutates else None
        pivot = path[-2] if len(path) >= 2 else path[-1]
        child = path[-1]
        denominator = max(1, total_steps - 1)
        output: list[dict[str, Any] | None] = []
        for index in range(total_steps):
            path_index = max(0, min(len(path) - 1, round((len(path) - 1) * index / denominator)))
            line = self._normalized(step_lines[index]) if index < len(step_lines) else ""
            stage, active, note = "search", [], ""
            if family == "avl" and operation_name in {"insertar", "eliminar"}:
                active = [str(path[path_index])]
                if any(token in line for token in ("while (padre != null)", "if (padre->fe ==", "if (n == padre->izq)", "padre->fe--;", "padre->fe++;", "if (n->fe <= 0)", "if (n->fe >= 0)")):
                    stage = "pre_rebalance" if hint else "rebalance_scan"
                    active = [str(pivot)]
                    note = f"Nodo desbalanceado detectado en {pivot}." if hint else "Actualizando factor de equilibrio (FE)."
                if any(token in line for token in ("avl_rsd(", "avl_rsi(", "avl_rdd(", "avl_rdi(")):
                    stage, active = "rebalance", [str(pivot), str(child)]
                    note = self._rotation_message(hint) or "Aplicando ajuste AVL."
                if any(token in line for token in ("*raiz = nuevo;", "padre->izq = nuevo;", "padre->der = nuevo;")):
                    stage, active, note = "apply", [str(path[-1])], "Aplicando cambio final sobre el arbol."
            elif family == "red_black" and operation_name in {"insertar", "eliminar"}:
                active = [str(path[path_index])]
                if "while (actual != null && dato != actual->nro)" in line:
                    note = "Recorriendo el arbol para ubicar la posicion de insercion."
                elif any(token in line for token in ("*arbol = actual;", "padre->izq = actual;", "padre->der = actual;")):
                    stage, active, note = "apply", [str(path[-1])], "Nodo enlazado al arbol (insercion BST)."
                elif "actual->rbt_color = rojo;" in line:
                    stage, note = "pre_fixup", "Nodo nuevo nace rojo antes del ajuste RN."
                elif "rbt_insercion_caso1(" in line:
                    stage, active, note = "fixup", [str(path[-1])], "Aplicando fix-up Rojo-Negro (recoloreos/rotaciones)."
                elif "printf(" in line:
                    stage, note = "post_fixup", "Insercion Rojo-Negro completada."
            elif operation_name in {"minimo", "maximo"}:
                stage = "search" if index < total_steps - 1 else "result"
                active = [str(path[path_index])]
                note = ("Descendiendo por izquierda para encontrar el minimo." if operation_name == "minimo" else "Descendiendo por derecha para encontrar el maximo.")
                if index == total_steps - 1:
                    note = f"{'Minimo' if operation_name == 'minimo' else 'Maximo'} encontrado en {path[-1]}."
            elif index == total_steps - 1 and operation_name in {"insertar", "eliminar"}:
                stage, active, note = "apply", [str(path[-1])], "Aplicando cambio final sobre el arbol."
            debug: dict[str, Any] = {"path_keys": deepcopy(path), "path_index": path_index, "stage": stage}
            if active:
                debug["active_keys"] = active
            if note:
                debug["note"] = note
            if hint and stage in {"pre_rebalance", "rebalance", "post_rebalance"}:
                debug.update({"rotation_hint": deepcopy(hint), "unbalanced_key": str(pivot)})
                message = self._rotation_message(hint)
                if message:
                    debug["rotation_message"] = message
            output.append(debug)
        return output


class GraphTraceStrategy(LegacyTraceStrategy):
    """Build progressive node/edge states and graph metadata."""

    family = "graph"

    @staticmethod
    def _is_weighted(edges: list[Any]) -> bool:
        for edge in edges:
            if not isinstance(edge, dict):
                continue
            try:
                if float(edge.get("weight", 1)) != 1.0:
                    return True
            except (TypeError, ValueError):
                continue
        return False

    def build_boundaries(
        self,
        before_state: dict[str, Any],
        after_state: dict[str, Any],
        total_steps: int,
        step_lines: list[str],
    ) -> list[dict[str, Any]]:
        boundaries = total_steps + 1
        anchor = SequentialTraceStrategy._anchor(step_lines, total_steps)

        def progressive(key: str) -> list[Any]:
            sampled = SequentialTraceStrategy._sample(
                SequentialTraceStrategy._transition_states(
                    list(before_state.get(key) or []),
                    list(after_state.get(key) or []),
                ),
                boundaries,
            )
            return SequentialTraceStrategy._align(sampled, boundaries, anchor)

        node_states = progressive("nodes")
        edge_states = progressive("edges")
        result: list[dict[str, Any]] = []
        for index in range(boundaries):
            current = deepcopy(before_state)
            nodes = node_states[index] if isinstance(node_states[index], list) else []
            edges = edge_states[index] if isinstance(edge_states[index], list) else []
            current["nodes"] = nodes
            current["edges"] = edges
            current["directed"] = bool(after_state.get("directed", before_state.get("directed", False)))
            current["weighted"] = self._is_weighted(edges)
            current["metadata"] = {
                "vertices_count": len(nodes),
                "edges_count": len(edges),
                "is_empty": not nodes,
            }
            for key in ("last_operation", "last_result"):
                current[key] = deepcopy(after_state.get(key, current.get(key)))
            result.append(current)
        result[0] = deepcopy(before_state)
        result[-1] = deepcopy(after_state)
        return result


class HashTraceStrategy(LegacyTraceStrategy):
    """Build progressive bucket states and derived hash metadata."""

    family = "hash"

    def build_boundaries(
        self,
        before_state: dict[str, Any],
        after_state: dict[str, Any],
        total_steps: int,
        step_lines: list[str],
    ) -> list[dict[str, Any]]:
        boundaries = total_steps + 1
        raw_states = SequentialTraceStrategy._sample(
            SequentialTraceStrategy._transition_states(
                list(before_state.get("buckets") or []),
                list(after_state.get("buckets") or []),
            ),
            boundaries,
        )
        bucket_states = SequentialTraceStrategy._align(
            raw_states,
            boundaries,
            SequentialTraceStrategy._anchor(step_lines, total_steps),
        )
        result: list[dict[str, Any]] = []
        after_metadata = after_state.get("metadata") if isinstance(after_state.get("metadata"), dict) else {}
        for buckets in bucket_states:
            current_buckets = deepcopy(buckets if isinstance(buckets, list) else [])
            size = 0
            collisions = 0
            for bucket in current_buckets:
                if not isinstance(bucket, dict):
                    continue
                entries = list(bucket.get("entries") or [])
                bucket["entries"] = entries
                bucket["size"] = len(entries)
                bucket["collisions"] = max(0, len(entries) - 1)
                size += bucket["size"]
                collisions += bucket["collisions"]
            capacity = len(current_buckets) if current_buckets else int(after_metadata.get("capacity", 0))
            current = deepcopy(before_state)
            current["buckets"] = current_buckets
            current["metadata"] = {
                "size": size,
                "capacity": capacity,
                "load_factor": round(float(size) / float(capacity), 6) if capacity else 0.0,
                "collisions": collisions,
                "is_empty": size == 0,
                "resized": bool(after_metadata.get("resized", False)),
                "resize_event": deepcopy(after_metadata.get("resize_event")),
            }
            for key in ("last_operation", "last_result"):
                current[key] = deepcopy(after_state.get(key, current.get(key)))
            current["title"] = after_state.get("title", current.get("title"))
            current["structure"] = after_state.get("structure", current.get("structure"))
            result.append(current)
        result[0] = deepcopy(before_state)
        result[-1] = deepcopy(after_state)
        return result


class SortingTraceStrategy(LegacyTraceStrategy):
    family = "sorting"


class TraceStrategyRegistry:
    """Resolve one strategy for every currently supported structure."""

    _strategies: dict[str, TraceStrategy] = {
        "sequential": SequentialTraceStrategy(),
        "tree": TreeTraceStrategy(),
        "graph": GraphTraceStrategy(),
        "hash": HashTraceStrategy(),
        "sorting": SortingTraceStrategy(),
    }
    _structure_families: dict[str, str] = {
        "stack": "sequential",
        "queue": "sequential",
        "priority_queue": "sequential",
        "linked_list": "sequential",
        "circular_list": "sequential",
        "sublist": "sequential",
        "abb": "tree",
        "avl": "tree",
        "red_black": "tree",
        "binary_heap": "tree",
        "graph": "graph",
        "hash_table": "hash",
        "sorting": "sorting",
        "sorting_array": "sorting",
    }

    @classmethod
    def resolve(cls, structure_id: str) -> TraceStrategy:
        family = cls._structure_families.get(structure_id)
        if family is None:
            raise KeyError(f"No existe estrategia de traza para '{structure_id}'.")
        return cls._strategies[family]
