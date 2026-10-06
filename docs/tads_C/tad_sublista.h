#ifndef SUBLISTA_H
#define SUBLISTA_H

#include <stdbool.h>
#include <stddef.h>

/**
 * @file tad_sublista.h
 * @brief TAD Lista de padres con sublista de hijos.
 */

/** @brief Nodo hijo de una sublista. */
typedef struct Sublista {
    int nro; /**< Dato entero almacenado. */
    struct Sublista *sgte; /**< Enlace al siguiente nodo. */
} Sublista;

/** @brief Nodo padre de la lista principal. */
typedef struct Nodo {
    int nro; /**< Dato entero almacenado. */
    struct Nodo *sgte; /**< Enlace al siguiente nodo. */
    Sublista *sub; /**< Cabeza de la sublista asociada. */
} Nodo;

/**
 * @brief Inicializa la lista principal de nodos padre estableciéndola en NULL.
 * @param[out] lista Doble puntero a la lista a inicializar.
 * @note Con lista NULL no accede a memoria. Solo asigna NULL: no libera una cadena previamente existente; el llamador debe destruirla o conservar su referencia.
 */
void sublista_inicializar(Nodo **lista);
/**
 * @brief Inserta un nuevo nodo padre al final de la lista principal.
 * @param[in,out] lista       Doble puntero a la lista principal.
 * @param[in]     valor_padre Valor del nuevo padre.
 * @return Puntero al nuevo nodo insertado, o NULL si falla.
 * @note Admite valores repetidos como reservas distintas. Con lista NULL o malloc fallido retorna NULL sin modificar la cadena.
 */
Nodo *sublista_insertar_padre_final(Nodo **lista, int valor_padre);
/**
 * @brief Busca un nodo padre por su valor.
 * @param[in] lista       Puntero al primer nodo de la lista.
 * @param[in] valor_padre Valor a buscar.
 * @return Puntero al nodo padre encontrado, o NULL si no existe.
 * @note Devuelve la primera coincidencia desde la cabeza. Con lista NULL retorna NULL; no modifica nodos ni enlaces.
 */
Nodo *sublista_buscar_padre(Nodo *lista, int valor_padre);
/**
 * @brief Elimina la primera ocurrencia de un nodo padre y todos sus hijos.
 * @param[in,out] lista       Doble puntero a la lista.
 * @param[in]     valor_padre Valor del padre a eliminar.
 * @return true si fue eliminado con éxito, false si no se encontró.
 * @note Libera los hijos uno a uno y después el primer padre coincidente; conserva los demás padres. Con lista NULL o cabeza NULL retorna false sin cambios. Alias externos a las reservas liberadas dejan de ser válidos.
 */
bool sublista_eliminar_padre_primero(Nodo **lista, int valor_padre);
/**
 * @brief Cuenta el número de nodos padre en la lista.
 * @param[in] lista Puntero constante a la lista.
 * @return Cantidad de nodos padre.
 * @note Con lista NULL retorna 0. Recorre una cadena válida sin modificarla.
 */
int sublista_contar_padres(const Nodo *lista);
/**
 * @brief Inserta un nuevo nodo hijo al final de la sublista de un padre.
 * @param[in,out] padre      Puntero al nodo padre.
 * @param[in]     valor_hijo Valor del nuevo hijo.
 * @return true si se insertó exitosamente, false en caso de error.
 * @note Con padre NULL o malloc fallido retorna false sin cambiar enlaces. Los hijos repetidos ocupan reservas distintas.
 */
bool sublista_insertar_hijo_final(Nodo *padre, int valor_hijo);
/**
 * @brief Busca el padre por valor e inserta al final de su sublista.
 * @param[in,out] lista Lista principal de padres.
 * @param[in] valor_padre Valor del padre destino.
 * @param[in] valor_hijo Valor del nuevo hijo.
 * @return true si el padre existe y el hijo se inserta; false en otro caso.
 * @note Busca el primer padre coincidente. Si no existe o falla la reserva retorna false, sin crear hijos huérfanos ni modificar otras ramas.
 */
bool sublista_insertar_hijo(Nodo *lista, int valor_padre, int valor_hijo);
/**
 * @brief Busca un nodo hijo dentro de una sublista por su valor.
 * @param[in] lista_hijos Puntero al primer nodo de la sublista.
 * @param[in] valor_hijo  Valor a buscar.
 * @return Puntero al hijo encontrado, o NULL si no existe.
 * @note Devuelve la primera coincidencia. Una cabeza NULL produce NULL; no modifica la sublista.
 */
Sublista *sublista_buscar_hijo(Sublista *lista_hijos, int valor_hijo);
/**
 * @brief Elimina la primera ocurrencia de un hijo en la sublista de un padre.
 * @param[in,out] padre      Puntero al nodo padre.
 * @param[in]     valor_hijo Valor del hijo a eliminar.
 * @return true si se eliminó correctamente, false si no se encontró.
 * @note Libera solo la primera coincidencia; conserva el padre y los demás hijos.
 * @note Con padre NULL o sin hijos retorna false sin modificar memoria.
 */
bool sublista_eliminar_hijo_primero(Nodo *padre, int valor_hijo);
/**
 * @brief Busca el padre por valor y elimina la primera coincidencia de hijo.
 * @param[in,out] lista Lista principal de padres.
 * @param[in] valor_padre Valor del padre destino.
 * @param[in] valor_hijo Valor del hijo a eliminar.
 * @return true si se elimina un hijo; false si no existe padre o hijo.
 * @note Opera sobre el primer padre coincidente; no elimina otras coincidencias.
 * @note La lista se pasa por valor, pero los enlaces de sus hijos pueden cambiar.
 */
bool sublista_eliminar_hijo(Nodo *lista, int valor_padre, int valor_hijo);
/**
 * @brief Cuenta cuántos hijos tiene un nodo padre.
 * @param[in] padre Puntero constante al padre.
 * @return Número de hijos del padre.
 * @note Con padre NULL retorna 0; no modifica campos ni enlaces.
 */
int sublista_contar_hijos(const Nodo *padre);
/**
 * @brief Copia los valores de los hijos de un padre a un arreglo.
 * @param[in]  padre     Puntero constante al padre.
 * @param[out] destino   Arreglo donde se copiarán los valores.
 * @param[in]  capacidad Tamaño máximo del arreglo destino.
 * @return El número de elementos copiados.
 * @note Copia como máximo capacidad valores y retorna los copiados, no el total de hijos si el arreglo es menor. Con padre NULL, destino NULL o capacidad no positiva retorna 0 sin escribir. Las posiciones restantes del arreglo no se inicializan.
 */
int sublista_copiar_hijos(const Nodo *padre, int *destino, int capacidad);
/**
 * @brief Copia los hijos del primer padre con el valor indicado.
 * @param[in] lista Lista principal de padres.
 * @param[in] valor_padre Valor del padre buscado.
 * @param[out] destino Arreglo que recibe los valores de los hijos.
 * @param[in] capacidad Capacidad del arreglo destino.
 * @return Cantidad copiada, o -1 si no existe el padre.
 * @note Consulta solo el primer padre coincidente. Si no existe retorna -1; si existe pero destino es NULL o capacidad no positiva retorna 0 sin escribir. No modifica la estructura.
 */
int sublista_obtener_hijos(Nodo *lista, int valor_padre, int *destino, int capacidad);
/**
 * @brief Genera una representación textual de la lista y sus sublistas.
 * @param[in]  lista     Puntero constante a la lista de padres.
 * @param[out] destino   Buffer para escribir la cadena resultante.
 * @param[in]  capacidad Capacidad máxima del buffer.
 * @note Con destino NULL o capacidad 0 no escribe. Con capacidad positiva la salida queda terminada en NUL y puede truncarse; una lista NULL se representa como Lista padre vacia. No modifica la estructura.
 */
void sublista_formatear(const Nodo *lista, char *destino, size_t capacidad);
/**
 * @brief Libera completamente la memoria de todos los padres y sus respectivos hijos.
 * @param[in,out] lista Doble puntero a la lista principal.
 * @note Con lista NULL no accede a memoria. Libera los hijos de cada padre antes de ese padre, deja la cabeza NULL y no altera listas ajenas. Alias externos a nodos liberados dejan de ser válidos.
 */
void sublista_destruir(Nodo **lista);

#endif
