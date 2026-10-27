#ifndef TADCOLA_H
#define TADCOLA_H

/**
 * @file tad_cola.h
 * @brief TAD Cola FIFO enlazada de enteros.
 */

/** @brief Nodo de la cola enlazada. */
struct NodoCola {
    int nro; /**< Dato entero almacenado. */
    struct NodoCola *sgte; /**< Enlace al siguiente nodo. */
};

/** @brief Estructura principal de la cola FIFO. */
struct Cola {
    struct NodoCola *delante; /**< Primer nodo de la cola. */
    struct NodoCola *atras; /**< Último nodo de la cola. */
};

/**
 * @brief Reserva y publica un nuevo nodo al final de la FIFO.
 * @param[in,out] q Direccion prestada de una cola inicializada y consistente.
 * @param valor Entero a almacenar, incluidos negativos y -1.
 * @note NULL q imprime error y retorna sin escritura. Fallo malloc imprime error y
 *       conserva la cola. El retorno void no comunica exito al caller.
 * @note La cola recibe propiedad del nodo; desencolar o vaciar lo libera.
 */
void cola_encolar(struct Cola *q, int valor);

/**
 * @brief Copia el dato del frente, retira su enlace y libera exactamente ese nodo.
 * @param[in,out] q Direccion prestada de una FIFO consistente, o NULL.
 * @return Dato extraido; -1 tambien es un dato valido. Ante q NULL/cola vacia,
 *         imprime diagnostico y devuelve -1 sin cambiar enlaces.
 * @note Compruebe la cola no vacia antes de extraer; el valor -1 no distingue error.
 * @note Los aliases al nodo liberado dejan de ser utilizables; q sigue valido.
 */
int cola_desencolar(struct Cola *q);

/**
 * @brief Imprime la FIFO de delante a atras sin modificar nodos.
 * @param[in] q Copia prestada de cola con lista viva y aciclica.
 * @note Siempre imprime prefijo Cola: y salto de linea, incluso vacia. No reserva ni libera.
 */
void cola_mostrar(struct Cola q);

/**
 * @brief Libera la lista y pone delante y atras en NULL.
 * @param[in,out] q Direccion prestada de cola propia consistente; NULL se ignora.
 * @note Cada nodo debe ser vivo, propio y no compartido con otra estructura propietaria. No reserva ni imprime; aliases a nodos liberados quedan invalidos.
 */
void cola_vaciar(struct Cola *q);

/**
 * @brief Consulta el dato de delante sin modificar la cola.
 * @param[in] q Copia prestada de cola consistente.
 * @return Dato del primer nodo o -1 si delante es NULL; -1 tambien es dato valido.
 * @note No reserva, libera ni imprime. Requiere punteros vivos cuando no son NULL.
 */
int cola_frente(struct Cola q);
/**
 * @brief Consulta el dato de atras sin modificar la cola.
 * @param[in] q Copia prestada de cola consistente.
 * @return Dato del ultimo nodo o -1 si atras es NULL; -1 tambien es dato valido.
 * @note Consulta atras directamente, no recorre ni valida consistencia frente/final. No reserva, libera ni imprime.
 */
int cola_final(struct Cola q);

#endif
