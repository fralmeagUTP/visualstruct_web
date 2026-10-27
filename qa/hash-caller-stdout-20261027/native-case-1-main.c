/** @file main.c
 * @brief Caller Hash H1 de mutaciones y consultas C observadas.
 * @details Enteros C y capacidad fija; recrear libera primero la instancia anterior.
 * Un fallo real de reserva se informa y sale por cleanup. No inyecta fallos QA.
 * Consultas ausentes se reproducen; validaciones rechazadas no llaman C.
 */
#include "tad_tabla_hash.h"
#include <stdio.h>
#include <limits.h>

/** @brief Ejecuta el historial y libera todos los objetos.
 * @return 0 en exito; 1 ante fallo de reserva o insercion.
 */
int main(void) {
    TablaHash tabla = {0};
    int status = 0;
    th_inicializar(&tabla, 17);
    if (!tabla.buckets) { status = 1; goto cleanup; }
    th_destruir(&tabla);
    th_inicializar(&tabla, 64);
    if (!tabla.buckets) { status = 1; goto cleanup; }
    printf("create:%d\n", tabla.capacidad);
    { char buffer[2048];
      th_formatear(&tabla, buffer, sizeof(buffer));
      printf("format:keys:\n%s", buffer);
      printf("keys:");
      for (int i = 0; tabla.buckets && i < tabla.capacidad; i++) {
          for (const THNodo *node = tabla.buckets[i]; node; node = node->siguiente) {
              printf("%d;", node->clave);
          }
      }
      printf("\n");
    }
    { THEstadisticas stats = th_estadisticas(&tabla);
      char texto[512];
      th_formatear_estadisticas(&tabla, texto, sizeof(texto));
      printf("stats-C:%d:%d:%d:%d:%.9g\n", stats.capacidad, stats.cantidad, stats.buckets_ocupados, stats.colisiones, (double)stats.factor_carga);
      printf("stats-format:\n%s", texto);
      printf("stats-API-projection:%d:%d:%.17g\n", tabla.capacidad, tabla.cantidad, ((tabla.capacidad > 0) ? ((double)tabla.cantidad / (double)tabla.capacidad) : 0.0));
    }
    { bool ok = th_insertar(&tabla, INT_MIN, 2147483647);
      printf("insert:%d:%d:%d\n", INT_MIN, 2147483647, (int)ok);
      if (!ok) { status = 1; goto cleanup; } }
    { int output = 123456789; bool found = th_buscar(&tabla, INT_MIN, &output);
      printf("get:%d:%d", INT_MIN, (int)found);
      if (found) {
          printf(":%d", output);
      }
      printf("\n");
    }
    { char buffer[2048];
      th_formatear(&tabla, buffer, sizeof(buffer));
      printf("format:values:\n%s", buffer);
      printf("values:");
      for (int i = 0; tabla.buckets && i < tabla.capacidad; i++) {
          for (const THNodo *node = tabla.buckets[i]; node; node = node->siguiente) {
              printf("%d;", node->valor);
          }
      }
      printf("\n");
    }
    { THEstadisticas stats = th_estadisticas(&tabla);
      char texto[512];
      th_formatear_estadisticas(&tabla, texto, sizeof(texto));
      printf("stats-C:%d:%d:%d:%d:%.9g\n", stats.capacidad, stats.cantidad, stats.buckets_ocupados, stats.colisiones, (double)stats.factor_carga);
      printf("stats-format:\n%s", texto);
      printf("stats-API-projection:%d:%d:%.17g\n", tabla.capacidad, tabla.cantidad, ((tabla.capacidad > 0) ? ((double)tabla.cantidad / (double)tabla.capacidad) : 0.0));
    }
    printf("state:%d:%d\n", tabla.capacidad, tabla.cantidad);
cleanup:
    th_destruir(&tabla);
    return status;
}
