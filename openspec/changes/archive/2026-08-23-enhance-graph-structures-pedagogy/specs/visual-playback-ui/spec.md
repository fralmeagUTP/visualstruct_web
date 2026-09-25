## ADDED Requirements

### Requirement: Reproductor reversible de grafos
El reproductor SHALL ofrecer preparar, reproducir, pausar, inicio, anterior, siguiente, final y repetir, con progreso navegable por función, fase, concepto, vértice y arista.

#### Scenario: navegar a una relajación
- **WHEN** el estudiante selecciona un punto de la barra de progreso
- **THEN** grafo, tabla, auxiliar, código, consola e historial muestran el mismo frame

### Requirement: Estructuras auxiliares visibles
La interfaz SHALL mostrar cola BFS, pila DFS, cola de prioridad, tabla de distancias/predecesores, frontera de Prim y Union-Find cuando el C los utiliza.

#### Scenario: ejecutar Kruskal
- **WHEN** se examina una arista
- **THEN** son visibles la lista ordenada, componentes, representantes y decisión causal

### Requirement: Predicción opcional de grafos
El estudiante SHALL poder predecir extracción, vecino, relajación, predecesor, arista MST o ciclo, solicitar pistas y continuar sin responder.

#### Scenario: predecir relajación
- **GIVEN** distancias y peso visibles
- **WHEN** se activa modo práctica
- **THEN** el siguiente estado permanece oculto hasta responder o continuar

### Requirement: Presentación adaptable de grafos
La interfaz SHALL mantener grafo y C simultáneamente visibles en escritorio y pestañas persistentes en móvil sin perder contexto.

#### Scenario: alternar grafo y código en móvil
- **GIVEN** DFS pausado durante backtracking
- **WHEN** se cambia de pestaña
- **THEN** conserva cursor, pila, vértice activo, tabla e invariante

### Requirement: Leyenda y accesibilidad de grafos
Estados de vértices, aristas, orientación, pesos, relajaciones y MST SHALL comunicarse mediante texto o símbolos además de color y movimiento.

#### Scenario: anunciar una arista rechazada
- **WHEN** Kruskal rechaza una arista
- **THEN** una región accesible anuncia extremos, peso, representantes y motivo del rechazo

### Requirement: Exportación de evidencia de grafos
El módulo SHALL exportar captura y resumen con grafo, algoritmo, entrada, cursor, frame, auxiliar, tablas, invariante, resultado y progreso de sesión.

#### Scenario: exportar una relajación
- **WHEN** se exporta durante Dijkstra
- **THEN** la evidencia incluye arista, condición, distancia/predecesor antes y después
