# graph-learning-workspace Specification

## Purpose
TBD - created by archiving change reorganize-graph-learning-workspace. Update Purpose after archive.
## Requirements
### Requirement: Flujo coherente en todas las fases de Grafos
Construcción, Recorridos, Camino mínimo y Expansión mínima MUST presentar las cinco etapas comunes en orden y sin numeración repetida. La fase activa MUST seguir limitando operaciones y algoritmos disponibles.

#### Scenario: abrir Camino mínimo
- **WHEN** una persona visita `/graph/graph/camino-minimo`
- **THEN** prepara Dijkstra o Bellman-Ford dentro de la primera etapa
- **AND** encuentra visualización, código, comprensión y resultados en orden

### Requirement: Visualización fiel del frame de algoritmo
El lienzo MUST reflejar sólo vértices, aristas, pesos, auxiliares y decisiones existentes en el frame canónico. BFS/DFS, caminos mínimos y MST MUST comunicar con texto además de color sus estados activos e invariantes.

#### Scenario: relajación de Dijkstra
- **WHEN** un frame mejora una distancia tentativa
- **THEN** se identifica arista, distancia y predecesor actualizados
- **AND** Comprender explica la relajación correspondiente al código activo

### Requirement: Código C vertical y correlacionado
Relacionar con código C MUST ubicar funciones sobre el código, con checkbox junto al encabezado. El bloque C MUST usar el ancho disponible sin scroll horizontal global y mantener el resaltado del frame.

#### Scenario: elegir una función de Prim
- **WHEN** se elige una función en Expansión mínima
- **THEN** el código asociado aparece debajo a ancho completo
- **AND** el lienzo conserva la arista o frontera activa

### Requirement: Resultados agrupados y plegables
Resultados de la ejecución MUST ocultar/restaurar juntos consola C, historial, TAD y exportaciones; el TAD MUST ser estático cuando el panel esté abierto.

#### Scenario: Consultar el resultado sin recargar el área principal

- **WHEN** una operación de grafo termina y la persona abre Resultados de la ejecución
- **THEN** consola C, historial técnico, resumen del TAD y exportaciones se muestran en el mismo grupo
- **AND** abrir o cerrar ese grupo no altera el lienzo, la traza ni el código activo
