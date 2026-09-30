"""Didactic help content for sorting module."""

from __future__ import annotations

from typing import Any

from app.domain.sorting import SORTING_ALGORITHMS
from app.domain.sorting.pedagogy import SORTING_LEARNING_CATALOG, SORTING_THEORY_CATALOG


class SortingHelpService:
    """Serve educational texts for sorting."""

    _MODULE_HELP = {
        "title": "Ayuda del modulo de metodos de ordenamiento",
        "description": (
            "Este modulo interpreta algoritmos de ordenamiento del TAD en C sobre arreglos de enteros. "
            "Puedes ejecutar en modo rapido (resultado final) o paso a paso (traza didactica completa)."
        ),
        "tips": [
            "Primero crea un arreglo manual o genera uno aleatorio.",
            "Luego selecciona el algoritmo y usa Reproducir.",
            "Con 'Interpretar codigo paso a paso' activado, usa Anterior/Siguiente para validar comparaciones y movimientos.",
            "Con la opcion desactivada, Reproducir aplica directamente el estado final.",
            "El resultado final debe ser identico entre modo rapido y ultimo paso interpretado.",
        ],
    }

    _ALGO_SUMMARY: dict[str, str] = {
        "intercambio": "Compara cada par (i, j) y permuta cuando encuentra desorden.",
        "seleccion": "Busca el minimo del tramo no ordenado y lo coloca en la posicion actual.",
        "insercion": "Inserta cada elemento en su lugar desplazando mayores hacia la derecha.",
        "burbuja": "Compara adyacentes y burbujea los mayores hacia el final en cada pasada.",
        "shell": "Generaliza insercion usando saltos (gaps) decrecientes hasta 1.",
        "quicksort": "Particiona por pivote y ordena recursivamente subarreglos.",
        "mergesort": "Divide recursivamente y fusiona subarreglos ordenados usando auxiliar.",
        "heapsort": "Construye max-heap y extrae repetidamente la raiz al final del arreglo.",
        "counting_sort": "Cuenta ocurrencias por rango de valores y reconstruye el arreglo.",
        "binsort": "En este TAD delega en counting sort.",
        "radixsort": "Ordena por digitos (LSD) y maneja negativos separando grupos.",
    }

    @staticmethod
    def get_module_help() -> dict[str, Any]:
        """Return module-level help."""
        return SortingHelpService._MODULE_HELP

    @staticmethod
    def get_structure_help(structure_id: str) -> dict[str, Any]:
        """Return help for sorting structure."""
        if structure_id != "sorting_array":
            return {
                "title": "Estructura no encontrada",
                "summary": "No hay ayuda disponible para esta estructura.",
                "supported_operations": [],
                "pending_operations": [],
            }

        ops = [item["id"] for item in SORTING_ALGORITHMS]
        ops.extend(["imprimir_arreglo", "copiar_arreglo", "probar_algoritmo_void", "probar_algoritmo_int"])
        pending = [
            "El SDD lista como candidatos burbuja/seleccion/insercion/shell/merge/quick/heap.",
            "El TAD real tambien incluye intercambio, counting sort, binsort y radixsort.",
        ]
        return {
            "title": "Metodos de Ordenamiento",
            "summary": (
                "Arreglo lineal de enteros ordenado mediante metodos clasicos del TAD C. "
                "La simulacion resalta comparaciones, intercambios/movimientos, pivote, rangos y auxiliares."
            ),
            "supported_operations": ops,
            "supported_algorithms": [
                {
                    "id": item["id"], "label": item["label"], "summary": SortingHelpService._ALGO_SUMMARY.get(item["id"], ""),
                    "objective": SORTING_LEARNING_CATALOG[item["id"]]["objective"],
                    "mastery": SORTING_LEARNING_CATALOG[item["id"]]["mastery"],
                    "theory": SORTING_THEORY_CATALOG[item["id"]],
                    "common_error": "Confundir el estado parcial con el resultado final o ignorar los límites del rango activo.",
                }
                for item in SORTING_ALGORITHMS
            ],
            "pending_operations": pending,
        }
