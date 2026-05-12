"""Didactic help content for hierarchical structures."""

from __future__ import annotations

from typing import Any


class HierarchicalHelpService:
    """Serve educational texts for the hierarchical module."""

    _MODULE_HELP = {
        "title": "Ayuda del modulo jerarquico",
        "description": (
            "Las estructuras jerarquicas organizan datos en niveles. "
            "En este modulo puedes ejecutar operaciones reales y verificar "
            "propiedades de orden y balanceo en cada paso."
        ),
        "tips": [
            "Inserta varios valores y compara inorden entre ABB, AVL y Rojo-Negro.",
            "Después de insertar o eliminar, revisa siempre la validación del árbol.",
            "En montículo, compara la forma de arreglo con su forma de árbol.",
        ],
    }

    _STRUCTURE_HELP: dict[str, dict[str, Any]] = {
        "abb": {
            "title": "ABB",
            "summary": "Árbol binario de búsqueda sin duplicados.",
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
            "summary": "Árbol auto-balanceado con factor de balance en [-1, 1].",
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
                "El TAD no expone información textual de rotaciones realizadas.",
            ],
        },
        "red_black": {
            "title": "Rojo-Negro",
            "summary": "Árbol balanceado por coloración rojo/negro.",
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
            "title": "Montículo Binario",
            "summary": "Min-heap con representación interna en arreglo.",
            "supported_operations": [
                "insertar",
                "extraer_raiz",
                "raiz",
                "a_lista",
                "limpiar",
            ],
            "pending_operations": [
                "No existe en el TAD una operación pública para cambiar a max-heap en caliente.",
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
