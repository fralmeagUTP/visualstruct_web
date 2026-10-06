#ifndef LISTA_CIRCULAR_H
#define LISTA_CIRCULAR_H

#include <stdbool.h>
#include <stddef.h>

/**
 * @file tad_lista_circular.h
 * @brief TAD Lista circular simple de enteros.
 */

/** @brief Nodo interno de la lista circular. */
typedef struct lcir_nodo LCirNodo;

/** @brief Estructura principal de lista circular. */
typedef struct {
    LCirNodo *cabeza; /**< Primer nodo del anillo; NULL si está vacío. */
    LCirNodo *cola; /**< Último nodo del anillo; NULL si está vacío. */
    int cantidad; /**< Número de elementos almacenados. */
} ListaCircular;

/**
 * @brief Inicializa la estructura principal de la lista circular vacía.
 *
 * @param[in,out] lista Puntero a la estructura de la lista circular.
 *
 * @post Con lista no nula, cabeza y cola quedan en NULL y cantidad en 0.
 * @note Si lista es NULL, retorna sin modificar memoria.
 * @note Complejidad temporal: O(1).
 */
void lcir_inicializar(ListaCircular *lista);
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
bool lcir_insertar_inicio(ListaCircular *lista, int valor);
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
bool lcir_insertar_final(ListaCircular *lista, int valor);
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
int lcir_buscar_posiciones(const ListaCircular *lista, int valor, int *destino, int capacidad);
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
bool lcir_eliminar_inicio(ListaCircular *lista);
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
bool lcir_eliminar_primero(ListaCircular *lista, int valor);
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
void lcir_invertir(ListaCircular *lista);
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
bool lcir_vacia(const ListaCircular *lista);
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
int lcir_contar(const ListaCircular *lista);
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
int lcir_copiar_valores(const ListaCircular *lista, int *destino, int capacidad);
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
void lcir_formatear(const ListaCircular *lista, char *destino, size_t capacidad);
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
void lcir_destruir(ListaCircular *lista);

#endif
