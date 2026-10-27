# Auditoría de caminos mínimos

Se revisaron rutas alcanzables, destinos inalcanzables, pesos negativos, ciclo
negativo, límites enteros y reconstrucción de predecesores.

| Área | Resultado |
|---|---|
| Ruta y costo final con pesos no negativos | Aprobado |
| Destino inalcanzable | Aprobado |
| Detección Bellman-Ford de ciclo negativo | Aprobado en estado final |
| Política Dijkstra para pesos negativos | Divergencia (`GRAPH-004`, alta) |
| Tablas temporales y relajaciones visuales | Fallido (`GRAPH-005`, alta) |

La animación actual deriva una ruta final; no interpreta los vectores que el C
modifica durante cada pasada.


## Dijkstra LOW baseline: execution authorized, instruction review OPEN

16independent native endpoint cases compile strictC17;13agree and3disagree:equal-priority order (C1-3-4/API1-2-4),INT_MAXtreatedas infinity inC but reachable inAPI, overflow sum2147483648discardedbyCbutacceptedAPI. Bothnegative-weightcases correctlyreject, includingdisconnectednegativearc; historicalGRAPH-004negativeguard claim is not a current proven defect. Newstrongregression18IDs:13pass/5fail8.50s (3parity+2successfulhistory). No xfail/suppression/assertionweakening.

3actualbrowser cases,6realqueries: repeatedidenticalcalls become1localmaincall and0after2reloads,0extraPOST/pageerrors. All3originalstudentmainsfailstrictC17unusedcamino;2nonemptyresultcallersleak2nodes each. Observationalvariants only:38alloc/34free/4live; originalcompilefail preserved, not counted as passing actualmains. They print precomputedUItext ratherthancomputedpath. Caller/history fixes pending.

1freshHTTP4C/H/doc/helpertestpasses1.62s,Doxygen0,actualprivatehelperbodies strictC17.5individualsourcecontracts reviewed; docs105/208,103pending;all71graphdeclarationmetadata refreshed. C/H executabletokensunchanged; integer infinity/tie/globalnegative/ownership notes andguide limits accurate. Genericinitialtrace presents double dist[1]=0beforeCarrayinit,auxiliarypriority_queue despiteactualminscan;Actualhelperframes/typedarrays/nativeinstructionconformance not verified. Evidence:evidence/visible-graph-dijkstra-baseline-low. Global13/22 andBFS/DFSclosures unchanged. Next boundedMEDIUMscope proposed in graph-dijkstra-instruction-review-plan.md; don't implement numeric/decimal policy redesign silently. No active tests/push/merge/deploy.

The original table is historical: only the new Dijkstra baseline above is current evidence. Bellman-Ford instruction/state claims are not reverified by this Dijkstra assignment.
