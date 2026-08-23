"""Adapter for graph structure and algorithms."""

from __future__ import annotations

import random
from typing import Any

from app.adapters.base_adapter import BaseAdapter
from app.domain.graph import Grafo


class GraphAdapter(BaseAdapter):
    """Adapt `Grafo` to the common visualizer contract."""

    def __init__(self) -> None:
        """Initialize adapter state."""
        self._graph: Grafo[int] | None = None
        self._last_operation: dict[str, Any] = {}
        self._last_result: dict[str, Any] | None = None
        self.create()

    @property
    def graph(self) -> Grafo[int]:
        """Return non-null graph instance."""
        if self._graph is None:
            self.create()
        return self._graph  # type: ignore[return-value]

    def create(self) -> None:
        """Create a default empty undirected graph."""
        self._graph = Grafo(dirigido=False)
        self._last_result = None
        self._record_last_operation(
            name="create_graph",
            status="success",
            message="Grafo creado correctamente (no dirigido).",
        )

    def _record_last_operation(self, name: str, status: str, message: str) -> None:
        """Persist operation outcome for didactic feedback."""
        self._last_operation = {
            "name": name,
            "status": status,
            "message": message,
        }

    def record_failed_operation(self, name: str, message: str) -> None:
        """Persist a failed operation in visual state."""
        self._record_last_operation(name=name, status="error", message=message)

    @staticmethod
    def _require_vertex(payload: dict[str, Any], key: str, label: str) -> int:
        """Read and validate required integer vertex."""
        return BaseAdapter._require_int(payload=payload, key=key, label=label)

    @staticmethod
    def _parse_bool(value: Any) -> bool:
        """Parse bool from mixed input values."""
        if isinstance(value, bool):
            return value
        if isinstance(value, str):
            text = value.strip().lower()
            if text in {"1", "true", "si", "yes"}:
                return True
            if text in {"0", "false", "no"}:
                return False
        if isinstance(value, (int, float)):
            return bool(value)
        raise ValueError("El valor de 'dirigido' es invalido.")

    @staticmethod
    def _parse_weight(payload: dict[str, Any], key: str = "weight") -> int:
        """Parse the integer weight represented by the C graph contract."""
        value = payload.get(key, 1)
        if value is None or str(value).strip() == "":
            return 1
        try:
            if isinstance(value, bool):
                raise ValueError
            parsed = int(value)
            if float(value) != parsed:
                raise ValueError
            return parsed
        except (TypeError, ValueError) as error:
            raise ValueError("El peso debe ser un entero representable por el TAD C.") from error

    def _set_result(self, name: str, result: dict[str, Any]) -> dict[str, Any]:
        """Persist successful result payload."""
        self._last_result = result
        self._record_last_operation(
            name=name,
            status="success",
            message=result.get("message", "Operacion ejecutada correctamente."),
        )
        return result

    @staticmethod
    def _rebuild_path(
        previous: dict[int, int | None],
        start: int,
        end: int,
    ) -> list[int]:
        """Build shortest path from predecessor map."""
        path: list[int] = []
        current: int | None = end

        while current is not None:
            path.append(current)
            if current == start:
                break
            current = previous.get(current)

        if not path or path[-1] != start:
            return []

        path.reverse()
        return path

    def execute(self, operation_name: str, payload: dict[str, Any]) -> dict[str, Any]:
        """Execute one graph operation."""
        if operation_name == "create_graph":
            directed = self._parse_bool(payload.get("directed", False))
            self._graph = Grafo(dirigido=directed)
            self._last_result = None
            return self._set_result(
                operation_name,
                {"message": f"Grafo creado correctamente ({'dirigido' if directed else 'no dirigido'})."},
            )

        if operation_name == "generate_random_graph":
            vertices_count = BaseAdapter._require_int(payload, "vertices_count", "cantidad de vertices")
            if vertices_count <= 0:
                raise ValueError("La cantidad de vertices debe ser mayor que 0.")
            if vertices_count > 200:
                raise ValueError("La cantidad de vertices no puede ser mayor a 200.")

            directed = self.graph.dirigido
            seed_value = payload.get("seed")
            if seed_value is None or str(seed_value).strip() == "":
                seed = random.randint(1, 999_999_999)
                payload["seed"] = seed
            else:
                seed = BaseAdapter._require_int(payload, "seed", "semilla")
            rng = random.Random(seed)

            self._graph = Grafo(dirigido=directed)
            vertices = list(range(1, vertices_count + 1))
            for vertex in vertices:
                self.graph.insertar_vertice(vertex)

            if vertices_count > 1:
                shuffled = vertices[:]
                rng.shuffle(shuffled)
                for index in range(1, len(shuffled)):
                    current = shuffled[index]
                    parent = shuffled[rng.randrange(0, index)]
                    weight = rng.randint(1, 20)
                    self.graph.insertar_arista(parent, current, weight)

            max_edges = (
                vertices_count * (vertices_count - 1)
                if directed
                else (vertices_count * (vertices_count - 1)) // 2
            )
            min_edges = max(0, vertices_count - 1)
            extra_capacity = max(0, max_edges - min_edges)
            extra_edges_target = rng.randint(0, min(extra_capacity, max(1, vertices_count)))

            existing_keys: set[tuple[int, int]] = set()
            for origin, target, _weight in self.graph.aristas():
                o = int(origin)
                t = int(target)
                if directed:
                    existing_keys.add((o, t))
                else:
                    existing_keys.add((min(o, t), max(o, t)))

            attempts = 0
            max_attempts = max(30, extra_edges_target * 20)
            while extra_edges_target > 0 and attempts < max_attempts:
                attempts += 1
                origin = rng.choice(vertices)
                target = rng.choice(vertices)
                if origin == target:
                    continue
                key = (origin, target) if directed else (min(origin, target), max(origin, target))
                if key in existing_keys:
                    continue
                weight = rng.randint(1, 20)
                self.graph.insertar_arista(origin, target, weight)
                existing_keys.add(key)
                extra_edges_target -= 1

            result_edges = self.graph.cantidad_aristas()
            return self._set_result(
                operation_name,
                {
                    "message": (
                        f"Se genero un grafo aleatorio con {vertices_count} vertices y "
                        f"{result_edges} aristas (semilla {seed})."
                    ),
                    "result": {
                        "vertices_count": vertices_count,
                        "edges_count": result_edges,
                        "seed": seed,
                    },
                },
            )

        if operation_name == "insert_vertex":
            vertex = self._require_vertex(payload, "vertex", "vertice")
            self.graph.insertar_vertice(vertex)
            return self._set_result(operation_name, {"message": f"Se inserto el vertice '{vertex}'."})

        if operation_name == "remove_vertex":
            vertex = self._require_vertex(payload, "vertex", "vertice")
            self.graph.eliminar_vertice(vertex)
            return self._set_result(operation_name, {"message": f"Se elimino el vertice '{vertex}'."})

        if operation_name == "insert_edge":
            origin = self._require_vertex(payload, "origin", "origen")
            target = self._require_vertex(payload, "target", "destino")
            weight = self._parse_weight(payload)
            self.graph.insertar_arista(origin, target, weight)
            return self._set_result(
                operation_name,
                {"message": f"Se inserto la arista {origin} -> {target} con peso {weight}."},
            )

        if operation_name == "remove_edge":
            origin = self._require_vertex(payload, "origin", "origen")
            target = self._require_vertex(payload, "target", "destino")
            existed = self.graph.existe_arista(origin, target)
            self.graph.eliminar_arista(origin, target)
            message = (
                f"Se elimino la arista {origin} -> {target}."
                if existed
                else f"La arista {origin} -> {target} no existia; no hubo cambios."
            )
            return self._set_result(operation_name, {"message": message, "result": existed})

        if operation_name == "exists_vertex":
            vertex = self._require_vertex(payload, "vertex", "vertice")
            exists = self.graph.existe_vertice(vertex)
            return self._set_result(
                operation_name,
                {"message": f"Vertice '{vertex}': {'existe' if exists else 'no existe'}.", "result": exists},
            )

        if operation_name == "exists_edge":
            origin = self._require_vertex(payload, "origin", "origen")
            target = self._require_vertex(payload, "target", "destino")
            exists = self.graph.existe_arista(origin, target)
            return self._set_result(
                operation_name,
                {"message": f"Arista {origin} -> {target}: {'existe' if exists else 'no existe'}.", "result": exists},
            )

        if operation_name == "neighbors":
            vertex = self._require_vertex(payload, "vertex", "vertice")
            result = self.graph.vecinos(vertex)
            return self._set_result(
                operation_name,
                {"message": f"Vecinos de '{vertex}': {result}.", "result": result},
            )

        if operation_name == "edge_weight":
            origin = self._require_vertex(payload, "origin", "origen")
            target = self._require_vertex(payload, "target", "destino")
            if not self.graph.existe_arista(origin, target):
                raise ValueError(f"La arista {origin} -> {target} no existe.")
            result = self.graph.peso(origin, target)
            return self._set_result(
                operation_name,
                {"message": f"Peso de {origin} -> {target}: {result}.", "result": result},
            )

        if operation_name == "list_vertices":
            result = self.graph.vertices()
            return self._set_result(operation_name, {"message": f"Vertices: {result}.", "result": result})

        if operation_name == "list_edges":
            result = self.graph.aristas()
            return self._set_result(operation_name, {"message": f"Aristas: {result}.", "result": result})

        if operation_name == "run_bfs":
            start = self._require_vertex(payload, "start", "inicio")
            result = self.graph.bfs(start)
            return self._set_result(operation_name, {"message": f"BFS desde '{start}': {result}.", "result": result})

        if operation_name == "run_dfs":
            start = self._require_vertex(payload, "start", "inicio")
            result = self.graph.dfs(start)
            return self._set_result(operation_name, {"message": f"DFS desde '{start}': {result}.", "result": result})

        if operation_name == "run_dijkstra":
            start = self._require_vertex(payload, "start", "inicio")
            end = self._require_vertex(payload, "end", "destino")
            dist, prev = self.graph.dijkstra(start)
            previous = {key: value for key, value in prev.items()}
            path = self._rebuild_path(previous=previous, start=start, end=end)
            reachable = len(path) > 0
            distance = dist.get(end)
            path_edges = [[path[index], path[index + 1]] for index in range(len(path) - 1)]
            result = {
                "distances": dist,
                "previous": prev,
                "start": start,
                "end": end,
                "path": path,
                "path_edges": path_edges,
                "reachable": reachable,
                "distance_to_destination": distance if reachable else None,
            }
            if reachable:
                route_text = " -> ".join(str(node) for node in path)
                message = (
                    f"Dijkstra desde '{start}' hasta '{end}': "
                    f"distancia minima {distance}, ruta {route_text}."
                )
            else:
                message = f"No existe ruta desde '{start}' hasta '{end}'."
            return self._set_result(
                operation_name,
                {"message": message, "result": result},
            )

        if operation_name == "run_bellman_ford":
            start = self._require_vertex(payload, "start", "inicio")
            end = self._require_vertex(payload, "end", "destino")
            dist, prev, has_negative_cycle = self.graph.bellman_ford(start)
            previous = {key: value for key, value in prev.items()}
            path: list[int] = []
            reachable = False
            distance: float | None = None
            path_edges: list[list[int]] = []

            if not has_negative_cycle:
                path = self._rebuild_path(previous=previous, start=start, end=end)
                reachable = len(path) > 0
                distance = dist.get(end) if reachable else None
                path_edges = [[path[index], path[index + 1]] for index in range(len(path) - 1)]

            result = {
                "distances": dist,
                "previous": prev,
                "has_negative_cycle": has_negative_cycle,
                "start": start,
                "end": end,
                "path": path,
                "path_edges": path_edges,
                "reachable": reachable,
                "distance_to_destination": distance,
            }
            cycle_text = "si" if has_negative_cycle else "no"
            if has_negative_cycle:
                message = (
                    f"Bellman-Ford detecto ciclo negativo desde '{start}'. "
                    "No se puede garantizar ruta minima hacia el destino."
                )
            elif reachable:
                route_text = " -> ".join(str(node) for node in path)
                message = (
                    f"Bellman-Ford desde '{start}' hasta '{end}': "
                    f"distancia minima {distance}, ruta {route_text}. "
                    f"Ciclo negativo: {cycle_text}."
                )
            else:
                message = (
                    f"No existe ruta desde '{start}' hasta '{end}'. "
                    f"Ciclo negativo: {cycle_text}."
                )
            return self._set_result(
                operation_name,
                {"message": message, "result": result},
            )

        if operation_name == "run_prim":
            start_vertex = self._require_vertex(payload, "start", "inicio")
            mst, total = self.graph.prim(start_vertex)
            components = self.graph.componentes_no_dirigidos()
            connected = components <= 1
            result = {
                "mst_edges": mst, "total_weight": total, "connected": connected,
                "components_count": components, "kind": "mst" if connected else "minimum_spanning_forest",
            }
            return self._set_result(
                operation_name,
                {
                    "message": (
                        f"Prim desde '{start_vertex}' ejecutado. "
                        f"Peso total del {'arbol' if connected else 'bosque'} de expansion minima: {total}. "
                        f"Componentes: {components}."
                    ),
                    "result": result,
                },
            )

        if operation_name == "run_kruskal":
            mst, total = self.graph.kruskal()
            components = self.graph.componentes_no_dirigidos()
            connected = components <= 1
            result = {
                "mst_edges": mst, "total_weight": total, "uses_union_find": True,
                "connected": connected, "components_count": components,
                "kind": "mst" if connected else "minimum_spanning_forest",
            }
            return self._set_result(
                operation_name,
                {"message": f"Kruskal ejecutado. Peso total del {'arbol' if connected else 'bosque'}: {total}. Componentes: {components}.", "result": result},
            )

        if operation_name == "clear_graph":
            directed = self.graph.dirigido
            self._graph = Grafo(dirigido=directed)
            self._last_result = None
            return self._set_result(operation_name, {"message": "Grafo limpiado correctamente."})

        raise ValueError(f"Operacion no soportada: {operation_name}.")

    def to_visual_state(self) -> dict[str, Any]:
        """Serialize graph state for frontend rendering."""
        edges = self.graph.aristas()
        nodes = self.graph.vertices()
        weighted = any(float(weight) != 1.0 for _, _, weight in edges)
        return {
            "structure": "graph",
            "directed": self.graph.dirigido,
            "weighted": weighted,
            "nodes": [{"id": str(vertex), "label": str(vertex), "value": str(vertex)} for vertex in nodes],
            "edges": [
                {"source": str(origin), "target": str(target), "weight": weight}
                for origin, target, weight in edges
            ],
            "metadata": {
                "vertices_count": self.graph.cantidad_vertices(),
                "edges_count": self.graph.cantidad_aristas(),
                "is_empty": self.graph.cantidad_vertices() == 0,
            },
            "last_operation": self._last_operation,
            "last_result": self._last_result,
        }

    def reset(self) -> None:
        """Reset graph while preserving directed mode."""
        directed = self.graph.dirigido
        self._graph = Grafo(dirigido=directed)
        self._last_result = None
        self._record_last_operation(
            name="reset",
            status="success",
            message="Estado reiniciado correctamente.",
        )

    def get_supported_operations(self) -> list[dict[str, Any]]:
        """Return dynamic operation metadata for the graph panel."""
        return [
            {
                "name": "create_graph",
                "label": "Crear grafo",
                "mutates": True,
                "inputs": [
                    {
                        "name": "directed",
                        "label": "Tipo",
                        "type": "select",
                        "options": [
                            {"value": "false", "label": "No dirigido"},
                            {"value": "true", "label": "Dirigido"},
                        ],
                    }
                ],
            },
            {
                "name": "generate_random_graph",
                "label": "Generar grafo aleatorio",
                "mutates": True,
                "inputs": [
                    {
                        "name": "vertices_count",
                        "label": "Cantidad de vertices",
                        "type": "number",
                    }
                ],
            },
            {
                "name": "insert_vertex",
                "label": "Insertar vertice",
                "mutates": True,
                "inputs": [{"name": "vertex", "label": "Vertice", "type": "number"}],
            },
            {
                "name": "remove_vertex",
                "label": "Eliminar vertice",
                "mutates": True,
                "inputs": [{"name": "vertex", "label": "Vertice", "type": "number"}],
            },
            {
                "name": "insert_edge",
                "label": "Insertar arista",
                "mutates": True,
                "inputs": [
                    {"name": "origin", "label": "Origen", "type": "number"},
                    {"name": "target", "label": "Destino", "type": "number"},
                    {"name": "weight", "label": "Peso", "type": "number"},
                ],
            },
            {
                "name": "remove_edge",
                "label": "Eliminar arista",
                "mutates": True,
                "inputs": [
                    {"name": "origin", "label": "Origen", "type": "number"},
                    {"name": "target", "label": "Destino", "type": "number"},
                ],
            },
            {
                "name": "exists_vertex",
                "label": "Existe vertice",
                "mutates": False,
                "inputs": [{"name": "vertex", "label": "Vertice", "type": "number"}],
            },
            {
                "name": "exists_edge",
                "label": "Existe arista",
                "mutates": False,
                "inputs": [
                    {"name": "origin", "label": "Origen", "type": "number"},
                    {"name": "target", "label": "Destino", "type": "number"},
                ],
            },
            {"name": "list_vertices", "label": "Listar vertices", "mutates": False, "inputs": []},
            {"name": "list_edges", "label": "Listar aristas", "mutates": False, "inputs": []},
            {
                "name": "neighbors",
                "label": "Vecinos",
                "mutates": False,
                "inputs": [{"name": "vertex", "label": "Vertice", "type": "number"}],
            },
            {
                "name": "edge_weight",
                "label": "Consultar peso",
                "mutates": False,
                "inputs": [
                    {"name": "origin", "label": "Origen", "type": "number"},
                    {"name": "target", "label": "Destino", "type": "number"},
                ],
            },
            {
                "name": "run_bfs",
                "label": "BFS",
                "mutates": False,
                "inputs": [{"name": "start", "label": "Inicio", "type": "number"}],
            },
            {
                "name": "run_dfs",
                "label": "DFS",
                "mutates": False,
                "inputs": [{"name": "start", "label": "Inicio", "type": "number"}],
            },
            {
                "name": "run_dijkstra",
                "label": "Dijkstra",
                "mutates": False,
                "inputs": [
                    {"name": "start", "label": "Inicio", "type": "number"},
                    {"name": "end", "label": "Destino", "type": "number"},
                ],
            },
            {
                "name": "run_bellman_ford",
                "label": "Bellman-Ford",
                "mutates": False,
                "inputs": [
                    {"name": "start", "label": "Inicio", "type": "number"},
                    {"name": "end", "label": "Destino", "type": "number"},
                ],
            },
            {
                "name": "run_prim",
                "label": "Prim",
                "mutates": False,
                "inputs": [{"name": "start", "label": "Inicio", "type": "number"}],
            },
            {"name": "run_kruskal", "label": "Kruskal", "mutates": False, "inputs": []},
            {"name": "clear_graph", "label": "Limpiar grafo", "mutates": True, "inputs": []},
        ]
