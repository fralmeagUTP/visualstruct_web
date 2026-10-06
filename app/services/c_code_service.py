"""Didactic service that exposes C source snippets for selected TADs."""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any


class CCodeService:
    """Load C source snippets from `docs/tads_C` for the didactic panel."""

    _DOCS_TADS_C = Path(__file__).resolve().parents[2] / "docs" / "tads_C"

    # Only these canonical teaching assets may be exposed for download.  Keeping
    # this mapping here avoids ever deriving a filesystem path from a request.
    _DOWNLOADABLE_TADS: dict[str, dict[str, object]] = {
        "stack": {"source": "tad_pila.c", "header": "tad_pila.h", "label": "Pila"},
        "queue": {"source": "tad_cola.c", "header": "tad_cola.h", "label": "Cola"},
        "priority_queue": {"source": "tad_cola_prioridad.c", "header": "tad_cola_prioridad.h", "label": "Cola de prioridad"},
        "linked_list": {"source": "tad_lista.c", "header": "tad_lista.h", "label": "Lista enlazada"},
        "circular_list": {"source": "tad_lista_circular.c", "header": "tad_lista_circular.h", "label": "Lista circular"},
        "sublist": {"source": "tad_sublista.c", "header": "tad_sublista.h", "label": "Sublista"},
        "abb": {"source": "tad_abb.c", "header": "tad_abb.h", "label": "ABB"},
        "avl": {"source": "tad_avl.c", "header": "tad_avl.h", "label": "AVL"},
        "red_black": {"source": "tad_rojo_negro.c", "header": "tad_rojo_negro.h", "label": "Árbol rojo-negro"},
        "binary_heap": {"source": "tad_monticulo_binario.c", "header": "tad_monticulo_binario.h", "label": "Montículo binario"},
        "graph": {
            "source": "tad_grafo.c", "header": "tad_grafo.h", "label": "Grafo",
            "dependencies": ("queue",),
            "note": "Los recorridos del grafo usan el TAD Cola; descarga también sus archivos si vas a compilar los recorridos.",
        },
        "hash_table": {"source": "tad_tabla_hash.c", "header": "tad_tabla_hash.h", "label": "Tabla hash"},
        "sorting_array": {"source": "tad_ordenamiento.c", "header": "tad_ordenamiento.h", "label": "Métodos de ordenamiento"},
    }

    _LINKED_LIST_OPERATION_MAP: dict[str, str] = {
        "insertar_inicio": "lista_insertar_inicio",
        "insertar_final": "lista_insertar_final",
        "lista_insertar_elemento": "lista_insertar_elemento",
        "insertar_elemento": "lista_insertar_elemento",
        "buscar_elemento": "lista_buscar_elemento",
        "mostrar": "lista_mostrar",
        "eliminar_elemento": "lista_eliminar_elemento",
        "eliminar_repetidos": "lista_eliminar_repetidos",
        "insertar_posicion": "lista_insertar_elemento",
        "eliminar_primero": "lista_eliminar_inicio",
        "buscar_posiciones": "lista_buscar_elemento",
        "eliminar_inicio": "lista_eliminar_inicio",
        "eliminar_final": "lista_eliminar_final",
        "eliminar_posicion": "lista_eliminar_posicion",
        "primero": "lista_primero",
        "ultimo": "lista_ultimo",
    }
    _STACK_OPERATION_MAP: dict[str, str] = {
        "apilar": "pila_apilar",
        "desapilar": "pila_desapilar",
        "cima": "pila_cima",
        "mostrar": "pila_mostrar",
    }
    _QUEUE_OPERATION_MAP: dict[str, str] = {
        "encolar": "cola_encolar",
        "desencolar": "cola_desencolar",
        "frente": "cola_frente",
        "final": "cola_final",
        "mostrar": "cola_mostrar",
    }
    _PRIORITY_QUEUE_OPERATION_MAP: dict[str, str] = {
        "encolar": "cp_encolar",
        "desencolar": "cp_desencolar",
        "frente": "cp_frente",
        "inicializar": "cp_inicializar",
        "vacia": "cp_vacia",
        "contar": "cp_contar",
        "copiar_items": "cp_copiar_items",
        "formatear": "cp_formatear",
    }
    _CIRCULAR_LIST_OPERATION_MAP: dict[str, str] = {
        "insertar_inicio": "lcir_insertar_inicio",
        "insertar_final": "lcir_insertar_final",
        "eliminar_inicio": "lcir_eliminar_inicio",
        "eliminar_primero": "lcir_eliminar_primero",
        "buscar_posiciones": "lcir_buscar_posiciones",
        "invertir": "lcir_invertir",
    }
    _SUBLIST_OPERATION_MAP: dict[str, str] = {
        "insertar_padre": "sublista_insertar_padre_final",
        "insertar_hijo": "sublista_insertar_hijo",
        "eliminar_padre": "sublista_eliminar_padre_primero",
        "eliminar_hijo": "sublista_eliminar_hijo",
        "hijos_de": "sublista_obtener_hijos",
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
    _SORTING_OPERATION_MAP: dict[str, str] = {
        "intercambio": "ordenar_intercambio",
        "seleccion": "ordenar_seleccion",
        "insercion": "ordenar_insercion",
        "burbuja": "ordenar_burbuja",
        "shell": "ordenar_shell",
        "quicksort": "ordenar_quicksort",
        "mergesort": "ordenar_mergesort",
        "heapsort": "ordenar_heapsort",
        "counting_sort": "ordenar_counting_sort",
        "binsort": "ordenar_binsort",
        "radixsort": "ordenar_radixsort",
        "imprimir_arreglo": "imprimir_arreglo",
        "copiar_arreglo": "copiar_arreglo",
        "probar_algoritmo_void": "probar_algoritmo_void",
        "probar_algoritmo_int": "probar_algoritmo_int",
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
        if structure_id == "sorting_array":
            return cls._build_sorting_data()
        return None

    @classmethod
    def get_downloadable_tad(cls, structure_id: str) -> dict[str, Any] | None:
        """Return safe metadata for a complete, canonical TAD source download."""
        item = cls._DOWNLOADABLE_TADS.get(structure_id)
        if item is None:
            return None
        source = cls._DOCS_TADS_C / str(item["source"])
        header = cls._DOCS_TADS_C / str(item["header"])
        if not source.is_file() or not header.is_file():
            return None
        return {
            "label": str(item["label"]),
            "source_name": source.name,
            "header_name": header.name,
            "dependencies": tuple(item.get("dependencies", ())),
            "note": str(item.get("note", "")),
        }

    @classmethod
    def get_downloadable_tad_file(cls, structure_id: str, file_kind: str) -> Path | None:
        """Return one allowlisted TAD file for a Help download, never a request path."""
        if file_kind not in {"source", "header"}:
            return None
        item = cls._DOWNLOADABLE_TADS.get(structure_id)
        if item is None:
            return None
        path = cls._DOCS_TADS_C / str(item[file_kind])
        return path if path.is_file() else None

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
        operation_code["limpiar"] = cls._extract_function_with_comment(c_text, "lista_limpiar") or (
            "/* Codigo C no disponible para lista_limpiar. */"
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

        # Show the exact public function responsible for this operation.  The
        # downloaded source already contains its final pointer/count reset, so
        # appending cp_inicializar here would present a synthetic method that
        # is not what the priority-queue adapter executes.
        operation_code["limpiar"] = cls._extract_function_with_comment(c_text, "cp_vaciar")

        # Enqueue calls this allocator.  Include both real C functions in the
        # didactic source so the allocation and field initialization are not a
        # black box; both snippets are extracted verbatim from the downloadable
        # .c file and are shared by the operation panel and Help.
        create_node = cls._extract_function_with_comment(c_text, "cp_crear_nodo")
        enqueue = operation_code.get("encolar", "")
        if create_node and enqueue:
            operation_code["encolar"] = f"{create_node}\n\n{enqueue}"

        if "formatear" in operation_code:
            dependency = cls._extract_function_with_comment(c_text, "cp_append_text")
            if dependency:
                operation_code["formatear"] += "\n\n" + dependency

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

        operation_code["limpiar"] = cls._extract_function_with_comment(c_text, "lcir_destruir")

        # Insertions call this allocator; show its real body with each public
        # operation so allocation and field initialization are not a black box.
        create_node = cls._extract_function_with_comment(c_text, "lcir_crear_nodo")
        if create_node:
            for operation_name in ("insertar_inicio", "insertar_final"):
                operation = operation_code.get(operation_name, "")
                if operation:
                    operation_code[operation_name] = f"{operation}\n\n{create_node}"

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

        destroy_fn = cls._extract_function_with_comment(c_text, "sublista_destruir")
        destroy_children_fn = cls._extract_function_with_comment(c_text, "destruir_hijos")
        if destroy_fn:
            operation_code["limpiar"] = destroy_fn

        helper_for_operation = {
            "insertar_padre": ("crear_padre",),
            "insertar_hijo": ("sublista_buscar_padre", "sublista_insertar_hijo_final", "crear_hijo"),
            "eliminar_padre": ("destruir_hijos",),
            "eliminar_hijo": ("sublista_buscar_padre", "sublista_eliminar_hijo_primero"),
            "hijos_de": ("sublista_buscar_padre", "sublista_copiar_hijos"),
            "limpiar": ("destruir_hijos",),
        }
        for operation_name, helpers in helper_for_operation.items():
            if operation_name not in operation_code:
                continue
            helper_sources = [
                cls._extract_function_with_comment(c_text, helper)
                for helper in helpers
            ]
            operation_code[operation_name] = "\n\n".join(
                part for part in (operation_code[operation_name], *helper_sources) if part
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
            "/**\n"
            " * @brief Cuenta hojas sin modificar el arbol ni imprimir.\n"
            " * @param nodo Raiz prestada del subarbol, o NULL.\n"
            " * @return 0 para NULL, 1 para una hoja, o la suma de ambos subarboles.\n"
            " * @note Helper mostrado por la aplicacion; no incluido en el C/H descargado.\n"
            " * C no fija el orden de evaluacion de las dos llamadas sumadas.\n"
            " * No declara locales para sus resultados parciales; son operandos de la expresion.\n"
            " * Tiempo O(n), pila recursiva O(h); no reserva ni libera nodos.\n"
            " */\n"
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
            "/**\n"
            " * @brief Valida orden ABB estricto con limites opcionales, sin mutacion.\n"
            " * @param nodo Raiz del subarbol finito y aciclico; NULL admitido.\n"
            " * @param hay_minimo Indicador de limite inferior presente; cero lo omite.\n"
            " * @param minimo Limite inferior exclusivo, solo comparado si hay_minimo.\n"
            " * @param hay_maximo Indicador de limite superior presente; cero lo omite.\n"
            " * @param maximo Limite superior exclusivo, solo comparado si hay_maximo.\n"
            " * @return 1 si el subarbol respeta todos los limites; 0 si no.\n"
            " * @note Auxiliar didactico de la aplicacion; no exportado por el C/H del TAD.\n"
            " * La llamada inicial usa 0,0,0,0: INT_MIN e INT_MAX son claves validas.\n"
            " * No usa sentinelas fuera de int ni suma/resta uno. Los limites presentes\n"
            " * rechazan igualdad y duplicados. El cortocircuito omite limites ausentes\n"
            " * y omite el subarbol derecho cuando el izquierdo resulta invalido.\n"
            " */\n"
            "int abb_validar_rango(ABBNodo* nodo, int hay_minimo, int minimo, int hay_maximo, int maximo) {\n"
            "    if (nodo == NULL) {\n"
            "        return 1;\n"
            "    }\n"
            "    if ((hay_minimo && nodo->valor <= minimo) || (hay_maximo && nodo->valor >= maximo)) {\n"
            "        return 0;\n"
            "    }\n"
            "    if (!abb_validar_rango(nodo->izquierdo, hay_minimo, minimo, 1, nodo->valor)) {\n"
            "        return 0;\n"
            "    }\n"
            "    if (!abb_validar_rango(nodo->derecho, 1, nodo->valor, hay_maximo, maximo)) {\n"
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

        operation_code['validar'] = (
            "/**\n"
            " * @brief Comprueba equilibrio por alturas en cada subarbol.\n"
            " * @param nodo Raiz prestada del subarbol; NULL es valido.\n"
            " * @return 1 si todas las diferencias altura(der)-altura(izq) estan entre -1 y 1; 0 en otro caso.\n"
            " * @pre Enlaces finitos, aciclicos y nodos vivos.\n"
            " * @note No verifica orden ABB, padres ni el FE almacenado; la validacion del backend es distinta.\n"
            " * @note No muta, reserva, libera ni imprime; cortocircuita al hallar desequilibrio.\n"
            " * @note C no fija el orden de los operandos de la resta de alturas; ambas consultas son puras.\n"
            " * @note Recalcula alturas por nodo: coste O(n*h), no certificado lineal.\n"
            " */\n" + operation_code['validar']
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

        # Eliminar necesita sus seis dependencias reales, sin cambiar el menu o C.
        delete_helpers = [cls._extract_function_with_comment(c_text, fn) for fn in
                          ["colorOf", "rbt_rotar_dcha", "rbt_rotar_izda", "transplantar",
                           "minimo", "arreglarEliminacion", "rbt_eliminar"]]
        if all(delete_helpers):
            operation_code["eliminar"] = "\n\n".join(delete_helpers)

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
        operation_code.setdefault('inorden', '/**\n * @brief Imprime los enteros en orden ascendente, cada uno seguido de un espacio.\n * @param nodo Raiz prestada; NULL no imprime nada.\n * @note Auxiliar de la aplicacion y del main, no exportado por el C/H. No muta ni libera.\n */\nvoid rbt_inorden(RBT nodo) {\n    if (nodo == NULL) return;\n    rbt_inorden(nodo->izq);\n    printf("%d ", nodo->nro);\n    rbt_inorden(nodo->der);\n}')
        operation_code.setdefault('altura', '/**\n * @brief Calcula la altura en nodos, sin mutar el arbol.\n * @param nodo Raiz prestada; NULL admitido.\n * @return 0 para NULL; uno mas que la mayor altura de los hijos en otro caso.\n * @note Auxiliar de la aplicacion y del main, no exportado por el C/H.\n */\nint rbt_altura(RBT nodo) {\n    if (nodo == NULL) return 0;\n    int altIzq = rbt_altura(nodo->izq);\n    int altDer = rbt_altura(nodo->der);\n    return (altIzq > altDer ? altIzq : altDer) + 1;\n}')
        validator = cls._extract_function_with_comment(c_text, "rbt_validar")
        validation_helper = cls._extract_function_with_comment(c_text, "rbt_validar_altura_negra")
        operation_code["validar"] = "#include <limits.h>\n\n" + validation_helper + "\n\n" + validator


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

        heapify_up = cls._extract_function_with_comment(c_text, "heapify_up")
        heapify_down = cls._extract_function_with_comment(c_text, "heapify_down")
        if heapify_up and operation_code.get("insertar"):
            operation_code["insertar"] = f"{heapify_up}\n\n{operation_code['insertar']}"
        if heapify_down and operation_code.get("extraer_raiz"):
            operation_code["extraer_raiz"] = f"{heapify_down}\n\n{operation_code['extraer_raiz']}"

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
            "/* Requiere <stdlib.h>; reserva solo si hay elementos. */\n"
            "int cantidad = monticulo_cantidad(&monticulo);\n"
            "int *buffer = cantidad > 0 ? malloc((size_t)cantidad * sizeof *buffer) : NULL;\n"
            "if (cantidad > 0 && buffer == NULL) {\n"
            "    /* Sin memoria: no copiar ni presentar un resultado incompleto. */\n"
            "    return EXIT_FAILURE;\n"
            "}\n"
            "int usados = monticulo_copiar_valores(&monticulo, buffer, cantidad);\n"
            "for (int i = 0; i < usados; i++) {\n"
            "    /* buffer[i] contiene el valor en el indice i, no orden total. */\n"
            "}\n"
            "free(buffer);"
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

        # BFS calls the actual graph scans, successor allocator and FIFO TAD.
        # These are verbatim downloadable definitions, never synthetic C.
        bfs = operation_code.get("run_bfs")
        if bfs:
            helpers = [cls._extract_function_with_comment(c_text, name) for name in
                       ("grafo_desmarcar", "grafo_marcar_vertice", "grafo_marcado_vertice", "grafo_sucesores")]
            queue_text = cls._safe_read(cls._DOCS_TADS_C / "tad_cola.c")
            helpers += [cls._extract_function_with_comment(queue_text, name) for name in
                        ("cola_encolar", "cola_desencolar")]
            operation_code["run_bfs"] = "\n\n".join([bfs] + [h for h in helpers if h])

        # Para DFS se muestra tambien la subrutina recursiva llamada para
        # mantener coherencia con la interpretacion paso a paso.
        dfs_wrapper = cls._extract_function_with_comment(c_text, "grafo_dfs")
        dfs_recursive = cls._extract_function_with_comment(c_text, "grafo_dfs_recursivo")
        if dfs_wrapper and dfs_recursive:
            dfs_helpers = [cls._extract_function_with_comment(c_text, name) for name in (
                "grafo_agregar_recorrido", "grafo_existe_vertice", "grafo_desmarcar",
                "grafo_marcar_vertice", "grafo_marcado_vertice", "grafo_sucesores",
            )]
            operation_code["run_dfs"] = "\n\n".join([dfs_wrapper, dfs_recursive] + [h for h in dfs_helpers if h])

        # Four numeric algorithms show every actual helper they can call.
        # BFS/DFS snippets above remain unchanged and are not reopened.
        dependencies = {
            "run_dijkstra": ("grafo_orden", "grafo_vertices", "inicializarVectorVertices", "indiceVertice",
                "grafo_tiene_peso_negativo", "grafo_sucesores_atomicos", "grafo_costo_arco", "liberarListaArcos"),
            "run_bellman_ford": ("grafo_orden", "grafo_vertices", "inicializarVectorVertices", "indiceVertice",
                "grafo_arcos", "grafo_costo_arco", "liberarListaArcos"),
            "run_prim": ("grafo_orden", "grafo_vertices", "inicializarVectorVertices", "indiceVertice",
                "grafo_sucesores_atomicos", "grafo_costo_arco", "liberarListaArcos"),
            "run_kruskal": ("grafo_orden", "grafo_tamano", "grafo_vertices", "inicializarVectorVertices", "indiceVertice",
                "grafo_arcos", "grafo_encontrar_conjunto", "grafo_unir_conjuntos", "liberarListaArcos"),
        }
        for operation, names in dependencies.items():
            if operation in operation_code:
                helpers = [cls._extract_function_with_comment(c_text, name) for name in names]
                if not all(helpers):
                    raise ValueError(f"Falta una dependencia C real de {operation}.")
                operation_code[operation] = "\n\n".join([operation_code[operation], *helpers])

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

        hash_index = cls._extract_function_with_comment(c_text, "th_indice")
        hash_search = cls._extract_function_with_comment(c_text, "th_buscar")
        dependencies = {
            "insert": (hash_index,),
            "get": (hash_index,),
            "contains": (hash_index, hash_search),
            "remove": (hash_index,),
        }
        for operation_name, helpers in dependencies.items():
            public_function = operation_code.get(operation_name)
            if public_function:
                operation_code[operation_name] = "\n\n".join(
                    [public_function] + [snippet for snippet in helpers if snippet]
                )

        formatter = cls._extract_function_with_comment(c_text, "th_formatear")
        append = cls._extract_function_with_comment(c_text, "th_append_text")
        for listing in ("keys", "values", "items"):
            operation_code[listing] = "\n\n".join([
                "/* Texto C de tabla completa; la proyeccion API es independiente. */\n"
                "char buffer[2048];\n"
                "th_formatear(&tabla, buffer, sizeof(buffer));",
                formatter, append,
            ])
        operation_code["stats"] = "\n\n".join([
            "/* C float y texto; la proyeccion API mantiene su cociente propio. */\n"
            "THEstadisticas stats = th_estadisticas(&tabla);\n"
            "char texto[512];\n"
            "th_formatear_estadisticas(&tabla, texto, sizeof(texto));",
            cls._extract_function_with_comment(c_text, "th_estadisticas"),
            cls._extract_function_with_comment(c_text, "th_formatear_estadisticas"),
        ])

        init_fn = cls._extract_function_with_comment(c_text, "th_inicializar")
        destroy_fn = cls._extract_function_with_comment(c_text, "th_destruir")
        clear_fn = cls._extract_function_with_comment(c_text, "th_vaciar")
        if init_fn and destroy_fn:
            operation_code["destroy_table"] = "\n\n".join([destroy_fn, clear_fn] if clear_fn else [destroy_fn])
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

    @classmethod
    def _build_sorting_data(cls) -> dict[str, Any]:
        """Build didactic C-code payload for sorting methods."""
        c_text = cls._safe_read(cls._DOCS_TADS_C / "tad_ordenamiento.c")
        h_text = cls._safe_read(cls._DOCS_TADS_C / "tad_ordenamiento.h")

        operation_code: dict[str, str] = {}
        for operation_name, function_name in cls._SORTING_OPERATION_MAP.items():
            snippet = cls._extract_function_with_comment(c_text, function_name)
            if snippet:
                operation_code[operation_name] = snippet

        validation = cls._extract_function_with_comment(c_text, "arreglo_valido")
        swap = cls._extract_function_with_comment(c_text, "intercambiar")
        quick = cls._extract_function_with_comment(c_text, "quicksort_recursivo")
        merge = cls._extract_function_with_comment(c_text, "mezclar")
        merge_recursive = cls._extract_function_with_comment(c_text, "mergesort_recursivo")
        heap = cls._extract_function_with_comment(c_text, "heapify")
        min_max = cls._extract_function_with_comment(c_text, "obtener_minimo_maximo")
        counting = cls._extract_function_with_comment(c_text, "ordenar_counting_sort")
        radix_digit = cls._extract_function_with_comment(c_text, "counting_por_digito")

        dependencies: dict[str, tuple[str, ...]] = {
            "intercambio": (validation, swap),
            "seleccion": (validation, swap),
            "insercion": (validation,),
            "burbuja": (validation, swap),
            "shell": (validation,),
            "quicksort": (validation, swap, quick),
            "mergesort": (validation, merge, merge_recursive),
            "heapsort": (validation, swap, heap),
            "counting_sort": (validation, min_max),
            "binsort": (validation, min_max, counting),
            "radixsort": (validation, radix_digit),
        }
        for operation_name, helpers in dependencies.items():
            public_function = operation_code.get(operation_name)
            if public_function:
                operation_code[operation_name] = "\n\n".join(
                    [snippet for snippet in helpers if snippet] + [public_function]
                )

        structure_text = cls._extract_sorting_structure(h_text)
        return {
            "record": structure_text,
            "operations": operation_code,
            "default_operation": (
                "Codigo C no disponible para esta operacion en docs/tads_C/tad_ordenamiento.c."
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

    @staticmethod
    def _extract_sorting_structure(header_text: str) -> str:
        """Extract C declarations/constants that describe sorting module contract."""
        ok_match = re.search(r"#define\s+ORDENAMIENTO_OK\s+\d+", header_text)
        err_match = re.search(r"#define\s+ORDENAMIENTO_ERROR\s+\d+", header_text)
        api_block = re.search(
            r"void\s+imprimir_arreglo[\s\S]*?void\s+probar_algoritmo_int\s*\([^;]*\)\s*;",
            header_text,
        )
        blocks: list[str] = []
        if ok_match:
            blocks.append(ok_match.group(0).strip())
        if err_match:
            blocks.append(err_match.group(0).strip())
        if api_block:
            blocks.append(api_block.group(0).strip())
        if blocks:
            return "\n\n".join(blocks)
        return "Contrato de ordenamiento en C no encontrado."

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

