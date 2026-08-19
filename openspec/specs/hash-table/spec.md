# hash-table Specification

## Purpose

Módulo del TAD Tabla Hash (`hash_table`): mapeo clave→valor con encadenamiento por
bucket, estadísticas de carga/colisiones y eventos de rehash, visualizados por
buckets.

## Requirements

### Requirement: Endpoints del módulo hash
El sistema DEBE exponer `GET /hash/`, `GET /hash/<structure_id>`,
`POST /hash/<structure_id>/operate` y `POST /hash/<structure_id>/reset` con el
contrato JSON común (`success`, `message`, `result?`, `visual_state`, `history`,
`execution_trace`; `200`/`400`/`404`).

#### Scenario: índice hash
- **WHEN** un cliente hace `GET /hash/`
- **THEN** responde `200` listando la Tabla Hash

#### Scenario: inserción exitosa
- **WHEN** se envía `{"operation": "insert", "payload": {"key": "ana", "value": "90"}}`
  a `/hash/hash_table/operate`
- **THEN** responde `200` con `success=true` y el par visible en su bucket

### Requirement: Validación de entradas de texto
Los campos `key` y `value` DEBEN validarse como texto no vacío, produciendo el
mensaje de obligatoriedad cuando falten.

#### Scenario: clave vacía rechazada
- **WHEN** se ejecuta `insert` con `{"key": "  ", "value": "x"}`
- **THEN** responde `400` con `"El campo 'clave' es obligatorio."` (o etiqueta equivalente)

### Requirement: Operaciones del TAD
El sistema DEBE soportar `create_table`, `insert` (inserta o actualiza), `get`,
`contains`, `remove`, `keys`, `values`, `items`, `stats`, `clear` y
`destroy_table`/reinicialización, según el contrato del TAD C.

#### Scenario: get de clave existente
- **GIVEN** la tabla contiene `{"ana": "90"}`
- **WHEN** se ejecuta `get` con `{"key": "ana"}`
- **THEN** responde `200` con `result="90"` y sin mutar el historial

#### Scenario: get de clave ausente
- **WHEN** se ejecuta `get` con una clave inexistente
- **THEN** responde `400` indicando que la clave no existe

#### Scenario: remove ajusta la cadena del bucket
- **GIVEN** dos claves que colisionan en el mismo bucket
- **WHEN** se elimina la primera
- **THEN** la segunda sigue siendo accesible vía `get`

### Requirement: Resolución de colisiones por encadenamiento
El sistema DEBE resolver colisiones encadenando entradas dentro del mismo bucket y
DEBE reflejar en el estado visual el tamaño y número de colisiones por bucket.

#### Scenario: colisión visible en el estado
- **GIVEN** dos claves mapeadas al mismo bucket
- **WHEN** se solicita el estado visual
- **THEN** ese bucket reporta `size=2` y `collisions=1`

### Requirement: Rehash por factor de carga
El sistema DEBE redimensionar la tabla cuando el factor de carga supera el umbral
del TAD (0.75), redistribuyendo las claves y registrando el evento de resize en
`metadata` (`resized`, `resize_event`).

#### Scenario: resize al crecer la carga
- **GIVEN** una tabla cerca del umbral de carga
- **WHEN** se inserta una clave que supera el umbral
- **THEN** la capacidad aumenta, las claves se redistribuyen y `metadata` refleja el resize

### Requirement: Estadísticas de la tabla
La operación `stats` DEBE devolver métricas de la tabla: tamaño, capacidad, factor
de carga y colisiones totales, coherentes con el estado visual.

#### Scenario: stats coherentes con buckets
- **GIVEN** una tabla con 6 entradas y capacidad 8
- **WHEN** se ejecuta `stats`
- **THEN** el factor de carga reportado es `0.75` y las colisiones coinciden con la
  suma por bucket

### Requirement: Estado visual por buckets
El adapter DEBE exponer `buckets` (cada uno con `entries`, `size`, `collisions`),
`metadata` (`size`, `capacity`, `load_factor`, `collisions`, `is_empty`,
`resized`, `resize_event`) y `last_operation`/`last_result`.

#### Scenario: tabla vacía
- **WHEN** se solicita el estado visual de una tabla recién creada
- **THEN** `metadata.is_empty=true` y todos los buckets están vacíos
