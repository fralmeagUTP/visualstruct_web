# Progreso derivado por metodos de Ordenamientos

Informe de fuentes existentes; no contador operacional ni tarea global nueva. Cierres finitos leidos del catalogo/continuity/source-marker y evidencia, sin ejecutar nuevamente sus casos. Global13/22 y ledger121/208 permanecen.

| Metodo | Estado por instruccion | Fuente |
|---|---|---|
| Intercambio directo | cierre solo casos registrados | openspec/changes/audit-local-quality-and-unified-controls/evidence/visible-sorting-intercambio-instructions/README.md |
| Seleccion directa | cierre solo casos registrados | openspec/changes/audit-local-quality-and-unified-controls/evidence/visible-sorting-seleccion-instructions/README.md |
| Insercion directa | cierre solo casos registrados | openspec/changes/audit-local-quality-and-unified-controls/evidence/visible-sorting-insercion-instructions/README.md |
| Burbuja mejorada | cierre solo casos registrados | openspec/changes/audit-local-quality-and-unified-controls/evidence/visible-sorting-burbuja-instructions/README.md |
| Shell sort | cierre solo casos registrados | openspec/changes/audit-local-quality-and-unified-controls/evidence/visible-sorting-shell-instructions/README.md |
| Quick sort | cierre solo casos registrados | openspec/changes/audit-local-quality-and-unified-controls/evidence/visible-sorting-quicksort-instructions/README.md |
| Merge sort | cierre solo casos registrados | evidence/visible-sorting-mergesort-instructions/README.md |
| Heap sort | cierre solo casos registrados | evidence/visible-sorting-heapsort-instructions/README.md |
| Counting sort | cierre ampliado acotado: UI1..80/int32/size_t64, éxito k<=1000000 y errores registrados; equivalencia sparse revisada y evidencia vigente | sorting-counting-consolidated-closure-decision.md |
| Binsort | cierre ampliado acotado: UI1..80/int32/size_t64, éxito k<=1000000 y errores registrados; criterio estructural/evidencia vigente | sorting-binsort-consolidated-closure-decision.md |
| Radix sort | baseline LOW recogido;39IDs18pass21fallos; instrucción/helper/memoria/replay abiertos | sorting-radix-baseline-checkpoint-low.md |

Ocho cierres finitos previos preservados: Intercambio, Seleccion, Insercion, Burbuja mejorada, Shell, Quick sort, Merge sort, Heap sort. Counting añade el noveno cierre bajo dominio/criterio/límites explícitos de la decisión consolidada; Binsort y Radix sort pendientes. La tabla no suma restauraciones, casos solapados ni callers a tareas globales.

## Checkpoint Counting ampliado 2026-10-02T18:12:42.165328+00:00

Núcleo disperso aislado: 16IDs propios pasan, contraste416eventos congelados y cap nativo size_t64 con siete muestras. NO integrado en API/player: cinco regresiones API rojas y corte actual conservado. Counting PARCIAL. Diseño antes de ampliar contrato compartido: sorting-counting-expanded-integration-checkpoint.md; evidencia visible-sorting-counting-expanded-fidelity. No nuevos cierres ni suma de IDs solapados a global/doc ledger.

## Integración Counting 2026-10-02T18:50:00.685104+00:00

Instrucción nueva de coordinación y35IDs locales/2probes browser; corte4 eliminado yHTTP/UI paginados activos. El checkpoint anterior sin integración es fotografía histórica sustituida por esta evidencia. Método sigue parcial; no ocho cierres reabiertos ni avance global/ledger. Siguiente alcance requiere coordinación para oráculos fuera4/fault, no elegir otro método desde historia.

## Counting LOW nativo/fault 2026-10-02T19:20:09.228222+00:00

Ocho casos/5504eventosC completos, dosdigests streamingcap,sietefallosnativos+retry ycorreccionesHTTP/browser verificadas.46IDs únicos en logs38/11consolapamiento3, no suma a cobertura/tarea global. Brecha de traza deerror documentada: sorting-counting-error-instruction-gap-low.md. Counting siguePARCIAL; los pendientes outside4/fault delcheckpoint anterior son historia sustituida por nuevaevidencia. Ocho cierresprevios/C/H intactos;0nuevoscierres.

## Counting errores MEDIUM 2026-10-02T19:57:09.908110+00:00

59IDs únicos (46previos+13nuevos), cuatrooráculos450eventos de errores, ochooráculos5504eventos exitosos preservados ydosdigests máximos idénticos. UI150restauraciones/3probes: doserroresrangoreales yunaTESTINGfixtureNULLrotulada; noOOMreal. C/H/ocho cierres/runtime preservados. Brecha didáctica deerror delcheckpoint LOW resuelta para causas/casos registrados; dominio ampliado continúaPARCIAL a revisión de coordinación. No repetición de cierres, tareasglobales/ledger sin aumento. MEDIUM terminado; siguienteacciónLOW según sorting-counting-error-instructions-checkpoint.md.

## Counting revisión consolidada LOW 2026-10-02T20:08:31.886208+00:00

Counting9/11 bajo sorting-counting-consolidated-closure-decision.md: cutoff eliminado, representación lossless revisada,59IDs vigentes, oráculos/fallos/UI/callers pertinentes verificados.3IDs acotados adicionales sonrepetición de subconjunto, no62. Sin hueco funcional abierto detectado en dominio UIint32/size_t64;32bit/OOMglobal/exhaustividad no certificados. EstadoPARCIAL de checkpoints previos superado por esta revisión, conservando historia. Binsort LOW preparado en sorting-binsort-baseline-plan-low.md, sin ejecutar. Global/ledger sin cambio.

## Binsort baseline LOW 2026-10-02T20:48:10.676126+00:00

Resultados/métricas8/8;4341eventoscompuestos vs238frames.32IDs19pass13fallos abiertos.3UI78restauraciones/0POSTextra/0JSerrors y4callersC17Doxygen/6calls6alloc/free0vivos. Cnativebounds seguro/int32size_t64; APImaxsentineldiagnósticonoOOM. LOWmetrics/rawconsole/faststep/modelError/metadatosfixed, no instruccióncompleja. PlanMEDIUMsorting-binsort-instruction-review-plan.md. Baselinecompleto,métodopendiente;9/11sin aumento, global/ledger igual.


## Binsort MEDIUM checkpoint before method closure

2026-10-02T21:21:22.522603+00:00 — coordination-sorting-binsort-medium-20261002 / sorting.binsort-instructions.13fallos resueltos,60IDs únicos vigentes(32originales intactos+28nuevos),4341eventos éxito y462ERROR C/API iguales. TapeBin wrapperCount sincutoff, parámetros suspendidos/alias/source/scopes/free, /step/pages/reload/export sinredispatch. UI5probes+2errores adicionales/0POSTextra/JSerrors/5secciones;80/k1m conserva3000912pasos en1231records/12744946bytescontenedores/DOM64.4callers exactosreusados+1nuevo C17/Doxygen0/1alloc1free0vivos. C/H/nueve cierres/commonruntime/originaltestSHA intactos. Evidencia evidence/visible-sorting-binsort-instructions ysorting-binsort-instructions-checkpoint-medium.md. Binsort NOcerrado: revisiónLOWpendiente antes de10/11;Radixnoiniciado. Límites int32/size_t64/noexhaustividad/fingerprints/noOOMreal/fixtureNULLrotulada/memoriaretendida noRSS. Global13/22,ledger121/208 sin incremento. Previewpropio5051actualizado;afterinforma,sinpush/merge/deploy.


## Binsort expanded-domain verified closure with explicit limits

2026-10-02T21:32:01.509197+00:00 — Consolidación LOW autorizada: coordination-sorting-binsort-consolidated-review-low-20261002 / sorting.binsort-expanded-fidelity. Décimo de once bajo UI1..80/int32/size_t64, éxito k<=1m y errores registrados, por equivalencia estructural sobre Counting byteidéntico más oráculos y pruebas.60IDs vigentes,3probes sensibles3pass1.30s son subconjunto. C/H/nueve cierres/runtimes intactos; preview5051 actual verificado sin reinicio.4341eventos éxito y462errores, UI/callers/recursos se reutilizan, no nuevas pruebas Count. Límites, plataformas y simulaciones: sorting-binsort-consolidated-closure-decision.md y evidence/visible-sorting-binsort-consolidated-review-low. Sin brecha funcional abierta detectada en este alcance ni exhaustividad; fingerprints/NULLsimulado/noOOM/RSS/ABI32bit explícitos.10/11 no cierra auditoría global13/22/ledger121/208. Siguiente: Radixbaseline LOW autorizado con nueva asignación yguarda; sinpush/merge/deploy.


## Radix LOW baseline collected; instruction fidelity pending

2026-10-02T21:55:30.309953+00:00 — coordination-sorting-radix-baseline-low-20261002 / sorting.radix-baseline-low. OchoresultadosC/API iguales;3748eventos estructurales/seleccionados frente72agregados.39IDs18pass21fallos sinxfail: controles/helper/lifecycle/línea/comparaciones/modelMemoryError500/stepredispatch/rawconsole. UI3casos78restauraciones0POSTextra/JSerrors5secciones;historial/main/JSON conservados,faststep/reload pierden traza.3originales callersC17/Doxygen0/6calls60alloc60free0vivos. Mismos8éxitos+6faultprobes sobreC/Horiginales, no doblecoverage;NULLmallocsimulado,int32size_t64/INT_MINdefinido,noOOM/UB. Código/C_H/diez cierres SHAidénticos ypreview16304/24752sinrestart. Baselinecompleto, Radixinstrabierto;10/11/global13/22/ledger121/208igual. Evidencia evidence/visible-sorting-radix-baseline-low ysorting-radix-baseline-checkpoint-low.md. MEDIUMplan preparado sin implementar, requiere nueva asignación. Sinpush/merge/deploy.
