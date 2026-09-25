# Diseño pedagógico del módulo de tablas hash

## Decisiones de fidelidad

1. La primera versión mejorada mantiene capacidad fija porque esa es la semántica del TAD C actual.
2. La clave externa es la clave almacenada y comparada por el C; no se permiten identificadores sustitutos invisibles.
3. Clave y valor son enteros mientras la estructura C sea `int`/`int`.
4. Un valor de texto solo podrá añadirse con otro TAD C que defina copia, propiedad y liberación de cadenas.
5. El frontend representa eventos del backend y no infiere búsquedas, comparaciones o cambios de enlaces desde el resultado final.
6. Cada cambio visual debe corresponder a una instrucción C ejecutada.

## Arquitectura de pantalla

- **Preparar:** capacidad, operación, nivel y ejemplo guiado.
- **Predecir:** índice, colisión, comparación, actualización, enlace o liberación esperada.
- **Ejecutar:** tabla y código visibles simultáneamente, con controles completos.
- **Comprender:** fórmula hash, variables, cadena activa, costo observado, memoria e invariante.
- **Relacionar con C:** índice de funciones, línea activa, llamadas, punteros, retornos y `printf`.
- **Comparar:** misma entrada en capacidades distintas sobre copias aisladas.
- **Reflexionar:** conclusión, historial, errores frecuentes y exportación.

En móvil se usarán pestañas persistentes Tabla/Código sin perder cursor ni estado auxiliar. Las tablas grandes ofrecerán vista completa, solo ocupados y minimapa, manteniendo accesible el bucket activo.

## Contrato de frame

```json
{
  "schema_version": 1,
  "operation": "insert",
  "concept": "hash|compare|allocate|link|update|unlink|free|return",
  "source": {"line_index": 31, "line_text": "int indice = th_indice(tabla, clave);"},
  "hash": {"key": -2, "capacity": 3, "raw_remainder": -2, "normalized_index": 1},
  "condition": {"substituted": "actual->clave == -2", "result": false},
  "variables": {"indice": 1, "cantidad": 2},
  "pointers": {"actual": "0xNODO-02", "anterior": "NULL", "nuevo": "0xNODO-03"},
  "chain": {"bucket": 1, "before": [1, 4], "after": [-2, 1, 4], "examined": [1, 4]},
  "cost": {"hash_evaluations": 1, "comparisons": 2},
  "memory": {"allocated": ["0xNODO-03"], "freed": [], "links_changed": ["bucket[1]"]},
  "state_before": {},
  "state_after": {},
  "invariant": {"holds": true, "evidence": "-2 pertenece a bucket 1; cantidad=3"},
  "narration": {"basic": "...", "intermediate": "...", "advanced": "..."}
}
```

## Invariantes

- Todo nodo está en `th_indice(tabla, nodo->clave)`.
- No existen claves duplicadas.
- `cantidad` coincide con el número de nodos alcanzables.
- Cada cadena termina en `NULL` y no contiene ciclos.
- Ningún bucket referencia memoria liberada.
- Actualizar una clave no cambia cantidad, dirección ni colisiones.
- Vaciar libera nodos y conserva buckets/capacidad; destruir también libera buckets y deja estado cero.

## Comparación por capacidad

Una comparación recibe una secuencia inmutable de claves y crea copias independientes con capacidades, por ejemplo, 3, 7 y 17. Se sincroniza por inserción y muestra buckets ocupados, colisiones, longitud máxima/promedio, factor de carga y comparaciones de búsqueda. No se usa como prueba universal de rendimiento.

## Estrategia de pruebas

- Golden traces de índice positivo/negativo, colisión, actualización, búsqueda y eliminación.
- Propiedades de ubicación, unicidad, cantidad, aciclicidad y ausencia de referencias colgantes.
- Casos vacíos, capacidad 1, colisiones múltiples, clave cero, negativos y fallos de `malloc`.
- Compilación del `main` exportado y conformidad C17.
- Equivalencia frame a frame entre C, backend, traza, consola, historial y visualización.
- Playwright para reproducción, práctica, comparación, teclado, móvil y movimiento reducido.
- Suite completa, cobertura, AddressSanitizer y UndefinedBehaviorSanitizer.
