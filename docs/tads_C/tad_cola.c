#include <stdio.h>
#include <stdlib.h>

//------------------------------------------------------------------------
/**
 * @brief Nodo de una lista enlazada para la cola.
 */
struct NodoCola {
    int nro;                      
    struct NodoCola *sgte;       
};


//------------------------------------------------------------------------
/**
 * @brief Estructura que representa una cola con punteros al inicio y al final.
 */
struct Cola {
    struct NodoCola *delante;    
    struct NodoCola *atras;      
};


//------------------------------------------------------------------------
/**
 * @brief Inserta un nuevo elemento al final de la cola.
 * @param q Puntero a la cola.
 * @param valor Valor a encolar.
 */


//------------------------------------------------------------------------
void cola_encolar(struct Cola *q, int valor) {
    if (q == NULL) {
        printf("Error: cola no inicializada.\n");
        return;
    }

    struct NodoCola *aux = (struct NodoCola *) malloc(sizeof(struct NodoCola));
    if (aux == NULL) {
        printf("Error: no se pudo asignar memoria.\n");
        return;
    }

    aux->nro = valor;
    aux->sgte = NULL;

    if (q->delante == NULL) {
        q->delante = aux;  // Primer elemento encolado
    } else {
        q->atras->sgte = aux;
    }
    q->atras = aux;  // Siempre apunta al último
}

//------------------------------------------------------------------------
/**
 * @brief Elimina y devuelve el primer elemento de la cola.
 * @param q Puntero a la cola.
 * @return int Valor desencolado.
 */
int cola_desencolar(struct Cola *q) {
    if (q == NULL || q->delante == NULL) {
        printf("Cola vacía. No se puede desencolar.\n");
        return -1;  // Valor de error
    }

    struct NodoCola *aux = q->delante;
    int num = aux->nro;
    q->delante = aux->sgte;

    if (q->delante == NULL) {
        q->atras = NULL;  // Cola vacía después de desencolar
    }

    free(aux);
    return num;
}

//------------------------------------------------------------------------
/**
 * @brief Muestra todos los elementos de la cola.
 * @param q Cola a mostrar.
 */
void cola_mostrar(struct Cola q) {
    struct NodoCola *aux = q.delante;
    printf("Cola: ");
    while (aux != NULL) {
        printf("%d ", aux->nro);
        aux = aux->sgte;
    }
    printf("\n");
}

//------------------------------------------------------------------------
/**
 * @brief Vacía completamente la cola liberando memoria.
 * @param q Puntero a la cola.
 */
void cola_vaciar(struct Cola *q) {
    struct NodoCola *aux;
    if (q == NULL) {
        return;
    }

    while (q->delante != NULL) {
        aux = q->delante;
        q->delante = aux->sgte;
        free(aux);
    }
    q->delante = NULL;
    q->atras = NULL;
}


//------------------------------------------------------------------------
/**
 * @brief Retorna el valor al cola_frente de la cola sin eliminarlo.
 * @param q Cola de la cual se obtiene el cola_frente.
 * @return Valor en el cola_frente de la cola, o -1 si está vacía.
 */
int cola_frente(struct Cola q) {
    if (q.delante != NULL)
        return q.delante->nro;
    else
        return -1;
}
