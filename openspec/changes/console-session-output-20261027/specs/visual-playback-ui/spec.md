## ADDED Requirements
### Requirement: Observed session stdout
La consola DEBE conservar sólo salida auténtica observada de operaciones anteriores y el prefijo de la operación activa correspondiente al cursor, sin deduplicar impresiones repetidas ni truncar líneas.
#### Scenario: Two queries and replay
- **GIVEN** una consulta que emite stdout seguida por otra consulta
- **WHEN** se avanza, retrocede y reproduce la segunda traza
- **THEN** el prefijo anterior permanece y sólo cambia el prefijo activo; replay no duplica salida.
### Requirement: Observed cache and scrolling
La consola DEBE conservar scroll manual y sólo seguir el final si ya estaba allí; una caché observada DEBE invalidarse si difieren historial o versión o tras reset.
#### Scenario: Reload and reset
- **GIVEN** observaciones cacheadas asociadas exactamente al historial
- **WHEN** se recarga con historial distinto o se restablece la estructura
- **THEN** se descarta la caché sin sintetizar stdout desde resultados o etiquetas.
