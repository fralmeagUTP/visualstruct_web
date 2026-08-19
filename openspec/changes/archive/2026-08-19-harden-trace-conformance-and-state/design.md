# Diseño técnico

## 1. Principios

- Migración incremental y compatible con las respuestas JSON actuales.
- Determinismo: el mismo historial y versión producen el mismo estado.
- Un solo modelo de pasos; reglas especializadas mediante estrategias.
- El código C sigue siendo la referencia didáctica, pero ahora es verificable.
- La optimización de estado nunca debe ocultar corrupción ni aceptar snapshots incompatibles.

## 2. Motor modular de trazas

### Contrato `TraceStep`

Cada paso tendrá, como mínimo:

```text
line_index: int | null
line_text: str
event: str
stage: str
before_state: dict
after_state: dict
console: list[str]
metadata: dict
```

`event` describe semántica estable (`condition`, `allocation`, `assignment`, `link`,
`rotation`, `visit`, `compare`, `swap`, `return`, `error`) y no una etiqueta de UI.

### Componentes

- `TraceEngine`: valida el contrato, ordena pasos, limita volumen y garantiza estado final.
- `ControlFlowPlanner`: selecciona líneas ejecutadas a partir del snippet y el resultado.
- `TraceStrategy`: interfaz para generar eventos específicos de una familia.
- Estrategias: `SequentialTraceStrategy`, `TreeTraceStrategy`, `GraphTraceStrategy`,
  `HashTraceStrategy` y `SortingTraceStrategy`.
- `TraceStrategyRegistry`: resuelve la estrategia por `structure_id`.

El endpoint y el frontend conservarán inicialmente el JSON actual. Un adaptador de
compatibilidad proyectará `TraceStep` al esquema legado mientras se migra la UI.

## 3. Conformidad C↔Python

### Harness C

Cada TAD tendrá un ejecutable de prueba no interactivo que reciba un escenario serializado o
generado en compilación y produzca un estado canónico. El harness no aceptará código arbitrario
ni será invocado desde endpoints web.

### Estado canónico

- Secuenciales: secuencia de valores y tamaño.
- Árboles: recorrido in-order, forma cuando sea contractual e invariantes de balance/color.
- Montículo: arreglo lógico, tamaño y propiedad de heap.
- Grafo: vértices, aristas normalizadas y resultados algorítmicos.
- Hash: pares clave/valor, capacidad lógica y estadísticas contractuales.
- Ordenamiento: arreglo final y métricas contractuales cuando sean equivalentes.

Las pruebas diferenciales usarán semillas fijas, conservarán el escenario mínimo que falle y
distinguirán diferencias de contrato de diferencias de representación.

### Seguridad de memoria

La CI Linux compilará con `-std=c17 -Wall -Wextra -Wpedantic -Werror` y ejecutará AddressSanitizer
y UndefinedBehaviorSanitizer. Los fallos serán bloqueantes.

## 4. Checkpoints de sesión

La sesión conservará eventos mutantes y un checkpoint opcional:

```json
{
  "schema_version": 1,
  "history_offset": 100,
  "structure_id": "stack",
  "adapter_version": "...",
  "state": {},
  "checksum": "..."
}
```

El servicio reconstruirá desde el checkpoint compatible y reproducirá solo eventos posteriores.
Si versión, checksum o estructura no coinciden, descartará el checkpoint y hará replay completo.
Los historiales actuales sin checkpoint seguirán siendo válidos.

Se generará un checkpoint cada número configurable de operaciones, inicialmente 50. El formato
serializado será responsabilidad del adaptador mediante métodos explícitos; no se usará `pickle`.

## 5. Configuración segura

Se introduce `APP_ENV=development|testing|production`. En `production`, el arranque fallará si:

- `FLASK_SECRET_KEY` falta o conserva el valor de desarrollo;
- `SESSION_COOKIE_SECURE` es falso, salvo override explícito documentado;
- `ENABLE_PROXY_FIX` es verdadero sin número de proxies confiables configurado.

Desarrollo y pruebas conservarán defaults cómodos y mensajes de advertencia claros.

## 6. Compatibilidad y migración

1. Añadir pruebas golden sobre el comportamiento actual.
2. Introducir contratos y adaptadores sin cambiar respuestas públicas.
3. Migrar secuenciales, árboles, hash, grafos y ordenamiento, en ese orden.
4. Activar checkpoints detrás de una opción de configuración.
5. Ejecutar ambos caminos en pruebas y comparar resultados.
6. Eliminar el camino legado solo cuando todas las familias estén migradas.

## 7. Observabilidad

Se medirán `replay_operations`, `checkpoint_hit`, `checkpoint_fallback`,
`trace_steps_generated`, `trace_strategy` y duración de reconstrucción. Los logs no incluirán
cookies, secretos ni payloads completos de usuario.

