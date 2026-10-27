# Migración del arnés al C canónico del libro

Fallo inicial conservado: [C17/sanitizers, commit 2e080c2](https://github.com/fralmeagUTP/visualstruct_web/actions/runs/40515360028). El arnés utilizaba firmas anteriores: inserción sin `GrafoEstado`, costo como valor centinela y algoritmos sin salida de estado. No compilaba contra el C/H entregado.

El arnés ahora observa explícitamente estados y el indicador de salida escrita, usa las funciones canónicas de liberación y acumula costos en `long long`. El caso histórico con un cuarto vértice aislado exige `GRAFO_DESCONECTADO` y resultado nulo, en lugar de presentar un árbol parcial como MST completo.

La regresión adicional compila el archivo canónico sin editarlo e instrumenta únicamente su unidad de traducción. Verifica:

- Caminos de costo 4294967294 con Dijkstra y Bellman-Ford.
- Arco ausente sin escribir la salida, costo cero y actualización de duplicado.
- Ausencia de vértice, camino propio válido y destino inaccesible.
- MST unitario válido, desconexión, asimetría y conexión simétrica.
- Cada reserva de inserciones y de BFS, DFS, caminos, MST, sucesores y predecesores: fallo real, limpieza completa y conservación de marcas ante fallo.
- Publicación de marcas de recorrido sólo tras éxito y destrucción final sin reservas vivas.

La misma regresión se integra en C17, AddressSanitizer y UBSan. Localmente pasan los trece arneses con eventos QA y flags estrictos. Los resultados Linux remotos se revisan por separado; este registro no certifica el resto de la suite ni autoriza un despliegue con CI fallido. Los 26 C/H de la entrega permanecen intactos.
