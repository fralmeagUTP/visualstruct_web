"""Semantic execution planners for graph algorithms."""

from __future__ import annotations

from typing import Any

from app.services.trace.control_flow import ControlFlowPlanner


class GraphAlgorithmPlanner:
    """Expand didactic graph algorithms into deterministic source-line steps."""

    @staticmethod
    def find_line(normalized_lines: list[str], needle: str) -> int:
        target = str(needle).strip().lower()
        return next((index for index, line in enumerate(normalized_lines) if target in line), -1)

    @staticmethod
    def adjacency_from_state(state: dict[str, Any]) -> dict[str, list[str]]:
        adjacency: dict[str, list[str]] = {}
        for node in state.get("nodes", []) if isinstance(state.get("nodes"), list) else []:
            if isinstance(node, dict) and str(node.get("id", "")):
                adjacency.setdefault(str(node["id"]), [])
        directed = bool(state.get("directed", False))
        for edge in state.get("edges", []) if isinstance(state.get("edges"), list) else []:
            if not isinstance(edge, dict):
                continue
            source, target = str(edge.get("source", "")), str(edge.get("target", ""))
            if not source or not target:
                continue
            if target not in adjacency.setdefault(source, []):
                adjacency[source].append(target)
            if not directed and source not in adjacency.setdefault(target, []):
                adjacency[target].append(source)

        return adjacency

    @staticmethod
    def derive_dfs_tree_edges(path: list[str], adjacency: dict[str, list[str]]) -> list[list[str]]:
        if not path:
            return []
        children: dict[str, list[str]] = {}
        stack = [path[0]]
        for position, node in enumerate(path[1:], start=1):
            parent: str | None = None
            while stack:
                candidate = stack[-1]
                if node in adjacency.get(candidate, []):
                    parent = candidate
                    break
                stack.pop()
            if parent is None:
                parent = next(
                    (candidate for candidate in reversed(path[:position]) if node in adjacency.get(candidate, [])),
                    None,
                )
            if parent is not None:
                children.setdefault(parent, []).append(node)
            stack.append(node)

        edges: list[list[str]] = []
        def walk(current: str) -> None:
            for child in children.get(current, []):
                edges.append([current, child])
                walk(child)
        walk(path[0])
        return edges

    @classmethod
    def expand_dfs(
        cls,
        *,
        lines: list[str],
        before_state: dict[str, Any],
        after_state: dict[str, Any],
        payload: dict[str, Any],
        success: bool,
    ) -> list[int] | None:
        normalized_lines = [ControlFlowPlanner.normalize_line(line) for line in lines]

        header_dfs = cls.find_line(
            normalized_lines, "listavertice grafo_dfs("
        )
        if_exists = cls.find_line(
            normalized_lines, "if (!grafo_existe_vertice(g, inicio))"
        )
        desmarcar = cls.find_line(
            normalized_lines, "g = grafo_desmarcar(g);"
        )
        recorrido_decl = cls.find_line(
            normalized_lines, "listavertice recorrido = null;"
        )
        dfs_call = cls.find_line(
            normalized_lines, "grafo_dfs_recursivo(g, inicio, &recorrido);"
        )
        return_recorrido = cls.find_line(
            normalized_lines, "return recorrido;"
        )
        return_null = cls.find_line(
            normalized_lines, "return null;"
        )

        header_rec = cls.find_line(
            normalized_lines, "void grafo_dfs_recursivo("
        )
        if_recorrido_null = cls.find_line(
            normalized_lines, "if (recorrido == null)"
        )
        mark_line = cls.find_line(
            normalized_lines, "g = grafo_marcar_vertice(g, actual);"
        )
        tmp_decl = cls.find_line(
            normalized_lines, "listavertice tmp = (listavertice) malloc"
        )
        if_tmp_null = cls.find_line(
            normalized_lines, "if (tmp == null) return;"
        )
        tmp_set_data = cls.find_line(
            normalized_lines, "tmp->dato = actual;"
        )
        tmp_set_mark = cls.find_line(
            normalized_lines, "tmp->marcado = 0;"
        )
        tmp_set_sig = cls.find_line(
            normalized_lines, "tmp->sig = *recorrido;"
        )
        set_recorrido = cls.find_line(
            normalized_lines, "*recorrido = tmp;"
        )
        suces_decl = cls.find_line(
            normalized_lines, "listavertice suces = grafo_sucesores(g, actual);"
        )
        while_suces = cls.find_line(
            normalized_lines, "while (suces)"
        )
        if_unmarked = cls.find_line(
            normalized_lines, "if (!grafo_marcado_vertice(g, suces->dato))"
        )
        recursive_call = cls.find_line(
            normalized_lines, "grafo_dfs_recursivo(g, suces->dato, recorrido);"
        )
        temp_decl = cls.find_line(
            normalized_lines, "listavertice temp = suces;"
        )
        suces_next = cls.find_line(
            normalized_lines, "suces = suces->sig;"
        )
        free_temp = cls.find_line(
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
            return ControlFlowPlanner.limit_step_indexes(expanded)

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

        adjacency = cls.adjacency_from_state(after_state)
        children_edges = cls.derive_dfs_tree_edges(visit_order, adjacency)
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
        return ControlFlowPlanner.limit_step_indexes(expanded)

    @classmethod
    def expand_dijkstra(
        cls,
        *,
        lines: list[str],
        after_state: dict[str, Any],
        success: bool,
        message: str,
    ) -> list[int] | None:
        normalized = [ControlFlowPlanner.normalize_line(line) for line in lines]

        header = cls.find_line(normalized, "listaarco grafo_dijkstra(")
        guard_n = cls.find_line(normalized, "if (n <= 0)")
        return_null = cls.find_line(normalized, "return null;")
        alloc_dist = cls.find_line(normalized, "dist = malloc(sizeof(int) * n);")
        alloc_guard = cls.find_line(
            normalized, "if (dist == null || prev == null || visitado == null || vertices == null)"
        )
        init_vertices_guard = cls.find_line(
            normalized, "if (!inicializarvectorvertices(g, vertices, n))"
        )
        init_loop = cls.find_line(normalized, "for (i = 0; i < n; i++)")
        init_dist = cls.find_line(normalized, "dist[i] = int_max;")
        init_prev = cls.find_line(normalized, "prev[i] = -1;")
        idx_inicio = cls.find_line(normalized, "idx_inicio = indicevertice(vertices, n, inicio);")
        idx_llegada = cls.find_line(normalized, "idx_llegada = indicevertice(vertices, n, llegada);")
        idx_guard = cls.find_line(normalized, "if (idx_inicio == -1 || idx_llegada == -1)")
        dist_start = cls.find_line(normalized, "dist[idx_inicio] = 0;")
        main_loop = cls.find_line(normalized, "for (i = 0; i < n; i++)")
        for_j = cls.find_line(normalized, "for (j = 0; j < n; j++)")
        if_pick = cls.find_line(normalized, "if (!visitado[j] && dist[j] < min)")
        set_min = cls.find_line(normalized, "min = dist[j];")
        set_u = cls.find_line(normalized, "u = j;")
        if_u_minus = cls.find_line(normalized, "if (u == -1)")
        break_line = cls.find_line(normalized, "break;")
        set_visit = cls.find_line(normalized, "visitado[u] = 1;")
        suces_decl = cls.find_line(normalized, "suces = grafo_sucesores(g, vertices[u]);")
        while_suces = cls.find_line(normalized, "while (suces != null)")
        v_idx = cls.find_line(normalized, "int v = indicevertice(vertices, n, suces->dato);")
        if_v_ok = cls.find_line(normalized, "if (v != -1 && !visitado[v])")
        costo_line = cls.find_line(normalized, "int costo = grafo_costo_arco(g, vertices[u], vertices[v]);")
        if_overflow = cls.find_line(
            normalized, "if (costo >= 0 && dist[u] != int_max && dist[u] <= int_max - costo)"
        )
        nueva_dist = cls.find_line(normalized, "int nueva_dist = dist[u] + costo;")
        if_relax = cls.find_line(normalized, "if (nueva_dist < dist[v])")
        set_dist = cls.find_line(normalized, "dist[v] = nueva_dist;")
        set_prev = cls.find_line(normalized, "prev[v] = u;")
        tmp_line = cls.find_line(normalized, "listavertice temp = suces;")
        next_suces = cls.find_line(normalized, "suces = suces->sig;")
        free_temp = cls.find_line(normalized, "free(temp);")
        if_unreachable = cls.find_line(normalized, "if (dist[idx_llegada] == int_max)")
        while_prev = cls.find_line(normalized, "while (prev[destino] != -1)")
        new_arc = cls.find_line(normalized, "listaarco nuevo = malloc(sizeof(struct nodoa));")
        if_new_null = cls.find_line(normalized, "if (nuevo == null)")
        liberar_camino = cls.find_line(normalized, "liberarlistaarcos(camino);")
        set_camino_null = cls.find_line(normalized, "camino = null;")
        set_origen = cls.find_line(normalized, "nuevo->origen = vertices[prev[destino]];")
        set_destino = cls.find_line(normalized, "nuevo->destino = vertices[destino];")
        set_costo_arc = cls.find_line(normalized, "nuevo->costo = grafo_costo_arco(g, nuevo->origen, nuevo->destino);")
        set_sig = cls.find_line(normalized, "nuevo->sig = camino;")
        set_camino = cls.find_line(normalized, "camino = nuevo;")
        set_dest = cls.find_line(normalized, "destino = prev[destino];")
        free_dist = cls.find_line(normalized, "free(dist);")
        free_prev = cls.find_line(normalized, "free(prev);")
        free_vis = cls.find_line(normalized, "free(visitado);")
        free_vertices = cls.find_line(normalized, "free(vertices);")
        return_camino = cls.find_line(normalized, "return camino;")

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
            return ControlFlowPlanner.limit_step_indexes(out)

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
            return ControlFlowPlanner.limit_step_indexes(out)

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
        return ControlFlowPlanner.limit_step_indexes(out)

    @classmethod
    def expand_bfs(
        cls,
        *,
        lines: list[str],
        after_state: dict[str, Any],
        success: bool,
        message: str,
        payload: dict[str, Any],
    ) -> list[int] | None:
        normalized = [ControlFlowPlanner.normalize_line(line) for line in lines]

        header = cls.find_line(normalized, "listavertice grafo_bfs(")
        desmarcar = cls.find_line(normalized, "g = grafo_desmarcar(g);")
        cola_decl = cls.find_line(normalized, "struct cola cola = {null, null};")
        rec_decl = cls.find_line(normalized, "listavertice recorrido = null;")
        v_decl = cls.find_line(normalized, "listavertice v = g.v;")
        existe_decl = cls.find_line(normalized, "int existe = 0;")
        while_v = cls.find_line(normalized, "while (v != null)")
        if_v_eq = cls.find_line(normalized, "if (v->dato == inicio)")
        set_existe = cls.find_line(normalized, "existe = 1;")
        break_line = cls.find_line(normalized, "break;")
        v_next = cls.find_line(normalized, "v = v->sig;")
        if_not_exists_return = cls.find_line(normalized, "if (!existe) return null;")
        encolar_inicio = cls.find_line(normalized, "cola_encolar(&cola, inicio);")
        marcar_inicio = cls.find_line(normalized, "g = grafo_marcar_vertice(g, inicio);")
        while_cola = cls.find_line(normalized, "while (cola.delante != null)")
        actual_decl = cls.find_line(normalized, "int actual = cola_desencolar(&cola);")
        if_actual_minus = cls.find_line(normalized, "if (actual == -1)")
        tmp_decl = cls.find_line(normalized, "listavertice tmp = (listavertice) malloc(sizeof(struct nodov));")
        if_tmp_null = cls.find_line(normalized, "if (tmp == null) continue;")
        tmp_dato = cls.find_line(normalized, "tmp->dato = actual;")
        tmp_mark = cls.find_line(normalized, "tmp->marcado = 0;")
        tmp_sig = cls.find_line(normalized, "tmp->sig = recorrido;")
        rec_set = cls.find_line(normalized, "recorrido = tmp;")
        suces_decl = cls.find_line(normalized, "listavertice suces = grafo_sucesores(g, actual);")
        while_suces = cls.find_line(normalized, "while (suces != null)")
        if_unmarked = cls.find_line(normalized, "if (!grafo_marcado_vertice(g, suces->dato))")
        encolar_suces = cls.find_line(normalized, "cola_encolar(&cola, suces->dato);")
        marcar_suces = cls.find_line(normalized, "g = grafo_marcar_vertice(g, suces->dato);")
        temp_decl = cls.find_line(normalized, "listavertice temp = suces;")
        suces_next = cls.find_line(normalized, "suces = suces->sig;")
        free_temp = cls.find_line(normalized, "free(temp);")
        return_rec = cls.find_line(normalized, "return recorrido;")

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
        adjacency = cls.adjacency_from_state(after_state)
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
            return ControlFlowPlanner.limit_step_indexes(out)

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
        return ControlFlowPlanner.limit_step_indexes(out)

    @classmethod
    def expand_bellman_ford(
        cls,
        *,
        lines: list[str],
        after_state: dict[str, Any],
        success: bool,
        message: str,
    ) -> list[int] | None:
        normalized = [ControlFlowPlanner.normalize_line(line) for line in lines]

        header = cls.find_line(normalized, "listaarco grafo_bellman_ford(")
        guard_n = cls.find_line(normalized, "if (n <= 0)")
        return_null = cls.find_line(normalized, "return null;")
        alloc_dist = cls.find_line(normalized, "dist = malloc(sizeof(int) * n);")
        alloc_guard = cls.find_line(normalized, "if (dist == null || prev == null || vertices == null)")
        init_vertices_guard = cls.find_line(normalized, "if (!inicializarvectorvertices(g, vertices, n))")
        init_loop = cls.find_line(normalized, "for (i = 0; i < n; i++)")
        init_dist = cls.find_line(normalized, "dist[i] = int_max;")
        init_prev = cls.find_line(normalized, "prev[i] = -1;")
        idx_inicio = cls.find_line(normalized, "idx_inicio = indicevertice(vertices, n, inicio);")
        idx_llegada = cls.find_line(normalized, "idx_llegada = indicevertice(vertices, n, llegada);")
        idx_guard = cls.find_line(normalized, "if (idx_inicio == -1 || idx_llegada == -1)")
        dist_start = cls.find_line(normalized, "dist[idx_inicio] = 0;")
        pass_loop = cls.find_line(normalized, "for (i = 0; i < n - 1; i++)")
        a_decl = cls.find_line(normalized, "listaarco a = grafo_arcos(g);")
        while_a = cls.find_line(normalized, "while (a != null)")
        idx_u = cls.find_line(normalized, "int u = indicevertice(vertices, n, a->origen);")
        idx_v = cls.find_line(normalized, "int v = indicevertice(vertices, n, a->destino);")
        if_uv = cls.find_line(normalized, "if (u != -1 && v != -1 && dist[u] != int_max)")
        cand_decl = cls.find_line(normalized, "long long cand = (long long)dist[u] + (long long)a->costo;")
        if_relax = cls.find_line(normalized, "if (cand >= int_min && cand <= int_max && (int)cand < dist[v])")
        set_dist = cls.find_line(normalized, "dist[v] = (int)cand;")
        set_prev = cls.find_line(normalized, "prev[v] = u;")
        next_a = cls.find_line(normalized, "a = a->sig;")
        print_neg = cls.find_line(normalized, "printf(\"se detecto un ciclo negativo.\\n\");")
        if_unreachable = cls.find_line(normalized, "if (dist[idx_llegada] == int_max)")
        while_prev = cls.find_line(normalized, "while (prev[destino] != -1)")
        new_arc = cls.find_line(normalized, "listaarco nuevo = malloc(sizeof(struct nodoa));")
        if_new_null = cls.find_line(normalized, "if (nuevo == null)")
        liberar_camino = cls.find_line(normalized, "liberarlistaarcos(camino);")
        set_camino_null = cls.find_line(normalized, "camino = null;")
        break_line = cls.find_line(normalized, "break;")
        set_origen = cls.find_line(normalized, "nuevo->origen = vertices[prev[destino]];")
        set_destino = cls.find_line(normalized, "nuevo->destino = vertices[destino];")
        set_costo = cls.find_line(normalized, "nuevo->costo = grafo_costo_arco(g, nuevo->origen, nuevo->destino);")
        set_sig = cls.find_line(normalized, "nuevo->sig = camino;")
        set_camino = cls.find_line(normalized, "camino = nuevo;")
        set_dest = cls.find_line(normalized, "destino = prev[destino];")
        free_dist = cls.find_line(normalized, "free(dist);")
        free_prev = cls.find_line(normalized, "free(prev);")
        free_vertices = cls.find_line(normalized, "free(vertices);")
        return_camino = cls.find_line(normalized, "return camino;")

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
                return ControlFlowPlanner.limit_step_indexes(out)
            _a(next_a)
            _a(while_a)

        _a(if_unreachable)
        if not reachable:
            _a(free_dist)
            _a(free_prev)
            _a(free_vertices)
            _a(return_null)
            return ControlFlowPlanner.limit_step_indexes(out)

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
        return ControlFlowPlanner.limit_step_indexes(out)

    @classmethod
    def expand_kruskal(
        cls,
        *,
        lines: list[str],
        before_state: dict[str, Any],
        after_state: dict[str, Any],
        success: bool,
        message: str,
    ) -> list[int] | None:
        normalized = [ControlFlowPlanner.normalize_line(line) for line in lines]

        header = cls.find_line(normalized, "listaarco grafo_kruskal(")
        guard_nm = cls.find_line(normalized, "if (n <= 0 || m <= 0)")
        return_null = cls.find_line(normalized, "return null;")
        allocs = cls.find_line(normalized, "conjuntos.padre = malloc")
        alloc_guard = cls.find_line(
            normalized, "if (conjuntos.padre == null || vertices == null || aristas == null)"
        )
        init_vertices_guard = cls.find_line(
            normalized, "if (!inicializarvectorvertices(g, vertices, n))"
        )
        init_parent_loop = cls.find_line(
            normalized, "for (i = 0; i < n; i++) conjuntos.padre[i] = i;"
        )
        while_collect = cls.find_line(
            normalized, "while (a != null && i < m)"
        )
        assign_collect = cls.find_line(normalized, "aristas[i++] = a;")
        next_collect = cls.find_line(normalized, "a = a->sig;")
        for_x = cls.find_line(normalized, "for (int x = 0; x < i - 1; x++)")
        for_y = cls.find_line(normalized, "for (int y = 0; y < i - x - 1; y++)")
        if_swap = cls.find_line(
            normalized, "if (aristas[y]->costo > aristas[y+1]->costo)"
        )
        swap_tmp = cls.find_line(normalized, "listaarco tmp = aristas[y];")
        swap_a = cls.find_line(normalized, "aristas[y] = aristas[y+1];")
        swap_b = cls.find_line(normalized, "aristas[y+1] = tmp;")
        for_j = cls.find_line(normalized, "for (int j = 0; j < i; j++)")
        idx_u = cls.find_line(
            normalized, "int u = indicevertice(vertices, n, aristas[j]->origen);"
        )
        idx_v = cls.find_line(
            normalized, "int v = indicevertice(vertices, n, aristas[j]->destino);"
        )
        if_take = cls.find_line(
            normalized,
            "if (u != -1 && v != -1 && grafo_encontrar_conjunto(&conjuntos, u) != grafo_encontrar_conjunto(&conjuntos, v))",
        )
        union_line = cls.find_line(
            normalized, "grafo_unir_conjuntos(&conjuntos, u, v);"
        )
        new_decl = cls.find_line(
            normalized, "listaarco nuevo = malloc(sizeof(struct nodoa));"
        )
        if_new_null = cls.find_line(normalized, "if (nuevo == null)")
        liberar_mst = cls.find_line(normalized, "liberarlistaarcos(mst);")
        set_mst_null = cls.find_line(normalized, "mst = null;")
        break_line = cls.find_line(normalized, "break;")
        set_origen = cls.find_line(normalized, "nuevo->origen = aristas[j]->origen;")
        set_destino = cls.find_line(normalized, "nuevo->destino = aristas[j]->destino;")
        set_costo = cls.find_line(normalized, "nuevo->costo = aristas[j]->costo;")
        set_sig = cls.find_line(normalized, "nuevo->sig = mst;")
        set_mst = cls.find_line(normalized, "mst = nuevo;")
        free_aristas = cls.find_line(normalized, "free(aristas);")
        free_padre = cls.find_line(normalized, "free(conjuntos.padre);")
        free_vertices = cls.find_line(normalized, "free(vertices);")
        return_mst = cls.find_line(normalized, "return mst;")

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
            return ControlFlowPlanner.limit_step_indexes(out)

        _a(allocs)
        _a(alloc_guard)
        if not success and "malloc" in msg:
            _a(return_null)
            return ControlFlowPlanner.limit_step_indexes(out)

        _a(init_vertices_guard)
        if not success and "vertices" in msg:
            _a(return_null)
            return ControlFlowPlanner.limit_step_indexes(out)

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
        return ControlFlowPlanner.limit_step_indexes(out)
