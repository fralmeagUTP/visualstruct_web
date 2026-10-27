# Evidencia finita Hash caller stdout — 2026-10-27

Trabajo en la copia integrada `visualstruct-syntax-review`, sin publicar, compilar en runtime, commit, push ni modificar C/H. La interrupción de Desktop-FM dejó únicamente scope/proposal/tasks/assignment escritos; tras recuperar conexión se ejecutó la guarda before y se implementó el alcance autorizado.

## Diagnóstico y resultado

El main Hash ya imprimía resultados. Sus modelos de instrucciones terminaban en el retorno del TAD o formatter, con console vacía; el journal conservaba consultas reales pero no sus bytes. Ahora un AST único genera las instrucciones de impresión del main y las ejecuta sobre los valores y buffers reales de esos modelos. La CRT C efectúa las conversiones; no hay formato numérico Python ni stdout derivado de mensajes de dominio.

El prefijo determinista se restaura desde el journal, incluido get ausente HTTP400 según el contrato existente. Cada printf añade un fragmento y snapshot de stdout después del retorno real; el cursor inicial no anticipa salida. Los pasos se identifican como caller/main y no resaltan una línea ajena del TAD. clear/destroy no ganan mensajes. El epílogo state sólo pertenece a la terminación del main independiente.

## Pruebas completadas

`python -m pytest tests/test_hash_caller_stdout.py -q --disable-warnings --maxfail=1`:

**11 passed in 72.81s.**

- Dos cronologías HTTP con 32 operaciones totales: create, insert/update, negativos y extremos int32, get repetido y ausente, contains presente/ausente, keys/values/items, stats con colisiones y precisión distinta float C/double API, remove presente/ausente, clear, destroy y consultas posteriores.
- El main exacto devuelto por la aplicación se compiló con GCC `-std=c17 -Wall -Wextra -Wpedantic -Werror`. stdout nativo coincide exactamente con los bytes del journal más el printf final del epílogo. No se repite ese printf final por operación interactiva.
- Todos los snapshots equivalen al prefijo realmente emitido; eventos printf sólo después del TAD. GET conserva la salida del journal, y las entradas incluyen las consultas repetidas y ausentes.
- Oráculo nativo separado de promociones `%d`, `%.9g`, `%.17g`, `%s`, `%%`, con INT_MIN, float32 promovido y double.
- Rechazo de `%n`, conversión desconocida, argumentos ausentes/sobrantes, overflow int32, NUL en string/formato. Búsqueda ausente con output deliberadamente no inicializado: el AST no lo lee.
- Hashes C/H comprobados antes/después sin cambios.

Smoke de servicio y ruta: create3, insert1/10, get1, get99, contains1, stats y keys imprimen sus bytes correctos. get99 mantiene HTTP400 y `get:99:0\n`; siguientes prefijos y GET contienen esa salida auténtica.

Coordinación informó **Hash UI 1 PASS** y **syntax Hash/Sorting 3 PASS** en la composición integrada con el helper compartido. Las pruebas de navegador pertenecen a `tests/test_hash_sorting_console_dom.py`, mantenido por el agente de presentación; no se atribuyen a este agente.

## Compatibilidad y límites

Windows verificado mediante `msvcrt._snprintf`. UCRT no exporta snprintf como función en este entorno. Unix usa `CDLL(None).snprintf`, sin compiler adicional; no fue ejecutado en Linux en esta sesión. Se verifica el vocabulario finito de formatos y valores usados por Hash; no se afirma equivalencia universal entre CRTs, locales o formatos/exponentes no usados. Los formatos son constantes internas, nunca entrada C del usuario.

Los modelos TAD preexistentes siguen siendo modelos acotados de sentencias; este cambio no certifica universalmente su intérprete ni reabre su auditoría. La validación nueva vincula las proyecciones del listado con celdas/enlaces del heap y comprueba buffers terminados antes de leerlos. Las inyecciones QA que no reproduce el main no generan un stdout que aparente ser reproducible. Sin pruebas generales ni despliegue.

## Archivos de implementación

- Nuevos: `app/services/caller_printf.py`, `hash_caller_program.py`, `hash_caller_stdout.py`.
- Modificados: `app/services/hash_main_service.py`, `hash_structure_service.py`, `hash_journal_service.py`, `app/routes/hash_routes.py`.
- Prueba nueva: `tests/test_hash_caller_stdout.py`.
- `qa/hash-caller-stdout-20261027/` conserva los dos main C17 exactos de los oráculos completados y hashes de C/H.

Nota posterior de coordinación: fronteraCRT tambiénprobada enLinuxlibc encontenedorQAtemporalreadonly/sinred; PASSint32,string,float32/double,%% yformatosrechazados. Véase caller-console-integration-20261027/evidence.md. No equivalevalidaciónuniversalCRT nidespliegue.
