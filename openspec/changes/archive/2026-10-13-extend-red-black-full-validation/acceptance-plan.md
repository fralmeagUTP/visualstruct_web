# Aceptación propuesta para el único auditor RN

No ejecutada por este autor. Dueño técnico01a0fc18-c146-7460-b83f-47a215e630cf después de checkpoint actual Encolar y asignación/guardas RN específicas. Buscar evidencia previa antes de repetir cierres Insertar/Eliminar; no suite masiva por generar un contrato.

| ID | Fixture/entrada segura | Esperado y evidencia requerida |
|---|---|---|
| RN-V01 | NULL y hoja negra con NULLhijos/padre | C1/backendTrue; cero mutación estructural/alloc/free/output; NIL conceptual negro |
| RN-V02 | Hoja negra INT_MIN y INT_MAX; árboles válidos de varias alturas | True; cotas sin overflow; misma altura negra independiente |
| RN-V03 | Raíz roja; color char distinto r/n; rojo-rojo | False; evento/condición/retorno real, sin reparación |
| RN-V04 | Raíz10 negra/hijo5 negro/otroNULL | False por altura negra; conservar contraejemplo del validador parcial |
| RN-V05 | Raíz10 negra/hijo5rojo con padreNULL | False; no validar la vista reconstruida que corrige padre |
| RN-V06 | Padre raíz vivo noNULL; padrehijo vivo incorrecto | False por identidad, no comparación estructural recursiva |
| RN-V07 | Duplicado en representación; descendiente que cumple padre local pero viola cota ancestral | False; preservar rechazo/no-op de duplicado en operaciones actuales |
| RN-V08 | Autociclo, ciclo interior y reserva compartida, todo objeto vivo | Termina False; ejecución acotada/timebox para detectar no terminación; cleanup externo por reservas únicas. No constructor/serializer/destructor recursivo del árbol corrupto |
| RN-V09 | LL/LR/RR/RL y tío rojo de inserción con fixtures existentes | Invariantes en el estado estable tras cada inserción completa desde árbol válido; mapa a caso3/4/5 y primitivas reales; comparar oráculo independiente, no sólo el nuevo validador |
| RN-V10 | Cuatro situaciones de `arreglarEliminacion` (deleteFixup descriptivo) y ramas espejo seleccionadas por fixtures reales | Preservar propiedades en el estado estable tras cada eliminación completa desde árbol válido; inventario caso→rama→fixture→eventos. No inventar alcanzabilidad ni sumar mismos casos repetidos |
| RN-V11 | C/H HTTP +main real, repetición Validar, reload | Compilación C17 estricto; llamada pública sin auxiliar homónimo; resultado C calculado, caller dueño libera fuera de historial |
| RN-V12 | Traces válidas/invalidantes test-only en vista segura | Fuente/helpers/alias/scopes/cotas/altura/retornos exactos; no mutación/printf del validador; ambasvistas/replay sinPOST; ausencia de ramas omitidas |
| RN-V13 | Integración Insertar/Eliminar/Limpiar/consultas focales | IDs previos conservados; expectativas antiguas del validador parcial supersedidas sólo por contrato aprobado y originales archivados; no debilitar negativos |

Datos anteriores son criterios, no resultados. Fixtures válidos se crean con API real; corrupción estructural sólo en harness/control test-only y sin desreferencias inválidas. Observador/oráculo independiente debe validar cinco reglas/ABB/padres antes de interpretar nuevo rbt_validar como su propia prueba. Vacío y singleton son explícitos; NULL hoja no es reserva NIL. Sanitizers donde realmente disponibles con versiones/flags/ABI/hash; bloqueo de infraestructura se reporta, no sustituye ejecución por C17 ni configuraciónCI.

Por fila: requisito/escenario, fixture, esperado, observado, testID/log, Cfunción/línea/eventos, versiones y hashes. Para memoria: validador0alloc/free ycaller externo balanceado. Para docs: Doxygen de bytes HTTP yrevisión por símbolo/guía, no sólo0warnings. Para aceptación final: affectedchecks yfuentes coherentes; no atribuir nuevos defectos de rotación sin contraejemplo reproducible.

Fuentes: [modelo C/H](../../../../docs/tads_C/tad_rojo_negro.h), [kernel C](../../../../docs/tads_C/tad_rojo_negro.c), [wrapper](../../../../app/domain/hierarchical/tad_wrappers.py), [propuesta previa](../2026-10-13-audit-local-quality-and-unified-controls/red-black-validation-extension-proposal.md), [limitación previa](../2026-10-13-audit-local-quality-and-unified-controls/red-black-validation-limit-decision.md). Las rutas son lectura; el único auditor mantiene sus checkpoints y seguimiento.

## Criterio de ámbito corregido

RN-V09/10 validan estado estable final de operaciones completas; sus frames intermedios muestran rebalanceo real y pueden infringir temporalmente propiedades RN. No exigir todas las propiedades tras rotación aislada. RN-V03..08 devuelven invalidez sin reparar y conservan el fixture recibido. No cambiar algoritmo ni agregar arquitectura para satisfacer estas filas.

## Aceptación explícita RN-IMPL-01, integrada en las trece filas existentes

- RN-V01/V03..08: comparar campos/valores/colores/enlaces/identidades antes/después; para consultas de servicio completadas True oFalse exigir history_nuevo=history_previo+[validar], exactamente una entrada yningún efecto mutante estructural. Direct call C no crea historial de aplicación; fixtures corruptos sólo por transporte RAW/test-only seguro.
- RN-V11: dos solicitudes explícitas iguales conservan dos entradas reales deconsulta ydos llamadas en main; llamada False completada también se registra. Caller calcula resultadosC, no copia texto cacheado. No contar navegación como otra solicitud.
- RN-V12/V13: GET/reload conserva exactamente el registro de operaciones con consultas sin llamar otra vez adapter.execute(validar); avance/retroceso/reinicio noañade entradas/POST ni cambia secuencia mutante. Error deentrada/ejecución conserva history sin consulta aparentemente completada. Comparar contenido estructural, no sólo longitud.

Reutilizar tests dehistoria yRAW existentes antesdecrear casos. Esta lista es aceptación documental pendiente deQA ypruebas porauditor; no ejecutada por esteautor. No exigir un journal separado ni alterar formato/currentbehavior. Conservar originales supersedidos para demostrar cambio deredacción, no cambio funcional.
