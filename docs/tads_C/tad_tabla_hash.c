#include "tad_tabla_hash.h"
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdarg.h>

/**
 * @file tad_tabla_hash.c
 * @brief Implementación del TAD Tabla Hash.
 */

/**
 * @brief Ajunta texto formateado dentro de un buffer acotado.
 * @param destino Buffer de salida.
 * @param capacidad Tamaño total del buffer, incluido el terminador.
 * @param usado Contador de bytes usados que se actualiza o satura a capacidad.
 * @param fmt Formato de vsnprintf para los argumentos variables.
 * @pre Buffer externo escribible de capacidad bytes; usado es size_t escribible; formato/argumentos validos de vsnprintf; salidas/formato no se solapan.
 * @note NULL destino/usado o *usado >= capacidad se ignoran. Error vsnprintf no incrementa usado; truncamiento lo satura a capacidad, no a longitud real. No reserva/libera ni imprime stdout.
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

/**
 * @brief Normaliza el módulo de una clave, incluidas claves negativas.
 * @param tabla Tabla con capacidad positiva.
 * @param clave Clave entera.
 * @return Índice entre 0 y capacidad-1, o -1 ante tabla NULL o capacidad no positiva.
 * @note Consulta capacidad sin acceder a buckets; admite INT_MIN y claves negativas. No reserva, libera ni modifica la tabla.
 */
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
 * @pre Estructura sin recursos propietarios pendientes; capacidad * sizeof(THNodo*) debe caber en size_t.
 * @note NULL tabla o capacidad <= 0 retorna sin escribir: no inicializa una estructura indeterminada. No libera recursos previos: destruir antes de reinicializar.
 * @note Con capacidad positiva fija cantidad=0; malloc fallido deja buckets=NULL y capacidad=0. Retorno void no comunica exito. No rehash.
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
 * @pre Tabla inicializada con buckets validos y cadenas propias vivas aciclicas, contadores consistentes; cantidad+1 cabe en int al insertar clave nueva.
 * @note NULL tabla/buckets o capacidad <= 0 retorna false. Actualizar no reserva ni cambia cantidad; insertar publica nodo propio al inicio. Fallo malloc retorna false sin mutacion. Capacidad fija: no rehash.
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
 * @pre Tabla inicializada con cadenas vivas aciclicas; valor es int externo escribible sin solaparse con nodos/metadata.
 * @note NULL tabla/buckets/valor o capacidad <= 0 retorna false. False no escribe salida. No reserva/libera/imprime ni cambia tabla bajo precondiciones.
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
 * @pre Tabla inicializada con buckets y cadenas vivas aciclicas o NULL.
 * @note Delega a th_buscar con salida local; false para tabla no utilizable. No reserva/libera ni imprime.
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
 * @pre Tabla inicializada, propia y consistente; cadenas vivas aciclicas sin ownership compartido.
 * @note NULL tabla/buckets o capacidad <= 0 retorna false. Elimina primera coincidencia, libera un nodo y decrementa cantidad; ausencia conserva tabla. Aliases a nodo liberado quedan invalidos. No rehash.
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
 * @pre Tabla inicializada, propia y consistente con capacidad entradas de buckets y cadenas vivas aciclicas.
 * @note NULL tabla/buckets no escribe ni normaliza metadata. Libera nodos, pone buckets individuales NULL y cantidad=0; conserva arreglo y capacidad. Aliases a nodos liberados quedan invalidos.
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
 * @pre Tabla inicializada, propia y consistente; nodos y arreglo son reservas liberables sin compartir ownership.
 * @note NULL tabla/buckets se ignoran sin normalizar metadata. Tras vaciar y liberar arreglo fija buckets=NULL, capacidad=cantidad=0. No libera estructura prestada. Aliases a nodos/arreglo quedan invalidos.
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
 * @return true si tabla es NULL o cantidad==0; false en otro caso.
 * @note Consulta contador sin recorrer buckets ni validar corrupcion. No reserva/libera/modifica.
 */
bool th_vacia(const TablaHash *tabla) {
    if (!tabla) return true;
    return tabla->cantidad == 0;
}


/**
 * @brief Retorna la cantidad de elementos en la tabla.
 * @param[in] tabla Puntero a la tabla hash.
 * @return 0 ante tabla NULL; de otro modo contador almacenado cantidad, sin normalizacion ni recount.
 * @note Estructura prestada inicializada; no reserva/libera/modifica.
 */
int th_cantidad(const TablaHash *tabla) {
    if (!tabla) return 0;
    return tabla->cantidad;
}


/**
 * @brief Retorna la capacidad actual de la tabla.
 * @param[in] tabla Puntero a la tabla hash.
 * @return 0 ante tabla NULL; de otro modo capacidad almacenada, sin normalizacion.
 * @note Estructura prestada inicializada; no reserva/libera/modifica.
 */
int th_capacidad(const TablaHash *tabla) {
    if (!tabla) return 0;
    return tabla->capacidad;
}


/**
 * @brief Calcula y retorna las estadísticas de la tabla hash.
 * @param[in] tabla Puntero a la tabla hash.
 * @return Estructura con las estadísticas calculadas.
 * @pre Si utilizable, capacidad entradas de buckets, cadenas vivas aciclicas y contadores representables en int.
 * @note Devuelve todos los campos cero ante tabla/buckets NULL o capacidad <= 0. Cantidad se lee de metadata; factor_carga es cantidad/capacidad float. Colisiones suma nodos menos uno por bucket ocupado. No reserva/libera/modifica.
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
 * @pre Buffer externo de al menos capacidad bytes sin solaparse con tabla/nodos; tabla inicializada y cadenas vivas aciclicas si no NULL.
 * @note NULL destino o capacidad cero no escriben. Buffer valido positivo termina en NUL; trunca a capacidad-1 caracteres y capacidad 1 produce cadena vacia. Tabla/buckets NULL escribe Tabla no inicializada. No reserva/libera ni imprime stdout.
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
 * @pre Buffer externo de al menos capacidad bytes sin solaparse con tabla/nodos; tabla inicializada y cadenas vivas aciclicas si no NULL.
 * @note NULL destino/capacidad cero no escriben. Buffer valido positivo termina en NUL, truncando si hace falta. Tabla/buckets NULL escribe Tabla no inicializada. Factor de carga con dos decimales; no reserva/libera ni imprime stdout.
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
