## ADDED Requirements

### Requirement: Material docente del módulo de ordenamiento
El sistema SHALL incluir una guía docente con objetivos, secuencias sugeridas, preguntas de
predicción, actividades comparativas y criterios observables de comprensión.

#### Scenario: preparar una clase de métodos cuadráticos
- **WHEN** un docente consulta la secuencia de Intercambio, Selección, Inserción y Burbuja
- **THEN** obtiene ejemplos comunes, preguntas, conceptos a contrastar y una actividad de cierre

### Requirement: Glosario contextual
El sistema SHALL ofrecer definiciones contextuales enlazadas desde la pantalla para términos de
ordenamiento y C, sin abandonar el frame actual.

#### Scenario: consultar estabilidad
- **GIVEN** una ejecución pausada
- **WHEN** el estudiante abre el término `estable`
- **THEN** ve definición y ejemplo con duplicados y al cerrar conserva el mismo cursor
