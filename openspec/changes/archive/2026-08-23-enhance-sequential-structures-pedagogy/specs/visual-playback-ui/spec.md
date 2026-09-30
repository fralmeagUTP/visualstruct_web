## ADDED Requirements

### Requirement: Reproductor reversible para TAD secuenciales
El reproductor SHALL ofrecer preparar, reproducir, pausar, inicio, anterior, siguiente, final y repetir, además
de una barra navegable con función, fase y concepto.

#### Scenario: retroceder sobre free
- **GIVEN** un frame posterior a `free(aux)`
- **WHEN** el estudiante retrocede un paso
- **THEN** se restauran exactamente objeto, punteros, variables, pila, código, consola y estado visual anteriores

### Requirement: Presentación adaptable sin pérdida de contexto
La interfaz SHALL mantener estado y C simultáneamente visibles en escritorio y pestañas persistentes en móvil.

#### Scenario: cambiar a móvil durante una operación
- **GIVEN** una operación pausada
- **WHEN** cambia el ancho y el estudiante alterna entre Estado y Código
- **THEN** conserva cursor, narración, punteros y frame actual

### Requirement: Accesibilidad de estados secuenciales
Los extremos, enlaces, candidatos, memoria y estados SHALL comunicarse mediante texto o símbolos además del color.

#### Scenario: recorrer cola de prioridad con lector
- **WHEN** cambia el candidato seleccionado
- **THEN** una región accesible anuncia valor, prioridad, orden de llegada y motivo de selección

