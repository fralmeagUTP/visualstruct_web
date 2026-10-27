# Pila/Colas/Prioridad: pendientes tras cierre finito Cola limpiar

La nueva instrucción LOW autoriza recuperar y comenzar un baseline independiente. No escoger desde checkpoint antiguo ni repetir métodos cerrados.

| Operación | Evidencia y cierre real | Pendiente concreto |
| --- | --- | --- |
| Pila limpiar | Cierre finito stack-limpiar-finite-closure-decision-low.md | Fuera de fixtures: ABI, historia/profundidad arbitraria, OOM real |
| Pila desapilar | Cierre previo comunicado por coordinación, conservado | No reabrir por simetría |
| Pila apilar | 8 observaciones en native-stack-statements19; SHA histórico distinto | Recuperar guards/reserva/publicación/vida/caller/reload faltantes antes bloque fino |
| Pila cima | API implementada, no selector actual | Auditoría readonly aparte sin ampliar UI |
| Cola limpiar | Cierre finito queue-limpiar-finite-closure-decision-low.md | Sólo límites finitos explícitos; no whole Cola |
| Cola encolar/desencolar | FIFO23 observaciones y regresiones parciales previas | Lagunas guards/lifetime/scope/caller/reload aún deben mapearse, sin repetir muestras cerradas |
| Cola frente/final | Contrato/API vigente, no selector actual | Recuperar readonly/error guards/caller; no inventar botón |
| Prioridad encolar | test_priority_queue_trace_conformance reserva/aux/publicación | Falta baseline completo lifetime/scopes/NULL/caller/reload; no certificación por la suite103 vieja |
| Prioridad desencolar/frente | priority-instruction-review:16ops/8seeds,566events,289→291observaciones; after-fix30divs y log8pass1red | Recuperar estado actual de candidatos/aliases/cantidad/condiciones y DOM; histórico no certifica cierre ni reabre casos por su parecido |
| Prioridad limpiar | Test anterior sólo3free/valores despuésfrontstore/finalvacío | Próximo baseline LOW fino cp_vaciar, sin observer previo exclusivo: aux/next scopes/lifetime, rear seNULLANTESúltimofree y cantidad decreceDESPUÉSfree |

La evidencia nativa antigua de Prioridad contiene sólo modes desencolar/frente. Su C SHA2af9... difiere de SHAactual a768...; no atribuir cambio funcional sólo a hash ni reutilizarlo para cp_vaciar. `priority-native-regression-final.log` en directorio inicial termina7fail2pass; after-fix1 posterior8pass1red. No decir que todo Prioridad es verde o sumar corridas. No reruns de esos modes para iniciar limpiar.

Siguiente baseline autorizado: `priority_queue.limpiar-baseline-low`. Recuperar C/H y cuerpos reales, bindings/asignación/before nuevos. Fixtures FIFO físicas empty/single/multi con prioridades heterogéneas/duplicados/negativo, repetir y reinsertar; NULLnative. Cp_vaciar no ordena por prioridad: next conserva enlace vivo, front avanza, rear==aux se evalúa antesfree y seNULLsiúltimo, free invalidaaux, cantidad>0/decrement ocurren despuésfree, aux=next vuelvepuntero válido anteswhile. No leer uninitializedaux/next o retiredptr; cantidad temporal no equivale al largoalcanzable duranteunlink. Guardcantidadfalse conlista inconsistente no inferido ni inventadoAPI.

Baselines no son cierres; registrar rojos y checkpoint antes MEDIUM. C/H/otroscierres/H1/RN/Grafos intactos, no contratos nuevos/publicación. Global13/22/docs121/208 sin incremento. C1 documental y agregado final pendientes.
