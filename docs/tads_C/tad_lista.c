#include <stdio.h>
#include <stdlib.h>

/**
 * @brief Nodo de una lista enlazada simple.
 */
struct NodoLista {
    int nro;                     
    struct NodoLista *sgte;      
};

typedef struct NodoLista* Tlista;

static Tlista CrearNodoLista(int valor) {
    Tlista q = (Tlista) malloc(sizeof(struct NodoLista));
    if (q == NULL) {
        printf("Error: no se pudo asignar memoria.\n");
        return NULL;
    }
    q->nro = valor;
    q->sgte = NULL;
    return q;
}


//----------------------------------------------------------------
/**
 * @brief Inserta un nuevo nodo al inicio de la lista.
 * @param lista Puntero a la lista.
 * @param valor Valor entero a insertar.
 */
void lista_insertar_inicio(Tlista *lista, int valor) {
    if (lista == NULL) {
        return;
    }

    Tlista q = CrearNodoLista(valor);
    if (q == NULL) {
        return;
    }

    q->sgte = *lista;
    *lista = q;
}


//---------------------------------------------------------------
/**
 * @brief Inserta un nuevo nodo al final de la lista.
 * @param lista Puntero a la lista.
 * @param valor Valor entero a insertar.
 */
void lista_insertar_final(Tlista *lista, int valor) {
    if (lista == NULL) {
        return;
    }

    Tlista q = CrearNodoLista(valor);
    if (q == NULL) {
        return;
    }

    if (*lista == NULL) {
        *lista = q;
    } else {
        Tlista t = *lista;
        while (t->sgte != NULL) {
            t = t->sgte;
        }
        t->sgte = q;
    }
}

//---------------------------------------------------------------
/**
 * @brief Inserta un nodo en una posición dada.
 * @param lista Puntero a la lista.
 * @param valor Valor a insertar.
 * @param pos Posición base para la inserción.
 */
void lista_insertar_elemento(Tlista *lista, int valor, int pos) {
    if (lista == NULL || pos <= 0) {
        return;
    }

    Tlista q = CrearNodoLista(valor);
    if (q == NULL) {
        return;
    }

    /*
     * Contrato actual:
     * - pos == 1: inserta al inicio.
     * - pos > 1 : inserta despues del nodo en posicion base `pos`.
     */
    if (pos == 1) {
        q->sgte = *lista;
        *lista = q;
        return;
    }

    Tlista t = *lista;
    int i = 1;
    while (t != NULL) {
        if (i == pos) {
            q->sgte = t->sgte;
            t->sgte = q;
            return;
        }
        t = t->sgte;
        i++;
    }

    printf("   Error...Posicion no encontrada..!\n");
    free(q);
}

//---------------------------------------------------------------
/**
 * @brief Busca un elemento en la lista e imprime su posición.
 * @param lista Lista en la que se busca.
 * @param valor Valor a buscar.
 */
void lista_buscar_elemento(Tlista lista, int valor) {
    int i = 1, encontrado = 0;
    Tlista q = lista;

    while (q != NULL) {
        if (q->nro == valor) {
            printf("\n Encontrado en la posicion %d\n", i);
            encontrado = 1;
        }
        q = q->sgte;
        i++;
    }

    if (!encontrado) {
        printf("\n Numero no encontrado..\n");
    }
}


//---------------------------------------------------------------
/**
 * @brief Muestra los elementos de la lista con su posición.
 * @param lista Lista a mostrar.
 */
void lista_mostrar(Tlista lista) {
    int i = 1;
    Tlista aux = lista;
    while (aux != NULL) {
        printf(" %d) %d\n", i, aux->nro);
        aux = aux->sgte;
        i++;
    }
}


//---------------------------------------------------------------
/**
 * @brief Elimina la primera ocurrencia de un valor en la lista.
 * @param lista Puntero a la lista.
 * @param valor Valor a eliminar.
 */
void lista_eliminar_elemento(Tlista *lista, int valor) {
    if (lista == NULL || *lista == NULL) {
        printf(" Valor no encontrado o lista vacia.\n");
        return;
    }

    Tlista p = *lista, ant = NULL;

    while (p != NULL) {
        if (p->nro == valor) {
            if (p == *lista) {
                *lista = p->sgte;
            } else {
                ant->sgte = p->sgte;
            }
            free(p);
            return;
        }
        ant = p;
        p = p->sgte;
    }

    printf(" Valor no encontrado o lista vacia.\n");
}


//---------------------------------------------------------------
/**
 * @brief Elimina todas las ocurrencias de un valor en la lista.
 * @param lista Puntero a la lista.
 * @param valor Valor a eliminar.
 */
void lista_eliminar_repetidos(Tlista *lista, int valor) {
    if (lista == NULL || *lista == NULL) {
        printf("\n\n Valores eliminados..\n");
        return;
    }

    Tlista q = *lista, ant = NULL;

    while (q != NULL) {
        if (q->nro == valor) {
            Tlista temp = q;
            if (q == *lista) {
                *lista = q->sgte;
                q = *lista;
            } else {
                ant->sgte = q->sgte;
                q = ant->sgte;
            }
            free(temp);
        } else {
            ant = q;
            q = q->sgte;
        }
    }
    printf("\n\n Valores eliminados..\n");
}
