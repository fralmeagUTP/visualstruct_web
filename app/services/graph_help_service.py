"""Didactic help content for graph structures."""

from __future__ import annotations

from typing import Any


class GraphHelpService:
    """Serve educational texts for the graph module."""

    _MODULE_HELP = {
        "title": "Ayuda del modulo de grafos",
        "description": (
            "Este modulo separa construccion y algoritmos para interpretar codigo C de grafos "
            "de forma didactica: primero se modela el grafo y luego se simulan recorridos, "
            "caminos minimos y expansion minima paso a paso o en modo rapido de resultado final."
        ),
        "tips": [
            "Flujo sugerido: define tipo de grafo, crea vertices/aristas y despues ejecuta el algoritmo.",
            "Usa Reproducir para la traza completa y Siguiente/Anterior paso para validar condiciones y actualizaciones.",
            "Si desactivas 'Interpretar codigo paso a paso', Reproducir aplica directamente el estado final.",
            "El resultado visual final en modo rapido debe coincidir con el ultimo estado de la traza interpretada.",
            "Interpreta el estado visual junto con 'Accion actual' para distinguir exploracion, relajacion y cierre.",
            "Con pesos negativos usa Bellman-Ford; para no dirigidos ponderados compara Prim y Kruskal.",
            "Ejecuta BFS y DFS desde el mismo origen para contrastar ordenes de visita.",
        ],
    }

    _STRUCTURE_HELP: dict[str, dict[str, Any]] = {
        "graph": {
            "title": "Grafo",
            "summary": (
                "Representacion por lista de adyacencia para grafos dirigidos o no dirigidos, con peso opcional. "
                "La simulacion interpreta el codigo C por subrutinas y muestra visualmente recorridos, "
                "relajacion de aristas, rutas minimas y expansion minima segun el algoritmo seleccionado."
            ),
            "supported_operations": [
                "create_graph",
                "insert_vertex",
                "generate_random_graph",
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
