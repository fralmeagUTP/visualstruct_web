# Hitos documentales C/H por familia — 2026-10-04

Asignación coordination-documentary-comments-families-low-20261004 / documentation.symbols. Aprobación textual del usuario «Si lo apruebo» conservada en evidence/visible-documentary-comments-families-low/authorization.json: exclusivamente comentarios, no instrucciones, firmas, structs, macros ni comportamiento. Cierres finitos funcionales previos conservados, no repetidos. Runtime/preview/sesiones sin cambios.

## Resultado real

67 contratos revisados y actualizados en 14 C/H: bloque 14 (Pila5/Cola4/auxiliares Prioridad5), bloque 15 Hash y bloque 38 (Heap14/Sorting12/Lista6/Prioridad6). Se verificaron 117 comentarios adjuntos C/H contra el contrato revisado exacto; no se certifica contenido por mera existencia de tags. Se retiraron 38 bloques duplicados obsoletos, conservados en snapshots.

Se documentan precondiciones de objetos vivos/estructuras inicializadas, retornos ante NULL/vacio, salida no escrita al fallar, buffers/disjuncion/ownership, aliases invalidados por free/realloc, contadores y aritmetica de indices representables. No ampliacion a aliases arbitrarios, estructuras corruptas ni indices enormes. Hechos relevantes: reinicializar no libera recursos previos; construir Heap destruye la reserva anterior antes de la nueva, cantidad exige buffer real suficiente; eliminacion Lista usa indice cero; -1 puede ser dato Pila/Cola; Hash mantiene capacidad fija sin rehash.

## Validacion ejecutada en D

- Cada C/H editado conserva todos los tokens no comentario, incluidos literales completos; salida GCC -E -P tokenizada coincide antes/despues. Macros/directivas se comprueban por preprocesado, no eliminando literales.
- C17 -pedantic -Wall -Wextra -Werror: headers editados y las 13 unidades C reales compilan. Objetos -O0 -g0 byte identicos antes/despues, siete editadas y seis dependientes sin editar. Es compilacion real a objetos, no ejecucion de algoritmos.
- CCodeService extrae las mismas firmas, cuerpos e internas lineas C de las 93 funciones de las siete unidades editadas. Prefacios documentales pueden cambiar; no se afirma certificacion browser nueva.
- Doxygen 1.18.0 real: bloques 14/15/38 y conjunto actual 26 C/H, EXTRACT_ALL=NO, EXTRACT_STATIC=YES, WARN_IF_UNDOCUMENTED=YES, WARN_IF_DOC_ERROR=YES, WARN_NO_PARAMDOC=YES: exit0 y cero advertencias. XML por funcion y SHA conservados; cero warnings no sustituye revision semantica.
- 26 GET HTTP C/H: nombres y bytes exactos iguales a docs/tads_C en D. Preview listener4664/parent1744 ejecuta run.py absoluto D; no reinicio/reset.
- 795 archivos protegidos revisados: solo los 14 C/H autorizados difieren. App/static/templates/tests, original ledger y restantes fuentes intactos. No suites funcionales, native reruns ni sanitizadores nuevos.

## Inventario y cierres documentales delimitados

Ledger materializado vigente (evidencia local: `openspec/changes/archive/2026-10-13-audit-local-quality-and-unified-controls/evidence/visible-documentary-comments-families-low/final/documentation-symbol-signoff-ledger-current.json`), derivado de XML completo: 211 funciones /386 declaraciones en13familias. Respecto al histórico208: sólo grafo_sucesores_atomicos, rbt_validar y rbt_validar_altura_negra añadidos; ningún símbolo histórico desaparece.

Categorias derivadas del ledger, no contador manual: 67 contratos de comentarios revisados y ligados a fuente actual; 118 endorsements históricos conservados/revinculados (incluye RN19 y Graph15 con cuerpo/documentacion C y contrato H idénticos); 20 pendientes individuales; 3 contratos históricos Graph sustituidos que requieren revisión individual de fuente actual; 3 símbolos nuevos inventariados con QA finita existente ligada, sin aceptación individual global automática. Quedan26registros sin endorsement individual global vigente bajo esas categorías. Revisión documental de los67 no crea prueba nativa de ramas no ejecutadas.

Graph18 revisados: 15 cuerpos/comentarios preservados; BF/Prim cambiaron cuerpo y comentarios; Dijkstra cambió cuerpo con comentario conservado. Los3se vinculan al contrato/QA aprobado actual y conservan el endorsement antiguo como historia, sin trasladarlo ciegamente. Helper nuevo tiene XML/ownership/fallos atomicos ya documentados; QA finita no sustituye el signoff individual global.

RN19: archivos históricos exactos recuperados; firmas/cuerpos/comentarios C idénticos, contratos H preservados y todos inputs del QA vigente coincidentes. Handoff final documental23:28 sustituye la advertencia antigua de permiso pendiente. Vínculo documental cerrado sin reabrir validador/rotaciones.

Desapilar: contrato actual revisado y comentarios cerrados; informes native-stack-statements.json y downloads-final.json comparten SHA histórico comprobado. Fuente íntegra de aquel SHA no recuperada; el artefacto antiguo de C consultado tiene SHA posterior, no sirve como bytes históricos ni evidencia de destino. Vínculo histórico entre informes cerrado, equivalencia completa de input nativo histórico a fuente actual aún no acreditada.

Heap: el harness nativo tiene rama remove, pero CHECKS estándar no la ejecuta. En corpus acotado no se encontró reporte durable para construir/remove; ausencia en aquel CHECKS es comprobada, inexistencia universal no afirmada. Los modelos Python no sustituyen C; cantidad99/buffer5 no es fixture C válida. Comentarios de ambos callers revisados por código; no inventar prueba de guards/fallo reserva/ausente/ultimo/arriba/abajo.

## Nueve criterios globales: residuales necesarios

|Criterio|Cerrado o recuperado en este hito|Residual real|
|---|---|---|
|11 Oraculo C|Preservacion ejecutable completa de las unidades; Desapilar ligado entre informes historicos|Recuperar bytes/reporte exacto vigente Desapilar; prueba nativa Heap especifica no localizada; restantes huecos por caso, sin repetir cierres|
|12 Seccion2|93 cuerpos/lineas de funciones extraidas preservados|No browser nuevo; correspondencia instruccion/vistas de casos restantes y agregado por criterio|
|13 C/H/Doxygen|26 descargas exactas;13C compilados; XML211/386;67contratos y118endorsements ligados|26registros pendientes de endorsement individual global; no cierre por tags/warnings ni lectura|
|14 Manual/ayudas|Guías Graph previamente corregidas; contratos C/H ahora precisos|Cruzar ayudas/formatos/limites restantes y completar contenido faltante|
|16 Cambios/regresiones|Cambios sólo comentario probados por tokens/preprocesado/objetos y extraccion|Agregar evidencias de cambios aprobados restantes; no reaplicar pruebas historicas por inercia|
|17 Decisiones|Permiso C/H resuelto y persistido; contratos aprobados preservados|Sólo ambiguedades nuevas vigentes/C1 y reconciliacion global; no reconsultar permisos sustituidos|
|18 Gate final|Compilacion/documentacion focal ejecutadas con comandos/SHA|Suite/cobertura/gate final aun pendientes; limitacion ASan/UBSan histórica sin instalar/reprobar|
|19 Entrega|Ledger vivo, snapshots históricos y deltas enlazados|Entrega/agregado global, sin archivar cambio ni consolidar specs por sintaxis|
|22 Raices/dependencias|Funciones públicas/privadas inventariadas realmente, nuevo helper incluido|Clasificar usos/hidden/legacy; utilidades Lista no expuestas no equivalen a función muerta|

Estado global13/22 conservado. Próximo bloque propuesto para coordinación: revisión individual de26registros documentales pendientes y recuperación específica de pruebas/vínculos, antes del agregado final. No implementaciones nuevas ni ampliar200vertices. Los checkpoints anteriores son fotografías conservadas; sus permisos pendientes C/H están sustituidos por la aprobación registrada aquí.
