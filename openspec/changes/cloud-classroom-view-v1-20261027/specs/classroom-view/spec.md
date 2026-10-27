## ADDED Requirements
### Requirement: Visualización de clase prioritaria
La UI DEBE mantener estructura grande y C lateral, con zoom/pan explícitos y memoria opcional.
#### Scenario: ABB9 y estructura degenerada
- **GIVEN** nueve nodos y una traza real.
- **WHEN** se avanza o retrocede20frames.
- **THEN** valores legibles, imagen prioritaria, zoom/pan conservados y documento estable.
### Requirement: Resultados accesibles sin alterar contenido
La UI DEBE separar consola,main y TAD con controles de copiar/ampliar reversibles.
#### Scenario: copiar y cerrar panel ampliado
- **GIVEN** resultado C real y main del historial.
- **WHEN** se cambia panel, copia código y cierra ampliación.
- **THEN** texto compilable exacto, stdout intacto, foco/vista restaurados y ninguna operación nueva.
### Requirement: Alcance transversal y conservación
Las cinco familias DEBEN usar el criterio adaptado sin modificar C ni productores.
#### Scenario: regresión de cinco familias
- **GIVEN** sorting,secuenciales,jerárquicas,grafos yhash.
- **WHEN** se prueban casos representativos y exportaciones.
- **THEN** controles, memoria opcional, copias y exportación funcionan; C/H coinciden con v0.
