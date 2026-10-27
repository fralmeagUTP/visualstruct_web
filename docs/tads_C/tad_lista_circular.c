/**
 * @file tad_lista_circular.c
 * @brief Implementación del TAD Lista circular.
 */

#include "tad_lista_circular.h"

#include <stdio.h>
#include <stdarg.h>
#include <stdlib.h>

/**
 * @brief Nodo de una lista circular; sgte enlaza de nuevo a cabeza al final.
 */
struct lcir_nodo {
    int valor; /**< Dato almacenado. */
    struct lcir_nodo *sgte; /**< Enlace al siguiente nodo. */
};

/**
 * @brief Agrega texto formateado en un buffer de tamaño acotado.
 * @param destino Buffer de salida.
 * @param capacidad Capacidad total en bytes, incluido el terminador.
 * @param usado Contador actualizado de bytes; se satura a capacidad si hay truncamiento.
 * @param fmt Formato de vsnprintf para los argumentos variables.
 * @pre fmt es un formato válido y destino dispone de capacidad bytes si no es NULL.
 * @note Si destino/usado es NULL o usado alcanzó capacidad no escribe.
 */
static void lcir_append_text(char *destino, size_t capacidad, size_t *usado, const char *fmt, ...) {
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
 * @brief Crea un nuevo nodo para la lista circular.
 *
 * @param[in] valor Entero a almacenar en el nuevo nodo.
 *
 * @return Puntero al nuevo nodo, o NULL si la asignación de memoria falla.
 * @post En éxito valor contiene el dato y sgte es NULL; todavía no pertenece al anillo.
 * @note El llamador adquiere la propiedad de la reserva y debe publicarla o liberarla.
 *
 * @note Complejidad temporal: O(1).
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

/*
 * @brief Inicializa la estructura principal de la lista circular vacía.
 *
 * @param lista Puntero a la estructura de la lista circular.
 *
 * @post La cabeza y cola quedan apuntando a NULL.
 * @note Complejidad temporal: O(1).
 */
/**
 * @brief Inicializa la estructura principal de la lista circular vacía.
 *
 * @param[in,out] lista Puntero a la estructura de la lista circular.
 *
 * @post Con lista no nula, cabeza y cola quedan en NULL y cantidad en 0.
 * @note Si lista es NULL, retorna sin modificar memoria.
 * @note Complejidad temporal: O(1).
 */
void lcir_inicializar(ListaCircular *lista) {
    if (lista == NULL) {
        return;
    }
    lista->cabeza = NULL;
    lista->cola = NULL;
    lista->cantidad = 0;
}

/*
 * @brief Inserta un nuevo elemento al inicio de la lista circular.
 *
 * @param lista Puntero a la lista.
 * @param valor Dato a insertar.
 *
 * @return true si se insertó con éxito, false en caso de error.
 *
 * @post Si la lista estaba vacía, el nodo apunta a sí mismo.
 * @note Complejidad temporal: O(1) ya que se mantiene el puntero a la cola.
 */
/**
 * @brief Inserta un nuevo elemento al inicio de la lista circular.
 *
 * @param[in,out] lista Puntero a la lista.
 * @param[in]     valor Dato a insertar.
 *
 * @return true si se insertó; false si lista es NULL o malloc falla.
 * @post En éxito cantidad aumenta en uno y cola->sgte enlaza con cabeza.
 * @note Si falla la reserva, conserva cabeza, cola, cantidad y enlaces anteriores.
 *
 * @post Si la lista estaba vacía, el nodo apunta a sí mismo.
 * @note Complejidad temporal: O(1) ya que se mantiene el puntero a la cola.
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
        lista->cantidad = 1;
        return true;
    }

    nuevo->sgte = lista->cabeza;
    lista->cola->sgte = nuevo;
    lista->cabeza = nuevo;
    lista->cantidad++;
    return true;
}

/*
 * @brief Inserta un nuevo elemento al final de la lista circular.
 *
 * @param lista Puntero a la lista.
 * @param valor Dato a insertar.
 *
 * @return true si se insertó con éxito, false en caso de error.
 *
 * @note Complejidad temporal: O(1) debido a la existencia del puntero a la cola.
 */
/**
 * @brief Inserta un nuevo elemento al final de la lista circular.
 *
 * @param[in,out] lista Puntero a la lista.
 * @param[in]     valor Dato a insertar.
 *
 * @return true si se insertó; false si lista es NULL o malloc falla.
 * @post En éxito cantidad aumenta en uno y cola->sgte enlaza con cabeza.
 * @note Si falla la reserva, conserva cabeza, cola, cantidad y enlaces anteriores.
 *
 * @note Complejidad temporal: O(1) debido a la existencia del puntero a la cola.
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
        lista->cantidad = 1;
        return true;
    }

    nuevo->sgte = lista->cabeza;
    lista->cola->sgte = nuevo;
    lista->cola = nuevo;
    lista->cantidad++;
    return true;
}

/*
 * @brief Busca un valor y guarda las posiciones (índices basados en 1) en las que aparece.
 *
 * @param lista     Puntero constante a la lista.
 * @param valor     Elemento a buscar.
 * @param destino   Arreglo donde se escribirán las posiciones (1-based).
 * @param capacidad Capacidad máxima del arreglo de posiciones.
 *
 * @return El número de apariciones de dicho valor en la lista.
 *
 * @note Complejidad temporal: O(N), recorre la lista completa.
 */
/**
 * @brief Busca un valor y guarda las posiciones (índices basados en 1) en las que aparece.
 *
 * @param[in]  lista     Puntero constante a la lista.
 * @param[in]  valor     Elemento a buscar.
 * @param[out] destino   Arreglo donde se escribirán las posiciones (1-based).
 * @param[in]  capacidad Capacidad máxima del arreglo de posiciones.
 *
 * @return El número de apariciones de dicho valor en la lista.
 *
 * @note Complejidad temporal: O(N), recorre la lista completa.
 * @note Retorna todas las coincidencias aunque destino sea NULL o capacidad sea insuficiente.
 * @note Solo copia el prefijo que cabe; con capacidad <= 0 no escribe posiciones.
 * @post No modifica nodos ni enlaces; lista NULL o sin cabeza retorna 0.
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

/*
 * @brief Elimina el primer nodo que contenga el valor especificado.
 *
 * @param lista Puntero a la lista.
 * @param valor Elemento a remover de la lista.
 *
 * @return true si el nodo fue eliminado, false si no se encontró.
 *
 * @post Reajusta cabeza y/o cola si fueron eliminadas.
 * @note Complejidad temporal: O(N) en el peor caso.
 */
/**
 * @brief Elimina el primer nodo que contenga el valor especificado.
 *
 * @param[in,out] lista Puntero a la lista.
 * @param[in]     valor Elemento a remover de la lista.
 *
 * @return true si el nodo fue eliminado, false si no se encontró.
 *
 * @post Reajusta cabeza y/o cola si fueron eliminadas.
 * @note Complejidad temporal: O(N) en el peor caso.
 * @note Lista NULL, vacía o valor ausente retorna false sin liberar nodos.
 * @post En éxito libera una sola reserva, la primera coincidencia desde cabeza.
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
                lista->cabeza = NULL;
                lista->cola = NULL;
                lista->cantidad = 0;
                free(actual);
                return true;
            }

            anterior->sgte = actual->sgte;
            if (actual == lista->cabeza) {
                lista->cabeza = actual->sgte;
            }
            if (actual == lista->cola) {
                lista->cola = anterior;
            }
            if (lista->cantidad > 0) {
                lista->cantidad--;
            }
            free(actual);
            return true;
        }
        anterior = actual;
        actual = actual->sgte;
    } while (actual != lista->cabeza);

    return false;
}

/*
 * @brief Elimina el nodo de la cabeza de la lista circular.
 *
 * @param lista Puntero a la lista circular.
 * @return true si se eliminó la cabeza; false si la lista era nula o vacía.
 * @post Si quedan nodos, la cola vuelve a enlazar con la nueva cabeza.
 */
/**
 * @brief Elimina el nodo de la cabeza de la lista circular.
 *
 * @param[in,out] lista Puntero a la lista circular.
 * @return true si se eliminó la cabeza; false si la lista era nula o vacía.
 * @post Si quedan nodos, la cola vuelve a enlazar con la nueva cabeza.
 * @post En éxito libera exactamente la reserva de la cabeza anterior.
 * @post Si era el único nodo, cabeza y cola quedan NULL y cantidad en 0.
 * @note Con varios nodos, cola->sgte apunta a la nueva cabeza al terminar.
 * @note La cantidad cambia en su escritura C; retirar alcance no equivale a free.
 */
bool lcir_eliminar_inicio(ListaCircular *lista) {
    LCirNodo *actual;

    if (lista == NULL || lista->cabeza == NULL) {
        return false;
    }

    actual = lista->cabeza;
    if (lista->cabeza == lista->cola) {
        lista->cabeza = NULL;
        lista->cola = NULL;
        lista->cantidad = 0;
        free(actual);
        return true;
    }

    lista->cabeza = actual->sgte;
    lista->cola->sgte = lista->cabeza;
    if (lista->cantidad > 0) {
        lista->cantidad--;
    }
    free(actual);
    return true;
}

/*
 * @brief Invierte la dirección de la lista circular internamente.
 *
 * @details
 * Recorre todos los nodos invirtiendo los punteros "sgte".
 * Al terminar, actualiza los punteros globales de cabeza y cola.
 *
 * @param lista Puntero a la lista.
 *
 * @note Complejidad temporal: O(N).
 */
/**
 * @brief Invierte la dirección de la lista circular internamente.
 *
 * @details
 * Recorre todos los nodos invirtiendo los punteros "sgte".
 * Al terminar, actualiza los punteros globales de cabeza y cola.
 *
 * @param[in,out] lista Puntero a la lista.
 *
 * @note Complejidad temporal: O(N).
 * @note Con lista NULL, vacía o un solo nodo no modifica la estructura.
 * @post Conserva cantidad y las mismas reservas; no usa malloc ni free.
 * @note Los enlaces intermedios pueden no formar todavía el anillo final.
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

/*
 * @brief Comprueba si la lista circular está vacía.
 *
 * @param lista Puntero constante a la lista.
 *
 * @return true si está vacía, false si contiene al menos un elemento.
 *
 * @note Complejidad temporal: O(1).
 */
/**
 * @brief Comprueba si la lista circular está vacía.
 *
 * @param[in] lista Puntero constante a la lista.
 *
 * @return true si está vacía, false si contiene al menos un elemento.
 *
 * @note Complejidad temporal: O(1).
 * @note Evalúa lista == NULL o cantidad == 0; no recorre enlaces ni consulta cabeza.
 */
bool lcir_vacia(const ListaCircular *lista) {
    return lista == NULL || lista->cantidad == 0;
}

/*
 * @brief Cuenta la cantidad de nodos de la lista circular.
 *
 * @param lista Puntero constante a la lista.
 *
 * @return La cantidad de elementos, o 0 si está vacía.
 *
 * @note Complejidad temporal: O(1).
 */
/**
 * @brief Cuenta la cantidad de nodos de la lista circular.
 *
 * @param[in] lista Puntero constante a la lista.
 *
 * @return La cantidad de elementos, o 0 si está vacía.
 *
 * @note Complejidad temporal: O(1).
 * @note Retorna el campo cantidad almacenado, o 0 si lista es NULL; no recorre nodos.
 */
int lcir_contar(const ListaCircular *lista) {
    if (lista == NULL) {
        return 0;
    }
    return lista->cantidad;
}

/*
 * @brief Copia secuencialmente los valores de la lista a un arreglo.
 *
 * @param lista     Puntero constante a la lista.
 * @param destino   Arreglo donde se copiarán los valores.
 * @param capacidad Número máximo de elementos que puede almacenar el destino.
 *
 * @return Cantidad de elementos copiados de manera exitosa.
 *
 * @note Complejidad temporal: O(min(N, capacidad)).
 */
/**
 * @brief Copia secuencialmente los valores de la lista a un arreglo.
 *
 * @param[in]  lista     Puntero constante a la lista.
 * @param[out] destino   Arreglo donde se copiarán los valores.
 * @param[in]  capacidad Número máximo de elementos que puede almacenar el destino.
 *
 * @return Cantidad de elementos copiados de manera exitosa.
 *
 * @note Complejidad temporal: O(min(N, capacidad)).
 * @note Lista NULL/vacía, destino NULL o capacidad <= 0 retorna 0 sin escribir.
 * @post Copia como máximo capacidad valores desde cabeza sin modificar el TAD.
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

/*
 * @brief Genera una representación textual de la lista para imprimir.
 *
 * @details
 * Escribe en el destino el formato:
 * HEAD -> [1]=x -> [2]=y -> (vuelve a HEAD)
 *
 * @param lista     Puntero constante a la lista.
 * @param destino   Buffer destino de la cadena resultante.
 * @param capacidad Tamaño del buffer destino.
 *
 * @note Complejidad temporal: O(N).
 */
/**
 * @brief Genera una representación textual de la lista para imprimir.
 *
 * @details
 * Escribe en el destino el formato:
 * HEAD -> [1]=x -> [2]=y -> (vuelve a HEAD)
 *
 * @param[in]  lista     Puntero constante a la lista.
 * @param[out] destino   Buffer destino de la cadena resultante.
 * @param[in]  capacidad Tamaño del buffer destino.
 *
 * @note Complejidad temporal: O(N).
 * @note capacidad incluye el terminador NUL; destino NULL o capacidad 0 no se escribe.
 * @note Puede truncar el texto y omitir el cierre descriptivo si no cabe en el buffer.
 * @note Lista NULL o vacía produce Lista circular vacia, limitada por capacidad.
 */
void lcir_formatear(const ListaCircular *lista, char *destino, size_t capacidad) {
    LCirNodo *actual;
    size_t usado = 0;
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
    lcir_append_text(destino, capacidad, &usado, "HEAD -> ");

    do {
        lcir_append_text(destino, capacidad, &usado, "[%d]=%d", pos, actual->valor);
        actual = actual->sgte;
        pos++;

        if (actual != lista->cabeza && usado < capacidad) {
            lcir_append_text(destino, capacidad, &usado, " -> ");
        }
    } while (actual != lista->cabeza && usado < capacidad);

    if (usado < capacidad) {
        lcir_append_text(destino, capacidad, &usado, " -> (vuelve a HEAD)");
    }
}

/*
 * @brief Libera la memoria de todos los nodos de la lista y la limpia.
 *
 * @param lista Puntero a la lista.
 *
 * @post La estructura se reinicializa al estado vacío.
 * @note Complejidad temporal: O(N).
 */
/**
 * @brief Libera la memoria de todos los nodos de la lista y la limpia.
 *
 * @param[in,out] lista Puntero a la lista.
 *
 * @post La estructura se reinicializa al estado vacío.
 * @note Complejidad temporal: O(N).
 * @note Con lista NULL o cabeza NULL retorna sin acceder ni normalizar otros campos.
 * @post Con un anillo válido libera cada reserva una vez y deja los dos extremos NULL y cantidad 0.
 * @note Los aliases externos de nodos liberados dejan de ser válidos.
 */
void lcir_destruir(ListaCircular *lista) {
    LCirNodo *actual;
    LCirNodo *next;

    if (lista == NULL || lista->cabeza == NULL) {
        return;
    }

    actual = lista->cabeza;
    if (lista->cabeza == lista->cola) {
        lista->cabeza = NULL;
        lista->cola = NULL;
        lista->cantidad = 0;
        free(actual);
        return;
    }

    while (actual != lista->cola) {
        next = actual->sgte;
        lista->cabeza = next;
        lista->cola->sgte = lista->cabeza;
        if (lista->cantidad > 0) {
            lista->cantidad--;
        }
        free(actual);
        actual = next;
    }

    lista->cabeza = NULL;
    lista->cola = NULL;
    lista->cantidad = 0;
    free(actual);
}
