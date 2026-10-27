"""Adapter for graph structure and algorithms."""

from __future__ import annotations

from typing import Any

from app.adapters.base_adapter import BaseAdapter
from app.domain.graph import Grafo
from app.domain.graph.educational_capacity import MAX_VERTICES, check_capacity


class GraphAdapter(BaseAdapter):
    """Adapt `Grafo` to the common visualizer contract."""

    def __init__(self) -> None:
        """Initialize adapter state."""
        self._enforce_educational_limit = True
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
        """Normalize finite integral values within the downloaded C int range."""
        from app.domain.graph.integer_algorithms import integer_weight
        value = payload.get(key, 1)
        if value is None or str(value).strip() == "":
            return 1
        return integer_weight(value)

    def _set_result(self, name: str, result: dict[str, Any]) -> dict[str, Any]:
        """Persist successful result payload."""
        self._last_result = result
        self._record_last_operation(
            name=name,
            status="success" if result.get("success", True) else "error",
            message=result.get("message", "Operacion ejecutada correctamente."),
        )
        return result

    def execute(self, operation_name: str, payload: dict[str, Any]) -> dict[str, Any]:
        """Execute only the canonical book C interpreter; no legacy algorithm fallback."""
        from app.domain.graph.book_application import execute_book_operation
        if self._enforce_educational_limit:
            check_capacity(self.graph, operation_name, payload, self._require_vertex, BaseAdapter._require_int)
        return self._set_result(operation_name, execute_book_operation(self, operation_name, payload))

    def to_visual_state(self) -> dict[str, Any]:
        """Serialize graph state for frontend rendering."""
        # Presentation may combine equal reverse arcs, but raw C arcs remain available.
        arcs = list(self.graph._g._arcos)
        edges = []
        seen = set()
        for origin, target, weight in arcs:
            key = (origin, target, weight) if self.graph.dirigido else (min(origin, target), max(origin, target), weight)
            if key not in seen:
                seen.add(key)
                edges.append((origin, target, weight))
        nodes = list(self.graph._g._vertices)
        weighted = any(weight != 1 for _, _, weight in edges)
        arc_set = set(arcs)
        asymmetric = [{"source":str(o), "target":str(d), "weight":w} for o, d, w in arcs if (d, o, w) not in arc_set] if not self.graph.dirigido else []
        return {
            "structure": "graph",
            "directed": self.graph.dirigido,
            "weighted": weighted,
            "nodes": [{"id": str(vertex), "label": str(vertex), "value": str(vertex), "marked": self.graph._g._marcas.get(vertex, 0)} for vertex in nodes],
            "edges": [
                {"source": str(origin), "target": str(target), "weight": weight}
                for origin, target, weight in edges
            ],
            "c_arcs": [{"source":str(o), "target":str(d), "weight":w} for o, d, w in arcs],
            "asymmetric_pairs": asymmetric,
            "source_contract": "graph-book/v1",
            "metadata": {
                "vertices_count": len(nodes),
                "edges_count": len(edges),
                "c_arcs_count": len(arcs),
                "is_empty": self.graph.cantidad_vertices() == 0,
            },
            "last_operation": self._last_operation,
            "last_result": self._last_result,
        }

    def reset(self) -> None:
        """Reset graph while preserving directed mode."""
        self.execute("clear_graph", {})
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
                        "label": f"Cantidad de vertices (maximo {MAX_VERTICES})",
                        "type": "number",
                        "min": 1, "max": MAX_VERTICES, "step": 1,
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
