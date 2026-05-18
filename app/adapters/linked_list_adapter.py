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
        if operation_name == "insertar_posicion":
            valor = self._require_int(payload, "value", "valor")
            posicion_ui = self._require_int(payload, "position", "posicion")
            if posicion_ui < 1:
                raise ValueError("La posicion debe iniciar en 1.")
            changed = self._structure.insertar_elemento(posicion_ui, valor, -1)
            if not changed:
                return {"message": "Error...Posicion no encontrada..!"}
            return {"message": f"Se inserto '{valor}' en la posicion {posicion_ui}."}

        op = operation_name
        if op == "lista_insertar_elemento":
            valor = self._require_int(payload, "value", "valor")
            posicion_ui = self._require_int(payload, "position", "posicion")
            if posicion_ui < 1:
                raise ValueError("La posicion debe iniciar en 1.")
            changed = self._structure.insertar_elemento(posicion_ui, valor, 0)
            if not changed:
                return {"message": "Error...Posicion no encontrada..!"}
            return {"message": f"Se inserto '{valor}' en la posicion base {posicion_ui}."}
        if op == "eliminar_primero":
            op = "eliminar_elemento"
        elif op in {"buscar_posiciones", "primero", "ultimo", "invertir"}:
            # Compatibilidad legacy: se mantiene sin mostrar en UI.
            pass

        if op == "insertar_elemento":
            valor = self._require_int(payload, "value", "valor")
            posicion_ui = self._require_int(payload, "position", "posicion")
            desplazamiento = self._parse_relative_insertion(payload)
            changed = self._structure.insertar_elemento(posicion_ui, valor, desplazamiento)
            if not changed:
                return {"message": "Error...Posicion no encontrada..!"}
            lugar = "antes" if desplazamiento < 0 else "despues"
            return {"message": f"Se inserto '{valor}' {lugar} de la posicion {posicion_ui}."}
        if op == "insertar_inicio":
            valor = self._require_int(payload, "value", "valor")
            self._structure.insertar_inicio(valor)
            return {"message": f"Se inserto '{valor}' al inicio."}
        if op == "insertar_final":
            valor = self._require_int(payload, "value", "valor")
            self._structure.insertar_final(valor)
            return {"message": f"Se inserto '{valor}' al final."}
        if op == "eliminar_elemento":
            valor = self._require_int(payload, "value", "valor")
            eliminado = self._structure.eliminar_elemento(valor)
            if eliminado:
                return {"message": f"Se elimino la primera ocurrencia de '{valor}'."}
            return {"message": f"No se encontro '{valor}' para eliminar."}
        if op == "eliminar_repetidos":
            valor = self._require_int(payload, "value", "valor")
            eliminados = self._structure.eliminar_repetidos(valor)
            return {
                "message": f"Se eliminaron {eliminados} ocurrencias de '{valor}'.",
                "result": eliminados,
            }
        if op == "buscar_elemento":
            valor = self._require_int(payload, "value", "valor")
            posiciones = self._structure.buscar_elemento(valor)
            if posiciones:
                return {
                    "message": f"'{valor}' aparece en posiciones {posiciones}.",
                    "result": posiciones,
                }
            return {"message": f"'{valor}' no aparece en la lista.", "result": []}
        if op == "mostrar":
            valores = self._structure.mostrar()
            return {"message": f"Lista actual: {valores}", "result": valores}
        if op == "buscar_posiciones":
            valor = self._require_int(payload, "value", "valor")
            posiciones = [posicion + 1 for posicion in self._structure.buscar_posiciones(valor)]
            if posiciones:
                return {
                    "message": f"'{valor}' aparece en posiciones {posiciones}.",
                    "result": posiciones,
                }
            return {"message": f"'{valor}' no aparece en la lista.", "result": []}
        if op == "eliminar_inicio":
            valor = self._structure.eliminar_inicio()
            return {"message": f"Se elimino '{valor}' desde el inicio.", "result": valor}
        if op == "eliminar_final":
            valor = self._structure.eliminar_final()
            return {"message": f"Se elimino '{valor}' desde el final.", "result": valor}
        if op == "eliminar_posicion":
            posicion_ui = self._require_int(payload, "position", "posicion")
            posicion_tad = self._to_zero_based_position(posicion_ui)
            valor = self._structure.eliminar_posicion(posicion_tad)
            return {
                "message": f"Se elimino '{valor}' en la posicion {posicion_ui}.",
                "result": valor,
            }
        if op == "invertir":
            self._structure.invertir()
            return {"message": "La lista se invirtio correctamente."}
        if op == "primero":
            valor = self._structure.primero()
            return {"message": f"El primer elemento es '{valor}'.", "result": valor}
        if op == "ultimo":
            valor = self._structure.ultimo()
            return {"message": f"El ultimo elemento es '{valor}'.", "result": valor}
        if op == "limpiar":
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
                "name": "lista_insertar_elemento",
                "label": "Lista insertar elemento",
                "mutates": True,
                "inputs": [
                    {"name": "value", "label": "Valor", "type": "number"},
                    {"name": "position", "label": "Posicion", "type": "number", "min": 1},
                ],
            },
            {
                "name": "eliminar_elemento",
                "label": "Eliminar elemento",
                "mutates": True,
                "inputs": [
                    {"name": "value", "label": "Valor", "type": "number"}
                ],
            },
            {
                "name": "eliminar_repetidos",
                "label": "Eliminar repetidos",
                "mutates": True,
                "inputs": [{"name": "value", "label": "Valor", "type": "number"}],
            },
            {
                "name": "buscar_elemento",
                "label": "Buscar elemento",
                "mutates": False,
                "inputs": [{"name": "value", "label": "Valor", "type": "number"}],
            },
            {"name": "mostrar", "label": "Mostrar (legacy)", "mutates": False, "hidden": True, "inputs": []},
            {"name": "limpiar", "label": "Limpiar", "mutates": True, "inputs": []},
            {
                "name": "insertar_posicion",
                "label": "Insertar posicion (legacy)",
                "mutates": True,
                "hidden": True,
                "inputs": [
                    {"name": "value", "label": "Valor", "type": "number"},
                    {"name": "position", "label": "Posicion", "type": "number", "min": 1},
                ],
            },
            {
                "name": "insertar_elemento",
                "label": "Insertar elemento (legacy)",
                "mutates": True,
                "hidden": True,
                "inputs": [
                    {"name": "value", "label": "Valor", "type": "number"},
                    {"name": "position", "label": "Posicion", "type": "number", "min": 1},
                    {
                        "name": "relative",
                        "label": "Modo (-1 antes, 0 despues)",
                        "type": "number",
                        "min": -1,
                    },
                ],
            },
            {
                "name": "eliminar_primero",
                "label": "Eliminar primero (legacy)",
                "mutates": True,
                "hidden": True,
                "inputs": [{"name": "value", "label": "Valor", "type": "number"}],
            },
            {
                "name": "buscar_posiciones",
                "label": "Buscar posiciones (legacy)",
                "mutates": False,
                "hidden": True,
                "inputs": [{"name": "value", "label": "Valor", "type": "number"}],
            },
            {"name": "eliminar_inicio", "label": "Eliminar inicio (legacy)", "mutates": True, "hidden": True, "inputs": []},
            {"name": "eliminar_final", "label": "Eliminar final (legacy)", "mutates": True, "hidden": True, "inputs": []},
            {
                "name": "eliminar_posicion",
                "label": "Eliminar posicion (legacy)",
                "mutates": True,
                "hidden": True,
                "inputs": [
                    {"name": "position", "label": "Posicion", "type": "number", "min": 1}
                ],
            },
            {"name": "invertir", "label": "Invertir (legacy)", "mutates": True, "hidden": True, "inputs": []},
            {"name": "primero", "label": "Primero (legacy)", "mutates": False, "hidden": True, "inputs": []},
            {"name": "ultimo", "label": "Ultimo (legacy)", "mutates": False, "hidden": True, "inputs": []},
        ]

    @staticmethod
    def _to_zero_based_position(position_ui: int) -> int:
        """Convert one-based UI position into zero-based TAD position."""
        if position_ui < 1:
            raise ValueError("La posicion debe iniciar en 1.")
        return position_ui - 1

    @staticmethod
    def _parse_relative_insertion(payload: dict[str, Any]) -> int:
        raw = payload.get("relative", 0)
        if raw is None or str(raw).strip() == "":
            return 0
        value = int(raw)
        if value not in {-1, 0}:
            raise ValueError("El modo de insercion debe ser -1 (antes) o 0 (despues).")
        return value

