#ifndef MONTICULO_BINARIO_H
#define MONTICULO_BINARIO_H

#include <stdbool.h>
#include <stddef.h>

/**
 * @file monticulo_binario.h
 * @brief API de Montículo Binario (Min-Heap o Max-Heap) soportado en arreglo dinámico.
 */

typedef enum {
    MONTICULO_MIN,
    MONTICULO_MAX
} TipoMonticulo;

typedef struct {
    int *datos;
    int cantidad;
    int capacidad;
    TipoMonticulo tipo;
} MonticuloBinario;

/** @brief Inicializa un monticulo vacio con una capacidad inicial y un tipo. */
void monticulo_inicializar(MonticuloBinario *m, TipoMonticulo tipo, int capacidad_inicial);

/** @brief Inserta un valor en el monticulo manteniendo la propiedad. */
bool monticulo_insertar(MonticuloBinario *m, int valor);

/** @brief Consulta la raiz del monticulo sin extraerla. */
bool monticulo_raiz(const MonticuloBinario *m, int *resultado);

/** @brief Extrae la raiz del monticulo y reorganiza los elementos. */
bool monticulo_extraer_raiz(MonticuloBinario *m, int *resultado);

/** @brief Elimina una ocurrencia de un valor dentro del monticulo. */
bool monticulo_eliminar_valor(MonticuloBinario *m, int valor);

/** @brief Verifica si el monticulo esta vacio. */
bool monticulo_vacio(const MonticuloBinario *m);

/** @brief Retorna la cantidad actual de elementos en el monticulo. */
int monticulo_cantidad(const MonticuloBinario *m);

/** @brief Retorna la capacidad total alojada en el arreglo del monticulo. */
int monticulo_capacidad(const MonticuloBinario *m);

/** @brief Construye un monticulo a partir de un arreglo de valores dados. */
bool monticulo_construir(MonticuloBinario *m, const int *valores, int cantidad);

/** @brief Copia los valores actuales del arreglo interno a un destino. */
int monticulo_copiar_valores(const MonticuloBinario *m, int *destino, int capacidad);

/** @brief Genera una representacion textual en linea del arreglo interno. */
void monticulo_formatear_arreglo(const MonticuloBinario *m, char *destino, size_t capacidad);

/** @brief Genera una representacion textual simulando niveles del arbol. */
void monticulo_formatear_arbol(const MonticuloBinario *m, char *destino, size_t capacidad);

/** @brief Libera la memoria interna del monticulo. */
void monticulo_destruir(MonticuloBinario *m);

#endif
