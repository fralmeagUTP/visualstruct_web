"""Compile C harnesses and compare their state with equivalent Python adapters."""

from __future__ import annotations

import json
import shutil
import subprocess
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable

from app.adapters.queue_adapter import QueueAdapter
from app.adapters.stack_adapter import StackAdapter
from app.adapters.circular_list_adapter import CircularListAdapter
from app.adapters.linked_list_adapter import LinkedListAdapter
from app.adapters.priority_queue_adapter import PriorityQueueAdapter
from app.adapters.sublist_adapter import SublistAdapter
from app.adapters.abb_adapter import ABBAdapter
from app.adapters.avl_adapter import AVLAdapter
from app.adapters.binary_heap_adapter import BinaryHeapAdapter
from app.adapters.red_black_adapter import RedBlackAdapter
from app.adapters.graph_adapter import GraphAdapter
from app.adapters.hash_table_adapter import HashTableAdapter
from app.adapters.sorting_adapter import SortingAdapter
from app.services.conformance.canonical_state import canonicalize_state


class ConformanceRunnerError(RuntimeError):
    """Raised when a harness cannot be compiled or executed safely."""


@dataclass(frozen=True)
class ScenarioOperation:
    operation: str
    payload: dict[str, Any]


@dataclass(frozen=True)
class ConformanceResult:
    structure_id: str
    equivalent: bool
    c_state: dict[str, Any]
    python_state: dict[str, Any]


@dataclass(frozen=True)
class ErrorConformanceResult:
    structure_id: str
    equivalent: bool
    c_error: str | None
    python_error: str | None


@dataclass(frozen=True)
class _RunnerSpec:
    adapter_factory: Callable[[], Any]
    c_source: str
    tad_sources: tuple[str, ...]
    to_c_arguments: Callable[[list[ScenarioOperation]], list[str]]


def _required_int(payload: dict[str, Any], key: str) -> str:
    value = payload.get(key)
    if value is None:
        raise ConformanceRunnerError(f"falta {key}")
    return str(value)


def _stack_arguments(operations: list[ScenarioOperation]) -> list[str]:
    arguments: list[str] = []
    for item in operations:
        if item.operation == "apilar":
            arguments.extend(["push", _required_int(item.payload, "value")])
        elif item.operation == "desapilar":
            arguments.append("pop")
        else:
            raise ConformanceRunnerError(f"operación de pila no soportada: {item.operation}")
    return arguments


def _queue_arguments(operations: list[ScenarioOperation]) -> list[str]:
    arguments: list[str] = []
    for item in operations:
        if item.operation == "encolar":
            arguments.extend(["enqueue", _required_int(item.payload, "value")])
        elif item.operation == "desencolar":
            arguments.append("dequeue")
        else:
            raise ConformanceRunnerError(f"operación de cola no soportada: {item.operation}")
    return arguments


def _mapped_arguments(
    operations: list[ScenarioOperation],
    mapping: dict[str, tuple[str, ...]],
) -> list[str]:
    arguments: list[str] = []
    for item in operations:
        fields = mapping.get(item.operation)
        if fields is None:
            raise ConformanceRunnerError(f"operación no soportada: {item.operation}")
        arguments.append(fields[0])
        arguments.extend(_required_int(item.payload, field) for field in fields[1:])
    return arguments


def _linked_list_arguments(operations: list[ScenarioOperation]) -> list[str]:
    return _mapped_arguments(
        operations,
        {
            "insertar_inicio": ("prepend", "value"),
            "insertar_final": ("append", "value"),
            "eliminar_elemento": ("remove", "value"),
        },
    )


def _circular_list_arguments(operations: list[ScenarioOperation]) -> list[str]:
    return _mapped_arguments(
        operations,
        {
            "insertar_inicio": ("prepend", "value"),
            "insertar_final": ("append", "value"),
            "eliminar_primero": ("remove", "value"),
            "invertir": ("reverse",),
        },
    )


def _priority_queue_arguments(operations: list[ScenarioOperation]) -> list[str]:
    return _mapped_arguments(
        operations,
        {
            "encolar": ("enqueue", "value", "priority"),
            "desencolar": ("dequeue",),
        },
    )


def _sublist_arguments(operations: list[ScenarioOperation]) -> list[str]:
    return _mapped_arguments(
        operations,
        {
            "insertar_padre": ("add_parent", "parent"),
            "insertar_hijo": ("add_child", "parent", "child"),
        },
    )


def _tree_arguments(operations: list[ScenarioOperation]) -> list[str]:
    return _mapped_arguments(
        operations,
        {"insertar": ("insert", "value"), "eliminar": ("remove", "value")},
    )


def _heap_arguments(operations: list[ScenarioOperation]) -> list[str]:
    return _mapped_arguments(
        operations,
        {
            "insertar": ("insert", "value"),
            "extraer_raiz": ("extract",),
        },
    )


def _graph_arguments(operations: list[ScenarioOperation]) -> list[str]:
    arguments: list[str] = []
    for item in operations:
        if item.operation == "create_graph":
            if item.payload.get("directed") not in (True, 1, "true", "1"):
                raise ConformanceRunnerError("el harness C de grafo requiere directed=true")
            continue
        mapping = {
            "insert_vertex": ("add_vertex", "vertex"),
            "insert_edge": ("add_edge", "origin", "target", "weight"),
        }
        arguments.extend(_mapped_arguments([item], mapping))
    return arguments


def _hash_arguments(operations: list[ScenarioOperation]) -> list[str]:
    return _mapped_arguments(
        operations,
        {
            "insert": ("put", "key", "value"),
            "remove": ("remove", "key"),
        },
    )


def _sorting_arguments(operations: list[ScenarioOperation]) -> list[str]:
    values: list[Any] | None = None
    algorithm = "bubble"
    algorithm_names = {
        "intercambio": "exchange", "seleccion": "selection", "insercion": "insertion",
        "burbuja": "bubble", "shell": "shell", "quicksort": "quick", "heapsort": "heap",
    }
    ran = False
    for item in operations:
        if item.operation == "create_array":
            raw = item.payload.get("values")
            values = raw if isinstance(raw, list) else [part.strip() for part in str(raw).split(",") if part.strip()]
        elif item.operation == "select_algorithm":
            selected = str(item.payload.get("algorithm_id", ""))
            if selected not in algorithm_names:
                raise ConformanceRunnerError(f"algoritmo no soportado por harness: {selected}")
            algorithm = algorithm_names[selected]
        elif item.operation == "run":
            ran = True
        else:
            raise ConformanceRunnerError(f"operación de ordenamiento no soportada: {item.operation}")
    if values is None or not ran:
        raise ConformanceRunnerError("ordenamiento requiere create_array y run")
    return [algorithm, *[str(int(value)) for value in values]]


SPECS = {
    "stack": _RunnerSpec(StackAdapter, "stack_harness.c", ("tad_pila.c",), _stack_arguments),
    "queue": _RunnerSpec(QueueAdapter, "queue_harness.c", ("tad_cola.c",), _queue_arguments),
    "linked_list": _RunnerSpec(LinkedListAdapter, "linked_list_harness.c", ("tad_lista.c",), _linked_list_arguments),
    "circular_list": _RunnerSpec(CircularListAdapter, "circular_list_harness.c", ("tad_lista_circular.c",), _circular_list_arguments),
    "priority_queue": _RunnerSpec(PriorityQueueAdapter, "priority_queue_harness.c", ("tad_cola_prioridad.c",), _priority_queue_arguments),
    "sublist": _RunnerSpec(SublistAdapter, "sublist_harness.c", ("tad_sublista.c",), _sublist_arguments),
    "binary_heap": _RunnerSpec(BinaryHeapAdapter, "binary_heap_harness.c", ("tad_monticulo_binario.c",), _heap_arguments),
    "abb": _RunnerSpec(ABBAdapter, "abb_harness.c", ("tad_abb.c",), _tree_arguments),
    "avl": _RunnerSpec(AVLAdapter, "avl_harness.c", ("tad_avl.c",), _tree_arguments),
    "red_black": _RunnerSpec(RedBlackAdapter, "red_black_harness.c", ("tad_rojo_negro.c",), _tree_arguments),
    "graph": _RunnerSpec(GraphAdapter, "graph_harness.c", ("tad_grafo.c", "tad_cola.c"), _graph_arguments),
    "hash_table": _RunnerSpec(HashTableAdapter, "hash_table_harness.c", ("tad_tabla_hash.c",), _hash_arguments),
    "sorting": _RunnerSpec(SortingAdapter, "sorting_harness.c", ("tad_ordenamiento.c",), _sorting_arguments),
}


class ConformanceRunner:
    """Run deterministic C/Python scenarios outside the web request path."""

    def __init__(self, root: Path | None = None, compiler: str | None = None) -> None:
        self.root = root or Path(__file__).resolve().parents[3]
        self.compiler = compiler or shutil.which("gcc") or ""
        self.harness_dir = self.root / "tests" / "conformance" / "c_harnesses"
        self.c_tads_dir = self.root / "docs" / "tads_C"

    def _compile(self, structure_id: str, destination: Path) -> None:
        if not self.compiler:
            raise ConformanceRunnerError("gcc no está disponible")
        spec = SPECS[structure_id]
        command = [
            self.compiler, "-std=c17", "-Wall", "-Wextra", "-Wpedantic", "-Werror",
            "-I", str(self.c_tads_dir), "-I", str(self.harness_dir),
            str(self.harness_dir / spec.c_source),
            *(str(self.c_tads_dir / source) for source in spec.tad_sources),
            "-o", str(destination),
        ]
        completed = subprocess.run(command, capture_output=True, text=True, check=False)
        if completed.returncode != 0:
            raise ConformanceRunnerError(f"falló compilación de {structure_id}: {completed.stderr.strip()}")

    @staticmethod
    def _canonical_c_output(stdout: str) -> dict[str, Any]:
        for line in reversed(stdout.splitlines()):
            if line.strip().startswith("{"):
                return json.loads(line)
        raise ConformanceRunnerError("el harness no emitió estado canónico")

    def compare(self, structure_id: str, operations: list[ScenarioOperation]) -> ConformanceResult:
        normalized_id = str(structure_id).strip().lower()
        if normalized_id not in SPECS:
            raise ConformanceRunnerError(f"runner no registrado: {structure_id}")
        spec = SPECS[normalized_id]
        arguments = spec.to_c_arguments(operations)
        adapter = spec.adapter_factory()
        for item in operations:
            adapter.execute(item.operation, dict(item.payload))
        python_state = canonicalize_state(normalized_id, adapter.to_visual_state())

        with tempfile.TemporaryDirectory(prefix="visualestruct-conformance-") as directory:
            executable = Path(directory) / f"{normalized_id}_harness.exe"
            self._compile(normalized_id, executable)
            completed = subprocess.run([str(executable), *arguments], capture_output=True, text=True, check=False)
            if completed.returncode != 0:
                raise ConformanceRunnerError(f"falló escenario C de {normalized_id}: {completed.stderr.strip()}")
            c_state = self._canonical_c_output(completed.stdout)

        return ConformanceResult(
            structure_id=normalized_id,
            equivalent=c_state.get("state") == python_state.get("state"),
            c_state=c_state,
            python_state=python_state,
        )

    def compare_error(
        self, structure_id: str, operations: list[ScenarioOperation]
    ) -> ErrorConformanceResult:
        """Require both implementations to reject the same deterministic scenario."""
        normalized_id = str(structure_id).strip().lower()
        if normalized_id not in SPECS:
            raise ConformanceRunnerError(f"runner no registrado: {structure_id}")
        spec = SPECS[normalized_id]
        arguments = spec.to_c_arguments(operations)

        python_error: str | None = None
        adapter = spec.adapter_factory()
        try:
            for item in operations:
                adapter.execute(item.operation, dict(item.payload))
        except Exception as error:  # The domain exposes several intentional error types.
            python_error = f"{type(error).__name__}: {error}"

        with tempfile.TemporaryDirectory(prefix="visualestruct-conformance-error-") as directory:
            executable = Path(directory) / f"{normalized_id}_harness.exe"
            self._compile(normalized_id, executable)
            completed = subprocess.run(
                [str(executable), *arguments], capture_output=True, text=True, check=False
            )
            c_error = completed.stderr.strip() if completed.returncode != 0 else None

        return ErrorConformanceResult(
            structure_id=normalized_id,
            equivalent=python_error is not None and c_error is not None,
            c_error=c_error,
            python_error=python_error,
        )


class CompiledConformanceRunner(ConformanceRunner):
    """Reuse strict C17 harness binaries across a large differential campaign."""

    def __init__(self, root: Path | None = None, compiler: str | None = None) -> None:
        super().__init__(root=root, compiler=compiler)
        self._temporary_directory = tempfile.TemporaryDirectory(
            prefix="visualestruct-conformance-campaign-"
        )
        self._output_dir = Path(self._temporary_directory.name)
        self._executables: dict[str, Path] = {}

    def close(self) -> None:
        self._temporary_directory.cleanup()

    def __enter__(self) -> "CompiledConformanceRunner":
        return self

    def __exit__(self, *_args: object) -> None:
        self.close()

    def compile_all(self) -> None:
        for structure_id in sorted(SPECS):
            self._executable(structure_id)

    def _executable(self, structure_id: str) -> Path:
        executable = self._executables.get(structure_id)
        if executable is None:
            executable = self._output_dir / f"{structure_id}_harness.exe"
            self._compile(structure_id, executable)
            self._executables[structure_id] = executable
        return executable

    def compare(self, structure_id: str, operations: list[ScenarioOperation]) -> ConformanceResult:
        normalized_id = str(structure_id).strip().lower()
        if normalized_id not in SPECS:
            raise ConformanceRunnerError(f"runner no registrado: {structure_id}")
        spec = SPECS[normalized_id]
        arguments = spec.to_c_arguments(operations)
        adapter = spec.adapter_factory()
        for item in operations:
            adapter.execute(item.operation, dict(item.payload))
        python_state = canonicalize_state(normalized_id, adapter.to_visual_state())

        completed = subprocess.run(
            [str(self._executable(normalized_id)), *arguments],
            capture_output=True,
            text=True,
            check=False,
        )
        if completed.returncode != 0:
            raise ConformanceRunnerError(
                f"falló escenario C de {normalized_id}: {completed.stderr.strip()}"
            )
        c_state = self._canonical_c_output(completed.stdout)
        return ConformanceResult(
            structure_id=normalized_id,
            equivalent=c_state.get("state") == python_state.get("state"),
            c_state=c_state,
            python_state=python_state,
        )
