## REMOVED Requirements
### Requirement: Validación de entradas de texto
**Reason**: Sustituido por Validación de entradas enteras según decisión H1 aprobada.
**Migration**: No prometer compatibilidad de sesiones de texto; auditoría posterior verifica entradas y sesiones.

### Requirement: Rehash por factor de carga
**Reason**: Sustituido por Capacidad fija de la tabla según decisión H1 aprobada.
**Migration**: No anunciar resize automático; creación explícita permite elegir capacidad.

## ADDED Requirements

### Requirement: Validación de entradas enteras
Los campos `key` y `value` SHALL validarse como enteros representables por el tipo `int` del TAD C. La capacidad de creación SHALL ser un entero positivo representable por ese tipo. El sistema SHALL rechazar entradas ausentes o no enteras; no SHALL convertir texto libre en identificadores internos para simular claves.

#### Scenario: texto libre rechazado
- **WHEN** se ejecuta `insert` con `{"key": "ana", "value": 90}`
- **THEN** responde `400` indicando entrada entera inválida, sin insertar una clave sustituta

#### Scenario: par entero conservado
- **WHEN** se inserta `{"key": -2, "value": 90}` en una tabla válida
- **THEN** se conservan directamente la clave -2 y el valor 90


### Requirement: Capacidad fija de la tabla
El sistema SHALL conservar la capacidad elegida al crear una tabla durante inserciones, actualizaciones, consultas, eliminaciones y vaciado. El factor de carga no SHALL activar resize ni rehash automático. El encadenamiento permite más entradas que buckets. Una creación explícita puede elegir otra capacidad; la destrucción conserva su semántica de liberación del TAD C.

#### Scenario: carga mayor que uno
- **GIVEN** una tabla de capacidad 3 con claves 1, 4 y 7
- **WHEN** se inserta la clave 10
- **THEN** conserva capacidad 3 y las claves originales encadenadas en bucket 1; la interfaz no anuncia resize ni rehash

#### Scenario: vaciado conserva capacidad
- **GIVEN** una tabla creada con capacidad 3
- **WHEN** se ejecuta `clear`
- **THEN** quedan cero entradas y se conserva capacidad 3


## MODIFIED Requirements

### Requirement: Endpoints del módulo hash
El sistema SHALL exponer `GET /hash/`, `GET /hash/<structure_id>`,
`POST /hash/<structure_id>/operate` y `POST /hash/<structure_id>/reset` con el
contrato JSON común (`success`, `message`, `result?`, `visual_state`, `history`,
`execution_trace`; `200`/`400`/`404`).

#### Scenario: índice hash
- **WHEN** un cliente hace `GET /hash/`
- **THEN** responde `200` listando la Tabla Hash

#### Scenario: inserción exitosa
- **WHEN** se envía `{"operation": "insert", "payload": {"key": 1, "value": 90}}`
  a `/hash/hash_table/operate`
- **THEN** responde `200` con `success=true` y el par visible en su bucket


### Requirement: Operaciones del TAD
El sistema SHALL soportar `create_table`, `insert` (inserta o actualiza), `get`,
`contains`, `remove`, `keys`, `values`, `items`, `stats`, `clear` y
`destroy_table`/reinicialización, según el contrato del TAD C.

#### Scenario: get de clave existente
- **GIVEN** la tabla contiene `{1: 90}`
- **WHEN** se ejecuta `get` con `{"key": 1}`
- **THEN** responde `200` con `result=90` y sin mutar el historial

#### Scenario: get de clave ausente
- **WHEN** se ejecuta `get` con una clave inexistente
- **THEN** responde `400` indicando que la clave no existe

#### Scenario: remove ajusta la cadena del bucket
- **GIVEN** dos claves que colisionan en el mismo bucket
- **WHEN** se elimina la primera
- **THEN** la segunda sigue siendo accesible vía `get`


### Requirement: Estado visual por buckets
El adapter SHALL exponer `buckets` (cada uno con `entries`, `size`, `collisions`),
`metadata` (`size`, `capacity`, `load_factor`, `collisions`, `is_empty`,
`capacity_policy="fixed"`) y `last_operation`/`last_result`. La vista no SHALL anunciar un resize automático inexistente.

#### Scenario: tabla vacía
- **WHEN** se solicita el estado visual de una tabla recién creada
- **THEN** `metadata.is_empty=true` y todos los buckets están vacíos

### Requirement: Resolución de colisiones por encadenamiento
El sistema SHALL resolver colisiones encadenando entradas dentro del mismo bucket y
SHALL reflejar en el estado visual el tamaño y número de colisiones por bucket.

#### Scenario: colisión visible en el estado
- **GIVEN** dos claves mapeadas al mismo bucket
- **WHEN** se solicita el estado visual
- **THEN** ese bucket reporta `size=2` y `collisions=1`


### Requirement: Estadísticas de la tabla
La operación `stats` SHALL devolver métricas de la tabla: tamaño, capacidad, factor
de carga y colisiones totales, coherentes con el estado visual.

#### Scenario: stats coherentes con buckets
- **GIVEN** una tabla con 6 entradas y capacidad 8
- **WHEN** se ejecuta `stats`
- **THEN** el factor de carga reportado es `0.75` y las colisiones coinciden con la
  suma por bucket

