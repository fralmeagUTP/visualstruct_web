#include "lista_circular.h"

#include <stdio.h>
#include <stdlib.h>

struct lcir_nodo {
    int valor;
    struct lcir_nodo *sgte;
};

/**
 * @brief Crea un nuevo nodo para la lista circular.
 * @param[in] valor Entero a almacenar en el nuevo nodo.
 * @return Puntero al nuevo nodo, o NULL si la asignación de memoria falla.
 */
static LCirNodo *lcir_crear_nodo(int valor) {
    LCirNodo *nodo = (LCirNodo *)malloc(sizeof(LCirNodo));
    if (nodo == NULL) {
        return NULL;
    }
    nodo->valor = valor;
    nodo->sgte = NULL;
    return nodo;
}

/**
 * @brief Inicializa la estructura principal de la lista circular vacía.
 * @param[in,out] lista Puntero a la estructura de la lista circular.
 */
void lcir_inicializar(ListaCircular *lista) {
    if (lista == NULL) {
        return;
    }
    lista->cabeza = NULL;
    lista->cola = NULL;
}

/**
 * @brief Inserta un nuevo elemento al inicio de la lista circular.
 * @param[in,out] lista Puntero a la lista.
 * @param[in]     valor Dato a insertar.
 * @return true si se insertó con éxito, false en caso de error.
 */
bool lcir_insertar_inicio(ListaCircular *lista, int valor) {
    LCirNodo *nuevo;

    if (lista == NULL) {
        return false;
    }

    nuevo = lcir_crear_nodo(valor);
    if (nuevo == NULL) {
        return false;
    }

    if (lista->cabeza == NULL) {
        nuevo->sgte = nuevo;
        lista->cabeza = nuevo;
        lista->cola = nuevo;
        return true;
    }

    nuevo->sgte = lista->cabeza;
    lista->cola->sgte = nuevo;
    lista->cabeza = nuevo;
    return true;
}

/**
 * @brief Inserta un nuevo elemento al final de la lista circular.
 * @param[in,out] lista Puntero a la lista.
 * @param[in]     valor Dato a insertar.
 * @return true si se insertó con éxito, false en caso de error.
 */
bool lcir_insertar_final(ListaCircular *lista, int valor) {
    LCirNodo *nuevo;

    if (lista == NULL) {
        return false;
    }

    nuevo = lcir_crear_nodo(valor);
    if (nuevo == NULL) {
        return false;
    }

    if (lista->cabeza == NULL) {
        nuevo->sgte = nuevo;
        lista->cabeza = nuevo;
        lista->cola = nuevo;
        return true;
    }

    nuevo->sgte = lista->cabeza;
    lista->cola->sgte = nuevo;
    lista->cola = nuevo;
    return true;
}

/**
 * @brief Busca un valor y guarda las posiciones (índices basados en 1) en las que aparece.
 * @param[in]  lista     Puntero constante a la lista.
 * @param[in]  valor     Elemento a buscar.
 * @param[out] destino   Arreglo donde se escribirán las posiciones (1-based).
 * @param[in]  capacidad Capacidad máxima del arreglo de posiciones.
 * @return El número de apariciones de dicho valor en la lista.
 */
int lcir_buscar_posiciones(const ListaCircular *lista, int valor, int *destino, int capacidad) {
    LCirNodo *actual;
    int encontrados = 0;
    int pos = 1;

    if (lista == NULL || lista->cabeza == NULL) {
        return 0;
    }

    actual = lista->cabeza;
    do {
        if (actual->valor == valor) {
            if (destino != NULL && encontrados < capacidad) {
                destino[encontrados] = pos;
            }
            encontrados++;
        }
        actual = actual->sgte;
        pos++;
    } while (actual != lista->cabeza);

    return encontrados;
}

/**
 * @brief Elimina el primer nodo que contenga el valor especificado.
 * @param[in,out] lista Puntero a la lista.
 * @param[in]     valor Elemento a remover de la lista.
 * @return true si el nodo fue eliminado, false si no se encontró.
 */
bool lcir_eliminar_primero(ListaCircular *lista, int valor) {
    LCirNodo *actual;
    LCirNodo *anterior;

    if (lista == NULL || lista->cabeza == NULL) {
        return false;
    }

    actual = lista->cabeza;
    anterior = lista->cola;
    do {
        if (actual->valor == valor) {
            if (actual == lista->cabeza && actual == lista->cola) {
                free(actual);
                lista->cabeza = NULL;
                lista->cola = NULL;
                return true;
            }

            anterior->sgte = actual->sgte;
            if (actual == lista->cabeza) {
                lista->cabeza = actual->sgte;
            }
            if (actual == lista->cola) {
                lista->cola = anterior;
            }
            free(actual);
            return true;
        }
        anterior = actual;
        actual = actual->sgte;
    } while (actual != lista->cabeza);

    return false;
}

/**
 * @brief Invierte la dirección de la lista circular internamente.
 * @param[in,out] lista Puntero a la lista.
 */
void lcir_invertir(ListaCircular *lista) {
    LCirNodo *prev;
    LCirNodo *curr;
    LCirNodo *next;
    LCirNodo *old_head;

    if (lista == NULL || lista->cabeza == NULL || lista->cabeza == lista->cola) {
        return;
    }

    prev = lista->cola;
    curr = lista->cabeza;
    do {
        next = curr->sgte;
        curr->sgte = prev;
        prev = curr;
        curr = next;
    } while (curr != lista->cabeza);

    old_head = lista->cabeza;
    lista->cabeza = lista->cola;
    lista->cola = old_head;
}

/**
 * @brief Comprueba si la lista circular está vacía.
 * @param[in] lista Puntero constante a la lista.
 * @return true si está vacía, false si contiene al menos un elemento.
 */
bool lcir_vacia(const ListaCircular *lista) {
    return lista == NULL || lista->cabeza == NULL;
}

/**
 * @brief Cuenta la cantidad de nodos de la lista circular.
 * @param[in] lista Puntero constante a la lista.
 * @return La cantidad de elementos, o 0 si está vacía.
 */
int lcir_contar(const ListaCircular *lista) {
    LCirNodo *actual;
    int cantidad = 0;

    if (lista == NULL || lista->cabeza == NULL) {
        return 0;
    }

    actual = lista->cabeza;
    do {
        cantidad++;
        actual = actual->sgte;
    } while (actual != lista->cabeza);

    return cantidad;
}

/**
 * @brief Copia secuencialmente los valores de la lista a un arreglo.
 * @param[in]  lista     Puntero constante a la lista.
 * @param[out] destino   Arreglo donde se copiarán los valores.
 * @param[in]  capacidad Número máximo de elementos que puede almacenar el destino.
 * @return Cantidad de elementos copiados de manera exitosa.
 */
int lcir_copiar_valores(const ListaCircular *lista, int *destino, int capacidad) {
    LCirNodo *actual;
    int usados = 0;

    if (lista == NULL || lista->cabeza == NULL || destino == NULL || capacidad <= 0) {
        return 0;
    }

    actual = lista->cabeza;
    do {
        if (usados >= capacidad) {
            break;
        }
        destino[usados] = actual->valor;
        usados++;
        actual = actual->sgte;
    } while (actual != lista->cabeza);

    return usados;
}

/**
 * @brief Genera una representación textual de la lista para imprimir.
 * @param[in]  lista     Puntero constante a la lista.
 * @param[out] destino   Buffer destino de la cadena resultante.
 * @param[in]  capacidad Tamaño del buffer destino.
 */
void lcir_formatear(const ListaCircular *lista, char *destino, size_t capacidad) {
    LCirNodo *actual;
    size_t usado = 0;
    int escritos;
    int pos = 1;

    if (destino == NULL || capacidad == 0) {
        return;
    }

    destino[0] = '\0';
    if (lista == NULL || lista->cabeza == NULL) {
        snprintf(destino, capacidad, "Lista circular vacia");
        return;
    }

    actual = lista->cabeza;
    escritos = snprintf(destino, capacidad, "HEAD -> ");
    if (escritos < 0) {
        return;
    }
    usado = (size_t)escritos;

    do {
        escritos = snprintf(destino + usado, capacidad - usado, "[%d]=%d", pos, actual->valor);
        if (escritos < 0) {
            return;
        }
        usado += (size_t)escritos;
        actual = actual->sgte;
        pos++;

        if (actual != lista->cabeza && usado < capacidad) {
            escritos = snprintf(destino + usado, capacidad - usado, " -> ");
            if (escritos < 0) {
                return;
            }
            usado += (size_t)escritos;
        }
    } while (actual != lista->cabeza && usado < capacidad);

    if (usado < capacidad) {
        snprintf(destino + usado, capacidad - usado, " -> (vuelve a HEAD)");
    }
}

/**
 * @brief Libera la memoria de todos los nodos de la lista y la limpia.
 * @param[in,out] lista Puntero a la lista.
 */
void lcir_destruir(ListaCircular *lista) {
    LCirNodo *actual;
    LCirNodo *next;

    if (lista == NULL || lista->cabeza == NULL) {
        return;
    }

    actual = lista->cabeza->sgte;
    while (actual != NULL && actual != lista->cabeza) {
        next = actual->sgte;
        free(actual);
        actual = next;
    }
    free(lista->cabeza);
    lista->cabeza = NULL;
    lista->cola = NULL;
}
