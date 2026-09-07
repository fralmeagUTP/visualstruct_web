# Diseño de validación integral

## Principio de exhaustividad verificable

"Todas las opciones" se define como cada elemento del inventario ejecutable de la versión evaluada, no como una lista estática. El recolector debe leer:

- blueprints y rutas públicas;
- `get_supported_operations()` de cada adaptador;
- algoritmos de ordenamiento y grafos;
- fases de grafo, ejemplos guiados, comparadores y exportaciones;
- controles de reproducción, ayuda, nivel didáctico, predicción, práctica, teclado y preferencias de accesibilidad.

El manifiesto resultante contiene identificador, módulo, URL/API, precondiciones, entradas válidas/límite/erróneas, mutabilidad y oráculo. CI falla si una opción registrada carece de al menos un caso trazable.

## Catálogo base sujeto a recolección

| Módulo | Cobertura mínima |
|---|---|
| Secuenciales | pila, cola, cola de prioridad, lista enlazada, lista circular y sublista; todas las operaciones publicadas, reinicio y ayuda. |
| Jerárquicas | ABB, AVL, rojo-negro y montículo binario; inserción, búsqueda, eliminación, recorridos/ajustes y casos de balance o heap. |
| Grafos | construcción y todas las fases; vértices/aristas, BFS, DFS, Dijkstra, Bellman-Ford, Prim, Kruskal, comparación y errores de pesos/conectividad. |
| Hash | capacidad, inserción, actualización, búsqueda, existencia, eliminación, vaciado, destrucción, fallo controlado de memoria y comparación de capacidades. |
| Ordenamiento | los once algoritmos registrados, selección, entrada manual/aleatoria, ejecución, comparación, escenarios pedagógicos y controles de reproducción. |
| Transversal | inicio, navegación, health check, ayuda, sesiones, validación, exportación, consola, historial, preferencias visuales y responsive. |

## Capas y oráculos

1. **Dominio y C:** el resultado y los invariantes se contrastan con harnesses C17, golden traces y propiedades. Los sanitizers se ejecutan en un entorno que los soporte.
2. **Servicio/API:** se comprueba código HTTP, payload, persistencia/replay de sesión, validación y ausencia de mutación en operaciones de consulta o comparación.
3. **Traza:** cada frame corresponde a una instrucción/rama ejecutada, conserva estados antes/después y llega al mismo estado final que la ejecución rápida.
4. **Interfaz E2E:** Playwright activa cada control real y comprueba DOM, foco, consola, código resaltado, visualización y navegación hacia delante, atrás, reinicio y repetición.
5. **Calidad no funcional:** accesibilidad WCAG 2.2 AA automatizable y revisión guiada, seguridad de entrada/sesión, rendimiento, errores de servidor, responsividad y compatibilidad Chromium/Firefox.

## Datos de prueba

Cada opción recibe, como corresponda: estado vacío, caso normal, primer/último elemento, único elemento, duplicados, valores negativos y cero, límites enteros, colisiones, grafos desconectados/ciclos/pesos negativos, arreglos ya ordenados/inversos/repetidos y payloads inválidos. Los datos aleatorios deben tener semilla registrada para permitir reproducción.

## Artefactos y criterio de salida

- `docs/qa/app-coverage-manifest-v1.json`: inventario y cobertura por opción.
- `docs/qa/comprehensive-app-test-report.md`: resultados, evidencia, ambientes y hallazgos.
- `docs/qa/comprehensive-app-quality-results-v1.json`: resultados consumibles por CI.
- Un hallazgo incluye operación, datos, esperado, observado, severidad, causa probable, ubicación, prueba propuesta y recomendación sin aplicar cambios.

La validación se acepta solo cuando no haya opciones sin caso, no haya fallos críticos/altos abiertos, pasen los gates funcionales y los fallos de infraestructura estén identificados separadamente.
