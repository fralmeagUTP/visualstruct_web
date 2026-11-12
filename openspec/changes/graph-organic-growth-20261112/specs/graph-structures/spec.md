## ADDED Requirements

### Requirement: Continuidad geométrica incremental
La visualización DEBE conservar continuidad espacial al insertar vértices y aristas sin imponer un círculo al superar quince vértices. No DEBE modificar el grafo ni resultados C para lograrlo.

#### Scenario: Crecimiento de un componente
- **GIVEN** un componente de quince vértices ya dibujado
- **WHEN** se añade el vértice dieciséis y sus aristas
- **THEN** el dibujo crece desde las posiciones existentes sin sustituirlas por un anillo.

#### Scenario: Reproducción de estados
- **GIVEN** una topología vista durante paso a paso
- **WHEN** se retrocede y vuelve a avanzar
- **THEN** se reutilizan las posiciones conocidas, sin cambiar pesos, dirección ni resultados.

### Requirement: Comentario pedagógico de GrafoEstado
La referencia DEBE explicar los estados según su uso real, sin cambiar tokens ejecutables ni índices de líneas de las funciones.

#### Scenario: Lectura del enum
- **GIVEN** la fuente C canónica
- **WHEN** se consulta GrafoEstado
- **THEN** se distinguen éxito, memoria, ausencia, pesos/ciclos negativos, desconexión, argumentos y rango sin inventar garantías.
