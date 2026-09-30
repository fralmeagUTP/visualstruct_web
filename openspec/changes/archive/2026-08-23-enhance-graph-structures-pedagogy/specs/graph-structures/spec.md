## ADDED Requirements

### Requirement: Progresión pedagógica de grafos
El módulo SHALL ofrecer niveles Básico, Intermedio y Avanzado sobre una única traza canónica y SHALL conservar grafo, algoritmo, entrada, fase, estado y cursor al cambiar de nivel.

#### Scenario: cambiar de nivel durante una relajación
- **GIVEN** Dijkstra pausado al examinar una arista
- **WHEN** el estudiante cambia de Básico a Avanzado
- **THEN** permanece en el mismo frame y aparecen expresión C, variables, cola de prioridad, distancias y predecesores

### Requirement: Construcción y representación causal
La construcción SHALL sincronizar dibujo, lista de adyacencia, grados, orientación, peso y memoria C en cada inserción o eliminación.

#### Scenario: eliminar un vértice con aristas incidentes
- **WHEN** se elimina un vértice
- **THEN** la traza identifica cada arco desconectado/liberado y la lista de adyacencia coincide con el dibujo final

### Requirement: Explicación causal de BFS
BFS SHALL mostrar cola FIFO, extracción, examen de vecinos, descubrimiento, nivel y árbol de predecesores.

#### Scenario: descubrir un vecino
- **WHEN** BFS examina un vecino no visitado
- **THEN** el frame muestra la condición verdadera, lo marca una sola vez, asigna nivel/predecesor y lo inserta al final de la cola

### Requirement: Explicación causal de DFS
DFS SHALL mostrar pila explícita o recursiva, vértice activo, descenso, backtracking y finalización.

#### Scenario: retornar de una rama
- **WHEN** un vértice no tiene vecinos pendientes
- **THEN** el frame lo marca finalizado, restaura el llamador y continúa con el siguiente vecino real

### Requirement: Explicación causal de Dijkstra
Dijkstra SHALL mostrar pesos válidos, cola de prioridad, extracción mínima, relajaciones, cierre y reconstrucción por predecesores.

#### Scenario: relajación exitosa
- **WHEN** `dist[u] + peso < dist[v]` es verdadera
- **THEN** se muestran valores sustituidos, distancia anterior/nueva, nuevo predecesor y actualización de la cola

#### Scenario: peso negativo
- **WHEN** la entrada contiene un peso negativo
- **THEN** Dijkstra no se ejecuta y la ayuda explica por qué su invariante dejaría de ser válido

### Requirement: Explicación causal de Bellman-Ford
Bellman-Ford SHALL mostrar iteración, arista activa, relajación, cambios, terminación anticipada y pasada de detección de ciclos negativos.

#### Scenario: detectar ciclo negativo alcanzable
- **WHEN** una arista todavía puede relajarse después de `V-1` iteraciones desde el origen
- **THEN** se marca el ciclo negativo alcanzable y no se presenta una ruta mínima válida

### Requirement: Explicación causal de Prim
Prim SHALL mostrar conjunto incorporado, frontera, clave, padre, candidato, arista aceptada y peso acumulado.

#### Scenario: elegir arista de frontera
- **WHEN** existen varias candidatas
- **THEN** la traza demuestra cuál tiene clave mínima y por qué conecta un vértice nuevo

### Requirement: Explicación causal de Kruskal y Union-Find
Kruskal SHALL mostrar aristas ordenadas, componentes, `find`, compresión, `union` y aceptación o rechazo por ciclo.

#### Scenario: rechazar una arista
- **WHEN** ambos extremos tienen el mismo representante
- **THEN** la arista se rechaza con evidencia textual y las componentes no cambian

### Requirement: Invariantes verificables de grafos
Cada frame SHALL publicar el invariante aplicable, su estado y evidencia concreta por vértice, arista, nivel, componente o distancia.

#### Scenario: validar un MST final
- **WHEN** termina Prim o Kruskal sobre un grafo conexo
- **THEN** se demuestra cobertura, aciclicidad, `V-1` aristas y peso total

### Requirement: Ejemplos guiados de grafos
El módulo SHALL preparar mediante operaciones públicas ejemplos normales, límites, inválidos, desconectados, ponderados y con ciclos.

#### Scenario: cargar ciclo negativo
- **WHEN** se prepara el ejemplo Bellman-Ford correspondiente
- **THEN** el grafo y la operación quedan listos sin regenerarse al reproducir

### Requirement: Comparaciones aisladas de algoritmos
Las comparaciones SHALL usar copias profundas independientes de un grafo inmutable y sincronizarse por concepto.

#### Scenario: comparar Dijkstra y Bellman-Ford
- **WHEN** ambos reciben el mismo grafo de pesos no negativos
- **THEN** se comparan relajaciones, estructura auxiliar, restricciones y resultado sin compartir historial
