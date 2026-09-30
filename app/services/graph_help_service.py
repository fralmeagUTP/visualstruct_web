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
            "learning_guide": {
                "objective": "Interpretar cómo el código C transforma representación, auxiliares y propiedades del grafo en cada instrucción ejecutada.",
                "strategy": "Predecir, avanzar un frame, contrastar la evidencia y explicar el invariante antes de continuar.",
                "invariants": ["BFS descubre una sola vez y usa FIFO.", "DFS conserva una pila coherente.", "Dijkstra solo cierra mínimos con pesos no negativos.", "Bellman-Ford distingue inalcanzable de ciclo negativo alcanzable.", "Prim y Kruskal producen un árbol o bosque acíclico de peso mínimo."],
                "memory": "Los vértices y enlaces muestran direcciones lógicas estables; malloc, NULL, desconexión y free se relacionan con el dibujo.",
                "complexity": {"BFS/DFS": "O(V+E)", "Dijkstra": "O(V²+E) en el TAD didáctico", "Bellman-Ford": "O(VE)", "Prim": "O(VE)", "Kruskal": "O(E log E) más Union-Find"},
                "applications": ["redes y conectividad", "rutas y costos", "dependencias", "diseño de redes mínimas"],
                "common_errors": ["confundir menor número de aristas con menor peso", "usar Dijkstra con pesos negativos", "olvidar componentes desconectadas", "aceptar una arista que cierra ciclo"],
            },
            "glossary": {"adyacencia": "Relación directa entre dos vértices.", "frontera": "Candidatos todavía no incorporados.", "relajación": "Intento de mejorar una distancia mediante una arista.", "predecesor": "Vértice anterior usado para reconstruir una ruta.", "MST": "Árbol de expansión de peso total mínimo.", "Union-Find": "Estructura que mantiene componentes disjuntas."},
            "teacher_guide": ["Solicitar una predicción antes de cada extracción o relajación.", "Comparar algoritmos con la misma entrada y pedir una conclusión causal.", "Usar contraejemplos: peso negativo, destino inalcanzable, ciclo y grafo desconectado.", "Evaluar la explicación del invariante, no solo el resultado final."],
            "keyboard": ["Alt+→ siguiente", "Alt+← anterior", "Alt+Inicio inicio", "Alt+Fin final", "Alt+P pausar"],
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
