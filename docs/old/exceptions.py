"""Excepciones comunes para los TAD."""

class TADError(Exception):
    """Error base para los TAD."""


class EstructuraVaciaError(TADError):
    """Se lanza cuando una operación requiere elementos y la estructura está vacía."""


class ElementoDuplicadoError(TADError):
    """Se lanza cuando no se permiten duplicados y el elemento ya existe."""


class ElementoNoEncontradoError(TADError):
    """Se lanza cuando un elemento requerido no existe."""


class PosicionInvalidaError(TADError):
    """Se lanza cuando una posición o índice no es válido."""


class VerticeNoEncontradoError(TADError):
    """Se lanza cuando un vértice no existe en el grafo."""


class AristaNoEncontradaError(TADError):
    """Se lanza cuando una arista no existe en el grafo."""


class PesoNegativoError(TADError):
    """Se lanza cuando un algoritmo no admite pesos negativos."""
