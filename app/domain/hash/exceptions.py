"""Common exceptions for Hash module TAD."""


class TADError(Exception):
    """Base error for TAD operations."""


class EstructuraVaciaError(TADError):
    """Raised when an operation requires elements but structure is empty."""


class ElementoDuplicadoError(TADError):
    """Raised when duplicates are not allowed and element already exists."""


class ElementoNoEncontradoError(TADError):
    """Raised when a required element does not exist."""


class PosicionInvalidaError(TADError):
    """Raised when a position or index is invalid."""
