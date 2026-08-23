# Propuesta: Mejorar la pedagogía del módulo de grafos

## Why

El módulo permite construir grafos y ejecutar BFS, DFS, Dijkstra, Bellman-Ford, Prim y Kruskal, pero gran parte del estado que explica esos algoritmos permanece implícito. El estudiante observa vértices y aristas resaltados sin disponer siempre de la cola, pila, cola de prioridad, tabla de distancias, predecesores, frontera o Union-Find que causaron el cambio.

La pantalla está organizada por funciones del sistema y no por el ciclo cognitivo preparar, predecir, ejecutar, comprender, comparar y reflexionar. Además, algunos respaldos visuales todavía derivan pasos desde el resultado en el frontend, lo cual puede divergir de la ejecución real del código C.

## What Changes

- Emitir frames canónicos de grafos que vinculen cada instrucción C ejecutada con condición, variables, estructuras auxiliares, vértices, aristas, estado anterior/posterior e invariante.
- Eliminar inferencias frontend de recorrido, relajación, camino o MST cuando no procedan de eventos del backend.
- Reorganizar la pantalla en Preparar, Predecir, Ejecutar, Comprender, Relacionar con C, Comparar y Reflexionar.
- Incorporar niveles Básico, Intermedio y Avanzado sobre una única traza.
- Visualizar cola BFS, pila DFS, cola de prioridad, tablas de distancia/predecesor, frontera de Prim y Union-Find de Kruskal.
- Explicar relajaciones exitosas y fallidas, cierre de vértices, ciclos negativos, aceptación/rechazo de aristas e invariantes.
- Añadir ejemplos guiados, predicciones, pistas, práctica, controles completos y progreso conceptual de sesión.
- Comparar BFS/DFS, Dijkstra/Bellman-Ford y Prim/Kruskal sobre copias aisladas de una entrada inmutable.
- Ampliar ayuda, glosario, guía docente, accesibilidad y exportación de evidencia.
- Cerrar con contratos, golden traces, propiedades, equivalencia de modos, Playwright, cobertura, C17, ASan y UBSan.

## Out of Scope

- Añadir algoritmos que no expone actualmente el TAD, como Floyd-Warshall, A* o flujo máximo.
- Ejecutar código C arbitrario suministrado por el usuario.
- Cambiar la semántica pública del TAD C de grafos.
- Persistir calificaciones o datos personales fuera de la sesión.
- Tratar BFS como camino mínimo ponderado o presentar Prim/Kruskal como válidos para grafos dirigidos.

## Dependencies

- Reutiliza el motor común de trazas, reproducción y exportación.
- Conserva las correcciones de fidelidad causal ya cerradas.
- Reutiliza patrones pedagógicos de ordenamiento, estructuras secuenciales y jerárquicas sin compartir estado mutable.

## Impact

- Backend: contrato de frames, invariantes y comparaciones aisladas de grafos.
- Frontend: pantalla, reproductor, visualizaciones auxiliares, práctica y comparador.
- Ayuda: contenido por algoritmo, glosario y guía docente.
- QA: golden traces, propiedades, equivalencia C/backend/traza/UI y accesibilidad.
