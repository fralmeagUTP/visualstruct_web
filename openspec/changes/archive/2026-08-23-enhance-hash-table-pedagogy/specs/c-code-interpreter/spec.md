## ADDED Requirements

### Requirement: Frame causal de tabla hash
El intérprete SHALL emitir frames versionados que vinculen cada instrucción C ejecutada con fórmula hash, condición, variables, punteros, cadena, costo, memoria, estado anterior/posterior e invariante.

#### Scenario: calcular índice
- **WHEN** se ejecuta `th_indice`
- **THEN** el frame contiene operandos, residuo, rama de normalización e índice retornado

### Requirement: Llamadas auxiliares completas
El seguimiento SHALL incluir el contenido ejecutado de `th_indice`, `th_buscar`, `th_contiene`, `th_vaciar` y demás auxiliares llamados.

#### Scenario: ejecutar contiene
- **WHEN** `th_contiene` llama a `th_buscar`
- **THEN** el seguimiento entra a la función, recorre la cadena real y retorna al llamador correcto

### Requirement: Ruta sin inferencia frontend
El frontend SHALL NOT deducir bucket, comparaciones, enlaces, reservas o liberaciones desde el resultado final.

#### Scenario: clave ausente
- **WHEN** la búsqueda termina en `NULL`
- **THEN** solo aparecen las comparaciones realmente ejecutadas y no se inventa una coincidencia

### Requirement: Memoria y punteros causales
Los frames SHALL representar `malloc`, comprobación de `NULL`, inicialización, cambios de enlace y `free` con identidades estables.

#### Scenario: liberar nodo intermedio
- **WHEN** el C ejecuta `free(actual)`
- **THEN** el enlace anterior ya fue actualizado y ninguna referencia válida conserva la dirección liberada

### Requirement: Programa principal C17 válido
El historial técnico SHALL generar llamadas con tipos y valores equivalentes a los ejecutados y SHALL compilar como C17.

#### Scenario: exportar historial
- **WHEN** el usuario insertó, buscó y eliminó enteros
- **THEN** el `main` resultante compila con warnings como errores y reproduce el mismo estado/salida

### Requirement: Restauración exacta
Cada frame SHALL permitir restaurar tabla, punteros, cadena activa, memoria, consola, historial y código al navegar en ambas direcciones.

#### Scenario: retroceder sobre free
- **WHEN** se vuelve al frame anterior a la liberación
- **THEN** el nodo y sus enlaces reaparecen con las mismas identidades y no se duplica la consola
