#include "cola.h"

#include <stdio.h>
#include <stdlib.h>

struct nodo {
    int nro;
    struct nodo *sgte;
};

/**
 * @brief Inicializa una cola poniéndola en estado vacío.
 * @param cola Puntero a la estructura Cola a inicializar.
 *             Si es NULL la función no hace nada.
 */
void cola_inicializar(Cola *cola) {
    if (cola == NULL) {
        return;
    }
    cola->delante = NULL;
    cola->atras = NULL;
}

/**
 * @brief Inserta un valor al final de la cola (política FIFO).
 * @param cola  Puntero a la Cola destino.
 * @param valor Entero que se desea insertar.
 * @return @c true  si la inserción fue exitosa.
 * @return @c false si @p cola es NULL o no hay memoria disponible.
 */
bool cola_encolar(Cola *cola, int valor) {
    Nodo *aux;
    if (cola == NULL) {
        return false;
    }

    aux = (Nodo *)malloc(sizeof(Nodo));
    if (aux == NULL) {
        return false;
    }

    aux->nro = valor;
    aux->sgte = NULL;

    if (cola->delante == NULL) {
        cola->delante = aux;
    } else {
        cola->atras->sgte = aux;
    }

    cola->atras = aux;
    return true;
}

/**
 * @brief Extrae el elemento del frente de la cola.
 * @param cola  Puntero a la Cola de origen.
 * @param valor Puntero donde se almacenará el valor extraído.
 * @return @c true  si se extrajo un elemento correctamente.
 * @return @c false si @p cola o @p valor son NULL, o la cola está vacía.
 */
bool cola_desencolar(Cola *cola, int *valor) {
    Nodo *aux;
    if (cola == NULL || cola->delante == NULL || valor == NULL) {
        return false;
    }

    aux = cola->delante;
    *valor = aux->nro;
    cola->delante = aux->sgte;
    free(aux);

    if (cola->delante == NULL) {
        cola->atras = NULL;
    }

    return true;
}

/**
 * @brief Elimina todos los elementos de la cola y libera su memoria.
 * @param cola Puntero a la Cola que se desea vaciar.
 *             Si es NULL la función no hace nada.
 */
void cola_vaciar(Cola *cola) {
    Nodo *aux;
    if (cola == NULL) {
        return;
    }

    while (cola->delante != NULL) {
        aux = cola->delante;
        cola->delante = aux->sgte;
        free(aux);
    }

    cola->atras = NULL;
}

/**
 * @brief Indica si la cola no contiene elementos.
 * @param cola Puntero constante a la Cola a consultar.
 * @return @c true  si @p cola es NULL o no tiene nodos.
 * @return @c false si contiene al menos un elemento.
 */
bool cola_vacia(const Cola *cola) {
    return cola == NULL || cola->delante == NULL;
}

/**
 * @brief Cuenta el número de elementos en la cola.
 * @param cola Puntero constante a la Cola.
 * @return Número de nodos presentes, o 0 si @p cola es NULL.
 */
int cola_contar(const Cola *cola) {
    int cantidad = 0;
    Nodo *actual;
    if (cola == NULL) {
        return 0;
    }

    actual = cola->delante;
    while (actual != NULL) {
        cantidad++;
        actual = actual->sgte;
    }
    return cantidad;
}

/**
 * @brief Copia los valores de la cola en un arreglo externo.
 * @param cola      Puntero constante a la Cola de origen.
 * @param destino   Arreglo donde se almacenarán los valores copiados.
 * @param capacidad Tamaño máximo del arreglo @p destino.
 * @return Número de elementos efectivamente copiados,
 *         o 0 si algún parámetro es inválido.
 */
int cola_copiar_valores(const Cola *cola, int *destino, int capacidad) {
    int usados = 0;
    Nodo *actual;

    if (cola == NULL || destino == NULL || capacidad <= 0) {
        return 0;
    }

    actual = cola->delante;
    while (actual != NULL && usados < capacidad) {
        destino[usados] = actual->nro;
        usados++;
        actual = actual->sgte;
    }

    return usados;
}

/**
 * @brief Genera una representación textual de la cola.
 *
 * @param cola      Puntero constante a la Cola a representar.
 * @param destino   Buffer de caracteres donde se escribirá el resultado.
 * @param capacidad Tamaño en bytes del buffer @p destino.
 *                  Si es 0 o @p destino es NULL la función no hace nada.
 */
void cola_formatear(const Cola *cola, char *destino, size_t capacidad) {
    Nodo *actual;
    size_t usado = 0;
    int escritos;

    if (destino == NULL || capacidad == 0) {
        return;
    }

    destino[0] = '\0';

    if (cola == NULL || cola->delante == NULL) {
        snprintf(destino, capacidad, "Cola vacia");
        return;
    }

    actual = cola->delante;
    escritos = snprintf(destino, capacidad, "Frente -> ");
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

    if (usado < capacidad) {
        snprintf(destino + usado, capacidad - usado, " <- Final");
    }
}
