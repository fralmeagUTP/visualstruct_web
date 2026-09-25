
/**
 * @file tad_ordenamiento.c
 * @brief Implementacion didactica de metodos clasicos de ordenamiento en C estandar.
 *
 * Este archivo contiene implementaciones autocontenidas de algoritmos de ordenamiento
 * internos sobre arreglos de enteros. Incluye metodos directos y avanzados:
 * intercambio, seleccion, insercion, burbuja, Shell, QuickSort, MergeSort,
 * HeapSort, Counting Sort, Binsort y Radix Sort.
 *
 * @details
 * Compilacion sugerida:
 * @code
 * gcc -std=c99 -Wall -Wextra -pedantic tad_ordenamiento.c -o ordenamientos
 * @endcode
 *
 * @author Francisco Alejandro Medina Aguirre
 * @date 2026
 */

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <limits.h>
#include <stdint.h>
#include "tad_ordenamiento.h"


/**
 * @brief Intercambia el contenido de dos variables enteras.
 *
 * @param a Puntero al primer entero.
 * @param b Puntero al segundo entero.
 */
static void intercambiar(int *a, int *b) {
	int temporal;
	if (a == NULL || b == NULL) return;
	temporal = *a;
	*a = *b;
	*b = temporal;
}

/**
 * @brief Verifica si un arreglo puede procesarse.
 *
 * @param arreglo Arreglo de enteros.
 * @param n Número de elementos del arreglo.
 * @return 1 si el arreglo es válido; 0 en caso contrario.
 */
static int arreglo_valido(const int arreglo[], size_t n) {
	return arreglo != NULL && n > 0;
}

/**
 * @brief Imprime un arreglo de enteros en una línea.
 *
 * @param arreglo Arreglo de enteros.
 * @param n Número de elementos del arreglo.
 */
void imprimir_arreglo(const int arreglo[], size_t n) {
	size_t i;
	if (!arreglo_valido(arreglo, n)) { printf("[]\n"); return; }
	printf("[");
	for (i = 0; i < n; ++i) {
		printf("%d", arreglo[i]);
		if (i + 1 < n) printf(", ");
	}
	printf("]\n");
}

/**
 * @brief Copia los elementos de un arreglo origen hacia un arreglo destino.
 *
 * @param destino Arreglo destino.
 * @param origen Arreglo origen.
 * @param n Número de elementos a copiar.
 * @return ORDENAMIENTO_OK si la copia fue correcta; ORDENAMIENTO_ERROR en caso contrario.
 */
int copiar_arreglo(int destino[], const int origen[], size_t n) {
	if (destino == NULL || origen == NULL || n == 0) return ORDENAMIENTO_ERROR;
	memcpy(destino, origen, n * sizeof(int));
	return ORDENAMIENTO_OK;
}

/**
 * @brief Ordena un arreglo usando el método de intercambio directo.
 *
 * @param arreglo Arreglo de enteros a ordenar.
 * @param n Número de elementos del arreglo.
 */
void ordenar_intercambio(int arreglo[], size_t n) {
	size_t i, j;
	if (!arreglo_valido(arreglo, n)) return;
	for (i = 0; i + 1 < n; ++i)
		for (j = i + 1; j < n; ++j)
			if (arreglo[i] > arreglo[j]) intercambiar(&arreglo[i], &arreglo[j]);
}

/**
 * @brief Ordena un arreglo usando selección directa.
 *
 * @param arreglo Arreglo de enteros a ordenar.
 * @param n Número de elementos del arreglo.
 */
void ordenar_seleccion(int arreglo[], size_t n) {
	size_t i, j, indice_menor;
	if (!arreglo_valido(arreglo, n)) return;
	for (i = 0; i + 1 < n; ++i) {
		indice_menor = i;
		for (j = i + 1; j < n; ++j)
			if (arreglo[j] < arreglo[indice_menor]) indice_menor = j;
		if (indice_menor != i) intercambiar(&arreglo[i], &arreglo[indice_menor]);
	}
}

/**
 * @brief Ordena un arreglo usando inserción directa.
 *
 * @param arreglo Arreglo de enteros a ordenar.
 * @param n Número de elementos del arreglo.
 */
void ordenar_insercion(int arreglo[], size_t n) {
	size_t i;
	if (!arreglo_valido(arreglo, n)) return;
	for (i = 1; i < n; ++i) {
		int clave = arreglo[i];
		size_t j = i;
		while (j > 0 && arreglo[j - 1] > clave) {
			arreglo[j] = arreglo[j - 1];
			--j;
		}
		arreglo[j] = clave;
	}
}

/**
 * @brief Ordena un arreglo usando burbuja mejorada.
 *
 * @param arreglo Arreglo de enteros a ordenar.
 * @param n Número de elementos del arreglo.
 */
void ordenar_burbuja(int arreglo[], size_t n) {
	size_t pasada, j;
	int hubo_intercambio;
	if (!arreglo_valido(arreglo, n)) return;
	for (pasada = 0; pasada + 1 < n; ++pasada) {
		hubo_intercambio = 0;
		for (j = 0; j + 1 < n - pasada; ++j) {
			if (arreglo[j] > arreglo[j + 1]) {
				intercambiar(&arreglo[j], &arreglo[j + 1]);
				hubo_intercambio = 1;
			}
		}
		if (!hubo_intercambio) break;
	}
}

/**
 * @brief Ordena un arreglo usando Shell Sort.
 *
 * @param arreglo Arreglo de enteros a ordenar.
 * @param n Número de elementos del arreglo.
 */
void ordenar_shell(int arreglo[], size_t n) {
	size_t intervalo;
	if (!arreglo_valido(arreglo, n)) return;
	for (intervalo = n / 2; intervalo > 0; intervalo /= 2) {
		size_t i;
		for (i = intervalo; i < n; ++i) {
			int temporal = arreglo[i];
			size_t j = i;
			while (j >= intervalo && arreglo[j - intervalo] > temporal) {
				arreglo[j] = arreglo[j - intervalo];
				j -= intervalo;
			}
			arreglo[j] = temporal;
		}
	}
}

/**
 * @brief Particiona un arreglo para QuickSort usando pivote central (función auxiliar).
 *
 * @param arreglo Arreglo de enteros.
 * @param primero Índice inicial.
 * @param ultimo Índice final.
 */
static void quicksort_recursivo(int arreglo[], int primero, int ultimo) {
	int i = primero, j = ultimo, pivote = arreglo[(primero + ultimo) / 2];
	while (i <= j) {
		while (arreglo[i] < pivote) ++i;
		while (arreglo[j] > pivote) --j;
		if (i <= j) {
			intercambiar(&arreglo[i], &arreglo[j]);
			++i; --j;
		}
	}
	if (primero < j) quicksort_recursivo(arreglo, primero, j);
	if (i < ultimo) quicksort_recursivo(arreglo, i, ultimo);
}

/**
 * @brief Ordena un arreglo usando QuickSort.
 *
 * @param arreglo Arreglo de enteros a ordenar.
 * @param n Número de elementos del arreglo.
 */
void ordenar_quicksort(int arreglo[], size_t n) {
	if (!arreglo_valido(arreglo, n)) return;
	quicksort_recursivo(arreglo, 0, (int)n - 1);
}

/**
 * @brief Mezcla dos subarreglos ordenados dentro del arreglo principal (función auxiliar para MergeSort).
 *
 * @param arreglo Arreglo de enteros.
 * @param auxiliar Arreglo auxiliar.
 * @param izquierda Índice inicial.
 * @param medio Índice medio.
 * @param derecha Índice final.
 */
static void mezclar(int arreglo[], int auxiliar[], size_t izquierda, size_t medio, size_t derecha) {
	size_t i = izquierda, j = medio + 1, k = izquierda;
	while (i <= medio && j <= derecha) {
		if (arreglo[i] <= arreglo[j]) auxiliar[k++] = arreglo[i++];
		else auxiliar[k++] = arreglo[j++];
	}
	while (i <= medio) auxiliar[k++] = arreglo[i++];
	while (j <= derecha) auxiliar[k++] = arreglo[j++];
	for (i = izquierda; i <= derecha; ++i) arreglo[i] = auxiliar[i];
}

/**
 * @brief Función recursiva auxiliar de MergeSort.
 *
 * @param arreglo Arreglo de enteros.
 * @param auxiliar Arreglo auxiliar.
 * @param izquierda Índice inicial.
 * @param derecha Índice final.
 */
static void mergesort_recursivo(int arreglo[], int auxiliar[], size_t izquierda, size_t derecha) {
	if (izquierda >= derecha) return;
	size_t medio = izquierda + (derecha - izquierda) / 2;
	mergesort_recursivo(arreglo, auxiliar, izquierda, medio);
	mergesort_recursivo(arreglo, auxiliar, medio + 1, derecha);
	mezclar(arreglo, auxiliar, izquierda, medio, derecha);
}

/**
 * @brief Ordena un arreglo usando MergeSort.
 *
 * @param arreglo Arreglo de enteros a ordenar.
 * @param n Número de elementos del arreglo.
 * @return ORDENAMIENTO_OK si se ordenó correctamente; ORDENAMIENTO_ERROR si falló memoria.
 */
int ordenar_mergesort(int arreglo[], size_t n) {
	int *auxiliar;
	if (!arreglo_valido(arreglo, n)) return ORDENAMIENTO_ERROR;
	auxiliar = (int *)malloc(n * sizeof(int));
	if (auxiliar == NULL) return ORDENAMIENTO_ERROR;
	mergesort_recursivo(arreglo, auxiliar, 0, n - 1);
	free(auxiliar);
	return ORDENAMIENTO_OK;
}

/**
 * @brief Restaura la propiedad de montículo máximo desde un índice dado (función auxiliar para HeapSort).
 *
 * @param arreglo Arreglo de enteros.
 * @param n Tamaño lógico del montículo.
 * @param raiz Índice de la raíz del submontículo.
 */
static void heapify(int arreglo[], size_t n, size_t raiz) {
	size_t mayor = raiz, izquierdo = 2 * raiz + 1, derecho = 2 * raiz + 2;
	if (izquierdo < n && arreglo[izquierdo] > arreglo[mayor]) mayor = izquierdo;
	if (derecho < n && arreglo[derecho] > arreglo[mayor]) mayor = derecho;
	if (mayor != raiz) {
		intercambiar(&arreglo[raiz], &arreglo[mayor]);
		heapify(arreglo, n, mayor);
	}
}

/**
 * @brief Ordena un arreglo usando HeapSort.
 *
 * @param arreglo Arreglo de enteros a ordenar.
 * @param n Número de elementos del arreglo.
 */
void ordenar_heapsort(int arreglo[], size_t n) {
	size_t i;
	if (!arreglo_valido(arreglo, n)) return;
	for (i = n / 2; i > 0; --i) heapify(arreglo, n, i - 1);
	for (i = n; i > 1; --i) {
		intercambiar(&arreglo[0], &arreglo[i - 1]);
		heapify(arreglo, i - 1, 0);
	}
}

/**
 * @brief Obtiene el menor y mayor valor de un arreglo (función auxiliar).
 *
 * @param arreglo Arreglo de enteros.
 * @param n Número de elementos.
 * @param minimo Dirección donde se almacena el mínimo.
 * @param maximo Dirección donde se almacena el máximo.
 * @return ORDENAMIENTO_OK si se calcularon los valores; ORDENAMIENTO_ERROR en caso contrario.
 */
static int obtener_minimo_maximo(const int arreglo[], size_t n, int *minimo, int *maximo) {
	size_t i;
	if (!arreglo_valido(arreglo, n) || minimo == NULL || maximo == NULL) return ORDENAMIENTO_ERROR;
	*minimo = arreglo[0]; *maximo = arreglo[0];
	for (i = 1; i < n; ++i) {
		if (arreglo[i] < *minimo) *minimo = arreglo[i];
		if (arreglo[i] > *maximo) *maximo = arreglo[i];
	}
	return ORDENAMIENTO_OK;
}

/**
 * @brief Ordena un arreglo usando Counting Sort.
 *
 * @param arreglo Arreglo de enteros a ordenar.
 * @param n Número de elementos del arreglo.
 * @return ORDENAMIENTO_OK si se ordenó correctamente; ORDENAMIENTO_ERROR si falló memoria.
 */
int ordenar_counting_sort(int arreglo[], size_t n) {
	int minimo, maximo; size_t rango, i, indice; int *conteo;
	if (!arreglo_valido(arreglo, n)) return ORDENAMIENTO_ERROR;
	if (!obtener_minimo_maximo(arreglo, n, &minimo, &maximo)) return ORDENAMIENTO_ERROR;
	rango = (size_t)((long long)maximo - (long long)minimo + 1LL);
	if (rango > ORDENAMIENTO_RANGO_MAX || rango > SIZE_MAX / sizeof(int)) return ORDENAMIENTO_ERROR;
	conteo = (int *)calloc(rango, sizeof(int));
	if (conteo == NULL) return ORDENAMIENTO_ERROR;
	for (i = 0; i < n; ++i) ++conteo[arreglo[i] - minimo];
	indice = 0;
	for (i = 0; i < rango; ++i)
		while (conteo[i] > 0) { arreglo[indice++] = (int)i + minimo; --conteo[i]; }
	free(conteo);
	return ORDENAMIENTO_OK;
}

/**
 * @brief Ordena un arreglo usando Binsort o clasificación por urnas.
 *
 * @param arreglo Arreglo de enteros a ordenar.
 * @param n Número de elementos del arreglo.
 * @return ORDENAMIENTO_OK si se ordenó correctamente; ORDENAMIENTO_ERROR si falló memoria.
 */
int ordenar_binsort(int arreglo[], size_t n) {
	return ordenar_counting_sort(arreglo, n);
}

/**
 * @brief Ordena por conteo según un dígito decimal específico para Radix Sort (función auxiliar).
 *
 * @param arreglo Arreglo de enteros no negativos.
 * @param n Número de elementos.
 * @param exp Potencia de 10 que representa el dígito a procesar.
 * @return ORDENAMIENTO_OK si se ordenó correctamente; ORDENAMIENTO_ERROR si falló memoria.
 */
static int counting_por_digito(uint32_t arreglo[], size_t n, uint32_t exp) {
	size_t conteo[10] = {0}; uint32_t *salida; size_t i;
	salida = (uint32_t *)malloc(n * sizeof(uint32_t));
	if (salida == NULL) return ORDENAMIENTO_ERROR;
	for (i = 0; i < n; ++i) ++conteo[(arreglo[i] / exp) % 10];
	for (i = 1; i < 10; ++i) conteo[i] += conteo[i - 1];
	for (i = n; i > 0; --i) {
		uint32_t valor = arreglo[i - 1];
		uint32_t digito = (valor / exp) % 10U;
		salida[conteo[digito] - 1] = valor;
		--conteo[digito];
	}
	for (i = 0; i < n; ++i) arreglo[i] = salida[i];
	free(salida);
	return ORDENAMIENTO_OK;
}

/**
 * @brief Ordena un arreglo usando Radix Sort LSD en base 10.
 *
 * Esta implementación acepta enteros negativos separándolos de los no negativos,
 * ordenando magnitudes y recombinando al final.
 *
 * @param arreglo Arreglo de enteros a ordenar.
 * @param n Número de elementos del arreglo.
 * @return ORDENAMIENTO_OK si se ordenó correctamente; ORDENAMIENTO_ERROR si falló memoria.
 */
int ordenar_radixsort(int arreglo[], size_t n) {
	uint32_t *negativos, *positivos; size_t cant_negativos = 0, cant_positivos = 0, i, indice;
	if (!arreglo_valido(arreglo, n)) return ORDENAMIENTO_ERROR;
	negativos = (uint32_t *)malloc(n * sizeof(uint32_t));
	positivos = (uint32_t *)malloc(n * sizeof(uint32_t));
	if (negativos == NULL || positivos == NULL) { free(negativos); free(positivos); return ORDENAMIENTO_ERROR; }
	for (i = 0; i < n; ++i) {
		if (arreglo[i] < 0) negativos[cant_negativos++] = 0U - (uint32_t)arreglo[i];
		else positivos[cant_positivos++] = (uint32_t)arreglo[i];
	}
	if (cant_negativos > 0) {
		uint32_t maximo = negativos[0], exp = 1U;
		for (i = 1; i < cant_negativos; ++i) if (negativos[i] > maximo) maximo = negativos[i];
		for (;;) {
			if (!counting_por_digito(negativos, cant_negativos, exp)) { free(negativos); free(positivos); return ORDENAMIENTO_ERROR; }
			if (exp > maximo / 10U) break;
			exp *= 10U;
		}
	}
	if (cant_positivos > 0) {
		uint32_t maximo = positivos[0], exp = 1U;
		for (i = 1; i < cant_positivos; ++i) if (positivos[i] > maximo) maximo = positivos[i];
		if (maximo > 0U) for (;;) {
			if (!counting_por_digito(positivos, cant_positivos, exp)) { free(negativos); free(positivos); return ORDENAMIENTO_ERROR; }
			if (exp > maximo / 10U) break;
			exp *= 10U;
		}
	}
	indice = 0;
	for (i = cant_negativos; i > 0; --i) {
		uint32_t magnitud = negativos[i - 1];
		arreglo[indice++] = magnitud == (uint32_t)INT_MAX + 1U ? INT_MIN : -(int)magnitud;
	}
	for (i = 0; i < cant_positivos; ++i) arreglo[indice++] = (int)positivos[i];
	free(negativos); free(positivos);
	return ORDENAMIENTO_OK;
}

/**
 * @brief Ejecuta y muestra un algoritmo de ordenamiento sobre una copia del arreglo base.
 *
 * @param nombre Nombre descriptivo del algoritmo.
 * @param ordenar Función de ordenamiento que no retorna estado.
 * @param base Arreglo base.
 * @param n Número de elementos.
 */
void probar_algoritmo_void(const char *nombre, void (*ordenar)(int[], size_t), const int base[], size_t n) {
	int *copia;
	if (nombre == NULL || ordenar == NULL || !arreglo_valido(base, n)) return;
	copia = (int *)malloc(n * sizeof(int));
	if (copia == NULL) { printf("%s: error de memoria\n", nombre); return; }
	copiar_arreglo(copia, base, n);
	ordenar(copia, n);
	printf("%-18s: ", nombre);
	imprimir_arreglo(copia, n);
	free(copia);
}

/**
 * @brief Ejecuta y muestra un algoritmo de ordenamiento que retorna estado.
 *
 * @param nombre Nombre descriptivo del algoritmo.
 * @param ordenar Función de ordenamiento que retorna ORDENAMIENTO_OK o ORDENAMIENTO_ERROR.
 * @param base Arreglo base.
 * @param n Número de elementos.
 */
void probar_algoritmo_int(const char *nombre, int (*ordenar)(int[], size_t), const int base[], size_t n) {
	int *copia;
	if (nombre == NULL || ordenar == NULL || !arreglo_valido(base, n)) return;
	copia = (int *)malloc(n * sizeof(int));
	if (copia == NULL) { printf("%s: error de memoria\n", nombre); return; }
	copiar_arreglo(copia, base, n);
	if (!ordenar(copia, n)) { printf("%s: error al ordenar\n", nombre); free(copia); return; }
	printf("%-18s: ", nombre);
	imprimir_arreglo(copia, n);
	free(copia);
}
