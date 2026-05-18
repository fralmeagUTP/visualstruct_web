#ifndef TABLA_HASH_H
#define TABLA_HASH_H

#include <stdbool.h>
#include <stddef.h>

/**
 * @file tad_tabla_hash.h
 * @brief TAD Tabla Hash con encadenamiento separado.
 */

/** @brief Nodo de una lista de colision. */
typedef struct th_nodo {
    int clave;                 
    int valor;                 
    struct th_nodo *siguiente; 
} THNodo;

/** @brief Estructura principal de la tabla hash. */
typedef struct {
    THNodo **buckets; 
    int capacidad;    
    int cantidad;     
} TablaHash;

/** @brief Estadisticas de ocupacion y colisiones. */
typedef struct {
    int capacidad;        
    int cantidad;         
    int buckets_ocupados; 
    int colisiones;       
    float factor_carga;  
} THEstadisticas;

int th_indice(const TablaHash *tabla, int clave);
void th_inicializar(TablaHash *tabla, int capacidad);
bool th_insertar(TablaHash *tabla, int clave, int valor);
bool th_buscar(const TablaHash *tabla, int clave, int *valor);
bool th_contiene(const TablaHash *tabla, int clave);
bool th_eliminar(TablaHash *tabla, int clave);
void th_vaciar(TablaHash *tabla);
void th_destruir(TablaHash *tabla);
bool th_vacia(const TablaHash *tabla);
int th_cantidad(const TablaHash *tabla);
int th_capacidad(const TablaHash *tabla);
THEstadisticas th_estadisticas(const TablaHash *tabla);
void th_formatear(const TablaHash *tabla, char *destino, size_t capacidad);
void th_formatear_estadisticas(const TablaHash *tabla, char *destino, size_t capacidad);

#endif
