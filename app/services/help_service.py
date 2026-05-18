"""Didactic help content for sequential structures."""

from __future__ import annotations

from typing import Any


class HelpService:
    """Serve educational texts for the sequential module."""

    _MODULE_HELP = {
        "title": "Ayuda del modulo secuencial",
        "description": (
            "Este modulo permite estudiar estructuras lineales (pila, cola, listas) "
            "como un interprete de codigo C: cada operacion se ejecuta por pasos y su "
            "efecto se refleja de inmediato en la animacion del estado."
        ),
        "tips": [
            "Flujo sugerido: selecciona operacion, completa entradas y usa Reproducir para ver la secuencia completa.",
            "Usa Siguiente/Anterior paso para verificar punteros auxiliares, reasignaciones y returns tempranos.",
            "Contrasta LIFO (pila) vs FIFO (cola) y valida que HEAD/TOPE/FRONT/BACK queden consistentes.",
        ],
    }

    _STRUCTURE_HELP: dict[str, dict[str, Any]] = {
        "stack": {
            "title": "Pila",
            "summary": (
                "Estructura LIFO (Last In, First Out): el ultimo nodo en entrar queda en el TOPE "
                "y es el primero en salir. En la simulacion observa como se crea el nodo auxiliar, "
                "se enlaza al tope actual y luego se reasigna el puntero principal de la pila."
            ),
            "supported_operations": ["apilar", "desapilar", "limpiar"],
            "pending_operations": [],
        },
        "queue": {
            "title": "Cola",
            "summary": (
                "Estructura FIFO (First In, First Out): el primer nodo en entrar queda al frente y "
                "sale primero. En la animacion revisa las reasignaciones de frente/atras y verifica "
                "que al quedar vacia ambos extremos vuelvan al estado nulo."
            ),
            "supported_operations": ["encolar", "desencolar", "limpiar"],
            "pending_operations": [],
        },
        "priority_queue": {
            "title": "Cola de Prioridad",
            "summary": (
                "Estructura FIFO por nivel de prioridad: se atiende primero el elemento con menor "
                "valor numerico de prioridad y, en empate, se conserva el orden de llegada. "
                "La simulacion muestra inserciones ordenadas y el impacto de cada comparacion."
            ),
            "supported_operations": ["encolar(valor, prioridad)", "desencolar", "frente", "limpiar"],
            "pending_operations": [],
        },
        "linked_list": {
            "title": "Lista Enlazada",
            "summary": (
                "Secuencia lineal de nodos enlazados por referencias al siguiente. En el simulador "
                "debes seguir el avance de punteros auxiliares para inserciones/eliminaciones por "
                "posicion, verificando que el HEAD siempre conserve la conectividad de la lista."
            ),
            "supported_operations": [
                "insertar_inicio",
                "insertar_final",
                "lista_insertar_elemento",
                "buscar_elemento",
                "mostrar",
                "eliminar_elemento",
                "eliminar_repetidos",
                "limpiar",
            ],
            "pending_operations": [
                "lista_insertar_elemento usa modo relativo: -1 (antes) o 0 (despues).",
            ],
        },
        "circular_list": {
            "title": "Lista Circular",
            "summary": (
                "Lista enlazada circular donde el ultimo nodo apunta nuevamente al primero. "
                "La interpretacion paso a paso debe evidenciar el cierre del ciclo en cada alta/baja "
                "de nodos para evitar rupturas o ciclos invalidos."
            ),
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
            "summary": (
                "Estructura jerarquica secuencial: cada nodo padre mantiene su propia sublista de hijos. "
                "En la animacion observa dos niveles de punteros (padres e hijos) y valida que cada "
                "operacion afecte solo la rama correspondiente sin corromper otras sublistas."
            ),
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
