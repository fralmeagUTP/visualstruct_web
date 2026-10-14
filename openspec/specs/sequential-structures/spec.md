# sequential-structures Specification

## Purpose

Módulo de estructuras secuenciales: Pila (`stack`), Cola (`queue`), Cola de
Prioridad (`priority_queue`), Lista Enlazada (`linked_list`), Lista Circular
(`circular_list`) y Sublista (`sublist`). Expone páginas interactivas y endpoints
JSON para operar cada TAD con trazas didácticas.
## Requirements
### Requirement: Catálogo de estructuras secuenciales
El sistema MUST mantener un registro de las 6 estructuras secuenciales con `name`,
`description` y clase adapter, y MUST responder `GET /sequential/` renderizando el
índice con todas ellas.

#### Scenario: índice lista las 6 estructuras
- **WHEN** un cliente hace `GET /sequential/`
- **THEN** responde `200` y la vista incluye Pila, Cola, Cola de Prioridad, Lista
  Enlazada, Lista Circular y Sublista

#### Scenario: estructura desconocida
- **WHEN** se solicita metadata de un id no registrado
- **THEN** se eleva `KeyError` y la ruta responde `404`

### Requirement: Página interactiva de estructura
El sistema MUST responder `GET /sequential/<structure_id>` con un view model que
incluya `id`, `name`, `description`, `operations` (metadata con inputs y flag
`mutates`), `visual_state` reconstruido desde el historial de sesión, contenido
didáctico (código C o fallback) y `history` válido.

#### Scenario: página con estado previo
- **GIVEN** el usuario apiló 3 valores en `stack` previamente
- **WHEN** hace `GET /sequential/stack`
- **THEN** la página muestra los 3 elementos reconstruidos desde el historial

#### Scenario: página de estructura inexistente
- **WHEN** hace `GET /sequential/no_existe`
- **THEN** responde `404`

### Requirement: Ejecución de operaciones
El sistema MUST responder `POST /sequential/<structure_id>/operate` aceptando JSON
`{"operation": <nombre>, "payload": <dict>}` y devolviendo un cuerpo con `success`,
`message`, `visual_state`, `history` y `execution_trace` (más `result` cuando la
operación retorna valor). Responde `200` si la operación tiene éxito y `400` con el
mismo contrato si falla.

#### Scenario: operación exitosa
- **WHEN** se envía `{"operation": "apilar", "payload": {"value": 7}}` a `/sequential/stack/operate`
- **THEN** responde `200` con `success=true`, mensaje `"Se apiló '7' correctamente."`
  y el `visual_state` contiene el nuevo tope

#### Scenario: operación no soportada
- **WHEN** se envía `{"operation": "inventada", "payload": {}}`
- **THEN** responde `400` con mensaje indicando que la operación no está soportada
  y sin alterar el historial

#### Scenario: estructura inexistente en operate
- **WHEN** se envía la operación a `/sequential/no_existe/operate`
- **THEN** responde `404`

### Requirement: Validación del cuerpo de la petición
El sistema MUST rechazar con `400` las peticiones sin nombre de operación
(`"Debes seleccionar una operación."`) o con `payload` que no sea un objeto
(`"El payload enviado es inválido."`).

#### Scenario: operación vacía
- **WHEN** se envía `{"operation": "", "payload": {}}`
- **THEN** responde `400` con el mensaje de operación faltante

#### Scenario: payload no es diccionario
- **WHEN** se envía `{"operation": "apilar", "payload": [1,2]}`
- **THEN** responde `400` con el mensaje de payload inválido

### Requirement: Validación de entradas enteras
Los campos `value`, `parent`, `child` y equivalentes DEBEN validarse como enteros.
Un campo obligatorio ausente MUST producir `"El campo '<label>' es obligatorio."` y
un valor no entero MUST producir `"El campo '<label>' debe ser un número entero."`.

#### Scenario: valor no entero rechazado
- **WHEN** se envía `apilar` con `{"value": "abc"}`
- **THEN** responde `400` con el mensaje de entero inválido y la estructura no cambia

### Requirement: Errores didácticos de dominio
El sistema MUST traducir las excepciones de dominio a mensajes didácticos en
español: estructura vacía → `"No se puede ejecutar la operación porque la
estructura está vacía."`; posición inválida → `"La posición ingresada es inválida
para el estado actual."`; elemento no encontrado y otros errores de TAD → su propio
mensaje. Los errores inesperados DEBEN reportarse como `"Ocurrió un error inesperado
durante la operación."`.

#### Scenario: desapilar pila vacía
- **GIVEN** una pila vacía
- **WHEN** se ejecuta `desapilar`
- **THEN** responde `400` con el mensaje de estructura vacía y el `visual_state` sin cambios

### Requirement: Registro de historial solo en mutaciones
El sistema MUST conservar operaciones reales mutantes y consultas registradas explícitamente por el journal aprobado. Las consultas MUST preservar el estado estructural aunque añadan evidencia cronológica; GET/reconstrucción/replay MUST NOT volver a ejecutar la consulta histórica. Una consulta pública rechazada o no registrada MUST NOT crear entrada exitosa, llamada C ni resultados inventados.

#### Scenario: consulta registrada y recarga
- **GIVEN** una consulta Priorityfrente exitosa registrada por el contrato vigente
- **WHEN** se recarga o reconstruye su historial
- **THEN** mantiene resultado cronológico y estado sin un nuevo dispatch de consulta

#### Scenario: consulta privada no publicada
- **WHEN** se pide CimaPila o FrenteFinalCola por la API pública no registrada
- **THEN** responde rechazo sin journal exitoso ni ejecución C y no se publica una nueva opción para satisfacer el diseño antiguo

#### Scenario: consulta exitosa no muta historial
- **GIVEN** una pila con historial apilar5 y núcleo privado cima
- **WHEN** se evalúa la consulta privada en su harness aceptado
- **THEN** retorna5 sin cambiar estructura ni fabricar una entrada de historial
- **AND** una solicitud pública no registrada permanece rechazada; no se afirma un éxito API o UI

### Requirement: Reinicio de estructura
El sistema MUST responder `POST /sequential/<structure_id>/reset` limpiando el
historial de la estructura y devolviendo `success=true`, mensaje de reinicio, el
`visual_state` vacío y `history` vacío. Para estructuras desconocidas MUST
responder `404`.

#### Scenario: reset exitoso
- **GIVEN** una lista enlazada con elementos
- **WHEN** se hace `POST /sequential/linked_list/reset`
- **THEN** responde `200` con estado visual vacío e historial `[]`

### Requirement: Contrato de adapters secuenciales
Cada adapter secuencial MUST implementar el contrato común (`create`, `execute`,
`to_visual_state`, `reset`, `get_supported_operations`) y exponer un estado visual
lineal serializable con `kind: "linear"`, `title`, `items`, `size` y `empty`.

#### Scenario: estado visual de pila
- **GIVEN** una pila con valores `[3, 2, 1]` (tope primero)
- **WHEN** se solicita `to_visual_state()`
- **THEN** retorna `kind="linear"`, `title="Pila (tope a fondo)"`, `items` con 3
  entradas, `size=3` y `empty=false`

### Requirement: Operaciones por estructura
El sistema MUST exponer las operaciones registradas vigentes: Pila apilar/desapilar/limpiar; Cola encolar/desencolar/limpiar; Prioridad encolar/desencolar/limpiar y frente como API hidden registrada; listas/sublista según metadata canónica. Invertir de Lista enlazada está retirado por autorización y MUST NOT reaparecer; invertir de Lista circular conserva su contrato. CimaPila/FrenteFinalCola permanecen núcleos privados con rechazo público, sin player ni consulta UI exitosa. Prioridad MUST conservar el orden de llegada y seleccionar el primer mínimo estable sin ordenar físicamente la cadena. Las APIs hidden conservadas MUST distinguirse de opciones del selector.

#### Scenario: encolar con prioridad
- **GIVEN** una cola con entradas de prioridades distintas
- **WHEN** se encola un elemento con prioridad
- **THEN** el nodo se añade según orden de llegada y la selección de frente/desencolar respeta el mínimo estable
- **AND** no se presenta una ordenación de la cadena como ejecución C

#### Scenario: insertar hijo en padre inexistente
- **GIVEN** una sublista sin el padre10
- **WHEN** se ejecuta insertar_hijo con parent10/child1
- **THEN** el rechazo conserva estructura e historial conforme al contrato C y no inventa una inserción

### Requirement: Piloto visual limitado a Pila
El rediseño compacto MUST aplicarse inicialmente solo a `stack`. Las demás
estructuras secuenciales deben conservar su disposición actual hasta que el
piloto sea aprobado explícitamente.

#### Scenario: aislamiento del piloto
- **WHEN** se visita Cola, Cola de prioridad, Lista enlazada, Lista circular o
  Sublista durante el piloto
- **THEN** sus pantallas no adoptan accidentalmente la disposición experimental de Pila

### Requirement: Descripción exacta de inserción en primera posición
El mensaje de una inserción exitosa MUST describir la rama alcanzada del contrato C canónico; para insertar_elemento con position1 MUST indicar inserción al inicio, independientemente del desplazamiento permitido.

#### Scenario: Primera posición con desplazamiento después
- **GIVEN** lista[1,3] yposition1,relative0,value2.
- **WHEN** insertar_elemento se ejecuta exitosamente.
- **THEN** lista[2,1,3] ymensaje al inicio, sin afirmar después.

#### Scenario: Posición posterior conserva su descripción
- **GIVEN** lista[1,3] yposition2,relative0,value2.
- **WHEN** insertar_elemento se ejecuta exitosamente.
- **THEN** lista[1,3,2] ymensaje después de la posición2.

### Requirement: Fragmento printf de eliminación simple
La traza de eliminar_elemento en lista simple MUST conservar el literal printf ejecutado, incluido el terminador de línea, en el evento correspondiente.

#### Scenario: Eliminación en lista vacía
- **GIVEN** lista simple vacía y eliminación por valor.
- **WHEN** el C alcanza el printf de lista vacía y retorna.
- **THEN** console contiene exactamente un fragmento " Valor no encontrado o lista vacia.\n" en el printf y ningún fragmento nuevo en return.

