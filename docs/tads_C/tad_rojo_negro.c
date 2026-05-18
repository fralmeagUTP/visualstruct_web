#include <stdio.h>
#include <stdlib.h>

#ifdef _WIN32
#include <windows.h>
#endif

#define ROJO 'r'
#define NEGRO 'n'

/**
 * @struct nodoRBT
 * @brief Estructura para un nodo de Árbol Rojo-Negro.
 */
typedef struct nodoRBT {
    int nro;                   
    char rbt_color;               
    struct nodoRBT *padre;     
    struct nodoRBT *izq;       
    struct nodoRBT *der;       
} nodoRBT;

typedef struct nodoRBT *RBT;

/* Prototipos de funciones */
RBT rbt_abuelo(RBT n);
RBT rbt_tio(RBT n);
void rbt_rotar_dcha(RBT *r, RBT nodoRBT);
void rbt_rotar_izda(RBT *r, RBT nodoRBT);
void rbt_insercion_caso1(RBT n, RBT *arbol);
void rbt_insercion_caso2(RBT n, RBT *arbol);
void rbt_insercion_caso3(RBT n, RBT *arbol);
void rbt_insercion_caso4(RBT n, RBT *arbol);
void rbt_insercion_caso5(RBT n, RBT *arbol);


/**
 * @brief Configura el rbt_color del texto en la consola (Windows).
 * @param c Código de rbt_color (ej: 12=rojo, 8=gris oscuro, 15=blanco).
 */
void rbt_color(int c) {
#ifdef _WIN32
    SetConsoleTextAttribute(GetStdHandle(STD_OUTPUT_HANDLE), c);
#else
    (void)c;
#endif
}


/**
 * @brief Busca un valor en el árbol Rojo-Negro.
 * @param nodoRBT Raíz del árbol.
 * @param dato Valor a rbt_buscar.
 * @return Puntero al nodo encontrado o NULL si no existe.
 */
RBT rbt_buscar(RBT nodoRBT, int dato) {
    RBT actual = nodoRBT;
    if (nodoRBT == NULL) {
        printf("\n\tEl arbol esta vacio\n\n");
        return NULL;
    }
    while (actual != NULL) {
        if (dato == actual->nro) {
            printf("\n\tEl numero %d existe en el arbol\n", dato);
            return actual;
        } else if (dato < actual->nro)
            actual = actual->izq;
        else if (dato > actual->nro)
            actual = actual->der;
    }
    printf("\n\tEl numero %d NO existe en el arbol\n", dato);
    return NULL;
}

/**
 * @brief Muestra el árbol visualmente (rotado 90°) con colores.
 * @param arbol Raíz del árbol.
 * @param n Nivel de profundidad (usar 0 al invocar).
 */
void rbt_verArbol(RBT arbol, int n) {
    int i;
    if (arbol == NULL)
        return;
    rbt_verArbol(arbol->der, n + 1);

    for (i = 0; i < n; i++)
        printf("   ");

    if (arbol->rbt_color == ROJO)
        rbt_color(12);
    else if (arbol->rbt_color == NEGRO)
        rbt_color(8);
    printf("%d\n", arbol->nro);

    rbt_verArbol(arbol->izq, n + 1);
    rbt_color(15);
}


/**
 * @brief Devuelve el rbt_abuelo de un nodo.
 * @param n Nodo dado.
 * @return Puntero al rbt_abuelo o NULL si no existe.
 */
RBT rbt_abuelo(RBT n) {
    if ((n != NULL) && (n->padre != NULL))
        return n->padre->padre;
    else
        return NULL;
}

/**
 * @brief Devuelve el tío de un nodo (hermano del padre).
 * @param n Nodo dado.
 * @return Puntero al tío o NULL si no existe.
 */
RBT rbt_tio(RBT n) {
    RBT a = rbt_abuelo(n);
    if (a == NULL)
        return NULL;
    if (n->padre == a->izq)
        return a->der;
    else
        return a->izq;
}

/**
 * @brief Rotación simple derecha.
 * @param r Referencia a la raíz del árbol.
 * @param nodoRBT Nodo sobre el que se aplica la rotación.
 */
void rbt_rotar_dcha(RBT *r, RBT nodoRBT) {
    if (r == NULL || nodoRBT == NULL || nodoRBT->izq == NULL) {
        return;
    }

    RBT padre = nodoRBT->padre;
    RBT A = nodoRBT;
    RBT B = A->izq;
    RBT C = B->der;
    if (padre != NULL) {
        if (padre->der == A)
            padre->der = B;
        else
            padre->izq = B;
    } else
        *r = B;

    A->izq = C;
    B->der = A;
    A->padre = B;
    if (C)
        C->padre = A;
    B->padre = padre;
}

/**
 * @brief Rotación simple izquierda.
 * @param r Referencia a la raíz del árbol.
 * @param nodoRBT Nodo sobre el que se aplica la rotación.
 */
void rbt_rotar_izda(RBT *r, RBT nodoRBT) {
    if (r == NULL || nodoRBT == NULL || nodoRBT->der == NULL) {
        return;
    }

    RBT padre = nodoRBT->padre;
    RBT A = nodoRBT;
    RBT B = A->der;
    RBT C = B->izq;
    if (padre != NULL) {
        if (padre->der == A)
            padre->der = B;
        else
            padre->izq = B;
    } else
        *r = B;

    A->der = C;
    B->izq = A;
    A->padre = B;
    if (C)
        C->padre = A;
    B->padre = padre;
}

/**
 * @brief Caso 5 de inserción: rotación final y recoloreo.
 * @param n Nodo insertado.
 * @param arbol Referencia a la raíz del árbol.
 */
void rbt_insercion_caso5(RBT n, RBT *arbol) {
    RBT a = rbt_abuelo(n);
    n->padre->rbt_color = NEGRO;
    a->rbt_color = ROJO;
    if ((n == n->padre->izq) && (n->padre == a->izq)) {
        rbt_rotar_dcha(arbol, a);
    } else {
        rbt_rotar_izda(arbol, a);
    }
}

/**
 * @brief Caso 4 de inserción: ajuste para alinear nodo, padre y rbt_abuelo.
 * @param n Nodo insertado (puede cambiar tras rotación).
 * @param arbol Referencia a la raíz del árbol.
 */
void rbt_insercion_caso4(RBT n, RBT *arbol) {
    RBT a = rbt_abuelo(n);
    RBT nuevo_n = n;

    if ((n == n->padre->der) && (n->padre == a->izq)) {
        rbt_rotar_izda(arbol, n->padre);
        nuevo_n = n->izq;
    } else if ((n == n->padre->izq) && (n->padre == a->der)) {
        rbt_rotar_dcha(arbol, n->padre);
        nuevo_n = n->der;
    }
    rbt_insercion_caso5(nuevo_n, arbol);
}

/**
 * @brief Caso 3 de inserción: tío rojo o tío negro.
 * @param n Nodo insertado.
 * @param arbol Referencia a la raíz del árbol.
 */
void rbt_insercion_caso3(RBT n, RBT *arbol) {
    RBT t = rbt_tio(n);
    RBT a;

    if ((t != NULL) && (t->rbt_color == ROJO)) {
        n->padre->rbt_color = NEGRO;
        t->rbt_color = NEGRO;
        a = rbt_abuelo(n);
        a->rbt_color = ROJO;
        rbt_insercion_caso1(a, arbol);
    } else {
        rbt_insercion_caso4(n, arbol);
    }
}

/**
 * @brief Caso 2 de inserción: si padre es negro, árbol válido.
 * @param n Nodo insertado.
 * @param arbol Referencia a la raíz del árbol.
 */
void rbt_insercion_caso2(RBT n, RBT *arbol) {
    if (n->padre->rbt_color == NEGRO)
        return;
    else
        rbt_insercion_caso3(n, arbol);
}

/**
 * @brief Caso 1 de inserción: si es raíz, pintar de negro.
 * @param n Nodo insertado.
 * @param arbol Referencia a la raíz del árbol.
 */
void rbt_insercion_caso1(RBT n, RBT *arbol) {
    if (n->padre == NULL)
        n->rbt_color = NEGRO;
    else
        rbt_insercion_caso2(n, arbol);
}

/**
 * @brief Inserta un valor en el árbol Rojo-Negro.
 * @param arbol Referencia a la raíz del árbol.
 * @param dato Valor a rbt_insertar.
 */
void rbt_insertar(RBT *arbol, int dato) {
    if (arbol == NULL) {
        return;
    }

    RBT padre = NULL;
    RBT actual = *arbol;
    while (actual != NULL && dato != actual->nro) {
        padre = actual;
        if (dato < actual->nro)
            actual = actual->izq;
        else if (dato > actual->nro)
            actual = actual->der;
    }
    if (actual != NULL)
        return;
    actual = malloc(sizeof(struct nodoRBT));
    if (actual == NULL) {
        return;
    }
    actual->nro = dato;
    actual->izq = actual->der = NULL;
    actual->padre = padre;
    actual->rbt_color = ROJO;
    if (padre == NULL) {
        *arbol = actual;
    } else if (dato < padre->nro) {
        padre->izq = actual;
    } else if (dato > padre->nro) {
        padre->der = actual;
    }
    rbt_insercion_caso1(actual, arbol);
    printf("\tEl numero ha sido insertado\n");
}

/* ====== Eliminacion con rebalanceo (algoritmo tipo CLRS), sin NIL ====== */
/**
 * @brief Devuelve el rbt_color de un nodo, considerando NULL como negro.
 * @param n Nodo a consultar (puede ser NULL).
 * @return 'n' si n es NULL o el nodo es negro; 'r' si el nodo es rojo.
 */
static char colorOf(RBT n) { return (n == NULL) ? NEGRO : n->rbt_color; }

/**
 * @brief Reemplaza el subárbol en u por el subárbol v.
 * @param root Referencia a la raíz del árbol.
 * @param u Raíz del subárbol a reemplazar.
 * @param v Subárbol que ocupará el lugar de u (puede ser NULL).
 */
static void transplantar(RBT *root, RBT u, RBT v) {
    if (u->padre == NULL) {
        *root = v;
    } else if (u == u->padre->izq) {
        u->padre->izq = v;
    } else {
        u->padre->der = v;
    }
    if (v) v->padre = u->padre;
}

/**
 * @brief Retorna el nodo con el valor mínimo de un subárbol.
 * @param n Raíz del subárbol (no NULL si se espera un resultado).
 * @return Puntero al nodo mínimo, o NULL si n es NULL.
 */
static RBT minimo(RBT n) {
    while (n && n->izq) n = n->izq;
    return n;
}

/**
 * @brief Restaura las propiedades Rojo-Negro tras una eliminación.
 * @param root Referencia a la raíz del árbol.
 * @param x Nodo que sube en el fix-up (puede ser NULL).
 * @param x_parent Padre de x (debe ser válido cuando x es NULL).
 */
static void arreglarEliminacion(RBT *root, RBT x, RBT x_parent) {
    /* Mientras x no sea la raiz y sea negro, corregimos desde abajo hacia arriba */
    while (x != *root && colorOf(x) == NEGRO) {
        if (x_parent == NULL) {
            break;
        }

        int es_izq = (x == (x_parent ? x_parent->izq : NULL));
        RBT w = x_parent ? (es_izq ? x_parent->der : x_parent->izq) : NULL; /* hermano de x */
        RBT w_izq = w ? w->izq : NULL;
        RBT w_der = w ? w->der : NULL;

        if (es_izq) {
            /* CASO 1 (simétrico): w rojo -> rotar izda en padre */
            if (colorOf(w) == ROJO) {
                w->rbt_color = NEGRO;
                x_parent->rbt_color = ROJO;
                rbt_rotar_izda(root, x_parent);
                w = x_parent->der; w_izq = w ? w->izq : NULL; w_der = w ? w->der : NULL;
            }
            /* CASO 2: w negro y sus dos hijos negros -> recolorear w y subir */
            if (colorOf(w_izq) == NEGRO && colorOf(w_der) == NEGRO) {
                if (w) w->rbt_color = ROJO;
                x = x_parent;
                x_parent = x ? x->padre : NULL;
            } else {
                /* CASO 3: w negro, hijo derecho negro, hijo izquierdo rojo -> rotar dcha en w */
                if (colorOf(w_der) == NEGRO) {
                    if (w_izq) w_izq->rbt_color = NEGRO;
                    if (w) { w->rbt_color = ROJO; rbt_rotar_dcha(root, w); }
                    w = x_parent ? x_parent->der : NULL; w_izq = w ? w->izq : NULL; w_der = w ? w->der : NULL;
                }
                /* CASO 4: w negro, hijo derecho rojo -> rotar izda en padre y recolorear */
                if (w) w->rbt_color = colorOf(x_parent);
                x_parent->rbt_color = NEGRO;
                if (w_der) w_der->rbt_color = NEGRO;
                rbt_rotar_izda(root, x_parent);
                x = *root; /* terminamos */
            }
        } else {
            /* Lado derecho: casos espejo */
            if (colorOf(w) == ROJO) {
                w->rbt_color = NEGRO;
                x_parent->rbt_color = ROJO;
                rbt_rotar_dcha(root, x_parent);
                w = x_parent ? x_parent->izq : NULL; w_izq = w ? w->izq : NULL; w_der = w ? w->der : NULL;
            }
            if (colorOf(w_der) == NEGRO && colorOf(w_izq) == NEGRO) {
                if (w) w->rbt_color = ROJO;
                x = x_parent;
                x_parent = x ? x->padre : NULL;
            } else {
                if (colorOf(w_izq) == NEGRO) {
                    if (w_der) w_der->rbt_color = NEGRO;
                    if (w) { w->rbt_color = ROJO; rbt_rotar_izda(root, w); }
                    w = x_parent ? x_parent->izq : NULL; w_izq = w ? w->izq : NULL; w_der = w ? w->der : NULL;
                }
                if (w) w->rbt_color = colorOf(x_parent);
                x_parent->rbt_color = NEGRO;
                if (w_izq) w_izq->rbt_color = NEGRO;
                rbt_rotar_dcha(root, x_parent);
                x = *root;
            }
        }
    }
    if (x) x->rbt_color = NEGRO;
}

/**
 * @brief Elimina un valor del árbol Rojo-Negro (con rebalanceo).
 * @param arbol Referencia a la raíz del árbol.
 * @param key Clave a eliminar.
 */
void rbt_eliminar(RBT *arbol, int key) {
    RBT z = *arbol;
    while (z != NULL && z->nro != key) {
        if (key < z->nro) z = z->izq; else z = z->der;
    }
    if (z == NULL) return; /* no encontrado */

    RBT y = z;
    char y_color_original = y->rbt_color;
    RBT x = NULL;
    RBT x_parent = NULL;

    if (z->izq == NULL) {
        x = z->der;
        x_parent = z->padre;
        transplantar(arbol, z, z->der);
    } else if (z->der == NULL) {
        x = z->izq;
        x_parent = z->padre;
        transplantar(arbol, z, z->izq);
    } else {
        y = minimo(z->der);
        y_color_original = y->rbt_color;
        x = y->der;
        if (y->padre == z) {
            x_parent = y;
        } else {
            transplantar(arbol, y, y->der);
            x_parent = y->padre;
            y->der = z->der;
            y->der->padre = y;
        }
        transplantar(arbol, z, y);
        y->izq = z->izq;
        y->izq->padre = y;
        y->rbt_color = z->rbt_color;
    }

    free(z);

    if (y_color_original == NEGRO) {
        arreglarEliminacion(arbol, x, x_parent);
    }
    if (*arbol) (*arbol)->rbt_color = NEGRO;
}

/**
 * @brief Libera toda la memoria del árbol Rojo-Negro (postorden).
 * @param arbol Raíz del árbol a liberar.
 */
void rbt_liberar(RBT arbol) {
    if (arbol == NULL)
        return;
    rbt_liberar(arbol->izq);
    rbt_liberar(arbol->der);
    free(arbol);
}


