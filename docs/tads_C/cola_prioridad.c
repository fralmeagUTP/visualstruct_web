#include "cola_prioridad.h"

#include <stdio.h>
#include <stdlib.h>

struct cp_nodo {
    int valor;
    int prioridad;
    struct cp_nodo *sgte;
};

/**
 * @brief Inicializa una ColaPrioridad poniéndola en estado vacío.
 * @param[out] cola Puntero a la ColaPrioridad que se va a inicializar.
 *                  Si es NULL la función no hace nada.
 */
void cp_inicializar(ColaPrioridad *cola) {
    if (cola == NULL) {
        return;
    }
    cola->delante = NULL;
    cola->atras = NULL;
}

/**
 * @brief Encola un elemento con su valor y prioridad asociada.
 * @param[in,out] cola      Puntero a la ColaPrioridad destino.
 * @param[in]     valor     Dato entero a almacenar.
 * @param[in]     prioridad Número de prioridad (menor valor = mayor prioridad).
 * @return @c true  si el nodo fue creado e insertado correctamente.
 * @return @c false si @p cola es NULL o @c malloc() falla.
 */
bool cp_encolar(ColaPrioridad *cola, int valor, int prioridad) {
    CPNodo *nuevo;
    if (cola == NULL) {
        return false;
    }

    nuevo = (CPNodo *)malloc(sizeof(CPNodo));
    if (nuevo == NULL) {
        return false;
    }

    nuevo->valor = valor;
    nuevo->prioridad = prioridad;
    nuevo->sgte = NULL;

    if (cola->delante == NULL) {
        cola->delante = nuevo;
    } else {
        cola->atras->sgte = nuevo;
    }
    cola->atras = nuevo;
    return true;
}

/**
 * @brief Desencola el elemento de mayor prioridad efectiva.
 * @param[in,out] cola      Puntero a la ColaPrioridad de origen.
 * @param[out]    valor     Puntero donde se escribe el valor del nodo extraído.
 * @param[out]    prioridad Puntero donde se escribe la prioridad extraída.
 * @return @c true  si se extrajo un elemento correctamente.
 * @return @c false si @p cola, @p valor o @p prioridad son NULL,
 *                  o la cola está vacía.
 */
bool cp_desencolar(ColaPrioridad *cola, int *valor, int *prioridad) {
    CPNodo *actual;
    CPNodo *prev;
    CPNodo *objetivo;
    CPNodo *objetivoPrev;

    if (cola == NULL || cola->delante == NULL || valor == NULL || prioridad == NULL) {
        return false;
    }

    actual = cola->delante;
    prev = NULL;
    objetivo = actual;
    objetivoPrev = NULL;

    while (actual != NULL) {
        if (actual->prioridad < objetivo->prioridad) {
            objetivo = actual;
            objetivoPrev = prev;
        }
        prev = actual;
        actual = actual->sgte;
    }

    if (objetivo == cola->delante) {
        cola->delante = objetivo->sgte;
        if (cola->delante == NULL) {
            cola->atras = NULL;
        }
    } else {
        objetivoPrev->sgte = objetivo->sgte;
        if (cola->atras == objetivo) {
            cola->atras = objetivoPrev;
        }
    }

    *valor = objetivo->valor;
    *prioridad = objetivo->prioridad;
    free(objetivo);
    return true;
}

/**
 * @brief Indica si la cola de prioridad no contiene ningún elemento.
 * @param[in] cola Puntero constante a la ColaPrioridad a consultar.
 * @return @c true  si @p cola es NULL o @c delante es NULL.
 * @return @c false si la cola tiene al menos un elemento.
 */
bool cp_vacia(const ColaPrioridad *cola) {
    return cola == NULL || cola->delante == NULL;
}

/**
 * @brief Cuenta el número de elementos presentes en la cola.
 * @param[in] cola Puntero constante a la ColaPrioridad.
 * @return Número de nodos (>= 0). Retorna 0 si @p cola es NULL.
 */
int cp_contar(const ColaPrioridad *cola) {
    int cantidad = 0;
    CPNodo *aux;

    if (cola == NULL) {
        return 0;
    }

    aux = cola->delante;
    while (aux != NULL) {
        cantidad++;
        aux = aux->sgte;
    }
    return cantidad;
}

/**
 * @brief Copia el valor y prioridad de cada elemento en arreglos externos.
 * @param[in]  cola        Puntero constante a la ColaPrioridad de origen.
 * @param[out] valores     Arreglo donde se almacenarán los valores copiados.
 * @param[out] prioridades Arreglo donde se almacenarán las prioridades.
 * @param[in]  capacidad   Número máximo de elementos a copiar.
 * @return Número de elementos efectivamente copiados.
 *         Retorna 0 si algún parámetro es inválido.
 */
int cp_copiar_items(const ColaPrioridad *cola, int *valores, int *prioridades, int capacidad) {
    int usados = 0;
    CPNodo *aux;

    if (cola == NULL || valores == NULL || prioridades == NULL || capacidad <= 0) {
        return 0;
    }

    aux = cola->delante;
    while (aux != NULL && usados < capacidad) {
        valores[usados] = aux->valor;
        prioridades[usados] = aux->prioridad;
        usados++;
        aux = aux->sgte;
    }
    return usados;
}

/**
 * @brief Genera una representación textual de la cola de prioridad.
 * @param[in]  cola      Puntero constante a la ColaPrioridad.
 * @param[out] destino   Buffer donde se escribirá la cadena resultante.
 * @param[in]  capacidad Tamaño en bytes del buffer @p destino.
 */
void cp_formatear(const ColaPrioridad *cola, char *destino, size_t capacidad) {
    CPNodo *aux;
    size_t usado = 0;
    int escritos;

    if (destino == NULL || capacidad == 0) {
        return;
    }

    destino[0] = '\0';

    if (cola == NULL || cola->delante == NULL) {
        snprintf(destino, capacidad, "Cola de prioridad vacia");
        return;
    }

    escritos = snprintf(destino, capacidad, "frente -> ");
    if (escritos < 0) {
        return;
    }
    usado = (size_t)escritos;

    aux = cola->delante;
    while (aux != NULL && usado < capacidad) {
        escritos = snprintf(destino + usado, capacidad - usado, "%d(p=%d)", aux->valor, aux->prioridad);
        if (escritos < 0) {
            return;
        }
        usado += (size_t)escritos;
        aux = aux->sgte;
        if (aux != NULL && usado < capacidad) {
            escritos = snprintf(destino + usado, capacidad - usado, " | ");
            if (escritos < 0) {
                return;
            }
            usado += (size_t)escritos;
        }
    }
}

/**
 * @brief Elimina todos los elementos de la cola y libera su memoria.
 * @param[in,out] cola Puntero a la ColaPrioridad a vaciar.
 *                     Si es NULL la función no hace nada.
 */
void cp_vaciar(ColaPrioridad *cola) {
    CPNodo *aux;
    CPNodo *next;

    if (cola == NULL) {
        return;
    }

    aux = cola->delante;
    while (aux != NULL) {
        next = aux->sgte;
        free(aux);
        aux = next;
    }

    cola->delante = NULL;
    cola->atras = NULL;
}
