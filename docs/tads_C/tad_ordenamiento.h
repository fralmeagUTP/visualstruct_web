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

/**
 * @brief Código de éxito: 1.
 */
#define ORDENAMIENTO_OK 1
/**
 * @brief Código de error: 0.
 */
#define ORDENAMIENTO_ERROR 0
/**
 * @brief Maximo de valores posibles del intervalo inclusivo max-min+1: 1000000.
 * @note Lo aplica Counting Sort y por delegacion Binsort. No limita n ni
 * establece el rango de Radix u otros ordenamientos; la reserva tambien debe
 * caber en size_t y puede fallar.
 */
#define ORDENAMIENTO_RANGO_MAX 1000000U

#ifdef __cplusplus
extern "C" {
#endif

/**
 * @brief Imprime un arreglo de enteros en una línea.
 * 
 * @param arreglo Arreglo de enteros.
 * @param n Número de elementos del arreglo.
 * @pre Si arreglo no NULL y n>0, contiene n ints vivos legibles.
 * @note NULL arreglo o n==0 imprime [] y salto de linea. No reserva/libera ni modifica datos.
 */
void imprimir_arreglo(const int arreglo[], size_t n);
/**
 * @brief Copia los elementos de un arreglo origen hacia un arreglo destino.
 * 
 * @param destino Arreglo destino.
 * @param origen Arreglo origen.
 * @param n Número de elementos a copiar.
 * @return ORDENAMIENTO_OK si la copia fue correcta; ORDENAMIENTO_ERROR en caso contrario.
 * @pre Buffers vivos de al menos n ints, destino escribible y origen legible, sin solapamiento; n*sizeof(int) representable en size_t.
 * @note NULL buffers o n==0 retorna ORDENAMIENTO_ERROR sin copiar. Usa memcpy, no memmove; no admite buffers solapados ni valida longitud. No reserva/libera.
 */
int copiar_arreglo(int destino[], const int origen[], size_t n);

/**
 * @brief Ordena un arreglo usando el método de intercambio directo.
 *
 * @param arreglo Arreglo de enteros a ordenar.
 * @param n Número de elementos del arreglo.
 * @note Tiempo O(n^2), memoria O(1); no estable por intercambios no adyacentes.
 * @note Arreglo NULL o n==0 no se procesa; funciones int retornan ERROR y funciones void no comunican estado.
 */
void ordenar_intercambio(int arreglo[], size_t n);
/**
 * @brief Ordena un arreglo usando selección directa.
 *
 * @param arreglo Arreglo de enteros a ordenar.
 * @param n Número de elementos del arreglo.
 * @note Tiempo O(n^2), memoria O(1); no estable por intercambio con el minimo distante.
 * @note Arreglo NULL o n==0 no se procesa; funciones int retornan ERROR y funciones void no comunican estado.
 */
void ordenar_seleccion(int arreglo[], size_t n);
/**
 * @brief Ordena un arreglo usando inserción directa.
 *
 * @param arreglo Arreglo de enteros a ordenar.
 * @param n Número de elementos del arreglo.
 * @note Mejor O(n), peor O(n^2), memoria O(1); estable por desplazar solo valores estrictamente mayores.
 * @note Arreglo NULL o n==0 no se procesa; funciones int retornan ERROR y funciones void no comunican estado.
 */
void ordenar_insercion(int arreglo[], size_t n);
/**
 * @brief Ordena un arreglo usando burbuja mejorada.
 *
 * @param arreglo Arreglo de enteros a ordenar.
 * @param n Número de elementos del arreglo.
 * @note Mejor O(n), peor O(n^2), memoria O(1); estable por intercambiar vecinos solo si son estrictamente mayores.
 * @note Arreglo NULL o n==0 no se procesa; funciones int retornan ERROR y funciones void no comunican estado.
 */
void ordenar_burbuja(int arreglo[], size_t n);
/**
 * @brief Ordena un arreglo usando Shell Sort.
 *
 * @param arreglo Arreglo de enteros a ordenar.
 * @param n Número de elementos del arreglo.
 * @note Gaps n/2, n/4, ...; peor O(n^2), memoria O(1); no estable.
 * @note Arreglo NULL o n==0 no se procesa; funciones int retornan ERROR y funciones void no comunican estado.
 */
void ordenar_shell(int arreglo[], size_t n);
/**
 * @brief Ordena un arreglo usando QuickSort.
 *
 * @param arreglo Arreglo de enteros a ordenar.
 * @param n Número de elementos del arreglo.
 * @note Promedio O(n log n), peor O(n^2); pila O(log n) promedio, O(n) peor; no estable. n debe permitir indices int y suma de extremos int.
 * @note Arreglo NULL o n==0 no se procesa; funciones int retornan ERROR y funciones void no comunican estado.
 */
void ordenar_quicksort(int arreglo[], size_t n);
/**
 * @brief Ordena un arreglo usando MergeSort.
 *
 * @param arreglo Arreglo de enteros a ordenar.
 * @param n Número de elementos del arreglo.
 * @return ORDENAMIENTO_OK si se ordenó correctamente; ORDENAMIENTO_ERROR ante arreglo NULL, n == 0 o fallo de memoria.
 * @note Tiempo O(n log n), auxiliar O(n), pila O(log n); estable porque la mezcla toma primero el lado izquierdo en igualdad.
 * @note Arreglo NULL o n==0 no se procesa; funciones int retornan ERROR y funciones void no comunican estado.
 */
int  ordenar_mergesort(int arreglo[], size_t n);
/**
 * @brief Ordena un arreglo usando HeapSort.
 *
 * @param arreglo Arreglo de enteros a ordenar.
 * @param n Número de elementos del arreglo.
 * @note Tiempo O(n log n), sin arreglo auxiliar; heapify recursivo usa pila O(log n), no espacio total O(1); no estable.
 * @note Arreglo NULL o n==0 no se procesa; funciones int retornan ERROR y funciones void no comunican estado.
 */
void ordenar_heapsort(int arreglo[], size_t n);
/**
 * @brief Ordena un arreglo usando Counting Sort.
 *
 * @param arreglo Arreglo de enteros a ordenar.
 * @param n Número de elementos del arreglo.
 * @return ORDENAMIENTO_OK si se ordenó correctamente; ORDENAMIENTO_ERROR ante arreglo NULL, n == 0, rango mayor que ORDENAMIENTO_RANGO_MAX, tamaño no representable o fallo de memoria.
 * @note Tiempo O(n+k), memoria O(k), k=max-min+1 <= ORDENAMIENTO_RANGO_MAX; reconstruye enteros por frecuencia, sin preservar identidad de registros iguales.
 * @note Arreglo NULL o n==0 no se procesa; funciones int retornan ERROR y funciones void no comunican estado.
 */
int  ordenar_counting_sort(int arreglo[], size_t n);
/**
 * @brief Ordena delegando en Counting Sort; conserva sus límites de rango y códigos de error.
 *
 * @param arreglo Arreglo de enteros a ordenar.
 * @param n Número de elementos del arreglo.
 * @return ORDENAMIENTO_OK si se ordenó correctamente; ORDENAMIENTO_ERROR ante arreglo NULL, n == 0, rango mayor que ORDENAMIENTO_RANGO_MAX, tamaño no representable o fallo de memoria.
 * @note Delegacion exacta a Counting Sort: O(n+k) tiempo, O(k) memoria y mismo limite; no es una implementacion independiente de buckets.
 * @note Arreglo NULL o n==0 no se procesa; funciones int retornan ERROR y funciones void no comunican estado.
 */
int  ordenar_binsort(int arreglo[], size_t n);
/**
 * @brief Ordena un arreglo usando Radix Sort LSD en base 10.
 *
 * Esta implementación acepta enteros negativos separándolos de los no negativos,
 * ordenando magnitudes y recombinando al final.
 *
 * @param arreglo Arreglo de enteros a ordenar.
 * @param n Número de elementos del arreglo.
 * @return ORDENAMIENTO_OK si se ordenó correctamente; ORDENAMIENTO_ERROR ante arreglo NULL, n == 0 o fallo de memoria.
 * @note Base 10, O(d(n+10)) tiempo y O(n+10) memoria. Conteo por digito estable; la inversion final del grupo negativo no garantiza estabilidad de registros negativos iguales. INT_MIN usa magnitud uint32_t y recomposicion protegida.
 * @note Arreglo NULL o n==0 no se procesa; funciones int retornan ERROR y funciones void no comunican estado.
 */
int  ordenar_radixsort(int arreglo[], size_t n);

/**
 * @brief Ejecuta y muestra un algoritmo de ordenamiento sobre una copia del arreglo base.
 * 
 * @param nombre Nombre descriptivo del algoritmo.
 * @param ordenar Función de ordenamiento que no retorna estado.
 * @param base Arreglo base.
 * @param n Número de elementos.
 * @pre nombre es cadena viva terminada en NUL; base contiene n ints legibles, n*sizeof(int) representable. Callback valido recibe copia prestada, no la libera ni retiene; se cumplen sus limites particulares.
 * @note NULL nombre/callback/base o n==0 no hace nada. Malloc fallido imprime error. Copia base, ejecuta callback, imprime copia y la libera; base queda intacta bajo precondiciones.
 */
void probar_algoritmo_void(const char *nombre, void (*ordenar)(int[], size_t), const int base[], size_t n);
/**
 * @brief Ejecuta y muestra un algoritmo de ordenamiento que retorna estado.
 * 
 * @param nombre Nombre descriptivo del algoritmo.
 * @param ordenar Función de ordenamiento que retorna ORDENAMIENTO_OK o ORDENAMIENTO_ERROR.
 * @param base Arreglo base.
 * @param n Número de elementos.
 * @pre nombre es cadena viva terminada en NUL; base contiene n ints legibles, n*sizeof(int) representable. Callback valido recibe copia prestada, no la libera ni retiene; se cumplen sus limites particulares.
 * @note NULL nombre/callback/base o n==0 no hace nada. Error de malloc imprime diagnostico; callback con retorno cero imprime error y libera copia sin imprimir arreglo. Exito no cero imprime copia y la libera.
 */
void probar_algoritmo_int(const char *nombre, int (*ordenar)(int[], size_t), const int base[], size_t n);

#ifdef __cplusplus
}
#endif

#endif // TAD_ORDENAMIENTO_H
