"""Preflight explicit supported teaching C; never supply or execute missing input."""
from __future__ import annotations
import re
from app.domain.sorting import SortingExecutionError
from app.services.c_code_service import CCodeService

_FUNCTIONS = re.compile(r'^\s*(?:static\s+)?[A-Za-z_][\w\s*]*?\b([A-Za-z_]\w*)\s*\([^;]*?\)\s*\{', re.MULTILINE)

class SortingSourceError(SortingExecutionError):
    """Controlled source admission failure; no C execution took place."""


def _without_comments(source: str) -> str:
    return re.sub(r'"(?:\\.|[^"\\])*"|\'(?:\\.|[^\'\\])*\'|/\*[\s\S]*?\*/|//[^\n]*',
                  lambda m: " " + "\n" * m.group().count("\n") if m.group().startswith(("/*", "//")) else m.group(), source)

def _has_preprocessing_directive(source: str) -> bool:
    """Detect directives after C translation phases relevant to their spelling.

    The native teaching snippets contain no directives. This admission policy does
    not evaluate macros or conditional inclusion: preprocessing is outside the
    supported subset, including valid general C programs that require it.
    Trigraph replacement and escaped-newline removal precede comment removal in
    C, so alternate spellings cannot conceal a directive or invent one in a comment.
    """
    trigraphs = {"=": "#", "/": "\\", "'": "^", "(": "[", ")": "]",
                 "!": "|", "<": "{", ">": "}", "-": "~"}
    translated = source.replace("\r\n", "\n").replace("\r", "\n")
    translated = re.sub(r"\?\?([=/'()!<>-])", lambda m: trigraphs[m.group(1)], translated)
    translated = translated.replace("\\\n", "")
    uncommented = _without_comments(translated)
    return re.search(r"^[ \t\v\f]*(?:#|%:)", uncommented, re.MULTILINE) is not None


def _instruction_lines(source: str) -> list[str]:
    """Keep native statement layout required by the existing line localizers."""
    return [line.strip() for line in _without_comments(source).splitlines() if line.strip()]

def validate_sorting_source(algorithm_id: str, source_code: str) -> None:
    """Require mapped native C bodies with their supported instruction layout.

    This checks the supported teaching snippet, not arbitrary C execution. Canonical
    content is used only for comparison; absent input is never filled or defaulted.
    """
    if not isinstance(source_code, str) or not source_code.strip():
        raise SortingSourceError("Codigo C completo requerido para ordenar; no se ejecuto el algoritmo.")
    if _has_preprocessing_directive(source_code):
        raise SortingSourceError("Codigo C con directivas de preprocesamiento fuera del subconjunto soportado; no se ejecuto el algoritmo.")
    data = CCodeService.get_structure_data("sorting_array")
    canonical = data.get("operations", {}).get(algorithm_id, "") if data else ""
    expected = _without_comments(canonical)
    required = list(dict.fromkeys(_FUNCTIONS.findall(expected)))
    if not required or "ordenar_" + algorithm_id not in required:
        raise SortingSourceError("Codigo C canonico no disponible; no se ejecuto el algoritmo.")
    supplied = _without_comments(source_code)
    for name in required:
        actual = CCodeService._extract_function_with_comment(supplied, name)
        approved = CCodeService._extract_function_with_comment(expected, name)
        if not actual or _instruction_lines(actual) != _instruction_lines(approved):
            raise SortingSourceError("Codigo C incompleto o no compatible con el algoritmo y sus auxiliares; no se ejecuto el algoritmo.")
