"""Didactic help content for sequential structures."""

from __future__ import annotations

from typing import Any


class HelpService:
    """Serve educational texts for the sequential module."""

    _MODULE_HELP = {
        "title": "Ayuda del módulo secuencial",
        "description": (
            "Las estructuras secuenciales organizan elementos en un orden lineal. "
            "En este módulo puedes ejecutar operaciones reales sobre TAD y observar "
            "cómo cambia su estado paso a paso."
        ),
        "tips": [
            "Empieza con operaciones de inserción para poblar la estructura.",
            "Ejecuta consultas (como frente/cima) para verificar el estado sin modificarlo.",
            "Compara el comportamiento FIFO de cola con LIFO de pila.",
        ],
    }

    _STRUCTURE_HELP: dict[str, dict[str, Any]] = {
        "stack": {
            "title": "Pila",
            "summary": "Estructura LIFO: el último en entrar es el primero en salir.",
            "supported_operations": ["apilar", "desapilar", "cima", "limpiar"],
            "pending_operations": [],
        },
        "queue": {
            "title": "Cola",
            "summary": "Estructura FIFO: el primero en entrar es el primero en salir.",
            "supported_operations": ["encolar", "desencolar", "frente", "final", "limpiar"],
            "pending_operations": [],
        },
        "priority_queue": {
            "title": "Cola de Prioridad",
            "summary": "Atiende primero al elemento con menor valor numérico de prioridad.",
            "supported_operations": ["encolar(valor, prioridad)", "desencolar", "frente", "limpiar"],
            "pending_operations": [],
        },
        "linked_list": {
            "title": "Lista Enlazada",
            "summary": "Secuencia de nodos conectados por referencias al siguiente.",
            "supported_operations": [
                "insertar_inicio",
                "insertar_final",
                "insertar_posicion",
                "eliminar_inicio",
                "eliminar_final",
                "eliminar_posicion",
                "eliminar_primero",
                "buscar_posiciones",
                "invertir",
                "primero",
                "ultimo",
                "limpiar",
            ],
            "pending_operations": [],
        },
        "circular_list": {
            "title": "Lista Circular",
            "summary": "La cola apunta de nuevo a la cabeza cerrando el ciclo.",
            "supported_operations": [
                "insertar_inicio",
                "insertar_final",
                "eliminar_inicio",
                "eliminar_primero",
                "buscar_posiciones",
                "invertir",
                "limpiar",
            ],
            "pending_operations": [
                "No existe eliminar_final en el TAD suministrado.",
                "No existe eliminar_posicion en el TAD suministrado.",
            ],
        },
        "sublist": {
            "title": "Sublista",
            "summary": "Lista de padres donde cada padre mantiene su lista de hijos.",
            "supported_operations": [
                "insertar_padre",
                "insertar_hijo",
                "eliminar_padre",
                "eliminar_hijo",
                "hijos_de",
                "limpiar",
            ],
            "pending_operations": [
                "No existe eliminar_todos_los_hijos de un padre en el TAD suministrado.",
            ],
        },
    }

    @staticmethod
    def get_module_help() -> dict[str, Any]:
        """Return the didactic help for the sequential module."""
        return HelpService._MODULE_HELP

    @staticmethod
    def get_structure_help(structure_id: str) -> dict[str, Any]:
        """Return help for a concrete structure id."""
        return HelpService._STRUCTURE_HELP.get(
            structure_id,
            {
                "title": "Estructura no encontrada",
                "summary": "No hay ayuda disponible para esta estructura.",
                "supported_operations": [],
                "pending_operations": [],
            },
        )
