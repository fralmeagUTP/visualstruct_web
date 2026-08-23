"""Visual debug-step and control-flow planning for graph traces."""

from __future__ import annotations

from copy import deepcopy
from typing import Any

from app.services.trace.control_flow import ControlFlowPlanner
from app.services.trace.graph_planner import GraphAlgorithmPlanner


class GraphTracePlanner:
    """Build visual metadata and orchestrate graph algorithm line expansion."""

    @staticmethod
    def _line_is_assignment_mutation(line_text: str) -> bool:
        line = ControlFlowPlanner.normalize_line(line_text)
        if "=" not in line or any(token in line for token in ("==", "!=", "<=", ">=")):
            return False
        return not line.startswith(("if ", "if(", "while ", "while(", "for ", "for("))

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

        if operation_name == "run_bfs" and isinstance(result, list):
            path = [str(item) for item in result]
            adjacency = GraphAlgorithmPlanner.adjacency_from_state(after_state)
            bfs_tree_edges = GraphTracePlanner._derive_bfs_tree_edges(path, adjacency)
            seen_nodes: set[str] = set()
            staged_nodes: list[str] = []
            staged_edges: list[list[str]] = []
            for index in range(total_steps):
                count = _prefix_count(len(path), index)
                prefix = path[:count]
                if prefix:
                    current = prefix[-1]
                    if current not in seen_nodes:
                        seen_nodes.add(current)
                        staged_nodes.append(current)
                    staged_edges = []
                    for edge in bfs_tree_edges:
                        if edge[1] in seen_nodes:
                            staged_edges.append([edge[0], edge[1]])
                else:
                    current = None
                stage = "init" if index == 0 else "visit" if index < total_steps - 1 else "complete"
                note = (
                    f"Visitando {current}."
                    if current is not None
                    else "Preparando recorrido."
                )
                debug_steps.append(
                    {
                        "stage": stage,
                        "note": note,
                        "graph_progress": {
                            "mode": "traversal",
                            "nodes": deepcopy(staged_nodes),
                            "edges": deepcopy(staged_edges),
                        },
                    }
                )
            return debug_steps

        if operation_name == "run_dfs" and isinstance(result, list):
            path = [str(item) for item in result]
            adjacency = GraphAlgorithmPlanner.adjacency_from_state(after_state)
            dfs_tree_edges = GraphAlgorithmPlanner.derive_dfs_tree_edges(path, adjacency)
            seen_nodes: set[str] = set()
            staged_nodes: list[str] = []
            staged_edges: list[list[str]] = []

            for index in range(total_steps):
                count = _prefix_count(len(path), index)
                prefix = path[:count]
                if prefix:
                    current = prefix[-1]
                    if current not in seen_nodes:
                        seen_nodes.add(current)
                        staged_nodes.append(current)
                    staged_edges = []
                    for edge in dfs_tree_edges:
                        if edge[1] in seen_nodes:
                            staged_edges.append([edge[0], edge[1]])
                    stage = "init" if index == 0 else "visit" if index < total_steps - 1 else "complete"
                    note = (
                        f"Llamada DFS en {current}."
                        if stage != "complete"
                        else f"DFS completado. Ultimo retorno en {current}."
                    )
                else:
                    stage = "init"
                    note = "Preparando recorrido DFS."

                debug_steps.append(
                    {
                        "stage": stage,
                        "note": note,
                        "graph_progress": {
                            "mode": "traversal",
                            "nodes": deepcopy(staged_nodes),
                            "edges": deepcopy(staged_edges),
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
            node_ids = [str(node.get("id")) for node in (after_state.get("nodes") or []) if isinstance(node, dict)]
            final_distances = {str(key): value for key, value in (result.get("distances") or {}).items()}
            final_previous = {
                str(key): (None if value is None else str(value))
                for key, value in (result.get("previous") or {}).items()
            }

            def _progress(*, distances, previous, visited, selected=None, candidates=None, nodes=None, edges=None):
                return {
                    "mode": "shortest",
                    "nodes": list(nodes or []),
                    "edges": list(edges or []),
                    "distances": deepcopy(distances),
                    "previous": deepcopy(previous),
                    "visited": list(visited),
                    "selected": selected,
                    "candidates": list(candidates or []),
                }

            if operation_name == "run_bellman_ford" and has_negative_cycle:
                timeline: list[dict[str, Any]] = []
                timeline.append(
                    {
                        "stage": "init",
                        "note": f"Iniciando Bellman-Ford desde {origin}.",
                        "graph_progress": _progress(distances={node: (0.0 if node == origin else None) for node in node_ids}, previous={node: None for node in node_ids}, visited=[], nodes=[origin] if origin else []),
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
                            "graph_progress": _progress(distances=final_distances, previous=final_previous, visited=[], candidates=[edge[1]], nodes=[edge[0], edge[1]], edges=[edge]),
                        }
                    )
                timeline.append(
                    {
                        "stage": "detect_negative_cycle",
                        "note": "Se detecto ciclo negativo: aun hay relajacion tras |V|-1 pasadas.",
                        "graph_progress": _progress(distances=final_distances, previous=final_previous, visited=[], edges=sample_edges),
                    }
                )
                timeline.append(
                    {
                        "stage": "complete",
                        "note": "Bellman-Ford finalizo con ciclo negativo.",
                        "graph_progress": _progress(distances=final_distances, previous=final_previous, visited=[], edges=sample_edges),
                    }
                )
                return _sample_timeline(timeline)

            if not path or not reachable:
                initial_distances = {node: (0.0 if node == origin else None) for node in node_ids}
                initial_previous = {node: None for node in node_ids}
                timeline = [
                    {
                        "stage": "init",
                        "note": f"Iniciando desde {origin} y buscando ruta a {destination}.",
                        "graph_progress": _progress(distances=initial_distances, previous=initial_previous, visited=[]),
                    },
                    {
                        "stage": "detect_unreachable",
                        "note": "No existe ruta entre inicio y destino.",
                        "graph_progress": _progress(distances=final_distances, previous=final_previous, visited=[]),
                    },
                    {
                        "stage": "complete",
                        "note": "Ejecucion finalizada sin ruta alcanzable.",
                        "graph_progress": _progress(distances=final_distances, previous=final_previous, visited=[]),
                    },
                ]
                return _sample_timeline(timeline)

            distances = {node: (0.0 if node == origin else None) for node in node_ids}
            previous = {node: None for node in node_ids}
            visited: list[str] = []
            timeline = [
                {
                    "stage": "init",
                    "note": f"Iniciando en {path[0]}.",
                    "graph_progress": _progress(distances=distances, previous=previous, visited=visited, candidates=[path[0]], nodes=[path[0]]),
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
                        "graph_progress": _progress(distances=distances, previous=previous, visited=visited, selected=from_node, candidates=path[i:], nodes=path[:i]),
                    }
                )
                if from_node not in visited:
                    visited.append(from_node)
                timeline.append(
                    {
                        "stage": "relax_edge",
                        "note": f"Relajando arista {from_node} -> {to_node}.",
                        "graph_progress": _progress(distances=distances, previous=previous, visited=visited, selected=from_node, candidates=[to_node], nodes=prefix_nodes, edges=prefix_edges),
                    }
                )
                distances[to_node] = final_distances.get(to_node)
                previous[to_node] = from_node
                timeline.append(
                    {
                        "stage": "update_distance",
                        "note": f"Actualizando distancia tentativa de {to_node}.",
                        "graph_progress": _progress(distances=distances, previous=previous, visited=visited, selected=from_node, candidates=[to_node], nodes=prefix_nodes, edges=prefix_edges),
                    }
                )
            if path[-1] not in visited:
                visited.append(path[-1])
            timeline.append(
                {
                    "stage": "complete",
                    "note": f"Ruta minima consolidada hacia {path[-1]}.",
                    "graph_progress": _progress(distances=final_distances, previous=final_previous, visited=visited, selected=path[-1], nodes=path, edges=[[path[j - 1], path[j]] for j in range(1, len(path))]),
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

    _normalized_line_text = staticmethod(ControlFlowPlanner.normalize_line)

    @staticmethod
    def _graph_out_degree_map(after_state: dict[str, Any]) -> dict[str, int]:
        edges = after_state.get("edges")
        if not isinstance(edges, list):
            return {}
        directed = bool(after_state.get("directed", False))
        degree_map: dict[str, int] = {}
        for edge in edges:
            if not isinstance(edge, dict):
                continue
            source = str(edge.get("source"))
            target = str(edge.get("target"))
            degree_map[source] = degree_map.get(source, 0) + 1
            if not directed:
                degree_map[target] = degree_map.get(target, 0) + 1
        return degree_map

    _graph_adjacency_from_state = staticmethod(GraphAlgorithmPlanner.adjacency_from_state)
    _derive_dfs_tree_edges = staticmethod(GraphAlgorithmPlanner.derive_dfs_tree_edges)

    @staticmethod
    def _derive_bfs_tree_edges(path: list[str], adjacency: dict[str, list[str]]) -> list[list[str]]:
        if not path:
            return []

        root = path[0]
        order_index = {node: idx for idx, node in enumerate(path)}
        distance: dict[str, int] = {root: 0}
        queue: list[str] = [root]

        while queue:
            current = queue.pop(0)
            for neighbor in adjacency.get(current, []):
                if neighbor in distance:
                    continue
                distance[neighbor] = distance[current] + 1
                queue.append(neighbor)

        edges: list[list[str]] = []
        for node in path[1:]:
            level = distance.get(node)
            if level is None:
                continue
            parent_candidates: list[str] = []
            for candidate in path:
                if candidate == node:
                    break
                if distance.get(candidate) == level - 1 and node in adjacency.get(candidate, []):
                    parent_candidates.append(candidate)
            if not parent_candidates:
                continue
            parent = min(parent_candidates, key=lambda candidate: order_index.get(candidate, 10**9))
            edges.append([parent, node])
        return edges

    @staticmethod
    def _is_condition_line(line_text: str) -> bool:
        normalized = ControlFlowPlanner.normalize_line(line_text)
        return (
            normalized.startswith("if ")
            or normalized.startswith("if(")
            or normalized.startswith("else if")
            or normalized.startswith("switch ")
            or normalized.startswith("switch(")
            or normalized.startswith("case ")
            or normalized.startswith("default:")
        )

    _limit_step_indexes = staticmethod(ControlFlowPlanner.limit_step_indexes)

    @staticmethod
    def _prioritize_graph_condition_steps(indexes: list[int], lines: list[str]) -> list[int]:
        if len(indexes) < 2:
            return indexes
        reordered = list(indexes)
        for _ in range(3):
            changed = False
            for pos in range(len(reordered) - 1):
                current_idx = reordered[pos]
                next_idx = reordered[pos + 1]
                current_text = lines[current_idx] if 0 <= current_idx < len(lines) else ""
                next_text = lines[next_idx] if 0 <= next_idx < len(lines) else ""
                if (
                    GraphTracePlanner._line_is_assignment_mutation(current_text)
                    and GraphTracePlanner._is_condition_line(next_text)
                ):
                    reordered[pos], reordered[pos + 1] = reordered[pos + 1], reordered[pos]
                    changed = True
            if not changed:
                break
        return reordered

    @staticmethod
    def _graph_control_repeat_count(
        *,
        operation_name: str,
        normalized_line: str,
        after_state: dict[str, Any],
    ) -> int:
        result_wrapper = after_state.get("last_result") if isinstance(after_state, dict) else None
        result = result_wrapper.get("result") if isinstance(result_wrapper, dict) else None
        nodes = after_state.get("nodes")
        edges = after_state.get("edges")
        node_count = len(nodes) if isinstance(nodes, list) else 0
        edge_count = len(edges) if isinstance(edges, list) else 0

        if operation_name in {"run_bfs", "run_dfs"} and isinstance(result, list):
            path = [str(item) for item in result]
            visit_count = max(1, len(path))
            degree_map = GraphTracePlanner._graph_out_degree_map(after_state)
            neighbor_checks = sum(max(1, degree_map.get(node, 0)) for node in path)
            neighbor_checks = max(visit_count, neighbor_checks)
            if "while (" in normalized_line and ("frente < atras" in normalized_line or "tope > 0" in normalized_line):
                return visit_count + 1
            if "for (" in normalized_line and "cant_sucesores" in normalized_line:
                return max(1, (neighbor_checks + visit_count - 1) // visit_count)
            if "if (!visitado[sucesores[i]])" in normalized_line:
                return max(1, (neighbor_checks + visit_count - 1) // visit_count)
            return 1

        if operation_name == "run_dijkstra" and isinstance(result, dict):
            path_edges = result.get("path_edges")
            path_edge_count = len(path_edges) if isinstance(path_edges, list) else 0
            vertices_span = max(1, node_count)
            outer_passes = max(1, min(vertices_span, path_edge_count + 1 if path_edge_count > 0 else vertices_span))

            if "for (i = 0; i < n_vertices; i++)" in normalized_line:
                return outer_passes
            if "for (j = 0; j < n_vertices; j++)" in normalized_line:
                return vertices_span
            if "for (j = 0; j < cant; j++)" in normalized_line:
                relax_total = max(1, path_edge_count * 2 if path_edge_count > 0 else max(1, edge_count))
                return max(1, min((relax_total + outer_passes - 1) // outer_passes, 20))
            if "while (actual != -1" in normalized_line:
                return max(1, path_edge_count + 1)
            return 1

        if operation_name == "run_bellman_ford":
            passes = max(1, min(max(1, node_count - 1), 16))
            relax_edges = max(1, min(passes * max(1, edge_count), 140))
            if "for (i = 1; i < n_vertices; i++)" in normalized_line:
                return passes
            if "for (j = 0; j < n_vertices; j++)" in normalized_line:
                return max(1, node_count)
            if "for (k = 0; k < cant; k++)" in normalized_line:
                per_pass = max(1, (relax_edges + passes - 1) // passes)
                per_vertex = max(1, (per_pass + max(1, node_count) - 1) // max(1, node_count))
                return max(1, min(per_vertex, 20))
            if "while (actual != -1" in normalized_line:
                return max(1, min(node_count, 30))
            return 1

        if operation_name == "run_prim":
            mst_edges = []
            if isinstance(result, dict) and isinstance(result.get("mst_edges"), list):
                mst_edges = result["mst_edges"]
            mst_count = len(mst_edges)
            if "for (i = 0; i < n; i++)" in normalized_line:
                return max(1, min(max(node_count, mst_count + 1), 30))
            if "for (j = 0; j < n; j++)" in normalized_line:
                return max(1, node_count)
            if "for (j = 0; j < cant; j++)" in normalized_line:
                outer = max(1, min(max(node_count, mst_count + 1), 30))
                total = max(1, min(max(mst_count * 2, 2), 120))
                return max(1, min((total + outer - 1) // outer, 20))
            return 1

        if operation_name == "run_kruskal":
            if "for (size_t j = i + 1; j < m; j++)" in normalized_line:
                return max(1, min(max(1, edge_count // 2), 20))
            if "for (size_t i = 0; i < m && resultado.cantidad < n - 1; i++)" in normalized_line:
                return max(1, min(edge_count, 120))
            if "for (size_t i = 0; i < m; i++)" in normalized_line:
                return max(1, min(edge_count, 120))
            if "for (size_t i = 0; i < n; i++)" in normalized_line:
                return max(1, min(node_count, 40))
            return 1

        return 1

    _extract_state_size = staticmethod(ControlFlowPlanner.state_size)

    _is_if_header = staticmethod(ControlFlowPlanner.is_if_header)
    _is_else_header = staticmethod(ControlFlowPlanner.is_else_header)
    _is_loop_header = staticmethod(ControlFlowPlanner.is_loop_header)
    _is_return_statement = staticmethod(ControlFlowPlanner.is_return_statement)
    _estimate_generic_loop_iterations = staticmethod(ControlFlowPlanner.estimate_loop_iterations)
    _evaluate_generic_condition = staticmethod(ControlFlowPlanner.evaluate_condition)

    _expand_generic_control_flow_indexes = staticmethod(ControlFlowPlanner.expand_generic)

    @staticmethod
    def _expand_graph_control_flow_indexes(
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
        if not operation_name.startswith("run_"):
            return executable_line_indexes
        if operation_name == "run_bfs":
            bfs_indexes = GraphAlgorithmPlanner.expand_bfs(
                lines=lines,
                after_state=after_state,
                success=success,
                message=message,
                payload=payload or {},
            )
            if bfs_indexes is not None:
                return bfs_indexes
        if operation_name == "run_dijkstra":
            dijkstra_indexes = GraphAlgorithmPlanner.expand_dijkstra(
                lines=lines,
                after_state=after_state,
                success=success,
                message=message,
            )
            if dijkstra_indexes is not None:
                return dijkstra_indexes
        if operation_name == "run_bellman_ford":
            bellman_indexes = GraphAlgorithmPlanner.expand_bellman_ford(
                lines=lines,
                after_state=after_state,
                success=success,
                message=message,
            )
            if bellman_indexes is not None:
                return bellman_indexes
        if operation_name == "run_kruskal":
            kruskal_indexes = GraphAlgorithmPlanner.expand_kruskal(
                lines=lines,
                before_state=before_state,
                after_state=after_state,
                success=success,
                message=message,
            )
            if kruskal_indexes is not None:
                return kruskal_indexes
        if operation_name == "run_dfs":
            dfs_indexes = GraphAlgorithmPlanner.expand_dfs(
                lines=lines,
                before_state=before_state,
                after_state=after_state,
                payload=payload or {},
                success=success,
            )
            if dfs_indexes is not None:
                return dfs_indexes

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
                normalized_line = ControlFlowPlanner.normalize_line(line_text)

                if ControlFlowPlanner.is_if_header(normalized_line):
                    segment.append(line_index)
                    if "{" not in line_text:
                        close_paren = line_text.rfind(")")
                        trailing_stmt = line_text[close_paren + 1 :].strip() if close_paren >= 0 else ""
                        if trailing_stmt:
                            cond_true = ControlFlowPlanner.evaluate_condition(
                                normalized_line=normalized_line,
                                success=success,
                                message=message,
                                before_state=before_state,
                                after_state=after_state,
                                payload=payload,
                            )
                            if cond_true and trailing_stmt.lower().startswith("return"):
                                return segment, True
                            pos += 1
                            continue
                    open_line_index = (
                        line_index
                        if "{" in line_text
                        else ControlFlowPlanner.next_nonempty_line_index(lines, line_index + 1)
                    )
                    close_line_index = (
                        ControlFlowPlanner.find_matching_brace_line(lines, open_line_index)
                        if open_line_index >= 0
                        else -1
                    )
                    cond_true = ControlFlowPlanner.evaluate_condition(
                        normalized_line=normalized_line,
                        success=success,
                        message=message,
                        before_state=before_state,
                        after_state=after_state,
                        payload=payload,
                    )
                    if close_line_index < 0 or close_line_index <= line_index:
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
                        else_norm = ControlFlowPlanner.normalize_line(else_text)
                        if ControlFlowPlanner.is_else_header(else_norm):
                            else_has_block = True
                            else_open_line = (
                                else_index
                                if "{" in else_text
                                else ControlFlowPlanner.next_nonempty_line_index(lines, else_index + 1)
                            )
                            else_close_line = (
                                ControlFlowPlanner.find_matching_brace_line(lines, else_open_line)
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
                        nested, did_return = _expand_segment(else_pos + 1, else_block_end_pos)
                        segment.extend(nested)
                        if did_return:
                            return segment, True

                    if else_has_block and else_block_end_pos > 0:
                        pos = else_block_end_pos
                    else:
                        pos = block_end_pos
                    continue

                is_loop_header = (
                    normalized_line.startswith("while ")
                    or normalized_line.startswith("while(")
                    or normalized_line.startswith("for ")
                    or normalized_line.startswith("for(")
                )
                if not is_loop_header:
                    if ControlFlowPlanner.is_else_header(normalized_line):
                        pos += 1
                        continue
                    segment.append(line_index)
                    if ControlFlowPlanner.is_return_statement(normalized_line):
                        return segment, True
                    pos += 1
                    continue

                open_line_index = line_index if "{" in line_text else ControlFlowPlanner.next_nonempty_line_index(lines, line_index + 1)
                close_line_index = (
                    ControlFlowPlanner.find_matching_brace_line(lines, open_line_index)
                    if open_line_index >= 0
                    else -1
                )
                if close_line_index < 0 or close_line_index <= line_index:
                    segment.append(line_index)
                    pos += 1
                    continue

                block_end_pos = _next_pos_after_line(pos + 1, close_line_index)
                if block_end_pos <= pos + 1:
                    segment.append(line_index)
                    pos += 1
                    continue

                repeat_count = GraphTracePlanner._graph_control_repeat_count(
                    operation_name=operation_name,
                    normalized_line=normalized_line,
                    after_state=after_state,
                )
                repeat_count = max(1, min(repeat_count, 180))
                nested_body, nested_returns = _expand_segment(pos + 1, block_end_pos)
                for _ in range(repeat_count):
                    segment.append(line_index)
                    segment.extend(nested_body)
                    if nested_returns:
                        return segment, True
                pos = block_end_pos
            return segment, False

        expanded, _ = _expand_segment(0, len(sorted_exec))
        return ControlFlowPlanner.limit_step_indexes(expanded)
