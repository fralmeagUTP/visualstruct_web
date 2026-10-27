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
    int clave; /**< Clave entera del elemento. */
    int valor; /**< Dato almacenado. */
    struct th_nodo *siguiente; /**< Enlace al siguiente nodo del bucket. */
} THNodo;

/**
 * @brief Tabla de claves y valores int con buckets de capacidad fija.
 * @note Estado utilizable: capacidad>0, buckets apunta a capacidad cabezas y
 * las cadenas son propias, vivas y aciclicas. cantidad cuenta claves almacenadas;
 * actualizar una clave no incrementa ese contador. No rehash. Copiar la
 * estructura comparte buckets/nodos; no duplica propiedad ni inicializa memoria.
 */
typedef struct {
    THNodo **buckets; /**< Arreglo de cabezas de cadenas de colisión. */
    int capacidad; /**< Capacidad reservada de la estructura. */
    int cantidad; /**< Número de elementos almacenados. */
} TablaHash;

/**
 * @brief Fotografia por valor de metadata y ocupacion, sin punteros propietarios.
 * @note th_estadisticas devuelve todos los campos cero si tabla/buckets es NULL
 * o capacidad<=0. En otra tabla lee cantidad de metadata y recorre los buckets
 * para ocupacion/colisiones; no recalcula ni repara cantidad.
 */
typedef struct {
    int capacidad; /**< Capacidad reservada de la estructura. */
    int cantidad; /**< Número de elementos almacenados. */
    int buckets_ocupados; /**< Número de buckets con al menos un nodo. */
    int colisiones; /**< Elementos que exceden el primer nodo de cada bucket ocupado. */
    float factor_carga; /**< Cociente float de metadata cantidad/capacidad en tabla utilizable; cero en salida vacia de error. */
} THEstadisticas;

/**
 * @brief Normaliza el módulo de una clave, incluidas claves negativas.
 * @param tabla Tabla con capacidad positiva.
 * @param clave Clave entera.
 * @return Índice entre 0 y capacidad-1, o -1 ante tabla NULL o capacidad no positiva.
 * @note Consulta capacidad sin acceder a buckets; admite INT_MIN y claves negativas. No reserva, libera ni modifica la tabla.
 */
int th_indice(const TablaHash *tabla, int clave);
/**
 * @brief Inicializa la tabla hash.
 * @param[out] tabla Puntero a la tabla hash.
 * @param[in] capacidad Capacidad (número de buckets) de la tabla.
 * @pre Estructura sin recursos propietarios pendientes; capacidad * sizeof(THNodo*) debe caber en size_t.
 * @note NULL tabla o capacidad <= 0 retorna sin escribir: no inicializa una estructura indeterminada. No libera recursos previos: destruir antes de reinicializar.
 * @note Con capacidad positiva fija cantidad=0; malloc fallido deja buckets=NULL y capacidad=0. Retorno void no comunica exito. No rehash.
 */
void th_inicializar(TablaHash *tabla, int capacidad);
/**
 * @brief Inserta un par clave-valor, actualizando el valor si la clave existe.
 * @param[in,out] tabla Puntero a la tabla hash.
 * @param[in] clave Clave a insertar.
 * @param[in] valor Valor asociado a la clave.
 * @return true si se insertó o actualizó correctamente, false en error.
 * @pre Tabla inicializada con buckets validos y cadenas propias vivas aciclicas, contadores consistentes; cantidad+1 cabe en int al insertar clave nueva.
 * @note NULL tabla/buckets o capacidad <= 0 retorna false. Actualizar no reserva ni cambia cantidad; insertar publica nodo propio al inicio. Fallo malloc retorna false sin mutacion. Capacidad fija: no rehash.
 */
bool th_insertar(TablaHash *tabla, int clave, int valor);
/**
 * @brief Busca el valor asociado a una clave.
 * @param[in] tabla Puntero a la tabla hash constante.
 * @param[in] clave Clave a buscar.
 * @param[out] valor Puntero donde se almacenará el valor si se encuentra.
 * @return true si se encontró la clave, false si no.
 * @pre Tabla inicializada con cadenas vivas aciclicas; valor es int externo escribible sin solaparse con nodos/metadata.
 * @note NULL tabla/buckets/valor o capacidad <= 0 retorna false. False no escribe salida. No reserva/libera/imprime ni cambia tabla bajo precondiciones.
 */
bool th_buscar(const TablaHash *tabla, int clave, int *valor);
/**
 * @brief Verifica si una clave existe en la tabla.
 * @param[in] tabla Puntero a la tabla hash.
 * @param[in] clave Clave a verificar.
 * @return true si la clave existe, false si no.
 * @pre Tabla inicializada con buckets y cadenas vivas aciclicas o NULL.
 * @note Delega a th_buscar con salida local; false para tabla no utilizable. No reserva/libera ni imprime.
 */
bool th_contiene(const TablaHash *tabla, int clave);
/**
 * @brief Elimina una clave de la tabla hash.
 * @param[in,out] tabla Puntero a la tabla hash.
 * @param[in] clave Clave a eliminar.
 * @return true si fue eliminada, false si no existía o error.
 * @pre Tabla inicializada, propia y consistente; cadenas vivas aciclicas sin ownership compartido.
 * @note NULL tabla/buckets o capacidad <= 0 retorna false. Elimina primera coincidencia, libera un nodo y decrementa cantidad; ausencia conserva tabla. Aliases a nodo liberado quedan invalidos. No rehash.
 */
bool th_eliminar(TablaHash *tabla, int clave);
/**
 * @brief Elimina todos los elementos manteniendo la capacidad de la tabla.
 * @param[in,out] tabla Puntero a la tabla hash.
 * @pre Tabla inicializada, propia y consistente con capacidad entradas de buckets y cadenas vivas aciclicas.
 * @note NULL tabla/buckets no escribe ni normaliza metadata. Libera nodos, pone buckets individuales NULL y cantidad=0; conserva arreglo y capacidad. Aliases a nodos liberados quedan invalidos.
 */
void th_vaciar(TablaHash *tabla);
/**
 * @brief Destruye la tabla hash liberando toda su memoria.
 * @param[in,out] tabla Puntero a la tabla hash.
 * @pre Tabla inicializada, propia y consistente; nodos y arreglo son reservas liberables sin compartir ownership.
 * @note NULL tabla/buckets se ignoran sin normalizar metadata. Tras vaciar y liberar arreglo fija buckets=NULL, capacidad=cantidad=0. No libera estructura prestada. Aliases a nodos/arreglo quedan invalidos.
 */
void th_destruir(TablaHash *tabla);
/**
 * @brief Indica si la tabla está vacía.
 * @param[in] tabla Puntero a la tabla hash.
 * @return true si tabla es NULL o cantidad==0; false en otro caso.
 * @note Consulta contador sin recorrer buckets ni validar corrupcion. No reserva/libera/modifica.
 */
bool th_vacia(const TablaHash *tabla);
/**
 * @brief Retorna la cantidad de elementos en la tabla.
 * @param[in] tabla Puntero a la tabla hash.
 * @return 0 ante tabla NULL; de otro modo contador almacenado cantidad, sin normalizacion ni recount.
 * @note Estructura prestada inicializada; no reserva/libera/modifica.
 */
int th_cantidad(const TablaHash *tabla);
/**
 * @brief Retorna la capacidad actual de la tabla.
 * @param[in] tabla Puntero a la tabla hash.
 * @return 0 ante tabla NULL; de otro modo capacidad almacenada, sin normalizacion.
 * @note Estructura prestada inicializada; no reserva/libera/modifica.
 */
int th_capacidad(const TablaHash *tabla);
/**
 * @brief Calcula y retorna las estadísticas de la tabla hash.
 * @param[in] tabla Puntero a la tabla hash.
 * @return Estructura con las estadísticas calculadas.
 * @pre Si utilizable, capacidad entradas de buckets, cadenas vivas aciclicas y contadores representables en int.
 * @note Devuelve todos los campos cero ante tabla/buckets NULL o capacidad <= 0. Cantidad se lee de metadata; factor_carga es cantidad/capacidad float. Colisiones suma nodos menos uno por bucket ocupado. No reserva/libera/modifica.
 */
THEstadisticas th_estadisticas(const TablaHash *tabla);
/**
 * @brief Formatea el contenido de la tabla hash en una cadena de texto.
 * @param[in] tabla Puntero a la tabla hash.
 * @param[out] destino Buffer donde se escribirá la representación.
 * @param[in] capacidad Tamaño máximo del buffer destino.
 * @pre Buffer externo de al menos capacidad bytes sin solaparse con tabla/nodos; tabla inicializada y cadenas vivas aciclicas si no NULL.
 * @note NULL destino o capacidad cero no escriben. Buffer valido positivo termina en NUL; trunca a capacidad-1 caracteres y capacidad 1 produce cadena vacia. Tabla/buckets NULL escribe Tabla no inicializada. No reserva/libera ni imprime stdout.
 */
void th_formatear(const TablaHash *tabla, char *destino, size_t capacidad);
/**
 * @brief Formatea las estadísticas de la tabla en una cadena de texto.
 * @param[in] tabla Puntero a la tabla hash.
 * @param[out] destino Buffer donde se escribirá la representación.
 * @param[in] capacidad Tamaño máximo del buffer destino.
 * @pre Buffer externo de al menos capacidad bytes sin solaparse con tabla/nodos; tabla inicializada y cadenas vivas aciclicas si no NULL.
 * @note NULL destino/capacidad cero no escriben. Buffer valido positivo termina en NUL, truncando si hace falta. Tabla/buckets NULL escribe Tabla no inicializada. Factor de carga con dos decimales; no reserva/libera ni imprime stdout.
 */
void th_formatear_estadisticas(const TablaHash *tabla, char *destino, size_t capacidad);

#endif
