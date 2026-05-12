"""Didactic help content for hash-table module."""

from __future__ import annotations

from typing import Any


class HashHelpService:
    """Serve educational texts for hash-table module."""

    _MODULE_HELP = {
        "title": "Ayuda del modulo de tablas hash",
        "description": (
            "El modulo de tablas hash permite gestionar pares clave-valor "
            "y observar buckets, colisiones y redimensionamiento automatico."
        ),
        "tips": [
            "Crea la tabla con capacidad positiva antes de insertar.",
            "Observa el factor de carga para anticipar redimensionamientos.",
            "Compara busqueda, contiene y eliminacion en claves existentes/no existentes.",
        ],
    }

    _STRUCTURE_HELP: dict[str, dict[str, Any]] = {
        "hash_table": {
            "title": "Tabla Hash",
            "summary": "Hash con encadenamiento separado y resize cuando el factor de carga supera 0.75.",
            "supported_operations": [
                "create_table",
                "insert",
                "get",
                "contains",
                "remove",
                "keys",
                "values",
                "items",
                "stats",
                "clear",
            ],
            "pending_operations": [
                "El TAD no expone tecnicas alternativas de hashing (lineal/cuadratico/doble hash).",
                "La visualizacion de buckets usa atributos internos del TAD de forma temporal.",
            ],
        }
    }

    @staticmethod
    def get_module_help() -> dict[str, Any]:
        """Return didactic help for hash module."""
        return HashHelpService._MODULE_HELP

    @staticmethod
    def get_structure_help(structure_id: str) -> dict[str, Any]:
        """Return help for one hash structure."""
        return HashHelpService._STRUCTURE_HELP.get(
            structure_id,
            {
                "title": "Estructura no encontrada",
                "summary": "No hay ayuda disponible para esta estructura.",
                "supported_operations": [],
                "pending_operations": [],
            },
        )
