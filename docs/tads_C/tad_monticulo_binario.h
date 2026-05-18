#ifndef MONTICULO_BINARIO_H
#define MONTICULO_BINARIO_H

#include <stdbool.h>
#include <stddef.h>

/**
 * @file tad_monticulo_binario.h
 * @brief TAD Monticulo binario (min o max heap) sobre arreglo dinamico.
 */

/** @brief Tipo de monticulo. */
typedef enum {
    MONTICULO_MIN = 0,  
    MONTICULO_MAX = 1   
} TipoMonticulo;

/** @brief Estructura principal del monticulo binario. */
typedef struct {
    int *datos;            
    int cantidad;         
    int capacidad;         
    TipoMonticulo tipo;    
} MonticuloBinario;

void monticulo_inicializar(MonticuloBinario *m, TipoMonticulo tipo, int capacidad_inicial);
bool monticulo_insertar(MonticuloBinario *m, int valor);
bool monticulo_raiz(const MonticuloBinario *m, int *resultado);
bool monticulo_extraer_raiz(MonticuloBinario *m, int *resultado);
bool monticulo_eliminar_valor(MonticuloBinario *m, int valor);
bool monticulo_vacio(const MonticuloBinario *m);
int monticulo_cantidad(const MonticuloBinario *m);
int monticulo_capacidad(const MonticuloBinario *m);
bool monticulo_construir(MonticuloBinario *m, const int *valores, int cantidad);
int monticulo_copiar_valores(const MonticuloBinario *m, int *destino, int capacidad);
void monticulo_formatear_arreglo(const MonticuloBinario *m, char *destino, size_t capacidad);
void monticulo_formatear_arbol(const MonticuloBinario *m, char *destino, size_t capacidad);
void monticulo_destruir(MonticuloBinario *m);

#endif
