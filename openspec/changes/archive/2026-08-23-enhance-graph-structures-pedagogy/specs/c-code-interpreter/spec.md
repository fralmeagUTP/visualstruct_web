## ADDED Requirements

### Requirement: Frame causal de grafos
El intérprete SHALL emitir frames versionados que vinculen cada instrucción C ejecutada con condición, variables, auxiliares, vértices, aristas, tablas, memoria, estado anterior/posterior e invariante.

#### Scenario: extraer de la cola BFS
- **WHEN** el C ejecuta la extracción
- **THEN** el frame muestra cola antes/después, vértice retornado y continuación exacta

### Requirement: Ruta de grafos sin inferencia frontend
El frontend SHALL NOT deducir recorridos, relajaciones, predecesores, caminos, selección MST ni ciclos a partir del resultado final o de diferencias aproximadas.

#### Scenario: relajación fallida
- **GIVEN** una arista que no mejora la distancia
- **WHEN** se reproduce el frame
- **THEN** no cambia distancia ni predecesor y no aparece una actualización inventada

### Requirement: Condiciones sustituidas de grafos
Las comparaciones SHALL mostrar expresión C, valores concretos, resultado y consecuencia real, incluyendo visitado, distancia, representante y frontera.

#### Scenario: comprobar componentes en Kruskal
- **WHEN** se evalúa `find(u) != find(v)`
- **THEN** aparecen ambos representantes, resultado y decisión de aceptar o rechazar

### Requirement: Semántica de memoria de grafos
Los frames SHALL representar reserva, inicialización, enlaces, desconexión y liberación de vértices, aristas y auxiliares con identidades lógicas estables.

#### Scenario: liberar un vértice
- **WHEN** el C ejecuta `free`
- **THEN** todas sus referencias incidentes ya están desconectadas y no quedan punteros válidos hacia memoria liberada

### Requirement: Restauración causal completa
Cada frame SHALL contener estado suficiente para restaurar exactamente grafo, auxiliares, tablas, consola, historial y visualización al navegar en ambas direcciones.

#### Scenario: retroceder una unión
- **WHEN** se retrocede sobre `union`
- **THEN** se restauran padres/rangos, arista candidata, componentes y línea C anteriores
