## ADDED Requirements
### Requirement: Entrada múltiple sin cambiar TAD
El visualizador DEBE validar todos los valores antes de invocar operaciones unitarias y conservar orden, historia y C auténticos.
#### Scenario: Lista inválida
- **GIVEN** una lista con entrada vacía, fuera de int32 o duplicado prohibido
- **WHEN** se intenta iniciar
- **THEN** no se ejecuta ninguna operación y se señala posición.
### Requirement: Control secuencial honesto
La cola DEBE ejecutar como máximo una operación en vuelo y respetar fin de traza antes de otra operación.
#### Scenario: Detener o fallo incierto
- **GIVEN** una operación aceptada o respuesta incierta
- **WHEN** se detiene o falla el transporte
- **THEN** conserva lo confirmado, descarta pendientes, no reintenta y no promete rollback.
