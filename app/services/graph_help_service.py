"""Didactic help content for graph structures."""

from __future__ import annotations

from typing import Any


class GraphHelpService:
    """Serve educational texts for the graph module."""

    _MODULE_HELP = {
        "title": "Ayuda del modulo de grafos",
        "description": (
            "El modulo de grafos permite crear grafos dirigidos y no dirigidos, "
            "insertar vertices/aristas y ejecutar algoritmos clasicos sobre el TAD real."
        ),
        "tips": [
            "Crea el grafo dirigido/no dirigido antes de probar Prim o Kruskal.",
            "Si hay pesos negativos, usa Bellman-Ford en lugar de Dijkstra.",
            "Compara BFS y DFS desde el mismo vertice inicial.",
        ],
    }

    _STRUCTURE_HELP: dict[str, dict[str, Any]] = {
        "graph": {
            "title": "Grafo",
            "summary": "Representacion por lista de adyacencia con recorridos y caminos minimos.",
            "supported_operations": [
                "create_graph",
                "insert_vertex",
                "remove_vertex",
                "insert_edge",
                "remove_edge",
                "exists_vertex",
                "exists_edge",
                "neighbors",
                "edge_weight",
                "list_vertices",
                "list_edges",
                "run_bfs",
                "run_dfs",
                "run_dijkstra",
                "run_bellman_ford",
                "run_prim",
                "run_kruskal",
                "clear_graph",
            ],
            "pending_operations": [
                "Union-Find no tiene pagina independiente: se integra conceptualmente en Kruskal.",
                "No se implementan algoritmos adicionales no expuestos por el TAD (por ejemplo, Floyd-Warshall).",
            ],
        }
    }

    @staticmethod
    def get_module_help() -> dict[str, Any]:
        """Return didactic help for graph module."""
        return GraphHelpService._MODULE_HELP

    @staticmethod
    def get_structure_help(structure_id: str) -> dict[str, Any]:
        """Return help for one graph structure."""
        return GraphHelpService._STRUCTURE_HELP.get(
            structure_id,
            {
                "title": "Estructura no encontrada",
                "summary": "No hay ayuda disponible para esta estructura.",
                "supported_operations": [],
                "pending_operations": [],
            },
        )
