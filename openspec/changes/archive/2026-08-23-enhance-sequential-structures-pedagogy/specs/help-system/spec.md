## ADDED Requirements

### Requirement: Ayuda pedagógica por TAD secuencial
La ayuda SHALL explicar objetivo, estrategia, invariante, memoria, casos límite y errores frecuentes de cada TAD.

#### Scenario: consultar cola de prioridad
- **WHEN** el estudiante abre su ayuda
- **THEN** encuentra la diferencia entre orden de llegada, prioridad, selección y desempate estable con un ejemplo reproducible

### Requirement: Material docente secuencial
El sistema SHALL publicar una guía docente con secuencias de clase, preguntas predictivas, actividades y criterios de dominio.

#### Scenario: preparar una clase LIFO frente a FIFO
- **WHEN** un docente consulta la guía
- **THEN** dispone de una secuencia común, preguntas, resultados esperados y actividad de cierre

### Requirement: Glosario de memoria y enlaces
La ayuda SHALL ofrecer definiciones contextuales de nodo, enlace, alias, LIFO, FIFO, prioridad, circularidad,
`malloc`, `NULL`, `free` e invariante.

#### Scenario: consultar free durante una traza
- **WHEN** el estudiante abre la definición contextual de `free`
- **THEN** comprende qué memoria deja de ser válida y por qué no deben quedar punteros colgantes

