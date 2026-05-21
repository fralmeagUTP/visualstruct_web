/**
 * @file tad_ordenamiento.h
 * @brief Declaraciones de métodos clásicos de ordenamiento y utilidades para arreglos de enteros.
 *
 * Este archivo contiene las declaraciones de funciones para algoritmos de ordenamiento
 * y utilidades asociadas, para uso modular en C.
 *
 * @author Francisco Alejandro Medina Aguirre
 * @date 2026
 */

#ifndef TAD_ORDENAMIENTO_H
#define TAD_ORDENAMIENTO_H

#include <stddef.h>

#define ORDENAMIENTO_OK 1
#define ORDENAMIENTO_ERROR 0

#ifdef __cplusplus
extern "C" {
#endif

void imprimir_arreglo(const int arreglo[], size_t n);
int copiar_arreglo(int destino[], const int origen[], size_t n);

void ordenar_intercambio(int arreglo[], size_t n);
void ordenar_seleccion(int arreglo[], size_t n);
void ordenar_insercion(int arreglo[], size_t n);
void ordenar_burbuja(int arreglo[], size_t n);
void ordenar_shell(int arreglo[], size_t n);
void ordenar_quicksort(int arreglo[], size_t n);
int  ordenar_mergesort(int arreglo[], size_t n);
void ordenar_heapsort(int arreglo[], size_t n);
int  ordenar_counting_sort(int arreglo[], size_t n);
int  ordenar_binsort(int arreglo[], size_t n);
int  ordenar_radixsort(int arreglo[], size_t n);

void probar_algoritmo_void(const char *nombre, void (*ordenar)(int[], size_t), const int base[], size_t n);
void probar_algoritmo_int(const char *nombre, int (*ordenar)(int[], size_t), const int base[], size_t n);

#ifdef __cplusplus
}
#endif

#endif // TAD_ORDENAMIENTO_H
