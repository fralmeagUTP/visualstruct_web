## ADDED Requirements

### Requirement: Identificadores registrados en ayuda
Las páginas de ayuda de los cinco módulos SHALL responder 404 para identificadores no registrados en el módulo solicitado. Las estructuras registradas SHALL conservar 200; sin mapeo C SHALL conservar el placeholder y c_available=false.

#### Scenario: Identificador inexistente o de otro módulo
- **WHEN** se solicita ayuda para un identificador inexistente o registrado solo en otro módulo
- **THEN** responde 404

#### Scenario: Estructura registrada sin C
- **GIVEN** una estructura registrada sin mapeo C
- **WHEN** se solicita su ayuda
- **THEN** responde 200 con placeholder y c_available=false
