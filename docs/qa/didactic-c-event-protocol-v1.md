# Protocolo de eventos C didácticos v1

Los harnesses emiten su estado canónico por `stdout`. Cuando la variable
`VISUALESTRUCT_QA_EVENTS=1` está activa, emiten adicionalmente eventos NDJSON por `stderr`; así la
instrumentación no cambia el contrato de conformidad existente.

Cada línea usa `schema: "didactic-c-event/v1"` y contiene:

- `sequence`: entero contiguo desde cero por invocación;
- `structure_id`: TAD auditado;
- `event`: categoría (`lifecycle`, `argument`, `condition`, `branch`, `loop`, `call`, `return`,
  `assignment`, `allocation`, `free`, `pointer_link`, `comparison`, `swap`, `printf` o `error`);
- `phase`: posición semántica (`begin`, `input`, `before`, `after`, `output`, `return`, `end`);
- `detail`: descripción estable sin direcciones físicas ni datos secretos.

La primera versión instrumenta el ciclo de vida, argumentos, errores y finalización en los 13
harnesses. Las extensiones por familia añadirán eventos semánticos y estados intermedios sin
romper estos campos obligatorios.

```json
{"schema":"didactic-c-event/v1","sequence":0,"structure_id":"stack","event":"lifecycle","phase":"begin","detail":"harness invocation"}
```

## Valores observables e identidad lógica

Los eventos `return` que producen un entero usan el detalle reproducible
`value=<entero>` (y, cuando corresponda, `priority=<entero>`). Las líneas de
`stdout` que no son documentos `canonical-state/v1` se conservan como salidas
equivalentes a `printf`.

Las identidades visuales se derivan de snapshots consecutivos mediante IDs
lógicos deterministas (`node:1`, `entry:2`, etc.). Las direcciones físicas no
forman parte del contrato y nunca deben llegar al frontend.

## Reglas

1. El canal es determinista para los mismos argumentos y fuentes.
2. No se usan direcciones de memoria como identidad contractual.
3. Un error emite `event=error`, `phase=return` antes de terminar con código no cero.
4. Una ejecución exitosa termina con `event=lifecycle`, `phase=end` después del estado canónico.
5. Cada operación exitosa emite `event=snapshot`, `phase=before` inmediatamente antes de escribir
   su estado canónico intermedio en `stdout`; el último JSON adicional es el estado final.
6. El orden de los snapshots constituye la secuencia causal C contra la que se comparan los frames
   del frontend.

## Cobertura interna de las fuentes

El runner `scripts/run_c_execution_coverage.py` recompila cada caso con `--coverage`,
`-fcondition-coverage` y `-O0`. El reporte `c-execution-coverage.json` conserva por fuente las
líneas y funciones ejecutadas, sus conteos, llamadas, condiciones y ramas tomadas/no tomadas.
Estos datos son el oráculo de qué rutas internas se ejecutaron realmente, incluidos ciclos,
recursión, retornos anticipados y `switch`, sin modificar las fuentes de los TAD.
