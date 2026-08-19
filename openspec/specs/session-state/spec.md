# session-state Specification

## Purpose

Define cómo se persiste y reconstruye el estado de las estructuras por usuario:
sesiones server-side con Flask-Session, historial de operaciones mutantes por
estructura, y reconstrucción del estado por replay del historial (no existen
instancias de estructuras vivas en el servidor).
## Requirements
### Requirement: Backend de sesión server-side
El sistema MUST almacenar las sesiones en servidor usando Flask-Session con backend
`cachelib` (FileSystemCache en `.flask_session/`, threshold `10000`, modo `0o600`)
por defecto, o `redis` cuando `SESSION_TYPE=redis` y `SESSION_REDIS_URL` sea válida.
Si Flask-Session no está instalado, DEBE hacer fallback a sesión por cookie firmada
con una advertencia en el log. Si la conexión a Redis falla, DEBE mantener el
backend configurado y registrar una advertencia.

#### Scenario: sesión filesystem por defecto
- **GIVEN** `SESSION_TYPE` no está definida
- **WHEN** se crea la aplicación
- **THEN** las sesiones se persisten en archivos bajo `.flask_session/`

#### Scenario: Redis como backend
- **GIVEN** `SESSION_TYPE=redis` y `SESSION_REDIS_URL=redis://host:6379/0`
- **WHEN** se crea la aplicación y Redis está accesible
- **THEN** las sesiones se almacenan en Redis con prefijo `wved:`

#### Scenario: fallo de conexión a Redis
- **GIVEN** `SESSION_TYPE=redis` con una URL inalcanzable
- **WHEN** se crea la aplicación
- **THEN** se registra advertencia y la app sigue operativa con la configuración previa

### Requirement: Seguridad de la cookie de sesión
El sistema MUST emitir la cookie `visualstruct_session` siempre con `HttpOnly`,
con `SameSite` configurable (default `Lax`), `Secure` configurable (default `false`),
vida permanente configurable (default `240` minutos) y refresco en cada request.

#### Scenario: cookie emitida con flags seguros
- **WHEN** un cliente recibe la cookie de sesión
- **THEN** la cookie incluye `HttpOnly` y `SameSite=Lax`

### Requirement: Historial de operaciones por estructura
El sistema MUST persistir en sesión, bajo la clave `sequential_histories`, un
historial por estructura que contenga **únicamente operaciones mutantes** como
`{"operation": <nombre>, "payload": <dict>}`. Las operaciones de solo consulta NO
DEBEN registrarse. El historial DEBE truncarse a las últimas `SESSION_MAX_HISTORY`
entradas (default `300`) y descartar elementos que no sean diccionarios.

#### Scenario: operación mutante registrada
- **GIVEN** una pila con historial vacío
- **WHEN** se ejecuta `apilar` con éxito
- **THEN** el historial de `stack` contiene `{"operation": "apilar", "payload": {"value": ...}}`

#### Scenario: consulta no registrada
- **GIVEN** una pila con historial existente
- **WHEN** se ejecuta una operación de consulta (no mutante) con éxito
- **THEN** el historial permanece sin cambios

#### Scenario: truncado al máximo
- **GIVEN** `SESSION_MAX_HISTORY=300` y un historial con 300 entradas
- **WHEN** se registra una operación mutante adicional
- **THEN** el historial conserva solo las últimas 300 entradas

### Requirement: Reconstrucción de estado por replay
El sistema MUST reconstruir el estado de una estructura desde el checkpoint compatible más
reciente y re-ejecutar en orden únicamente las operaciones posteriores. Si no existe checkpoint,
DEBE reconstruir mediante replay completo. Los pasos que fallen durante el replay DEBEN omitirse
silenciosamente y excluirse del historial válido devuelto.

Un checkpoint DEBE incluir versión de esquema, identificador de estructura, versión del adapter,
posición del historial, estado serializado sin `pickle` y checksum. Un checkpoint corrupto,
incompatible o de otra estructura DEBE descartarse y causar fallback a replay completo.

#### Scenario: estado reconstruido desde checkpoint
- **GIVEN** un historial de 120 operaciones y un checkpoint válido en la operación 100
- **WHEN** se solicita el view model de la estructura
- **THEN** el adapter importa el checkpoint y reproduce únicamente las 20 operaciones posteriores
- **AND** el estado final equivale al replay completo

#### Scenario: estado reconstruido tras recargar
- **GIVEN** un historial válido `[apilar(1), apilar(2)]`
- **WHEN** se solicita el view model de la estructura
- **THEN** el estado visual reconstruido contiene los elementos `[1, 2]`

#### Scenario: historial legado sin checkpoint
- **GIVEN** una sesión creada antes de introducir checkpoints
- **WHEN** se reconstruye la estructura
- **THEN** el sistema reproduce el historial completo sin perder operaciones

#### Scenario: checkpoint incompatible
- **GIVEN** un checkpoint con checksum inválido o versión de adapter distinta
- **WHEN** se reconstruye la estructura
- **THEN** el checkpoint se descarta
- **AND** el sistema usa replay completo y registra el fallback sin datos sensibles

#### Scenario: paso inválido omitido en replay
- **GIVEN** un historial que contiene un paso con payload que ahora falla
- **WHEN** se reconstruye el adapter
- **THEN** el paso inválido se omite y el historial devuelto solo contiene pasos válidos

### Requirement: Reinicio de estructura
El sistema MUST permitir eliminar el historial de una estructura, dejándola en
estado vacío.

#### Scenario: reset limpia el historial
- **GIVEN** una estructura con historial persistido
- **WHEN** se invoca el endpoint de reset
- **THEN** el historial de esa estructura se elimina de la sesión y el estado visual queda vacío

### Requirement: Aislamiento entre usuarios
El sistema MUST aislar los historiales por sesión de usuario: dos clientes distintos
NO DEBEN compartir estado de estructuras.

#### Scenario: dos sesiones independientes
- **GIVEN** dos clientes con cookies de sesión distintas
- **WHEN** ambos operan sobre la misma estructura
- **THEN** cada uno observa únicamente su propio historial y estado

### Requirement: Creación periódica de checkpoints
El sistema MUST crear un checkpoint después de un número configurable de operaciones mutantes,
con valor inicial de 50, y DEBE conservar como máximo el número de checkpoints configurado por
estructura.

#### Scenario: intervalo alcanzado
- **GIVEN** intervalo de checkpoint igual a 50
- **WHEN** se confirma la operación mutante número 50
- **THEN** el estado validado se serializa como checkpoint en esa posición

#### Scenario: operación de consulta
- **GIVEN** un historial situado una operación antes del intervalo
- **WHEN** se ejecuta una consulta no mutante
- **THEN** no se crea checkpoint ni cambia la posición del historial

### Requirement: Presupuesto de reconstrucción
En el entorno de rendimiento de referencia, la reconstrucción de una estructura con 300
operaciones y checkpoints habilitados DEBE completar con latencia p95 inferior a 200 ms. La CI o
un job periódico MUST registrar el resultado para detectar regresiones.

#### Scenario: historial máximo
- **GIVEN** un conjunto representativo de historiales de 300 operaciones por familia
- **WHEN** se ejecuta el benchmark de reconstrucción
- **THEN** la latencia p95 es menor a 200 ms
- **AND** el reporte incluye familia, operaciones reproducidas y uso de checkpoint

