"""Didactic sorting interpreter aligned with `docs/tads_C/tad_ordenamiento.c`."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


SORTING_ALGORITHMS: list[dict[str, str]] = [
    {"id": "intercambio", "label": "Intercambio directo", "c_function": "ordenar_intercambio"},
    {"id": "seleccion", "label": "Seleccion directa", "c_function": "ordenar_seleccion"},
    {"id": "insercion", "label": "Insercion directa", "c_function": "ordenar_insercion"},
    {"id": "burbuja", "label": "Burbuja mejorada", "c_function": "ordenar_burbuja"},
    {"id": "shell", "label": "Shell sort", "c_function": "ordenar_shell"},
    {"id": "quicksort", "label": "Quick sort", "c_function": "ordenar_quicksort"},
    {"id": "mergesort", "label": "Merge sort", "c_function": "ordenar_mergesort"},
    {"id": "heapsort", "label": "Heap sort", "c_function": "ordenar_heapsort"},
    {"id": "counting_sort", "label": "Counting sort", "c_function": "ordenar_counting_sort"},
    {"id": "binsort", "label": "Binsort", "c_function": "ordenar_binsort"},
    {"id": "radixsort", "label": "Radix sort", "c_function": "ordenar_radixsort"},
]
ORDENAMIENTO_RANGO_MAX = 1_000_000


class SortingExecutionError(ValueError):
    """Raised when sorting execution cannot proceed."""


@dataclass
class _Metrics:
    comparisons: int = 0
    swaps: int = 0
    moves: int = 0
    steps: int = 0


class SortingInterpreter:
    """Generate didactic traces for sorting algorithms."""

    def __init__(self, values: list[int], algorithm_id: str) -> None:
        self.values = list(values)
        self.algorithm_id = str(algorithm_id).strip()
        self.metrics = _Metrics()
        self.sorted_indices: set[int] = set()
        self._steps: list[dict[str, Any]] = []
        if self.algorithm_id not in {item["id"] for item in SORTING_ALGORITHMS}:
            raise SortingExecutionError("El algoritmo seleccionado no existe en el TAD de ordenamiento.")

    def run(self) -> dict[str, Any]:
        """Execute algorithm and return trace and final visual state."""
        if not self.values:
            raise SortingExecutionError("El arreglo no puede estar vacio.")

        self._record("Inicio de ejecucion.", line_token="entry")
        method = getattr(self, f"_run_{self.algorithm_id}")
        method()
        self.sorted_indices = set(range(len(self.values)))
        self._record("Arreglo ordenado.", line_token="return")
        final_state = self._build_state(last_action="Ordenamiento finalizado.")
        return {
            "steps": self._steps,
            "final_state": final_state,
            "metrics": {
                "comparisons": self.metrics.comparisons,
                "swaps": self.metrics.swaps,
                "moves": self.metrics.moves,
                "steps": self.metrics.steps,
            },
        }

    def _record(
        self,
        action: str,
        *,
        line_token: str | None = None,
        comparing: list[int] | None = None,
        swapping: list[int] | None = None,
        active_range: list[int] | None = None,
        pivot_index: int | None = None,
        auxiliary: list[int] | None = None,
        console: str | None = None,
    ) -> None:
        self.metrics.steps += 1
        self._steps.append(
            {
                "step": self.metrics.steps,
                "line_token": line_token,
                "action": action,
                "array_snapshot": list(self.values),
                "comparing_indices": list(comparing or []),
                "swapping_indices": list(swapping or []),
                "sorted_indices": sorted(self.sorted_indices),
                "active_range": list(active_range) if active_range else None,
                "pivot_index": pivot_index,
                "auxiliary_snapshot": list(auxiliary) if auxiliary is not None else None,
                "console_output": console or action,
                "metrics": {
                    "comparisons": self.metrics.comparisons,
                    "swaps": self.metrics.swaps,
                    "moves": self.metrics.moves,
                },
            }
        )

    def _cmp(self, i: int, j: int, *, active_range: list[int] | None = None, line_token: str = "compare") -> bool:
        self.metrics.comparisons += 1
        self._record(
            f"Comparar posiciones {i} y {j} ({self.values[i]} vs {self.values[j]}).",
            line_token=line_token,
            comparing=[i, j],
            active_range=active_range,
        )
        return self.values[i] > self.values[j]

    def _swap(self, i: int, j: int, *, active_range: list[int] | None = None, line_token: str = "swap") -> None:
        self.values[i], self.values[j] = self.values[j], self.values[i]
        self.metrics.swaps += 1
        self._record(
            f"Intercambiar posiciones {i} y {j}.",
            line_token=line_token,
            swapping=[i, j],
            active_range=active_range,
            console=f"Intercambio: {i} <-> {j}",
        )

    def _run_intercambio(self) -> None:
        n = len(self.values)
        for i in range(n - 1):
            for j in range(i + 1, n):
                if self._cmp(i, j, active_range=[i, n - 1]):
                    self._swap(i, j, active_range=[i, n - 1])
            self.sorted_indices.add(i)
        if n:
            self.sorted_indices.add(n - 1)

    def _run_seleccion(self) -> None:
        n = len(self.values)
        for i in range(n - 1):
            min_idx = i
            self._record(
                f"Nuevo minimo provisional en indice {min_idx}.",
                line_token="init_min",
                active_range=[i, n - 1],
            )
            for j in range(i + 1, n):
                self.metrics.comparisons += 1
                self._record(
                    f"Comparar arreglo[{j}] con minimo actual arreglo[{min_idx}].",
                    line_token="compare_min",
                    comparing=[j, min_idx],
                    active_range=[i, n - 1],
                )
                if self.values[j] < self.values[min_idx]:
                    min_idx = j
                    self._record(
                        f"Nuevo indice minimo: {min_idx}.",
                        line_token="set_min",
                        comparing=[min_idx],
                        active_range=[i, n - 1],
                    )
            if min_idx != i:
                self._swap(i, min_idx, active_range=[i, n - 1])
            self.sorted_indices.add(i)
        if n:
            self.sorted_indices.add(n - 1)

    def _run_insercion(self) -> None:
        n = len(self.values)
        for i in range(1, n):
            key = self.values[i]
            self.metrics.moves += 1
            self._record(
                f"Tomar clave {key} desde indice {i}.",
                line_token="take_key",
                active_range=[0, i],
            )
            j = i
            while j > 0:
                self.metrics.comparisons += 1
                self._record(
                    f"Comparar clave {key} con arreglo[{j - 1}]={self.values[j - 1]}.",
                    line_token="while_compare",
                    comparing=[j - 1, j],
                    active_range=[0, i],
                )
                if self.values[j - 1] <= key:
                    break
                self.values[j] = self.values[j - 1]
                self.metrics.moves += 1
                self._record(
                    f"Desplazar arreglo[{j - 1}] a posicion {j}.",
                    line_token="shift",
                    swapping=[j - 1, j],
                    active_range=[0, i],
                )
                j -= 1
            self.values[j] = key
            self.metrics.moves += 1
            self._record(
                f"Insertar clave {key} en indice {j}.",
                line_token="insert_key",
                swapping=[j],
                active_range=[0, i],
            )
            self.sorted_indices = set(range(0, i + 1))

    def _run_burbuja(self) -> None:
        n = len(self.values)
        for passed in range(n - 1):
            swapped = False
            for j in range(0, n - 1 - passed):
                if self._cmp(j, j + 1, active_range=[0, n - 1 - passed]):
                    self._swap(j, j + 1, active_range=[0, n - 1 - passed])
                    swapped = True
            self.sorted_indices.add(n - 1 - passed)
            if not swapped:
                self._record("No hubo intercambio en la pasada; termina temprano.", line_token="break")
                for k in range(0, n - 1 - passed):
                    self.sorted_indices.add(k)
                break

    def _run_shell(self) -> None:
        n = len(self.values)
        gap = n // 2
        while gap > 0:
            self._record(f"Intervalo actual (gap): {gap}.", line_token="gap")
            for i in range(gap, n):
                temp = self.values[i]
                self.metrics.moves += 1
                j = i
                self._record(
                    f"Insertar {temp} en subarreglo por gap {gap}.",
                    line_token="take_temp",
                    active_range=[0, n - 1],
                )
                while j >= gap:
                    self.metrics.comparisons += 1
                    self._record(
                        f"Comparar arreglo[{j - gap}] con temporal {temp}.",
                        line_token="gap_compare",
                        comparing=[j - gap, j],
                        active_range=[0, n - 1],
                    )
                    if self.values[j - gap] <= temp:
                        break
                    self.values[j] = self.values[j - gap]
                    self.metrics.moves += 1
                    self._record(
                        f"Desplazar arreglo[{j - gap}] hacia {j}.",
                        line_token="gap_shift",
                        swapping=[j - gap, j],
                        active_range=[0, n - 1],
                    )
                    j -= gap
                self.values[j] = temp
                self.metrics.moves += 1
                self._record(
                    f"Ubicar temporal en indice {j}.",
                    line_token="gap_insert",
                    swapping=[j],
                    active_range=[0, n - 1],
                )
            gap //= 2

    def _run_quicksort(self) -> None:
        self._quicksort_rec(0, len(self.values) - 1)

    def _quicksort_rec(self, first: int, last: int) -> None:
        if first >= last:
            return
        i, j = first, last
        pivot_index = (first + last) // 2
        pivot = self.values[pivot_index]
        self._record(
            f"Particionar rango [{first}, {last}] con pivote {pivot}.",
            line_token="pivot",
            active_range=[first, last],
            pivot_index=pivot_index,
        )
        while i <= j:
            while True:
                self.metrics.comparisons += 1
                self._record(
                    f"Evaluar arreglo[{i}] < pivote {pivot}: {self.values[i] < pivot}.",
                    line_token="move_i",
                    comparing=[i, pivot_index],
                    active_range=[first, last],
                    pivot_index=pivot_index,
                )
                if not self.values[i] < pivot:
                    break
                i += 1
            while True:
                self.metrics.comparisons += 1
                self._record(
                    f"Evaluar arreglo[{j}] > pivote {pivot}: {self.values[j] > pivot}.",
                    line_token="move_j",
                    comparing=[j, pivot_index],
                    active_range=[first, last],
                    pivot_index=pivot_index,
                )
                if not self.values[j] > pivot:
                    break
                j -= 1
            self.metrics.comparisons += 1
            if i <= j:
                self._swap(i, j, active_range=[first, last], line_token="partition_swap")
                i += 1
                j -= 1
        if first < j:
            self._quicksort_rec(first, j)
        if i < last:
            self._quicksort_rec(i, last)

    def _run_mergesort(self) -> None:
        aux = list(self.values)
        self._mergesort_rec(aux, 0, len(self.values) - 1)

    def _mergesort_rec(self, aux: list[int], left: int, right: int) -> None:
        if left >= right:
            return
        mid = left + (right - left) // 2
        self._record(
            f"Dividir rango [{left}, {right}] en [{left}, {mid}] y [{mid + 1}, {right}].",
            line_token="split",
            active_range=[left, right],
        )
        self._mergesort_rec(aux, left, mid)
        self._mergesort_rec(aux, mid + 1, right)
        self._merge(aux, left, mid, right)

    def _merge(self, aux: list[int], left: int, mid: int, right: int) -> None:
        i, j, k = left, mid + 1, left
        while i <= mid and j <= right:
            self.metrics.comparisons += 1
            self._record(
                f"Comparar en mezcla: arreglo[{i}] y arreglo[{j}].",
                line_token="merge_compare",
                comparing=[i, j],
                active_range=[left, right],
                auxiliary=aux[left:right + 1],
            )
            if self.values[i] <= self.values[j]:
                aux[k] = self.values[i]
                i += 1
            else:
                aux[k] = self.values[j]
                j += 1
            self.metrics.moves += 1
            k += 1
        while i <= mid:
            aux[k] = self.values[i]
            self.metrics.moves += 1
            i += 1
            k += 1
        while j <= right:
            aux[k] = self.values[j]
            self.metrics.moves += 1
            j += 1
            k += 1
        for idx in range(left, right + 1):
            self.values[idx] = aux[idx]
            self.metrics.moves += 1
        self._record(
            f"Fusion completada para rango [{left}, {right}].",
            line_token="merge_copy_back",
            active_range=[left, right],
            auxiliary=aux[left:right + 1],
        )

    def _run_heapsort(self) -> None:
        n = len(self.values)
        for i in range(n // 2 - 1, -1, -1):
            self._heapify(n, i)
        for end in range(n - 1, 0, -1):
            self._swap(0, end, active_range=[0, end], line_token="heap_extract")
            self.sorted_indices.add(end)
            self._heapify(end, 0)
        if n:
            self.sorted_indices.add(0)

    def _heapify(self, n: int, root: int) -> None:
        largest = root
        left = 2 * root + 1
        right = 2 * root + 2

        if left < n:
            self.metrics.comparisons += 1
            self._record(
                f"Comparar hijo izquierdo {left} con raiz {largest}.",
                line_token="heap_compare",
                comparing=[left, largest],
                active_range=[0, n - 1],
            )
            if self.values[left] > self.values[largest]:
                largest = left
        if right < n:
            self.metrics.comparisons += 1
            self._record(
                f"Comparar hijo derecho {right} con mayor {largest}.",
                line_token="heap_compare",
                comparing=[right, largest],
                active_range=[0, n - 1],
            )
            if self.values[right] > self.values[largest]:
                largest = right

        if largest != root:
            self._swap(root, largest, active_range=[0, n - 1], line_token="heap_swap")
            self._heapify(n, largest)

    def _run_counting_sort(self) -> None:
        min_v = min(self.values)
        max_v = max(self.values)
        rng = max_v - min_v + 1
        if rng > ORDENAMIENTO_RANGO_MAX:
            raise SortingExecutionError(
                f"El rango de conteo ({rng}) supera el máximo permitido ({ORDENAMIENTO_RANGO_MAX})."
            )
        count = [0] * rng
        self._record(
            f"Inicializar arreglo de conteo con rango [{min_v}, {max_v}].",
            line_token="count_init",
            auxiliary=count,
        )
        for number in self.values:
            count[number - min_v] += 1
            self.metrics.moves += 1
            self._record(
                f"Incrementar conteo para valor {number}.",
                line_token="count_fill",
                auxiliary=count,
            )
        idx = 0
        for offset, amount in enumerate(count):
            while amount > 0:
                self.values[idx] = offset + min_v
                idx += 1
                amount -= 1
                self.metrics.moves += 1
                count[offset] = amount
                self._record(
                    "Reconstruir arreglo desde conteos.",
                    line_token="count_write",
                    active_range=[0, len(self.values) - 1],
                    auxiliary=count,
                )

    def _run_binsort(self) -> None:
        self._record(
            "Binsort delega en Counting Sort segun implementacion C.",
            line_token="binsort_delegate",
        )
        self._run_counting_sort()

    def _run_radixsort(self) -> None:
        negatives = [-value for value in self.values if value < 0]
        positives = [value for value in self.values if value >= 0]
        self._record(
            "Separar negativos y no negativos para radix.",
            line_token="radix_split",
            auxiliary=negatives + positives,
        )
        if negatives:
            self._radix_non_negative(negatives)
        if positives:
            self._radix_non_negative(positives)
        result: list[int] = []
        for value in reversed(negatives):
            result.append(-value)
        result.extend(positives)
        self.values[:] = result
        self._record("Recombinar negativos y positivos ordenados.", line_token="radix_merge")

    def _radix_non_negative(self, arr: list[int]) -> None:
        max_v = max(arr)
        exp = 1
        while max_v // exp > 0:
            self._counting_digit(arr, exp)
            exp *= 10

    def _counting_digit(self, arr: list[int], exp: int) -> None:
        output = [0] * len(arr)
        count = [0] * 10
        for number in arr:
            count[(number // exp) % 10] += 1
        for i in range(1, 10):
            count[i] += count[i - 1]
        for i in range(len(arr) - 1, -1, -1):
            number = arr[i]
            digit = (number // exp) % 10
            output[count[digit] - 1] = number
            count[digit] -= 1
        for i in range(len(arr)):
            arr[i] = output[i]
            self.metrics.moves += 1
        self._record(
            f"Radix: ordenar por digito de exp={exp}.",
            line_token="radix_digit",
            auxiliary=output,
        )

    def _build_state(self, *, last_action: str) -> dict[str, Any]:
        return {
            "kind": "sorting_array",
            "title": "Arreglo de ordenamiento",
            "items": list(self.values),
            "size": len(self.values),
            "highlighted_indices": [],
            "comparing_indices": [],
            "swapping_indices": [],
            "sorted_indices": sorted(self.sorted_indices),
            "active_range": [0, len(self.values) - 1] if self.values else None,
            "pivot_index": None,
            "auxiliary_array": None,
            "metrics": {
                "comparisons": self.metrics.comparisons,
                "swaps": self.metrics.swaps,
                "moves": self.metrics.moves,
                "steps": self.metrics.steps,
            },
            "last_operation": {
                "name": self.algorithm_id,
                "status": "success",
                "message": last_action,
            },
        }
