"""Routes for didactic help pages."""

from __future__ import annotations

from copy import deepcopy

from flask import Blueprint, render_template

from app.services.hash_help_service import HashHelpService
from app.services.hash_structure_service import HashStructureService
from app.services.graph_help_service import GraphHelpService
from app.services.graph_structure_service import GraphStructureService
from app.services.hierarchical_help_service import HierarchicalHelpService
from app.services.hierarchical_structure_service import HierarchicalStructureService
from app.services.help_service import HelpService
from app.services.c_code_service import CCodeService
from app.services.structure_service import StructureService

help_bp = Blueprint("help", __name__, url_prefix="/help")


def _normalize_operation_name(operation_label: str) -> str:
    """Normalize operation labels to operation ids used in C-code maps."""
    return str(operation_label).split("(", 1)[0].strip()


def _enrich_help_with_c_code(help_data: dict, structure_id: str) -> dict:
    """Attach C structure/method snippets to one help payload."""
    enriched = deepcopy(help_data)
    c_data = CCodeService.get_structure_data(structure_id)

    if c_data is None:
        enriched["c_available"] = False
        enriched["c_code_title"] = "Codigo C"
        enriched["c_structure_code"] = "/* No hay estructura C documentada para este TAD en docs/tads_C. */"
        enriched["c_methods"] = []
        return enriched

    operation_map = c_data.get("operations", {})
    supported_operations = enriched.get("supported_operations", [])
    c_methods: list[dict[str, str | bool]] = []
    covered_keys: set[str] = set()

    for operation_label in supported_operations:
        key = _normalize_operation_name(operation_label)
        covered_keys.add(key)
        snippet = operation_map.get(key, c_data.get("default_operation", ""))
        c_methods.append(
            {
                "operation": operation_label,
                "code": snippet,
                "available": key in operation_map,
            }
        )

    for key, snippet in operation_map.items():
        if key in covered_keys:
            continue
        c_methods.append(
            {
                "operation": key,
                "code": snippet,
                "available": True,
            }
        )

    enriched["c_available"] = True
    enriched["c_code_title"] = c_data.get("code_title", "Codigo C")
    enriched["c_structure_code"] = c_data.get("record", "/* Estructura C no encontrada. */")
    enriched["c_methods"] = c_methods
    return enriched


@help_bp.get("/sequential")
def sequential_help() -> str:
    """Render sequential module help page."""
    module_help = HelpService.get_module_help()
    structures = StructureService.list_structures()
    return render_template("help/sequential.html", module_help=module_help, structures=structures)


@help_bp.get("/sequential/<structure_id>")
def structure_help(structure_id: str) -> str:
    """Render a specific structure help page."""
    data = HelpService.get_structure_help(structure_id)
    data = _enrich_help_with_c_code(data, structure_id)
    return render_template("help/structure.html", help_data=data, structure_id=structure_id)


@help_bp.get("/hierarchical")
def hierarchical_help() -> str:
    """Render hierarchical module help page."""
    module_help = HierarchicalHelpService.get_module_help()
    structures = HierarchicalStructureService.list_structures()
    return render_template("help/hierarchical.html", module_help=module_help, structures=structures)


@help_bp.get("/hierarchical/<structure_id>")
def hierarchical_structure_help(structure_id: str) -> str:
    """Render one hierarchical structure help page."""
    data = HierarchicalHelpService.get_structure_help(structure_id)
    data = _enrich_help_with_c_code(data, structure_id)
    return render_template(
        "help/hierarchical_structure.html",
        help_data=data,
        structure_id=structure_id,
    )


@help_bp.get("/graph")
def graph_help() -> str:
    """Render graph module help page."""
    module_help = GraphHelpService.get_module_help()
    structures = GraphStructureService.list_structures()
    return render_template("help/graph.html", module_help=module_help, structures=structures)


@help_bp.get("/graph/<structure_id>")
def graph_structure_help(structure_id: str) -> str:
    """Render one graph structure help page."""
    data = GraphHelpService.get_structure_help(structure_id)
    data = _enrich_help_with_c_code(data, structure_id)
    return render_template(
        "help/graph_structure.html",
        help_data=data,
        structure_id=structure_id,
    )


@help_bp.get("/hash")
def hash_help() -> str:
    """Render hash module help page."""
    module_help = HashHelpService.get_module_help()
    structures = HashStructureService.list_structures()
    return render_template("help/hash.html", module_help=module_help, structures=structures)


@help_bp.get("/hash/<structure_id>")
def hash_structure_help(structure_id: str) -> str:
    """Render one hash structure help page."""
    data = HashHelpService.get_structure_help(structure_id)
    data = _enrich_help_with_c_code(data, structure_id)
    return render_template(
        "help/hash_structure.html",
        help_data=data,
        structure_id=structure_id,
    )
