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

    _PEDAGOGY = {
        "stack": {"objective": "Predecir inserción y extracción LIFO.", "strategy": "Seguir TOP, aux y el enlace siguiente.", "invariant": "TOP es el único extremo; todos los nodos terminan en NULL.", "memory": "Cada apilar reserva; cada desapilar desconecta antes de liberar.", "errors": ["Confundir TOP con el fondo", "Usar aux después de free"]},
        "queue": {"objective": "Explicar FIFO y las transiciones de extremos.", "strategy": "Seguir FRONT para salir y BACK para entrar.", "invariant": "Vacía implica FRONT == BACK == NULL.", "memory": "El nodo saliente se desconecta de FRONT antes de free.", "errors": ["Extraer por BACK", "No anular BACK al retirar el único nodo"]},
        "priority_queue": {"objective": "Separar llegada, prioridad y desempate estable.", "strategy": "Conservar la cadena de llegada y recorrer candidatos.", "invariant": "El primer mínimo de prioridad es seleccionado.", "memory": "Solo el candidato elegido se desconecta y libera.", "errors": ["Dibujar la cadena físicamente ordenada", "Romper el empate por llegada"]},
        "linked_list": {"objective": "Mantener la conectividad al buscar, insertar y eliminar.", "strategy": "Seguir HEAD, anterior y actual.", "invariant": "Cada nodo es alcanzable una vez desde HEAD y el último apunta a NULL.", "memory": "Guardar el enlace siguiente antes de liberar.", "errors": ["Perder HEAD", "Sobrescribir un enlace antes de conservar el resto"]},
        "circular_list": {"objective": "Conservar el cierre y terminar recorridos seguros.", "strategy": "Seguir HEAD/TAIL y detectar la vuelta al inicio.", "invariant": "TAIL->next == HEAD cuando hay nodos.", "memory": "Actualizar el cierre antes de liberar el nodo retirado.", "errors": ["Esperar NULL en un recorrido", "Dejar TAIL apuntando a memoria liberada"]},
        "sublist": {"objective": "Modificar una rama sin afectar a las demás.", "strategy": "Localizar primero el padre y luego recorrer sus hijos.", "invariant": "Cada hijo pertenece a un único padre.", "memory": "La liberación de una rama no autoriza liberar ramas vecinas.", "errors": ["Insertar un hijo sin padre", "Compartir enlaces entre ramas"]},
    }

    GLOSSARY = {
        "Nodo": "Objeto dinámico con datos y uno o más enlaces.", "Enlace": "Campo puntero que conecta objetos.", "Alias": "Dos punteros que designan el mismo objeto.", "LIFO": "El último en entrar es el primero en salir.", "FIFO": "El primero en entrar es el primero en salir.", "Prioridad": "Criterio de selección independiente del orden físico.", "Circularidad": "El último enlace vuelve al inicio.", "malloc": "Reserva memoria; puede devolver NULL.", "free": "Libera una reserva que deja de ser válida.",
    }

    @staticmethod
    def get_module_help() -> dict[str, Any]:
        """Return the didactic help for the sequential module."""
        return HelpService._MODULE_HELP

    @staticmethod
    def get_structure_help(structure_id: str) -> dict[str, Any]:
        """Return help for a concrete structure id."""
        result = dict(HelpService._STRUCTURE_HELP.get(
            structure_id,
            {
                "title": "Estructura no encontrada",
                "summary": "No hay ayuda disponible para esta estructura.",
                "supported_operations": [],
                "pending_operations": [],
            },
        ))
        result.update(HelpService._PEDAGOGY.get(structure_id, {}))
        result["glossary"] = dict(HelpService.GLOSSARY)
        return result
