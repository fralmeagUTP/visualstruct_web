## ADDED Requirements

### Requirement: Salida ejecutada del caller
El sistema DEBE ejecutar las mismas instrucciones printf del caller que genera en main.c, sobre los retornos reales del TAD, conservando intactos C/H canónicos.

#### Scenario: Consulta Dijkstra
- **GIVEN** un grafo y una consulta con ruta, sin ruta, inicio igual a destino o error C
- **WHEN** se ejecuta el caller generado
- **THEN** su stdout interpretado coincide con stdout del mismo main compilado en C17 y aparece sólo al alcanzar la instrucción del caller.

### Requirement: Historial de consola y navegación
La consola DEBE mostrar el prefijo de operaciones anteriores y sólo la salida actual emitida al cursor, sin duplicar salida al repetir.

#### Scenario: Retroceso y recarga
- **GIVEN** una sesión con operaciones anteriores y una consulta actual
- **WHEN** el lector retrocede, avanza y repite la traza
- **THEN** conserva el prefijo, restaura el snapshot de stdout actual y no ejecuta otro POST.
- **WHEN** recarga la sesión
- **THEN** la consola restaura el stdout completo de su historial real.

### Requirement: Scroll legible
La consola DEBE permitir scroll vertical y horizontal y preservar la posición del lector cuando no está al final.

#### Scenario: Salida extensa
- **GIVEN** una consola con muchas líneas y líneas largas
- **WHEN** llegan nuevos fragmentos
- **THEN** sólo sigue automáticamente el final si el lector ya estaba al final.
