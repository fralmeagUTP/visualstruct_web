# Integración local stdout Hash/Ordenamiento — 2026-10-27

Copia visualstruct-syntax-review, base bfe7ab0284a4735cd5660dcc0c88c5ac05b8a6ac más fixes locales previos conservados. Sin commit/push/despliegue. C/H canónicos26paths sin cambio.

## Diagnóstico antes
Hash y Sorting main sí imprimían; traces no ejecutaban sus instrucciones caller. No era silencio de diseño de esas consultas/ejecuciones. Hash journal separa consultas de mutaciones, por ello usar sólohistory perdía repetidas/ausentes.

## Corrección
Hash: AST único de printf/if/recorrido genera fragmentos C y se ejecuta sobre celdas/buffers del TAD, formatos viaCRT con formatos limitados. Callerframes posteriores a retorno reales, source_rolecaller y sin fingir líneaTAD. Journal almacena bytes auténticos; GET reconstruye sin cachebrowser. El epílogo state del standalone main es sólo salida de terminación del programa, no se repite porconsulta. clear/destroy son void y no reciben mensajes nuevos.
Sorting: VM C existente ejecuta main y cuerpo canónico imprimir_arreglo/arreglo_valido; llamadas de algoritmo consumen efectos ya aceptados/validados, GET no reordena. Cabecera Run ya emitida antesdeTAD vive enprefijo; Estadostring/arreglo noaparecen hasta retorno final. No se alteran eventos/cantidadtapeTAD; eventos caller se añaden comometadatosdeprocedencia. Páginas enriquecidas conservan mismo cursor.
UI usa trace.console_prefix+step.console_stdout y model.console_output, no concatena de nuevo bytesyaacumulados. ConsoleHistory.publish conserva scrollmanual yautofollowalfinal; texto literal.

## Verificado
Hash native11passed72.81s:2cronologías32opsC17strict stdoutjournal+epílogo, INTMIN/MAX, repetidas/ausentes,colisiones,listados,statsfloat/double, formatosCRT y7rechazosincluido%n/ausentenolecturauninitialized. Hash Chromium1passed16.48s: normalesx2,cadacursor,prev/nextsinPOST,scrollmanual/final,cacheclearreload,ausenteHTTP400literalpersistido,reset yerrors[].
Sorting Chromium1passed14.70s:burbuja[2,1]x2,cadacursor,prev/nextsinPOST,scrollmanual/final,cacheclearreload,reset yerrors[]. Native11algosstdoutC17PASS; batería inicial13passed2failed14.65s: endpointtestaleatorio404 yGETstateomitiócampo; revalidaciónpuntualpendientealguardar.
Resaltado trasnuevoscambios3passed5deselected21.94s (Hash/Sorting yantesdespuésmain). No suitesglobales niCIremotoejecutados.

Capturas revisadas: ../syntax-evidence/console-hash-integrated.png y console-sorting-integrated.png. Logs browser locales excluyen distribución de sessionsfixture. Véanse evidencias propias hash-caller-stdout y sorting-caller-stdout para comandos/oráculos.

Linux libc frontera printf verificada en contenedor temporal --rm, sin red/puertos, rootfsreadonly y único archivo montado readonly, imagenlocalexistente sha256:96a0fd24d1d28dd2b2f656bc2be4ad9c65967bfa881c151e4afcdffae0de0724. PASS int32extremos, stringliteral, float32%.9g/double%.17g,%% y formatosrechazados%n/NUL. Contenedor temporal eliminado al salir0; servicio5050 sin modificación. No equivale a despliegue ni prueba completaLinuxdelaapp.

Cierrelocal: Sorting15testsúnicosverificadosporparticiones:13inicialesPASS+2reparadosPASS, sinrepetir11nativos. Mixedvoid/int/randomseed yGETsinreordenarPASS; pagedlast/firstcursor,recarga/trace/console_output,historialinmutable yprovenanceC PASS(1passed14deselected0.60s). Sóloúltimos2fallosinicialesdocumentadosyresueltos, sinreducircontroles. Sumadenuevaspruebas:11Hash+15Sorting+2Chromium+3resaltado=31ejecucionesaprobadasalcancefinito (3resaltadossonrevalidación, no casosnuevosglobales). SinCIglobal/despliegue.
