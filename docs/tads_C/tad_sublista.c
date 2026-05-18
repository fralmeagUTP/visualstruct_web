#include "tad_sublista.h"

#include <stdio.h>
#include <stdarg.h>
#include <stdlib.h>

/**
 * @brief Crea un nuevo nodo padre.
 * @param[in] valor Valor entero a almacenar.
 * @return Puntero al nuevo nodo, o NULL si falla la memoria.
 */
static Nodo *crear_padre(int valor) {
    Nodo *nuevo = (Nodo *)malloc(sizeof(Nodo));
    if (nuevo == NULL) {
        return NULL;
    }
    nuevo->nro = valor;
    nuevo->sgte = NULL;
    nuevo->sub = NULL;
    return nuevo;
}

/**
 * @brief Crea un nuevo nodo hijo para una sublista.
 * @param[in] valor Valor entero a almacenar.
 * @return Puntero a la nueva sublista, o NULL si falla la memoria.
 */
static Sublista *crear_hijo(int valor) {
    Sublista *nuevo = (Sublista *)malloc(sizeof(Sublista));
    if (nuevo == NULL) {
        return NULL;
    }
    nuevo->nro = valor;
    nuevo->sgte = NULL;
    return nuevo;
}

static void sublista_append_text(char *destino, size_t capacidad, size_t *usado, const char *fmt, ...) {
    va_list args;
    int escritos;

    if (destino == NULL || usado == NULL || *usado >= capacidad) {
        return;
    }

    va_start(args, fmt);
    escritos = vsnprintf(destino + *usado, capacidad - *usado, fmt, args);
    va_end(args);
    if (escritos < 0) {
        return;
    }
    if ((size_t)escritos >= capacidad - *usado) {
        *usado = capacidad;
    } else {
        *usado += (size_t)escritos;
    }
}

/**
 * @brief Libera la memoria de todos los nodos en una sublista de hijos.
 * @param[in,out] lista_hijos Doble puntero al primer nodo hijo.
 */
static void destruir_hijos(Sublista **lista_hijos) {
    Sublista *actual;
    Sublista *next;

    if (lista_hijos == NULL) {
        return;
    }

    actual = *lista_hijos;
    while (actual != NULL) {
        next = actual->sgte;
        free(actual);
        actual = next;
    }
    *lista_hijos = NULL;
}

/**
 * @brief Inicializa la lista principal de nodos padre estableciéndola en NULL.
 * @param[out] lista Doble puntero a la lista a inicializar.
 */
void sublista_inicializar(Nodo **lista) {
    if (lista == NULL) {
        return;
    }
    *lista = NULL;
}

/**
 * @brief Inserta un nuevo nodo padre al final de la lista principal.
 * @param[in,out] lista       Doble puntero a la lista principal.
 * @param[in]     valor_padre Valor del nuevo padre.
 * @return Puntero al nuevo nodo insertado, o NULL si falla.
 */
Nodo *sublista_insertar_padre_final(Nodo **lista, int valor_padre) {
    Nodo *nuevo;
    Nodo *actual;

    if (lista == NULL) {
        return NULL;
    }

    nuevo = crear_padre(valor_padre);
    if (nuevo == NULL) {
        return NULL;
    }

    if (*lista == NULL) {
        *lista = nuevo;
        return nuevo;
    }

    actual = *lista;
    while (actual->sgte != NULL) {
        actual = actual->sgte;
    }
    actual->sgte = nuevo;
    return nuevo;
}

/**
 * @brief Busca un nodo padre por su valor.
 * @param[in] lista       Puntero al primer nodo de la lista.
 * @param[in] valor_padre Valor a buscar.
 * @return Puntero al nodo padre encontrado, o NULL si no existe.
 */
Nodo *sublista_buscar_padre(Nodo *lista, int valor_padre) {
    Nodo *actual = lista;
    while (actual != NULL) {
        if (actual->nro == valor_padre) {
            return actual;
        }
        actual = actual->sgte;
    }
    return NULL;
}

/**
 * @brief Elimina la primera ocurrencia de un nodo padre y todos sus hijos.
 * @param[in,out] lista       Doble puntero a la lista.
 * @param[in]     valor_padre Valor del padre a eliminar.
 * @return true si fue eliminado con éxito, false si no se encontró.
*/
bool sublista_eliminar_padre_primero(Nodo **lista, int valor_padre) {
    Nodo *actual;
    Nodo *anterior = NULL;

    if (lista == NULL || *lista == NULL) {
        return false;
    }

    actual = *lista;
    while (actual != NULL) {
        if (actual->nro == valor_padre) {
            if (anterior == NULL) {
                *lista = actual->sgte;
            } else {
                anterior->sgte = actual->sgte;
            }
            destruir_hijos(&actual->sub);
            free(actual);
            return true;
        }
        anterior = actual;
        actual = actual->sgte;
    }

    return false;
}

/**
 * @brief Cuenta el número de nodos padre en la lista.
 * @param[in] lista Puntero constante a la lista.
 * @return Cantidad de nodos padre.
 */
int sublista_contar_padres(const Nodo *lista) {
    int n = 0;
    const Nodo *actual = lista;
    while (actual != NULL) {
        n++;
        actual = actual->sgte;
    }
    return n;
}

/**
 * @brief Inserta un nuevo nodo hijo al final de la sublista de un padre.
 * @param[in,out] padre      Puntero al nodo padre.
 * @param[in]     valor_hijo Valor del nuevo hijo.
 * @return true si se insertó exitosamente, false en caso de error.
 */
bool sublista_insertar_hijo_final(Nodo *padre, int valor_hijo) {
    Sublista *nuevo;
    Sublista *actual;

    if (padre == NULL) {
        return false;
    }

    nuevo = crear_hijo(valor_hijo);
    if (nuevo == NULL) {
        return false;
    }

    if (padre->sub == NULL) {
        padre->sub = nuevo;
        return true;
    }

    actual = padre->sub;
    while (actual->sgte != NULL) {
        actual = actual->sgte;
    }
    actual->sgte = nuevo;
    return true;
}

/**
 * @brief Busca un nodo hijo dentro de una sublista por su valor.
 * @param[in] lista_hijos Puntero al primer nodo de la sublista.
 * @param[in] valor_hijo  Valor a buscar.
 * @return Puntero al hijo encontrado, o NULL si no existe.
 */
Sublista *sublista_buscar_hijo(Sublista *lista_hijos, int valor_hijo) {
    Sublista *actual = lista_hijos;
    while (actual != NULL) {
        if (actual->nro == valor_hijo) {
            return actual;
        }
        actual = actual->sgte;
    }
    return NULL;
}

/**
 * @brief Elimina la primera ocurrencia de un hijo en la sublista de un padre.
 * @param[in,out] padre      Puntero al nodo padre.
 * @param[in]     valor_hijo Valor del hijo a eliminar.
 * @return true si se eliminó correctamente, false si no se encontró.
 */
bool sublista_eliminar_hijo_primero(Nodo *padre, int valor_hijo) {
    Sublista *actual;
    Sublista *anterior = NULL;

    if (padre == NULL || padre->sub == NULL) {
        return false;
    }

    actual = padre->sub;
    while (actual != NULL) {
        if (actual->nro == valor_hijo) {
            if (anterior == NULL) {
                padre->sub = actual->sgte;
            } else {
                anterior->sgte = actual->sgte;
            }
            free(actual);
            return true;
        }
        anterior = actual;
        actual = actual->sgte;
    }

    return false;
}

/**
 * @brief Cuenta cuántos hijos tiene un nodo padre.
 * @param[in] padre Puntero constante al padre.
 * @return Número de hijos del padre.
 */
int sublista_contar_hijos(const Nodo *padre) {
    int n = 0;
    const Sublista *actual;

    if (padre == NULL) {
        return 0;
    }

    actual = padre->sub;
    while (actual != NULL) {
        n++;
        actual = actual->sgte;
    }
    return n;
}

/**
 * @brief Copia los valores de los hijos de un padre a un arreglo.
 * @param[in]  padre     Puntero constante al padre.
 * @param[out] destino   Arreglo donde se copiarán los valores.
 * @param[in]  capacidad Tamaño máximo del arreglo destino.
 * @return El número de elementos copiados.
 */
int sublista_copiar_hijos(const Nodo *padre, int *destino, int capacidad) {
    int usados = 0;
    const Sublista *actual;

    if (padre == NULL || destino == NULL || capacidad <= 0) {
        return 0;
    }

    actual = padre->sub;
    while (actual != NULL && usados < capacidad) {
        destino[usados] = actual->nro;
        usados++;
        actual = actual->sgte;
    }
    return usados;
}

/**
 * @brief Genera una representación textual de la lista y sus sublistas.
 * @param[in]  lista     Puntero constante a la lista de padres.
 * @param[out] destino   Buffer para escribir la cadena resultante.
 * @param[in]  capacidad Capacidad máxima del buffer.
 */
void sublista_formatear(const Nodo *lista, char *destino, size_t capacidad) {
    const Nodo *padre;
    const Sublista *hijo;
    size_t usado = 0;

    if (destino == NULL || capacidad == 0) {
        return;
    }

    destino[0] = '\0';
    if (lista == NULL) {
        snprintf(destino, capacidad, "Lista padre vacia");
        return;
    }

    padre = lista;
    while (padre != NULL && usado < capacidad) {
        sublista_append_text(destino, capacidad, &usado, "P(%d): ", padre->nro);

        hijo = padre->sub;
        if (hijo == NULL) {
            sublista_append_text(destino, capacidad, &usado, "(sin hijos)");
        } else {
            while (hijo != NULL && usado < capacidad) {
                sublista_append_text(destino, capacidad, &usado, "[%d]", hijo->nro);
                hijo = hijo->sgte;
                if (hijo != NULL && usado < capacidad) {
                    sublista_append_text(destino, capacidad, &usado, " -> ");
                }
            }
        }

        padre = padre->sgte;
        if (padre != NULL && usado < capacidad) {
            sublista_append_text(destino, capacidad, &usado, "\n");
        }
    }
}

/**
 * @brief Libera completamente la memoria de todos los padres y sus respectivos hijos.
 * @param[in,out] lista Doble puntero a la lista principal.
 */
void sublista_destruir(Nodo **lista) {
    Nodo *actual;
    Nodo *next;

    if (lista == NULL) {
        return;
    }

    actual = *lista;
    while (actual != NULL) {
        next = actual->sgte;
        destruir_hijos(&actual->sub);
        free(actual);
        actual = next;
    }
    *lista = NULL;
}
