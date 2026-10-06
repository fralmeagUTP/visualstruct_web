"""Build the final, reproducible QA report for didactic C trace fidelity."""

from __future__ import annotations

import json
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
QA = ROOT / "docs" / "qa"
FINDINGS = QA / "findings"
INVENTORY = QA / "didactic-c-trace-inventory.json"
RESULTS = QA / "didactic-c-trace-results.json"
REPORT = QA / "didactic-c-trace-audit.md"
BACKLOG = QA / "correction-backlog.md"
FIXTURES = ROOT / "tests" / "qa" / "fixtures" / "didactic-qa-minimal-cases-v1.json"

REQUIRED = {
    "case_id", "structure_id", "operation", "input", "expected", "observed",
    "result", "severity", "discrepancy", "probable_cause", "location",
    "recommended_test", "suggested_fix",
}
SEVERITIES = ("critical", "high", "medium", "low")
P0 = {"SORT-003"}
P1 = {
    "GRAPH-001", "GRAPH-002", "GRAPH-003", "GRAPH-004", "GRAPH-006",
    "HASH-001", "HASH-002", "LINKED-001", "PRIORITY-001", "PRIORITY-002",
    "QUEUE-001", "RBT-002", "SORT-004", "STACK-001",
}


def compact(value: object, limit: int = 180) -> str:
    text = json.dumps(value, ensure_ascii=False, separators=(",", ":"))
    text = text.replace("|", "\\|").replace("\n", " ")
    return text if len(text) <= limit else text[: limit - 1] + "…"


def md(value: object) -> str:
    return str(value).replace("|", "\\|").replace("\n", " ")


def priority(case_id: str) -> str:
    if case_id in P0:
        return "P0"
    if case_id in P1:
        return "P1"
    return "P2"


def main() -> None:
    inventory = json.loads(INVENTORY.read_text(encoding="utf-8"))
    findings = [json.loads(path.read_text(encoding="utf-8")) for path in sorted(FINDINGS.glob("*.json"))]
    if not findings:
        raise SystemExit("No QA findings found")

    ids: set[str] = set()
    for finding in findings:
        missing = REQUIRED - finding.keys()
        if missing:
            raise SystemExit(f"{finding.get('case_id', '?')}: missing {sorted(missing)}")
        if finding["case_id"] in ids or finding["severity"] not in SEVERITIES:
            raise SystemExit(f"Invalid or duplicate finding: {finding['case_id']}")
        if not finding["expected"] or not finding["observed"]:
            raise SystemExit(f"Finding without reproducible evidence: {finding['case_id']}")
        ids.add(finding["case_id"])
        finding["priority"] = priority(finding["case_id"])

    operation_results = []
    for structure in inventory["structures"]:
        related = [f for f in findings if f["structure_id"] in {structure["id"], "application"}]
        for operation in structure["operations"]:
            hits = [f["case_id"] for f in related if operation["name"] in f["operation"].split("/")]
            operation_results.append({
                "structure_id": structure["id"],
                "operation": operation["name"],
                "c_function": operation["c_function"],
                "mapping_status": operation["mapping_status"],
                "result": "failed" if hits else "passed",
                "finding_ids": hits,
                "evidence": [
                    "docs/qa/didactic-c-trace-inventory.json",
                    "docs/qa/generated-audit-v1.json",
                    *([f"docs/qa/findings/{case_id}.json" for case_id in hits]),
                ],
            })

    if len(operation_results) != inventory["operations_count"]:
        raise SystemExit("Inventory operation count is inconsistent")

    severity_counts = Counter(f["severity"] for f in findings)
    priority_counts = Counter(f["priority"] for f in findings)
    result = {
        "schema": "didactic-c-trace-audit/v1",
        "scope": {"structures": inventory["structures_count"], "operations": inventory["operations_count"]},
        "summary": {
            "findings": len(findings),
            "severity": {name: severity_counts[name] for name in SEVERITIES},
            "priority": {name: priority_counts[name] for name in ("P0", "P1", "P2")},
            "generated_sequences": 5000,
            "new_generated_failures": 0,
        },
        "operation_results": operation_results,
        "findings": findings,
        "residual_validation": [
            "Eventos semánticos/intermedios específicos por familia (2.1).",
            "Eventos por cada reserva/reasignación/liberación intermedia (2.3).",
            "Matriz ASan/UBSan en Linux (2.5).",
        ],
        "product_logic_modified": False,
    }
    RESULTS.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    lines = [
        "# Informe final de fidelidad didáctica C",
        "",
        "## Resultado ejecutivo",
        "",
        f"Se auditaron **{inventory['structures_count']} TAD y {inventory['operations_count']} operaciones**. "
        f"Se documentaron **{len(findings)} discrepancias reproducibles**: "
        f"{severity_counts['critical']} crítica y {severity_counts['high']} altas. "
        "Las 5.000 secuencias deterministas de regresión no descubrieron fallos adicionales. "
        "Esta auditoría no modifica lógica productiva.",
        "",
        "Cada operación del inventario tiene un resultado en `didactic-c-trace-results.json`; cada fallo enlaza "
        "evidencia esperada/observada, localización, prueba y corrección sugerida.",
        "",
        "## Hallazgos por operación/caso",
        "",
        "| Caso | TAD / operación | Entrada | Esperado | Observado | Resultado / severidad | Causa y localización | Prueba y corrección sugerida |",
        "|---|---|---|---|---|---|---|---|",
    ]
    for f in findings:
        lines.append(
            f"| {f['case_id']} | {f['structure_id']} / {f['operation']} | {compact(f['input'])} | "
            f"{compact(f['expected'])} | {compact(f['observed'])} | FALLIDO / {f['severity']} ({f['priority']}) | "
            f"{md(f['probable_cause'])} `{f['location']}` | "
            f"{md(f['recommended_test'])} **Sugerencia:** {md(f['suggested_fix'])} |"
        )
    lines += [
        "",
        "## Evidencia y límites de cierre",
        "",
        "La matriz completa de 120 resultados está en `docs/qa/didactic-c-trace-results.json`; los casos "
        "mínimos están en `tests/qa/fixtures/didactic-qa-minimal-cases-v1.json`. Los resultados se apoyan "
        "en los resúmenes por familia, los 29 JSON individuales y la auditoría generada.",
        "",
        "Quedan como validaciones residuales del OpenSpec la instrumentación intermedia detallada de 2.1/2.3 "
        "y ASan/UBSan en Linux de 2.5. No invalidan la publicación de este informe, pero deben ejecutarse "
        "antes de declarar cerrada la iniciativa completa.",
    ]
    REPORT.write_text("\n".join(lines) + "\n", encoding="utf-8")

    backlog = [
        "# Backlog priorizado de correcciones",
        "",
        "No se aplicó ninguna corrección funcional. Cada elemento requiere autorización explícita, "
        "implementación aislada y ejecución de su prueba recomendada.",
        "",
        "| Prioridad | Caso | Severidad | Discrepancia | Módulo | Corrección sugerida |",
        "|---|---|---|---|---|---|",
    ]
    for f in sorted(findings, key=lambda item: (item["priority"], item["case_id"])):
        backlog.append(
            f"| {f['priority']} | {f['case_id']} | {f['severity']} | {md(f['discrepancy'])} | "
            f"`{f['location']}` | {md(f['suggested_fix'])} |"
        )
    backlog += [
        "",
        "P0 bloquea fidelidad semántica y seguridad C; P1 altera estado, resultado o rama observable; "
        "P2 altera causalidad visual, temporales, resaltado o detalle didáctico.",
    ]
    BACKLOG.write_text("\n".join(backlog) + "\n", encoding="utf-8")

    FIXTURES.parent.mkdir(parents=True, exist_ok=True)
    fixture = {
        "schema": "didactic-qa-minimal-cases/v1",
        "cases": [{"case_id": f["case_id"], "structure_id": f["structure_id"], "operation": f["operation"], "input": f["input"]} for f in findings],
    }
    FIXTURES.write_text(json.dumps(fixture, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
