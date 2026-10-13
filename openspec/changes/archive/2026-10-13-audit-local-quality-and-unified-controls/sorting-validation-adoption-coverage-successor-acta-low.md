# Adopción real de validación incremental Sorting y cobertura sucesora

Proyecto D:\MisProyectos\Web_VisualEstruct; cambio audit-local-quality-and-unified-controls, operación audit.sorting-validation-adoption-coverage-successor, assignment coordination-sorting-validation-adoption-coverage25-low-20261005. Orden nueva autoriza adoptar exactamente el candidato aceptado sólo después de renovar cobertura/remapear evidencia y cumplir condicionesQA. Primer acto23:46:26UTC, máximo25min, Sol LOW.

## Resultado concreto

Adoptados23:55:36UTC únicamente app/services/trace/engine.py (SHA e11de016ecf23907d25e25bb76fb3f3e40bd4d0622b12f9bbce014d40a2ec7fc) yapp/adapters/sorting_adapter.py (SHA d4af49c0e5cb552bb092fc6c24fa0a95d7a0cdef67ee9809d1c284e34c532cdf), byteporbyteexactos al candidato final aceptado. Backuporiginal2archivos enbackup-before, aceptado enaccepted-candidate ydiff exacto accepted-candidate.diff. Los184módulos restantes deapp idénticos yC/H sin cambios. No adaptaciónextra ni campaña16/535.

APIvalidate_legacy_trace/validate_steps default yretorno concopias independientes ASTidénticos. La única llamadaSortingque descartaba retorno usa la vía readonly. Después deescribir, import fresco delcanónico confirmó SortingAdapter.TraceEngine is app.services.trace.engine.TraceEngine yreadonly efectivo, rutasD reales. Regresiónfocalpostadopción109contrastes PASS y2parespequeñosBurbuja/Heap66/97pasos PASS; SHA desalidacompleta igual alparstaged conbaselineviejo. Son repeticiones de esos mismos contrastes/2entradas, no nuevasfamiliasglobales, no16mediciones ni536/644tests actuales.

## Cobertura renovada antes deadoptar y confirmada después

Raw535aceptado inmutable SHA d9c40419e509906cda869d43e0c25d3692235f57ef0d41a2d277ffc481f803e8. Se mantiene la procedencia/dictamen535 anterior, no se reejecuta como otra suite. Datos de184archivos fuenteidénticos conservan EXACTAMENTE líneas/contextos. Para2sucesores se remapean únicamente líneas textualmenteiguales yconigualownerAST, conservando contextos; se excluyen antiguas líneas ejecutadas engine12(importmodificado) yadapter379(llamadacambiada). Líneas nuevas/cambiadas sólo reciben cobertura ejecutada REAL en elcandidato deSHAaceptado; no se lesatribuyen ejecucionesviejas.

Ejecuciónfocal real bajo coverage7.14.0:109contrastesequivalencia,2pares pequeños y3checksadicionales fallback(profundidad90,ciclo,IDstrsubclass), incluida la elegibilidad/víaerror/roundtrip/defaultAPI/fallback. Sólo2copiascandidatas medidas, fuentesexactas. Rawstaged/contextos/pathmap, mapahistórico yrawunion preservados propios. Harnesstrace code/reference yAST antes/durante/adopción explícitos. La instrumentación decoverage no es medidaperformance; no nuevoC/compilador/browser.

Resultado sucesor: **20140/24226=83.13382316519441%**,4086faltantes,186módulos y4exclusiones originales. Denominador:24164−(60engine+275adapter)+(122engine+275adapter)=24226, delta+62sentencias; numerador19771archivosnoafectados+121engine+248adapter=20140. No se añadieron exclusiones ni redujo conjunto dearchivos. Engine121/122=99.1803%; SortingAdapter248/275=90.1818%.

Raíces críticas deldominio conservadas yverificadas: Sorting399/417=95.6835%,Graph251/260=96.5385%,Hash128/129=99.2248%,Heap142/151=94.0397%, todas>=85. Losdominios fuente/data sonidénticos; no sólo umbralredondeado. GLOBAL83 yroot85 pasan en la unióncompatible derivada. No suitefinal/todointerprete/certificaciónfuncionalglobal; el83.0367488826%/20065/24164 anterior eshistórico.

Antes deadoptar se calculó conreporter dePythonParser usandoexactamente sourcecandidateaceptado paraesos2archivos, rutascanónicas yMISMOconfig/exclusiones/version; demás184conparser real. Sólo evaluación privada de cobertura, ningúnproducto editado para obtenerese resultado. Después deadoptar se produjo nuevojson conCoverage estándar SINreporter modificado leyendoCÓDIGO CANÓNICO REAL; igualdtotales, statements,ejecutadas,faltantes,exclusiones yresumen PORCADA186módulos. Gateprevio yconfirmaciónreal encoverage-pre-adoption-decision.json/canonical-verification.json, reportsstaged/canonical yrawsuccessor-union.coverage.

## Remapeo y límites

Pre-adoption-evidence-remapping.json se guardó ANTESdeescribir los2archivos.109+2pares aceptadosstaged se asocian alSHA exacto deldestino; defaultAPI/copyconsumers/Graph preservados medianteAST+fallback, no reparadosglobalmente. SharedinlineSorting afectaIntercambio,Selección,Inserción,Burbuja,Shell,Quick,Merge,Heap: resultados HTTP/timings delcanónicoanterior sonhistóricos, no tiemposmedidos delsucesor. No reescribirFAIL/ERRORanteriores ni afirmar15PASStrasadoptar.

Counting/Bin/Radix retornan porbranchpaginada intacta; C/kernel/tapes/codec ycamino preservados porAST/sources, las3observaciones previas conservan alcancefinito/fechadepipeline, no son3ejecuciones nuevas ni certificadoHTTPactual. DiagnósticoBurbuja80 se conserva exclusivamente comoadapter22.258s/41646pasos deversiónpreguardas, nunca benchmarkHTTP15deladoptado. Heap80sinprueba grande nueva. BFS,DFS y4Graph no se optimizaron/repararon; métricasprevias fechadas no equivalen aun benchmarkactual.

**No se afirmó MemoryErrorresueltoenHTTP,Heap80completo niHTTP<=15.** No se repitió ninguno de los16. Las3FAILlatencia previas y7sinrespuesta siguencomoobservacioneshistóricas ycriterio18pendiente. Checklistnoeditado;11/12/16 finitos no se reabren.19sóloentregaparcialveraz, no globalclosure/archivo.

No se comprobó versiónruntime/health depreview5051 ni se actuó para reiniciarlo; susimportscargados/reloadautomático no estánverificados por adopción dearchivos. SinGit/commit/push/merge/deploy, cambios UI/C/H/semántica/dominio/codecs. Cobertura/reporte autor requieren QAindependiente del sucesor; no ejecutar el antiguo verify_final_package.py contra2fuentesya sucedidas para certificarcurrentSHA. Paquetes/actas QAanteriores conservados, no corregidosretroactivamente.
