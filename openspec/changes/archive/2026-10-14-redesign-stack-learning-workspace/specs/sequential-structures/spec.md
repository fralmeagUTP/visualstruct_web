## ADDED Requirements

### Requirement: Piloto visual limitado a Pila
El rediseño compacto MUST aplicarse inicialmente solo a `stack`. Las demás
estructuras secuenciales deben conservar su disposición actual hasta que el
piloto sea aprobado explícitamente.

#### Scenario: aislamiento del piloto
- **WHEN** se visita Cola, Cola de prioridad, Lista enlazada, Lista circular o
  Sublista durante el piloto
- **THEN** sus pantallas no adoptan accidentalmente la disposición experimental de Pila
