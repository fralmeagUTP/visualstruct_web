#!/usr/bin/env bash
set -euo pipefail

root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
harness_dir="$root/tests/conformance/c_harnesses"
tad_dir="$root/docs/tads_C"
tmp_dir="$(mktemp -d)"
trap 'rm -rf "$tmp_dir"' EXIT

export ASAN_OPTIONS="detect_leaks=0:halt_on_error=1"
export UBSAN_OPTIONS="halt_on_error=1:print_stacktrace=1"
strict_flags=(-std=c17 -Wall -Wextra -Wpedantic -Werror -fno-omit-frame-pointer -g)
requested="${1:-all}"

run_case() {
    local structure_id="$1"
    local harness="$2"
    shift 2
    if [[ "$requested" != "all" && "$requested" != "$structure_id" ]]; then
        return 0
    fi
    local sources=()
    while [[ "$1" != "--" ]]; do
        sources+=("$tad_dir/$1")
        shift
    done
    shift
    local sanitizer
    for sanitizer in address undefined; do
        local executable="$tmp_dir/${structure_id}_${sanitizer}"
        timeout 60s gcc "${strict_flags[@]}" "-fsanitize=$sanitizer" \
            -I "$tad_dir" -I "$harness_dir" \
            "$harness_dir/$harness" "${sources[@]}" -o "$executable"
        # Docker Desktop's ASan runtime can recursively emit DEADLYSIGNAL when
        # the instrumented process is wrapped by coreutils timeout/redirection.
        # The harnesses are finite deterministic programs, so execute them
        # directly and let the sanitizer's non-zero exit status fail the job.
        if ! "$executable" "$@"; then
            echo "$structure_id: $sanitizer sanitizer execution failed" >&2
            return 1
        fi
    done
    echo "$structure_id PASS"
}

run_case linked_list linked_list_harness.c tad_lista.c -- append 2 prepend 1
run_case stack stack_harness.c tad_pila.c -- push 1 push 2 pop
run_case queue queue_harness.c tad_cola.c -- enqueue 1 enqueue 2 dequeue
run_case priority_queue priority_queue_harness.c tad_cola_prioridad.c -- enqueue 1 2 enqueue 2 1 dequeue
run_case circular_list circular_list_harness.c tad_lista_circular.c -- append 1 append 2 reverse
run_case sublist sublist_harness.c tad_sublista.c -- add_parent 1 add_child 1 2
run_case abb abb_harness.c tad_abb.c -- insert 2 insert 1 insert 3
run_case avl avl_harness.c tad_avl.c -- insert 30 insert 20 insert 10
run_case red_black red_black_harness.c tad_rojo_negro.c -- insert 10 insert 20 insert 30
run_case binary_heap binary_heap_harness.c tad_monticulo_binario.c -- insert 3 insert 1 extract
run_case graph graph_harness.c tad_grafo.c tad_cola.c -- add_vertex 1 add_vertex 2 add_edge 1 2 5
run_case hash_table hash_table_harness.c tad_tabla_hash.c -- put 1 10 put 2 20
run_case sorting sorting_harness.c tad_ordenamiento.c -- quick 3 1 2
