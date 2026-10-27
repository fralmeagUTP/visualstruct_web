"""Didactic help content for graph structures."""

from __future__ import annotations

from typing import Any

from app.domain.graph.educational_capacity import MAX_VERTICES


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
            f"Límite educativo de la aplicación: {MAX_VERTICES} vértices distintos, incluidos extremos creados por aristas. Los históricos de otro contrato se conservan sin reinterpretarlos silenciosamente. El C/H descargable coincide con el libro.",
            "Flujo sugerido: define tipo de grafo, crea vertices/aristas y despues ejecuta el algoritmo.",
            "Activa Paso a paso y pulsa Ejecutar operación; usa Siguiente paso y Paso anterior para validar condiciones y actualizaciones.",
            "Al cerrar Paso a paso se muestra el estado final de la misma ejecución; navegar no repite la operación.",
            "El resultado visual final en modo rapido debe coincidir con el ultimo estado de la traza interpretada.",
            "Interpreta el estado visual junto con 'Accion actual' para distinguir exploracion, relajacion y cierre.",
            "Con pesos negativos usa Bellman-Ford; para no dirigidos ponderados compara Prim y Kruskal.",
            "Ejecuta BFS y DFS desde el mismo origen para contrastar ordenes de visita.",
            "BFS usa t.prev como cola de índices y t.usado como marcas temporales. Las marcas del grafo se publican sólo al terminar con éxito; -1 sigue siendo un vértice válido.",
            "El historial graph-book/v1 conserva las llamadas C ejecutadas, incluidos sus estados de error; al recargar se reproducen con el mismo contrato. El main ordinario calcula resultados y libera listas propias; los fallos de malloc inyectados requieren el harness diagnóstico.",
        ],
    }

    _STRUCTURE_HELP: dict[str, dict[str, Any]] = {
        "graph": {
            "title": "Grafo",
            "max_vertices": MAX_VERTICES,
            "summary": (
                "Listas enlazadas separadas de vértices y arcos con pesos enteros. La vista no dirigida usa llamadas para ambos sentidos. "
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
                "invariants": ["BFS descubre una sola vez con una cola FIFO de índices en t.prev; no usa el TAD Cola externo.", "DFS conserva sus marcos recursivos y publica las marcas del grafo sólo al éxito.", "Dijkstra solo cierra mínimos con pesos no negativos.", "Bellman-Ford distingue inalcanzable de ciclo negativo alcanzable.", "Prim y Kruskal requieren simetría y conectividad; si falla, notifican un estado y liberan el parcial, no publican un bosque."],
                "memory": "Los identificadores de memoria son simbólicos, no direcciones reales. Trabajo posee arreglos temporales; vértices/arcos consultados son prestados y recorridos/vecinos/caminos devueltos son propios.",
                "complexity": {"BFS/DFS": "Modelo ideal O(V+E); el C obtiene vecinos barriendo arcos y busca índices linealmente.", "Dijkstra": "Modelo ideal de selección lineal O(V²+E); el C además barre arcos y busca índices linealmente.", "Bellman-Ford": "Modelo ideal O(VE); el C busca índices linealmente durante cada barrido de arcos.", "Prim": "El C valida simetría buscando arcos inversos, selecciona mínimos y busca índices linealmente.", "Kruskal": "El C valida simetría, ordena arcos con burbuja y aplica Union-Find; no se presupone un ordenamiento O(E log E)."},
                "applications": ["redes y conectividad", "rutas y costos", "dependencias", "diseño de redes mínimas"],
                "common_errors": ["confundir menor número de aristas con menor peso", "usar Dijkstra con pesos negativos", "olvidar componentes desconectadas", "aceptar una arista que cierra ciclo"],
            },
            "book_contract": [
                "La vista pedagógica admite hasta 15 vértices. Una traza conserva como máximo 4.000 eventos C/llamador más la publicación final; no se recortan pasos. Si supera el presupuesto, reduce el ejemplo o usa modo normal, que devuelve el resultado completo sin guardar una traza extensa.",
                "Los historiales del contrato anterior quedan suspendidos, no vacíos: se pueden exportar sin reinterpretarlos. Restablecer datos requiere confirmación para empezar con el código del libro.",
                "GrafoEstado: 0 OK; 1 MEMORIA; 2 NO_EXISTE; 3 PESO_NEGATIVO; 4 CICLO_NEGATIVO; 5 DESCONECTADO; 6 ARGUMENTO; 7 RANGO.",
                "NULL no determina el éxito: un camino de un vértice a sí mismo o un MST de un solo vértice puede ser NULL con GRAFO_OK.",
                "grafo_costo_arco retorna int 0/1 y escribe el costo en int *salida sólo si retorna 1; costo cero es válido.",
                "Las distancias usan long long; alcanzable distingue ausencia de distancia. INT_MAX no se usa como infinito. sumar_seguro devuelve 0 si detecta desbordamiento; el algoritmo llamador lo traduce a GRAFO_RANGO.",
                "grafo_eliminar_vertice retira y libera los arcos incidentes dentro del C del libro; el main no repite esa eliminación.",
                "grafo_vertices y grafo_arcos prestan sus listas: no se liberan como resultados propios. Vecinos, recorridos, caminos y MST propios se liberan con grafo_liberar_vertices o grafo_liberar_arcos.",
                "El modo no dirigido ejecuta una llamada por sentido; la inversa sólo se intenta si la primera termina OK. No hay transacción conjunta: fallar la segunda no deshace la primera.",
            ],
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
