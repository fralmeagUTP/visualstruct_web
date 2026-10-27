#ifndef TAD_PILA_H
#define TAD_PILA_H

/**
 * @file tad_pila.h
 * @brief TAD Pila enlazada de enteros.
 * @details Define el tipo abstracto de datos Pila y sus operaciones basicas.
 */

/** @brief Nodo de la pila enlazada. */
typedef struct NodoPila {
    int nro; /**< Dato entero almacenado. */
    struct NodoPila *sgte; /**< Enlace al siguiente nodo. */
} *ptrPila;

/**
 * @brief Reserva un nodo y lo publica como nueva cima.
 * @param[in,out] p Direccion prestada de la cabeza; NULL se diagnostica sin escritura.
 * @param[in] valor Entero a almacenar, incluido -1.
 * @pre Si p no es NULL, *p es NULL o una lista propia valida, viva y aciclica.
 * @note Fallo malloc imprime diagnostico y conserva *p. Retorno void no comunica exito.
 * @note El nodo nuevo pertenece a la pila; destruir o desapilar lo libera. No inicializa una cabeza indeterminada.
 */
void pila_apilar(ptrPila *p, int valor);

/**
 * @brief Copia el dato de cima, actualiza la cabeza y libera el nodo retirado.
 * @param[in,out] p Direccion prestada de cabeza o NULL.
 * @return Dato retirado; -1 ante p NULL o *p NULL con diagnostico en stdout. -1 tambien es un dato valido.
 * @pre Si hay nodos, deben ser vivos, propios y formar una lista aciclica.
 * @note No reserva memoria. Los aliases al nodo retirado quedan invalidos. Comprobar no vacia antes de usar el retorno como dato.
 */
int pila_desapilar(ptrPila *p);
/**
 * @brief Consulta el dato de cima sin cambiar enlaces.
 * @param[in] p Cabeza prestada viva o NULL.
 * @return Dato de cima o -1 si p es NULL; -1 no distingue vacio de dato almacenado.
 * @note No reserva, libera ni imprime. No valida punteros colgantes.
 */
int pila_cima(ptrPila p);

/**
 * @brief Imprime los datos de cima a fondo sin modificar nodos.
 * @param[in] p Lista prestada viva, aciclica o NULL.
 * @note NULL imprime el mensaje de pila vacia; cada dato se imprime con tabulacion y salto de linea. No reserva ni libera.
 */
void pila_mostrar(ptrPila p);

/**
 * @brief Libera todos los nodos y deja la cabeza en NULL.
 * @param[in,out] p Direccion de lista propia viva y aciclica; NULL se ignora.
 * @note No reserva ni imprime. Los aliases a nodos liberados dejan de ser validos; una copia externa de la cabeza no se actualiza.
 */
void pila_destruir(ptrPila *p);

#endif
