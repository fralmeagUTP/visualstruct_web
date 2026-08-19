# sequential-structures Specification

## Purpose

Módulo de estructuras secuenciales: Pila (`stack`), Cola (`queue`), Cola de
Prioridad (`priority_queue`), Lista Enlazada (`linked_list`), Lista Circular
(`circular_list`) y Sublista (`sublist`). Expone páginas interactivas y endpoints
JSON para operar cada TAD con trazas didácticas.

## Requirements

### Requirement: Catálogo de estructuras secuenciales
El sistema DEBE mantener un registro de las 6 estructuras secuenciales con `name`,
`description` y clase adapter, y DEBE responder `GET /sequential/` renderizando el
índice con todas ellas.

#### Scenario: índice lista las 6 estructuras
- **WHEN** un cliente hace `GET /sequential/`
- **THEN** responde `200` y la vista incluye Pila, Cola, Cola de Prioridad, Lista
  Enlazada, Lista Circular y Sublista

#### Scenario: estructura desconocida
- **WHEN** se solicita metadata de un id no registrado
- **THEN** se eleva `KeyError` y la ruta responde `404`

### Requirement: Página interactiva de estructura
El sistema DEBE responder `GET /sequential/<structure_id>` con un view model que
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
El sistema DEBE responder `POST /sequential/<structure_id>/operate` aceptando JSON
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
El sistema DEBE rechazar con `400` las peticiones sin nombre de operación
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
Un campo obligatorio ausente DEBE producir `"El campo '<label>' es obligatorio."` y
un valor no entero DEBE producir `"El campo '<label>' debe ser un número entero."`.

#### Scenario: valor no entero rechazado
- **WHEN** se envía `apilar` con `{"value": "abc"}`
- **THEN** responde `400` con el mensaje de entero inválido y la estructura no cambia

### Requirement: Errores didácticos de dominio
El sistema DEBE traducir las excepciones de dominio a mensajes didácticos en
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
El sistema DEBE agregar al historial de sesión únicamente las operaciones marcadas
`mutates: true` que hayan tenido éxito, y DEBE persistir el historial tras cada
operación.

#### Scenario: consulta exitosa no muta historial
- **GIVEN** una pila con historial `[apilar(5)]`
- **WHEN** se ejecuta `cima` con éxito
- **THEN** el historial devuelto sigue siendo `[apilar(5)]` y la respuesta incluye `result`

### Requirement: Reinicio de estructura
El sistema DEBE responder `POST /sequential/<structure_id>/reset` limpiando el
historial de la estructura y devolviendo `success=true`, mensaje de reinicio, el
`visual_state` vacío y `history` vacío. Para estructuras desconocidas DEBE
responder `404`.

#### Scenario: reset exitoso
- **GIVEN** una lista enlazada con elementos
- **WHEN** se hace `POST /sequential/linked_list/reset`
- **THEN** responde `200` con estado visual vacío e historial `[]`

### Requirement: Contrato de adapters secuenciales
Cada adapter secuencial DEBE implementar el contrato común (`create`, `execute`,
`to_visual_state`, `reset`, `get_supported_operations`) y exponer un estado visual
lineal serializable con `kind: "linear"`, `title`, `items`, `size` y `empty`.

#### Scenario: estado visual de pila
- **GIVEN** una pila con valores `[3, 2, 1]` (tope primero)
- **WHEN** se solicita `to_visual_state()`
- **THEN** retorna `kind="linear"`, `title="Pila (tope a fondo)"`, `items` con 3
  entradas, `size=3` y `empty=false`

### Requirement: Operaciones por estructura
El sistema DEBE soportar, como mínimo: Pila (`apilar`, `desapilar`, `limpiar`);
Cola (`encolar`, `desencolar`, consultas de frente/final, `limpiar`); Cola de
Prioridad (`encolar` con prioridad, `desencolar`, `frente`, `limpiar`); Lista
Enlazada (inserciones, eliminaciones, búsquedas, `invertir`, `limpiar`); Lista
Circular (`insertar_inicio`, `insertar_final`, `eliminar_primero`,
`buscar_posiciones`, `invertir`, `limpiar`); Sublista (`insertar_padre`,
`insertar_hijo`, `eliminar_padre`, `eliminar_hijo`, `hijos_de`, `limpiar`).

#### Scenario: encolar con prioridad
- **WHEN** se ejecuta `encolar` en `priority_queue` con `{"value": 9, "priority": 1}`
- **THEN** el elemento queda ordenado por prioridad en el estado visual

#### Scenario: insertar hijo en padre inexistente
- **GIVEN** una sublista sin el padre `10`
- **WHEN** se ejecuta `insertar_hijo` con `{"parent": 10, "child": 1}`
- **THEN** responde `400` con mensaje indicando que el padre no existe
