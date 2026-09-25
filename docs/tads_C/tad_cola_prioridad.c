#include "tad_cola_prioridad.h"

#include <stdio.h>
#include <stdarg.h>
#include <stdlib.h>

struct cp_nodo {
    int valor;
    int prioridad;
    struct cp_nodo *sgte;
};

static void cp_append_text(char *destino, size_t capacidad, size_t *usado, const char *fmt, ...) {
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

static CPNodo *cp_crear_nodo(int valor, int prioridad) {
    CPNodo *nuevo = (CPNodo *)malloc(sizeof(CPNodo));
    if (nuevo == NULL) {
        return NULL;
    }
    nuevo->valor = valor;
    nuevo->prioridad = prioridad;
    nuevo->sgte = NULL;
    return nuevo;
}

/**
 * @brief Inicializa una ColaPrioridad poniéndola en estado vacío.
 *
 * Establece @c delante y @c atras a NULL. Debe ser la primera llamada
 * antes de operar sobre la cola. No reserva memoria dinámica.
 *
 * @param[out] cola Puntero a la ColaPrioridad que se va a inicializar.
 *                  Si es NULL la función no hace nada.
 *
 * @post La cola queda vacía y lista para usarse.
 */
void cp_inicializar(ColaPrioridad *cola) {
    if (cola == NULL) {
        return;
    }
    cola->delante = NULL;
    cola->atras = NULL;
    cola->cantidad = 0;
}

/**
 * @brief Encola un elemento con su valor y prioridad asociada.
 *
 * @details
 * Reserva dinámicamente un nuevo @c CPNodo, almacena @p valor y
 * @p prioridad en él y lo enlaza al extremo @c atras de la cola.
 * Si la cola estaba vacía, tanto @c delante como @c atras apuntarán
 * al nuevo nodo. El orden de extracción depende de la prioridad,
 * no del orden de inserción.
 *
 * @param[in,out] cola      Puntero a la ColaPrioridad destino.
 * @param[in]     valor     Dato entero a almacenar.
 * @param[in]     prioridad Número de prioridad (menor valor = mayor prioridad).
 *
 * @return @c true  si el nodo fue creado e insertado correctamente.
 * @return @c false si @p cola es NULL o @c malloc() falla.
 *
 * @pre  La cola debe haber sido inicializada con cp_inicializar().
 * @post El tamaño de la cola aumenta en 1.
 * @note Complejidad temporal: O(1).
 */
bool cp_encolar(ColaPrioridad *cola, int valor, int prioridad) {
    CPNodo *nuevo;
    if (cola == NULL) {
        return false;
    }

    nuevo = cp_crear_nodo(valor, prioridad);
    if (nuevo == NULL) {
        return false;
    }

    if (cola->delante == NULL) {
        cola->delante = nuevo;
    } else {
        cola->atras->sgte = nuevo;
    }
    cola->atras = nuevo;
    cola->cantidad++;
    return true;
}

/**
 * @brief Desencola el elemento de mayor prioridad efectiva.
 *
 * @details
 * Recorre toda la cola buscando el nodo con el valor de prioridad más
 * bajo (número más pequeño). En caso de empate extrae el que fue
 * insertado primero (el que aparece antes en la lista).
 * Una vez encontrado, lo desenlaza actualizando @c delante o
 * @c atras según corresponda, escribe sus datos en los punteros
 * @p valor y @p prioridad y libera su memoria.
 *
 * @param[in,out] cola      Puntero a la ColaPrioridad de origen.
 * @param[out]    valor     Puntero donde se escribe el valor del nodo extraído.
 * @param[out]    prioridad Puntero donde se escribe la prioridad extraída.
 *
 * @return @c true  si se extrajo un elemento correctamente.
 * @return @c false si @p cola, @p valor o @p prioridad son NULL,
 *                  o la cola está vacía.
 *
 * @pre  La cola debe contener al menos un elemento.
 * @post El tamaño de la cola disminuye en 1.
 * @note Complejidad temporal: O(n), donde n es el número de elementos.
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
    if (cola->cantidad > 0) {
        cola->cantidad--;
    }
    return true;
}

bool cp_frente(const ColaPrioridad *cola, int *valor, int *prioridad) {
    const CPNodo *actual;
    const CPNodo *objetivo;
    if (cola == NULL || cola->delante == NULL || valor == NULL || prioridad == NULL) return false;
    objetivo = cola->delante;
    actual = cola->delante->sgte;
    while (actual != NULL) {
        if (actual->prioridad < objetivo->prioridad) objetivo = actual;
        actual = actual->sgte;
    }
    *valor = objetivo->valor;
    *prioridad = objetivo->prioridad;
    return true;
}

/**
 * @brief Indica si la cola de prioridad no contiene ningún elemento.
 *
 * @param[in] cola Puntero constante a la ColaPrioridad a consultar.
 *
 * @return @c true  si @p cola es NULL o @c delante es NULL.
 * @return @c false si la cola tiene al menos un elemento.
 *
 * @note Complejidad temporal: O(1).
 */
bool cp_vacia(const ColaPrioridad *cola) {
    return cola == NULL || cola->delante == NULL || cola->cantidad == 0;
}

/**
 * @brief Cuenta el número de elementos presentes en la cola.
 *
 * @param[in] cola Puntero constante a la ColaPrioridad.
 *
 * @return Número de nodos (>= 0). Retorna 0 si @p cola es NULL.
 *
 * @note Complejidad temporal: O(1).
 */
int cp_contar(const ColaPrioridad *cola) {
    if (cola == NULL) {
        return 0;
    }
    return cola->cantidad;
}

/**
 * @brief Copia el valor y prioridad de cada elemento en arreglos externos.
 *
 * @details
 * Recorre la cola de frente a fondo. Por cada nodo, copia su @c valor
 * en @p valores[@c i] y su @c prioridad en @p prioridades[@c i].
 * Se copian como máximo @p capacidad elementos. La cola no se modifica.
 *
 * @param[in]  cola        Puntero constante a la ColaPrioridad de origen.
 * @param[out] valores     Arreglo donde se almacenarán los valores copiados.
 * @param[out] prioridades Arreglo donde se almacenarán las prioridades.
 * @param[in]  capacidad   Número máximo de elementos a copiar.
 *
 * @return Número de elementos efectivamente copiados.
 *         Retorna 0 si algún parámetro es inválido.
 *
 * @pre  @p valores y @p prioridades deben apuntar a bloques con espacio
 *       para al menos @p capacidad enteros cada uno.
 * @note Complejidad temporal: O(min(n, capacidad)).
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
 *
 * @details
 * Escribe en @p destino una cadena con el formato:
 * @code
 * frente -> v1(p=p1) | v2(p=p2) | ... | vN(p=pN)
 * @endcode
 * donde @c vK es el valor y @c pK la prioridad del k-ésimo elemento
 * en orden de inserción. Si la cola está vacía escribe
 * @c "Cola de prioridad vacia".
 * La cadena siempre queda terminada en @c '\0' si @p capacidad >= 1.
 *
 * @param[in]  cola      Puntero constante a la ColaPrioridad.
 * @param[out] destino   Buffer donde se escribirá la cadena resultante.
 * @param[in]  capacidad Tamaño en bytes del buffer @p destino.
 *
 * @pre  @p destino debe apuntar a un buffer de al menos @p capacidad bytes.
 * @post @p destino contiene una cadena terminada en @c '\0'.
 * @note Si el contenido supera @p capacidad se trunca de forma segura.
 * @note Si @p destino es NULL o @p capacidad es 0, no hace nada.
 * @note Complejidad temporal: O(n).
 */
void cp_formatear(const ColaPrioridad *cola, char *destino, size_t capacidad) {
    CPNodo *aux;
    size_t usado = 0;

    if (destino == NULL || capacidad == 0) {
        return;
    }

    destino[0] = '\0';

    if (cola == NULL || cola->delante == NULL) {
        snprintf(destino, capacidad, "Cola de prioridad vacia");
        return;
    }

    cp_append_text(destino, capacidad, &usado, "frente -> ");

    aux = cola->delante;
    while (aux != NULL && usado < capacidad) {
        cp_append_text(destino, capacidad, &usado, "%d(p=%d)", aux->valor, aux->prioridad);
        aux = aux->sgte;
        if (aux != NULL && usado < capacidad) {
            cp_append_text(destino, capacidad, &usado, " | ");
        }
    }
}

/**
 * @brief Elimina todos los elementos de la cola y libera su memoria.
 *
 * @details
 * Recorre la cola desde @c delante hasta el final usando un puntero
 * @c next para guardar el enlace antes de liberar cada @c CPNodo.
 * Al finalizar, @c delante y @c atras quedan en NULL.
 *
 * @param[in,out] cola Puntero a la ColaPrioridad a vaciar.
 *                     Si es NULL la función no hace nada.
 *
 * @post La cola queda en el mismo estado que tras cp_inicializar().
 * @note Complejidad temporal: O(n).
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
    cola->cantidad = 0;
}
