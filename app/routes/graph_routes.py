"""Routes for the graph structures module."""

from __future__ import annotations

from typing import Any

from flask import Blueprint, abort, jsonify, render_template, request

from app.services.graph_help_service import GraphHelpService
from app.services.graph_structure_service import GraphStructureService
from app.services.session_service import SessionService

graph_bp = Blueprint("graph", __name__, url_prefix="/graph")

_GRAPH_PHASES: dict[str, dict[str, Any]] = {
    "construccion": {
        "title": "Construcción del grafo",
        "description": "Configura tipo de grafo y administra vertices/aristas.",
        "operations": {
            "insert_vertex",
            "generate_random_graph",
            "remove_vertex",
            "insert_edge",
            "remove_edge",
            "list_vertices",
            "list_edges",
            "neighbors",
            "edge_weight",
        },
        "algorithms": {"run_bfs", "run_dfs", "run_dijkstra", "run_bellman_ford", "run_prim", "run_kruskal"},
        "default_algorithm": "",
        "run_mode": "operation",
    },
    "recorridos": {
        "title": "Recorridos",
        "description": "Ejecuta BFS o DFS y analiza el orden de visita.",
        "operations": {
            "insert_vertex",
            "generate_random_graph",
            "remove_vertex",
            "insert_edge",
            "remove_edge",
            "list_vertices",
            "list_edges",
            "neighbors",
            "edge_weight",
        },
        "algorithms": {"run_bfs", "run_dfs"},
        "default_algorithm": "run_bfs",
        "run_mode": "algorithm",
    },
    "camino-minimo": {
        "title": "Camino mínimo",
        "description": "Calcula rutas mínimas con Dijkstra o Bellman-Ford.",
        "operations": {
            "insert_vertex",
            "generate_random_graph",
            "remove_vertex",
            "insert_edge",
            "remove_edge",
            "list_vertices",
            "list_edges",
            "neighbors",
            "edge_weight",
        },
        "algorithms": {"run_dijkstra", "run_bellman_ford"},
        "default_algorithm": "run_dijkstra",
        "run_mode": "algorithm",
    },
    "expansion-minima": {
        "title": "Árbol de expansión mínima",
        "description": "Ejecuta Prim o Kruskal en grafos no dirigidos.",
        "operations": {
            "insert_vertex",
            "generate_random_graph",
            "remove_vertex",
            "insert_edge",
            "remove_edge",
            "list_vertices",
            "list_edges",
            "neighbors",
            "edge_weight",
        },
        "algorithms": {"run_prim", "run_kruskal"},
        "default_algorithm": "run_prim",
        "run_mode": "algorithm",
    },
}

_GRAPH_DIDACTIC_NOTES: dict[str, dict[str, Any]] = {
    "construccion": {
        "default": (
            "Construccion del grafo: define si es dirigido o no dirigido, luego agrega o elimina vertices/aristas. "
            "La simulacion debe reflejar altas, bajas y consultas sobre la lista de adyacencia."
        ),
        "operations": {
            "create_graph": (
                "Crear/Reiniciar: limpia la estructura e inicializa un grafo vacio con el tipo elegido "
                "(dirigido o no dirigido)."
            ),
            "generate_random_graph": (
                "Generacion aleatoria: con N vertices construye un grafo conectado base y agrega aristas extra, "
                "manteniendo pesos positivos para facilitar pruebas de recorridos y caminos."
            ),
            "insert_vertex": "Insertar vertice: agrega el vertice si no existe y actualiza la representacion del grafo.",
            "remove_vertex": (
                "Eliminar vertice: quita el vertice y todas sus aristas incidentes para conservar consistencia."
            ),
            "insert_edge": (
                "Insertar arista/arco: conecta origen-destino con su peso. En no dirigido se refleja en ambos sentidos."
            ),
            "remove_edge": "Eliminar arista/arco: borra la conexion indicada (y su espejo si el grafo no es dirigido).",
            "neighbors": "Vecinos: lista sucesores/adyacentes del vertice segun el tipo de grafo.",
            "edge_weight": "Peso de arista: consulta el costo asociado a una conexion origen-destino.",
            "list_vertices": "Vertices: devuelve el conjunto actual de vertices del grafo.",
            "list_edges": "Aristas: devuelve las conexiones actuales con sus pesos.",
        },
    },
    "recorridos": {
        "default": (
            "Recorridos: exploran el grafo desde un origen respetando vertices marcados para no repetir visitas."
        ),
        "algorithms": {
            "run_bfs": (
                "BFS (anchura): usa una cola FIFO. Visita por niveles: primero los vecinos cercanos, "
                "luego los de mayor distancia."
            ),
            "run_dfs": (
                "DFS (profundidad): sigue una rama hasta el fondo (recursion o pila) y luego retrocede "
                "con backtracking."
            ),
        },
    },
    "camino-minimo": {
        "default": (
            "Camino minimo: compara distancias tentativas y predecesores para reconstruir la ruta de menor costo."
        ),
        "algorithms": {
            "run_dijkstra": (
                "Dijkstra: selecciona el vertice no visitado con menor distancia y relaja sus aristas salientes. "
                "Requiere pesos no negativos."
            ),
            "run_bellman_ford": (
                "Bellman-Ford: relaja todas las aristas en V-1 iteraciones y detecta ciclos negativos en una pasada final."
            ),
        },
    },
    "expansion-minima": {
        "default": (
            "Arbol de expansion minima: selecciona aristas de menor costo para conectar todos los vertices "
            "sin formar ciclos."
        ),
        "algorithms": {
            "run_prim": (
                "Prim: crece un arbol desde un vertice inicial, agregando siempre la arista minima que conecta "
                "un nodo nuevo."
            ),
            "run_kruskal": (
                "Kruskal: ordena aristas por peso y agrega solo las que no formen ciclo, usando Union-Find."
            ),
        },
    },
}


@graph_bp.get("/")
def graph_index() -> str:
    """Render graph structures cards page."""
    structures = GraphStructureService.list_structures()
    return render_template("graph/index.html", structures=structures)


@graph_bp.get("/<structure_id>")
def structure_page(structure_id: str) -> str:
    """Render one graph structure interaction page (fase de construccion por defecto)."""
    return _render_graph_phase(structure_id, "construccion")


@graph_bp.get("/<structure_id>/<phase>")
def structure_phase_page(structure_id: str, phase: str) -> str:
    """Render one graph structure interaction page by learning phase."""
    return _render_graph_phase(structure_id, phase)


def _render_graph_phase(structure_id: str, phase: str) -> str:
    """Build and render graph page for one selected phase."""
    session_key = f"graph::{structure_id}"
    phase_data = _GRAPH_PHASES.get(phase)
    if phase_data is None:
        abort(404)
    try:
        history = SessionService.get_history(session_key)
        model = GraphStructureService.get_view_model(structure_id, history)
    except KeyError:
        abort(404)

    help_data = GraphHelpService.get_structure_help(structure_id)
    return render_template(
        "graph/structure.html",
        model=model,
        help_data=help_data,
        graph_phase=phase,
        graph_phase_data=phase_data,
        graph_phase_order=list(_GRAPH_PHASES.keys()),
        graph_phases=_GRAPH_PHASES,
        graph_didactic_notes=_GRAPH_DIDACTIC_NOTES,
        graph_phase_note=_GRAPH_DIDACTIC_NOTES.get(phase, {}).get("default", help_data.get("summary", "")),
    )


@graph_bp.post("/<structure_id>/operate")
def operate_structure(structure_id: str) -> Any:
    """Execute one graph operation and return JSON response."""
    session_key = f"graph::{structure_id}"
    history = SessionService.get_history(session_key)
    body = request.get_json(silent=True) or {}
    operation_name = str(body.get("operation", "")).strip()
    payload = body.get("payload", {})

    if not operation_name:
        return jsonify({"success": False, "message": "Debes seleccionar una operación."}), 400
    if not isinstance(payload, dict):
        return jsonify({"success": False, "message": "El payload enviado es invalido."}), 400

    try:
        result = GraphStructureService.execute_operation(
            structure_id=structure_id,
            operation_name=operation_name,
            payload=payload,
            history=history,
        )
    except KeyError:
        return jsonify({"success": False, "message": "La estructura solicitada no existe."}), 404

    SessionService.save_history(session_key, result["history"])
    return jsonify(result), (200 if result["success"] else 400)


@graph_bp.post("/<structure_id>/reset")
def reset_structure(structure_id: str) -> Any:
    """Reset one graph structure state in user session."""
    session_key = f"graph::{structure_id}"
    try:
        GraphStructureService.get_structure(structure_id)
    except KeyError:
        return jsonify({"success": False, "message": "La estructura solicitada no existe."}), 404

    SessionService.clear_history(session_key)
    model = GraphStructureService.get_view_model(structure_id, [])
    return jsonify(
        {
            "success": True,
            "message": "La estructura fue reiniciada.",
            "visual_state": model["visual_state"],
            "history": [],
        }
    )
