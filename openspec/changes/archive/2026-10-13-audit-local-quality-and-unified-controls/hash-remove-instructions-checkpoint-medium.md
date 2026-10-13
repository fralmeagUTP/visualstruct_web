# Hash remove MEDIUM checkpoint ready for LOW

Proyecto canónico D:\MisProyectos\Web_VisualEstruct. Asignacióncoordination-hash-remove-instructions-medium-20261003, operaciónhash.remove-instructions-medium, autorización01a0fe61-3104-743a-b032-bcc289ad80cd. beforeexit0/afterfresco en evidencia. Tresfallosbaseline corregidos. CheckpointMEDIUM preparado; remove no se declara funcionalmentecerrado hasta revisiónLOW. Hash permanece4/11finito; create_table,insert,get,contains/11Sorting no reabiertos.

## Corrección concreta

Intérprete dedicado remove_instruction.py y branchremove en facade. Sin cambios a C/H, dominio/adapters, caller/journal o motores cerrados. No cambiosH1/RN/Grafos/thresholds. UI muestra arreglo de punteros y cantidadpendiente sólo para remove.

Frames causales de th_eliminar→th_indice/retorno con TablaHash*mutable/constTablaHash*helper, tipos int/THNodo*,aliasroot ylocales con scope/máscaras. Actual/anterior fuera de alcance antes de declaración/después de retorno; no NULL ficticio. Comparaciones/hashcost y retorno avanzan sólo al ejecutarse. Residuo negativoC0 no normaliza.

Unlink modifica bucket o anterior->siguiente, deja nodo vivo no publicado y cantidadvieja; free retira nodo y marca camposactualesinvalidos/máscara0, actual indeterminado initializedfalse/valueJSONnull/validfalse. Máscara7/campos/identidad previos sólo histórico, jamás lectura de memoria liberada. JSONnull no representa una asignaciónNULL del C. Pointers.actual y memory.freed conservan schema previo de identidad simbólica histórica etiquetada; actual_status explicita no utilizable. Dangling_references vacío describe enlaces alcanzables, no certifica valoractualC trasfree. Cantidad-- escribe después; invariante transitoria verificada cantidad=nodosalcanzables+1 mientraspendiente, sin falsepositivo ni adelantarcontador.

## IDs y evidencia independiente

123IDs únicos =106anteriores +9originalesremove +8nuevos. IDs originales y cuerpos intactos, incluyendo tresrojas ya verdes; sourcehashes protegidos.122pass47.14s en corridaafectada +1guardadicionalpass0.49s disjunto. Tras ajuste finalscope/lifetime:19pass14.64s, subconjunto de123, no suma142. Primeras122corridas120pass2fail y121pass1fail se conservan: schemafreed/identidad/invariante compatibilizados sin modificar tests anteriores. ID-overlap.json/unique-test-ids.json/collection.log/protected-comparison.json.

Mismos6fixtures y23eliminaciones vacío/ausente/repetición/head/middle/tail/cadena4/load4/3/negativos/residuo0/INT_MIN/MAX: resultado, estadofinal, ordenbuckets y cantidadidénticos.436eventos C seleccionados=317baseline+119helper, no119nuevoscasos.17free de nodos/0alloc durantekernel. C17_Generic parámetros mutable/const/int yassertaliasroot reales, cálculos/condiciones/scopes/heap/máscaras/rootcounters porframe en tests freshAPI contraobservaciones retenidas. GuardasNULLtabla/tabla0/destruida/signaturaconservadas delprobeC baseline; APIcap0 adicional3frames sinhelper/free; entradasinválidas sin C. report.json conserva primeraAPIobservaciónMEDIUM, validaciónfinal está en tests/logs frescos; no confundir con toda la memoria/lifetimeC física. Observador no inspecciona/compara pointeractual después de free, sólo nodosvivos/NULLsentinel seguro.

UI seisfixtures23operaciones/436frames/413restauraciones, todas con secuencianativa,highlight,statebefore/after,scopes/arreglo/countpendiente/heap,0redispatch/JS,5secciones,reloadtraceigual. Despuésúltimoajustemask/schema/scope:head97frames/92restauraciones, subconjuntode6, no sumar533. Browser seisreport/artifacts yfocusedfinal. Consolakernel sinprintf/frames[]; caller imprime bool calculado posteriormente.

Sieteprogramas main.c reales distintos C17estricto y Doxygen0 actualC/H+mains.34alloc=34free/0live;34puntosfinito mallocNULLexternalcallerstatus1. Cuatroprogramasreusados porSHAexacto21allocfree/21NULL; tresnuevos13allocfree/13NULL. Nada se cuenta dosveces; secuenciascaller/UI/native solapadas. Error inicialobservador de ruta relativa se corrigió en argumentos, no falloC; nota archivada. SinOOMreal/sanitizadores reales. C/Hbytesdescargados canónicos iguales.

## Recursos, coordinación y límites

Mismas23operacionesparaoverheadfinal: peaktracemalloc4604127bytes, JSONmáximo339052bytes, tiempo instrumentadomax0.630720s. IncluyeFlask/JSON/session/snapshots/journal; noRSS/SLA/rendimientonativo/threshold. Capacidad3/cadenas<=4/int32, Windows/Python3.10.5/GCCptr64/Chromium147. No dominioarbitrario/capacidadenorme/OOM/sessionquota/RSS/ABI32/consolecausalityglobal/UBSan/ASan certificados. Mismoengine sincutoffs nuevos; cierrefinito sólo evidencia seleccionada, no exhaustividad.

PaqueteC1/matrix20261003 leídos yQA documental aceptada segúncoordinador; C1requisitos1/12(11pendientes), ledger121/208(87pendientes) sin nuevoscierres. PropietarioSDD01a0fad1-4046-71ae-990c-a53383e81006; susarchivos/matriz/ledger no editados. Handoff técnico local abajo para integrarlo sinrepetiroráculos. DecisionesRN/Grafos solicitadas pero aún no aprobadas, nada inferido. Global13/22/docs121/208 unchanged. Guía no normativa docs/qa/hash-remove-guide.md yUSERGUIDE actualizados bajo requisitos existentes.

Revisiónautomática rechazó creación de deltaADDED por posiblecontratonuevo; comando no ejecutado/specno creada. Alternativasegura sólo guía/notastécnicas no normativas; no queda solicitud de ampliación pendiente. auto-review-rejection.md conserva motivo.

Preview canónico5051launcher38832HTTP200 actual sinreloader; identidadverificada antesdecadareload/cacheusuario conservada. Reinicioprimeroportdefault5050 corregido a5051 ylogpreservado. No tests/browseractivos alcheckpointsalvopreview. Sincommit/push/merge/despliegue/publicación. SiguienteLOW revisar123IDs/alcancereal/resources y cierrejustificado de remove; hastaentonces7métodospendientesexactos remove,keys,values,items,stats,clear,destroy_table. No comenzarotrobaseline antesdelcierrey nuevainstrucción.
