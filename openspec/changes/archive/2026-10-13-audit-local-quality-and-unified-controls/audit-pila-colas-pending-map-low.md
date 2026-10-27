# Pila/Colas: mapa actual tras cierre finito limpiar

Fuente de instrucción nueva: coordinación LOW20261003 autoriza comenzar siguiente baseline no bloqueado. No seleccionar desde checkpoint previo. Cierres sólo por evidencia y decisión fina.

| Familia/operación | Estado recuperado | Siguiente alcance pendiente |
| --- | --- | --- |
| Pila limpiar | Finito cerrado por stack-limpiar-finite-closure-decision-low.md | Fuera del cierre: profundidad/historial arbitrario/ABI/OOM real |
| Pila desapilar | Cierre previo comunicado por coordinación; conservar, no reabrir | No otra corrida por simetría |
| Pila apilar | Observaciones previas parciales8 dentro native-stack-statements19; SHA histórico distinto, no cierre global | Recuperar y contrastar guards/malloc/lifetime/caller/reload que falten antes un nuevo bloque |
| Pila cima | Implementado API, no selector visible actual; no inventar UI | Auditar contrato existente aparte si se asigna |
| Cola encolar/desencolar | FIFO23observaciones y tests previos parciales; guards/enlaces publicados/rearNULL/console | Identificar lagunas sin repetir muestras cerradas; no afirmar certificación total |
| Cola limpiar | test_queue_trace_semantics con2free y estados despuésfree, sin observer exclusivo/types/scopes/lifetime/reload/actualcaller | Próximo baseline LOW fino queue.limpiar-baseline-low |
| Cola frente/final | API/contrato vigente, no listado actual del selector | Recuperar evidencia y caminos readonly sin ampliar UI |
| Prioridad encolar/desencolar/frente/limpiar | test_priority_queue_trace_conformance y log parcial previo; allocator/scan/link estable | Ningún cierre global inferido; mapear pruebas/guards/lifetimes/caller/replay que falten |

Siguiente baseline Cola limpiar: empty/single/multi con duplicados y negativo, repetición y reinserción; C cola_vaciar y rootqstruct vivo. Aux se indetermina trasfree; frente adelanta antesfree; atrás puede señalar objeto vivo desconectado hasta último free y después ser indeterminado hasta q->atras=NULL. No leer/comparar ptr retirado. GuardqNULLnativa aparte, sininventarAPI. Sólo baseline LOW, registrar rojo y checkpoint sincorregirsemántica/MEDIUM.

Global13/22/docs121/208 sincambio; Hash11/Sorting11/otros cierres/RN/Grafos conservados. Pendiente agregado final y C1 documental; no tocarledger ajeno.
