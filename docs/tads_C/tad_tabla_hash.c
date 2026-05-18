#include "tad_tabla_hash.h"
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdarg.h>

/**
 * @file tabla_hash.c
 * @brief Implementación del TAD Tabla Hash.
 */

/**
 * @brief Calcula el índice de bucket para una clave.
 * @param[in] tabla Puntero a la tabla hash.
 * @param[in] clave Clave entera.
 * @return Índice del bucket correspondiente, o -1 si error.
 */
static void th_append_text(char *destino, size_t capacidad, size_t *usado, const char *fmt, ...) {
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

int th_indice(const TablaHash *tabla, int clave) {
    if (!tabla || tabla->capacidad <= 0) return -1;
    int indice = clave % tabla->capacidad;
    if (indice < 0) {
        indice += tabla->capacidad;
    }
    return indice;
}

/**
 * @brief Inicializa la tabla hash.
 * @param[out] tabla Puntero a la tabla hash.
 * @param[in] capacidad Capacidad (número de buckets) de la tabla.
 */
void th_inicializar(TablaHash *tabla, int capacidad) {
    if (!tabla || capacidad <= 0) return;
    
    tabla->capacidad = capacidad;
    tabla->cantidad = 0;
    tabla->buckets = (THNodo **)malloc(capacidad * sizeof(THNodo *));
    
    if (tabla->buckets) {
        for (int i = 0; i < capacidad; i++) {
            tabla->buckets[i] = NULL;
        }
    } else {
        tabla->capacidad = 0; // Error de memoria
    }
}

/**
 * @brief Inserta un par clave-valor, actualizando el valor si la clave existe.
 * @param[in,out] tabla Puntero a la tabla hash.
 * @param[in] clave Clave a insertar.
 * @param[in] valor Valor asociado a la clave.
 * @return true si se insertó o actualizó correctamente, false en error.
 */
bool th_insertar(TablaHash *tabla, int clave, int valor) {
    if (!tabla || !tabla->buckets || tabla->capacidad <= 0) return false;
    
    int indice = th_indice(tabla, clave);
    THNodo *actual = tabla->buckets[indice];
    
    // Buscar si ya existe para actualizar
    while (actual != NULL) {
        if (actual->clave == clave) {
            actual->valor = valor;
            return true;
        }
        actual = actual->siguiente;
    }
    
    // No existe, insertar al principio del bucket
    THNodo *nuevo = (THNodo *)malloc(sizeof(THNodo));
    if (!nuevo) return false;
    
    nuevo->clave = clave;
    nuevo->valor = valor;
    nuevo->siguiente = tabla->buckets[indice];
    tabla->buckets[indice] = nuevo;
    tabla->cantidad++;
    
    return true;
}

/**
 * @brief Busca el valor asociado a una clave.
 * @param[in] tabla Puntero a la tabla hash constante.
 * @param[in] clave Clave a buscar.
 * @param[out] valor Puntero donde se almacenará el valor si se encuentra.
 * @return true si se encontró la clave, false si no.
 */
bool th_buscar(const TablaHash *tabla, int clave, int *valor) {
    if (!tabla || !tabla->buckets || tabla->capacidad <= 0 || !valor) return false;
    
    int indice = th_indice(tabla, clave);
    THNodo *actual = tabla->buckets[indice];
    
    while (actual != NULL) {
        if (actual->clave == clave) {
            *valor = actual->valor;
            return true;
        }
        actual = actual->siguiente;
    }
    
    return false;
}

/**
 * @brief Verifica si una clave existe en la tabla.
 * @param[in] tabla Puntero a la tabla hash.
 * @param[in] clave Clave a verificar.
 * @return true si la clave existe, false si no.
 */
bool th_contiene(const TablaHash *tabla, int clave) {
    int dummy_valor;
    return th_buscar(tabla, clave, &dummy_valor);
}

/**
 * @brief Elimina una clave de la tabla hash.
 * @param[in,out] tabla Puntero a la tabla hash.
 * @param[in] clave Clave a eliminar.
 * @return true si fue eliminada, false si no existía o error.
 */
bool th_eliminar(TablaHash *tabla, int clave) {
    if (!tabla || !tabla->buckets || tabla->capacidad <= 0) return false;
    
    int indice = th_indice(tabla, clave);
    THNodo *actual = tabla->buckets[indice];
    THNodo *anterior = NULL;
    
    while (actual != NULL) {
        if (actual->clave == clave) {
            if (anterior == NULL) {
                tabla->buckets[indice] = actual->siguiente;
            } else {
                anterior->siguiente = actual->siguiente;
            }
            free(actual);
            tabla->cantidad--;
            return true;
        }
        anterior = actual;
        actual = actual->siguiente;
    }
    
    return false;
}

/**
 * @brief Elimina todos los elementos manteniendo la capacidad de la tabla.
 * @param[in,out] tabla Puntero a la tabla hash.
 */
void th_vaciar(TablaHash *tabla) {
    if (!tabla || !tabla->buckets) return;
    
    for (int i = 0; i < tabla->capacidad; i++) {
        THNodo *actual = tabla->buckets[i];
        while (actual != NULL) {
            THNodo *siguiente = actual->siguiente;
            free(actual);
            actual = siguiente;
        }
        tabla->buckets[i] = NULL;
    }
    tabla->cantidad = 0;
}

/**
 * @brief Destruye la tabla hash liberando toda su memoria.
 * @param[in,out] tabla Puntero a la tabla hash.
 */
void th_destruir(TablaHash *tabla) {
    if (!tabla || !tabla->buckets) return;
    
    th_vaciar(tabla);
    free(tabla->buckets);
    tabla->buckets = NULL;
    tabla->capacidad = 0;
    tabla->cantidad = 0;
}

/**
 * @brief Indica si la tabla está vacía.
 * @param[in] tabla Puntero a la tabla hash.
 * @return true si la cantidad es 0, false caso contrario.
 */
bool th_vacia(const TablaHash *tabla) {
    if (!tabla) return true;
    return tabla->cantidad == 0;
}

/**
 * @brief Retorna la cantidad de elementos en la tabla.
 * @param[in] tabla Puntero a la tabla hash.
 * @return Cantidad de elementos almacenados.
 */
int th_cantidad(const TablaHash *tabla) {
    if (!tabla) return 0;
    return tabla->cantidad;
}

/**
 * @brief Retorna la capacidad actual de la tabla.
 * @param[in] tabla Puntero a la tabla hash.
 * @return Capacidad (número de buckets).
 */
int th_capacidad(const TablaHash *tabla) {
    if (!tabla) return 0;
    return tabla->capacidad;
}

/**
 * @brief Calcula y retorna las estadísticas de la tabla hash.
 * @param[in] tabla Puntero a la tabla hash.
 * @return Estructura con las estadísticas calculadas.
 */
THEstadisticas th_estadisticas(const TablaHash *tabla) {
    THEstadisticas stats = {0};
    
    if (!tabla || !tabla->buckets || tabla->capacidad <= 0) return stats;
    
    stats.capacidad = tabla->capacidad;
    stats.cantidad = tabla->cantidad;
    stats.factor_carga = (float)tabla->cantidad / (float)tabla->capacidad;
    
    for (int i = 0; i < tabla->capacidad; i++) {
        THNodo *actual = tabla->buckets[i];
        if (actual != NULL) {
            stats.buckets_ocupados++;
            int nodos_en_bucket = 0;
            while (actual != NULL) {
                nodos_en_bucket++;
                actual = actual->siguiente;
            }
            if (nodos_en_bucket > 1) {
                stats.colisiones += (nodos_en_bucket - 1);
            }
        }
    }
    
    return stats;
}

/**
 * @brief Formatea el contenido de la tabla hash en una cadena de texto.
 * @param[in] tabla Puntero a la tabla hash.
 * @param[out] destino Buffer donde se escribirá la representación.
 * @param[in] capacidad Tamaño máximo del buffer destino.
 */
void th_formatear(const TablaHash *tabla, char *destino, size_t capacidad) {
    if (!destino || capacidad == 0) return;
    destino[0] = '\0';
    
    if (!tabla || !tabla->buckets) {
        snprintf(destino, capacidad, "Tabla no inicializada\n");
        return;
    }
    
    size_t usado = 0;
    for (int i = 0; i < tabla->capacidad && usado < capacidad; i++) {
        th_append_text(destino, capacidad, &usado, "[%d] -> ", i);
        
        THNodo *actual = tabla->buckets[i];
        while (actual != NULL && usado < capacidad) {
            th_append_text(destino, capacidad, &usado, "(%d:%d) -> ", actual->clave, actual->valor);
            actual = actual->siguiente;
        }
        
        if (usado < capacidad) {
            th_append_text(destino, capacidad, &usado, "NULL\n");
        }
    }
}

/**
 * @brief Formatea las estadísticas de la tabla en una cadena de texto.
 * @param[in] tabla Puntero a la tabla hash.
 * @param[out] destino Buffer donde se escribirá la representación.
 * @param[in] capacidad Tamaño máximo del buffer destino.
 */
void th_formatear_estadisticas(const TablaHash *tabla, char *destino, size_t capacidad) {
    if (!destino || capacidad == 0) return;
    destino[0] = '\0';
    
    if (!tabla || !tabla->buckets) {
        snprintf(destino, capacidad, "Tabla no inicializada\n");
        return;
    }
    
    THEstadisticas stats = th_estadisticas(tabla);
    snprintf(destino, capacidad, 
             "Capacidad: %d\n"
             "Cantidad: %d\n"
             "Buckets ocupados: %d\n"
             "Colisiones: %d\n"
             "Factor de carga: %.2f\n",
             stats.capacidad, stats.cantidad, stats.buckets_ocupados, 
             stats.colisiones, stats.factor_carga);
}
