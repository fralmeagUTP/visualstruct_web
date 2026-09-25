## ADDED Requirements

### Requirement: Ayuda pedagógica de grafos
La ayuda SHALL incluir objetivo, conocimientos previos, estrategia, representación, invariante, memoria, complejidad, restricciones, aplicaciones y errores frecuentes para construcción y cada algoritmo.

#### Scenario: consultar ayuda de Dijkstra
- **WHEN** se abre la ayuda
- **THEN** explica relajación, cola de prioridad, cierre definitivo, complejidad y restricción de pesos no negativos

### Requirement: Glosario contextual de grafos
El sistema SHALL definir vértice, arista, arco, adyacencia, grados, camino, ciclo, componente, relajación, distancia tentativa, predecesor, MST, frontera, Union-Find y ciclo negativo.

#### Scenario: consultar relajación
- **WHEN** se solicita el término durante Bellman-Ford
- **THEN** se explica usando distancia, arista y predecesor del frame actual

### Requirement: Guía docente de grafos
El proyecto SHALL publicar una guía con secuencias de clase, preguntas predictivas, contraejemplos, ejercicios evaluables, errores esperados y rúbrica.

#### Scenario: actividad BFS frente a DFS
- **WHEN** el docente selecciona la actividad comparativa
- **THEN** obtiene grafo común, preguntas, resultados esperados y criterios de evaluación
