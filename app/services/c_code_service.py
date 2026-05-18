"""Didactic service that exposes C source snippets for selected TADs."""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any


class CCodeService:
    """Load C source snippets from `docs/tads_C` for the didactic panel."""

    _DOCS_TADS_C = Path(__file__).resolve().parents[2] / "docs" / "tads_C"

    _LINKED_LIST_OPERATION_MAP: dict[str, str] = {
        "insertar_inicio": "lista_insertar_inicio",
        "insertar_final": "lista_insertar_final",
        "lista_insertar_elemento": "lista_insertar_elemento",
        "insertar_elemento": "lista_insertar_elemento",
        "buscar_elemento": "lista_buscar_elemento",
        "mostrar": "lista_mostrar",
        "eliminar_elemento": "lista_eliminar_elemento",
        "eliminar_repetidos": "lista_eliminar_repetidos",
    }
    _STACK_OPERATION_MAP: dict[str, str] = {
        "apilar": "pila_apilar",
        "desapilar": "pila_desapilar",
    }
    _QUEUE_OPERATION_MAP: dict[str, str] = {
        "encolar": "cola_encolar",
        "desencolar": "cola_desencolar",
    }
    _PRIORITY_QUEUE_OPERATION_MAP: dict[str, str] = {
        "encolar": "cp_encolar",
        "desencolar": "cp_desencolar",
    }
    _CIRCULAR_LIST_OPERATION_MAP: dict[str, str] = {
        "insertar_inicio": "lcir_insertar_inicio",
        "insertar_final": "lcir_insertar_final",
        "eliminar_primero": "lcir_eliminar_primero",
        "buscar_posiciones": "lcir_buscar_posiciones",
        "invertir": "lcir_invertir",
    }
    _SUBLIST_OPERATION_MAP: dict[str, str] = {
        "insertar_padre": "sublista_insertar_padre_final",
        "insertar_hijo": "sublista_insertar_hijo_final",
        "eliminar_padre": "sublista_eliminar_padre_primero",
        "eliminar_hijo": "sublista_eliminar_hijo_primero",
    }
    _ABB_OPERATION_MAP: dict[str, str] = {
        "insertar": "abb_insertar",
        "eliminar": "abb_eliminar",
        "buscar": "abb_buscar",
        "minimo": "abb_encontrarMinimo",
        "maximo": "abb_encontrarMaximo",
        "altura": "abb_altura",
        "inorden": "abb_inorden",
        "preorden": "abb_preorden",
        "postorden": "abb_postorden",
    }
    _AVL_OPERATION_MAP: dict[str, str] = {
        "insertar": "avl_insertar",
        "eliminar": "avl_eliminar",
        "buscar": "avl_buscar",
        "minimo": "avl_minimo",
        "altura": "avl_altura",
    }
    _RED_BLACK_OPERATION_MAP: dict[str, str] = {
        "insertar": "rbt_insertar",
        "eliminar": "rbt_eliminar",
        "buscar": "rbt_buscar",
    }
    _BINARY_HEAP_OPERATION_MAP: dict[str, str] = {
        "insertar": "monticulo_insertar",
        "extraer_raiz": "monticulo_extraer_raiz",
        "raiz": "monticulo_raiz",
    }
    _GRAPH_OPERATION_MAP: dict[str, str] = {
        "insert_vertex": "grafo_insertar_vertice",
        "remove_vertex": "grafo_eliminar_vertice",
        "insert_edge": "grafo_insertar_arco",
        "remove_edge": "grafo_eliminar_arco",
        "exists_vertex": "grafo_existe_vertice",
        "exists_edge": "grafo_existe_arco",
        "neighbors": "grafo_sucesores",
        "edge_weight": "grafo_costo_arco",
        "list_vertices": "grafo_vertices",
        "list_edges": "grafo_arcos",
        "run_bfs": "grafo_bfs",
        "run_dfs": "grafo_dfs",
        "run_dijkstra": "grafo_dijkstra",
        "run_bellman_ford": "grafo_bellman_ford",
        "run_prim": "grafo_prim",
        "run_kruskal": "grafo_kruskal",
    }
    _HASH_TABLE_OPERATION_MAP: dict[str, str] = {
        "create_table": "th_inicializar",
        "insert": "th_insertar",
        "get": "th_buscar",
        "contains": "th_contiene",
        "remove": "th_eliminar",
        "clear": "th_vaciar",
    }

    @classmethod
    def get_structure_data(cls, structure_id: str) -> dict[str, Any] | None:
        """Return C-code didactic data for a structure when available."""
        if structure_id == "linked_list":
            return cls._build_linked_list_data()
        if structure_id == "stack":
            return cls._build_stack_data()
        if structure_id == "queue":
            return cls._build_queue_data()
        if structure_id == "priority_queue":
            return cls._build_priority_queue_data()
        if structure_id == "circular_list":
            return cls._build_circular_list_data()
        if structure_id == "sublist":
            return cls._build_sublist_data()
        if structure_id == "abb":
            return cls._build_abb_data()
        if structure_id == "avl":
            return cls._build_avl_data()
        if structure_id == "red_black":
            return cls._build_red_black_data()
        if structure_id == "binary_heap":
            return cls._build_binary_heap_data()
        if structure_id == "graph":
            return cls._build_graph_data()
        if structure_id == "hash_table":
            return cls._build_hash_table_data()
        return None

    @classmethod
    def _build_linked_list_data(cls) -> dict[str, Any]:
        """Build didactic C-code payload for linked list."""
        c_text = cls._safe_read(cls._DOCS_TADS_C / "tad_lista.c")
        h_text = cls._safe_read(cls._DOCS_TADS_C / "tad_lista.h")

        operation_code: dict[str, str] = {}
        for operation_name, function_name in cls._LINKED_LIST_OPERATION_MAP.items():
            snippet = cls._extract_function_with_comment(c_text, function_name)
            if snippet:
                operation_code[operation_name] = snippet

        operation_code["insertar_posicion"] = operation_code.get("insertar_elemento", "")
        operation_code["insertar_elemento"] = operation_code.get("lista_insertar_elemento", "")
        operation_code["eliminar_primero"] = operation_code.get("eliminar_elemento", "")
        operation_code["buscar_posiciones"] = operation_code.get("buscar_elemento", "")
        operation_code["limpiar"] = (
            "/* Liberacion completa para dejar lista vacia. */\n"
            "while (*lista != NULL) {\n"
            "    int head = (*lista)->nro;\n"
            "    lista_eliminar_elemento(lista, head);\n"
            "}"
        )

        structure_text = cls._extract_linked_list_structure(h_text, c_text)
        return {
            "record": structure_text,
            "operations": operation_code,
            "default_operation": (
                "Codigo C no disponible para esta operacion en docs/tads_C/tad_lista.c."
            ),
            "code_title": "Codigo C",
        }

    @classmethod
    def _build_stack_data(cls) -> dict[str, Any]:
        """Build didactic C-code payload for stack."""
        c_text = cls._safe_read(cls._DOCS_TADS_C / "tad_pila.c")
        h_text = cls._safe_read(cls._DOCS_TADS_C / "tad_pila.h")

        operation_code: dict[str, str] = {}
        for operation_name, function_name in cls._STACK_OPERATION_MAP.items():
            snippet = cls._extract_function_with_comment(c_text, function_name)
            if snippet:
                operation_code[operation_name] = snippet

        init_fn = cls._extract_function_with_comment(c_text, "pila_inicializar")
        destroy_fn = cls._extract_function_with_comment(c_text, "pila_destruir")
        if init_fn and destroy_fn:
            operation_code["limpiar"] = (
                f"{destroy_fn}\n\n"
                "/* Reinicio recomendado del TAD luego de liberar nodos */\n"
                f"{init_fn}"
            )
        elif destroy_fn:
            operation_code["limpiar"] = destroy_fn

        # El TAD no expone `pila_cima`; se deja explícito para el estudiante.
        operation_code["cima"] = (
            "/* Este TAD en C no define una funcion directa para leer la cima. */\n"
            "/* Para consulta didactica, se puede copiar 1 valor desde el tope: */\n"
            "int cima;\n"
            "int usados = pila_copiar_valores(&pila, &cima, 1);\n"
            "if (usados == 1) {\n"
            "    /* cima contiene el valor del tope */\n"
            "}"
        )

        structure_text = cls._extract_stack_structure(h_text, c_text)
        return {
            "record": structure_text,
            "operations": operation_code,
            "default_operation": (
                "Codigo C no disponible para esta operacion en docs/tads_C/tad_pila.c."
            ),
            "code_title": "Codigo C",
        }

    @classmethod
    def _build_queue_data(cls) -> dict[str, Any]:
        """Build didactic C-code payload for queue."""
        c_text = cls._safe_read(cls._DOCS_TADS_C / "tad_cola.c")
        h_text = cls._safe_read(cls._DOCS_TADS_C / "tad_cola.h")

        operation_code: dict[str, str] = {}
        for operation_name, function_name in cls._QUEUE_OPERATION_MAP.items():
            snippet = cls._extract_function_with_comment(c_text, function_name)
            if snippet:
                operation_code[operation_name] = snippet

        init_fn = cls._extract_function_with_comment(c_text, "cola_inicializar")
        clear_fn = cls._extract_function_with_comment(c_text, "cola_vaciar")
        if init_fn and clear_fn:
            operation_code["limpiar"] = (
                f"{clear_fn}\n\n"
                "/* Reinicio recomendado del TAD despues de vaciar */\n"
                f"{init_fn}"
            )
        elif clear_fn:
            operation_code["limpiar"] = clear_fn

        operation_code["frente"] = (
            "/* Este TAD en C no define una funcion directa cola_frente(). */\n"
            "/* Consulta didactica del frente mediante copia de 1 valor: */\n"
            "int frente;\n"
            "int usados = cola_copiar_valores(&cola, &frente, 1);\n"
            "if (usados == 1) {\n"
            "    /* frente contiene el valor del primer nodo */\n"
            "}"
        )
        operation_code["final"] = (
            "/* Este TAD en C no define una funcion directa cola_final(). */\n"
            "/* Consulta didactica del final recorriendo copia temporal: */\n"
            "int buffer[256];\n"
            "int usados = cola_copiar_valores(&cola, buffer, 256);\n"
            "if (usados > 0) {\n"
            "    int final = buffer[usados - 1];\n"
            "    /* final contiene el valor del ultimo nodo */\n"
            "}"
        )

        structure_text = cls._extract_queue_structure(h_text, c_text)
        return {
            "record": structure_text,
            "operations": operation_code,
            "default_operation": (
                "Codigo C no disponible para esta operacion en docs/tads_C/tad_cola.c."
            ),
            "code_title": "Codigo C",
        }

    @classmethod
    def _build_priority_queue_data(cls) -> dict[str, Any]:
        """Build didactic C-code payload for priority queue."""
        c_text = cls._safe_read(cls._DOCS_TADS_C / "tad_cola_prioridad.c")
        h_text = cls._safe_read(cls._DOCS_TADS_C / "tad_cola_prioridad.h")

        operation_code: dict[str, str] = {}
        for operation_name, function_name in cls._PRIORITY_QUEUE_OPERATION_MAP.items():
            snippet = cls._extract_function_with_comment(c_text, function_name)
            if snippet:
                operation_code[operation_name] = snippet

        init_fn = cls._extract_function_with_comment(c_text, "cp_inicializar")
        clear_fn = cls._extract_function_with_comment(c_text, "cp_vaciar")
        if init_fn and clear_fn:
            operation_code["limpiar"] = (
                f"{clear_fn}\n\n"
                "/* Reinicio recomendado del TAD despues de vaciar */\n"
                f"{init_fn}"
            )
        elif clear_fn:
            operation_code["limpiar"] = clear_fn

        operation_code["frente"] = (
            "/* Este TAD en C no define una funcion directa cp_frente(). */\n"
            "/* Consulta didactica: copiar el primer item en orden actual de enlace. */\n"
            "int valor;\n"
            "int prioridad;\n"
            "int usados = cp_copiar_items(&cola, &valor, &prioridad, 1);\n"
            "if (usados == 1) {\n"
            "    /* valor y prioridad del primer nodo enlazado */\n"
            "}"
        )

        structure_text = cls._extract_priority_queue_structure(h_text, c_text)
        return {
            "record": structure_text,
            "operations": operation_code,
            "default_operation": (
                "Codigo C no disponible para esta operacion en docs/tads_C/tad_cola_prioridad.c."
            ),
            "code_title": "Codigo C",
        }

    @classmethod
    def _build_circular_list_data(cls) -> dict[str, Any]:
        """Build didactic C-code payload for circular linked list."""
        c_text = cls._safe_read(cls._DOCS_TADS_C / "tad_lista_circular.c")
        h_text = cls._safe_read(cls._DOCS_TADS_C / "tad_lista_circular.h")

        operation_code: dict[str, str] = {}
        for operation_name, function_name in cls._CIRCULAR_LIST_OPERATION_MAP.items():
            snippet = cls._extract_function_with_comment(c_text, function_name)
            if snippet:
                operation_code[operation_name] = snippet

        init_fn = cls._extract_function_with_comment(c_text, "lcir_inicializar")
        destroy_fn = cls._extract_function_with_comment(c_text, "lcir_destruir")
        if init_fn and destroy_fn:
            operation_code["limpiar"] = (
                f"{destroy_fn}\n\n"
                "/* Reinicio recomendado del TAD luego de liberar nodos */\n"
                f"{init_fn}"
            )
        elif destroy_fn:
            operation_code["limpiar"] = destroy_fn

        operation_code["eliminar_inicio"] = (
            "/* Este TAD en C no define una funcion directa lcir_eliminar_inicio(). */\n"
            "/* Se puede eliminar la cabeza usando lcir_eliminar_primero con su valor actual. */\n"
            "int head;\n"
            "int usados = lcir_copiar_valores(&lista, &head, 1);\n"
            "if (usados == 1) {\n"
            "    lcir_eliminar_primero(&lista, head);\n"
            "}"
        )

        structure_text = cls._extract_circular_list_structure(h_text, c_text)
        return {
            "record": structure_text,
            "operations": operation_code,
            "default_operation": (
                "Codigo C no disponible para esta operacion en docs/tads_C/tad_lista_circular.c."
            ),
            "code_title": "Codigo C",
        }

    @classmethod
    def _build_sublist_data(cls) -> dict[str, Any]:
        """Build didactic C-code payload for sublist."""
        c_text = cls._safe_read(cls._DOCS_TADS_C / "tad_sublista.c")
        h_text = cls._safe_read(cls._DOCS_TADS_C / "tad_sublista.h")

        operation_code: dict[str, str] = {}
        for operation_name, function_name in cls._SUBLIST_OPERATION_MAP.items():
            snippet = cls._extract_function_with_comment(c_text, function_name)
            if snippet:
                operation_code[operation_name] = snippet

        init_fn = cls._extract_function_with_comment(c_text, "sublista_inicializar")
        destroy_fn = cls._extract_function_with_comment(c_text, "sublista_destruir")
        if init_fn and destroy_fn:
            operation_code["limpiar"] = (
                f"{destroy_fn}\n\n"
                "/* Reinicio recomendado del TAD luego de liberar memoria */\n"
                f"{init_fn}"
            )
        elif destroy_fn:
            operation_code["limpiar"] = destroy_fn

        operation_code["hijos_de"] = (
            "/* Consulta de hijos en C: buscar padre y copiar su sublista a un arreglo. */\n"
            "Nodo *padre = sublista_buscar_padre(lista, valor_padre);\n"
            "if (padre != NULL) {\n"
            "    int hijos[256];\n"
            "    int usados = sublista_copiar_hijos(padre, hijos, 256);\n"
            "    /* hijos[0..usados-1] contiene los valores de la sublista */\n"
            "}"
        )

        structure_text = cls._extract_sublist_structure(h_text)
        return {
            "record": structure_text,
            "operations": operation_code,
            "default_operation": (
                "Codigo C no disponible para esta operacion en docs/tads_C/tad_sublista.c."
            ),
            "code_title": "Codigo C",
        }

    @classmethod
    def _build_abb_data(cls) -> dict[str, Any]:
        """Build didactic C-code payload for ABB."""
        c_text = cls._safe_read(cls._DOCS_TADS_C / "tad_abb.c")
        h_text = cls._safe_read(cls._DOCS_TADS_C / "tad_abb.h")

        operation_code: dict[str, str] = {}
        for operation_name, function_name in cls._ABB_OPERATION_MAP.items():
            snippet = cls._extract_function_with_comment(c_text, function_name)
            if snippet:
                operation_code[operation_name] = snippet

        clear_fn = cls._extract_function_with_comment(c_text, "abb_liberarArbol")
        if clear_fn:
            operation_code["limpiar"] = clear_fn
        operation_code["contar_hojas"] = (
            "int abb_contarHojas(ABBNodo* nodo) {\n"
            "    if (nodo == NULL) {\n"
            "        return 0;\n"
            "    }\n"
            "    if (nodo->izquierdo == NULL && nodo->derecho == NULL) {\n"
            "        return 1;\n"
            "    }\n"
            "    return abb_contarHojas(nodo->izquierdo) + abb_contarHojas(nodo->derecho);\n"
            "}"
        )
        operation_code["validar"] = (
            "int abb_validar_rango(ABBNodo* nodo, int minimo, int maximo) {\n"
            "    if (nodo == NULL) {\n"
            "        return 1;\n"
            "    }\n"
            "    if (nodo->valor <= minimo || nodo->valor >= maximo) {\n"
            "        return 0;\n"
            "    }\n"
            "    if (!abb_validar_rango(nodo->izquierdo, minimo, nodo->valor)) {\n"
            "        return 0;\n"
            "    }\n"
            "    if (!abb_validar_rango(nodo->derecho, nodo->valor, maximo)) {\n"
            "        return 0;\n"
            "    }\n"
            "    return 1;\n"
            "}"
        )

        structure_text = cls._extract_abb_structure(h_text, c_text)
        return {
            "record": structure_text,
            "operations": operation_code,
            "default_operation": (
                "Codigo C no disponible para esta operacion en docs/tads_C/tad_abb.c."
            ),
            "code_title": "Codigo C",
        }

    @classmethod
    def _build_avl_data(cls) -> dict[str, Any]:
        """Build didactic C-code payload for AVL."""
        c_text = cls._safe_read(cls._DOCS_TADS_C / "tad_avl.c")
        h_text = cls._safe_read(cls._DOCS_TADS_C / "tad_avl.h")

        operation_code: dict[str, str] = {}
        for operation_name, function_name in cls._AVL_OPERATION_MAP.items():
            snippet = cls._extract_function_with_comment(c_text, function_name)
            if snippet:
                operation_code[operation_name] = snippet

        clear_fn = cls._extract_function_with_comment(c_text, "avl_liberarAVL")
        if clear_fn:
            operation_code["limpiar"] = clear_fn
        operation_code.setdefault(
            "maximo",
            "AVL avl_maximo(AVL raiz) {\n"
            "    AVL aux = raiz;\n"
            "    while (aux != NULL && aux->der != NULL) {\n"
            "        aux = aux->der;\n"
            "    }\n"
            "    return aux;\n"
            "}",
        )
        operation_code.setdefault(
            "inorden",
            "void avl_inorden(AVL nodo) {\n"
            "    if (nodo != NULL) {\n"
            "        avl_inorden(nodo->izq);\n"
            "        printf(\"%d \", nodo->nro);\n"
            "        avl_inorden(nodo->der);\n"
            "    }\n"
            "}",
        )
        operation_code.setdefault(
            "validar",
            "int avl_validar_fes(AVL nodo) {\n"
            "    if (nodo == NULL) {\n"
            "        return 1;\n"
            "    }\n"
            "    int fe = avl_altura(nodo->der) - avl_altura(nodo->izq);\n"
            "    if (fe < -1 || fe > 1) {\n"
            "        return 0;\n"
            "    }\n"
            "    if (!avl_validar_fes(nodo->izq)) {\n"
            "        return 0;\n"
            "    }\n"
            "    if (!avl_validar_fes(nodo->der)) {\n"
            "        return 0;\n"
            "    }\n"
            "    return 1;\n"
            "}",
        )

        structure_text = cls._extract_avl_structure(h_text, c_text)
        return {
            "record": structure_text,
            "operations": operation_code,
            "default_operation": (
                "Codigo C no disponible para esta operacion en docs/tads_C/tad_avl.c."
            ),
            "code_title": "Codigo C",
        }

    @classmethod
    def _build_red_black_data(cls) -> dict[str, Any]:
        """Build didactic C-code payload for red-black tree."""
        c_text = cls._safe_read(cls._DOCS_TADS_C / "tad_rojo_negro.c")
        h_text = cls._safe_read(cls._DOCS_TADS_C / "tad_rojo_negro.h")
        # Fallback defensivo para repos que aun tengan nombres legacy.
        if not c_text:
            c_text = cls._safe_read(cls._DOCS_TADS_C / "rojo_negro.c")
        if not h_text:
            h_text = cls._safe_read(cls._DOCS_TADS_C / "rojo_negro.h")

        operation_code: dict[str, str] = {}
        for operation_name, function_name in cls._RED_BLACK_OPERATION_MAP.items():
            snippet = cls._extract_function_with_comment(c_text, function_name)
            if snippet:
                operation_code[operation_name] = snippet

        # Para la simulacion didactica de insercion RN se requiere visualizar
        # tambien las subrutinas llamadas (casos y rotaciones).
        insert_helpers: list[str] = []
        for helper_name in (
            "rbt_abuelo",
            "rbt_tio",
            "rbt_rotar_dcha",
            "rbt_rotar_izda",
            "rbt_insercion_caso5",
            "rbt_insercion_caso4",
            "rbt_insercion_caso3",
            "rbt_insercion_caso2",
            "rbt_insercion_caso1",
            "rbt_insertar",
        ):
            helper_snippet = cls._extract_function_with_comment(c_text, helper_name)
            if helper_snippet:
                insert_helpers.append(helper_snippet)
        if insert_helpers:
            operation_code["insertar"] = "\n\n".join(insert_helpers)

        clear_fn = cls._extract_function_with_comment(c_text, "rbt_liberar")
        if clear_fn:
            operation_code["limpiar"] = clear_fn
        operation_code.setdefault(
            "inorden",
            "void rbt_inorden(RBT nodo) {\n"
            "    if (nodo == NULL) {\n"
            "        return;\n"
            "    }\n"
            "    rbt_inorden(nodo->rbt_izq);\n"
            "    printf(\"%d \", nodo->rbt_dato);\n"
            "    rbt_inorden(nodo->rbt_der);\n"
            "}",
        )
        operation_code.setdefault(
            "altura",
            "int rbt_altura(RBT nodo) {\n"
            "    if (nodo == NULL) {\n"
            "        return 0;\n"
            "    }\n"
            "    int altIzq = rbt_altura(nodo->rbt_izq);\n"
            "    int altDer = rbt_altura(nodo->rbt_der);\n"
            "    return (altIzq > altDer ? altIzq : altDer) + 1;\n"
            "}",
        )
        operation_code.setdefault(
            "validar",
            "int rbt_validar(RBT raiz) {\n"
            "    if (raiz == NULL) {\n"
            "        return 1;\n"
            "    }\n"
            "    if (raiz->rbt_color == ROJO) {\n"
            "        if ((raiz->rbt_izq != NULL && raiz->rbt_izq->rbt_color == ROJO) ||\n"
            "            (raiz->rbt_der != NULL && raiz->rbt_der->rbt_color == ROJO)) {\n"
            "            return 0;\n"
            "        }\n"
            "    }\n"
            "    if (!rbt_validar(raiz->rbt_izq)) {\n"
            "        return 0;\n"
            "    }\n"
            "    if (!rbt_validar(raiz->rbt_der)) {\n"
            "        return 0;\n"
            "    }\n"
            "    return 1;\n"
            "}",
        )

        structure_text = cls._extract_red_black_structure(h_text, c_text)
        return {
            "record": structure_text,
            "operations": operation_code,
            "default_operation": (
                "Codigo C no disponible para esta operacion en docs/tads_C/tad_rojo_negro.c."
            ),
            "code_title": "Codigo C",
        }

    @classmethod
    def _build_binary_heap_data(cls) -> dict[str, Any]:
        """Build didactic C-code payload for binary heap."""
        c_text = cls._safe_read(cls._DOCS_TADS_C / "tad_monticulo_binario.c")
        h_text = cls._safe_read(cls._DOCS_TADS_C / "tad_monticulo_binario.h")

        operation_code: dict[str, str] = {}
        for operation_name, function_name in cls._BINARY_HEAP_OPERATION_MAP.items():
            snippet = cls._extract_function_with_comment(c_text, function_name)
            if snippet:
                operation_code[operation_name] = snippet

        init_fn = cls._extract_function_with_comment(c_text, "monticulo_inicializar")
        destroy_fn = cls._extract_function_with_comment(c_text, "monticulo_destruir")
        if init_fn and destroy_fn:
            operation_code["limpiar"] = (
                f"{destroy_fn}\n\n"
                "/* Reinicio recomendado del TAD tras liberar memoria interna */\n"
                f"{init_fn}"
            )
        elif destroy_fn:
            operation_code["limpiar"] = destroy_fn

        operation_code["a_lista"] = (
            "/* Copia didactica del arreglo interno del monticulo. */\n"
            "int buffer[256];\n"
            "int usados = monticulo_copiar_valores(&monticulo, buffer, 256);\n"
            "for (int i = 0; i < usados; i++) {\n"
            "    /* buffer[i] contiene el valor en el indice i */\n"
            "}"
        )

        structure_text = cls._extract_binary_heap_structure(h_text)
        return {
            "record": structure_text,
            "operations": operation_code,
            "default_operation": (
                "Codigo C no disponible para esta operacion en docs/tads_C/tad_monticulo_binario.c."
            ),
            "code_title": "Codigo C",
        }

    @classmethod
    def _build_graph_data(cls) -> dict[str, Any]:
        """Build didactic C-code payload for graph TAD."""
        c_text = cls._safe_read(cls._DOCS_TADS_C / "tad_grafo.c")
        h_text = cls._safe_read(cls._DOCS_TADS_C / "tad_grafo.h")

        operation_code: dict[str, str] = {}
        for operation_name, function_name in cls._GRAPH_OPERATION_MAP.items():
            snippet = cls._extract_function_with_comment(c_text, function_name)
            if snippet:
                operation_code[operation_name] = snippet

        # Para DFS se muestra tambien la subrutina recursiva llamada para
        # mantener coherencia con la interpretacion paso a paso.
        dfs_wrapper = cls._extract_function_with_comment(c_text, "grafo_dfs")
        dfs_recursive = cls._extract_function_with_comment(c_text, "grafo_dfs_recursivo")
        if dfs_wrapper and dfs_recursive:
            operation_code["run_dfs"] = f"{dfs_wrapper}\n\n{dfs_recursive}"

        create_fn = cls._extract_function_with_comment(c_text, "grafo_crear")
        if create_fn:
            operation_code["create_graph"] = create_fn
        operation_code["clear_graph"] = (
            "/* El TAD nuevo de grafo devuelve estructura por valor. */\n"
            "/* Reinicio didactico: */\n"
            "g = grafo_crear();"
        )

        structure_text = cls._extract_graph_structure(h_text, c_text)
        return {
            "record": structure_text,
            "operations": operation_code,
            "default_operation": (
                "Codigo C no disponible para esta operacion en docs/tads_C/tad_grafo.c."
            ),
            "code_title": "Codigo C",
        }

    @classmethod
    def _build_hash_table_data(cls) -> dict[str, Any]:
        """Build didactic C-code payload for hash table TAD."""
        c_text = cls._safe_read(cls._DOCS_TADS_C / "tad_tabla_hash.c")
        h_text = cls._safe_read(cls._DOCS_TADS_C / "tad_tabla_hash.h")

        operation_code: dict[str, str] = {}
        for operation_name, function_name in cls._HASH_TABLE_OPERATION_MAP.items():
            snippet = cls._extract_function_with_comment(c_text, function_name)
            if snippet:
                operation_code[operation_name] = snippet

        operation_code["keys"] = (
            "/* Este TAD en C no expone un metodo que retorne solo claves como arreglo. */\n"
            "/* Se puede recorrer la tabla completa usando th_formatear. */\n"
            "char buffer[2048];\n"
            "th_formatear(&tabla, buffer, sizeof(buffer));"
        )
        operation_code["values"] = (
            "/* Este TAD en C no expone un metodo que retorne solo valores como arreglo. */\n"
            "/* Se puede recorrer la tabla completa usando th_formatear. */\n"
            "char buffer[2048];\n"
            "th_formatear(&tabla, buffer, sizeof(buffer));"
        )
        operation_code["items"] = (
            "/* Consulta didactica de pares clave:valor por bucket. */\n"
            "char buffer[2048];\n"
            "th_formatear(&tabla, buffer, sizeof(buffer));"
        )
        operation_code["stats"] = (
            "/* Estadisticas del TAD tabla hash. */\n"
            "THEstadisticas stats = th_estadisticas(&tabla);\n"
            "char texto[512];\n"
            "th_formatear_estadisticas(&tabla, texto, sizeof(texto));"
        )

        init_fn = cls._extract_function_with_comment(c_text, "th_inicializar")
        destroy_fn = cls._extract_function_with_comment(c_text, "th_destruir")
        if init_fn and destroy_fn:
            operation_code["destroy_table"] = destroy_fn
            operation_code["clear_and_reinit"] = (
                f"{destroy_fn}\n\n"
                "/* Reinicio recomendado del TAD conservando una capacidad valida. */\n"
                f"{init_fn}"
            )

        structure_text = cls._extract_hash_table_structure(h_text)
        return {
            "record": structure_text,
            "operations": operation_code,
            "default_operation": (
                "Codigo C no disponible para esta operacion en docs/tads_C/tad_tabla_hash.c."
            ),
            "code_title": "Codigo C",
        }

    @staticmethod
    def _safe_read(path: Path) -> str:
        """Read a UTF-8 text file with replacement for invalid bytes."""
        if not path.exists():
            return ""
        return path.read_text(encoding="utf-8", errors="replace")

    @staticmethod
    def _extract_linked_list_structure(header_text: str, source_text: str) -> str:
        """Extract C declarations that describe the linked-list TAD structure."""
        nodo_match = re.search(r"struct\s+nodo\s*\{[\s\S]*?\};", source_text)
        lista_match = re.search(r"typedef\s+struct\s*\{[\s\S]*?\}\s*Lista\s*;", header_text)
        alias_match = re.search(r"typedef\s+struct\s+nodo\s+Nodo\s*;", header_text)
        nodo_new_match = re.search(
            r"typedef\s+struct\s+NodoLista\s*\{[\s\S]*?\}\s*\*?\s*Tlista\s*;",
            header_text,
        )

        blocks: list[str] = []
        if nodo_match:
            blocks.append(nodo_match.group(0).strip())
        if alias_match:
            blocks.append(alias_match.group(0).strip())
        if lista_match:
            blocks.append(lista_match.group(0).strip())
        if nodo_new_match:
            blocks.append(nodo_new_match.group(0).strip())

        if blocks:
            return "\n\n".join(blocks)
        return "Estructura en C no encontrada para Lista."

    @staticmethod
    def _extract_stack_structure(header_text: str, source_text: str) -> str:
        """Extract C declarations that describe the stack TAD structure."""
        nodo_match = re.search(r"struct\s+nodo\s*\{[\s\S]*?\};", source_text)
        alias_match = re.search(r"typedef\s+struct\s+nodo\s+Nodo\s*;", header_text)
        pila_match = re.search(r"typedef\s+struct\s*\{[\s\S]*?\}\s*Pila\s*;", header_text)
        nodo_new_match = re.search(
            r"typedef\s+struct\s+NodoPila\s*\{[\s\S]*?\}\s*\*?\s*ptrPila\s*;",
            header_text,
        )

        blocks: list[str] = []
        if nodo_match:
            blocks.append(nodo_match.group(0).strip())
        if alias_match:
            blocks.append(alias_match.group(0).strip())
        if pila_match:
            blocks.append(pila_match.group(0).strip())
        if nodo_new_match:
            blocks.append(nodo_new_match.group(0).strip())

        if blocks:
            return "\n\n".join(blocks)
        return "Estructura en C no encontrada para Pila."

    @staticmethod
    def _extract_queue_structure(header_text: str, source_text: str) -> str:
        """Extract C declarations that describe the queue TAD structure."""
        nodo_match = re.search(r"struct\s+nodo\s*\{[\s\S]*?\};", source_text)
        alias_match = re.search(r"typedef\s+struct\s+nodo\s+Nodo\s*;", header_text)
        cola_match = re.search(r"typedef\s+struct\s*\{[\s\S]*?\}\s*Cola\s*;", header_text)
        nodo_new_match = re.search(r"struct\s+NodoCola\s*\{[\s\S]*?\};", header_text)
        cola_new_match = re.search(r"struct\s+Cola\s*\{[\s\S]*?\};", header_text)

        blocks: list[str] = []
        if nodo_match:
            blocks.append(nodo_match.group(0).strip())
        if alias_match:
            blocks.append(alias_match.group(0).strip())
        if cola_match:
            blocks.append(cola_match.group(0).strip())
        if nodo_new_match:
            blocks.append(nodo_new_match.group(0).strip())
        if cola_new_match:
            blocks.append(cola_new_match.group(0).strip())

        if blocks:
            return "\n\n".join(blocks)
        return "Estructura en C no encontrada para Cola."

    @staticmethod
    def _extract_priority_queue_structure(header_text: str, source_text: str) -> str:
        """Extract C declarations that describe the priority-queue TAD structure."""
        nodo_match = re.search(r"struct\s+cp_nodo\s*\{[\s\S]*?\};", source_text)
        alias_match = re.search(r"typedef\s+struct\s+cp_nodo\s+CPNodo\s*;", header_text)
        cola_match = re.search(r"typedef\s+struct\s*\{[\s\S]*?\}\s*ColaPrioridad\s*;", header_text)

        blocks: list[str] = []
        if nodo_match:
            blocks.append(nodo_match.group(0).strip())
        if alias_match:
            blocks.append(alias_match.group(0).strip())
        if cola_match:
            blocks.append(cola_match.group(0).strip())

        if blocks:
            return "\n\n".join(blocks)
        return "Estructura en C no encontrada para ColaPrioridad."

    @staticmethod
    def _extract_circular_list_structure(header_text: str, source_text: str) -> str:
        """Extract C declarations that describe the circular-list TAD structure."""
        nodo_match = re.search(r"struct\s+lcir_nodo\s*\{[\s\S]*?\};", source_text)
        alias_match = re.search(r"typedef\s+struct\s+lcir_nodo\s+LCirNodo\s*;", header_text)
        lista_match = re.search(
            r"typedef\s+struct\s*\{[\s\S]*?\}\s*ListaCircular\s*;",
            header_text,
        )

        blocks: list[str] = []
        if nodo_match:
            blocks.append(nodo_match.group(0).strip())
        if alias_match:
            blocks.append(alias_match.group(0).strip())
        if lista_match:
            blocks.append(lista_match.group(0).strip())

        if blocks:
            return "\n\n".join(blocks)
        return "Estructura en C no encontrada para ListaCircular."

    @staticmethod
    def _extract_sublist_structure(header_text: str) -> str:
        """Extract C declarations that describe the sublist TAD structure."""
        child_match = re.search(
            r"typedef\s+struct\s+sublista\s*\{[\s\S]*?\}\s*Sublista\s*;",
            header_text,
        )
        parent_match = re.search(
            r"typedef\s+struct\s+nodo\s*\{[\s\S]*?\}\s*Nodo\s*;",
            header_text,
        )
        child_new_match = re.search(
            r"typedef\s+struct\s+Sublista\s*\{[\s\S]*?\}\s*Sublista\s*;",
            header_text,
        )
        parent_new_match = re.search(
            r"typedef\s+struct\s+Nodo\s*\{[\s\S]*?\}\s*Nodo\s*;",
            header_text,
        )

        blocks: list[str] = []
        if child_match:
            blocks.append(child_match.group(0).strip())
        if parent_match:
            blocks.append(parent_match.group(0).strip())
        if child_new_match:
            blocks.append(child_new_match.group(0).strip())
        if parent_new_match:
            blocks.append(parent_new_match.group(0).strip())

        if blocks:
            return "\n\n".join(blocks)
        return "Estructura en C no encontrada para Sublista."

    @staticmethod
    def _extract_abb_structure(header_text: str, source_text: str) -> str:
        """Extract C declarations that describe the ABB TAD structure."""
        nodo_match = re.search(
            r"typedef\s+struct\s+NodoAbb\s*\{[\s\S]*?\}\s*NodoAbb\s*;",
            source_text,
        )
        internal_match = re.search(r"struct\s+Abb\s*\{[\s\S]*?\};", source_text)
        opaque_match = re.search(r"typedef\s+struct\s+Abb\s+Abb\s*;", header_text)
        nodo_new_match = re.search(
            r"typedef\s+struct\s+ABBNodo\s*\{[\s\S]*?\}\s*ABBNodo\s*;",
            header_text,
        )

        blocks: list[str] = []
        if nodo_match:
            blocks.append(nodo_match.group(0).strip())
        if internal_match:
            blocks.append(internal_match.group(0).strip())
        if opaque_match:
            blocks.append(opaque_match.group(0).strip())
        if nodo_new_match:
            blocks.append(nodo_new_match.group(0).strip())

        if blocks:
            return "\n\n".join(blocks)
        return "Estructura en C no encontrada para ABB."

    @staticmethod
    def _extract_avl_structure(header_text: str, source_text: str) -> str:
        """Extract C declarations that describe the AVL TAD structure."""
        nodo_match = re.search(
            r"typedef\s+struct\s+NodoAvl\s*\{[\s\S]*?\}\s*NodoAvl\s*;",
            source_text,
        )
        internal_match = re.search(r"struct\s+Avl\s*\{[\s\S]*?\};", source_text)
        opaque_match = re.search(r"typedef\s+struct\s+Avl\s+Avl\s*;", header_text)
        nodo_new_match = re.search(
            r"typedef\s+struct\s+nodoAVL\s*\{[\s\S]*?\}\s*nodoAVL\s*;",
            header_text,
        )
        alias_new_match = re.search(r"typedef\s+nodoAVL\s*\*\s*AVL\s*;", header_text)

        blocks: list[str] = []
        if nodo_match:
            blocks.append(nodo_match.group(0).strip())
        if internal_match:
            blocks.append(internal_match.group(0).strip())
        if opaque_match:
            blocks.append(opaque_match.group(0).strip())
        if nodo_new_match:
            blocks.append(nodo_new_match.group(0).strip())
        if alias_new_match:
            blocks.append(alias_new_match.group(0).strip())

        if blocks:
            return "\n\n".join(blocks)
        return "Estructura en C no encontrada para AVL."

    @staticmethod
    def _extract_red_black_structure(header_text: str, source_text: str) -> str:
        """Extract C declarations that describe the red-black TAD structure."""
        nodo_match = re.search(
            r"typedef\s+struct\s+NodoRN\s*\{[\s\S]*?\}\s*NodoRN\s*;",
            source_text,
        )
        internal_match = re.search(r"struct\s+RojoNegro\s*\{[\s\S]*?\};", source_text)
        opaque_match = re.search(r"typedef\s+struct\s+RojoNegro\s+RojoNegro\s*;", header_text)
        nodo_new_match = re.search(
            r"typedef\s+struct\s+nodoRBT\s*\{[\s\S]*?\}\s*nodoRBT\s*;",
            header_text,
        )
        alias_new_match = re.search(
            r"typedef\s+struct\s+nodoRBT\s*\*\s*RBT\s*;",
            header_text,
        )

        blocks: list[str] = []
        if nodo_match:
            blocks.append(nodo_match.group(0).strip())
        if internal_match:
            blocks.append(internal_match.group(0).strip())
        if opaque_match:
            blocks.append(opaque_match.group(0).strip())
        if nodo_new_match:
            blocks.append(nodo_new_match.group(0).strip())
        if alias_new_match:
            blocks.append(alias_new_match.group(0).strip())

        if blocks:
            return "\n\n".join(blocks)
        return "Estructura en C no encontrada para RojoNegro."

    @staticmethod
    def _extract_binary_heap_structure(header_text: str) -> str:
        """Extract C declarations that describe the binary-heap TAD structure."""
        enum_match = re.search(
            r"typedef\s+enum\s*\{[\s\S]*?\}\s*TipoMonticulo\s*;",
            header_text,
        )
        heap_match = re.search(
            r"typedef\s+struct\s*\{[\s\S]*?\}\s*MonticuloBinario\s*;",
            header_text,
        )

        blocks: list[str] = []
        if enum_match:
            blocks.append(enum_match.group(0).strip())
        if heap_match:
            blocks.append(heap_match.group(0).strip())

        if blocks:
            return "\n\n".join(blocks)
        return "Estructura en C no encontrada para MonticuloBinario."

    @staticmethod
    def _extract_graph_structure(header_text: str, source_text: str) -> str:
        """Extract C declarations that describe graph TAD structure."""
        nodo_arista_block = CCodeService._extract_named_typedef_struct(source_text, "NodoArista")
        nodo_vertice_block = CCodeService._extract_named_typedef_struct(source_text, "NodoVertice")
        arista_block = CCodeService._extract_named_typedef_struct(header_text, "GrafoArista")
        recorrido_block = CCodeService._extract_named_typedef_struct(header_text, "GrafoRecorrido")
        camino_block = CCodeService._extract_named_typedef_struct(header_text, "GrafoCamino")
        opaque_match = re.search(r"typedef\s+struct\s+Grafo\s+Grafo\s*;", header_text)
        internal_match = re.search(r"struct\s+Grafo\s*\{[\s\S]*?\};", source_text)
        nodo_v_new = re.search(r"typedef\s+struct\s+NodoV\s*\{[\s\S]*?\}\s*\*ListaVertice\s*;", header_text)
        nodo_a_new = re.search(r"typedef\s+struct\s+NodoA\s*\{[\s\S]*?\}\s*\*ListaArco\s*;", header_text)
        grafo_new = re.search(r"typedef\s+struct\s+nodoGrafo\s*\{[\s\S]*?\}\s*Grafo\s*;", header_text)
        conjunto_new = re.search(r"typedef\s+struct\s+Conjunto\s*\{[\s\S]*?\}\s*Conjunto\s*;", header_text)

        blocks: list[str] = []
        if nodo_arista_block:
            blocks.append(nodo_arista_block)
        if nodo_vertice_block:
            blocks.append(nodo_vertice_block)
        if arista_block:
            blocks.append(arista_block)
        if recorrido_block:
            blocks.append(recorrido_block)
        if camino_block:
            blocks.append(camino_block)
        if opaque_match:
            blocks.append(opaque_match.group(0).strip())
        if internal_match:
            blocks.append(internal_match.group(0).strip())
        if nodo_v_new:
            blocks.append(nodo_v_new.group(0).strip())
        if nodo_a_new:
            blocks.append(nodo_a_new.group(0).strip())
        if grafo_new:
            blocks.append(grafo_new.group(0).strip())
        if conjunto_new:
            blocks.append(conjunto_new.group(0).strip())

        if blocks:
            return "\n\n".join(blocks)
        return "Estructura en C no encontrada para Grafo."

    @staticmethod
    def _extract_hash_table_structure(header_text: str) -> str:
        """Extract C declarations that describe hash-table TAD structure."""
        node_block = CCodeService._extract_named_typedef_struct(header_text, "THNodo")
        table_block = CCodeService._extract_named_typedef_struct(header_text, "TablaHash")
        stats_block = CCodeService._extract_named_typedef_struct(header_text, "THEstadisticas")

        blocks: list[str] = []
        if node_block:
            blocks.append(node_block)
        if table_block:
            blocks.append(table_block)
        if stats_block:
            blocks.append(stats_block)

        if blocks:
            return "\n\n".join(blocks)
        return "Estructura en C no encontrada para TablaHash."

    @classmethod
    def _extract_function_with_comment(cls, source_text: str, function_name: str) -> str:
        """Extract one C function body and its immediate doc comment if present."""
        signature = cls._find_function_signature(source_text, function_name)
        if signature is None:
            return ""

        start_index, brace_index = signature
        end_index = cls._find_function_end(source_text, brace_index)
        if end_index is None:
            return ""

        comment_start = cls._find_attached_comment_start(source_text, start_index)
        snippet_start = comment_start if comment_start is not None else start_index
        return source_text[snippet_start:end_index].strip()

    @staticmethod
    def _find_function_signature(
        source_text: str,
        function_name: str,
    ) -> tuple[int, int] | None:
        """Find the function signature start and opening brace index."""
        pattern = re.compile(
            rf"(^|\n)\s*(?:static\s+)?[A-Za-z_][\w\s\*]*\b{re.escape(function_name)}\s*\([^;]*?\)\s*\{{",
            re.MULTILINE,
        )
        match = pattern.search(source_text)
        if match is None:
            return None

        signature_start = match.start()
        brace_index = source_text.find("{", match.end() - 1)
        if brace_index == -1:
            return None
        return signature_start, brace_index

    @staticmethod
    def _find_function_end(source_text: str, opening_brace_index: int) -> int | None:
        """Find the end index of a C function by brace balancing."""
        depth = 0
        for index in range(opening_brace_index, len(source_text)):
            char = source_text[index]
            if char == "{":
                depth += 1
            elif char == "}":
                depth -= 1
                if depth == 0:
                    return index + 1
        return None

    @staticmethod
    def _find_attached_comment_start(source_text: str, function_start: int) -> int | None:
        """Return attached Doxygen comment start if it is immediately above function."""
        comment_start = source_text.rfind("/**", 0, function_start)
        if comment_start == -1:
            return None

        comment_end = source_text.find("*/", comment_start, function_start)
        if comment_end == -1:
            return None

        gap = source_text[comment_end + 2:function_start]
        if gap.strip():
            return None
        return comment_start

    @staticmethod
    def _extract_named_typedef_struct(source_text: str, struct_name: str) -> str:
        """Extract a concrete `typedef struct { ... } Name;` block by exact target name."""
        close_match = re.search(rf"\}}\s*{re.escape(struct_name)}\s*;", source_text)
        if close_match is None:
            return ""

        close_start = close_match.start()
        close_end = close_match.end()
        open_start = source_text.rfind("typedef struct", 0, close_start)
        if open_start == -1:
            return ""

        block = source_text[open_start:close_end].strip()
        return block

