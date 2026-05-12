"""Adapter for the linked list TAD."""

from __future__ import annotations

from typing import Any

from app.adapters.base_adapter import BaseAdapter
from app.domain.sequential import ListaEnlazada


class LinkedListAdapter(BaseAdapter):
    """Adapt `ListaEnlazada` to the generic adapter contract."""

    def __init__(self) -> None:
        self._structure: ListaEnlazada[int] | None = None
        self.create()

    def create(self) -> None:
        """Create an empty linked list instance."""
        self._structure = ListaEnlazada()

    def execute(self, operation_name: str, payload: dict[str, Any]) -> dict[str, Any]:
        """Execute one linked-list operation and return a didactic message."""
        if operation_name == "insertar_inicio":
            valor = self._require_int(payload, "value", "valor")
            self._structure.insertar_inicio(valor)
            return {"message": f"Se inserto '{valor}' al inicio."}
        if operation_name == "insertar_final":
            valor = self._require_int(payload, "value", "valor")
            self._structure.insertar_final(valor)
            return {"message": f"Se inserto '{valor}' al final."}
        if operation_name == "insertar_posicion":
            valor = self._require_int(payload, "value", "valor")
            posicion_ui = self._require_int(payload, "position", "posicion")
            posicion_tad = self._to_zero_based_position(posicion_ui)
            self._structure.insertar_posicion(posicion_tad, valor)
            return {"message": f"Se inserto '{valor}' en la posicion {posicion_ui}."}
        if operation_name == "eliminar_inicio":
            valor = self._structure.eliminar_inicio()
            return {"message": f"Se elimino '{valor}' desde el inicio.", "result": valor}
        if operation_name == "eliminar_final":
            valor = self._structure.eliminar_final()
            return {"message": f"Se elimino '{valor}' desde el final.", "result": valor}
        if operation_name == "eliminar_posicion":
            posicion_ui = self._require_int(payload, "position", "posicion")
            posicion_tad = self._to_zero_based_position(posicion_ui)
            valor = self._structure.eliminar_posicion(posicion_tad)
            return {
                "message": f"Se elimino '{valor}' en la posicion {posicion_ui}.",
                "result": valor,
            }
        if operation_name == "eliminar_primero":
            valor = self._require_int(payload, "value", "valor")
            eliminado = self._structure.eliminar_primero(valor)
            if eliminado:
                return {"message": f"Se elimino la primera ocurrencia de '{valor}'."}
            return {"message": f"No se encontro '{valor}' para eliminar."}
        if operation_name == "buscar_posiciones":
            valor = self._require_int(payload, "value", "valor")
            posiciones = [posicion + 1 for posicion in self._structure.buscar_posiciones(valor)]
            if posiciones:
                return {
                    "message": f"'{valor}' aparece en posiciones {posiciones}.",
                    "result": posiciones,
                }
            return {"message": f"'{valor}' no aparece en la lista.", "result": []}
        if operation_name == "invertir":
            self._structure.invertir()
            return {"message": "La lista se invirtio correctamente."}
        if operation_name == "primero":
            valor = self._structure.primero()
            return {"message": f"El primer elemento es '{valor}'.", "result": valor}
        if operation_name == "ultimo":
            valor = self._structure.ultimo()
            return {"message": f"El ultimo elemento es '{valor}'.", "result": valor}
        if operation_name == "limpiar":
            self._structure.limpiar()
            return {"message": "La lista enlazada se limpio correctamente."}
        raise ValueError(f"Operacion no soportada: {operation_name}.")

    def to_visual_state(self) -> dict[str, Any]:
        """Serialize linked-list state for frontend rendering."""
        items = self._structure.a_lista()
        return {
            "kind": "linear",
            "title": "Lista enlazada",
            "items": [{"value": value} for value in items],
            "size": self._structure.tamano(),
            "empty": self._structure.vacia(),
        }

    def reset(self) -> None:
        """Reset the linked list."""
        self._structure.limpiar()

    def get_supported_operations(self) -> list[dict[str, Any]]:
        """Return available linked-list operations and input metadata."""
        return [
            {
                "name": "insertar_inicio",
                "label": "Insertar inicio",
                "mutates": True,
                "inputs": [{"name": "value", "label": "Valor", "type": "number"}],
            },
            {
                "name": "insertar_final",
                "label": "Insertar final",
                "mutates": True,
                "inputs": [{"name": "value", "label": "Valor", "type": "number"}],
            },
            {
                "name": "insertar_posicion",
                "label": "Insertar posicion",
                "mutates": True,
                "inputs": [
                    {"name": "value", "label": "Valor", "type": "number"},
                    {"name": "position", "label": "Posicion", "type": "number", "min": 1},
                ],
            },
            {"name": "eliminar_inicio", "label": "Eliminar inicio", "mutates": True, "inputs": []},
            {"name": "eliminar_final", "label": "Eliminar final", "mutates": True, "inputs": []},
            {
                "name": "eliminar_posicion",
                "label": "Eliminar posicion",
                "mutates": True,
                "inputs": [
                    {"name": "position", "label": "Posicion", "type": "number", "min": 1}
                ],
            },
            {
                "name": "eliminar_primero",
                "label": "Eliminar primero por valor",
                "mutates": True,
                "inputs": [{"name": "value", "label": "Valor", "type": "number"}],
            },
            {
                "name": "buscar_posiciones",
                "label": "Buscar posiciones",
                "mutates": False,
                "inputs": [{"name": "value", "label": "Valor", "type": "number"}],
            },
            {"name": "limpiar", "label": "Limpiar", "mutates": True, "inputs": []},
        ]

    @staticmethod
    def _to_zero_based_position(position_ui: int) -> int:
        """Convert one-based UI position into zero-based TAD position."""
        if position_ui < 1:
            raise ValueError("La posicion debe iniciar en 1.")
        return position_ui - 1

