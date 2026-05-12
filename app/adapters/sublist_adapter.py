"""Adapter for the sublist TAD."""

from __future__ import annotations

from typing import Any

from app.adapters.base_adapter import BaseAdapter
from app.domain.sequential import Sublista


class SublistAdapter(BaseAdapter):
    """Adapt `Sublista` to the generic adapter contract."""

    def __init__(self) -> None:
        self._structure: Sublista[int] | None = None
        self.create()

    def create(self) -> None:
        self._structure = Sublista()

    def execute(self, operation_name: str, payload: dict[str, Any]) -> dict[str, Any]:
        if operation_name == "insertar_padre":
            valor = self._require_int(payload, "parent", "padre")
            self._structure.insertar_padre(valor)
            return {"message": f"Se insertÃ³ el padre '{valor}'."}
        if operation_name == "insertar_hijo":
            padre = self._require_int(payload, "parent", "padre")
            hijo = self._require_int(payload, "child", "hijo")
            self._structure.insertar_hijo(padre, hijo)
            return {"message": f"Se insertÃ³ el hijo '{hijo}' para el padre '{padre}'."}
        if operation_name == "eliminar_padre":
            padre = self._require_int(payload, "parent", "padre")
            eliminado = self._structure.eliminar_padre(padre)
            if eliminado:
                return {"message": f"Se eliminÃ³ el padre '{padre}' con su sublista."}
            return {"message": f"No se encontrÃ³ el padre '{padre}' para eliminar."}
        if operation_name == "eliminar_hijo":
            padre = self._require_int(payload, "parent", "padre")
            hijo = self._require_int(payload, "child", "hijo")
            eliminado = self._structure.eliminar_hijo(padre, hijo)
            if eliminado:
                return {"message": f"Se eliminÃ³ el hijo '{hijo}' del padre '{padre}'."}
            return {"message": f"No se encontrÃ³ el hijo '{hijo}' para el padre '{padre}'."}
        if operation_name == "hijos_de":
            padre = self._require_int(payload, "parent", "padre")
            hijos = self._structure.hijos_de(padre)
            return {"message": f"Hijos de '{padre}': {hijos}.", "result": hijos}
        if operation_name == "limpiar":
            self._structure.limpiar()
            return {"message": "La estructura sublista se limpiÃ³ correctamente."}
        raise ValueError(f"OperaciÃ³n no soportada: {operation_name}.")

    def to_visual_state(self) -> dict[str, Any]:
        data = self._structure.a_diccionario()
        items = [{"parent": parent, "children": children} for parent, children in data.items()]
        return {
            "kind": "sublist",
            "title": "Sublista (padres e hijos)",
            "items": items,
            "size": len(items),
            "empty": len(items) == 0,
        }

    def reset(self) -> None:
        self._structure.limpiar()

    def get_supported_operations(self) -> list[dict[str, Any]]:
        return [
            {
                "name": "insertar_padre",
                "label": "Insertar padre",
                "mutates": True,
                "inputs": [{"name": "parent", "label": "Padre", "type": "number"}],
            },
            {
                "name": "insertar_hijo",
                "label": "Insertar hijo",
                "mutates": True,
                "inputs": [
                    {"name": "parent", "label": "Padre", "type": "number"},
                    {"name": "child", "label": "Hijo", "type": "number"},
                ],
            },
            {
                "name": "eliminar_padre",
                "label": "Eliminar padre",
                "mutates": True,
                "inputs": [{"name": "parent", "label": "Padre", "type": "number"}],
            },
            {
                "name": "eliminar_hijo",
                "label": "Eliminar hijo",
                "mutates": True,
                "inputs": [
                    {"name": "parent", "label": "Padre", "type": "number"},
                    {"name": "child", "label": "Hijo", "type": "number"},
                ],
            },
            {
                "name": "hijos_de",
                "label": "Listar hijos",
                "mutates": False,
                "inputs": [{"name": "parent", "label": "Padre", "type": "number"}],
            },
            {"name": "limpiar", "label": "Limpiar", "mutates": True, "inputs": []},
        ]

