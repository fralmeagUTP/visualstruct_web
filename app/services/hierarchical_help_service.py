"""Didactic help content for hierarchical structures."""

from __future__ import annotations

from typing import Any


class HierarchicalHelpService:
    """Serve educational texts for the hierarchical module."""

    _MODULE_HELP = {
        "title": "Ayuda del modulo jerarquico",
        "description": (
            "Este modulo permite estudiar arboles como interprete visual de codigo C: "
            "la simulacion muestra comparaciones, inserciones/eliminaciones y ajustes "
            "de balance en el mismo orden en que se ejecutan las subrutinas."
        ),
        "tips": [
            "Ejecuta primero Reproducir para entender el flujo global y luego depura con Siguiente/Anterior paso.",
            "En ABB/AVL revisa la ruta de comparaciones; en AVL/Rojo-Negro verifica el momento exacto del rebalanceo.",
            "Despues de cada mutacion confirma validacion, recorridos y coherencia del arbol final.",
        ],
    }

    _STRUCTURE_HELP: dict[str, dict[str, Any]] = {
        "abb": {
            "title": "ABB",
            "summary": (
                "Arbol binario de busqueda sin duplicados: todo valor menor va al subarbol izquierdo "
                "y todo valor mayor al derecho. En la simulacion revisa la ruta de comparaciones y "
                "confirma que la propiedad de orden se preserve despues de cada insercion o eliminacion."
            ),
            "supported_operations": [
                "insertar",
                "eliminar",
                "buscar",
                "minimo",
                "maximo",
                "altura",
                "contar_hojas",
                "inorden",
                "preorden",
                "postorden",
                "validar",
                "limpiar",
            ],
            "pending_operations": [],
        },
        "avl": {
            "title": "AVL",
            "summary": (
                "Arbol AVL auto-balanceado: mantiene factor de equilibrio por nodo en el rango [-1, 1]. "
                "La animacion debe mostrar deteccion del nodo desbalanceado y aplicacion de rotaciones "
                "(LL, RR, LR, RL) sincronizadas con la linea C que se interpreta."
            ),
            "supported_operations": [
                "insertar",
                "eliminar",
                "buscar",
                "minimo",
                "maximo",
                "altura",
                "inorden",
                "validar",
                "limpiar",
            ],
            "pending_operations": [
                "El TAD no expone informacion textual de rotaciones realizadas.",
            ],
        },
        "red_black": {
            "title": "Rojo-Negro",
            "summary": (
                "Arbol balanceado por reglas de color (rojo/negro) que limitan la altura. "
                "Durante la simulacion observa recoloreos y rotaciones para mantener raiz negra, "
                "sin rojos consecutivos y con altura negra consistente entre caminos."
            ),
            "supported_operations": [
                "insertar",
                "eliminar",
                "buscar",
                "inorden",
                "altura",
                "validar",
                "limpiar",
            ],
            "pending_operations": [
                "El TAD no expone el detalle paso a paso de recoloreos/rotaciones.",
            ],
        },
        "binary_heap": {
            "title": "Monticulo Binario",
            "summary": (
                "Min-heap representado en arreglo y visualizado tambien como arbol casi completo. "
                "En cada operacion identifica los intercambios ascendentes/descendentes que restauran "
                "la propiedad: todo padre debe ser menor o igual que sus hijos."
            ),
            "supported_operations": [
                "insertar",
                "extraer_raiz",
                "raiz",
                "a_lista",
                "limpiar",
            ],
            "pending_operations": [
                "No existe en el TAD una operacion publica para cambiar a max-heap en caliente.",
            ],
        },
    }

    @staticmethod
    def get_module_help() -> dict[str, Any]:
        """Return the didactic help for hierarchical module."""
        return HierarchicalHelpService._MODULE_HELP

    @staticmethod
    def get_structure_help(structure_id: str) -> dict[str, Any]:
        """Return help for one hierarchical structure."""
        return HierarchicalHelpService._STRUCTURE_HELP.get(
            structure_id,
            {
                "title": "Estructura no encontrada",
                "summary": "No hay ayuda disponible para esta estructura.",
                "supported_operations": [],
                "pending_operations": [],
            },
        )
