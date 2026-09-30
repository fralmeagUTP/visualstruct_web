"""Control-flow planner faithful to the fixed-capacity hash-table C TAD."""
from __future__ import annotations

from typing import Any


class HashControlFlowPlanner:
    @staticmethod
    def _find(lines: list[str], token: str, start: int = 0) -> int:
        needle = "".join(token.lower().split())
        for index in range(start, len(lines)):
            if needle in "".join(lines[index].lower().split()):
                return index
        return -1

    @staticmethod
    def _chain(state: dict[str, Any], key: int) -> tuple[int, list[dict[str, Any]]]:
        metadata = state.get("metadata") if isinstance(state.get("metadata"), dict) else {}
        capacity = int(metadata.get("capacity", 0))
        if capacity <= 0:
            return -1, []
        bucket_index = key % capacity
        for bucket in state.get("buckets") or []:
            if isinstance(bucket, dict) and int(bucket.get("index", -1)) == bucket_index:
                return bucket_index, [entry for entry in bucket.get("entries") or [] if isinstance(entry, dict)]
        return bucket_index, []

    @classmethod
    def _index_call(cls, lines: list[str], call_line: int) -> tuple[list[int], int, int]:
        helper = cls._find(lines, "int th_indice(")
        if helper < 0:
            return []
        result = [helper]
        defensive = cls._find(lines, "if (!tabla || tabla->capacidad <= 0) return -1;", helper)
        remainder = cls._find(lines, "int indice = clave % tabla->capacidad;", helper)
        negative = cls._find(lines, "if (indice < 0)", helper)
        normalize = cls._find(lines, "indice += tabla->capacidad;", helper)
        return_line = cls._find(lines, "return indice;", helper)
        result.extend(index for index in (defensive, remainder, negative) if index >= 0)
        return result, normalize, return_line

    @classmethod
    def _search_body(cls, lines: list[str], function_start: int, chain: list[dict[str, Any]], key: int) -> list[int]:
        defensive = cls._find(lines, "if (!tabla || !tabla->buckets", function_start)
        index_call = cls._find(lines, "int indice = th_indice(tabla, clave);", function_start)
        actual = cls._find(lines, "THNodo *actual = tabla->buckets[indice];", function_start)
        loop = cls._find(lines, "while (actual != NULL)", function_start)
        compare = cls._find(lines, "if (actual->clave == clave)", loop)
        output = cls._find(lines, "*valor = actual->valor;", compare)
        return_true = cls._find(lines, "return true;", compare)
        advance = cls._find(lines, "actual = actual->siguiente;", compare)
        return_false = cls._find(lines, "return false;", max(advance, loop) + 1)
        result = [function_start, defensive, index_call]
        helper, normalize, helper_return = cls._index_call(lines, index_call)
        result.extend(helper)
        if key < 0 and normalize >= 0:
            result.append(normalize)
        if helper_return >= 0:
            result.append(helper_return)
        result.extend([actual])
        found = False
        for entry in chain:
            result.extend([loop, compare])
            if int(entry.get("key")) == key:
                result.extend([output, return_true])
                found = True
                break
            result.append(advance)
        if not found:
            result.extend([loop, return_false])
        return [index for index in result if index >= 0]

    @classmethod
    def expand(cls, *, operation_name: str, lines: list[str], before_state: dict[str, Any], payload: dict[str, Any], message: str) -> list[int] | None:
        if operation_name in {"clear", "destroy_table"}:
            return cls._expand_lifecycle(operation_name, lines, before_state)
        if operation_name not in {"insert", "get", "contains", "remove"}:
            return None
        try:
            key = int(payload.get("key"))
        except (TypeError, ValueError):
            return None
        _bucket, chain = cls._chain(before_state, key)

        if operation_name == "remove":
            return cls._remove_body(lines, chain, key)

        if operation_name == "contains":
            contains = cls._find(lines, "bool th_contiene(")
            dummy = cls._find(lines, "int dummy_valor;", contains)
            call = cls._find(lines, "return th_buscar(tabla, clave, &dummy_valor);", contains)
            search = cls._find(lines, "bool th_buscar(", call + 1)
            return [index for index in (contains, dummy, call) if index >= 0] + cls._search_body(lines, search, chain, key)

        function_token = "bool th_insertar(" if operation_name == "insert" else "bool th_buscar("
        start = cls._find(lines, function_token)
        if operation_name == "get":
            return cls._search_body(lines, start, chain, key)

        defensive = cls._find(lines, "if (!tabla || !tabla->buckets", start)
        index_call = cls._find(lines, "int indice = th_indice(tabla, clave);", start)
        actual = cls._find(lines, "THNodo *actual = tabla->buckets[indice];", start)
        loop = cls._find(lines, "while (actual != NULL)", start)
        compare = cls._find(lines, "if (actual->clave == clave)", loop)
        update = cls._find(lines, "actual->valor = valor;", compare)
        return_update = cls._find(lines, "return true;", update)
        advance = cls._find(lines, "actual = actual->siguiente;", compare)
        result = [start, defensive, index_call]
        helper, normalize, helper_return = cls._index_call(lines, index_call)
        result.extend(helper)
        if key < 0 and normalize >= 0:
            result.append(normalize)
        if helper_return >= 0:
            result.append(helper_return)
        result.append(actual)
        found = False
        for entry in chain:
            result.extend([loop, compare])
            if int(entry.get("key")) == key:
                result.extend([update, return_update])
                found = True
                break
            result.append(advance)
        if found:
            return [index for index in result if index >= 0]
        result.append(loop)
        malloc = cls._find(lines, "malloc(sizeof(THNodo))", loop)
        null_check = cls._find(lines, "if (!nuevo) return false;", malloc)
        result.extend([malloc, null_check])
        if "malloc simulado" in message.lower():
            return [index for index in result if index >= 0]
        for token in ("nuevo->clave = clave;", "nuevo->valor = valor;", "nuevo->siguiente = tabla->buckets[indice];", "tabla->buckets[indice] = nuevo;", "tabla->cantidad++;", "return true;"):
            result.append(cls._find(lines, token, max(malloc, 0)))
        return [index for index in result if index >= 0]

    @classmethod
    def _remove_body(cls, lines: list[str], chain: list[dict[str, Any]], key: int) -> list[int]:
        start = cls._find(lines, "bool th_eliminar(")
        defensive = cls._find(lines, "if (!tabla || !tabla->buckets", start)
        index_call = cls._find(lines, "int indice = th_indice(tabla, clave);", start)
        actual = cls._find(lines, "THNodo *actual = tabla->buckets[indice];", start)
        previous = cls._find(lines, "THNodo *anterior = NULL;", start)
        loop = cls._find(lines, "while (actual != NULL)", start)
        compare = cls._find(lines, "if (actual->clave == clave)", loop)
        header_if = cls._find(lines, "if (anterior == NULL)", compare)
        header_link = cls._find(lines, "tabla->buckets[indice] = actual->siguiente;", header_if)
        previous_link = cls._find(lines, "anterior->siguiente = actual->siguiente;", header_link)
        free = cls._find(lines, "free(actual);", previous_link)
        decrement = cls._find(lines, "tabla->cantidad--;", free)
        return_true = cls._find(lines, "return true;", decrement)
        advance_previous = cls._find(lines, "anterior = actual;", return_true)
        advance_actual = cls._find(lines, "actual = actual->siguiente;", advance_previous)
        return_false = cls._find(lines, "return false;", advance_actual)
        result = [start, defensive, index_call]
        helper, normalize, helper_return = cls._index_call(lines, index_call)
        result.extend(helper)
        if key < 0 and normalize >= 0:
            result.append(normalize)
        if helper_return >= 0:
            result.append(helper_return)
        result.extend([actual, previous])
        for position, entry in enumerate(chain):
            result.extend([loop, compare])
            if int(entry.get("key")) == key:
                result.append(header_if)
                result.append(header_link if position == 0 else previous_link)
                result.extend([free, decrement, return_true])
                return [index for index in result if index >= 0]
            result.extend([advance_previous, advance_actual])
        result.extend([loop, return_false])
        return [index for index in result if index >= 0]

    @classmethod
    def _expand_lifecycle(cls, operation_name: str, lines: list[str], before_state: dict[str, Any]) -> list[int]:
        start_token = "void th_destruir(" if operation_name == "destroy_table" else "void th_vaciar("
        start = cls._find(lines, start_token)
        defensive = cls._find(lines, "if (!tabla || !tabla->buckets)", start)
        result = [start, defensive]
        if operation_name == "destroy_table":
            call_clear = cls._find(lines, "th_vaciar(tabla);", start)
            result.append(call_clear)
            clear_start = cls._find(lines, "void th_vaciar(", call_clear + 1)
            if clear_start >= 0:
                result.extend(cls._clear_body(lines, before_state, clear_start))
            for token in ("free(tabla->buckets);", "tabla->buckets = NULL;", "tabla->capacidad = 0;", "tabla->cantidad = 0;"):
                result.append(cls._find(lines, token, max(call_clear, 0)))
            return [index for index in result if index >= 0]
        result.extend(cls._clear_body(lines, before_state, start, include_start=False))
        return [index for index in result if index >= 0]

    @classmethod
    def _clear_body(cls, lines: list[str], before_state: dict[str, Any], start: int, *, include_start: bool = True) -> list[int]:
        defensive = cls._find(lines, "if (!tabla || !tabla->buckets)", start)
        loop_bucket = cls._find(lines, "for (int i = 0; i < tabla->capacidad; i++)", start)
        actual = cls._find(lines, "THNodo *actual = tabla->buckets[i];", loop_bucket)
        loop_node = cls._find(lines, "while (actual != NULL)", actual)
        next_node = cls._find(lines, "THNodo *siguiente = actual->siguiente;", loop_node)
        free = cls._find(lines, "free(actual);", next_node)
        advance = cls._find(lines, "actual = siguiente;", free)
        null_bucket = cls._find(lines, "tabla->buckets[i] = NULL;", advance)
        count = cls._find(lines, "tabla->cantidad = 0;", null_bucket)
        result = [start, defensive] if include_start else []
        for bucket in before_state.get("buckets") or []:
            if not isinstance(bucket, dict):
                continue
            result.extend([loop_bucket, actual])
            for _entry in bucket.get("entries") or []:
                result.extend([loop_node, next_node, free, advance])
            result.extend([loop_node, null_bucket])
        result.append(count)
        return [index for index in result if index >= 0]
