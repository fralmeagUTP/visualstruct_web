"""Routes for didactic help pages."""

from __future__ import annotations

from copy import deepcopy
import re

from flask import Blueprint, render_template

from app.services.hash_help_service import HashHelpService
from app.services.hash_structure_service import HashStructureService
from app.services.graph_help_service import GraphHelpService
from app.services.graph_structure_service import GraphStructureService
from app.services.hierarchical_help_service import HierarchicalHelpService
from app.services.hierarchical_structure_service import HierarchicalStructureService
from app.services.help_service import HelpService
from app.services.c_code_service import CCodeService
from app.services.structure_service import StructureService

help_bp = Blueprint("help", __name__, url_prefix="/help")

_TAD_INTRODUCTIONS: dict[str, str] = {
    "stack": (
        "La Pila (LIFO) modela escenarios donde el ultimo elemento agregado es el primero en salir. "
        "En C se implementa con nodos enlazados y un puntero al tope; por eso la simulacion enfatiza "
        "creacion de auxiliares, reasignacion de punteros y liberacion de memoria."
    ),
    "queue": (
        "La Cola (FIFO) conserva el orden de llegada. Su TAD en C mantiene referencias al frente y al final, "
        "y cada operacion debe preservar consistencia cuando la estructura pasa de vacia a no vacia y viceversa."
    ),
    "priority_queue": (
        "La Cola de Prioridad atiende primero el elemento con mayor prioridad logica (segun contrato del TAD). "
        "La interpretacion muestra comparaciones para ubicar el nuevo nodo en la posicion correcta."
    ),
    "linked_list": (
        "La Lista Enlazada representa una secuencia dinamica de nodos conectados por punteros. "
        "Es clave entender desplazamiento por posicion, manejo de cabecera y casos borde en insercion/eliminacion."
    ),
    "circular_list": (
        "La Lista Circular reutiliza el ultimo enlace para volver al primer nodo. "
        "La simulacion permite verificar que el ciclo nunca se rompa tras cada actualizacion de enlaces."
    ),
    "sublist": (
        "La Sublista agrega un segundo nivel de enlaces: nodos padre y sus hijos. "
        "El foco didactico esta en aislar cambios por rama sin corromper otras relaciones."
    ),
    "abb": (
        "El ABB organiza claves por orden: menores a la izquierda y mayores a la derecha. "
        "La traza debe reflejar comparaciones sucesivas, decisiones condicionales y retorno recursivo."
    ),
    "avl": (
        "El AVL extiende al ABB con balanceo automatico. "
        "Ademas de insertar/eliminar, se interpretan factores de equilibrio y rotaciones para sostener altura logaritmica."
    ),
    "red_black": (
        "El Arbol Rojo-Negro usa reglas de color para mantener balance aproximado. "
        "Didacticamente interesa seguir recoloreos, rotaciones y validacion de invariantes tras cada cambio."
    ),
    "binary_heap": (
        "El Monticulo Binario (min-heap) se almacena en arreglo y se visualiza como arbol casi completo. "
        "Cada operacion aplica sift-up o sift-down para restaurar la propiedad de heap."
    ),
    "graph": (
        "El TAD de Grafo modela vertices y aristas (dirigidas o no) con pesos opcionales. "
        "La interpretacion separa construccion del grafo y ejecucion de algoritmos sobre el mismo estado."
    ),
    "hash_table": (
        "La Tabla Hash mapea claves a buckets mediante una funcion hash. "
        "La simulacion muestra colisiones, encadenamiento y eventos de rehash al crecer la carga."
    ),
}

_METHOD_EXPLANATIONS: dict[str, str] = {
    "apilar": "Reserva un nodo auxiliar, copia el valor, enlaza el nodo al tope actual y actualiza el puntero principal.",
    "desapilar": "Valida pila no vacia, extrae el nodo del tope, reasigna el tope al siguiente y libera memoria del nodo removido.",
    "limpiar": "Recorre la estructura liberando todos los nodos y deja el puntero raiz en estado nulo para reinicio seguro.",
    "encolar": "Crea nodo nuevo y lo conecta al final; si la cola estaba vacia actualiza tanto frente como final.",
    "desencolar": "Extrae el nodo del frente, avanza el puntero de frente y ajusta final cuando se elimina el ultimo elemento.",
    "frente": "Consulta el valor del nodo frontal sin modificar enlaces, preservando el estado interno.",
    "insertar_inicio": "Inserta nodo al inicio: enlaza el nuevo nodo antes del actual primero y actualiza la cabecera.",
    "insertar_final": "Recorre hasta el ultimo nodo y conecta el nuevo elemento al final de la secuencia.",
    "lista_insertar_elemento": "Inserta por posicion base segun contrato del TAD, ajustando enlaces previo/siguiente en el punto objetivo.",
    "buscar_elemento": "Recorre secuencialmente comparando valores hasta encontrar coincidencia o agotar la lista.",
    "mostrar": "Recorre la estructura para construir una salida ordenada sin alterar enlaces internos.",
    "eliminar_elemento": "Busca la primera ocurrencia, reconecta vecinos para excluir el nodo y libera su memoria.",
    "eliminar_repetidos": "Detecta duplicados durante el recorrido, elimina ocurrencias adicionales y conserva solo una por valor.",
    "eliminar_inicio": "Remueve la cabecera, mueve el inicio al siguiente nodo y libera el nodo anterior.",
    "eliminar_primero": "Elimina la primera coincidencia de un valor y recompone enlaces para mantener continuidad.",
    "buscar_posiciones": "Recorre toda la lista y registra todas las posiciones donde aparece el valor buscado.",
    "invertir": "Reasigna enlaces nodo a nodo para invertir la direccion completa de la lista.",
    "insertar_padre": "Crea nodo padre en la lista principal de sublistas manteniendo su cadena independiente.",
    "insertar_hijo": "Localiza el padre objetivo y agrega el hijo en su sublista, sin afectar otros padres.",
    "eliminar_padre": "Elimina un padre y libera recursivamente/iterativamente su sublista de hijos asociada.",
    "eliminar_hijo": "Dentro del padre indicado, busca el hijo por valor y lo elimina ajustando enlaces locales.",
    "hijos_de": "Devuelve la coleccion de hijos del padre solicitado sin modificar la estructura.",
    "insertar": "Inserta respetando reglas de orden/balance del TAD y actualiza punteros estructurales necesarios.",
    "eliminar": "Localiza el objetivo y aplica el caso de borrado correspondiente (hoja, un hijo, dos hijos o rebalanceo).",
    "buscar": "Navega por comparaciones hasta encontrar el valor o concluir que no existe.",
    "minimo": "Avanza por la rama izquierda hasta el ultimo nodo para obtener el menor valor del subarbol.",
    "maximo": "Avanza por la rama derecha hasta el ultimo nodo para obtener el mayor valor del subarbol.",
    "altura": "Calcula la altura estructural a partir de la profundidad maxima de sus ramas.",
    "contar_hojas": "Cuenta nodos sin hijos para medir terminales del arbol.",
    "inorden": "Recorrido izquierda-raiz-derecha; en ABB produce valores ordenados de menor a mayor.",
    "preorden": "Recorrido raiz-izquierda-derecha; util para serializar la forma del arbol.",
    "postorden": "Recorrido izquierda-derecha-raiz; usado en liberacion segura de memoria.",
    "validar": "Comprueba invariantes del TAD (orden, balance o reglas de color segun corresponda).",
    "raiz": "Retorna el valor de la raiz o tope logico de la estructura sin mutarla.",
    "a_lista": "Exporta el contenido interno a una representacion lineal para inspeccion externa.",
    "create_graph": "Inicializa/reinicia el grafo y configura su modalidad dirigido/no dirigido.",
    "generate_random_graph": "Construye un grafo aleatorio controlado por cantidad de vertices, garantizando conectividad base.",
    "insert_vertex": "Agrega un nuevo vertice si no existe en el conjunto actual.",
    "remove_vertex": "Elimina vertice y todas las aristas incidentes para mantener consistencia topologica.",
    "insert_edge": "Crea arista entre origen y destino con su peso; en no dirigido replica la conexion inversa.",
    "remove_edge": "Elimina la arista objetivo (y su espejo en grafos no dirigidos).",
    "exists_vertex": "Consulta booleana de existencia de vertice en el grafo.",
    "exists_edge": "Consulta booleana de existencia de arista entre dos vertices.",
    "neighbors": "Obtiene adyacentes/sucesores del vertice de entrada.",
    "edge_weight": "Recupera el peso asociado a una arista especifica.",
    "list_vertices": "Lista todos los vertices actualmente registrados.",
    "list_edges": "Lista todas las aristas con sus pesos actuales.",
    "run_bfs": "Ejecuta recorrido en anchura usando cola, visitando por capas desde el vertice inicial.",
    "run_dfs": "Ejecuta recorrido en profundidad con recursion/pila, explorando cada rama antes de retroceder.",
    "run_dijkstra": "Relaja aristas desde distancias minimas tentativas con pesos no negativos.",
    "run_bellman_ford": "Relaja todas las aristas repetidamente y detecta ciclos negativos.",
    "run_prim": "Construye arbol de expansion minima agregando la arista minima que conecta un nuevo vertice.",
    "run_kruskal": "Construye AEM ordenando aristas por peso y evitando ciclos con Union-Find.",
    "clear_graph": "Vacía vertices y aristas dejando el grafo listo para una nueva construccion.",
    "create_table": "Inicializa la tabla hash con su capacidad y parametros de control de carga.",
    "insert": "Calcula bucket hash e inserta/actualiza clave-valor, gestionando colisiones por encadenamiento.",
    "get": "Busca una clave y retorna su valor asociado si existe en la tabla.",
    "contains": "Verifica existencia de una clave sin extraer ni modificar su valor.",
    "remove": "Elimina una clave del bucket correspondiente y ajusta enlaces de la cadena.",
    "keys": "Devuelve todas las claves activas de la tabla.",
    "values": "Devuelve todos los valores almacenados actualmente.",
    "items": "Devuelve pares clave-valor para inspeccion completa del contenido.",
    "stats": "Calcula metricas de carga, buckets usados y colisiones para diagnostico.",
    "clear": "Limpia la tabla completa y reinicia su estado interno.",
}


def _normalize_operation_name(operation_label: str) -> str:
    """Normalize operation labels to operation ids used in C-code maps."""
    return str(operation_label).split("(", 1)[0].strip()


def _resolve_tad_introduction(enriched: dict, structure_id: str) -> str:
    """Return a detailed introduction for a TAD help page."""
    intro = _TAD_INTRODUCTIONS.get(structure_id, "")
    if intro:
        return intro
    summary = str(enriched.get("summary", "")).strip()
    if summary:
        return summary
    title = str(enriched.get("title", "TAD")).strip()
    return f"Esta seccion describe el TAD {title}, su contrato y su implementacion en C."


def _build_tad_description(summary: str, introduction: str) -> str:
    """Merge summary + introduction into a single coherent TAD description."""
    s = str(summary or "").strip()
    i = str(introduction or "").strip()
    if s and i:
        sl = s.lower()
        il = i.lower()
        if sl in il:
            return i
        if il in sl:
            return s
        return f"{s} {i}"
    return s or i


def _resolve_method_explanation(operation_label: str, structure_title: str) -> str:
    """Build a method explanation shown before each C snippet."""
    key = _normalize_operation_name(operation_label)
    text = _METHOD_EXPLANATIONS.get(key, "").strip()
    if text:
        return text
    return (
        f"Este metodo del TAD {structure_title} debe interpretarse respetando condicionales, ciclos, "
        "returns y actualizacion del estado visual segun el flujo real del codigo C."
    )


def _extract_c_symbol_from_snippet(snippet: str) -> str:
    """Extract the most representative C function symbol from a snippet."""
    text = str(snippet or "")
    if not text.strip():
        return ""

    signature = re.search(
        r"(?:^|\n)\s*(?:static\s+)?[A-Za-z_][\w\s\*]*\b([A-Za-z_]\w*)\s*\([^;]*\)\s*\{",
        text,
    )
    if signature:
        return signature.group(1).strip()

    blacklist = {"if", "for", "while", "switch", "return", "sizeof"}
    for call in re.finditer(r"\b([A-Za-z_]\w*)\s*\(", text):
        symbol = call.group(1).strip()
        if symbol and symbol not in blacklist:
            return symbol
    return ""


def _build_supported_operations_display(
    supported_operations: list[str],
    methods_by_operation: dict[str, dict[str, str | bool]],
) -> list[str]:
    """Return operation labels aligned with C TAD symbols whenever possible."""
    display: list[str] = []
    for operation_label in supported_operations:
        key = _normalize_operation_name(operation_label)
        method = methods_by_operation.get(key, {})
        symbol = str(method.get("c_symbol", "")).strip()
        if symbol:
            display.append(symbol)
            continue
        display.append(operation_label)
    return display


def _enrich_help_with_c_code(help_data: dict, structure_id: str) -> dict:
    """Attach C structure/method snippets to one help payload."""
    enriched = deepcopy(help_data)
    c_data = CCodeService.get_structure_data(structure_id)
    enriched["introduction"] = _resolve_tad_introduction(enriched, structure_id)
    enriched["tad_description"] = _build_tad_description(
        str(enriched.get("summary", "")),
        str(enriched.get("introduction", "")),
    )

    if c_data is None:
        enriched["c_available"] = False
        enriched["c_code_title"] = "Codigo C"
        enriched["c_structure_code"] = "/* No hay estructura C documentada para este TAD en docs/tads_C. */"
        enriched["c_methods"] = []
        return enriched

    operation_map = c_data.get("operations", {})
    supported_operations = enriched.get("supported_operations", [])
    structure_title = str(enriched.get("title", "TAD"))
    c_methods: list[dict[str, str | bool]] = []
    methods_by_operation: dict[str, dict[str, str | bool]] = {}
    covered_keys: set[str] = set()

    for operation_label in supported_operations:
        key = _normalize_operation_name(operation_label)
        covered_keys.add(key)
        snippet = operation_map.get(key, c_data.get("default_operation", ""))
        c_symbol = _extract_c_symbol_from_snippet(snippet)
        c_methods.append(
            {
                "operation": operation_label,
                "explanation": _resolve_method_explanation(operation_label, structure_title),
                "code": snippet,
                "c_symbol": c_symbol,
                "available": key in operation_map,
            }
        )
        methods_by_operation[key] = c_methods[-1]

    for key, snippet in operation_map.items():
        if key in covered_keys:
            continue
        c_symbol = _extract_c_symbol_from_snippet(snippet)
        c_methods.append(
            {
                "operation": key,
                "explanation": _resolve_method_explanation(key, structure_title),
                "code": snippet,
                "c_symbol": c_symbol,
                "available": True,
            }
        )
        methods_by_operation[key] = c_methods[-1]

    enriched["c_available"] = True
    enriched["c_code_title"] = c_data.get("code_title", "Codigo C")
    enriched["c_structure_code"] = c_data.get("record", "/* Estructura C no encontrada. */")
    enriched["c_methods"] = c_methods
    enriched["supported_operations_display"] = _build_supported_operations_display(
        list(supported_operations),
        methods_by_operation,
    )
    return enriched


@help_bp.get("/sequential")
def sequential_help() -> str:
    """Render sequential module help page."""
    module_help = HelpService.get_module_help()
    structures = StructureService.list_structures()
    return render_template("help/sequential.html", module_help=module_help, structures=structures)


@help_bp.get("/sequential/<structure_id>")
def structure_help(structure_id: str) -> str:
    """Render a specific structure help page."""
    data = HelpService.get_structure_help(structure_id)
    data = _enrich_help_with_c_code(data, structure_id)
    return render_template("help/structure.html", help_data=data, structure_id=structure_id)


@help_bp.get("/hierarchical")
def hierarchical_help() -> str:
    """Render hierarchical module help page."""
    module_help = HierarchicalHelpService.get_module_help()
    structures = HierarchicalStructureService.list_structures()
    return render_template("help/hierarchical.html", module_help=module_help, structures=structures)


@help_bp.get("/hierarchical/<structure_id>")
def hierarchical_structure_help(structure_id: str) -> str:
    """Render one hierarchical structure help page."""
    data = HierarchicalHelpService.get_structure_help(structure_id)
    data = _enrich_help_with_c_code(data, structure_id)
    return render_template(
        "help/hierarchical_structure.html",
        help_data=data,
        structure_id=structure_id,
    )


@help_bp.get("/graph")
def graph_help() -> str:
    """Render graph module help page."""
    module_help = GraphHelpService.get_module_help()
    structures = GraphStructureService.list_structures()
    return render_template("help/graph.html", module_help=module_help, structures=structures)


@help_bp.get("/graph/<structure_id>")
def graph_structure_help(structure_id: str) -> str:
    """Render one graph structure help page."""
    data = GraphHelpService.get_structure_help(structure_id)
    data = _enrich_help_with_c_code(data, structure_id)
    return render_template(
        "help/graph_structure.html",
        help_data=data,
        structure_id=structure_id,
    )


@help_bp.get("/hash")
def hash_help() -> str:
    """Render hash module help page."""
    module_help = HashHelpService.get_module_help()
    structures = HashStructureService.list_structures()
    return render_template("help/hash.html", module_help=module_help, structures=structures)


@help_bp.get("/hash/<structure_id>")
def hash_structure_help(structure_id: str) -> str:
    """Render one hash structure help page."""
    data = HashHelpService.get_structure_help(structure_id)
    data = _enrich_help_with_c_code(data, structure_id)
    return render_template(
        "help/hash_structure.html",
        help_data=data,
        structure_id=structure_id,
    )
