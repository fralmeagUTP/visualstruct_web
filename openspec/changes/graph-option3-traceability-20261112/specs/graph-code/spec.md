## ADDED Requirements

### Requirement: Alcance explícito de diez operaciones
La opción 3 de Grafos DEBE presentar la operación seleccionada y únicamente funciones de su cierre transitivo de llamadas C más limpieza pertinente del resultado propio. DEBE cubrir BFS, DFS, Dijkstra, Bellman-Ford, Prim, Kruskal, insertar vértice, eliminar vértice, insertar arista y eliminar arista.

#### Scenario: Seleccionar cualquiera de las diez operaciones
- **GIVEN** una operación de la matriz de evidence/traceability.md
- **WHEN** el usuario la selecciona en modo técnico
- **THEN** el lector y su índice muestran su entrada C y auxiliares pertinentes, no algoritmos ajenos
- **AND** el criterio de operación/subrutinas coincide con la referencia solicitada Pilas/apilar y Árboles/eliminar, sin modificar esos módulos.

### Requirement: Limpieza de resultados pertinente
La selección DEBE incluir las subrutinas de liberación del resultado propio que el caller deba ejecutar; no DEBE confundir esa limpieza con código de otro algoritmo.

#### Scenario: Resultado propio de recorrido o arcos
- **WHEN** se selecciona BFS/DFS o un algoritmo de caminos/expansión
- **THEN** se incluye respectivamente grafo_liberar_vertices o grafo_liberar_arcos y sus auxiliares pertinentes.

### Requirement: Coordenadas y sincronía canónicas
El filtrado NO DEBE modificar fuente C/H, fuente de traza, índices nativos, semántica de instrucciones ni estado de memoria. Cada paso C DEBE resaltar la fila original correspondiente y mantenerla visible.

#### Scenario: Adelante, atrás y reinicio
- **GIVEN** una traza cargada de cualquiera de las diez operaciones
- **WHEN** se navega adelante/atrás por todos sus cursores o se reinicia
- **THEN** la línea activa coincide con line_index y line_text canónicos; un paso sin línea C no muestra resaltado inventado
- **AND** navegar no vuelve a ejecutar la operación ni añade POSTs.

### Requirement: Selección y vista consistentes
El filtro DEBE seguir vigente al cargar traza, cambiar operación y alternar documentación extensa, sin reutilizar alcance de otra selección.

#### Scenario: Cambiar selección tras recorrer una traza
- **WHEN** el usuario cambia a otra operación de su fase
- **THEN** visibilidad e índice corresponden a la nueva selección y conservan índices canónicos.
