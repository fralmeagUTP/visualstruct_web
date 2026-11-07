"""Finite current callers for the original twelve hidden positional case intents."""
from pathlib import Path
import json
import shutil
import subprocess

ROOT = Path(__file__).resolve().parents[1]
CASES = [
    ('legacy-insert-before-position2', 'insertar_posicion', {'position': 2, 'value': 9}),
    ('legacy-relative-insert-after-position2', 'insertar_elemento', {'position': 2, 'relative': 0, 'value': 9}),
    ('legacy-delete-position2', 'eliminar_posicion', {'position': 2}),
    ('legacy-before-1', 'insertar_posicion', {'position': 1, 'value': 9}),
    ('legacy-before-3', 'insertar_posicion', {'position': 3, 'value': 9}),
    ('legacy-before-4', 'insertar_posicion', {'position': 4, 'value': 9}),
    ('legacy-before-5', 'insertar_posicion', {'position': 5, 'value': 9}),
    ('legacy-after-1', 'insertar_elemento', {'position': 1, 'relative': 0, 'value': 9}),
    ('legacy-after-3', 'insertar_elemento', {'position': 3, 'relative': 0, 'value': 9}),
    ('legacy-relative-before2', 'insertar_elemento', {'position': 2, 'relative': -1, 'value': 9}),
    ('legacy-delete-1', 'eliminar_posicion', {'position': 1}),
    ('legacy-delete-3', 'eliminar_posicion', {'position': 3}),
]
HIDDEN = {'insertar_posicion', 'insertar_elemento', 'eliminar_posicion'}
SEED = [4, 5, 6]
OBSERVER = r'''
#include <assert.h>
#include <stdio.h>
#include <stdlib.h>
#include "tad_lista.h"
static void *objects[32];
static int alive[32], used, allocations, frees, bad;
static void report(void) {
    int live = 0;
    for (int i = 0; i < used; ++i) live += alive[i];
    fprintf(stderr, "OWNERSHIP %d %d %d %d\n", allocations, frees, live, bad);
    assert(live == 0 && allocations == frees && bad == 0);
}
void *owned_malloc(size_t size) {
    if (used == 0) assert(atexit(report) == 0);
    void *p = malloc(size);
    assert(p != NULL && used < 32);
    objects[used] = p; alive[used++] = 1; ++allocations;
    return p;
}
void owned_free(void *p) {
    if (p == NULL) return;
    int found = -1;
    for (int i = 0; i < used; ++i) if (alive[i] && objects[i] == p) {found = i; break;}
    if (found < 0) {++bad; assert(0);}
    alive[found] = 0; objects[found] = NULL; ++frees;
    free(p);
}
void snapshot(Tlista head) {
    fputs("STATE [", stderr);
    int count = 0;
    for (Tlista p = head; p != NULL; p = p->sgte) {
        assert(count < 32);
        int known_live = 0;
        for (int i = 0; i < used; ++i) if (alive[i] && objects[i] == p) known_live = 1;
        assert(known_live);
        fprintf(stderr, "%s%d", count++ ? "," : "", p->nro);
    }
    fputs("]\n", stderr);
}
'''


def rendered_caller(page_html: str, target: Path) -> dict:
    """Run the shipped JS renderer on the actual HTTP model using jsdom."""
    html = target / 'page.html'
    html.write_text(page_html, encoding='utf-8')
    node = shutil.which('node')
    assert node, 'Node is required to validate the real caller renderer'
    run = subprocess.run([node, str(ROOT / 'qa/export_hidden_linked_caller.js'), str(ROOT), str(html)],
                         capture_output=True, text=True, timeout=30)
    assert run.returncode == 0, run.stderr
    return json.loads(run.stdout)


def verify_native_caller(source: str, expected: list[int], target: Path, client) -> dict:
    """Compile the unchanged caller, then observe state and exact allocation identity."""
    for kind, extension in [('source', 'c'), ('header', 'h')]:
        response = client.get('/help/source/linked_list/' + kind)
        assert response.status_code == 200
        name = 'tad_lista.' + extension
        assert response.data == (ROOT / 'docs/tads_C' / name).read_bytes()
        (target / name).write_bytes(response.data)
    compiler = shutil.which('gcc')
    assert compiler, 'Native C17 compiler is required'
    flags = [compiler, '-std=c17', '-Wall', '-Wextra', '-Wpedantic', '-Werror', '-I', str(target)]
    main = target / 'main.c'
    main.write_text(source, encoding='utf-8')
    original = target / 'original.exe'
    commands = [[*flags, str(main), str(target / 'tad_lista.c'), '-o', str(original)]]
    (target / 'observer.c').write_text(OBSERVER, encoding='utf-8')
    hooks = target / 'observer.h'
    hooks.write_text('#include <stddef.h>\nstruct NodoLista;\n'
                     'void *owned_malloc(size_t);\nvoid owned_free(void *);\nvoid snapshot(struct NodoLista *);\n', encoding='utf-8')
    cleanup = '    /* Liberar los nodos que aún pertenecen al caller. */ lista_limpiar(&lista);'
    assert source.count(cleanup) == 1
    observed_main = target / 'observed-main.c'
    observed_main.write_text('#include "observer.h"\n' + source.replace(cleanup, '    snapshot(lista);\n' + cleanup), encoding='utf-8')
    obj = target / 'list.o'
    observed = target / 'observed.exe'
    commands += [
        [*flags, '-include', str(hooks), '-Dmalloc=owned_malloc', '-Dfree=owned_free',
         '-c', str(target / 'tad_lista.c'), '-o', str(obj)],
        [*flags, str(observed_main), str(target / 'observer.c'), str(obj), '-o', str(observed)],
    ]
    for command in commands:
        build = subprocess.run(command, capture_output=True, text=True, timeout=30)
        assert build.returncode == 0 and not build.stderr, build.stderr
    raw = subprocess.run([str(original)], capture_output=True, text=True, timeout=10)
    run = subprocess.run([str(observed)], capture_output=True, text=True, timeout=10)
    assert raw.returncode == run.returncode == 0, (raw.stderr, run.stderr)
    assert raw.stdout == run.stdout and not raw.stderr
    lines = run.stderr.splitlines()
    state = next(line.removeprefix('STATE ') for line in lines if line.startswith('STATE '))
    assert json.loads(state) == expected
    ownership = next(line for line in lines if line.startswith('OWNERSHIP '))
    allocations, frees, live, bad = map(int, ownership.split()[1:])
    assert allocations == frees and allocations >= len(SEED) and live == bad == 0
    return {'compile_exit': 0, 'native_exit': 0, 'matches': True, 'ownership': ownership}
