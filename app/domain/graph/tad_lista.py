"""Alias del TAD de lista enlazada para el modulo de grafos.

Este modulo expone el contrato `tad_lista.py` nuevo dentro del namespace
`app.domain.graph` para mantener coherencia entre modulos.
"""

from __future__ import annotations

from app.domain.sequential.tad_lista import NodoLista, Tlista, lista_buscar_posiciones, lista_configurar_insertar_antes_despues_provider, lista_eliminar_elemento, lista_eliminar_repetidos, lista_insertar_elemento, lista_insertar_final, lista_insertar_inicio

__all__ = [
    "NodoLista",
    "Tlista",
    "lista_buscar_posiciones",
    "lista_configurar_insertar_antes_despues_provider",
    "lista_eliminar_elemento",
    "lista_eliminar_repetidos",
    "lista_insertar_elemento",
    "lista_insertar_final",
    "lista_insertar_inicio",
]
