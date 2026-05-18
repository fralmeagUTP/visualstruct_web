"""Didactic pseudocode and TAD-structure definitions for UI panels."""

from __future__ import annotations

import re
from typing import Any


class PseudocodeService:
    """Expose TAD structures and pseudocode by structure and operation."""

    _FIELD_TYPE_HINTS: dict[str, dict[str, str]] = {
        "stack": {"valor": "int"},
        "queue": {"valor": "int"},
        "priority_queue": {"valor": "int"},
        "linked_list": {"valor": "int"},
        "circular_list": {"valor": "int"},
        "sublist": {"valor": "int"},
        "abb": {"valor": "int"},
        "avl": {"valor": "int"},
        "red_black": {"valor": "int"},
        "graph": {"destino": "int"},
        "hash_table": {"clave": "string", "valor": "string"},
    }

    _DATA: dict[str, dict[str, Any]] = {
        "stack": {
            "record": (
                "Registro Nodo\n"
                "  valor\n"
                "  siguiente\n"
                "FinRegistro\n\n"
                "Registro Pila\n"
                "  cima : Nodo\n"
                "  tam  : Entero\n"
                "FinRegistro"
            ),
            "operations": {
                "apilar": "Si valor == vacio: Error\nInsertarInicio(lista, valor)",
                "desapilar": "Si tam == 0: Error\nret = EliminarInicio(lista)\nRetornar ret",
                "cima": "Si tam == 0: Error\nRetornar Primero(lista)",
                "limpiar": "lista = vacia\ntam = 0",
            },
        },
        "queue": {
            "record": (
                "Registro Nodo\n"
                "  valor\n"
                "  siguiente\n"
                "FinRegistro\n\n"
                "Registro Cola\n"
                "  frente : Nodo\n"
                "  final  : Nodo\n"
                "  tam    : Entero\n"
                "FinRegistro"
            ),
            "operations": {
                "encolar": "Si valor == vacio: Error\nInsertarFinal(lista, valor)",
                "desencolar": "Si tam == 0: Error\nret = EliminarInicio(lista)\nRetornar ret",
                "frente": "Si tam == 0: Error\nRetornar Primero(lista)",
                "final": "Si tam == 0: Error\nRetornar Ultimo(lista)",
                "limpiar": "lista = vacia\ntam = 0",
            },
        },
        "priority_queue": {
            "record": (
                "Registro ItemPrioridad\n"
                "  valor\n"
                "  prioridad : Entero\n"
                "FinRegistro\n\n"
                "Registro ColaPrioridad\n"
                "  items : Lista<ItemPrioridad>\n"
                "FinRegistro"
            ),
            "operations": {
                "encolar": (
                    "Validar(valor, prioridad)\n"
                    "InsertarOrdenado(items, por prioridad ascendente)"
                ),
                "desencolar": "Si items vacia: Error\nRetornar ExtraerPrimero(items)",
                "frente": "Si items vacia: Error\nRetornar VerPrimero(items)",
                "limpiar": "items = []",
            },
        },
        "linked_list": {
            "record": (
                "Registro Nodo\n"
                "  valor\n"
                "  siguiente : Nodo\n"
                "FinRegistro\n\n"
                "Registro ListaEnlazada\n"
                "  cabeza : Nodo\n"
                "  cola   : Nodo\n"
                "  tam    : Entero\n"
                "FinRegistro\n\n"
                "Nota UI: posicion inicia en 1."
            ),
            "operations": {
                "insertar_inicio": "Crear nodo\nnodo.siguiente = cabeza\ncabeza = nodo\nActualizar tam",
                "insertar_final": "Crear nodo\ncola.siguiente = nodo\ncola = nodo\nActualizar tam",
                "insertar_elemento": (
                    "Validar posicion >= 1\n"
                    "desplazamiento = AntesDespues()  // -1 antes, 0 despues\n"
                    "Recorrer hasta (posicion + desplazamiento)\n"
                    "Enlazar nuevo nodo"
                ),
                "lista_insertar_elemento": (
                    "Validar posicion >= 1\n"
                    "desplazamiento = lista_insertar_antes_despues()  // interno del TAD\n"
                    "Recorrer hasta (posicion + desplazamiento)\n"
                    "Enlazar nuevo nodo"
                ),
                "buscar_elemento": "Recorrer\nImprimir posiciones (base 1) donde valor coincide",
                "mostrar": "Recorrer\nImprimir indice y valor de cada nodo",
                "eliminar_elemento": "Recorrer\nEliminar primera coincidencia de valor",
                "eliminar_repetidos": "Recorrer\nEliminar todas las coincidencias de valor",
                "insertar_posicion": "Compatibilidad legacy: usar insertar_elemento",
                "eliminar_primero": "Compatibilidad legacy: usar eliminar_elemento",
                "buscar_posiciones": "Compatibilidad legacy: usar buscar_elemento",
                "limpiar": "cabeza = NULO\ncola = NULO\ntam = 0",
            },
        },
        "circular_list": {
            "record": (
                "Registro NodoCircular\n"
                "  valor\n"
                "  siguiente : NodoCircular\n"
                "FinRegistro\n\n"
                "Registro ListaCircular\n"
                "  cabeza : NodoCircular\n"
                "  cola   : NodoCircular\n"
                "  tam    : Entero\n"
                "FinRegistro\n\n"
                "Nota UI: posiciones mostradas en base 1."
            ),
            "operations": {
                "insertar_inicio": "Crear nodo\nnodo.siguiente = cabeza\ncabeza = nodo\ncola.siguiente = cabeza",
                "insertar_final": "Crear nodo\nnodo.siguiente = cabeza\ncola.siguiente = nodo\ncola = nodo",
                "eliminar_inicio": "Si tam == 0: Error\ncabeza = cabeza.siguiente\ncola.siguiente = cabeza",
                "eliminar_primero": "Recorrer ciclo\nEliminar primera coincidencia de valor",
                "buscar_posiciones": "Recorrer una vuelta completa desde cabeza\nGuardar posiciones (base 1)",
                "invertir": "Invertir punteros de cada nodo\nIntercambiar cabeza y cola",
                "limpiar": "cabeza = NULO\ncola = NULO\ntam = 0",
            },
        },
        "sublist": {
            "record": (
                "Registro Padre\n"
                "  valor\n"
                "  hijos : ListaEnlazada\n"
                "FinRegistro\n\n"
                "Registro Sublista\n"
                "  padres : ListaEnlazada<Padre>\n"
                "FinRegistro"
            ),
            "operations": {
                "insertar_padre": "Si padre existe: Error\nAgregar padre al final",
                "insertar_hijo": "Buscar padre\nSi no existe: Error\nAgregar hijo al final de su sublista",
                "eliminar_padre": "Buscar padre\nSi no existe: Error\nEliminar padre y sus hijos",
                "eliminar_hijo": "Buscar padre\nSi no existe: Error\nEliminar primera coincidencia del hijo",
                "hijos_de": "Buscar padre\nRetornar lista de hijos",
                "limpiar": "Eliminar todos los padres y sublistas",
            },
        },
        "abb": {
            "record": (
                "Registro NodoABB\n"
                "  valor\n"
                "  izq : NodoABB\n"
                "  der : NodoABB\n"
                "FinRegistro\n\n"
                "Registro ABB\n"
                "  raiz : NodoABB\n"
                "FinRegistro"
            ),
            "operations": {
                "insertar": "Insertar como BST segun comparacion",
                "eliminar": "Eliminar nodo (0,1,2 hijos)\nSi 2 hijos: usar sucesor inorden",
                "buscar": "Recorrer desde raiz\nizq si menor, der si mayor",
                "minimo": "Bajar por izquierda hasta NULO",
                "maximo": "Bajar por derecha hasta NULO",
                "altura": "Altura = 1 + max(altura izq, altura der)",
                "contar_hojas": "Contar nodos sin hijos",
                "inorden": "Izq, Nodo, Der",
                "preorden": "Nodo, Izq, Der",
                "postorden": "Izq, Der, Nodo",
                "validar": "Verificar propiedad BST en todo nodo",
                "limpiar": "raiz = NULO",
            },
        },
        "avl": {
            "record": (
                "Registro NodoAVL\n"
                "  valor\n"
                "  izq : NodoAVL\n"
                "  der : NodoAVL\n"
                "  altura : Entero\n"
                "FinRegistro\n\n"
                "Registro AVL\n"
                "  raiz : NodoAVL\n"
                "FinRegistro"
            ),
            "operations": {
                "insertar": "Insertar como BST\nRecalcular FE\nSi FE fuera de [-1,1], rotar (LL,RR,LR,RL)",
                "eliminar": "Eliminar como BST\nRecalcular FE\nRotar si hay desbalance",
                "buscar": "Recorrido BST",
                "minimo": "Bajar por izquierda",
                "maximo": "Bajar por derecha",
                "altura": "Retornar altura de raiz",
                "inorden": "Izq, Nodo, Der",
                "validar": "Todo nodo debe tener FE en {-1,0,1}",
                "limpiar": "raiz = NULO",
            },
        },
        "red_black": {
            "record": (
                "Registro NodoRN\n"
                "  valor\n"
                "  color : {ROJO, NEGRO}\n"
                "  izq, der, padre : NodoRN\n"
                "FinRegistro\n\n"
                "Registro ArbolRN\n"
                "  raiz : NodoRN\n"
                "FinRegistro"
            ),
            "operations": {
                "insertar": "Insertar como BST (rojo)\nReparar propiedades RN\nAsegurar raiz negra",
                "eliminar": "Eliminar nodo BST\nReparar propiedades RN post eliminacion",
                "buscar": "Recorrido BST",
                "inorden": "Izq, Nodo, Der",
                "altura": "Calcular altura del arbol",
                "validar": "Validar propiedades rojo-negro",
                "limpiar": "raiz = NULO",
            },
        },
        "binary_heap": {
            "record": (
                "Registro MonticuloBinario\n"
                "  arreglo : Lista\n"
                "  tam : Entero\n"
                "FinRegistro"
            ),
            "operations": {
                "insertar": "Agregar al final\nAplicar sift-up",
                "extraer_raiz": "Tomar raiz\nSubir ultimo a raiz\nAplicar sift-down",
                "raiz": "Retornar arreglo[0]",
                "a_lista": "Retornar copia del arreglo",
                "limpiar": "arreglo = []",
            },
        },
        "graph": {
            "record": (
                "Registro Arista\n"
                "  destino\n"
                "  peso : Real\n"
                "FinRegistro\n\n"
                "Registro Grafo\n"
                "  dirigido : Logico\n"
                "  ady : Diccionario<Vertice, Lista<Arista>>\n"
                "FinRegistro"
            ),
            "operations": {
                "create_graph": "ady = {}\ndirigido = valor elegido",
                "insert_vertex": "Si no existe vertice, crearlo",
                "remove_vertex": "Eliminar vertice y todas sus aristas incidentes",
                "insert_edge": "Agregar arista u->v (y v->u si no dirigido)",
                "remove_edge": "Eliminar arista u->v (y v->u si no dirigido)",
                "exists_vertex": "Retornar vertice en ady",
                "exists_edge": "Retornar si existe arista entre origen y destino",
                "neighbors": "Retornar vecinos del vertice",
                "edge_weight": "Retornar peso de la arista",
                "list_vertices": "Retornar lista de vertices",
                "list_edges": "Retornar lista de aristas",
                "run_bfs": "Usar cola\nVisitar por niveles desde inicio",
                "run_dfs": "Usar pila/recursion\nVisitar en profundidad desde inicio",
                "run_dijkstra": (
                    "Validar sin pesos negativos\n"
                    "Distancias = infinito\n"
                    "Relajar con cola de prioridad"
                ),
                "run_bellman_ford": "Relajar todas las aristas |V|-1 veces\nDetectar ciclo negativo",
                "run_prim": "Si dirigido: Error\nConstruir MST desde vertice inicial",
                "run_kruskal": "Si dirigido: Error\nOrdenar aristas\nUnion-Find para evitar ciclos",
                "clear_graph": "Vaciar vertices y aristas",
            },
        },
        "hash_table": {
            "record": (
                "Registro ParClaveValor\n"
                "  clave\n"
                "  valor\n"
                "FinRegistro\n\n"
                "Registro TablaHash\n"
                "  buckets : Arreglo de Lista<ParClaveValor>\n"
                "  capacidad : Entero\n"
                "  size : Entero\n"
                "FinRegistro"
            ),
            "operations": {
                "create_table": "Validar capacidad > 0\nInicializar buckets vacios",
                "insert": "i = hash(clave) mod capacidad\nActualizar o insertar\nRehash si supera umbral",
                "get": "Buscar clave en bucket i",
                "contains": "Retornar si clave existe",
                "remove": "Eliminar clave si existe",
                "keys": "Recorrer buckets y extraer claves",
                "values": "Recorrer buckets y extraer valores",
                "items": "Recorrer buckets y extraer pares",
                "stats": "Retornar size, capacidad, factor y colisiones",
                "clear": "Vaciar buckets y reset size",
            },
        },
    }

    _SIGNATURES: dict[str, str] = {
        "apilar": "Apilar(valor)",
        "desapilar": "Desapilar()",
        "cima": "Cima()",
        "limpiar": "Limpiar()",
        "encolar": "Encolar(valor)",
        "desencolar": "Desencolar()",
        "frente": "Frente()",
        "final": "Final()",
        "insertar_inicio": "InsertarInicio(valor)",
        "insertar_final": "InsertarFinal(valor)",
        "insertar_elemento": "InsertarElemento(valor, posicion, relativo)",
        "lista_insertar_elemento": "ListaInsertarElemento(valor, posicion)",
        "buscar_elemento": "BuscarElemento(valor)",
        "mostrar": "Mostrar()",
        "eliminar_elemento": "EliminarElemento(valor)",
        "eliminar_repetidos": "EliminarRepetidos(valor)",
        "insertar_posicion": "InsertarPosicion(valor, posicionUI)",
        "eliminar_inicio": "EliminarInicio()",
        "eliminar_final": "EliminarFinal()",
        "eliminar_posicion": "EliminarPosicion(posicionUI)",
        "eliminar_primero": "EliminarPrimero(valor)",
        "buscar_posiciones": "BuscarPosiciones(valor)",
        "invertir": "Invertir()",
        "primero": "Primero()",
        "ultimo": "Ultimo()",
        "insertar_padre": "InsertarPadre(parent)",
        "insertar_hijo": "InsertarHijo(parent, child)",
        "eliminar_padre": "EliminarPadre(parent)",
        "hijos_de": "HijosDe(parent)",
        "insertar": "Insertar(valor)",
        "eliminar": "Eliminar(valor)",
        "buscar": "Buscar(valor)",
        "minimo": "Minimo()",
        "maximo": "Maximo()",
        "altura": "Altura()",
        "contar_hojas": "ContarHojas()",
        "inorden": "Inorden()",
        "preorden": "Preorden()",
        "postorden": "Postorden()",
        "validar": "Validar()",
        "extraer_raiz": "ExtraerRaiz()",
        "raiz": "Raiz()",
        "a_lista": "ALista()",
        "create_graph": "CrearGrafo(esDirigido)",
        "insert_vertex": "InsertarVertice(v)",
        "remove_vertex": "EliminarVertice(v)",
        "insert_edge": "InsertarArista(u, v, w)",
        "remove_edge": "EliminarArista(u, v)",
        "exists_vertex": "ExisteVertice(v)",
        "exists_edge": "ExisteArista(u, v)",
        "neighbors": "Vecinos(v)",
        "edge_weight": "PesoArista(u, v)",
        "list_vertices": "ListarVertices()",
        "list_edges": "ListarAristas()",
        "run_bfs": "BFS(inicio)",
        "run_dfs": "DFS(inicio)",
        "run_dijkstra": "Dijkstra(inicio, destino)",
        "run_bellman_ford": "BellmanFord(inicio, destino)",
        "run_prim": "Prim(inicio)",
        "run_kruskal": "Kruskal()",
        "clear_graph": "LimpiarGrafo()",
        "create_table": "CrearTabla(capacidad)",
        "insert": "Insertar(clave, valor)",
        "get": "Buscar(clave)",
        "contains": "Contiene(clave)",
        "remove": "Eliminar(clave)",
        "keys": "Keys()",
        "values": "Values()",
        "items": "Items()",
        "stats": "Stats()",
        "clear": "LimpiarTabla()",
    }

    _PHRASE_TO_CALL: dict[str, str] = {
        "Actualizar o insertar": "Llamar InsertarOActualizarPar(clave, valor)",
        "Actualizar tam": "Llamar ActualizarTamano()",
        "Agregar al final": "Llamar AgregarAlFinal(arreglo, valor)",
        "Agregar arista u->v (y v->u si no dirigido)": "Llamar AgregarAristaSegunTipo(u, v, w)",
        "Agregar hijo al final de su sublista": "Llamar AgregarHijoFinal(padre, child)",
        "Agregar padre al final": "Llamar AgregarPadreFinal(parent)",
        "Aplicar sift-down": "Llamar SiftDown(arreglo, 0)",
        "Aplicar sift-up": "Llamar SiftUp(arreglo, UltimoIndice(arreglo))",
        "Asegurar raiz negra": "Llamar AsegurarRaizNegra()",
        "Bajar por derecha": "Llamar DescenderDerechaHastaUltimo()",
        "Bajar por derecha hasta NULO": "Llamar DescenderDerechaHastaNulo()",
        "Bajar por izquierda": "Llamar DescenderIzquierdaHastaUltimo()",
        "Bajar por izquierda hasta NULO": "Llamar DescenderIzquierdaHastaNulo()",
        "Buscar clave en bucket i": "Llamar BuscarEnBucket(i, clave)",
        "Buscar padre": "Llamar BuscarPadre(parent)",
        "Buscar penultimo": "Llamar BuscarPenultimoNodo()",
        "Calcular altura del arbol": "Llamar CalcularAltura(raiz)",
        "Construir MST desde vertice inicial": "Llamar ConstruirMSTPrim(inicio)",
        "Contar nodos sin hijos": "Llamar ContarHojas(raiz)",
        "Crear nodo": "Llamar CrearNodo(valor)",
        "Detectar ciclo negativo": "Llamar DetectarCicloNegativo()",
        "Eliminar arista u->v (y v->u si no dirigido)": "Llamar EliminarAristaSegunTipo(u, v)",
        "Eliminar clave si existe": "Llamar EliminarClaveSiExiste(clave)",
        "Eliminar como BST": "Llamar EliminarBST(valor)",
        "Eliminar nodo (0,1,2 hijos)": "Llamar EliminarNodoSegunCaso(valor)",
        "Eliminar nodo BST": "Llamar EliminarNodoBST(valor)",
        "Eliminar nodo en pos": "Llamar EliminarNodoEnIndice(pos)",
        "Eliminar padre y sus hijos": "Llamar EliminarPadreYHijos(parent)",
        "Eliminar primera coincidencia de valor": "Llamar EliminarPrimeraCoincidencia(valor)",
        "Eliminar todos los padres y sublistas": "Llamar LimpiarPadresYSublistas()",
        "Eliminar vertice y todas sus aristas incidentes": "Llamar EliminarVerticeYAristas(v)",
        "Guardar posiciones (base 1) donde valor coincide": "Llamar RecolectarPosicionesBase1(valor)",
        "Inicializar buckets vacios": "Llamar InicializarBuckets(capacidad)",
        "Insertar como BST": "Llamar InsertarBST(valor)",
        "Insertar como BST (rojo)": "Llamar InsertarBSTRojo(valor)",
        "Insertar como BST segun comparacion": "Llamar InsertarBST(valor)",
        "Insertar en indice pos": "Llamar InsertarEnIndice(pos, valor)",
        "InsertarFinal(lista, valor)": "Llamar InsertarFinal(lista, valor)",
        "InsertarInicio(lista, valor)": "Llamar InsertarInicio(lista, valor)",
        "InsertarOrdenado(items, por prioridad ascendente)": "Llamar InsertarOrdenadoPorPrioridad(items, valor, prioridad)",
        "Invertir punteros uno a uno": "Llamar InvertirPunteros()",
        "Izq, Der, Nodo": "Llamar RecorridoPostorden(raiz)",
        "Izq, Nodo, Der": "Llamar RecorridoInorden(raiz)",
        "Nodo, Izq, Der": "Llamar RecorridoPreorden(raiz)",
        "Ordenar aristas": "Llamar OrdenarAristasPorPeso()",
        "Recalcular FE": "Llamar RecalcularFactorEquilibrio()",
        "Recorrer": "Llamar RecorrerEstructura()",
        "Recorrer buckets y extraer claves": "Llamar ExtraerClavesDeBuckets()",
        "Recorrer buckets y extraer pares": "Llamar ExtraerParesDeBuckets()",
        "Recorrer buckets y extraer valores": "Llamar ExtraerValoresDeBuckets()",
        "Recorrer desde raiz": "Llamar BuscarDesdeRaiz(valor)",
        "Recorrer una vuelta completa desde cabeza": "Llamar RecorrerCicloCompletoDesdeCabeza()",
        "Recorrido BST": "Llamar BuscarDesdeRaiz(valor)",
        "Rehash si supera umbral": "Llamar RehashSiSuperaUmbral()",
        "Relajar con cola de prioridad": "Llamar RelajarConColaPrioridad()",
        "Relajar todas las aristas |V|-1 veces": "Llamar RelajarAristasBellmanFord()",
        "Reparar propiedades RN": "Llamar RepararPropiedadesRojoNegro()",
        "Reparar propiedades RN post eliminacion": "Llamar RepararRNPostEliminacion()",
        "Rotar si hay desbalance": "Llamar RotarSiHayDesbalanceAVL()",
        "Subir ultimo a raiz": "Llamar SubirUltimoElementoARaiz()",
        "Todo nodo debe tener FE en {-1,0,1}": "Llamar ValidarFactorEquilibrioEnRango()",
        "Tomar raiz": "Llamar TomarRaizActual()",
        "Union-Find para evitar ciclos": "Llamar AplicarUnionFindParaEvitarCiclos()",
        "Usar cola": "Llamar EjecutarConCola()",
        "Usar pila/recursion": "Llamar EjecutarConPilaORecursion()",
        "Vaciar buckets y reset size": "Llamar LimpiarBucketsYResetearSize()",
        "Vaciar vertices y aristas": "Llamar LimpiarVerticesYAristas()",
        "Validar capacidad > 0": "Llamar ValidarCapacidadPositiva(capacidad)",
        "Validar propiedades rojo-negro": "Llamar ValidarRojoNegro()",
        "Validar rango": "Llamar ValidarRangoDeIndice()",
        "Validar sin pesos negativos": "Llamar ValidarSinPesosNegativos()",
        "Validar(valor, prioridad)": "Llamar ValidarValorYPrioridad(valor, prioridad)",
        "Verificar propiedad BST en todo nodo": "Llamar ValidarPropiedadBST()",
        "Visitar en profundidad desde inicio": "Llamar EjecutarDFS(inicio)",
        "Visitar por niveles desde inicio": "Llamar EjecutarBFS(inicio)",
        "izq si menor, der si mayor": "Llamar ElegirSubarbolSegunComparacion(valor)",
    }

    @staticmethod
    def _normalize_type_name(type_name: str, field_name: str = "") -> str:
        """Normalize type names to a simpler C-like educational style."""
        raw = type_name.strip()
        if not raw:
            if field_name in {"izq", "der", "padre", "cabeza", "cola", "frente", "final", "cima", "raiz", "siguiente"}:
                return "Nodo*"
            return "Dato"

        lowered = raw.lower()
        if lowered == "entero":
            return "int"
        if lowered == "real":
            return "float"
        if lowered == "logico":
            return "bool"
        if lowered in {"texto", "cadena"}:
            return "string"

        if raw.startswith("Lista<"):
            return "Lista"
        if raw.startswith("Diccionario<"):
            return "Diccionario"
        if raw.startswith("Arreglo"):
            return "Arreglo"
        if raw.startswith("{") and raw.endswith("}"):
            return "enum"
        if raw.startswith("Nodo"):
            return f"{raw}*"

        if field_name in {"izq", "der", "padre", "cabeza", "cola", "frente", "final", "cima", "raiz", "siguiente"}:
            return f"{raw}*"
        return raw

    @classmethod
    def _format_record_field(cls, line: str, structure_id: str) -> str:
        """Convert one field line from `campo : Tipo` to `Tipo campo;`."""
        stripped = line.strip()
        if not stripped:
            return ""

        if ":" in stripped:
            left, right = stripped.split(":", maxsplit=1)
            fields = [item.strip() for item in left.split(",") if item.strip()]
            field_type = cls._normalize_type_name(right)
            if not fields:
                return f"{field_type};"
            return "\n".join(f"{field_type} {field};" for field in fields)

        hint_type = cls._FIELD_TYPE_HINTS.get(structure_id, {}).get(stripped, "")
        inferred_type = hint_type if hint_type else cls._normalize_type_name("", stripped)
        return f"{inferred_type} {stripped};"

    @classmethod
    def _format_record(cls, raw: str, structure_id: str) -> str:
        """Format TAD structure text with consistent indentation."""
        lines = raw.splitlines()
        formatted: list[str] = []
        inside_record = False
        for line in lines:
            stripped = line.strip()
            if not stripped:
                formatted.append("")
                continue
            if stripped.startswith("Registro "):
                formatted.append(stripped)
                formatted.append("{")
                inside_record = True
            elif stripped == "FinRegistro":
                if inside_record:
                    formatted.append("}")
                formatted.append(stripped)
                inside_record = False
            elif stripped.startswith("Nota "):
                formatted.append(stripped)
            else:
                field_block = cls._format_record_field(stripped, structure_id)
                for field_line in field_block.splitlines():
                    formatted.append(f"    {field_line}")
        return "\n".join(formatted)

    @classmethod
    def _normalize_operation_lines(cls, raw: str) -> list[str]:
        """Normalize shorthand operation lines into clearer pseudocode lines."""
        lines: list[str] = []
        for line in raw.splitlines():
            stripped = line.strip()
            if not stripped:
                continue
            if stripped == "Si no existe vertice, crearlo":
                lines.append("Si No ExisteVertice(v) Entonces")
                lines.append("    Llamar CrearVertice(v)")
                lines.append("FinSi")
                continue
            if stripped.startswith("Si ") and ": Error" in stripped:
                condition = stripped[3:].split(": Error", maxsplit=1)[0].strip()
                lines.append(f"Si {condition} Entonces")
                lines.append('    Error("Operacion no valida para el estado actual.")')
                lines.append("FinSi")
                continue
            mapped = cls._PHRASE_TO_CALL.get(stripped)
            if mapped is not None:
                lines.append(mapped)
                continue
            if cls._should_autocall(stripped):
                lines.append(f"Llamar {cls._to_subroutine_name(stripped)}()")
                continue
            lines.append(stripped)
        return lines

    @staticmethod
    def _should_autocall(line: str) -> bool:
        """Return whether a line should be transformed into `Llamar ...()`."""
        control_tokens = (
            "Si ", "FinSi", "Mientras ", "FinMientras", "Para ", "FinPara",
            "Retornar", "Error(", "Llamar ", "SubProceso", "FinSubProceso", "SiNo", "Sino",
        )
        if line.startswith(control_tokens):
            return False
        if "=" in line:
            return False
        return True

    @staticmethod
    def _to_c_like_lines(lines: list[str]) -> list[str]:
        """Convert normalized pseudocode lines into a C-like didactic style."""
        out: list[str] = []
        indent = 0
        for raw in lines:
            line = raw.strip()
            if not line:
                continue

            if line == "FinSi":
                indent = max(0, indent - 1)
                out.append(("    " * indent) + "}")
                continue

            if line in {"SiNo", "Sino"}:
                indent = max(0, indent - 1)
                out.append(("    " * indent) + "} else {")
                indent += 1
                continue

            if line.startswith("Si ") and line.endswith(" Entonces"):
                condition = line[3:-9].strip()
                out.append(("    " * indent) + f"if ({condition}) {{")
                indent += 1
                continue

            if line.startswith("Llamar "):
                call_expr = line[len("Llamar "):].strip()
                out.append(("    " * indent) + f"{call_expr};")
                continue

            if line.startswith("Retornar"):
                expr = line[len("Retornar"):].strip()
                if expr:
                    out.append(("    " * indent) + f"return {expr};")
                else:
                    out.append(("    " * indent) + "return;")
                continue

            if line.startswith("Error("):
                out.append(("    " * indent) + f"{line};")
                continue

            if "=" in line:
                out.append(("    " * indent) + f"{line};")
                continue

            out.append(("    " * indent) + f"{line};")
        return out

    @staticmethod
    def _to_subroutine_name(text: str) -> str:
        """Convert free text into a PascalCase subroutine-like name."""
        normalized = re.sub(r"[^0-9A-Za-záéíóúÁÉÍÓÚñÑ ]+", " ", text)
        words = [w for w in normalized.split() if w]
        if not words:
            return "Subrutina"
        cleaned: list[str] = []
        for word in words:
            base = word.lower()
            base = (
                base.replace("á", "a")
                .replace("é", "e")
                .replace("í", "i")
                .replace("ó", "o")
                .replace("ú", "u")
                .replace("ñ", "n")
            )
            cleaned.append(base.capitalize())
        return "".join(cleaned)

    @classmethod
    def _format_operation(cls, operation_name: str, raw: str) -> str:
        """Wrap one operation as a well-indented SubProceso block."""
        signature = cls._SIGNATURES.get(
            operation_name,
            operation_name.replace("_", " ").title() + "()",
        )
        body_lines = cls._normalize_operation_lines(raw)
        if not body_lines:
            body_lines = ["Escribir \"Sin detalle disponible.\""]

        block: list[str] = [f"SubProceso {signature}"]
        for line in cls._to_c_like_lines(body_lines):
            block.append(line)
        block.append("FinSubProceso")
        return "\n".join(block)

    @classmethod
    def get_structure_data(cls, structure_id: str) -> dict[str, Any]:
        """Return didactic data for one structure."""
        data = cls._DATA.get(structure_id)
        if data is None:
            return {
                "record": "Estructura no documentada.",
                "operations": {},
                "default_operation": "Seudocodigo no disponible para esta operacion.",
            }
        raw_operations: dict[str, str] = data.get("operations", {})
        formatted_operations = {
            name: cls._format_operation(name, raw_text)
            for name, raw_text in raw_operations.items()
        }
        return {
            "record": cls._format_record(data.get("record", "Estructura no documentada."), structure_id),
            "operations": formatted_operations,
            "default_operation": "Seudocodigo no disponible para esta operacion.",
        }
