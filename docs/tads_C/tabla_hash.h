#ifndef TABLA_HASH_H
#define TABLA_HASH_H

#include <stdbool.h>
#include <stddef.h>

/**
 * @file tabla_hash.h
 * @brief API de Tabla Hash con resolución de colisiones por encadenamiento separado.
 */

typedef struct THNodo {
    int clave;
    int valor;
    struct THNodo *siguiente;
} THNodo;

typedef struct {
    THNodo **buckets;
    int capacidad;
    int cantidad;
} TablaHash;

typedef struct {
    int capacidad;
    int cantidad;
    int buckets_ocupados;
    int colisiones;
    float factor_carga;
} THEstadisticas;

/** @brief Inicializa la tabla hash reservando memoria para los buckets. */
void th_inicializar(TablaHash *tabla, int capacidad);
/** @brief Inserta un par clave-valor, actualiza el valor si la clave ya existe. */
bool th_insertar(TablaHash *tabla, int clave, int valor);
/** @brief Busca el valor asociado a una clave. */
bool th_buscar(const TablaHash *tabla, int clave, int *valor);
/** @brief Indica si la clave existe en la tabla. */
bool th_contiene(const TablaHash *tabla, int clave);
/** @brief Elimina una clave y su valor asociado de la tabla. */
bool th_eliminar(TablaHash *tabla, int clave);
/** @brief Elimina todos los elementos de la tabla, manteniendo la capacidad. */
void th_vaciar(TablaHash *tabla);
/** @brief Libera toda la memoria de la tabla (buckets y nodos). */
void th_destruir(TablaHash *tabla);
/** @brief Indica si la tabla está vacía. */
bool th_vacia(const TablaHash *tabla);
/** @brief Retorna la cantidad de pares clave-valor en la tabla. */
int th_cantidad(const TablaHash *tabla);
/** @brief Retorna la capacidad total de la tabla (número de buckets). */
int th_capacidad(const TablaHash *tabla);
/** @brief Retorna el índice del bucket donde caería una clave. */
int th_indice(const TablaHash *tabla, int clave);
/** @brief Genera estadísticas de rendimiento de la tabla. */
THEstadisticas th_estadisticas(const TablaHash *tabla);
/** @brief Formatea el contenido de todos los buckets en una cadena. */
void th_formatear(const TablaHash *tabla, char *destino, size_t capacidad);
/** @brief Formatea las estadísticas en una cadena. */
void th_formatear_estadisticas(const TablaHash *tabla, char *destino, size_t capacidad);

#endif /* TABLA_HASH_H */
