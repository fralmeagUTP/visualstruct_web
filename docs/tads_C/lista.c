#include "lista.h"

#include <stdio.h>
#include <stdlib.h>

struct nodo {
    int nro;
    struct nodo *sgte;
};

static Nodo *crear_nodo(int valor) {
    Nodo *q = (Nodo *)malloc(sizeof(Nodo));
    if (q == NULL) {
        return NULL;
    }
    q->nro = valor;
    q->sgte = NULL;
    return q;
}

/**
 * @brief Inicializa una Lista poniéndola en estado vacío.
 * @param[out] lista Puntero a la Lista que se va a inicializar.
 *                   Si es NULL la función no hace nada.
 */
void lista_inicializar(Lista *lista) {
    if (lista == NULL) {
        return;
    }
    lista->cabeza = NULL;
}

/**
 * @brief Inserta un valor al inicio de la lista.
 * @param[in,out] lista Puntero a la Lista destino.
 * @param[in]     valor Valor entero a insertar.
 * @return @c true  si la inserción fue exitosa.
 * @return @c false si @p lista es NULL o @c malloc() falla.
 */
 bool lista_insertar_inicio(Lista *lista, int valor) {
    Nodo *q;
    if (lista == NULL) {
        return false;
    }

    q = crear_nodo(valor);
    if (q == NULL) {
        return false;
    }

    q->sgte = lista->cabeza;
    lista->cabeza = q;
    return true;
}

/**
 * @brief Inserta un valor al final de la lista.
 * @param[in,out] lista Puntero a la Lista destino.
 * @param[in]     valor Valor entero a insertar.
 * @return @c true  si la inserción fue exitosa.
 * @return @c false si @p lista es NULL o @c malloc() falla.
 */
 bool lista_insertar_final(Lista *lista, int valor) {
    Nodo *q;
    Nodo *t;

    if (lista == NULL) {
        return false;
    }

    q = crear_nodo(valor);
    if (q == NULL) {
        return false;
    }

    if (lista->cabeza == NULL) {
        lista->cabeza = q;
        return true;
    }

    t = lista->cabeza;
    while (t->sgte != NULL) {
        t = t->sgte;
    }
    t->sgte = q;
    return true;
}

/**
 * @brief Inserta un valor exactamente en la posición indicada (1-based).
 * @param[in,out] lista Puntero a la Lista destino.
 * @param[in]     valor Valor entero a insertar.
 * @param[in]     pos   Posición (1-based) exacta en la cual insertar.
 * @return @c true  si se insertó correctamente.
 * @return @c false si @p lista es NULL, @p pos < 1, la posición
 *                  excede el tamaño actual + 1, o falla malloc.
 */
bool lista_insertar_posicion(Lista *lista, int valor, int pos) {
    Nodo *q;
    Nodo *actual;
    int i;

    if (lista == NULL || pos < 1) {
        return false;
    }

    if (pos == 1) {
        return lista_insertar_inicio(lista, valor);
    }

    actual = lista->cabeza;
    // Buscar el nodo en pos - 1
    for (i = 1; actual != NULL && i < pos - 1; i++) {
        actual = actual->sgte;
    }

    // Si actual es NULL, pos > N + 1, es decir, la posicion no es valida.
    if (actual == NULL) {
        return false;
    }

    q = crear_nodo(valor);
    if (q == NULL) {
        return false;
    }

    q->sgte = actual->sgte;
    actual->sgte = q;

    return true;
}

/**
 * @brief Busca un valor y devuelve las posiciones (1-based) donde aparece.
 * @param[in]  lista     Puntero constante a la Lista.
 * @param[in]  valor     Valor entero a buscar.
 * @param[out] destino   Arreglo donde se almacenan las posiciones encontradas.
 *                       Puede ser NULL si solo se desea contar.
 * @param[in]  capacidad Tamaño máximo del arreglo @p destino.
 * @return Número total de coincidencias encontradas en la lista.
 *         Retorna 0 si @p lista es NULL.
 */
int lista_buscar_posiciones(const Lista *lista, int valor, int *destino, int capacidad) {
    Nodo *q;
    int i = 1;
    int encontrados = 0;

    if (lista == NULL) {
        return 0;
    }

    q = lista->cabeza;
    while (q != NULL) {
        if (q->nro == valor) {
            if (destino != NULL && encontrados < capacidad) {
                destino[encontrados] = i;
            }
            encontrados++;
        }
        q = q->sgte;
        i++;
    }

    return encontrados;
}

/**
 * @brief Elimina la primera ocurrencia de un valor en la lista.
 * @param[in,out] lista Puntero a la Lista.
 * @param[in]     valor Valor entero a eliminar.
 * @return @c true  si se encontró y eliminó el nodo.
 * @return @c false si @p lista es NULL o el valor no existe.
 */
bool lista_eliminar_primero(Lista *lista, int valor) {
    Nodo *p;
    Nodo *ant;

    if (lista == NULL) {
        return false;
    }

    p = lista->cabeza;
    ant = NULL;
    while (p != NULL) {
        if (p->nro == valor) {
            if (ant == NULL) {
                lista->cabeza = p->sgte;
            } else {
                ant->sgte = p->sgte;
            }
            free(p);
            return true;
        }
        ant = p;
        p = p->sgte;
    }

    return false;
}

/**
 * @brief Elimina todas las ocurrencias de un valor en la lista.
 * @param[in,out] lista Puntero a la Lista.
 * @param[in]     valor Valor entero a eliminar.
 * @return Número de nodos eliminados.
 *         Retorna 0 si @p lista es NULL o el valor no existe.
 */
int lista_eliminar_todos(Lista *lista, int valor) {
    Nodo *q;
    Nodo *ant;
    Nodo *tmp;
    int eliminados = 0;

    if (lista == NULL) {
        return 0;
    }

    q = lista->cabeza;
    ant = NULL;
    while (q != NULL) {
        if (q->nro == valor) {
            tmp = q;
            if (ant == NULL) {
                lista->cabeza = q->sgte;
                q = lista->cabeza;
            } else {
                ant->sgte = q->sgte;
                q = ant->sgte;
            }
            free(tmp);
            eliminados++;
        } else {
            ant = q;
            q = q->sgte;
        }
    }

    return eliminados;
}

/**
 * @brief Invierte el orden de todos los nodos de la lista.
 * @param[in,out] lista Puntero a la Lista a invertir.
 *                      Si es NULL la función no hace nada.
 */
void lista_invertir(Lista *lista) {
    Nodo *prev = NULL;
    Nodo *curr;
    Nodo *next;

    if (lista == NULL) {
        return;
    }

    curr = lista->cabeza;
    while (curr != NULL) {
        next = curr->sgte;
        curr->sgte = prev;
        prev = curr;
        curr = next;
    }
    lista->cabeza = prev;
}

/**
 * @brief Calcula el promedio aritmético de los valores de la lista.
 * @param[in]  lista     Puntero constante a la Lista.
 * @param[out] resultado Puntero donde se escribe el promedio calculado.
 * @return @c true  si la lista tiene al menos un elemento y se calculó.
 * @return @c false si @p lista o @p resultado son NULL, o la lista está vacía.
 */
bool lista_promedio(const Lista *lista, float *resultado) {
    long long suma = 0;
    int count = 0;
    Nodo *aux;

    if (lista == NULL || resultado == NULL) {
        return false;
    }

    aux = lista->cabeza;
    while (aux != NULL) {
        suma += aux->nro;
        count++;
        aux = aux->sgte;
    }

    if (count == 0) {
        return false;
    }

    *resultado = (float)suma / (float)count;
    return true;
}

/**
 * @brief Obtiene el valor mayor de la lista.
 * @param[in]  lista     Puntero constante a la Lista.
 * @param[out] resultado Puntero donde se escribe el mayor valor encontrado.
 * @return @c true  si la lista tiene al menos un elemento.
 * @return @c false si @p lista, @p resultado son NULL, o la lista está vacía.
 */
bool lista_mayor(const Lista *lista, int *resultado) {
    int max;
    Nodo *aux;

    if (lista == NULL || resultado == NULL || lista->cabeza == NULL) {
        return false;
    }

    max = lista->cabeza->nro;
    aux = lista->cabeza->sgte;
    while (aux != NULL) {
        if (aux->nro > max) {
            max = aux->nro;
        }
        aux = aux->sgte;
    }

    *resultado = max;
    return true;
}

/**
 * @brief Verifica si la lista está ordenada de forma ascendente.
 * @param[in] lista Puntero constante a la Lista.
 * @return @c true  si todos los elementos están en orden no decreciente,
 *                  o si la lista tiene 0 ó 1 elementos.
 * @return @c false si hay al menos un par fuera de orden o @p lista es NULL.
 */
bool lista_orden_asc(const Lista *lista) {
    Nodo *aux;
    if (lista == NULL || lista->cabeza == NULL || lista->cabeza->sgte == NULL) {
        return true;
    }

    aux = lista->cabeza;
    while (aux->sgte != NULL) {
        if (aux->nro > aux->sgte->nro) {
            return false;
        }
        aux = aux->sgte;
    }
    return true;
}

/**
 * @brief Indica si la lista no contiene ningún elemento.
 * @param[in] lista Puntero constante a la Lista a consultar.
 * @return @c true  si @p lista es NULL o @c cabeza es NULL.
 * @return @c false si la lista tiene al menos un elemento.
 */
bool lista_vacia(const Lista *lista) {
    return lista == NULL || lista->cabeza == NULL;
}

/**
 * @brief Cuenta el número de nodos de la lista.
 * @param[in] lista Puntero constante a la Lista.
 * @return Número de nodos (>= 0). Retorna 0 si @p lista es NULL.
 */
int lista_contar(const Lista *lista) {
    int cantidad = 0;
    Nodo *aux;
    if (lista == NULL) {
        return 0;
    }

    aux = lista->cabeza;
    while (aux != NULL) {
        cantidad++;
        aux = aux->sgte;
    }
    return cantidad;
}

/**
 * @brief Copia los valores de la lista en un arreglo externo.
 * @param[in]  lista     Puntero constante a la Lista de origen.
 * @param[out] destino   Arreglo donde se almacenarán los valores copiados.
 * @param[in]  capacidad Número máximo de elementos que caben en @p destino.
 * @return Número de elementos efectivamente copiados.
 *         Retorna 0 si @p lista, @p destino son NULL o @p capacidad <= 0.
 */
int lista_copiar_valores(const Lista *lista, int *destino, int capacidad) {
    int usados = 0;
    Nodo *aux;

    if (lista == NULL || destino == NULL || capacidad <= 0) {
        return 0;
    }

    aux = lista->cabeza;
    while (aux != NULL && usados < capacidad) {
        destino[usados] = aux->nro;
        usados++;
        aux = aux->sgte;
    }
    return usados;
}

/**
 * @brief Genera una representación textual de la lista.
 * @param[in]  lista     Puntero constante a la Lista a representar.
 * @param[out] destino   Buffer de caracteres donde se escribirá el resultado.
 * @param[in]  capacidad Tamaño en bytes del buffer @p destino.
 */
void lista_formatear(const Lista *lista, char *destino, size_t capacidad) {
    Nodo *aux;
    size_t usado = 0;
    int escritos;
    int pos = 1;

    if (destino == NULL || capacidad == 0) {
        return;
    }

    destino[0] = '\0';
    if (lista == NULL || lista->cabeza == NULL) {
        snprintf(destino, capacidad, "Lista vacia");
        return;
    }

    aux = lista->cabeza;
    while (aux != NULL && usado < capacidad) {
        escritos = snprintf(destino + usado, capacidad - usado, "[%d]=%d", pos, aux->nro);
        if (escritos < 0) {
            return;
        }
        usado += (size_t)escritos;

        aux = aux->sgte;
        pos++;
        if (aux != NULL && usado < capacidad) {
            escritos = snprintf(destino + usado, capacidad - usado, " -> ");
            if (escritos < 0) {
                return;
            }
            usado += (size_t)escritos;
        }
    }
}

/**
 * @brief Libera toda la memoria de los nodos de la lista.
 * @param[in,out] lista Puntero a la Lista a destruir.
 *                      Si es NULL la función no hace nada.
 */
void lista_destruir(Lista *lista) {
    Nodo *aux;
    Nodo *next;
    if (lista == NULL) {
        return;
    }

    aux = lista->cabeza;
    while (aux != NULL) {
        next = aux->sgte;
        free(aux);
        aux = next;
    }
    lista->cabeza = NULL;
}
