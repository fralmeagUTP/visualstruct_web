"""Adapter for the circular list TAD."""

from __future__ import annotations

from typing import Any

from app.adapters.base_adapter import BaseAdapter
from app.domain.sequential import ListaCircular


class CircularListAdapter(BaseAdapter):
    """Adapt `ListaCircular` to the generic adapter contract."""

    def __init__(self) -> None:
        self._structure: ListaCircular[int] | None = None
        self.create()

    def create(self) -> None:
        self._structure = ListaCircular()

    def execute(self, operation_name: str, payload: dict[str, Any]) -> dict[str, Any]:
        if operation_name == "insertar_inicio":
            valor = self._require_int(payload, "value", "valor")
            self._structure.insertar_inicio(valor)
            return {"message": f"Se insertó '{valor}' al inicio."}
        if operation_name == "insertar_final":
            valor = self._require_int(payload, "value", "valor")
            self._structure.insertar_final(valor)
            return {"message": f"Se insertó '{valor}' al final."}
        if operation_name == "eliminar_inicio":
            valor = self._structure.eliminar_inicio()
            return {"message": f"Se eliminó '{valor}' desde el inicio.", "result": valor}
        if operation_name == "eliminar_primero":
            valor = self._require_int(payload, "value", "valor")
            eliminado = self._structure.eliminar_primero(valor)
            if eliminado:
                return {"message": f"Se eliminó la primera ocurrencia de '{valor}'."}
            return {"message": f"No se encontró '{valor}' para eliminar."}
        if operation_name == "buscar_posiciones":
            valor = self._require_int(payload, "value", "valor")
            posiciones = [posicion + 1 for posicion in self._structure.buscar_posiciones(valor)]
            if posiciones:
                return {
                    "message": f"'{valor}' aparece en posiciones {posiciones}.",
                    "result": posiciones,
                }
            return {"message": f"'{valor}' no aparece en la lista circular.", "result": []}
        if operation_name == "invertir":
            self._structure.invertir()
            return {"message": "La lista circular se invirtió correctamente."}
        if operation_name == "limpiar":
            self._structure.limpiar()
            return {"message": "La lista circular se limpió correctamente."}
        raise ValueError(f"Operación no soportada: {operation_name}.")

    def to_visual_state(self) -> dict[str, Any]:
        items = self._structure.a_lista()
        return {
            "kind": "circular",
            "title": "Lista circular",
            "items": [{"value": value} for value in items],
            "size": self._structure.tamano(),
            "empty": self._structure.vacia(),
        }

    def reset(self) -> None:
        self._structure.limpiar()

    def get_supported_operations(self) -> list[dict[str, Any]]:
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
            {"name": "eliminar_inicio", "label": "Eliminar inicio", "mutates": True, "inputs": []},
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
            {"name": "invertir", "label": "Invertir", "mutates": True, "inputs": []},
            {"name": "limpiar", "label": "Limpiar", "mutates": True, "inputs": []},
        ]

