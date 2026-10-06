#ifndef COLA_PRIORIDAD_H
#define COLA_PRIORIDAD_H

#include <stdbool.h>
#include <stddef.h>

/**
 * @file tad_cola_prioridad.h
 * @brief TAD Cola de prioridad basada en lista enlazada.
 */

/** @brief Nodo interno de la cola de prioridad. */
typedef struct cp_nodo CPNodo;

/** @brief Estructura principal de cola de prioridad. */
typedef struct {
    CPNodo *delante; /**< Primer nodo de la cola; NULL si está vacía. */
    CPNodo *atras; /**< Último nodo de la cola; NULL si está vacía. */
    int cantidad; /**< Número de elementos almacenados. */
} ColaPrioridad;

/**
 * @brief Escribe el estado vacio sin reservar ni liberar nodos.
 * @param[out] cola Direccion valida de estructura o NULL (sin efecto).
 * @pre Antes del primer uso; si ya tiene nodos, vaciarlos antes de reinicializar.
 * @note Reinicializar una cola no vaciada pierde sus referencias y no libera los nodos. Delante/atras NULL y cantidad cero.
 */
void cp_inicializar(ColaPrioridad *cola);
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
bool cp_encolar(ColaPrioridad *cola, int valor, int prioridad);
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
bool cp_desencolar(ColaPrioridad *cola, int *valor, int *prioridad);
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
bool cp_frente(const ColaPrioridad *cola, int *valor, int *prioridad);
/**
 * @brief Consulta las guardas de vacio sin modificar la cola.
 * @param[in] cola Estructura prestada inicializada o NULL.
 * @return true si cola NULL, delante NULL o cantidad cero; false en otro caso.
 * @note No recorre nodos ni valida consistencia; no reserva, libera ni imprime.
 */
bool cp_vacia(const ColaPrioridad *cola);
/**
 * @brief Devuelve el contador almacenado de la cola.
 * @param[in] cola Estructura prestada inicializada o NULL.
 * @return 0 ante NULL; en otro caso cantidad sin recorrer ni corregir el contador.
 * @note En cola consistente es el numero de nodos. No valida corrupcion ni modifica memoria.
 */
int cp_contar(const ColaPrioridad *cola);
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
int cp_copiar_items(const ColaPrioridad *cola, int *valores, int *prioridades, int capacidad);
/**
 * @brief Escribe la representacion textual en orden de llegada.
 * @param[in] cola Cola prestada inicializada o NULL (texto vacio).
 * @param[out] destino Buffer externo escribible; NULL se ignora.
 * @param[in] capacidad Bytes disponibles incluyendo terminador; cero se ignora.
 * @pre Buffer de al menos capacidad bytes, sin solaparse con la cola.
 * @note Con destino valido y capacidad positiva inicializa y termina con NUL; trunca a capacidad-1 caracteres. Capacidad 1 produce cadena vacia.
 * @note No reserva/libera ni imprime stdout. No ordena por prioridad; NULL o delante NULL escribe Cola de prioridad vacia.
 */
void cp_formatear(const ColaPrioridad *cola, char *destino, size_t capacidad);
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
void cp_vaciar(ColaPrioridad *cola);

#endif
