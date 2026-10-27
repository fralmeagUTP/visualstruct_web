## ADDED Requirements

### Requirement: Lectura de código sin ajuste de línea
El sistema DEBE conservar indentación y líneas C originales con scroll horizontal local cuando excedan el panel, sin ensanchar la página; el eje vertical DEBE ser independiente.

#### Scenario: Línea ancha en las cinco familias
- **GIVEN** código actual, main del historial o estructura TAD con línea ancha
- **WHEN** se lee en panel normal o ampliado
- **THEN** se alcanza el final mediante la barra local sin hard-wrap, sin mover la página y sin alterar copiar C.

### Requirement: Pan horizontal estable
El resaltado de pasos DEBE conservar la posición horizontal elegida por el usuario sin centrado automático.

#### Scenario: Avanzar y retroceder
- **GIVEN** código desplazado horizontalmente
- **WHEN** cambia la línea activa
- **THEN** se conserva el pan horizontal mientras siga siendo válido.
