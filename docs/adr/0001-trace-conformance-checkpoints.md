# ADR 0001: motor de trazas, conformidad C y checkpoints

- Estado: Aceptado para implementación incremental
- Fecha: 2026-08-18
- OpenSpec: `harden-trace-conformance-and-state`

## Contexto

El servicio de trazas mezcla planificación de control de flujo, reglas de cinco familias,
snapshots y presentación. El estado se reconstruye reproduciendo hasta 300 operaciones. Aunque
los TAD C compilan, su equivalencia con Python no se prueba automáticamente.

## Decisión 1: motor de trazas por estrategias

Se mantendrá una fachada compatible, pero las reglas se moverán a estrategias de secuenciales,
árboles, grafos, hash y ordenamiento. Todas producirán un contrato común `TraceStep` validado por
un `TraceEngine`.

Consecuencias: los cambios por familia quedan aislados, pero durante la migración coexistirán el
modelo nuevo y un adaptador legado. La mitigación es migrar familia por familia y comparar contra
fixtures golden antes de retirar cada camino anterior.

## Decisión 2: estado observable canónico para conformidad

Los runners C y Python se compararán por resultados, errores e invariantes observables, no por
direcciones, nodos auxiliares ni detalles internos de representación. Ningún harness ejecutará
código suministrado por usuarios ni será expuesto mediante HTTP.

## Decisión 3: checkpoints JSON versionados

El historial de eventos continúa siendo la fuente de reconstrucción. Se agregan snapshots JSON
versionados con checksum y posición del historial para reproducir solo eventos posteriores. Ante
cualquier incompatibilidad se descarta el checkpoint y se usa replay completo. No se usará
`pickle` y las sesiones antiguas continuarán funcionando.

## Alternativas descartadas

- Reescribir el intérprete completo: riesgo y costo desproporcionados.
- Persistir objetos Python vivos: complica concurrencia, despliegue y compatibilidad.
- Usar únicamente snapshots: reduce auditabilidad y elimina el replay determinista.
- Comparar estructuras internas C/Python: acopla representaciones legítimamente diferentes.

