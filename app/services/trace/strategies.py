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





    @staticmethod


    def _stack_value(state: dict[str, Any]) -> Any:


        """Return the value that was pushed or is currently at TOP."""


        items = list(state.get("items") or [])


        if not items:


            return None


        first = items[0]


        return first.get("value") if isinstance(first, dict) else first





    @classmethod


    def _build_stack_boundaries(


        cls,


        before_state: dict[str, Any],


        after_state: dict[str, Any],


        step_lines: list[str],


    ) -> list[dict[str, Any]]:


        """Model the observable C lifetime of a stack node.





        A generic list diff cannot tell an allocation from the assignment that


        publishes it through ``*p``.  For a stack that distinction is central


        to the lesson: a node exists in ``aux`` after ``malloc`` but is not part


        of the stack until ``*p = aux``.  Likewise, a popped node remains owned


        by ``aux`` until the following ``free(aux)``.


        """


        before_items = list(before_state.get("items") or [])


        after_items = list(after_state.get("items") or [])


        is_push = any("pila_apilar(" in str(line) for line in step_lines)


        is_pop = any("pila_desapilar(" in str(line) for line in step_lines)


        current = deepcopy(before_state)


        states = [deepcopy(current)]





        if is_push:


            pushed_value = cls._stack_value(after_state)


            previous_top = "NULL" if not before_items else "TOP"


            for raw_line in step_lines:


                line = str(raw_line).strip().lower()


                if "malloc(" in line:


                    current["temporaries"] = {


                        "aux": {"allocated": True, "value": None, "next": None}


                    }


                elif "aux->nro" in line:


                    current["temporaries"] = {


                        "aux": {"allocated": True, "value": pushed_value, "next": None}


                    }


                elif "aux->sgte" in line:


                    current["temporaries"] = {


                        "aux": {"allocated": True, "value": pushed_value, "next": previous_top}


                    }


                elif "*p = aux" in line:


                    current = deepcopy(after_state)


                states.append(deepcopy(current))


            return states





        if is_pop:


            removed_value = cls._stack_value(before_state)


            next_top = "NULL" if not after_items else "TOP"


            for raw_line in step_lines:


                line = str(raw_line).strip().lower()


                if "aux = *p" in line:


                    # aux aliases the former TOP; it is not a second allocation.


                    current["aux"] = "TOP"


                    current["aux_value"] = removed_value


                elif "*p = aux->sgte" in line:


                    current = deepcopy(after_state)


                    current["aux"] = "nodo desconectado"


                    current["aux_value"] = removed_value


                    current["p"] = next_top


                elif "free(aux)" in line:


                    current = deepcopy(after_state)


                states.append(deepcopy(current))


            return states





        return []





    @classmethod


    def _build_queue_boundaries(


        cls,


        before_state: dict[str, Any],


        after_state: dict[str, Any],


        step_lines: list[str],


    ) -> list[dict[str, Any]]:


        """Model queue pointer changes on their exact C assignment lines."""


        before_items = list(before_state.get("items") or [])


        after_items = list(after_state.get("items") or [])


        is_enqueue = any("cola_encolar(" in str(line) for line in step_lines)


        is_dequeue = any("cola_desencolar(" in str(line) for line in step_lines)


        is_clear = any("cola_vaciar(" in str(line) for line in step_lines)


        def with_queue_pointers(state: dict[str, Any], *, delante: str | None = None, atras: str | None = None) -> dict[str, Any]:


            snapshot = deepcopy(state)


            items = list(snapshot.get("items") or [])


            snapshot["delante"] = delante if delante is not None else ("N1" if items else "NULL")


            snapshot["atras"] = atras if atras is not None else (f"N{len(items)}" if items else "NULL")


            return snapshot





        current = with_queue_pointers(before_state)


        states = [deepcopy(current)]





        if is_enqueue:


            value = after_items[-1].get("value") if after_items and isinstance(after_items[-1], dict) else None


            for raw_line in step_lines:


                line = str(raw_line).strip().lower()


                if "malloc(" in line:


                    current["temporaries"] = {"aux": {"allocated": True, "value": None, "next": None}}


                elif "aux->nro" in line:


                    current["temporaries"] = {"aux": {"allocated": True, "value": value, "next": None}}


                elif "aux->sgte = null" in line:


                    current["temporaries"] = {"aux": {"allocated": True, "value": value, "next": "NULL"}}


                elif "q->delante = aux" in line:


                    current = with_queue_pointers(after_state, delante="N1", atras="NULL")


                    current["aux"] = "N1"


                elif "q->atras->sgte = aux" in line:


                    current = with_queue_pointers(after_state, atras="N%d" % len(before_items))


                    current["aux"] = f"N{len(after_items)}"


                elif "q->atras = aux" in line:


                    current = with_queue_pointers(after_state)


                    current["aux"] = f"N{len(after_items)}"


                states.append(deepcopy(current))


            states[-1] = deepcopy(after_state)


            return states





        if is_dequeue:


            removed = before_items[0].get("value") if before_items and isinstance(before_items[0], dict) else None


            for raw_line in step_lines:


                line = str(raw_line).strip().lower()


                if "aux = q->delante" in line:


                    current["aux"] = "DELANTE"


                    current["aux_value"] = removed


                elif "q->delante = aux->sgte" in line:


                    current = with_queue_pointers(after_state)


                    current["aux"] = "nodo desconectado"


                    current["aux_value"] = removed


                    if not after_items:


                        current["atras"] = "N1"


                elif "q->atras = null" in line:


                    current = with_queue_pointers(after_state, delante="NULL", atras="NULL")


                    current["aux"] = "nodo desconectado"


                    current["aux_value"] = removed


                    current["atras"] = "NULL"


                elif "free(aux)" in line:


                    current = with_queue_pointers(after_state)


                states.append(deepcopy(current))


            states[-1] = deepcopy(after_state)


            return states





        if is_clear:


            working = list(before_items)


            for raw_line in step_lines:


                line = str(raw_line).strip().lower()


                if "aux = q->delante" in line and working:


                    current["aux"] = "DELANTE"


                    first = working[0]


                    current["aux_value"] = first.get("value") if isinstance(first, dict) else first


                elif "q->delante = aux->sgte" in line and working:


                    removed = working.pop(0)


                    current = with_queue_pointers({**before_state, "items": deepcopy(working), "size": len(working), "empty": not working})


                    current["aux"] = "nodo desconectado"


                    current["aux_value"] = removed.get("value") if isinstance(removed, dict) else removed


                    if not working:


                        current["atras"] = "N1"


                elif "free(aux)" in line:


                    current.pop("aux", None)


                    # aux_value is retained for the pedagogy frame that records free.


                elif "q->delante = null" in line:


                    current = with_queue_pointers(after_state, delante="NULL", atras="NULL")


                elif "q->atras = null" in line:


                    current = with_queue_pointers(after_state, delante="NULL", atras="NULL")


                states.append(deepcopy(current))


            states[-1] = deepcopy(after_state)


            return states





        return []





    @classmethod


    def _build_priority_queue_boundaries(


        cls,


        before_state: dict[str, Any],


        after_state: dict[str, Any],


        step_lines: list[str],


    ) -> list[dict[str, Any]]:


        """Mirror priority-queue links, candidate scans, and node lifetimes."""


        joined = "\n".join(str(line) for line in step_lines).lower()


        if not any(name in joined for name in ("cp_encolar(", "cp_desencolar(", "cp_frente(", "cp_vaciar(")):


            return []





        before_items = list(before_state.get("items") or [])


        after_items = list(after_state.get("items") or [])


        current = deepcopy(before_state)


        current["delante"] = "N1" if before_items else "NULL"


        current["atras"] = f"N{len(before_items)}" if before_items else "NULL"


        current["cantidad"] = len(before_items)


        current["node_ids"] = [f"N{i+1}" for i in range(len(before_items))]


        if before_items and any(name in joined for name in ("cp_desencolar(", "cp_frente(")):


            current["out_index"] = 0


            current["scan_complete"] = False


        states = [deepcopy(current)]





        def priority(item: Any) -> Any:


            return item.get("priority") if isinstance(item, dict) else None





        def refresh_out_index(items: list[Any]) -> int:


            if not items:


                return -1


            return min(range(len(items)), key=lambda index: (priority(items[index]), index))





        def set_items(items: list[Any], *, front: str | None = None, rear: str | None = None,


                      count: int | None = None, **extra: Any) -> None:


            nonlocal current


            current = deepcopy(current)


            current["items"] = deepcopy(items)


            current["size"] = len(items)


            current["empty"] = not items


            current["out_index"] = refresh_out_index(items)


            current["delante"] = front if front is not None else ("N1" if items else "NULL")


            current["atras"] = rear if rear is not None else (f"N{len(items)}" if items else "NULL")


            current["cantidad"] = len(before_items) if count is None else count


            current["title"] = after_state.get("title", current.get("title"))


            current["kind"] = after_state.get("kind", current.get("kind"))


            current.update(extra)





        operation = next((name for name in ("cp_encolar(", "cp_desencolar(", "cp_frente(", "cp_vaciar(") if name in joined), "")


        if operation == "cp_encolar(":


            if len(after_items) <= len(before_items):


                return []


            inserted = after_items[-1]


            linked_items = deepcopy(before_items)


            for raw_line in step_lines:


                line = str(raw_line).strip().lower()


                if "nuevo = (cpnodo *)malloc(" in line:


                    current["temporaries"] = {"nuevo": {"allocated": True, "valor": None, "prioridad": None, "sgte": None}}


                elif "nuevo->valor = valor" in line:


                    current.setdefault("temporaries", {}).setdefault("nuevo", {})["valor"] = inserted.get("value")


                elif "nuevo->prioridad = prioridad" in line:


                    current.setdefault("temporaries", {}).setdefault("nuevo", {})["prioridad"] = inserted.get("priority")


                elif "nuevo->sgte = null" in line:


                    current.setdefault("temporaries", {}).setdefault("nuevo", {})["sgte"] = "NULL"


                elif "cola->delante = nuevo" in line or "cola->atras->sgte = nuevo" in line:


                    linked_items = deepcopy(before_items) + [deepcopy(inserted)]


                    front = "N1"


                    rear = f"N{len(before_items)}" if before_items else "NULL"


                    set_items(linked_items, front=front, rear=rear, count=len(before_items))


                elif "cola->atras = nuevo" in line:


                    set_items(linked_items, front="N1", rear=f"N{len(linked_items)}", count=len(before_items))


                elif "cola->cantidad++" in line:


                    set_items(linked_items, front="N1", rear=f"N{len(linked_items)}", count=len(linked_items))


                    current.pop("temporaries", None)


                states.append(deepcopy(current))


            states[-1] = deepcopy(after_state)


            return states





        if operation in {"cp_desencolar(", "cp_frente("}:


            if not before_items:


                states.extend(deepcopy(current) for _ in step_lines)


                states[-1] = deepcopy(after_state)


                return states


            dequeue = operation == "cp_desencolar("


            target_index = min(range(len(before_items)), key=lambda index: (priority(before_items[index]), index))


            target = before_items[target_index]


            actual_index = 0 if dequeue else 1


            best_index = 0


            scan_index = -1


            for raw_line in step_lines:


                line = str(raw_line).strip().lower()


                if line == "actual = cola->delante->sgte;":


                    current["actual"] = "N2" if len(before_items) > 1 else "NULL"


                elif line == "actual = cola->delante;":


                    current["actual"] = "N1"


                elif line == "objetivo = cola->delante;":


                    current["objetivo"] = "N1"


                elif line == "prev = null;":


                    current["prev"] = "NULL"


                elif line == "objetivo = actual;":


                    if "pending_candidate" in current:


                        best_index = int(current.pop("pending_candidate"))


                    current["objetivo"] = f"N{best_index + 1}"


                    current["out_index"] = best_index


                elif line == "objetivoprev = null;":


                    current["objetivoPrev"] = "NULL"


                elif line.startswith("while (actual != null)"):


                    scan_index += 1


                    if dequeue:


                        actual_index = scan_index


                    current["actual"] = f"N{actual_index + 1}" if actual_index < len(before_items) else "NULL"


                    current["scan_complete"] = actual_index >= len(before_items)


                elif "if (actual->prioridad < objetivo->prioridad)" in line:


                    if actual_index < len(before_items) and actual_index > 0:


                        if priority(before_items[actual_index]) < priority(before_items[best_index]):


                            current["pending_candidate"] = actual_index


                elif line == "objetivoprev = prev;":


                    current["objetivoPrev"] = current.get("prev", "NULL")


                elif line == "prev = actual;":


                    current["prev"] = current.get("actual", "NULL")


                elif line == "actual = actual->sgte;":


                    actual_index += 1


                    current["actual"] = f"N{actual_index + 1}" if actual_index < len(before_items) else "NULL"


                elif "*valor = objetivo->valor" in line:


                    current["valor"] = target.get("value")


                elif "*prioridad = objetivo->prioridad" in line:


                    current["prioridad"] = target.get("priority")


                elif "cola->delante = objetivo->sgte" in line:


                    remaining = deepcopy(before_items[1:])


                    set_items(remaining, front="N2" if remaining else "NULL",


                              rear=f"N{len(before_items)}" if remaining else "N1",


                              count=len(before_items), node_ids=[f"N{i+1}" for i in range(len(before_items)) if i != target_index])


                    current["objetivo"] = f"N{target_index+1}"


                    current["temporaries"] = {"objetivo": {"allocated": True, "value": target.get("value"), "priority": target.get("priority"), "node_id": f"N{target_index+1}"}}


                    current["out_index"] = -1


                    current["candidate_detached"] = True


                elif "objetivoprev->sgte = objetivo->sgte" in line:


                    remaining = deepcopy(before_items[:target_index] + before_items[target_index + 1:])


                    set_items(remaining, front="N1", rear=f"N{len(before_items)}", count=len(before_items), node_ids=[f"N{i+1}" for i in range(len(before_items)) if i != target_index])


                    current["objetivo"] = f"N{target_index+1}"


                    current["temporaries"] = {"objetivo": {"allocated": True, "value": target.get("value"), "priority": target.get("priority"), "node_id": f"N{target_index+1}"}}


                    current["out_index"] = -1


                    current["candidate_detached"] = True


                elif "cola->atras = objetivoprev" in line:


                    current["atras"] = f"N{target_index}" if target_index > 0 else "NULL"


                elif "cola->atras = null" in line:


                    current["atras"] = "NULL"


                elif "free(objetivo)" in line:


                    current.pop("temporaries", None)


                    current["objetivo"] = "liberado"


                    for alias in ("prev", "objetivoPrev", "actual"):


                        if current.get(alias) == f"N{target_index+1}":


                            current[alias] = "liberado"


                elif "cola->cantidad--" in line:


                    current["cantidad"] = max(0, len(before_items) - 1)


                states.append(deepcopy(current))


            states[-1] = deepcopy(after_state)


            return states





        if operation == "cp_vaciar(":


            working = deepcopy(before_items)


            freed_count = 0


            current["aux"] = "N1" if working else "NULL"


            for raw_line in step_lines:


                line = str(raw_line).strip().lower()


                if "cola->delante = next" in line and working:


                    freed_item = working[0]


                    working.pop(0)


                    freed_count += 1


                    set_items(


                        working,


                        front=f"N{freed_count + 1}" if working else "NULL",


                        rear=f"N{len(before_items)}" if working else f"N{freed_count}",


                        count=len(before_items) - freed_count + 1,


                    )


                    current["aux"] = "nodo desconectado"


                    current["temporaries"] = {


                        "aux": {


                            "allocated": True,


                            "value": freed_item.get("value"),


                            "priority": freed_item.get("priority"),


                        }


                    }


                elif "cola->atras = null" in line:


                    current["atras"] = "NULL"


                elif "free(aux)" in line:


                    current["freed_aux"] = freed_count


                    current.pop("temporaries", None)


                    current["aux"] = "liberado"


                elif "cola->cantidad--" in line:


                    current["cantidad"] = max(0, len(before_items) - freed_count)


                elif "aux = next" in line:


                    current.pop("temporaries", None)


                    current["aux"] = f"N{freed_count + 1}" if working else "NULL"


                elif "cola->cantidad = 0" in line:


                    current["cantidad"] = 0


                states.append(deepcopy(current))


            states[-1] = deepcopy(after_state)


            return states


        return []








    @classmethod


    def _build_linked_list_boundaries(


        cls,


        before_state: dict[str, Any],


        after_state: dict[str, Any],


        step_lines: list[str],


        payload: dict[str, Any] | None = None,


    ) -> list[dict[str, Any]]:


        """Represent ``tad_lista.c`` mutations on their exact C lines.





        In particular, a freshly allocated ``q`` is a temporary node until an


        assignment publishes it through ``*lista`` or a reachable ``sgte``.


        Removing a node follows the inverse rule: it disappears from the list


        at the pointer reassignment and is only marked freed at ``free``.


        """


        before_items = list(before_state.get("items") or [])


        after_items = list(after_state.get("items") or [])


        joined = "\n".join(str(line) for line in step_lines).lower()


        if not any(token in joined for token in (


            "lista_insertar_", "lista_eliminar_", "lista_limpiar(", "lista_buscar_elemento(", "lista, head",


        )):


            return []





        def state_with_lista(state: dict[str, Any]) -> dict[str, Any]:


            snapshot = deepcopy(state)


            items = list(snapshot.get("items") or [])


            snapshot["lista"] = "N1" if items else "NULL"


            return snapshot





        def item_value(items: list[Any], index: int) -> Any:


            if not 0 <= index < len(items):


                return None


            item = items[index]


            return item.get("value") if isinstance(item, dict) else item





        current = state_with_lista(before_state)


        states = [deepcopy(current)]


        is_insert = any(token in joined for token in (


            "lista_insertar_inicio(", "lista_insertar_final(", "lista_insertar_elemento(",


        ))


        is_clear = "while (*lista != null)" in joined and (


            "lista_limpiar(" in joined or "lista_eliminar_elemento(lista, head)" in joined or "q = *lista" in joined


        )


        # Preserve multiplicity: an inserted duplicate is still a distinct


        # allocation, even though it has the same nro as another node.


        before_tokens = [cls._stable_token(item) for item in before_items]


        inserted_value = None


        for item in after_items:


            token = cls._stable_token(item)


            if token in before_tokens:


                before_tokens.remove(token)


            else:


                inserted_value = item.get("value") if isinstance(item, dict) else item


                break


        if inserted_value is None and len(after_items) > len(before_items):


            inserted_value = item_value(after_items, 0)





        if "lista_buscar_elemento(" in joined:


            nodes = [{"id": f"N{i+1}", "value": item_value(before_items, i),


                      "next": f"N{i+2}" if i+1 < len(before_items) else "NULL"}


                     for i in range(len(before_items))]


            head = nodes[0]["id"] if nodes else "NULL"


            q = i = encontrado = None





            def search_snapshot() -> dict[str, Any]:


                snapshot = deepcopy(before_state)


                snapshot.update(search_model=True, lista=head, head=head,


                                node_ids=[node["id"] for node in nodes],


                                heap_nodes=[{**node, "status": "linked"} for node in nodes])


                if q is not None:


                    snapshot["q"] = q


                if i is not None:


                    snapshot.update(i=i, encontrado=encontrado)


                return snapshot





            states = [search_snapshot()]


            for raw_line in step_lines:


                line = str(raw_line).strip().lower()


                if line == "int i = 1, encontrado = 0;":


                    i, encontrado = 1, 0


                elif line == "tlista q = lista;":


                    q = head


                elif line == "encontrado = 1;":


                    encontrado = 1


                elif line == "q = q->sgte;":


                    q = next(node["next"] for node in nodes if node["id"] == q)


                elif line == "i++;":


                    i += 1


                states.append(search_snapshot())


            states[-1] = deepcopy(after_state)


            return states





        if is_insert:


            nodes = [{"id": f"N{i+1}", "value": item_value(before_items, i),


                      "next": f"N{i+2}" if i+1 < len(before_items) else "NULL"}


                     for i in range(len(before_items))]


            head = nodes[0]["id"] if nodes else "NULL"


            q = t = i = None


            freed_q = None


            allocation_id = f"N{len(nodes)+1}"


            value = (payload or {}).get("value", inserted_value)


            if value is not None:


                value = int(value)


            local_names = ["q"] if "lista_insertar_inicio(" in joined else ["q", "t"]





            def insert_snapshot() -> dict[str, Any]:


                by_id = {node["id"]: node for node in nodes}


                reachable = []


                cursor = head


                while cursor != "NULL":


                    reachable.append(cursor)


                    cursor = by_id[cursor]["next"]


                snapshot = deepcopy(before_state)


                snapshot.update(insert_model=True, lista="&cabeza", head=head,


                                local_pointer_names=local_names, node_ids=reachable,


                                items=[{"value": by_id[node_id]["value"]} for node_id in reachable],


                                size=len(reachable), empty=not reachable,


                                heap_nodes=[{**node, "status": "linked" if node["id"] in reachable else "temporary"}


                                            for node in nodes])


                for name, value in (("q", q), ("t", t), ("i", i)):


                    if value is not None:


                        snapshot[name] = value


                if freed_q is not None:


                    snapshot["freed_q"] = freed_q


                return snapshot





            states = [insert_snapshot()]


            for raw_line in step_lines:


                line = str(raw_line).strip().lower()


                if line == "tlista q = crearnodolista(valor);":


                    q = allocation_id


                    nodes.append({"id": q, "value": value, "next": "NULL"})


                elif line == "tlista t = *lista;":


                    t = head


                elif line == "int i = 1;":


                    i = 1


                elif line == "i++;":


                    i += 1


                elif line == "t = t->sgte;":


                    t = next(node["next"] for node in nodes if node["id"] == t)


                elif line == "q->sgte = *lista;":


                    next(node for node in nodes if node["id"] == q)["next"] = head


                elif line == "q->sgte = t->sgte;":


                    successor = next(node["next"] for node in nodes if node["id"] == t)


                    next(node for node in nodes if node["id"] == q)["next"] = successor


                elif line == "*lista = q;":


                    head = q


                elif line == "t->sgte = q;":


                    next(node for node in nodes if node["id"] == t)["next"] = q


                elif line == "free(q);":


                    freed_q = q


                    nodes = [node for node in nodes if node["id"] != q]


                    q = f"indeterminado (liberado {freed_q})"


                states.append(insert_snapshot())


            states[-1] = deepcopy(after_state)


            return states





        if is_clear:


            # Stable identities belong to allocations, not to their current


            # position or value. A disconnected q stays live until free(q).


            nodes = [{"id": f"N{i+1}", "value": item_value(before_items, i),


                      "next": f"N{i+2}" if i+1 < len(before_items) else "NULL"}


                     for i in range(len(before_items))]


            head = nodes[0]["id"] if nodes else "NULL"


            q = None  # C local is uninitialized until q = *lista.


            freed_q = None





            def clear_snapshot() -> dict[str, Any]:


                by_id = {node["id"]: node for node in nodes}


                reachable = []


                cursor = head


                while cursor != "NULL":


                    reachable.append(cursor)


                    cursor = by_id[cursor]["next"]


                snapshot = deepcopy(before_state)


                snapshot.update(clear_model=True, lista="&cabeza", head=head,


                                node_ids=reachable,


                                items=[{"value": by_id[node_id]["value"]} for node_id in reachable],


                                size=len(reachable), empty=not reachable,


                                heap_nodes=[{**node, "status": "linked" if node["id"] in reachable else "detached"}


                                            for node in nodes])


                if q is not None:


                    snapshot["q"] = q


                if freed_q is not None:


                    snapshot["freed_q"] = freed_q


                return snapshot





            states = [clear_snapshot()]


            for raw_line in step_lines:


                line = str(raw_line).strip().lower()


                if line == "q = *lista;":


                    q = head


                    freed_q = None


                elif line == "*lista = q->sgte;":


                    head = next(node["next"] for node in nodes if node["id"] == q)


                elif line == "free(q);":


                    freed_q = q


                    nodes = [node for node in nodes if node["id"] != q]


                    # C makes a pointer to freed storage indeterminate. Never


                    # present q as a valid address or dereference it afterward.


                    q = f"indeterminado (liberado {freed_q})"


                states.append(clear_snapshot())


            # The planner includes the actual closing function brace: only


            # that scope-exit event drops locals and restores canonical state.


            states[-1] = deepcopy(after_state)


            return states





        if "lista_eliminar_repetidos(" in joined:


            nodes = [{"id": f"N{i+1}", "value": item_value(before_items, i),


                      "next": f"N{i+2}" if i+1 < len(before_items) else "NULL"}


                     for i in range(len(before_items))]


            head = nodes[0]["id"] if nodes else "NULL"


            q = ant = temp = None  # Not initialized until the declaration executes.


            freed_temp = None





            def delete_snapshot() -> dict[str, Any]:


                by_id = {node["id"]: node for node in nodes}


                reachable = []


                cursor = head


                while cursor != "NULL":


                    reachable.append(cursor)


                    cursor = by_id[cursor]["next"]


                snapshot = deepcopy(before_state)


                snapshot.update(delete_model=True, delete_all=True, lista="&cabeza", head=head,


                                node_ids=reachable,


                                items=[{"value": by_id[node_id]["value"]} for node_id in reachable],


                                size=len(reachable), empty=not reachable,


                                heap_nodes=[{**node, "status": "linked" if node["id"] in reachable else "detached"}


                                            for node in nodes])


                if q is not None:


                    snapshot.update(q=q, ant=ant)


                if temp is not None:


                    snapshot["temp"] = temp


                if freed_temp is not None:


                    snapshot["freed_temp"] = freed_temp


                return snapshot





            states = [delete_snapshot()]


            for raw_line in step_lines:


                line = str(raw_line).strip().lower()


                if line == "tlista q = *lista, ant = null;":


                    q, ant = head, "NULL"


                elif line == "tlista temp = q;":


                    temp = q


                elif line == "ant = q;":


                    ant = q


                elif line == "q = q->sgte;":


                    q = next(node["next"] for node in nodes if node["id"] == q)


                elif line == "*lista = q->sgte;":


                    head = next(node["next"] for node in nodes if node["id"] == q)


                elif line == "q = *lista;":


                    q = head


                elif line == "ant->sgte = q->sgte;":


                    successor = next(node["next"] for node in nodes if node["id"] == q)


                    next(node for node in nodes if node["id"] == ant)["next"] = successor


                elif line == "q = ant->sgte;":


                    q = next(node["next"] for node in nodes if node["id"] == ant)


                elif line == "free(temp);":


                    freed_temp = temp


                    nodes = [node for node in nodes if node["id"] != temp]


                    temp = f"indeterminado (liberado {freed_temp})"


                states.append(delete_snapshot())


            # Explicit return or actual final brace ends local scope; canonical


            # state remains the adapter result. Pedagogy keeps heap identities.


            states[-1] = deepcopy(after_state)


            return states





        if "lista_eliminar_elemento(" in joined:


            nodes = [{"id": f"N{i+1}", "value": item_value(before_items, i),


                      "next": f"N{i+2}" if i+1 < len(before_items) else "NULL"}


                     for i in range(len(before_items))]


            head = nodes[0]["id"] if nodes else "NULL"


            p = ant = None  # Not initialized until the declaration executes.


            freed_p = None





            def delete_snapshot() -> dict[str, Any]:


                by_id = {node["id"]: node for node in nodes}


                reachable = []


                cursor = head


                while cursor != "NULL":


                    reachable.append(cursor)


                    cursor = by_id[cursor]["next"]


                snapshot = deepcopy(before_state)


                snapshot.update(delete_model=True, lista="&cabeza", head=head,


                                node_ids=reachable,


                                items=[{"value": by_id[node_id]["value"]} for node_id in reachable],


                                size=len(reachable), empty=not reachable,


                                heap_nodes=[{**node, "status": "linked" if node["id"] in reachable else "detached"}


                                            for node in nodes])


                if p is not None:


                    snapshot.update(p=p, ant=ant)


                if freed_p is not None:


                    snapshot["freed_p"] = freed_p


                return snapshot





            states = [delete_snapshot()]


            for raw_line in step_lines:


                line = str(raw_line).strip().lower()


                if line == "tlista p = *lista, ant = null;":


                    p, ant = head, "NULL"


                elif line == "ant = p;":


                    ant = p


                elif line == "p = p->sgte;":


                    p = next(node["next"] for node in nodes if node["id"] == p)


                elif line == "*lista = p->sgte;":


                    head = next(node["next"] for node in nodes if node["id"] == p)


                elif line == "ant->sgte = p->sgte;":


                    successor = next(node["next"] for node in nodes if node["id"] == p)


                    next(node for node in nodes if node["id"] == ant)["next"] = successor


                elif line == "free(p);":


                    freed_p = p


                    nodes = [node for node in nodes if node["id"] != p]


                    p = f"indeterminado (liberado {freed_p})"


                states.append(delete_snapshot())


            # Explicit return or actual final brace ends local scope; canonical


            # state remains the adapter result. Pedagogy keeps heap identities.


            states[-1] = deepcopy(after_state)


            return states





        return []





    @classmethod


    def _build_circular_list_boundaries(


        cls,


        before_state: dict[str, Any],


        after_state: dict[str, Any],


        step_lines: list[str],


        payload: dict[str, Any] | None = None,


    ) -> list[dict[str, Any]]:


        """Model circular-list roots, tail closure, temporary nodes, and frees."""


        joined = "\n".join(str(line) for line in step_lines).lower()


        operation = next((name for name in (


            "lcir_insertar_inicio(", "lcir_insertar_final(",


            "lcir_eliminar_inicio(", "lcir_eliminar_primero(",


            "lcir_buscar_posiciones(", "lcir_invertir(", "lcir_destruir(",


        ) if name in joined), None)


        if operation is None:


            return []





        if operation in {"lcir_eliminar_inicio(", "lcir_buscar_posiciones(", "lcir_eliminar_primero(", "lcir_destruir(", "lcir_invertir("}:


            # Observe actual C writes independently of reachability and final API data.


            original = list(before_state.get("items") or [])


            nodes = [{"id":f"N{i+1}", "value":item["value"],


                      "next":f"N{i+2}" if i+1<len(original) else "N1"}


                     for i,item in enumerate(original)]


            head = "N1" if nodes else "NULL"


            tail = f"N{len(nodes)}" if nodes else "NULL"


            quantity = len(nodes)


            actual = previous = next_node = prev = curr = old_head = None


            freed = None


            search = operation == "lcir_buscar_posiciones("


            reverse = operation == "lcir_invertir("


            clear = operation == "lcir_destruir("


            found = position = None


            positions: list[int] = []





            def snapshot() -> dict[str, Any]:


                by_id = {node["id"]:node for node in nodes}


                reachable = []


                cursor = head


                while cursor in by_id and cursor not in reachable:


                    reachable.append(cursor)


                    cursor = by_id[cursor]["next"]


                state = deepcopy(before_state)


                # circular_insert_model is the existing shared circular heap projection.


                state.update(circular_insert_model=True, circular_delete_model=not search and not reverse, circular_clear_model=clear, circular_reverse_model=reverse, circular_search_model=search,


                             circular_delete_by_value_model=operation=="lcir_eliminar_primero(",


                             lista="&lc", cabeza=head, cola=tail,


                             cantidad=quantity, size=quantity, empty=head=="NULL",


                             reachable_count=len(reachable), node_ids=reachable,


                             cycle_target=cursor, active_function=operation[:-1],


                             items=[{"value":by_id[key]["value"]} for key in reachable],


                             heap_nodes=[{**node,"status":"linked" if node["id"] in reachable else "detached"} for node in nodes],


                             cola_sgte=by_id[tail]["next"] if tail in by_id else "NULL")


                if search:


                    state.update(destino="&posiciones", capacidad=max(1,len(original)), search_positions=deepcopy(positions))


                    if found is not None:state["encontrados"]=found


                    if position is not None:state["pos"]=position


                if actual is not None:state["actual"]=actual


                if previous is not None:state["anterior"]=previous


                for name,target in (("next",next_node),("prev",prev),("curr",curr),("old_head",old_head)):


                    if target is not None:state[name]=target


                if freed is not None:state["freed_actual"]=freed


                return state





            states = [snapshot()]


            for raw in step_lines:


                line = str(raw).strip().lower()


                by_id = {node["id"]:node for node in nodes}


                if line == "actual = lista->cabeza;":actual = head


                elif search and line == "int encontrados = 0;":found = 0


                elif search and line == "int pos = 1;":position = 1


                elif search and line == "destino[encontrados] = pos;":positions.append(position)


                elif search and line == "encontrados++;":found += 1


                elif line == "actual = actual->sgte;":actual = by_id[actual]["next"]


                elif search and line == "pos++;":position += 1


                elif line == "next = actual->sgte;":next_node = by_id[actual]["next"]


                elif line == "lista->cabeza = next;":head = next_node


                elif line == "actual = next;":actual = next_node


                elif line == "prev = lista->cola;":prev = tail


                elif line == "curr = lista->cabeza;":curr = head


                elif line == "next = curr->sgte;":next_node = by_id[curr]["next"]


                elif line == "curr->sgte = prev;":by_id[curr]["next"] = prev


                elif line == "prev = curr;":prev = curr


                elif line == "curr = next;":curr = next_node


                elif line == "old_head = lista->cabeza;":old_head = head


                elif line == "lista->cabeza = lista->cola;":head = tail


                elif line == "lista->cola = old_head;":tail = old_head


                elif line == "anterior = lista->cola;":previous = tail


                elif line == "anterior = actual;":previous = actual


                elif line == "anterior->sgte = actual->sgte;":by_id[previous]["next"] = by_id[actual]["next"]


                elif line == "lista->cola = anterior;":tail = previous


                elif line == "lista->cabeza = null;":head = "NULL"


                elif line == "lista->cola = null;":tail = "NULL"


                elif line == "lista->cantidad = 0;":quantity = 0


                elif line == "lista->cabeza = actual->sgte;":head = by_id[actual]["next"]


                elif line == "lista->cola->sgte = lista->cabeza;":by_id[tail]["next"] = head


                elif line == "lista->cantidad--;":quantity -= 1


                elif line == "free(actual);":


                    freed = actual


                    if previous==actual:previous="indeterminado (liberado)"


                    if next_node==actual:next_node="indeterminado (liberado)"


                    nodes = [node for node in nodes if node["id"] != actual]


                    actual = "indeterminado (liberado)"


                states.append(snapshot())


            states[-1] = deepcopy(after_state)


            return states





        if operation in {"lcir_insertar_inicio(", "lcir_insertar_final("}:


            # Allocation identities and actual root/link writes, not final-state diffs.


            original = list(before_state.get("items") or [])


            nodes = [{"id":f"N{i+1}", "value":item["value"],


                      "next":f"N{i+2}" if i+1<len(original) else "N1"}


                     for i,item in enumerate(original)]


            head = "N1" if nodes else "NULL"


            tail = f"N{len(nodes)}" if nodes else "NULL"


            quantity = len(nodes)


            allocated = f"N{len(nodes)+1}"


            new = local_node = None


            active = operation[:-1]


            value = (payload or {}).get("value")


            if value is None:


                target = list(after_state.get("items") or [])


                value = target[0 if operation=="lcir_insertar_inicio(" else -1]["value"]


            value = int(value)





            def snapshot() -> dict[str, Any]:


                by_id = {node["id"]:node for node in nodes}


                reachable = []


                cursor = head


                while cursor != "NULL" and cursor not in reachable:


                    reachable.append(cursor)


                    cursor = by_id[cursor]["next"]


                state = deepcopy(before_state)


                state.update(circular_insert_model=True, lista="&lc", cabeza=head,


                             cola=tail, cantidad=quantity, size=quantity,


                             reachable_count=len(reachable), empty=head=="NULL",


                             node_ids=reachable, cycle_target=cursor,


                             items=[{"value":by_id[key]["value"]} for key in reachable],


                             active_function=active,


                             heap_nodes=[{**node,"status":"linked" if node["id"] in reachable else "temporary"} for node in nodes])


                if new is not None:state["nuevo"]=new


                if local_node is not None:state["nodo"]=local_node


                state["cola_sgte"] = by_id[tail]["next"] if tail!="NULL" else "NULL"


                return state





            states = [snapshot()]


            for raw in step_lines:


                line = str(raw).strip().lower()


                if line.startswith("static lcirnodo *lcir_crear_nodo("):


                    active = "lcir_crear_nodo"


                elif "malloc(sizeof(lcirnodo))" in line:


                    nodes.append({"id":allocated,"value":"sin inicializar","next":"sin inicializar"})


                    local_node = allocated


                elif line == "nodo->valor = valor;":


                    nodes[-1]["value"] = value


                elif line == "nodo->sgte = null;":


                    nodes[-1]["next"] = "NULL"


                elif line == "return nodo;":


                    local_node = None


                    active = operation[:-1]


                elif line == "nuevo = lcir_crear_nodo(valor);":


                    new = allocated


                elif line == "nuevo->sgte = nuevo;":


                    nodes[-1]["next"] = new


                elif line == "nuevo->sgte = lista->cabeza;":


                    nodes[-1]["next"] = head


                elif line == "lista->cola->sgte = nuevo;":


                    next(node for node in nodes if node["id"]==tail)["next"] = new


                elif line == "lista->cabeza = nuevo;":head = new


                elif line == "lista->cola = nuevo;":tail = new


                elif line == "lista->cantidad = 1;":quantity = 1


                elif line == "lista->cantidad++;":quantity += 1


                states.append(snapshot())


            # Keep the endpoint contract canonical; pedagogy projects surviving heap identities.


            states[-1] = deepcopy(after_state)


            return states





        original = deepcopy(list(before_state.get("items") or []))


        target = deepcopy(list(after_state.get("items") or []))


        current = deepcopy(before_state)


        current["cabeza"] = "N1" if original else "NULL"


        current["cola"] = f"N{len(original)}" if original else "NULL"


        current["cola_sgte"] = "N1" if original else "NULL"


        current["links"] = {f"N{i + 1}": f"N{i + 2}" for i in range(max(0, len(original) - 1))}


        if original:


            current["links"][f"N{len(original)}"] = "N1"


        states = [deepcopy(current)]


        before_values = [item.get("value") if isinstance(item, dict) else item for item in original]


        after_values = [item.get("value") if isinstance(item, dict) else item for item in target]


        payload_value = after_values[0] if len(after_values) > len(before_values) and operation == "lcir_insertar_inicio(" else (


            after_values[-1] if len(after_values) > len(before_values) else None


        )


        target_value = next((value for value in before_values if value not in after_values), None)


        if operation == "lcir_eliminar_primero(" and target_value is None:


            # A removed duplicate may still occur in the final value sequence;


            # identify the first-occurrence removal by the requested operation's


            # diff rather than value uniqueness.


            for index, value in enumerate(before_values):


                if before_values[:index] + before_values[index + 1:] == after_values:


                    target_value = value


                    break





        working = deepcopy(original)


        temp: dict[str, Any] | None = None


        cursor = 0


        position = 0


        found_positions: list[int] = []


        reversed_links = deepcopy(current["links"])


        removed_index = next((i for i, item in enumerate(original) if item == next((x for x in original if (x.get("value") if isinstance(x, dict) else x) == target_value), None)), None)





        for raw_line in step_lines:


            line = str(raw_line).strip().lower()


            if "malloc(sizeof(lcirnodo))" in line:


                temp = {"allocated": True, "value": None, "next": "NULL"}


                current["temporaries"] = {"nuevo": deepcopy(temp)}


            elif "nodo->valor = valor" in line and temp is not None:


                temp["value"] = payload_value


                current["temporaries"] = {"nuevo": deepcopy(temp)}


            elif "nodo->sgte = null" in line and temp is not None:


                temp["next"] = "NULL"


                current["temporaries"] = {"nuevo": deepcopy(temp)}


            elif "nuevo->sgte = nuevo" in line and temp is not None:


                temp["next"] = "nuevo"


                current["temporaries"] = {"nuevo": deepcopy(temp)}


            elif "nuevo->sgte = lista->cabeza" in line and temp is not None:


                temp["next"] = current.get("cabeza", "NULL")


                current["temporaries"] = {"nuevo": deepcopy(temp)}


            elif "lista->cola->sgte = nuevo" in line and temp is not None:


                current["cola_sgte"] = "nuevo"


            elif "lista->cabeza = nuevo" in line and temp is not None:


                working = deepcopy(target)


                current["items"] = deepcopy(working)


                current["size"] = len(working)


                current["empty"] = not working


                current["cabeza"] = "N1" if working else "NULL"


                current["links"] = {f"N{i + 1}": f"N{i + 2}" for i in range(max(0, len(working) - 1))}


                if working:


                    current["links"][f"N{len(working)}"] = "N1"


                    current["cola_sgte"] = "N1"


            elif "lista->cola = nuevo" in line and temp is not None:


                working = deepcopy(target)


                current["items"] = deepcopy(working)


                current["size"] = len(working)


                current["empty"] = not working


                current["cola"] = f"N{len(working)}" if working else "NULL"


                current["cola_sgte"] = "N1" if working else "NULL"


                current.pop("temporaries", None)


            elif "lista->cantidad = 1" in line and temp is not None:


                current["size"] = 1


            elif "lista->cantidad++" in line and temp is not None:


                current["size"] = len(target)


                current.pop("temporaries", None)


                current["links"] = {f"N{i + 1}": f"N{i + 2}" for i in range(max(0, len(target) - 1))}


                if target:


                    current["links"][f"N{len(target)}"] = "N1"


                    current["cola_sgte"] = "N1"


                    current["cabeza"] = "N1"


                    current["cola"] = f"N{len(target)}"


            elif "actual = lista->cabeza" in line:


                current["actual"] = "N1" if working else "NULL"


                cursor = 0


                if working:


                    current["actual_value"] = working[0].get("value") if isinstance(working[0], dict) else working[0]


                if operation in {"lcir_eliminar_inicio(", "lcir_eliminar_primero(", "lcir_destruir("} and working:


                    first_value = working[0].get("value") if isinstance(working[0], dict) else working[0]


                    current["temporaries"] = {"actual": {"allocated": True, "value": first_value, "next": "linked"}}


            elif "anterior = lista->cola" in line:


                current["anterior"] = f"N{len(working)}" if working else "NULL"


            elif "prev = lista->cola" in line:


                current["prev"] = f"N{len(working)}" if working else "NULL"


            elif "curr = lista->cabeza" in line:


                current["curr"] = "N1" if working else "NULL"


            elif "actual = actual->sgte" in line:


                cursor = (cursor + 1) % len(working) if working else 0


                current["actual"] = f"N{cursor + 1}" if working else "NULL"


                if working:


                    current["actual_value"] = working[cursor].get("value") if isinstance(working[cursor], dict) else working[cursor]


                if operation == "lcir_eliminar_primero(" and working:


                    actual_value = working[cursor].get("value") if isinstance(working[cursor], dict) else working[cursor]


                    current["temporaries"] = {"actual": {"allocated": True, "value": actual_value, "next": "linked"}}


            elif "anterior = actual" in line:


                current["anterior"] = current.get("actual", "NULL")


            elif "actual->sgte = prev" in line or "curr->sgte = prev" in line:


                node = current.get("actual" if "actual->" in line else "curr", "NULL")


                reversed_links[str(node)] = current.get("prev", "NULL")


                current["links"] = deepcopy(reversed_links)


            elif "prev = curr" in line:


                current["prev"] = current.get("curr", "NULL")


            elif "curr = next" in line:


                current["curr"] = current.get("next", "NULL")


            elif "next = curr->sgte" in line:


                node = current.get("curr", "NULL")


                current["next"] = reversed_links.get(str(node), "NULL")


            elif "lista->cabeza = lista->cola" in line:


                current["cabeza"] = current.get("cola", "NULL")


                working.reverse()


                current["items"] = deepcopy(working)


            elif "lista->cola = old_head" in line:


                current["cola"] = "N1" if working else "NULL"


                current["cola_sgte"] = current.get("cabeza", "NULL")


            elif "actual->valor == valor" in line:


                current["actual_index"] = cursor


                current["actual_value"] = before_values[cursor] if cursor < len(before_values) else None


            elif "encontrados++" in line:


                found_positions.append(cursor + 1)


                current["found_positions"] = deepcopy(found_positions)


            elif "pos++" in line:


                position += 1


                current["position"] = position


            elif "anterior->sgte = actual->sgte" in line and removed_index is not None:


                if removed_index < len(working):


                    working.pop(removed_index)


                current["items"] = deepcopy(working)


                current["size"] = len(working)


                current["empty"] = not working


                current["cola_sgte"] = "N1" if working else "NULL"


                current["temporaries"] = {"actual": {"allocated": True, "value": target_value, "next": "desconectado"}}


                current["actual_value"] = target_value


            elif "lista->cabeza = actual->sgte" in line:


                if removed_index == 0 and working:


                    working.pop(0)


                current["items"] = deepcopy(working)


                current["size"] = len(working)


                current["empty"] = not working


                current["cabeza"] = "N1" if working else "NULL"


                current["cola_sgte"] = "N1" if working else "NULL"


                current["temporaries"] = {"actual": {"allocated": True, "value": target_value, "next": "desconectado"}}


                current["actual_value"] = target_value


            elif "lista->cola = anterior" in line:


                if removed_index == len(before_values) - 1 and working:


                    working.pop()


                current["items"] = deepcopy(working)


                current["size"] = len(working)


                current["empty"] = not working


                current["cola"] = f"N{len(working)}" if working else "NULL"


                current["temporaries"] = {"actual": {"allocated": True, "value": target_value, "next": "desconectado"}}


                current["actual_value"] = target_value


            elif "lista->cabeza = null" in line:


                working = []


                current.update({"items": [], "size": 0, "empty": True, "cabeza": "NULL", "cola_sgte": "NULL"})


            elif "lista->cola = null" in line:


                current["cola"] = "NULL"


            elif "lista->cantidad = 0" in line:


                current["size"] = 0


                current["empty"] = True


            elif "lista->cantidad--" in line:


                current["size"] = max(0, int(current.get("size", len(working))) - 1)


                current["empty"] = current["size"] == 0


            elif "free(actual)" in line:


                detached = (current.get("temporaries") or {}).get("actual", {})


                freed_value = detached.get("value", target_value)


                current.pop("temporaries", None)


                current["actual"] = "liberado"


                current["freed_nodes"] = [*current.get("freed_nodes", []), freed_value]


            elif "lista->cabeza = next" in line:


                if working:


                    working.pop(0)


                removed_value = before_values[len(before_values) - len(working) - 1]


                current["actual_value"] = removed_value


                current["items"] = deepcopy(working)


                current["size"] = len(working)


                current["empty"] = not working


                current["cabeza"] = "N1" if working else "NULL"


                current["temporaries"] = {"actual": {"allocated": True, "value": removed_value, "next": "desconectado"}}


            elif "lista->cola->sgte = lista->cabeza" in line:


                current["cola_sgte"] = current.get("cabeza", "NULL")


            elif "actual = next" in line:


                current["actual"] = current.get("cabeza", "NULL")


                if working:


                    current["actual_value"] = working[0].get("value") if isinstance(working[0], dict) else working[0]


                current.pop("temporaries", None)


            elif "return" in line and "true" not in line and operation == "lcir_buscar_posiciones(":


                current.pop("actual", None)


            states.append(deepcopy(current))





        states[-1] = deepcopy(after_state)


        return states





    @classmethod


    def _build_sublist_boundaries(


        cls, before_state: dict[str, Any], after_state: dict[str, Any], step_lines: list[str],


        payload: dict[str, Any] | None = None,


    ) -> list[dict[str, Any]]:


        """Apply visible sublist changes at their actual C pointer/free statements."""


        joined = "\n".join(str(line) for line in step_lines).lower()


        if not any(name in joined for name in ("sublista_insertar_padre_final(", "sublista_insertar_hijo(", "sublista_eliminar_padre_primero(", "sublista_eliminar_hijo(", "sublista_obtener_hijos(", "sublista_destruir(")):


            return []


        if any(name in joined for name in ("bool sublista_eliminar_hijo(", "bool sublista_eliminar_padre_primero(", "void sublista_destruir(", "int sublista_obtener_hijos(", "nodo *sublista_insertar_padre_final(", "bool sublista_insertar_hijo(")):


            parent_delete = "bool sublista_eliminar_padre_primero(" in joined

            clear_operation = "void sublista_destruir(" in joined

            query_operation = "int sublista_obtener_hijos(" in joined

            insert_parent = "nodo *sublista_insertar_padre_final(" in joined

            insert_child = "bool sublista_insertar_hijo(" in joined

            buffer_values = []


            nodes = []


            originals = list(before_state.get("items") or [])


            for i, item in enumerate(originals):


                children = list(item.get("children") or [])


                nodes.append({"id": f"P{i+1}", "kind": "parent", "value": item["parent"],


                              "next": f"P{i+2}" if i+1 < len(originals) else "NULL",


                              "sub": f"H{i+1}.1" if children else "NULL"})


                nodes.extend({"id": f"H{i+1}.{j+1}", "kind": "child", "value": value,


                              "next": f"H{i+1}.{j+2}" if j+1 < len(children) else "NULL"}


                             for j, value in enumerate(children))


            root = "P1" if originals else "NULL"


            frames = []


            pending = None


            freed = None


            returned = None


            payload = payload or {}





            def node_at(pointer):


                return next(node for node in nodes if node["id"] == pointer)





            def snapshot():


                reachable, child_ids, items = [], {}, []


                cursor = root


                while cursor != "NULL":


                    parent = node_at(cursor)


                    reachable.append(cursor)


                    chain, values = [], []


                    child = parent["sub"]


                    while child != "NULL":


                        allocation = node_at(child)


                        chain.append(child); values.append(allocation["value"])


                        child = allocation["next"]


                    child_ids[cursor] = chain


                    origin = int(cursor[1:]) - 1


                    metadata=originals[origin] if origin<len(originals) else list(after_state.get("items") or [])[-1]

                    items.append({**deepcopy(metadata), "parent":parent["value"], "children": values})


                    cursor = parent["next"]


                linked = set(reachable) | {n for ids in child_ids.values() for n in ids}


                state = deepcopy(before_state)


                state.update(sublist_delete_model=True, sublist_parent_delete=parent_delete, sublist_operation="insertar_padre" if insert_parent else "insertar_hijo" if insert_child else "limpiar" if clear_operation else "hijos_de" if query_operation else "eliminar_padre" if parent_delete else "eliminar_hijo", head=root, node_ids=reachable,


                             child_ids=child_ids, items=items, size=len(items), empty=not items,


                             heap_nodes=[{**node, "status": "linked" if node["id"] in linked else "detached"}


                                         for node in nodes], sublist_frames=deepcopy(frames),


                             scope_ended=not frames, returned=returned, helper_completed=pending=="destroy_return")



                if query_operation:

                    state.update(buffer_values=list(buffer_values),buffer_capacity=1024)


                if frames:


                    active = frames[-1]


                    state.update(active_function=active["function"], **active["parameters"], **active["locals"])


                    if active["function"] == "destruir_hijos":


                        state["owner_parent"] = active["owner_parent"]


                        state["sub_head"] = node_at(active["owner_parent"])["sub"]


                else:


                    state["active_function"] = "llamador"


                if freed is not None:


                    state["freed_actual"] = freed


                return state





            states = [snapshot()]


            for raw_line in step_lines:


                line = str(raw_line).strip()


                if line.startswith("Nodo *sublista_insertar_padre_final("):

                    frames.append({"function":"sublista_insertar_padre_final","parameters":{"lista":"&sublista","valor_padre":int(payload["parent"])},"locals":{}})

                elif line.startswith("bool sublista_insertar_hijo("):

                    frames.append({"function":"sublista_insertar_hijo","parameters":{"lista":root,"valor_padre":int(payload["parent"]),"valor_hijo":int(payload["child"])},"locals":{}})

                elif line.startswith("bool sublista_insertar_hijo_final("):

                    frames.append({"function":"sublista_insertar_hijo_final","parameters":{"padre":frames[-1]["locals"]["padre"],"valor_hijo":int(payload["child"])},"locals":{}})

                elif line in {"Nodo *nuevo;","Sublista *nuevo;"}:

                    frames[-1]["locals"]["nuevo"]="sin inicializar"

                elif line in {"nuevo = crear_padre(valor_padre);","nuevo = crear_hijo(valor_hijo);"}:

                    if pending=="allocator_return":frames[-1]["locals"]["nuevo"]=returned;pending=None

                    else:pending="allocator_call"

                elif line.startswith(("static Nodo *crear_padre(","static Sublista *crear_hijo(")):

                    parent_allocator=line.startswith("static Nodo *crear_padre(")

                    frames.append({"function":"crear_padre" if parent_allocator else "crear_hijo","parameters":{"valor":int(payload["parent"] if parent_allocator else payload["child"])},"locals":{}})

                elif "malloc(sizeof(" in line:

                    is_parent="sizeof(Nodo)" in line

                    if is_parent:identity=f"P{len(originals)+1}"

                    else:

                        owner=frames[-2]["parameters"]["padre"];prefix=f"H{owner[1:]}."

                        suffix=1+max([int(node["id"].split(".")[-1]) for node in nodes if node["id"].startswith(prefix)],default=0)

                        identity=f"{prefix}{suffix}"

                    nodes.append({"id":identity,"kind":"parent" if is_parent else "child","value":"sin inicializar","next":"sin inicializar",**({"sub":"sin inicializar"} if is_parent else {})})

                    frames[-1]["locals"]["nuevo"]=identity

                elif line in {"nuevo->nro = valor;","nuevo->sgte = NULL;","nuevo->sub = NULL;"}:

                    field="value" if "->nro" in line else "next" if "->sgte" in line else "sub"

                    node_at(frames[-1]["locals"]["nuevo"])[field]=frames[-1]["parameters"]["valor"] if field=="value" else "NULL"

                elif line == "return nuevo;":

                    active=frames.pop();returned=active["locals"]["nuevo"];pending="allocator_return" if active["function"] in {"crear_padre","crear_hijo"} else None

                elif line == "*lista = nuevo;":

                    root=frames[-1]["locals"]["nuevo"]

                elif line == "actual->sgte = nuevo;":

                    node_at(frames[-1]["locals"]["actual"])["next"]=frames[-1]["locals"]["nuevo"]

                elif line == "padre->sub = nuevo;":

                    node_at(frames[-1]["parameters"]["padre"])["sub"]=frames[-1]["locals"]["nuevo"]

                elif line.startswith("return sublista_insertar_hijo_final("):

                    if pending=="child_return":frames.pop();pending=None

                    else:pending="child_call"

                elif line.startswith("void sublista_destruir("):

                    frames.append({"function":"sublista_destruir","parameters":{"lista":"&sublista"},"locals":{}})

                elif line.startswith("int sublista_obtener_hijos("):

                    frames.append({"function":"sublista_obtener_hijos","parameters":{"lista":root,"valor_padre":int(payload["parent"]),"destino":"destino","capacidad":1024},"locals":{}})

                elif line.startswith("int sublista_copiar_hijos("):

                    frames.append({"function":"sublista_copiar_hijos","parameters":{"padre":frames[-1]["locals"]["padre"],"destino":"destino","capacidad":1024},"locals":{}})

                elif line == "int usados = 0;":

                    frames[-1]["locals"]["usados"] = 0

                elif line == "const Sublista *actual;":

                    frames[-1]["locals"]["actual"] = "sin inicializar"

                elif line == "destino[usados] = actual->nro;":

                    active=frames[-1];index=active["locals"]["usados"];value=node_at(active["locals"]["actual"])["value"]

                    assert index==len(buffer_values)

                    buffer_values.append(value)

                elif line == "usados++;":

                    frames[-1]["locals"]["usados"] += 1

                elif line.startswith("return sublista_copiar_hijos("):

                    if pending == "copy_return":frames.pop();pending=None

                    else:pending="copy_call"

                elif line == "return usados;":

                    returned=frames.pop()["locals"]["usados"];pending="copy_return"

                elif line == "return -1;":

                    frames.pop();returned=-1;pending=None

                elif line == "Nodo *next;":

                    frames[-1]["locals"]["next"]="sin inicializar"

                elif line == "*lista = next;":

                    root=frames[-1]["locals"]["next"]

                elif line == "}" and frames and frames[-1]["function"] == "sublista_destruir":

                    frames.pop();returned=None;pending=None

                elif line.startswith("bool sublista_eliminar_padre_primero("):


                    frames.append({"function": "sublista_eliminar_padre_primero",


                                   "parameters": {"lista": "&sublista", "valor_padre": int(payload["parent"])}, "locals": {}})


                elif line == "Nodo *actual;":


                    frames[-1]["locals"]["actual"] = "sin inicializar"


                elif line == "Nodo *anterior = NULL;":


                    frames[-1]["locals"]["anterior"] = "NULL"


                elif line == "actual = *lista;":


                    frames[-1]["locals"]["actual"] = root


                elif line == "*lista = actual->sgte;":


                    root = node_at(frames[-1]["locals"]["actual"])["next"]


                elif line == "destruir_hijos(&actual->sub);":


                    if pending == "destroy_return":


                        pending = None


                    else:


                        pending = "destroy_call"


                elif line.startswith("static void destruir_hijos("):


                    owner = frames[-1]["locals"]["actual"]


                    frames.append({"function": "destruir_hijos", "owner_parent": owner,


                                   "parameters": {"lista_hijos": f"&{owner}.sub"}, "locals": {}})


                elif line == "Sublista *next;":


                    frames[-1]["locals"]["next"] = "sin inicializar"


                elif line == "actual = *lista_hijos;":


                    frames[-1]["locals"]["actual"] = node_at(frames[-1]["owner_parent"])["sub"]


                elif line == "next = actual->sgte;":


                    frames[-1]["locals"]["next"] = node_at(frames[-1]["locals"]["actual"])["next"]


                elif line == "*lista_hijos = next;":


                    node_at(frames[-1]["owner_parent"])["sub"] = frames[-1]["locals"]["next"]


                elif line == "actual = next;":


                    frames[-1]["locals"]["actual"] = frames[-1]["locals"]["next"]


                elif line == "}" and frames and frames[-1]["function"] == "destruir_hijos":


                    frames.pop(); returned = None; pending = "destroy_return"


                elif line.startswith("bool sublista_eliminar_hijo("):


                    frames.append({"function": "sublista_eliminar_hijo",


                                   "parameters": {"lista": root, "valor_padre": int(payload["parent"]),


                                                  "valor_hijo": int(payload["child"])}, "locals": {}})


                elif line.startswith("Nodo *padre = sublista_buscar_padre("):


                    if pending == "search_return":


                        frames[-1]["locals"]["padre"] = returned


                        pending = None


                    else:


                        pending = "search_call"


                elif line.startswith("Nodo *sublista_buscar_padre("):


                    frames.append({"function": "sublista_buscar_padre",


                                   "parameters": {"lista": root, "valor_padre": int(payload["parent"])}, "locals": {}})


                elif line == "Nodo *actual = lista;":


                    frames[-1]["locals"]["actual"] = root


                elif line.startswith("bool sublista_eliminar_hijo_primero("):


                    frames.append({"function": "sublista_eliminar_hijo_primero",


                                   "parameters": {"padre": frames[-1]["locals"]["padre"],


                                                  "valor_hijo": int(payload["child"])}, "locals": {}})


                elif line == "Sublista *actual;":


                    frames[-1]["locals"]["actual"] = "sin inicializar"


                elif line == "Sublista *anterior = NULL;":


                    frames[-1]["locals"]["anterior"] = "NULL"


                elif line == "actual = padre->sub;":


                    frames[-1]["locals"]["actual"] = node_at(frames[-1]["parameters"]["padre"])["sub"]


                elif line == "anterior = actual;":


                    frames[-1]["locals"]["anterior"] = frames[-1]["locals"]["actual"]


                elif line == "actual = actual->sgte;":


                    frames[-1]["locals"]["actual"] = node_at(frames[-1]["locals"]["actual"])["next"]


                elif line == "padre->sub = actual->sgte;":


                    active = frames[-1]


                    node_at(active["parameters"]["padre"])["sub"] = node_at(active["locals"]["actual"])["next"]


                elif line == "anterior->sgte = actual->sgte;":


                    active = frames[-1]


                    node_at(active["locals"]["anterior"])["next"] = node_at(active["locals"]["actual"])["next"]


                elif line == "free(actual);":


                    freed = frames[-1]["locals"]["actual"]


                    nodes = [node for node in nodes if node["id"] != freed]


                    for frame in frames:


                        for name, value in list(frame["locals"].items()):


                            if value == freed:


                                frame["locals"][name] = "indeterminado (liberado)"


                elif line.startswith("return sublista_eliminar_hijo_primero("):


                    if pending == "child_return":


                        frames.pop(); pending = None


                    else:


                        pending = "child_call"


                elif line in {"return actual;", "return NULL;", "return true;", "return false;"}:


                    active = frames.pop()


                    if active["function"] == "sublista_buscar_padre":


                        returned = active["locals"].get("actual", "NULL") if line == "return actual;" else "NULL"


                        pending = "search_return"


                    else:


                        returned = line == "return true;"


                        pending = "child_return" if frames else None


                states.append(snapshot())


            states[-1] = deepcopy(after_state)


            return states





        before_items = deepcopy(list(before_state.get("items") or []))


        after_items = deepcopy(list(after_state.get("items") or []))


        current = deepcopy(before_state)


        current.pop("temporaries", None)


        current.pop("detached_parent", None)


        states = [deepcopy(current)]


        new_parent = next((item for item in after_items if item.get("id") not in {old.get("id") for old in before_items}), None)


        changed_parent = next((item for item in after_items if any(old.get("id") == item.get("id") and old.get("children") != item.get("children") for old in before_items)), None)


        removed_parent = next((item for item in before_items if item.get("id") not in {new.get("id") for new in after_items}), None)


        removed_child_parent = next((old for old in before_items if any(new.get("id") == old.get("id") and new.get("children") != old.get("children") for new in after_items)), None)


        inserted_child = None


        if changed_parent:


            old_parent = next(item for item in before_items if item.get("id") == changed_parent.get("id"))


            old_children = list(old_parent.get("children") or [])


            inserted_child = next((value for index, value in enumerate(changed_parent.get("children") or []) if index >= len(old_children) or old_children[index] != value), None)


        detached_child = None


        if removed_child_parent:


            new_parent_state = next(item for item in after_items if item.get("id") == removed_child_parent.get("id"))


            old_children = list(removed_child_parent.get("children") or [])


            new_children = list(new_parent_state.get("children") or [])


            detached_child = next((value for index, value in enumerate(old_children) if index >= len(new_children) or new_children[index] != value), None)





        def set_items(items: list[dict[str, Any]]) -> None:


            current["items"] = deepcopy(items)


            current["size"] = len(items)


            current["empty"] = not items





        for raw_line in step_lines:


            line = str(raw_line).strip().lower()


            if "malloc(sizeof(nodo))" in line or "malloc(sizeof(sublista))" in line:


                parent_alloc = "sizeof(nodo)" in line


                current["temporaries"] = {"nuevo": {"allocated": True, "kind": "parent" if parent_alloc else "child", "value": None, "next": "NULL"}}


            elif "nuevo->nro = valor" in line and current.get("temporaries"):


                temp = current["temporaries"].get("nuevo", {})


                temp["value"] = new_parent.get("parent") if temp.get("kind") == "parent" and new_parent else inserted_child


            elif "*lista = nuevo" in line and new_parent is not None:


                set_items(after_items)


                current.pop("temporaries", None)


            elif "actual->sgte = nuevo" in line:


                if new_parent is not None:


                    set_items(after_items)


                    current.pop("temporaries", None)


                elif changed_parent is not None:


                    set_items(after_items)


                    current.pop("temporaries", None)


            elif "padre->sub = nuevo" in line and changed_parent is not None:


                set_items(after_items)


                current.pop("temporaries", None)


            elif line in {"*lista = actual->sgte;", "anterior->sgte = actual->sgte;"} and removed_parent is not None:


                set_items([item for item in before_items if item.get("id") != removed_parent.get("id")])


                current["detached_parent"] = deepcopy(removed_parent)


            elif line in {"padre->sub = actual->sgte;", "anterior->sgte = actual->sgte;"} and removed_child_parent is not None:


                set_items(after_items)


                current["temporaries"] = {"actual": {"allocated": True, "kind": "child", "value": detached_child, "next": "desconectado"}}


            elif "*lista_hijos = next" in line:


                parent = current.get("detached_parent")


                if parent is None:


                    parent = next((item for item in current.get("items", []) if item.get("children")), None)


                if parent is not None:


                    children = list(parent.get("children") or [])


                    if children:


                        detached = children.pop(0)


                        parent["children"] = children


                        current["temporaries"] = {"actual": {"allocated": True, "kind": "child", "value": detached, "next": "desconectado"}}


            elif "*lista = next" in line and "detached_parent" not in current and before_items:


                active = list(current.get("items") or [])


                if active:


                    current["detached_parent"] = deepcopy(active[0])


                    set_items(active[1:])


            elif "free(actual)" in line:


                if current.get("temporaries", {}).get("actual", {}).get("kind") == "child":


                    current.pop("temporaries", None)


                elif current.get("detached_parent"):


                    parent = current["detached_parent"]


                    children = list(parent.get("children") or [])


                    if children:


                        children.pop(0)


                        parent["children"] = children


                    else:


                        current.pop("detached_parent", None)


                elif current.get("temporaries", {}).get("nuevo", {}).get("allocated"):


                    current.pop("temporaries", None)


            elif "actual = actual->sgte" in line and "actual" in current:


                current["actual"] = "siguiente nodo"


            states.append(deepcopy(current))





        states[-1] = deepcopy(after_state)


        return states





    def build_boundaries(


        self,


        before_state: dict[str, Any],


        after_state: dict[str, Any],


        total_steps: int,


        step_lines: list[str],


        payload: dict[str, Any] | None = None,


    ) -> list[dict[str, Any]]:


        """Return one state boundary per step plus the initial boundary."""


        boundaries = total_steps + 1


        before_items = list(before_state.get("items") or [])


        after_items = list(after_state.get("items") or [])


        stack_boundaries = self._build_stack_boundaries(


            before_state,


            after_state,


            step_lines,


        )


        if stack_boundaries:


            return stack_boundaries


        queue_boundaries = self._build_queue_boundaries(


            before_state,


            after_state,


            step_lines,


        )


        if queue_boundaries:


            return queue_boundaries


        priority_boundaries = self._build_priority_queue_boundaries(


            before_state,


            after_state,


            step_lines,


        )


        if priority_boundaries:


            return priority_boundaries


        linked_list_boundaries = self._build_linked_list_boundaries(


            before_state,


            after_state,


            step_lines,


            payload,


        )


        if linked_list_boundaries:


            return linked_list_boundaries


        circular_list_boundaries = self._build_circular_list_boundaries(


            before_state,


            after_state,


            step_lines,


            payload,


        )


        if circular_list_boundaries:


            return circular_list_boundaries


        sublist_boundaries = self._build_sublist_boundaries(


            before_state, after_state, step_lines, payload


        )


        if sublist_boundaries:


            return sublist_boundaries


        if before_state.get("kind") == "sublist" and not after_items:


            working = deepcopy(before_items)


            causal_states: list[list[Any]] = [deepcopy(working)]


            while working:


                while working[0].get("children"):


                    working[0]["children"].pop(0)


                    causal_states.append(deepcopy(working))


                working.pop(0)


                causal_states.append(deepcopy(working))


            transition_states = causal_states


        else:


            transition_states = self._transition_states(before_items, after_items)


        sampled = self._sample(transition_states, boundaries)


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


        if any("pila_apilar(" in str(line) for line in step_lines):


            before_items = list(before_state.get("items") or [])


            after_items = list(after_state.get("items") or [])


            value = after_items[0] if len(after_items) > len(before_items) else None


            if isinstance(value, dict) and "value" in value:


                value = value["value"]


            temporary: dict[str, Any] = {"aux": {"allocated": False, "value": None, "next": None}}


            for index, raw_line in enumerate(step_lines):


                line = str(raw_line).strip()


                if "malloc(" in line:


                    temporary["aux"]["allocated"] = True


                elif "aux->nro" in line:


                    temporary["aux"]["value"] = value


                elif "aux->sgte" in line:


                    temporary["aux"]["next"] = "top" if before_items else "NULL"


                if any(token in line for token in ("malloc(", "aux->nro", "aux->sgte")):


                    result[index + 1]["temporaries"] = deepcopy(temporary)


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


        before_values = list(before_state.get("array") or [])


        after_values = list(after_state.get("array") or [])


        raw_states: list[list[Any]]


        if len(after_values) == len(before_values) + 1:


            # Reproduce exactamente append + sift-up, no una interpolación del resultado.


            pending = list(after_values)


            for value in before_values:


                pending.remove(value)


            working = before_values + pending[:1]


            raw_states = [before_values, deepcopy(working)]


            index = len(working) - 1


            while index > 0:


                parent = (index - 1) // 2


                if working[parent] <= working[index]:


                    break


                working[parent], working[index] = working[index], working[parent]


                raw_states.append(deepcopy(working))


                index = parent


        elif len(after_values) + 1 == len(before_values) and before_values:


            # Reproduce reemplazo por el último elemento + sift-down.


            working = before_values[:-1]


            raw_states = [before_values, deepcopy(working)]


            if working:


                working[0] = before_values[-1]


                raw_states.append(deepcopy(working))


                index = 0


                while True:


                    left, right = 2 * index + 1, 2 * index + 2


                    best = index


                    if left < len(working) and working[left] < working[best]:


                        best = left


                    if right < len(working) and working[right] < working[best]:


                        best = right


                    if best == index:


                        break


                    working[index], working[best] = working[best], working[index]


                    raw_states.append(deepcopy(working))


                    index = best


        else:


            raw_states = SequentialTraceStrategy._transition_states(before_values, after_values)


        raw_states = SequentialTraceStrategy._sample(raw_states, boundaries)


        arrays = raw_states


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


            if "void rbt_eliminar(" in joined:


                patterns = ["if (*arbol) (*arbol)->rbt_color = negro;"]


            else:


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





        if family == "abb" and operation_name == "eliminar" and target is not None:


            target_node = self._find_node(before_root, target)


            if isinstance(target_node, dict) and isinstance(target_node.get("left"), dict) and isinstance(target_node.get("right"), dict):


                successor = target_node["right"]


                while isinstance(successor.get("left"), dict):


                    successor = successor["left"]


                middle_root = deepcopy(before_root)


                middle_target = self._find_node(middle_root, target)


                assert middle_target is not None


                middle_target["value"] = successor.get("value")


                copy_index = next((i for i, line in enumerate(step_lines) if "nodo->valor = temp->valor" in self._normalized(line)), -1)


                delete_index = next((i for i, line in enumerate(step_lines) if "nodo->derecho = abb_eliminar" in self._normalized(line)), -1)


                if copy_index >= 0 and delete_index >= copy_index:


                    middle = deepcopy(before_state)


                    middle["root"] = middle_root


                    result = []


                    for index in range(boundaries):


                        if index <= copy_index:


                            result.append(deepcopy(before_state))


                        elif index <= delete_index:


                            result.append(deepcopy(middle))


                        else:


                            result.append(deepcopy(after_state))


                    result[-1] = deepcopy(after_state)


                    return result





        if family in {"avl", "red_black"} and operation_name == "insertar" and target is not None:


            source = self._find_node(after_root, target)


            template = (


                {"value": target, "color": "RED", "left": None, "right": None}


                if family == "red_black"


                else self._template(source, target)


            )


            middle_root = self._insert(deepcopy(before_root), target, template)


            if family == "avl":


                self._refresh_avl_metadata(middle_root)


            hint = self._rotation_hint(before_state, after_state, target) if family == "avl" else None


            marker = "rbt_insercion_caso1(" if family == "red_black" else "avl_r"


            transition_index = next(


                (index for index, line in enumerate(step_lines) if marker in self._normalized(line)),


                -1,


            )


            transition_boundary = transition_index + 1


            if transition_boundary > mutation_boundary and transition_boundary < boundaries:


                middle = deepcopy(after_state)


                middle["root"] = middle_root


                first_rotation: dict[str, Any] | None = None


                rotation_kind = str((hint or {}).get("type", "")).upper()


                if family == "avl" and rotation_kind in {"LR", "RL"}:


                    first_root = deepcopy(middle_root)


                    child_value = self._number((hint or {}).get("child"))


                    first_root = self._rotate_at(first_root, child_value, "left" if rotation_kind == "LR" else "right")


                    self._refresh_avl_metadata(first_root)


                    first_rotation = deepcopy(middle)


                    first_rotation["root"] = first_root


                if family == "red_black":


                    return self._rbt_insert_boundaries(


                        before_state, after_state, middle, step_lines, mutation_boundary


                    )


                result = [


                    deepcopy(before_state) if index < mutation_boundary


                    else deepcopy(middle) if index < transition_boundary


                    else deepcopy(after_state)


                    for index in range(boundaries)


                ]


                if first_rotation is not None:


                    rotation_index = next((i for i, line in enumerate(step_lines) if "avl_rdd(" in self._normalized(line) or "avl_rdi(" in self._normalized(line)), -1)


                    if rotation_index >= 0:


                        result[rotation_index] = deepcopy(first_rotation)


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


    def _rotate_at(cls, root: dict[str, Any] | None, target: Any, direction: str) -> dict[str, Any] | None:


        if not isinstance(root, dict):


            return root


        if cls._number(root.get("value")) == target:


            if direction == "left" and isinstance(root.get("right"), dict):


                pivot = root["right"]


                root["right"] = pivot.get("left")


                pivot["left"] = root


                return pivot


            if direction == "right" and isinstance(root.get("left"), dict):


                pivot = root["left"]


                root["left"] = pivot.get("right")


                pivot["right"] = root


                return pivot


        root["left"] = cls._rotate_at(root.get("left"), target, direction)


        root["right"] = cls._rotate_at(root.get("right"), target, direction)


        return root





    @classmethod


    def _refresh_avl_metadata(cls, node: dict[str, Any] | None) -> int:


        if not isinstance(node, dict):


            return 0


        left = cls._refresh_avl_metadata(node.get("left"))


        right = cls._refresh_avl_metadata(node.get("right"))


        node["height"] = 1 + max(left, right)


        node["balance_factor"] = right - left


        return node["height"]





    @classmethod


    def _set_node_color(cls, root: dict[str, Any] | None, value: Any, color: str) -> None:


        node = cls._find_node(root, value)


        if node is not None:


            node["color"] = color





    @classmethod


    def _rbt_insert_boundaries(cls, before, after, inserted, lines, mutation_boundary):


        result = [deepcopy(before) for _ in range(len(lines) + 1)]


        current = deepcopy(inserted)


        for boundary in range(mutation_boundary, len(result)):


            if boundary > mutation_boundary:


                line = cls._normalized(lines[boundary - 1])


                target = cls._number(next(iter(cls._path(current.get("root"), after.get("root", {}).get("value"))), None))


                path = cls._path(current.get("root"), cls._find_inserted_value(before.get("root"), after.get("root")))


                if "n->padre->rbt_color = negro" in line and len(path) >= 2:


                    cls._set_node_color(current.get("root"), path[-2], "BLACK")


                elif "t->rbt_color = negro" in line and len(path) >= 3:


                    grand = cls._find_node(current.get("root"), path[-3])


                    parent = cls._find_node(current.get("root"), path[-2])


                    if grand and parent:


                        uncle = grand.get("right") if grand.get("left") is parent else grand.get("left")


                        if isinstance(uncle, dict): uncle["color"] = "BLACK"


                elif "a->rbt_color = rojo" in line and len(path) >= 3:


                    cls._set_node_color(current.get("root"), path[-3], "RED")


                elif line.startswith("rbt_rotar_dcha(arbol, a)") and len(path) >= 3:


                    current["root"] = cls._rotate_at(current.get("root"), cls._number(path[-3]), "right")


                elif line.startswith("rbt_rotar_izda(arbol, a)") and len(path) >= 3:


                    current["root"] = cls._rotate_at(current.get("root"), cls._number(path[-3]), "left")


            result[boundary] = deepcopy(current)


        result[0] = deepcopy(before)


        result[-1] = deepcopy(after)


        return result





    @classmethod


    def _find_inserted_value(cls, before_root, after_root):


        before_values = set(cls._parent_map(before_root))


        after_values = set(cls._parent_map(after_root))


        difference = after_values - before_values


        return next(iter(difference), None)








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


                elif operation_name == "eliminar" and "free(z);" in line:


                    stage, note = "unlink", "Liberando exactamente el nodo lógico z ya desenlazado."


                    debug_ids = {"z": str(payload.get("value")), "y": "successor_or_z", "x": "replacement", "x_parent": "replacement_parent"}


                elif operation_name == "eliminar" and "arreglareliminacion(" in line:


                    stage, note = "delete_fixup", "Ejecutando fix-up RN sólo cuando el color eliminado era negro."


                    debug_ids = {"z": str(payload.get("value")), "y": "removed_physical", "x": "replacement", "x_parent": "replacement_parent", "w": "sibling"}


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


            if family == "red_black" and operation_name == "eliminar" and "debug_ids" in locals():


                debug["logical_nodes"] = deepcopy(debug_ids)


                del debug_ids


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

    def normalize_steps(self, raw_steps, *, copy_value=deepcopy):
        """Copy by default; Graph validation may borrow read-only snapshots."""
        return [TraceStep.from_legacy(step, copy_value=copy_value) for step in raw_steps]






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


            occupied = 0


            chain_lengths: list[int] = []


            for bucket in current_buckets:


                if not isinstance(bucket, dict):


                    continue


                entries = list(bucket.get("entries") or [])


                bucket["entries"] = entries


                bucket["size"] = len(entries)


                bucket["collisions"] = max(0, len(entries) - 1)


                size += bucket["size"]


                collisions += bucket["collisions"]


                occupied += int(bucket["size"] > 0)


                chain_lengths.append(bucket["size"])


            capacity = len(current_buckets) if current_buckets else int(after_metadata.get("capacity", 0))


            current = deepcopy(before_state)


            current["buckets"] = current_buckets


            current["metadata"] = {


                "size": size,


                "capacity": capacity,


                "load_factor": round(float(size) / float(capacity), 6) if capacity else 0.0,


                "collisions": collisions,


                "occupied_buckets": occupied,


                "empty_buckets": max(0, capacity - occupied),


                "max_chain_length": max(chain_lengths, default=0),


                "chain_lengths": chain_lengths,


                "is_empty": size == 0,


                "capacity_policy": "fixed",


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


