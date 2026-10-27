## ADDED Requirements
### Requirement: Canon del libro sin alteración
El sistema DEBE utilizar C/H idénticos al libro y adaptar su implementación interpretada a ese contrato.
#### Scenario: Descargar código
- **GIVEN** la extracción canónica verificada
- **WHEN** se descarga grafo.c/h desde la segunda copia
- **THEN** los bytes y las firmas coinciden, sin sustituciones para acomodar el intérprete.
### Requirement: Estados y memoria fieles
El sistema DEBE preservar GrafoEstado, atomicidad, rangos y propiedad según la instrucción C ejecutada por el intérprete.
#### Scenario: Fallo de reserva
- **GIVEN** una inserción con extremos nuevos
- **WHEN** falla una reserva alcanzable
- **THEN** retorna GRAFO_MEMORIA sin publicar extremos/arco parciales y libera reservas temporales.
#### Scenario: NULL exitoso
- **GIVEN** un camino de inicio a sí mismo o MST singleton
- **WHEN** el canon retorna NULL con GRAFO_OK
- **THEN** la aplicación no inventa un error ni una lista propia inexistente.
### Requirement: Trazas y clase coherentes
El sistema DEBE enseñar las instrucciones y estructuras auxiliares del libro, con navegación reversible y main compilable.
#### Scenario: Recorrido y publicación de marcas
- **GIVEN** BFS/DFS con marcas previas
- **WHEN** ocurre un fallo o se completa el recorrido
- **THEN** las marcas se conservan al fallar y sólo se publican al éxito, en las instrucciones reales.
### Requirement: Compatibilidad explícita
El sistema DEBE aislar el nuevo contrato y preservar históricos sin reinterpretación silenciosa.
#### Scenario: Historial anterior
- **GIVEN** una historia o checkpoint del contrato web anterior
- **WHEN** se intenta cargar en el contrato del libro
- **THEN** no se usa una traza vieja; se informa de la incompatibilidad y se conserva la historia o se valida una transición explícita.
