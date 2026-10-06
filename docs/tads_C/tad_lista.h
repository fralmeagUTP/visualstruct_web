#ifndef TAD_LISTA_H
#define TAD_LISTA_H

/**
 * @file tad_lista.h
 * @brief TAD Lista simplemente enlazada de enteros.
 */

/** @brief Nodo de la lista enlazada. */
typedef struct NodoLista {
    int nro; /**< Dato entero almacenado. */
    struct NodoLista *sgte; /**< Enlace al siguiente nodo. */
} *Tlista;

/**
 * @brief Reserva e inserta un nodo al inicio de la cadena.
 * @param[in,out] lista Dirección de la variable cabeza del llamador; *lista puede ser NULL.
 * @param[in] valor Dato entero a insertar; se admiten valores repetidos.
 * @post En éxito, la nueva cabeza contiene valor y enlaza con la cabeza anterior.
 * @note Si lista es NULL no hace nada. Si malloc falla, conserva la cadena y escribe un diagnóstico en stdout.
 */
void lista_insertar_inicio(Tlista *lista, int valor);

/**
 * @brief Reserva e inserta un nodo al final de la cadena.
 * @param[in,out] lista Dirección de la variable cabeza del llamador; *lista puede ser NULL.
 * @param[in] valor Dato entero a insertar; se admiten valores repetidos.
 * @post En éxito, la cadena vacía recibe una cabeza; en otra cadena cambia el enlace del último nodo.
 * @note Si lista es NULL no hace nada. Si malloc falla, conserva la cadena y escribe un diagnóstico en stdout.
 */
void lista_insertar_final(Tlista *lista, int valor);

/**
 * @brief Inserta al inicio para pos=1, o después del nodo en la posición base pos.
 * @param[in,out] lista Dirección de la variable cabeza del llamador; *lista puede ser NULL.
 * @param[in] valor Dato entero a insertar; se admiten valores repetidos.
 * @param[in] pos Posición base: 1 incluso en lista vacía, o 2..n si existe el nodo base.
 * @note pos=1 no significa insertar después del primer nodo: inserta al inicio.
 * @note Si lista es NULL o pos<=0, retorna sin reservar ni modificar la cadena.
 * @note Un fallo de malloc conserva la cadena y escribe un diagnóstico en stdout.
 * @note Si no existe la posición base, escribe un diagnóstico, libera el nodo temporal y conserva la cadena.
 */
void lista_insertar_elemento(Tlista *lista, int valor, int pos);

/**
 * @brief Recorre toda la cadena e imprime las posiciones de todas las coincidencias.
 * @param[in] lista Cabeza de la cadena por valor; NULL representa lista vacía.
 * @param[in] valor Dato buscado.
 * @post No modifica nodos ni enlaces; las posiciones impresas comienzan en 1.
 * @note Es void: comunica las coincidencias mediante stdout, no devuelve una colección C.
 * @note Si no hay coincidencias, incluida la lista vacía, imprime Numero no encontrado.
 */
void lista_buscar_elemento(Tlista lista, int valor);

/**
 * @brief Imprime todos los elementos de la lista.
 * @param[in] lista Lista a mostrar.
 * @pre Lista prestada viva y aciclica; contador de posiciones debe caber en int durante todo recorrido.
 * @note Imprime posicion desde 1 y dato por linea; lista NULL no imprime nada. No reserva/libera ni modifica nodos.
 */
void lista_mostrar(Tlista lista);

/**
 * @brief Desconecta y libera únicamente la primera ocurrencia del valor.
 * @param[in,out] lista Dirección de la variable cabeza del llamador; *lista puede ser NULL.
 * @param[in] valor Dato cuya primera coincidencia se elimina.
 * @post Si hay coincidencia, reconecta la cabeza o el enlace anterior antes de free; las restantes ocurrencias se conservan.
 * @note Si lista es NULL, la cadena está vacía o no existe el valor, escribe un diagnóstico en stdout y no modifica la cadena.
 * @note No devuelve un estado de éxito: su tipo de retorno C es void.
 */
void lista_eliminar_elemento(Tlista *lista, int valor);

/**
 * @brief Desconecta y libera todas las ocurrencias del valor solicitado.
 * @param[in,out] lista Dirección de la variable cabeza del llamador; *lista puede ser NULL.
 * @param[in] valor Dato cuyas coincidencias se eliminan, incluso si solo hay una.
 * @post Conserva el orden y los nodos de los demás valores; no deja una copia del valor eliminado.
 * @note Si lista es NULL o la cadena está vacía, no modifica nodos. Imprime Valores eliminados también si no encontró coincidencias.
 * @note Es void: no devuelve un contador en C; el contador de la aplicación es información adicional del wrapper.
 */
void lista_eliminar_repetidos(Tlista *lista, int valor);

/**
 * @brief Desconecta y libera todos los nodos; deja la cabeza en NULL.
 * @param[in,out] lista Dirección de la variable cabeza del llamador; *lista puede ser NULL.
 * @post Cada nodo se desconecta de la cabeza antes de free(q); una cabeza inicialmente NULL permanece NULL.
 * @note Si lista es NULL retorna sin hacer nada. No escribe en stdout.
 * @note q es un alias local; después de free(q) su valor es indeterminado hasta la siguiente asignación. No se lee durante ese intervalo.
 */
void lista_limpiar(Tlista *lista);
/**
 * @brief Desenlaza y libera el primer nodo.
 * @param lista Dirección de la cabeza que se actualiza.
 * @param valor Salida del dato eliminado; no debe ser NULL.
 * @return 1 al eliminar; 0 ante lista vacía o punteros NULL.
 * @pre Lista propia viva y aciclica; lista es direccion escribible de cabeza y valor int externo escribible sin solaparse con cabeza/nodos.
 * @note Guardas NULL/vacio/indice inexistente retornan 0 sin escribir valor ni liberar. Exito retorna 1, copia dato, cambia enlaces y libera un nodo; aliases al nodo quedan invalidos. No reserva ni imprime.
 */
int lista_eliminar_inicio(Tlista *lista, int *valor);
/**
 * @brief Desenlaza y libera el último nodo.
 * @param lista Dirección de la cabeza que puede actualizarse.
 * @param valor Salida del dato eliminado; no debe ser NULL.
 * @return 1 al eliminar; 0 ante lista vacía o punteros NULL.
 * @pre Lista propia viva y aciclica; lista es direccion escribible de cabeza y valor int externo escribible sin solaparse con cabeza/nodos.
 * @note Guardas NULL/vacio/indice inexistente retornan 0 sin escribir valor ni liberar. Exito retorna 1, copia dato, cambia enlaces y libera un nodo; aliases al nodo quedan invalidos. No reserva ni imprime.
 */
int lista_eliminar_final(Tlista *lista, int *valor);
/**
 * @brief Desenlaza y libera el nodo en un índice basado en cero.
 * @param lista Dirección de la cabeza.
 * @param posicion Índice: cero identifica el primer nodo.
 * @param valor Salida del dato eliminado; no debe ser NULL.
 * @return 1 al eliminar; 0 ante índice fuera de rango o punteros NULL.
 * @pre Lista propia viva y aciclica; lista es direccion escribible de cabeza y valor int externo escribible sin solaparse con cabeza/nodos.
 * @note Guardas NULL/vacio/indice inexistente retornan 0 sin escribir valor ni liberar. Exito retorna 1, copia dato, cambia enlaces y libera un nodo; aliases al nodo quedan invalidos. No reserva ni imprime.
 * @note Posicion basada en cero; negativa retorna 0. No es el contrato posicional de lista_insertar_elemento.
 */
int lista_eliminar_posicion(Tlista *lista, int posicion, int *valor);

/**
 * @brief Consulta el primer dato sin modificar enlaces.
 * @param lista Cabeza de la lista.
 * @param valor Salida del dato consultado.
 * @return 1 si existe el nodo y valor no es NULL; 0 en otro caso.
 * @pre Lista prestada viva y aciclica; valor es int externo escribible sin solaparse con nodos.
 * @note Lista NULL o valor NULL retorna 0 sin escritura. Exito retorna 1 y escribe dato; no reserva/libera/imprime ni modifica enlaces bajo precondiciones.
 */
int lista_primero(Tlista lista, int *valor);
/**
 * @brief Consulta el último dato sin modificar enlaces.
 * @param lista Cabeza de la lista.
 * @param valor Salida del dato consultado.
 * @return 1 si existe el nodo y valor no es NULL; 0 en otro caso.
 * @pre Lista prestada viva y aciclica; valor es int externo escribible sin solaparse con nodos.
 * @note Lista NULL o valor NULL retorna 0 sin escritura. Exito retorna 1 y escribe dato; no reserva/libera/imprime ni modifica enlaces bajo precondiciones.
 */
int lista_ultimo(Tlista lista, int *valor);

#endif
