## ADDED Requirements

### Requirement: Caller Hash compartido y ejecutado
El sistema DEBE generar y ejecutar las mismas instrucciones printf de un AST finito del caller sobre los retornos, structs y buffers reales, preservando C/H canónicos.

#### Scenario: Búsqueda ausente
- **GIVEN** una llamada real de búsqueda que retorna false
- **WHEN** el caller ejecuta su printf y evalúa su if
- **THEN** imprime el indicador ausente y no lee output ni inventa un valor.

#### Scenario: Estadísticas y listado
- **GIVEN** buffers terminados y celdas reales de la traza TAD
- **WHEN** el caller imprime el buffer y su proyección pública
- **THEN** los bytes coinciden con el main compilado en C17 bajo el perfil verificado.

### Requirement: Prefijo Hash y cursor
El sistema DEBE conservar el stdout del journal y publicar sólo el prefijo de stdout actual al cursor.

#### Scenario: Repetición y recarga
- **GIVEN** consultas repetidas y una consulta ausente observadas
- **WHEN** se recarga la sesión o se retrocede y avanza dentro de la traza
- **THEN** las consultas permanecen en el journal y no se duplica ni anticipa stdout.

### Requirement: Epílogo independiente
El sistema DEBE distinguir las instrucciones por operación del printf final de main.

#### Scenario: Limpieza interactiva
- **GIVEN** clear o destroy void en una sesión interactiva
- **WHEN** retorna la operación
- **THEN** no agrega mensajes inventados ni ejecuta el printf state del epílogo de main.
