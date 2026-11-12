# Código pertinente de Grafos

La opción 3 muestra el algoritmo/operación seleccionado y el cierre transitivo de auxiliares pertinentes. Alcance: BFS, DFS, Dijkstra, Bellman-Ford, Prim, Kruskal e inserción/eliminación de vértice/arista.

Las filas e índices canónicos permanecen intactos para preservar el intérprete; las ajenas se ocultan y no figuran en el índice lateral. Incluye limpieza del resultado propio según el tipo devuelto. C/H, algoritmos, sesiones y semántica de ejecución no cambian.

## Verificación finita

- 26 pruebas nuevas: 16 de fuente/traza y 10 de navegador Chromium.
- 6.924 posiciones de cursor verificadas hacia adelante/atrás; selección, carga, siguiente/anterior, reset, índice lateral y ausencia de solicitudes adicionales al navegar.
- 61 regresiones de rutas/API/capacidad/retornos y 13 de CCodeService.
- Total: 100 pruebas focales aprobadas.
- Parche desplegado y servicio saludable; selección pública verificada para las diez operaciones.

El navegador usa un grafo pequeño no dirigido; la capa de traza añade casos vacíos/inicios inexistentes. No equivale a suite global, cobertura global ni todas las topologías. Al publicar, los cuatro workflows del head previo permanecían en cola sin jobs; no se afirma CI aprobado ni integración en main.
