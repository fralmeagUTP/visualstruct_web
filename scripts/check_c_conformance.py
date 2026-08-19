"""Compile and execute every C conformance harness with strict flags."""

from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import tempfile
from dataclasses import dataclass
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
HARNESS_DIR = ROOT / "tests" / "conformance" / "c_harnesses"
TAD_DIR = ROOT / "docs" / "tads_C"


@dataclass(frozen=True)
class HarnessCheck:
    tad_sources: tuple[str, ...]
    arguments: tuple[str, ...]


CHECKS: dict[str, HarnessCheck] = {
    "linked_list": HarnessCheck(("tad_lista.c",), ("append", "2", "prepend", "1")),
    "stack": HarnessCheck(("tad_pila.c",), ("push", "1", "push", "2", "pop")),
    "queue": HarnessCheck(("tad_cola.c",), ("enqueue", "1", "enqueue", "2", "dequeue")),
    "priority_queue": HarnessCheck(("tad_cola_prioridad.c",), ("enqueue", "1", "2", "enqueue", "2", "1", "dequeue")),
    "circular_list": HarnessCheck(("tad_lista_circular.c",), ("append", "1", "append", "2", "reverse")),
    "sublist": HarnessCheck(("tad_sublista.c",), ("add_parent", "1", "add_child", "1", "2")),
    "abb": HarnessCheck(("tad_abb.c",), ("insert", "2", "insert", "1", "insert", "3")),
    "avl": HarnessCheck(("tad_avl.c",), ("insert", "30", "insert", "20", "insert", "10")),
    "red_black": HarnessCheck(("tad_rojo_negro.c",), ("insert", "10", "insert", "20", "insert", "30")),
    "binary_heap": HarnessCheck(("tad_monticulo_binario.c",), ("insert", "3", "insert", "1", "extract")),
    "graph": HarnessCheck(("tad_grafo.c", "tad_cola.c"), ("add_vertex", "1", "add_vertex", "2", "add_edge", "1", "2", "5")),
    "hash_table": HarnessCheck(("tad_tabla_hash.c",), ("put", "1", "10", "put", "2", "20")),
    "sorting": HarnessCheck(("tad_ordenamiento.c",), ("quick", "3", "1", "2")),
}


def _canonical_output(stdout: str) -> dict[str, object]:
    for line in reversed(stdout.splitlines()):
        if line.strip().startswith("{"):
            return json.loads(line)
    raise RuntimeError("el harness no emitió JSON canónico")


def run_checks(
    *, compiler: str, sanitizers: bool, only: set[str] | None = None
) -> None:
    manifest = json.loads((HARNESS_DIR / "manifest.json").read_text(encoding="utf-8"))
    registered = manifest["structures"]
    if set(registered) != set(CHECKS) or any(not value for value in registered.values()):
        raise RuntimeError("manifiesto y matriz de verificación no cubren los mismos 13 TAD")

    with tempfile.TemporaryDirectory(prefix="visualestruct-c17-") as directory:
        output_dir = Path(directory)
        selected = sorted(only or CHECKS)
        unknown = set(selected) - set(CHECKS)
        if unknown:
            raise RuntimeError(f"TAD no registrado: {', '.join(sorted(unknown))}")
        for structure_id in selected:
            check = CHECKS[structure_id]
            executable = output_dir / structure_id
            flags = ["-std=c17", "-Wall", "-Wextra", "-Wpedantic", "-Werror"]
            if sanitizers:
                flags.extend(["-fsanitize=address,undefined", "-fno-omit-frame-pointer", "-g"])
            command = [
                compiler,
                *flags,
                "-I", str(TAD_DIR),
                "-I", str(HARNESS_DIR),
                str(HARNESS_DIR / registered[structure_id]),
                *(str(TAD_DIR / source) for source in check.tad_sources),
                "-o", str(executable),
            ]
            try:
                compiled = subprocess.run(
                    command, capture_output=True, text=True, check=False, timeout=60
                )
            except subprocess.TimeoutExpired as error:
                raise RuntimeError(
                    f"{structure_id}: compilación excedió 60 segundos"
                ) from error
            if compiled.returncode != 0:
                raise RuntimeError(f"{structure_id}: compilación fallida\n{compiled.stderr}")
            environment = os.environ.copy()
            if sanitizers:
                environment.update({"ASAN_OPTIONS": "detect_leaks=0:halt_on_error=1", "UBSAN_OPTIONS": "halt_on_error=1:print_stacktrace=1"})
            stdout_path = output_dir / f"{structure_id}.stdout"
            stderr_path = output_dir / f"{structure_id}.stderr"
            try:
                with stdout_path.open("w", encoding="utf-8") as stdout_file, stderr_path.open(
                    "w", encoding="utf-8"
                ) as stderr_file:
                    executed = subprocess.run(
                        [str(executable), *check.arguments],
                        stdout=stdout_file,
                        stderr=stderr_file,
                        text=True,
                        check=False,
                        env=environment,
                        timeout=30,
                    )
            except subprocess.TimeoutExpired as error:
                raise RuntimeError(
                    f"{structure_id}: ejecución excedió 30 segundos"
                ) from error
            executed_stdout = stdout_path.read_text(encoding="utf-8")
            executed_stderr = stderr_path.read_text(encoding="utf-8")
            if executed.returncode != 0:
                raise RuntimeError(f"{structure_id}: ejecución fallida\n{executed_stderr}")
            state = _canonical_output(executed_stdout)
            if state.get("structure_id") != structure_id:
                raise RuntimeError(f"{structure_id}: identificador canónico incorrecto")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--compiler", default=shutil.which("gcc") or "gcc")
    parser.add_argument("--sanitizers", action="store_true")
    parser.add_argument("--list", action="store_true")
    parser.add_argument("--only", action="append", choices=sorted(CHECKS))
    args = parser.parse_args()
    if args.list:
        print("\n".join(sorted(CHECKS)))
        return 0
    run_checks(
        compiler=args.compiler,
        sanitizers=args.sanitizers,
        only=set(args.only) if args.only else None,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
