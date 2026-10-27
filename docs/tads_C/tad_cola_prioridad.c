/**
 * @file tad_cola_prioridad.c
 * @brief Implementación del TAD Cola de prioridad en orden de llegada.
 */

#include "tad_cola_prioridad.h"

#include <stdio.h>
#include <stdarg.h>
#include <stdlib.h>

/**
 * @brief Nodo interno de cola de prioridad, enlazado en orden de llegada.
 */
struct cp_nodo {
    int valor; /**< Dato almacenado. */
    int prioridad; /**< Prioridad del elemento. */
    struct cp_nodo *sgte; /**< Enlace al siguiente nodo. */
};

/**
 * @brief Agrega texto formateado en un buffer de tamaño acotado.
 * @param destino Buffer de salida.
 * @param capacidad Capacidad total en bytes, incluido el terminador.
 * @param usado Contador actualizado de bytes; se satura a capacidad si hay truncamiento.
 * @param fmt Formato de vsnprintf para los argumentos variables.
 * @pre Buffer escribible de capacidad bytes; usado es size_t externo escribible; fmt y argumentos validos de vsnprintf, sin solaparse con salida.
 * @note NULL destino/usado o *usado >= capacidad se ignoran; error no incrementa usado. Truncamiento satura usado a capacidad. Caller inicializa buffer/contador; no reserva/libera ni imprime.
 */
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

/**
 * @brief Reserva e inicializa un nodo con enlace siguiente NULL.
 * @param valor Dato a almacenar.
 * @param prioridad Prioridad que se consulta al seleccionar la extracción.
 * @return Nodo reservado o NULL si falla malloc; el llamador adquiere su propiedad.
 * @note Enteros valor/prioridad admiten negativos y extremos int. Inicializa los tres campos; no imprime. Publicar en cola transfiere ownership; si no publica, caller debe liberar.
 */
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
 * @brief Escribe el estado vacio sin reservar ni liberar nodos.
 * @param[out] cola Direccion valida de estructura o NULL (sin efecto).
 * @pre Antes del primer uso; si ya tiene nodos, vaciarlos antes de reinicializar.
 * @note Reinicializar una cola no vaciada pierde sus referencias y no libera los nodos. Delante/atras NULL y cantidad cero.
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
 * @post Si retorna true, el tamaño aumenta en 1; si retorna false, la cola no cambia.
 * @note Complejidad temporal: O(1).
 * @pre Cola propia consistente, nodos vivos y aciclicos; cantidad+1 cabe en int.
 * @note NULL cola o malloc fallido retorna false sin publicar nodo ni escribir enlaces. No reordena nodos; prioridad menor se selecciona al extraer.
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
 * @pre  La cola debe estar inicializada; una cola vacía se admite y retorna false.
 * @post Si retorna true, el tamaño disminuye en 1; ante cola vacía o parámetros NULL no hay extracción.
 * @note Complejidad temporal: O(n), donde n es el número de elementos.
 * @pre Cola propia consistente y viva; valor y prioridad son ints externos escribibles disjuntos entre si y de nodos/metadata.
 * @note False no escribe salidas. Seleccion por comparacion estricta conserva primer minimo en orden enlazado. Libera exactamente el seleccionado; aliases al nodo quedan invalidos. No reserva ni imprime.
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


/**
 * @brief Consulta el elemento que sería atendido sin modificar la cola.
 * @details Selecciona la menor prioridad; los empates conservan el orden de llegada.
 * @param[in] cola Cola que se consulta.
 * @param[out] valor Valor del candidato seleccionado.
 * @param[out] prioridad Prioridad del candidato seleccionado.
 * @return true si hay candidato y los parámetros de salida son válidos.
 * @return false si la cola está vacía o cola, valor o prioridad son NULL.
 * @pre Cola prestada consistente con lista viva y aciclica; salidas externas escribibles disjuntas entre si y de cola/nodos.
 * @note False conserva salidas. No reserva/libera/imprime ni modifica cola bajo precondiciones; el puntero const no valida aliases externos.
 */
bool cp_frente(const ColaPrioridad *cola, int *valor, int *prioridad) {
    const CPNodo *actual;
    const CPNodo *objetivo;

    if (cola == NULL || cola->delante == NULL || valor == NULL || prioridad == NULL) {
        return false;
    }
    objetivo = cola->delante;
    actual = cola->delante->sgte;
    while (actual != NULL) {
        if (actual->prioridad < objetivo->prioridad) {
            objetivo = actual;
        }
        actual = actual->sgte;
    }
    *valor = objetivo->valor;
    *prioridad = objetivo->prioridad;
    return true;
}


/**
 * @brief Consulta las guardas de vacio sin modificar la cola.
 * @param[in] cola Estructura prestada inicializada o NULL.
 * @return true si cola NULL, delante NULL o cantidad cero; false en otro caso.
 * @note No recorre nodos ni valida consistencia; no reserva, libera ni imprime.
 */
bool cp_vacia(const ColaPrioridad *cola) {
    return cola == NULL || cola->delante == NULL || cola->cantidad == 0;
}


/**
 * @brief Devuelve el contador almacenado de la cola.
 * @param[in] cola Estructura prestada inicializada o NULL.
 * @return 0 ante NULL; en otro caso cantidad sin recorrer ni corregir el contador.
 * @note En cola consistente es el numero de nodos. No valida corrupcion ni modifica memoria.
 */
int cp_contar(const ColaPrioridad *cola) {
    if (cola == NULL) {
        return 0;
    }
    return cola->cantidad;
}


/**
 * @brief Copia datos en orden de llegada, sin ordenar por prioridad.
 * @param[in] cola Cola prestada inicializada con nodos vivos y aciclicos.
 * @param[out] valores Buffer externo de capacidad enteros.
 * @param[out] prioridades Segundo buffer externo de capacidad enteros.
 * @param[in] capacidad Maximo de elementos a copiar.
 * @return Numero copiado; 0 si cola/valores/prioridades NULL o capacidad <= 0.
 * @pre Con capacidad positiva los buffers son escribibles y no se solapan entre si ni con la cola.
 * @note No reserva/libera y no modifica la cola bajo esas precondiciones. No comprueba longitud real del buffer; copia hasta fin de lista o capacidad.
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
 * @brief Escribe la representacion textual en orden de llegada.
 * @param[in] cola Cola prestada inicializada o NULL (texto vacio).
 * @param[out] destino Buffer externo escribible; NULL se ignora.
 * @param[in] capacidad Bytes disponibles incluyendo terminador; cero se ignora.
 * @pre Buffer de al menos capacidad bytes, sin solaparse con la cola.
 * @note Con destino valido y capacidad positiva inicializa y termina con NUL; trunca a capacidad-1 caracteres. Capacidad 1 produce cadena vacia.
 * @note No reserva/libera ni imprime stdout. No ordena por prioridad; NULL o delante NULL escribe Cola de prioridad vacia.
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
 * @pre Cola inicializada, propia, consistente y aciclica; no compartir ownership de nodos.
 * @note NULL cola no escribe. Cada nodo se libera una vez, al final cantidad=0, delante=atras=NULL. No reserva ni imprime; aliases a nodos liberados quedan invalidos.
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
        cola->delante = next;
        if (cola->atras == aux) {
            cola->atras = NULL;
        }
        free(aux);
        if (cola->cantidad > 0) {
            cola->cantidad--;
        }
        aux = next;
    }

    cola->delante = NULL;
    cola->atras = NULL;
    cola->cantidad = 0;
}
