"""Build and verify the versioned functional-coverage inventory for QA."""

from __future__ import annotations

import ast
import argparse
import json
import re
import sys
from collections.abc import Iterable
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app import create_app
from app.domain.sorting import SORTING_ALGORITHMS
from app.routes.graph_routes import _GRAPH_PHASES
from app.services.graph_structure_service import GraphStructureService
from app.services.hash_structure_service import HashStructureService
from app.services.hierarchical_structure_service import HierarchicalStructureService
from app.services.sorting_structure_service import SortingStructureService
from app.services.structure_service import StructureService


DEFAULT_OUTPUT = ROOT / "docs" / "qa" / "app-coverage-manifest-v1.json"
INTERACTIVE_TAG = re.compile(r"<(button|input|select|textarea|a)\b([^>]*)>", re.IGNORECASE)
ATTRIBUTE = re.compile(r"([\w:-]+)\s*=\s*([\"'])(.*?)\2", re.DOTALL)


def _case_id(category: str, identifier: str) -> str:
    """Return a stable case identifier that can be implemented in later phases."""
    safe = re.sub(r"[^a-z0-9]+", "-", identifier.lower()).strip("-")
    return f"QA-{category.upper()}-{safe.upper()}"


def _item(*, category: str, identifier: str, source: str, module: str, oracle: str, metadata: dict[str, Any] | None = None) -> dict[str, Any]:
    """Create an inventory item with its mandatory coverage assignment."""
    return {
        "id": f"{category}:{identifier}",
        "category": category,
        "module": module,
        "source": source,
        "metadata": metadata or {},
        "coverage": {
            "case_id": _case_id(category, identifier),
            "layer": "e2e" if category == "control" else "api",
            "oracle": oracle,
        },
    }


def _service_items(module: str, service: Any) -> list[dict[str, Any]]:
    """Collect structures and their public adapter operations."""
    items: list[dict[str, Any]] = []
    for structure in service.list_structures():
        structure_id = structure["id"]
        items.append(
            _item(
                category="structure",
                identifier=f"{module}/{structure_id}",
                module=module,
                source=f"{type(service).__name__}.list_structures",
                oracle="La pantalla y el modelo de vista responden para la estructura registrada.",
                metadata=structure,
            )
        )
        adapter = service._new_adapter(structure_id)
        for operation in adapter.get_supported_operations():
            operation_name = str(operation["name"])
            items.append(
                _item(
                    category="operation",
                    identifier=f"{module}/{structure_id}/{operation_name}",
                    module=module,
                    source=f"{type(adapter).__name__}.get_supported_operations",
                    oracle="La API valida entradas y el estado/traza cumple el contrato de la operación.",
                    metadata={"structure_id": structure_id, "operation": operation},
                )
            )
    return items


def _route_items() -> list[dict[str, Any]]:
    """Collect public Flask rules from the application factory."""
    application = create_app()
    items: list[dict[str, Any]] = []
    for rule in sorted(application.url_map.iter_rules(), key=lambda item: item.rule):
        if rule.endpoint == "static":
            continue
        methods = sorted(method for method in rule.methods if method not in {"HEAD", "OPTIONS"})
        identifier = f"{','.join(methods)} {rule.rule}"
        items.append(
            _item(
                category="route",
                identifier=identifier,
                module=rule.endpoint.split(".", 1)[0],
                source=f"Flask:{rule.endpoint}",
                oracle="La ruta responde con el contrato HTTP esperado para datos válidos e inválidos.",
                metadata={"endpoint": rule.endpoint, "methods": methods, "rule": rule.rule},
            )
        )
    return items


def _graph_phase_items() -> list[dict[str, Any]]:
    """Collect graph phases and the algorithms selectable in each phase."""
    items: list[dict[str, Any]] = []
    for phase, data in sorted(_GRAPH_PHASES.items()):
        items.append(
            _item(
                category="phase",
                identifier=f"graph/{phase}",
                module="graph",
                source="app.routes.graph_routes._GRAPH_PHASES",
                oracle="La fase presenta solo operaciones y algoritmos habilitados por su configuración.",
                metadata={"phase": phase, "operations": sorted(data["operations"]), "algorithms": sorted(data["algorithms"])},
            )
        )
        for algorithm in sorted(data["algorithms"]):
            items.append(
                _item(
                    category="algorithm",
                    identifier=f"graph/{phase}/{algorithm}",
                    module="graph",
                    source="app.routes.graph_routes._GRAPH_PHASES",
                    oracle="El algoritmo cumple sus precondiciones, invariante y resultado publicado.",
                    metadata={"phase": phase, "algorithm": algorithm},
                )
            )
    return items


def _sorting_algorithm_items() -> list[dict[str, Any]]:
    """Collect all registered sorting algorithms."""
    return [
        _item(
            category="algorithm",
            identifier=f"sorting/{algorithm['id']}",
            module="sorting",
            source="app.domain.sorting.SORTING_ALGORITHMS",
            oracle="El arreglo final, las métricas y la traza coinciden con el algoritmo C seleccionado.",
            metadata=dict(algorithm),
        )
        for algorithm in SORTING_ALGORITHMS
    ]


def _control_items(*, include_unidentified: bool = False) -> list[dict[str, Any]]:
    """Collect every interactive HTML element with a stable identifier or action."""
    items: list[dict[str, Any]] = []
    for template in sorted((ROOT / "templates").rglob("*.html")):
        relative = template.relative_to(ROOT).as_posix()
        for index, match in enumerate(INTERACTIVE_TAG.finditer(template.read_text(encoding="utf-8")), start=1):
            tag, raw_attributes = match.groups()
            attributes = {name.lower(): value.strip() for name, _, value in ATTRIBUTE.findall(raw_attributes)}
            identifier = attributes.get("data-testid") or attributes.get("data-action") or attributes.get("id") or attributes.get("name")
            synthetic_identifier = not identifier
            if not identifier:
                if not include_unidentified:
                    continue
                identifier = f"anonymous-{index}"
            items.append(
                _item(
                    category="control",
                    identifier=f"{relative}:{tag}:{identifier}:{index}",
                    module=relative.split("/", 2)[1] if "/" in relative else "shared",
                    source=relative,
                    oracle="El control es operable, conserva el foco y produce el cambio de interfaz o API esperado.",
                    metadata={"tag": tag.lower(), "identifier": identifier, "attributes": attributes, **({"synthetic_identifier": True} if synthetic_identifier else {})},
                )
            )
    return items


def collect_inventory(*, include_unidentified_controls: bool = False) -> dict[str, Any]:
    """Return the complete inventory derived from the running application contracts."""
    entries: list[dict[str, Any]] = []
    entries.extend(_route_items())
    for module, service in (
        ("sequential", StructureService),
        ("hierarchical", HierarchicalStructureService),
        ("graph", GraphStructureService),
        ("hash", HashStructureService),
        ("sorting", SortingStructureService),
    ):
        entries.extend(_service_items(module, service))
    entries.extend(_graph_phase_items())
    entries.extend(_sorting_algorithm_items())
    entries.extend(_control_items(include_unidentified=include_unidentified_controls))
    entries.sort(key=lambda entry: entry["id"])
    counts: dict[str, int] = {}
    for entry in entries:
        counts[entry["category"]] = counts.get(entry["category"], 0) + 1
    return {
        "schema_version": 1,
        "generated_by": "scripts/build_app_quality_inventory.py",
        "coverage_policy": "Cada elemento publicado debe tener case_id, capa y oráculo no vacíos.",
        "summary": {"total": len(entries), "by_category": counts},
        "items": entries,
    }


def validate_inventory(inventory: dict[str, Any]) -> list[str]:
    """Return all policy violations found in an inventory."""
    errors: list[str] = []
    seen: set[str] = set()
    for entry in inventory.get("items", []):
        identifier = entry.get("id")
        if not isinstance(identifier, str) or not identifier:
            errors.append("Elemento sin identificador.")
            continue
        if identifier in seen:
            errors.append(f"Identificador duplicado: {identifier}")
        seen.add(identifier)
        coverage = entry.get("coverage")
        if not isinstance(coverage, dict) or not all(isinstance(coverage.get(key), str) and coverage[key].strip() for key in ("case_id", "layer", "oracle")):
            errors.append(f"Cobertura incompleta: {identifier}")
    if not inventory.get("items"):
        errors.append("El inventario no contiene elementos publicados.")
    return errors


def validate_executable_bindings(
    inventory: dict[str, Any], bindings: dict[str, Any], *, project_root: Path = ROOT,
) -> list[str]:
    """Check explicit case assignments; this is not a test execution certificate."""
    errors: list[str] = []
    if not isinstance(bindings, dict):
        return ["Formato de asignaciones ejecutables inválido."]
    assignments = bindings.get("items")
    if bindings.get("schema") != "app-executable-bindings/v1" or not isinstance(assignments, dict):
        return ["Formato de asignaciones ejecutables inválido."]
    root = project_root.resolve()
    for item in inventory.get("items", []):
        identifier = item.get("id")
        case = assignments.get(identifier)
        if not isinstance(case, dict):
            errors.append(f"Sin prueba ejecutable asignada: {identifier}")
            continue
        if not isinstance(case.get("input"), (dict, list)) or "expected" not in case:
            errors.append(f"Caso sin entrada y esperado explícitos: {identifier}")
        layer = case.get("layer")
        if layer not in {"unit", "api", "native", "e2e"} or (item.get("category") == "control" and layer != "e2e"):
            errors.append(f"Capa de prueba inválida: {identifier}")
        reference = case.get("test_node")
        if not isinstance(reference, str) or "::" not in reference:
            errors.append(f"Referencia de prueba inválida: {identifier}")
            continue
        file_name, *names = reference.split("::")
        path = (root / file_name).resolve()
        try:
            path.relative_to(root / "tests")
        except ValueError:
            errors.append(f"Prueba fuera de tests/: {identifier}")
            continue
        if path.suffix != ".py" or not names[-1].startswith("test_"):
            errors.append(f"Referencia de prueba inválida: {identifier}")
            continue
        try:
            nodes = ast.parse(path.read_text(encoding="utf-8-sig")).body
            node = None
            for name in names:
                node = next((candidate for candidate in nodes if isinstance(candidate, (ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)) and candidate.name == name), None)
                if node is None:
                    break
                nodes = node.body
            if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                errors.append(f"Función de prueba inexistente: {identifier}")
        except (OSError, SyntaxError, UnicodeError):
            errors.append(f"Fuente de prueba ausente o inválida: {identifier}")
    return errors


def write_inventory(path: Path = DEFAULT_OUTPUT) -> dict[str, Any]:
    """Generate, validate and write the canonical JSON artifact."""
    inventory = collect_inventory()
    errors = validate_inventory(inventory)
    if errors:
        raise ValueError("\n".join(errors))
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(inventory, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return inventory


def _parse_arguments(arguments: Iterable[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--check", action="store_true", help="Falla si el manifiesto versionado no coincide con el inventario actual.")
    parser.add_argument("--bindings", type=Path, help="Gate estricto: asignaciones explícitas a pruebas con datos/esperado; no acredita ejecución.")
    parser.add_argument("--disposition-overlay", type=Path, help="Disposiciones revisadas sobre IDs originales; requiere --bindings, no acredita ejecución.")
    return parser.parse_args(arguments)


def main(arguments: Iterable[str] | None = None) -> int:
    """Run the generator or freshness verifier."""
    args = _parse_arguments(arguments)
    inventory = collect_inventory(include_unidentified_controls=args.bindings is not None)
    errors = validate_inventory(inventory)
    if args.disposition_overlay is not None and args.bindings is None:
        raise SystemExit("El overlay requiere --bindings.")
    if args.bindings is not None:
        bindings = json.loads(args.bindings.read_text(encoding="utf-8"))
        if args.disposition_overlay is not None:
            from scripts.app_quality_disposition_overlay import apply_disposition_overlay
            overlay = json.loads(args.disposition_overlay.read_text(encoding="utf-8-sig"))
            inventory, bindings, disposition_summary, overlay_errors = apply_disposition_overlay(inventory, bindings, overlay, project_root=ROOT)
            errors.extend(overlay_errors)
            errors.extend(validate_inventory(inventory))
            inventory["disposition_summary"] = disposition_summary
            print(json.dumps(disposition_summary, ensure_ascii=False))
        errors.extend(validate_executable_bindings(inventory, bindings))
    if errors:
        raise SystemExit("\n".join(errors))
    serialized = json.dumps(inventory, ensure_ascii=False, indent=2) + "\n"
    if args.check:
        if not args.output.exists() or args.output.read_text(encoding="utf-8") != serialized:
            raise SystemExit("El manifiesto de cobertura está ausente o desactualizado. Ejecute scripts/build_app_quality_inventory.py.")
        print(f"Manifiesto de cobertura vigente: {args.output}")
        return 0
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(serialized, encoding="utf-8")
    print(f"Manifiesto generado: {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
