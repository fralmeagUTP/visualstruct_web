# Dictamen independiente: numeric-event-canonical-dag

Fecha: 2026-10-06. Proyecto canónico D:\MisProyectos\Web_VisualEstruct. Change review-sorting-projection-diff-coverage-quality; operación audit.numeric-event-canonical-dag-independent-quality; assignment coordination-numeric-event-canonical-dag-qa-low-20261006. Guarda before exit0 observada a10:44:33UTC antes de las comparaciones. No revisión C1 ni reapertura histórica.

**ACEPTAR la equivalencia funcional finita y el diagnóstico adverso. RECHAZAR este prototipo como optimización de memoria y como fundamento para BF30/adopción. Recomiendo descartar su representación actual como candidato de retención.** No hay corrección local única demostrada que resuelva ambos bloqueos: memorizar la decodificación reduce duplicación en validación, pero deja intacta la regresión durante generación. No propongo construir otra arquitectura sin presupuesto.

## Evidencia independiente

Los1.864 inputs del binding coinciden por SHA256, sin faltantes ni diferencias. Descomprimí y comparé íntegramente los40 archivos finales lógicos/transport con el paquete previo owned-canonical-history: bytes completos iguales en los20 casos,7.267 pasos y7.247 eventos. Esto conserva IDs/orden/tipos representados por los mismos bytes, source, estados, C_memory y salidas del alcance previamente validado. El builder sólo cambia el import del finalizador/pool y steps=[] por pool.history; BranchMachine idéntica. No se ejecutó la aplicación ni se repitieron pruebas.

EventHistory guarda IDs enteros y una referencia débil al propietario. publish conserva tabla codificada y referencias, no realizaciones lógicas históricas. materialize crea memo nuevo por llamada, devuelve contenedores ordinarios y no mantiene ese memo; la mutación de una realización temporal no cambia la tabla. Los finally eliminan las funciones recursivas para cortar sus ciclos. El caché activo de máquina persiste legítimamente. La etapa inicial con ciclos permanece archivada y no cuenta como otros20 casos.

La lectura de controles y sus scripts es coherente con cuatro aliases, once errores exactos, cuatro fallos de callback, once DAG malformados/inaccesibles, colisiones forzadas y omisión detectada, ocho mutaciones rechazadas y lifetime con GC deshabilitado. Los fallos tras cinco publicaciones conservan prefijo, C_memory y callback desacoplado. Los seis pares HTTP y dos grupos solapados de siete pares mantienen comparación completa/session6→7 o6. El fallo interno candidato después del primer header se compara con fallo baseline después de pack completo: demuestra efecto visible/rollback, no igualdad del punto interno. No hay archivos HTTP crudos separados ni fallo RAM real demostrado por la inyección.

Comprobé once registros de lanzamiento: diez positivos con before0 anterior/igual al inicio downstream y harness0; uno negativo exit2 sin downstream. Uno positivo corresponde a la etapa inicial, nueve al helper final. La fuente guarded_launch condiciona la creación del job/Popen al exit0; private_limits exige membresía y2GiB antes de imports. Los incidentes antiguos y corrección aditiva exit1→2 siguen intactos. Las guardas actuales no autentican retroactivamente el before histórico tardío.

## Mediciones y causa

Recalculé máximos de cinco checkpoints y porcentajes desde generation-joint-small.json:

| Caso | Baseline B | Event B | Aumento |
|---|---:|---:|---:|
| Dijkstra |4.399.951|7.802.260|77,3261%|
| Bellman-Ford |5.256.798|9.532.683|81,3401%|
| Prim |5.640.706|10.353.683|83,5530%|
| Kruskal |5.100.067|9.394.193|84,1974%|

El traversal suma una sola unión por identidad, con pool/tabla, paso actual y locales reales de builder/máquina/evaluador. La comparación no suma presupuestos independientes que dupliquen objetos compartidos. publish construye filas y pares list, referencias dict e índice; la tabla pública expandida pasa a existir desde generación. Estos componentes y la materialización actual explican un mecanismo consistente con el aumento; no se midió atribución exhaustiva del coste por tipo. El negativo BF que retiene realizaciones históricas tiene36.756.381B y bytes iguales: demuestra sensibilidad a retención real y liberación del candidato, pero no mejora frente al baseline.

validate_graph_logical_trace se conserva íntegro: conversiones round-trip, normalización, semantic.append y TraceEngine.validate_steps. Al iterar EventHistory, cada materialize tiene memo independiente. semantic.append conserva before_state/after_state de esas realizaciones. La sharing anterior entre pasos no sobrevive; el observado2→758 identidades para exactamente dos valores concuerda con esa causa concreta. Unión BF de validación5.492.762→11.230.051B (+104,45% aproximadamente), sin omitir validaciones.758 no significa758 estados semánticos distintos ni pruebas nuevas.

Estos bytes son checkpoints de graph traversal, no peak del proceso. deep omite closure cells y temporales internos en curso; el high-water del worker multi-arm contiene brazos anteriores. GC entre brazos no es GC durante requests. Los valores de JSON object+str omiten chunks/join/Response y el ensayo object+str+bytes es controlado. Las proyecciones BF lookup-only1,849/2,179GiB son escenarios, no cotas ni certificación de capacidad30/2GiB. Sin margen demostrado y sin nuevo BF30.

## Decisión concreta y límites

Descartar como optimización **la publicación inmediata usando filas públicas expandidas con materialización independiente por paso**. Conservar este prototipo, sus resultados y fallos como evidencia negativa; no adoptarlo ni lanzar otro grande desde este dictamen. El descarte es recomendación a coordinación, no un cambio ejecutado ni autorización para borrar/revertir originales.

Si coordinación decidiera mantener la idea en un futuro scope, el mínimo conceptual requeriría cambiar la representación interna: almacenar referencias compactas/IDs una sola vez, diferir las filas públicas y preservar sharing de nodos semánticos durante toda la validación. Memo global de cada paso sin límites retendría nuevamente todas las realizaciones y no constituye solución; reutilizar nodos por ID exige contrato readonly/lifetime y presupuesto conjunto de generación, validación y serialización. Esto son condiciones para una eventual propuesta, no implementación ni alternativa aprobada. El protocolo existente, orden, tipos, validadores y errores/session deben conservarse byte por byte.

No correcciones documentales materiales requeridas en el informe autor: ya declara el resultado adverso y sus límites correctamente. No cambios de producto, C/H, contratos, preview, Git, red ni benchmarks. Sólo checks.json, este informe y append al tracker propio. Global20/22 y viabilidad BF30 permanecen abiertos. after sólo reporta.

Resultados: checks.json (evidencia local: `openspec/changes/archive/2026-10-13-review-sorting-projection-diff-coverage-quality/evidence/numeric-event-canonical-dag-independent-review/checks.json`).
