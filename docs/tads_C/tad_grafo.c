/* Adaptacion docente del TAD para este libro.
   Conserva sus identificadores y las estrategias de los seis algoritmos. */
#include "tad_grafo.h"
#include <stdlib.h>
#include <stdio.h>
#include <stdint.h>
#include <limits.h>

static void fijar_estado(GrafoEstado *e, GrafoEstado valor) {
    if (e != NULL) *e = valor;
}

Grafo grafo_crear(void) {
    Grafo g = {NULL, NULL};
    return g;
}

int grafo_existe_vertice(Grafo g, int x) {
    for (ListaVertice v = g.v; v != NULL; v = v->sig)
        if (v->dato == x) return 1;
    return 0;
}

static ListaArco buscar_arco(Grafo g, int x, int y) {
    for (ListaArco a = g.a; a != NULL; a = a->sig)
        if (a->origen == x && a->destino == y) return a;
    return NULL;
}

int grafo_existe_arco(Grafo g, int x, int y) {
    return buscar_arco(g, x, y) != NULL;
}

Grafo grafo_insertar_vertice(Grafo g, int x, GrafoEstado *estado) {
    fijar_estado(estado, GRAFO_OK);
    if (grafo_existe_vertice(g, x)) return g;
    ListaVertice nuevo = malloc(sizeof *nuevo);
    if (nuevo == NULL) {
        fijar_estado(estado, GRAFO_MEMORIA);
        return g;
    }
    *nuevo = (struct NodoV){x, g.v, 0};
    g.v = nuevo;
    return g;
}

Grafo grafo_insertar_arco(Grafo g, int x, int y, int z,
                        GrafoEstado *estado) {
    ListaArco existente = buscar_arco(g, x, y);
    ListaVertice vx = NULL, vy = NULL;
    fijar_estado(estado, GRAFO_OK);
    if (existente != NULL) {
        existente->costo = z;
        return g;
    }
    if (!grafo_existe_vertice(g, x)) {
        vx = malloc(sizeof *vx);
        if (vx == NULL) {
            fijar_estado(estado, GRAFO_MEMORIA);
            return g;
        }
        *vx = (struct NodoV){x, NULL, 0};
    }
    if (y != x && !grafo_existe_vertice(g, y)) {
        vy = malloc(sizeof *vy);
        if (vy == NULL) {
            free(vx);
            fijar_estado(estado, GRAFO_MEMORIA);
            return g;
        }
        *vy = (struct NodoV){y, NULL, 0};
    }
    ListaArco nuevo = malloc(sizeof *nuevo);
    if (nuevo == NULL) {
        free(vx);
        free(vy);
        fijar_estado(estado, GRAFO_MEMORIA);
        return g;
    }
    if (vx != NULL) { vx->sig = g.v; g.v = vx; }
    if (vy != NULL) { vy->sig = g.v; g.v = vy; }
    *nuevo = (struct NodoA){x, y, z, g.a};
    g.a = nuevo;
    return g;
}

Grafo grafo_eliminar_arco(Grafo g, int x, int y) {
    ListaArco *enlace = &g.a;
    while (*enlace != NULL) {
        ListaArco actual = *enlace;
        if (actual->origen == x && actual->destino == y) {
            *enlace = actual->sig;
            free(actual);
            break;
        }
        enlace = &actual->sig;
    }
    return g;
}

Grafo grafo_eliminar_vertice(Grafo g, int x) {
    if (!grafo_existe_vertice(g, x)) return g;
    ListaArco *enlace = &g.a;
    while (*enlace != NULL) {
        ListaArco actual = *enlace;
        if (actual->origen == x || actual->destino == x) {
            *enlace = actual->sig;
            free(actual);
        } else enlace = &actual->sig;
    }
    ListaVertice *vertice = &g.v;
    while ((*vertice)->dato != x) vertice = &(*vertice)->sig;
    ListaVertice retirado = *vertice;
    *vertice = retirado->sig;
    free(retirado);
    return g;
}

int grafo_costo_arco(Grafo g, int x, int y, int *salida) {
    ListaArco a = buscar_arco(g, x, y);
    if (a == NULL || salida == NULL) return 0;
    *salida = a->costo;
    return 1;
}

int grafo_orden(Grafo g) {
    int n = 0;
    for (ListaVertice v = g.v; v != NULL; v = v->sig) n++;
    return n;
}

int grafo_tamano(Grafo g) {
    int m = 0;
    for (ListaArco a = g.a; a != NULL; a = a->sig) m++;
    return m;
}

int grafo_grado_vertice(Grafo g, int x) {
    int grado = 0;
    for (ListaArco a = g.a; a != NULL; a = a->sig)
        if (a->origen == x) grado++;
    return grado;
}

ListaVertice grafo_vertices(Grafo g) { return g.v; }

ListaArco grafo_arcos(Grafo g) { return g.a; }

Grafo grafo_marcar_vertice(Grafo g, int x) {
    for (ListaVertice v = g.v; v != NULL; v = v->sig)
        if (v->dato == x) { v->marcado = 1; break; }
    return g;
}

Grafo grafo_desmarcar_vertice(Grafo g, int x) {
    for (ListaVertice v = g.v; v != NULL; v = v->sig)
        if (v->dato == x) { v->marcado = 0; break; }
    return g;
}

Grafo grafo_desmarcar(Grafo g) {
    for (ListaVertice v = g.v; v != NULL; v = v->sig)
        v->marcado = 0;
    return g;
}

int grafo_marcado_vertice(Grafo g, int x) {
    for (ListaVertice v = g.v; v != NULL; v = v->sig)
        if (v->dato == x) return v->marcado;
    return 0;
}

void grafo_liberar_vertices(ListaVertice *lista) {
    if (lista == NULL) return;
    while (*lista != NULL) {
        ListaVertice siguiente = (*lista)->sig;
        free(*lista);
        *lista = siguiente;
    }
}

void grafo_liberar_arcos(ListaArco *lista) {
    if (lista == NULL) return;
    while (*lista != NULL) {
        ListaArco siguiente = (*lista)->sig;
        free(*lista);
        *lista = siguiente;
    }
}

void grafo_destruir(Grafo *g) {
    if (g == NULL) return;
    grafo_liberar_arcos(&g->a);
    grafo_liberar_vertices(&g->v);
}

static ListaVertice vecinos(Grafo g, int x, int inverso,
                            GrafoEstado *estado) {
    ListaVertice lista = NULL;
    fijar_estado(estado, GRAFO_OK);
    for (ListaArco a = g.a; a != NULL; a = a->sig) {
        if ((!inverso && a->origen == x) ||
            (inverso && a->destino == x)) {
            ListaVertice nuevo = malloc(sizeof *nuevo);
            if (nuevo == NULL) {
                grafo_liberar_vertices(&lista);
                fijar_estado(estado, GRAFO_MEMORIA);
                return NULL;
            }
            int valor = inverso ? a->origen : a->destino;
            *nuevo = (struct NodoV){valor, lista, 0};
            lista = nuevo;
        }
    }
    return lista;
}

ListaVertice grafo_sucesores(Grafo g, int x, GrafoEstado *estado) {
    return vecinos(g, x, 0, estado);
}

ListaVertice grafo_predecesores(Grafo g, int x, GrafoEstado *estado) {
    return vecinos(g, x, 1, estado);
}

void grafo_imprimir_vertices(Grafo g) {
    for (ListaVertice v = g.v; v != NULL; v = v->sig)
        printf("%d (marca %d)\n", v->dato, v->marcado);
}

void grafo_imprimir_arcos(Grafo g) {
    for (ListaArco a = g.a; a != NULL; a = a->sig)
        printf("%d -> %d (%d)\n", a->origen, a->destino, a->costo);
}

typedef struct {
    int n;
    int *vertices, *prev, *usado, *alcanzable;
    long long *dist;
} Trabajo;

static void liberar_trabajo(Trabajo *t) {
    free(t->vertices); free(t->prev); free(t->usado);
    free(t->alcanzable); free(t->dist);
}

static int preparar(Grafo g, Trabajo *t, GrafoEstado *estado) {
    *t = (Trabajo){0, NULL, NULL, NULL, NULL, NULL};
    fijar_estado(estado, GRAFO_OK);
    int n = grafo_orden(g);
    if (n == 0) { fijar_estado(estado, GRAFO_NO_EXISTE); return 0; }
    if ((size_t)n > SIZE_MAX / sizeof(long long)) {
        fijar_estado(estado, GRAFO_RANGO); return 0;
    }
    t->n = n;
    t->vertices = malloc((size_t)n * sizeof(int));
    t->prev = malloc((size_t)n * sizeof(int));
    t->usado = calloc((size_t)n, sizeof(int));
    t->alcanzable = calloc((size_t)n, sizeof(int));
    t->dist = calloc((size_t)n, sizeof(long long));
    if (!t->vertices || !t->prev || !t->usado ||
        !t->alcanzable || !t->dist) {
        liberar_trabajo(t);
        fijar_estado(estado, GRAFO_MEMORIA); return 0;
    }
    int i = 0;
    for (ListaVertice v = g.v; v != NULL; v = v->sig)
        t->vertices[i++] = v->dato;
    for (i = 0; i < n; i++) t->prev[i] = -1;
    return 1;
}

static int indiceVertice(const Trabajo *t, int valor) {
    for (int i = 0; i < t->n; i++)
        if (t->vertices[i] == valor) return i;
    return -1;
}

static int agregar_visita(ListaVertice *lista, ListaVertice *ultimo,
                          int valor) {
    ListaVertice nuevo = malloc(sizeof *nuevo);
    if (nuevo == NULL) return 0;
    *nuevo = (struct NodoV){valor, NULL, 0};
    if (*ultimo == NULL) *lista = nuevo;
    else (*ultimo)->sig = nuevo;
    *ultimo = nuevo;
    return 1;
}

static void publicar_marcas(Grafo g, ListaVertice recorrido) {
    grafo_desmarcar(g);
    for (; recorrido != NULL; recorrido = recorrido->sig)
        grafo_marcar_vertice(g, recorrido->dato);
}




ListaVertice grafo_bfs(Grafo g, int inicio, GrafoEstado *estado) {
    Trabajo t;
    ListaVertice lista = NULL, ultimo = NULL;
    if (!preparar(g, &t, estado)) return NULL;
    int s = indiceVertice(&t, inicio), correcto = 1;
    if (s < 0) {
        liberar_trabajo(&t);
        fijar_estado(estado, GRAFO_NO_EXISTE); return NULL;
    }
    /* prev se usa aqui como cola de indices, con capacidad n. */
    int frente = 0, final = 0;
    t.prev[final++] = s; t.usado[s] = 1;
    while (frente < final && correcto) {
        int u = t.prev[frente++];
        correcto = agregar_visita(&lista, &ultimo, t.vertices[u]);
        if (!correcto) break;
        GrafoEstado e;
        ListaVertice suces = grafo_sucesores(g, t.vertices[u], &e);
        if (e != GRAFO_OK) { correcto = 0; break; }
        for (ListaVertice p = suces; p != NULL; p = p->sig) {
            int v = indiceVertice(&t, p->dato);
            if (v >= 0 && !t.usado[v]) {
                t.usado[v] = 1;
                t.prev[final++] = v;
            }
        }
        grafo_liberar_vertices(&suces);
    }
    liberar_trabajo(&t);
    if (!correcto) {
        grafo_liberar_vertices(&lista);
        fijar_estado(estado, GRAFO_MEMORIA);
    } else publicar_marcas(g, lista);
    return lista;
}

static int grafo_dfs_recursivo(Grafo g, Trabajo *t, int u,
                              ListaVertice *lista, ListaVertice *ultimo) {
    t->usado[u] = 1;
    if (!agregar_visita(lista, ultimo, t->vertices[u])) return 0;
    GrafoEstado e;
    ListaVertice suces = grafo_sucesores(g, t->vertices[u], &e);
    if (e != GRAFO_OK) return 0;
    int correcto = 1;
    for (ListaVertice p = suces; p != NULL && correcto; p = p->sig) {
        int v = indiceVertice(t, p->dato);
        if (v >= 0 && !t->usado[v])
            correcto = grafo_dfs_recursivo(g, t, v, lista, ultimo);
    }
    grafo_liberar_vertices(&suces);
    return correcto;
}

ListaVertice grafo_dfs(Grafo g, int inicio, GrafoEstado *estado) {
    Trabajo t;
    ListaVertice lista = NULL, ultimo = NULL;
    if (!preparar(g, &t, estado)) return NULL;
    int s = indiceVertice(&t, inicio);
    if (s < 0) {
        liberar_trabajo(&t);
        fijar_estado(estado, GRAFO_NO_EXISTE); return NULL;
    }
    int correcto = grafo_dfs_recursivo(g, &t, s, &lista, &ultimo);
    liberar_trabajo(&t);
    if (!correcto) {
        grafo_liberar_vertices(&lista);
        fijar_estado(estado, GRAFO_MEMORIA);
    } else publicar_marcas(g, lista);
    return lista;
}

static int sumar_seguro(long long x, int y, long long *salida) {
    if ((y > 0 && x > LLONG_MAX - y) ||
        (y < 0 && x < LLONG_MIN - y)) return 0;
    *salida = x + y;
    return 1;
}

static ListaArco reconstruir(Grafo g, Trabajo *t, int s, int d,
                             GrafoEstado *estado) {
    ListaArco lista = NULL;
    if (!t->alcanzable[d]) {
        fijar_estado(estado, GRAFO_NO_EXISTE); return NULL;
    }
    int pasos = 0;
    while (d != s) {
        int p = t->prev[d];
        if (p < 0 || pasos++ >= t->n) {
            grafo_liberar_arcos(&lista);
            fijar_estado(estado, GRAFO_ARGUMENTO); return NULL;
        }
        ListaArco a = buscar_arco(g, t->vertices[p], t->vertices[d]);
        ListaArco nuevo = malloc(sizeof *nuevo);
        if (nuevo == NULL) {
            grafo_liberar_arcos(&lista);
            fijar_estado(estado, GRAFO_MEMORIA); return NULL;
        }
        *nuevo = (struct NodoA){a->origen, a->destino, a->costo, lista};
        lista = nuevo;
        d = p;
    }
    return lista;
}



ListaArco grafo_dijkstra(Grafo g, int inicio, int llegada,
                       GrafoEstado *estado) {
    Trabajo t;
    if (!preparar(g, &t, estado)) return NULL;
    int s = indiceVertice(&t, inicio), d = indiceVertice(&t, llegada);
    GrafoEstado e = GRAFO_OK;
    if (s < 0 || d < 0) e = GRAFO_NO_EXISTE;
    for (ListaArco a = g.a; a != NULL; a = a->sig)
        if (a->costo < 0) e = GRAFO_PESO_NEGATIVO;
    if (e == GRAFO_OK) t.alcanzable[s] = 1;
    for (int k = 0; k < t.n && e == GRAFO_OK; k++) {
        int u = -1;
        for (int j = 0; j < t.n; j++)
            if (!t.usado[j] && t.alcanzable[j] &&
                (u < 0 || t.dist[j] < t.dist[u])) u = j;
        if (u < 0) break;
        t.usado[u] = 1;
        for (ListaArco a = g.a; a != NULL; a = a->sig) {
            if (a->origen != t.vertices[u]) continue;
            int v = indiceVertice(&t, a->destino);
            if (t.usado[v]) continue;
            long long nueva;
            if (!sumar_seguro(t.dist[u], a->costo, &nueva)) {
                e = GRAFO_RANGO; break;
            }
            if (!t.alcanzable[v] || nueva < t.dist[v]) {
                t.dist[v] = nueva; t.prev[v] = u;
                t.alcanzable[v] = 1;
            }
        }
    }
    ListaArco camino = NULL;
    if (e == GRAFO_OK) camino = reconstruir(g, &t, s, d, &e);
    liberar_trabajo(&t);
    fijar_estado(estado, e);
    return camino;
}


ListaArco grafo_bellman_ford(Grafo g, int inicio, int llegada,
                           GrafoEstado *estado) {
    Trabajo t;
    if (!preparar(g, &t, estado)) return NULL;
    int s = indiceVertice(&t, inicio), d = indiceVertice(&t, llegada);
    GrafoEstado e = GRAFO_OK;
    if (s < 0 || d < 0) e = GRAFO_NO_EXISTE;
    else t.alcanzable[s] = 1;
    long long cota = (long long)(t.n - 1) * INT_MIN;
    for (int k = 0; k < t.n && e == GRAFO_OK; k++) {
        int cambio = 0;
        for (ListaArco a = g.a; a != NULL; a = a->sig) {
            int u = indiceVertice(&t, a->origen);
            int v = indiceVertice(&t, a->destino);
            if (!t.alcanzable[u]) continue;
            long long nueva;
            if (!sumar_seguro(t.dist[u], a->costo, &nueva)) {
                e = GRAFO_RANGO; break;
            }
            if (!t.alcanzable[v] || nueva < t.dist[v]) {
                if (k == t.n - 1 || nueva < cota) {
                    e = GRAFO_CICLO_NEGATIVO; break;
                }
                t.dist[v] = nueva; t.prev[v] = u;
                t.alcanzable[v] = 1; cambio = 1;
            }
        }
        if (!cambio) break;
    }
    ListaArco camino = NULL;
    if (e == GRAFO_OK) camino = reconstruir(g, &t, s, d, &e);
    liberar_trabajo(&t);
    fijar_estado(estado, e);
    return camino;
}


static int grafo_simetrico(Grafo g) {
    for (ListaArco a = g.a; a != NULL; a = a->sig) {
        ListaArco b = buscar_arco(g, a->destino, a->origen);
        if (b == NULL || b->costo != a->costo) return 0;
    }
    return 1;
}

ListaArco grafo_prim(Grafo g, int inicio, GrafoEstado *estado) {
    Trabajo t;
    if (!preparar(g, &t, estado)) return NULL;
    int s = indiceVertice(&t, inicio);
    GrafoEstado e = GRAFO_OK;
    if (!grafo_simetrico(g)) e = GRAFO_ARGUMENTO;
    else if (s < 0) e = GRAFO_NO_EXISTE;
    else t.alcanzable[s] = 1;
    for (int k = 0; k < t.n && e == GRAFO_OK; k++) {
        int u = -1;
        for (int j = 0; j < t.n; j++)
            if (!t.usado[j] && t.alcanzable[j] &&
                (u < 0 || t.dist[j] < t.dist[u])) u = j;
        if (u < 0) { e = GRAFO_DESCONECTADO; break; }
        t.usado[u] = 1;
        for (ListaArco a = g.a; a != NULL; a = a->sig) {
            if (a->origen != t.vertices[u]) continue;
            int v = indiceVertice(&t, a->destino);
            if (!t.usado[v] &&
                (!t.alcanzable[v] || a->costo < t.dist[v])) {
                t.dist[v] = a->costo; t.prev[v] = u;
                t.alcanzable[v] = 1;
            }
        }
    }
    ListaArco arbol = NULL;
    for (int i = 0; i < t.n && e == GRAFO_OK; i++) {
        if (t.prev[i] < 0) continue;
        ListaArco nuevo = malloc(sizeof *nuevo);
        if (nuevo == NULL) { e = GRAFO_MEMORIA; break; }
        *nuevo = (struct NodoA){t.vertices[t.prev[i]],
                    t.vertices[i], (int)t.dist[i], arbol};
        arbol = nuevo;
    }
    if (e != GRAFO_OK) grafo_liberar_arcos(&arbol);
    liberar_trabajo(&t);
    fijar_estado(estado, e);
    return arbol;
}


typedef struct { int *padre; int n; } Conjunto;

static int grafo_encontrar_conjunto(Conjunto *c, int x) {
    int raiz = x;
    while (c->padre[raiz] != raiz) raiz = c->padre[raiz];
    while (c->padre[x] != x) {
        int siguiente = c->padre[x];
        c->padre[x] = raiz; x = siguiente;
    }
    return raiz;
}

static void grafo_unir_conjuntos(Conjunto *c, int x, int y) {
    int a = grafo_encontrar_conjunto(c, x);
    int b = grafo_encontrar_conjunto(c, y);
    if (a != b) c->padre[b] = a;
}

ListaArco grafo_kruskal(Grafo g, GrafoEstado *estado) {
    Trabajo t;
    if (!preparar(g, &t, estado)) return NULL;
    GrafoEstado e = GRAFO_OK;
    int m = grafo_tamano(g);
    Conjunto c = {NULL, t.n};
    ListaArco *aristas = NULL, arbol = NULL;
    if (!grafo_simetrico(g)) e = GRAFO_ARGUMENTO;
    if ((size_t)m > SIZE_MAX / sizeof(ListaArco)) e = GRAFO_RANGO;
    if (e == GRAFO_OK) {
        c.padre = malloc((size_t)t.n * sizeof(int));
        if (m > 0) aristas = malloc((size_t)m * sizeof *aristas);
        if (c.padre == NULL || (m > 0 && aristas == NULL))
            e = GRAFO_MEMORIA;
    }
    int cantidad = 0;
    if (e == GRAFO_OK) {
        for (int i = 0; i < t.n; i++) c.padre[i] = i;
        for (ListaArco a = g.a; a != NULL; a = a->sig)
            aristas[cantidad++] = a;
        for (int i = 0; i < cantidad - 1; i++)
            for (int j = 0; j < cantidad - i - 1; j++)
                if (aristas[j]->costo > aristas[j + 1]->costo) {
                    ListaArco aux = aristas[j];
                    aristas[j] = aristas[j + 1]; aristas[j + 1] = aux;
                }
    }
    int elegidas = 0;
    for (int i = 0; i < cantidad && e == GRAFO_OK; i++) {
        ListaArco a = aristas[i];
        int u = indiceVertice(&t, a->origen);
        int v = indiceVertice(&t, a->destino);

        if (grafo_encontrar_conjunto(&c, u) ==
            grafo_encontrar_conjunto(&c, v)) continue;
        ListaArco nuevo = malloc(sizeof *nuevo);
        if (nuevo == NULL) { e = GRAFO_MEMORIA; break; }
        *nuevo = (struct NodoA){a->origen, a->destino, a->costo, arbol};
        arbol = nuevo; elegidas++;
        grafo_unir_conjuntos(&c, u, v);
    }
    if (e == GRAFO_OK && elegidas != t.n - 1) e = GRAFO_DESCONECTADO;
    if (e != GRAFO_OK) grafo_liberar_arcos(&arbol);
    free(c.padre); free(aristas); liberar_trabajo(&t);
    fijar_estado(estado, e);
    return arbol;
}
