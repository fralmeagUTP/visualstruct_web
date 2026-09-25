# Propuesta: reorganizar el espacio de aprendizaje de Grafos

## Why

El módulo de Grafos distribuye construcción, algoritmos, predicción, controles, visualización, código, comparación y resultados en siete bloques con controles repetidos. Esto dificulta seguir simultáneamente una instrucción C, el auxiliar del algoritmo y la arista o vértice que cambia.

La propuesta traslada el patrón aprobado para estructuras secuenciales: flujo corto, controles claros, visualización y código legibles, comprensión plegable y resultados reunidos, sin alterar algoritmos ni trazas canónicas.

## Inventario real incluido

El repositorio contiene un único TAD `graph` con estas rutas:

| Ruta | Alcance |
|---|---|
| `/graph/graph` y `/graph/graph/construccion` | crear/reiniciar, generar aleatorio, vértices, aristas y consultas |
| `/graph/graph/recorridos` | BFS y DFS |
| `/graph/graph/camino-minimo` | Dijkstra y Bellman-Ford |
| `/graph/graph/expansion-minima` | Prim y Kruskal |

Las operaciones públicas son crear/generar, insertar/eliminar vértice y arista, consultas de vértices/aristas/vecinos/peso, BFS, DFS, Dijkstra, Bellman-Ford, Prim, Kruskal y limpiar. `/graph/compare` permanece disponible.

## What Changes

- Normalizar cada fase con: 1. **Preparar y controlar**; 2. **Visualizar y ejecutar**; 3. **Relacionar con código C**; 4. **Comprender**; 5. **Resultados de la ejecución**.
- Conservar la navegación entre fases, pero mantener operación/algoritmo, entradas y controles principales en una sola tarjeta compacta.
- Hacer **Ejecutar operación** y **Paso a paso** las acciones principales; Anterior/Siguiente aparecen durante la traza.
- Mantener lienzo, leyenda y código C correlacionados; en móvil se conserva el conmutador existente entre ambos paneles.
- Adaptar Comprender a auxiliares reales: cola/visitados de BFS, pila o recursión de DFS, distancias/predecesores y relajación, y frontera/Union-Find para MST.
- Retirar de la vista principal nivel, Ejemplo guiado, Predecir y Comparar. No se eliminan datos ni endpoint de comparación.
- Agrupar consola C, historial, TAD y exportaciones en Resultados plegable, con el TAD estático al abrirlo.

## Out of Scope

- Crear algoritmos, representaciones, tipos de grafo o rutas nuevas.
- Cambiar políticas reales de lazos, aristas paralelas, pesos, validaciones o algoritmos.
- Eliminar `/graph/compare` o sus copias aisladas.
- Añadir pruebas automatizadas.

## Success Criteria

En las cuatro fases, una persona puede preparar y ejecutar un caso real, leer código y lienzo sin perder contexto, y recorrer sólo los frames ejecutados. Resultados se pliega como unidad.
