#include <stdio.h>
#include <stdlib.h>

/**
 * @brief Nodo de una pila enlazada.
 */
struct NodoPila {
    int nro;                     
    struct NodoPila *sgte;     
};

typedef struct NodoPila* ptrPila;


//---------------------------------------------------------------
/**
 * @brief Apila un nuevo valor en la pila.
 * @param p Puntero a la pila.
 * @param valor Valor entero que se apilará.
 */
void pila_apilar(ptrPila *p, int valor) {
    if (p == NULL) {
        printf("Error: pila no inicializada.\n");
        return;
    }

    ptrPila aux = (ptrPila) malloc(sizeof(struct NodoPila));
    if (aux == NULL) {
        printf("Error: No se pudo asignar memoria.\n");
        return;
    }
    aux->nro = valor;
    aux->sgte = *p;
    *p = aux;
}


//---------------------------------------------------------------
/**
 * @brief Desapila y devuelve el valor en la cima de la pila.
 * @param p Puntero a la pila.
 * @return int Valor desapilado.
 */
int pila_desapilar(ptrPila *p) {
    if (p == NULL || *p == NULL) {
        printf("Pila vacía. No se puede desapilar.\n");
        return -1;  // Valor de error
    }

    ptrPila aux = *p;
    int num = aux->nro;
    *p = aux->sgte;
    free(aux);
    return num;
}

int pila_cima(ptrPila p) {
    return p == NULL ? -1 : p->nro;
}


//---------------------------------------------------------------
/**
 * @brief Muestra todos los elementos de la pila.
 * @param p Pila a mostrar.
 */
void pila_mostrar(ptrPila p) {
    ptrPila aux = p;
    if (aux == NULL) {
        printf("Pila vacia.\n");
        return;
    }

    while (aux != NULL) {
        printf("\t%d\n", aux->nro);
        aux = aux->sgte;
    }
}


//---------------------------------------------------------------
/**
 * @brief Elimina todos los elementos de la pila.
 * @param p Puntero a la pila.
 */
void pila_destruir(ptrPila *p) {
    ptrPila aux;
    if (p == NULL) {
        return;
    }

    while (*p != NULL) {
        aux = *p;
        *p = aux->sgte;
        free(aux);
    }
}
