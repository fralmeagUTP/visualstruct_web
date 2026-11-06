"""Native regression of the E2E observation point, without a browser claim."""
from __future__ import annotations

import json
from pathlib import Path
import shutil
import subprocess

import pytest

from app.services.hierarchical_structure_service import HierarchicalStructureService
from app.services.structure_service import StructureService
from e2e_contract_helpers import observe_before_cleanup

ROOT = Path(__file__).resolve().parents[1]


@pytest.mark.parametrize("family,stem,operation,payload,cleanup,observation,expected", [
    ("linked_list", "tad_lista", "insertar_inicio", {"value": 8}, "lista_limpiar(&lista);", 'printf("AUDIT:%d\\n", lista ? lista->nro : -1);', "AUDIT:8"),
    ("circular_list", "tad_lista_circular", "insertar_final", {"value": 8}, "lcir_destruir(&lc);", 'int values[1]; int n = lcir_copiar_valores(&lc, values, 1); printf("AUDIT:%d\\n", n ? values[0] : -1);', "AUDIT:8"),
    ("sublist", "tad_sublista", "insertar_padre", {"parent": 8}, "sublista_destruir(&sublista);", 'printf("AUDIT:%d\\n", sublista ? sublista->nro : -1);', "AUDIT:8"),
    ("avl", "tad_avl", "insertar", {"value": 8}, "avl_liberarAVL(arbol);", 'printf("AUDIT:%d\\n", arbol ? arbol->nro : -1);', "AUDIT:8"),
])
def test_actual_generated_main_observed_before_owned_state_is_freed(tmp_path, family, stem, operation, payload, cleanup, observation, expected):
    compiler = shutil.which("gcc")
    assert compiler, "The native observation contract requires GCC"
    service = HierarchicalStructureService if family == "avl" else StructureService
    model = service.get_view_model(family, [])
    result = service._new_adapter(family).execute(operation, payload)
    fixture = [{"id": family, "module": "hierarchical" if family == "avl" else "sequential", "model": model,
                "operations": [{"name": operation, "payload": payload, "message": result["message"]}]}]
    fixture_path = tmp_path / "fixture.json"
    fixture_path.write_text(json.dumps(fixture), encoding="utf-8")
    subprocess.run(["node", str(ROOT / "qa/frontend_main_export.js"), str(ROOT), str(fixture_path), str(tmp_path)], check=True)
    main = (tmp_path / f"{family}.c").read_text(encoding="utf-8")

    def compile_and_run(source: str, label: str) -> str:
        path = tmp_path / f"{label}.c"
        path.write_text(source, encoding="utf-8")
        executable = tmp_path / label
        built = subprocess.run([compiler, "-std=c17", "-Wall", "-Wextra", "-Wpedantic", "-Werror",
                                "-I", str(ROOT / "docs/tads_C"), str(ROOT / f"docs/tads_C/{stem}.c"),
                                str(path), "-o", str(executable)], capture_output=True, text=True, timeout=30)
        assert built.returncode == 0, built.stderr
        ran = subprocess.run([str(executable)], capture_output=True, text=True, timeout=10)
        assert ran.returncode == 0, ran.stderr
        return ran.stdout

    compile_and_run(main, "unaltered")
    # Reproduce why the old observer is wrong: the final return follows cleanup.
    late = main.replace("    return 0;", "    " + observation + "\n    return 0;")
    assert "AUDIT:-1" in compile_and_run(late, "late-observer").splitlines()
    observed = observe_before_cleanup(main, cleanup, observation)
    assert observed.replace("    " + observation + "\n", "") == main
    assert expected in compile_and_run(observed, "before-cleanup").splitlines()
