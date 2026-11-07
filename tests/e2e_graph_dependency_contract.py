"""Verify the approved Graph caller has no external queue dependency."""
import re
import subprocess


def verify_graph_only_bfs(source: bytes, header: bytes, directory):
    for data in [source,header]:
        assert not re.search(rb'#\s*include\s*[<"]tad_cola(?:\.h)?[>"]', data)
    (directory/'tad_grafo.c').write_bytes(source)
    (directory/'tad_grafo.h').write_bytes(header)
    caller='''#include "tad_grafo.h"
#include <assert.h>
int main(void) {
    GrafoEstado status = GRAFO_OK;
    Grafo g = grafo_crear();
    g = grafo_insertar_vertice(g, 7, &status); assert(status == GRAFO_OK);
    g = grafo_insertar_vertice(g, 8, &status); assert(status == GRAFO_OK);
    g = grafo_insertar_arco(g, 7, 8, 1, &status); assert(status == GRAFO_OK);
    ListaVertice result = grafo_bfs(g, 7, &status);
    assert(status == GRAFO_OK && result && result->dato == 7);
    assert(result->sig && result->sig->dato == 8 && !result->sig->sig);
    grafo_liberar_vertices(&result); grafo_destruir(&g);
    assert(!result && !g.v && !g.a);
    return 0;
}
'''
    (directory/'main.c').write_text(caller)
    built=subprocess.run(['gcc','-std=c17','-Wall','-Wextra','-Wpedantic','-Werror',
                          str(directory/'tad_grafo.c'),str(directory/'main.c'),'-o',str(directory/'bfs')],capture_output=True,text=True,timeout=30)
    assert built.returncode==0,built.stderr
    run=subprocess.run([str(directory/'bfs')],capture_output=True,text=True,timeout=10)
    assert run.returncode==0,run.stderr
