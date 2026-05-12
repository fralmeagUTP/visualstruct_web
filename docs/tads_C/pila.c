#include "pila.h"

#include <stdio.h>
#include <stdlib.h>

struct nodo {
    int nro;
    struct nodo *sgte;
};

/**
 * @brief Inicializa una Pila poniéndola en estado vacío.
 * @param[out] pila Puntero a la Pila que se va a inicializar.
 *                  Si es NULL la función no hace nada.
 */
void pila_inicializar(Pila *pila) {
    if (pila == NULL) {
        return;
    }
    pila->tope = NULL;
}

/**
 * @brief Inserta un valor entero en el tope de la pila (push).
 * @param[in,out] pila  Puntero a la Pila destino.
 * @param[in]     valor Valor entero a insertar.
 * @return @c true  si el nodo fue creado e insertado correctamente.
 * @return @c false si @p pila es NULL o @c malloc() falla.
 */
bool pila_push(Pila *pila, int valor) {
    Nodo *aux;
    if (pila == NULL) {
        return false;
    }

    aux = (Nodo *)malloc(sizeof(Nodo));
    if (aux == NULL) {
        return false;
    }

    aux->nro = valor;
    aux->sgte = pila->tope;
    pila->tope = aux;
    return true;
}

/**
 * @brief Extrae el valor del tope de la pila (pop).
 * @param[in,out] pila  Puntero a la Pila de origen.
 * @param[out]    valor Puntero donde se almacenará el valor extraído.
 * @return @c true  si se extrajo un elemento correctamente.
 * @return @c false si @p pila o @p valor son NULL, o la pila está vacía.
 */
bool pila_pop(Pila *pila, int *valor) {
    Nodo *aux;
    if (pila == NULL || pila->tope == NULL || valor == NULL) {
        return false;
    }

    aux = pila->tope;
    *valor = aux->nro;
    pila->tope = aux->sgte;
    free(aux);
    return true;
}

/**
 * @brief Libera todos los nodos de la pila y deja @c tope en NULL.
 * @param[in,out] pila Puntero a la Pila a destruir.
 *                     Si es NULL la función no hace nada.
 */
void pila_destruir(Pila *pila) {
    Nodo *aux;
    if (pila == NULL) {
        return;
    }

    while (pila->tope != NULL) {
        aux = pila->tope;
        pila->tope = aux->sgte;
        free(aux);
    }
}

/**
 * @brief Cuenta el número de elementos presentes en la pila.
 * @param[in] pila Puntero constante a la Pila a consultar.
 * @return Número de nodos en la pila (>= 0).
 *         Retorna 0 si @p pila es NULL.
 */
int pila_contar(const Pila *pila) {
    int cantidad = 0;
    Nodo *actual;
    if (pila == NULL) {
        return 0;
    }

    actual = pila->tope;
    while (actual != NULL) {
        cantidad++;
        actual = actual->sgte;
    }
    return cantidad;
}

/**
 * @brief Indica si la pila no contiene ningún elemento.
 * @param[in] pila Puntero constante a la Pila a consultar.
 * @return @c true  si @p pila es NULL o su puntero @c tope es NULL.
 * @return @c false si la pila tiene al menos un elemento.
 */
bool pila_vacia(const Pila *pila) {
    return pila == NULL || pila->tope == NULL;
}

/**
 * @brief Copia los valores de la pila en un arreglo externo.
 * @param[in]  pila      Puntero constante a la Pila de origen.
 * @param[out] destino   Arreglo donde se almacenarán los valores copiados.
 * @param[in]  capacidad Número máximo de elementos que caben en @p destino.
 * @return Número de elementos efectivamente copiados (0 a @p capacidad).
 *         Retorna 0 si @p pila, @p destino son NULL o @p capacidad <= 0.
 */
int pila_copiar_valores(const Pila *pila, int *destino, int capacidad) {
    int usados = 0;
    Nodo *actual;

    if (pila == NULL || destino == NULL || capacidad <= 0) {
        return 0;
    }

    actual = pila->tope;
    while (actual != NULL && usados < capacidad) {
        destino[usados] = actual->nro;
        usados++;
        actual = actual->sgte;
    }

    return usados;
}

/**
 * @brief Genera una representación textual de la pila.
 * @param[in]  pila      Puntero constante a la Pila a representar.
 * @param[out] destino   Buffer de caracteres donde se escribirá el resultado.
 * @param[in]  capacidad Tamaño en bytes del buffer @p destino.
 */
void pila_formatear(const Pila *pila, char *destino, size_t capacidad) {
    Nodo *actual;
    size_t usado = 0;
    int escritos;

    if (destino == NULL || capacidad == 0) {
        return;
    }

    destino[0] = '\0';

    if (pila == NULL || pila->tope == NULL) {
        snprintf(destino, capacidad, "Pila vacia");
        return;
    }

    actual = pila->tope;
    escritos = snprintf(destino, capacidad, "Tope -> ");
    if (escritos < 0) {
        return;
    }
    usado = (size_t)escritos;

    while (actual != NULL && usado < capacidad) {
        escritos = snprintf(destino + usado, capacidad - usado, "%d", actual->nro);
        if (escritos < 0) {
            return;
        }
        usado += (size_t)escritos;

        actual = actual->sgte;
        if (actual != NULL && usado < capacidad) {
            escritos = snprintf(destino + usado, capacidad - usado, " | ");
            if (escritos < 0) {
                return;
            }
            usado += (size_t)escritos;
        }
    }
}
