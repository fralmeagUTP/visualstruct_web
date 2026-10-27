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
    th_inicializar(&tabla, 3);
    if (!tabla.buckets) { status = 1; goto cleanup; }
    printf("create:%d\n", tabla.capacidad);
    { bool ok = th_insertar(&tabla, 1, 10);
      printf("insert:%d:%d:%d\n", 1, 10, (int)ok);
      if (!ok) { status = 1; goto cleanup; } }
    { bool ok = th_insertar(&tabla, 4, 20);
      printf("insert:%d:%d:%d\n", 4, 20, (int)ok);
      if (!ok) { status = 1; goto cleanup; } }
    { bool ok = th_insertar(&tabla, -2, INT_MIN);
      printf("insert:%d:%d:%d\n", -2, INT_MIN, (int)ok);
      if (!ok) { status = 1; goto cleanup; } }
    { bool ok = th_insertar(&tabla, 1, -17);
      printf("insert:%d:%d:%d\n", 1, -17, (int)ok);
      if (!ok) { status = 1; goto cleanup; } }
    { int output = 123456789; bool found = th_buscar(&tabla, 1, &output);
      printf("get:%d:%d", 1, (int)found);
      if (found) {
          printf(":%d", output);
      }
      printf("\n");
    }
    { int output = 123456789; bool found = th_buscar(&tabla, 1, &output);
      printf("get:%d:%d", 1, (int)found);
      if (found) {
          printf(":%d", output);
      }
      printf("\n");
    }
    { int output = 123456789; bool found = th_buscar(&tabla, 99, &output);
      printf("get:%d:%d", 99, (int)found);
      if (found) {
          printf(":%d", output);
      }
      printf("\n");
    }
    { bool found = th_contiene(&tabla, -2);
      printf("contains:%d:%d\n", -2, (int)found);
    }
    { bool found = th_contiene(&tabla, 99);
      printf("contains:%d:%d\n", 99, (int)found);
    }
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
    { char buffer[2048];
      th_formatear(&tabla, buffer, sizeof(buffer));
      printf("format:items:\n%s", buffer);
      printf("items:");
      for (int i = 0; tabla.buckets && i < tabla.capacidad; i++) {
          for (const THNodo *node = tabla.buckets[i]; node; node = node->siguiente) {
              printf("%d:%d;", node->clave, node->valor);
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
    { bool removed = th_eliminar(&tabla, 4);
      printf("remove:%d\n", (int)removed);
    }
    { bool removed = th_eliminar(&tabla, 99);
      printf("remove:%d\n", (int)removed);
    }
    { THEstadisticas stats = th_estadisticas(&tabla);
      char texto[512];
      th_formatear_estadisticas(&tabla, texto, sizeof(texto));
      printf("stats-C:%d:%d:%d:%d:%.9g\n", stats.capacidad, stats.cantidad, stats.buckets_ocupados, stats.colisiones, (double)stats.factor_carga);
      printf("stats-format:\n%s", texto);
      printf("stats-API-projection:%d:%d:%.17g\n", tabla.capacidad, tabla.cantidad, ((tabla.capacidad > 0) ? ((double)tabla.cantidad / (double)tabla.capacidad) : 0.0));
    }
    th_vaciar(&tabla);
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
    th_destruir(&tabla);
    { int output = 123456789; bool found = th_buscar(&tabla, 1, &output);
      printf("get:%d:%d", 1, (int)found);
      if (found) {
          printf(":%d", output);
      }
      printf("\n");
    }
    { bool found = th_contiene(&tabla, 1);
      printf("contains:%d:%d\n", 1, (int)found);
    }
    { char buffer[2048];
      th_formatear(&tabla, buffer, sizeof(buffer));
      printf("format:items:\n%s", buffer);
      printf("items:");
      for (int i = 0; tabla.buckets && i < tabla.capacidad; i++) {
          for (const THNodo *node = tabla.buckets[i]; node; node = node->siguiente) {
              printf("%d:%d;", node->clave, node->valor);
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
