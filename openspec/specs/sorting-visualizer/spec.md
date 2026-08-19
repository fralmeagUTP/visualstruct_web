# sorting-visualizer Specification

## Purpose

Módulo de ordenamiento (`sorting_array`): visualizador de algoritmos clásicos del
TAD C sobre arreglos de enteros, con API dedicada bajo `/api/ordenamiento/`,
navegación por cursor paso a paso y trazas con comparaciones e intercambios.

## Requirements

### Requirement: Páginas del módulo
El sistema DEBE responder `GET /sorting/` con el índice del módulo y
`GET /sorting/visualizador` con el visualizador (modelo reconstruido desde el
historial de sesión bajo la clave `sorting::sorting_array`). La ruta alias
`GET /sorting/sorting_array` DEBE comportarse igual que `/sorting/visualizador`.

#### Scenario: alias de compatibilidad
- **WHEN** un cliente hace `GET /sorting/sorting_array`
- **THEN** recibe la misma página que `GET /sorting/visualizador`

### Requirement: Creación de arreglos
El sistema DEBE crear arreglos desde texto vía `POST /api/ordenamiento/create-array`
con `{"values": "..."}` y generar arreglos aleatorios vía
`POST /api/ordenamiento/random-array` con `size`, `min_value`, `max_value` y `seed`
opcional (misma semilla DEBE producir el mismo arreglo).

#### Scenario: crear arreglo desde lista de valores
- **WHEN** se envía `{"values": "5,3,8,1"}` a `create-array`
- **THEN** responde `200` y el estado visual contiene el arreglo `[5, 3, 8, 1]`

#### Scenario: aleatorio reproducible con semilla
- **WHEN** se envía `random-array` dos veces con `{"size": 10, "seed": 42}`
- **THEN** ambas respuestas contienen exactamente el mismo arreglo

### Requirement: Selección y ejecución de algoritmos
El sistema DEBE soportar los 11 algoritmos del TAD: `intercambio`, `seleccion`,
`insercion`, `burbuja`, `shell`, `quicksort`, `mergesort`, `heapsort`,
`counting_sort`, `binsort` y `radixsort`, seleccionables vía
`POST /api/ordenamiento/algorithm` y ejecutables vía `POST /api/ordenamiento/run`
con `mode` (`step_by_step` o completo).

#### Scenario: ordenamiento correcto
- **GIVEN** el arreglo `[5, 3, 8, 1]`
- **WHEN** se selecciona `quicksort` y se ejecuta `run`
- **THEN** el estado final es `[1, 3, 5, 8]`

#### Scenario: algoritmo desconocido
- **WHEN** se selecciona un `algorithm_id` inexistente
- **THEN** responde `400` indicando que el algoritmo no es válido

### Requirement: Navegación por cursor paso a paso
El sistema DEBE permitir navegar la ejecución con `POST /api/ordenamiento/step`
usando `direction` (`next`/`prev`) y `cursor`, devolviendo el paso actual con las
comparaciones, intercambios/movimientos y rangos activos correspondientes.

#### Scenario: avanzar un paso
- **GIVEN** una ejecución paso a paso de `burbuja` sobre `[3, 1, 2]`
- **WHEN** se envía `step` con `{"direction": "next", "cursor": -1}`
- **THEN** responde `200` con el primer paso de la traza y el nuevo cursor

#### Scenario: retroceder un paso
- **GIVEN** el cursor en el paso 3
- **WHEN** se envía `step` con `{"direction": "prev", "cursor": 3}`
- **THEN** responde `200` con el paso anterior y el cursor actualizado

### Requirement: Consulta y reinicio de estado
El sistema DEBE responder `GET /api/ordenamiento/state` con el estado actual del
visualizador y `POST /api/ordenamiento/reset` reiniciando arreglo y cursor.

#### Scenario: estado actual
- **WHEN** un cliente hace `GET /api/ordenamiento/state`
- **THEN** recibe `200` con el arreglo actual, algoritmo seleccionado y cursor

#### Scenario: reset del módulo
- **GIVEN** una ejecución en curso
- **WHEN** se hace `POST /api/ordenamiento/reset`
- **THEN** el estado vuelve a vacío y el historial de sesión del módulo se limpia

### Requirement: Contrato de errores del API
Los endpoints del API DEBEN devolver el contrato JSON común (`success`, `message`,
`visual_state`, `history`, `execution_trace`) con `200` en éxito, `400` en error de
validación/operación y `404` ante estructura desconocida.

#### Scenario: validación fallida
- **WHEN** se envía `create-array` con valores no numéricos
- **THEN** responde `400` con mensaje didáctico y sin mutar el estado previo

### Requirement: Trazas didácticas de ordenamiento
Las ejecuciones DEBEN producir trazas que muestren comparaciones, intercambios o
movimientos, pivote (quicksort), rangos activos y arreglos auxiliares (mergesort,
counting, radix), sincronizadas con el código C del algoritmo.

#### Scenario: burbuja muestra intercambios
- **GIVEN** el arreglo `[2, 1]`
- **WHEN** se ejecuta `burbuja` paso a paso
- **THEN** la traza incluye la comparación `(2,1)` y el intercambio resultante
