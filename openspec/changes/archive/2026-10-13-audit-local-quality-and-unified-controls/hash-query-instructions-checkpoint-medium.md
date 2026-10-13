# Hash query instruction MEDIUM checkpoint ready for LOW

Proyecto canónico D:\MisProyectos\Web_VisualEstruct. Asignación coordination-hash-query-instructions-medium-20261003; operación hash.get-contains-instructions-medium. Guard before exit0; after fresco registrado en evidence/visible-hash-query-instructions-medium. MEDIUM delimitado completado; este checkpoint no declara cierre funcional de get/contains. Revisión LOW siguiente antes de ampliar.

## Cambios y contratos

Get ausente ahora HTTP400/successFalse/resultNone según spec existente. Contains ausente conserva false/HTTP200. Intérprete dedicado de consultas reproduce llamadas/scopes th_contiene→th_buscar→th_indice, tipos const TablaHash*/int/int*, alias raíz, locales, retornos y salida inicializada/indeterminada sin leer dummy. Residuo C cero de clave negativa no ejecuta normalización. Caller inicializa output; sólo imprime valor encontrado. Tabla/cadena no mutan y consultas no reservan/liberan.

Journal de llamadas observado separado de historial mutante conserva repeticiones y consultas ausentes; main.c reproduce orden y resultados reales (incluidas consultas antes/después de actualización), recarga conserva caller/traza y reset los elimina. Validaciones públicas rechazadas no aparentan llamada C. Parser vigente acepta texto entero '1'; bool/texto no numérico/fracciones/fuera int32 se rechazan. No expansión H1.

## Evidencia y IDs únicos

106 IDs únicos recopilados en unique-test-ids.json, 106 passed/35.25s (affected106.log): 101 previos +5 nuevos. Los 98 previos de creación/inserción y las tres regresiones baseline mantienen sus IDs. Originales C/H/engine creación-inserción/11Sorting/testfiles preservados, excepto expectativa legacy get ausente200→400 de un mismo ID. Original byte a byte archivado; supersesión exacta y hashes en legacy-query-test-supersession.json/protected-comparison.json. Primera corrida100pass1fallo legacy se conserva en affected101-first.log; no xfail ni relajación de kernel.

24 resultados baseline C/API permanecen iguales; cuatro fixtures vacío/cadena/negativos/extremos int32 comparan cada evento nativo, condiciones, comparaciones/hashcalls, salida/máscara, heap y scopes. Get ausente cambia envoltura HTTP requerida, no resultado C. Sonda C17 adicional verifica firmas y guardas NULLtabla/NULLsalida/tabla0/destruida, salida intacta, residuo cero, extremo; suposiciones incorrectas del observador void/parser corregidas y documentadas, producto sin cambio adicional. No IDs adicionales por sondas.

UI Chromium147 real preview5051 D: 25 consultas en tres fixtures (con repetición),450frames/425restauraciones, cero POST adicional/erroresJS, cinco secciones, panel salida verificado, recarga idéntica. Frames/UI/native son solapados, no conteo agregado. Evidencia browser/report.json y capturas; primer pase conservado.

Cuatro callers HTTP/browser auténticos compilados C17 O2/Wall/Wextra/Wpedantic/Werror:17alloc/17free/0vivos y17puntos finitos mallocNULL externo, cleanup status1, sin OOM/lecturas indeterminadas. Caller HTTP demuestra dos get iguales, get ausente, contains ausente y get10→update20→get20. Doxygen real sobre C/H descargados y cuatro mains: warnings vacíos. C/H bytes canónicos idénticos. Guía suplementaria docs/qa/hash-query-guide.md; no cierre documental global.

## Límites y siguiente paso

Verificación finita Windows/Python3.10.5/GCC int32,puntero64/Chromium147. Journal sin cuota propia: retención arbitraria y truncamiento del historial mutante pueden invalidar su binding; sesiones largas no certificadas. Snapshots de cadenas enormes, RSS/SLA/OOM no certificados. Alias UI simbólicos dentro de operación. Creación/inserción permanecen cerradas sólo en casos registrados; queries usan fixtures sin reabrir bloque. Global13/22 y docs121/208 no cambian; otras9operaciones Hash pendientes hasta revisiónLOW/cierre justificado de estas dos. No cambios RN/Grafos, no commit/push/merge/despliegue. Siguiente: LOW revisar checkpoint/retención limitada y decidir cierre finito con evidencia, sin ampliar antes del informe.
