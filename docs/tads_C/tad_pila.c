/**
 * @file tad_pila.c
 * @brief Implementación del TAD Pila LIFO.
 */

#include <stdio.h>
#include <stdlib.h>

/**
 * @brief Nodo de una pila enlazada.
 */
struct NodoPila {
    int nro; /**< Dato entero almacenado. */
    struct NodoPila *sgte; /**< Enlace al siguiente nodo. */
};

/** @brief Puntero a nodo o cima de pila; NULL representa pila vacía. */
typedef struct NodoPila* ptrPila;


//---------------------------------------------------------------

/**
 * @brief Reserva un nodo y lo publica como nueva cima.
 * @param[in,out] p Direccion prestada de la cabeza; NULL se diagnostica sin escritura.
 * @param[in] valor Entero a almacenar, incluido -1.
 * @pre Si p no es NULL, *p es NULL o una lista propia valida, viva y aciclica.
 * @note Fallo malloc imprime diagnostico y conserva *p. Retorno void no comunica exito.
 * @note El nodo nuevo pertenece a la pila; destruir o desapilar lo libera. No inicializa una cabeza indeterminada.
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
 * @brief Copia el dato de cima, actualiza la cabeza y libera el nodo retirado.
 * @param[in,out] p Direccion prestada de cabeza o NULL.
 * @return Dato retirado; -1 ante p NULL o *p NULL con diagnostico en stdout. -1 tambien es un dato valido.
 * @pre Si hay nodos, deben ser vivos, propios y formar una lista aciclica.
 * @note No reserva memoria. Los aliases al nodo retirado quedan invalidos. Comprobar no vacia antes de usar el retorno como dato.
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

/**
 * @brief Consulta el dato de cima sin cambiar enlaces.
 * @param[in] p Cabeza prestada viva o NULL.
 * @return Dato de cima o -1 si p es NULL; -1 no distingue vacio de dato almacenado.
 * @note No reserva, libera ni imprime. No valida punteros colgantes.
 */
int pila_cima(ptrPila p) {
    return p == NULL ? -1 : p->nro;
}


//---------------------------------------------------------------

/**
 * @brief Imprime los datos de cima a fondo sin modificar nodos.
 * @param[in] p Lista prestada viva, aciclica o NULL.
 * @note NULL imprime el mensaje de pila vacia; cada dato se imprime con tabulacion y salto de linea. No reserva ni libera.
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
 * @brief Libera todos los nodos y deja la cabeza en NULL.
 * @param[in,out] p Direccion de lista propia viva y aciclica; NULL se ignora.
 * @note No reserva ni imprime. Los aliases a nodos liberados dejan de ser validos; una copia externa de la cabeza no se actualiza.
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
