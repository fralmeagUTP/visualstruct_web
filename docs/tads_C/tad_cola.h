#ifndef TADCOLA_H
#define TADCOLA_H

/**
 * @file tad_cola.h
 * @brief TAD Cola FIFO enlazada de enteros.
 */

/** @brief Nodo de la cola enlazada. */
struct NodoCola {
    int nro;                     
    struct NodoCola *sgte;       
};

/** @brief Estructura principal de la cola FIFO. */
struct Cola {
    struct NodoCola *delante;    
    struct NodoCola *atras;      
};

/**
 * @brief Inserta un elemento al final de la cola.
 * @param[in,out] q Cola destino.
 * @param[in] valor Valor a encolar.
 */
void cola_encolar(struct Cola *q, int valor);

/**
 * @brief Extrae el elemento del cola_frente de la cola.
 * @param[in,out] q Cola origen.
 * @return Valor extraido, o -1 si no se puede extraer.
 */
int cola_desencolar(struct Cola *q);

/**
 * @brief Imprime todos los elementos de la cola.
 * @param[in] q Cola a mostrar.
 */
void cola_mostrar(struct Cola q);

/**
 * @brief Libera todos los nodos de la cola.
 * @param[in,out] q Cola a vaciar.
 */
void cola_vaciar(struct Cola *q);

/**
 * @brief Obtiene el valor del cola_frente sin eliminarlo.
 * @param[in] q Cola origen.
 * @return Valor en cola_frente, o -1 si la cola esta vacia.
 */
int cola_frente(struct Cola q);

#endif
