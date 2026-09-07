## ADDED Requirements

### Requirement: Frame causal de estructura secuencial
El intérprete SHALL emitir frames versionados que vinculen una instrucción C realmente ejecutada con condición,
variables, pila, punteros, objetos de memoria, consola, estado anterior y estado posterior.

#### Scenario: enlazar un nodo nuevo
- **WHEN** el C ejecuta `aux->sgte = *p`
- **THEN** el frame identifica ambos objetos, el destino anterior y nuevo, la línea exacta y el estado visual resultante

### Requirement: Prohibición de interpolación visual
El sistema SHALL rechazar la asociación de frames a líneas C por proporción, posición aproximada o análisis de ramas en el frontend.

#### Scenario: no existe evento para una línea
- **GIVEN** una línea C que no fue ejecutada
- **WHEN** se reproduce la operación
- **THEN** no aparece un frame visual atribuido a esa línea

### Requirement: Trazabilidad de ciclos circulares
Los recorridos circulares SHALL registrar cada iteración, identidad lógica visitada y condición real de salida.

#### Scenario: volver al nodo inicial
- **WHEN** el cursor alcanza nuevamente el primer nodo
- **THEN** el frame evalúa la condición de parada y termina sin inventar otra iteración

