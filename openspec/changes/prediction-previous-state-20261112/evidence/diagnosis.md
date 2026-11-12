# Diagnóstico y límites

Baseline anterior (head50c4, Desktop):1FAIL3.87s; pregunta visible después del bucle máximo8, falla antigua clase seq-practice-hidden. DOM confirmó gráfico anterior visible y cinco ayudas displaynone/aria-hidden=true. No se adaptó entonces: faltaba decisión contractual. Nueva decisión recibida2026-11-12 resuelve esa ambigüedad y se registra aparte sin alterar historia.

Head actual exacto4c7244a31128cadea6cba48716f947b7e73db4a6. Fuente sequential.js requestPrediction detiene antes de step; advancePendingPrediction borra índice antes de await step, y evento cursor clearPrediction restaura ayudas. Este examen no prueba por sí solo ausencia de fugas.

Desktop diagnóstico API privada aislada apilar7:10steps;7 link_assigned conserva rootNULL con temporal máscara3;8 root_assigned/assignment cambia rootpush-new, statuslinked y state.items7. Esa selección se usa solo para localizar evento en respuesta pública. El oráculo compara gráfica DOM real navegada por botones Siguiente/Anterior y detalle Paso N y valores independientes rootNULL/temporary frente a rootpush-new/linked/nro7. Pila renderiza memoria HTML (no requiere SVG inexistente), y snapshots también incluyen SVG si existe.

Candidato3 casos: original con8pasos, práctica on/off, respuesta y reset; dos ramas responder/omitir con estados distintos, ausencia de avance/pistas reveladoras, doble activación inmediata, scoreexacto y ceroPOST durante navegación. Sin cambios runtime. Pendiente único bloque Desktop bajo JobObject120s/2GiB agregado, máximo8casos. No prueba universal de todas estructuras/eventos ni repuntuación en replays posteriores; no cierra RBT ni CI global.

## V1 y corrección de preparación V2
Desktop V1 afa938: originalPASS, ramaanswerFAIL en selector slider antes del oráculo; skipnoejecutada por -x.1PASS1FAIL16.09s, wall17.016s, pico319516672bytes, exit1, JobObject0. No evidencia de defecto de contrato. Fuente3417–3421 conserva progreso textual y quita contenedor técnico con slider. V2 usa botones públicos next/prev conservados y progressdetail PasoN, sin acceso player interno, sin incrementar8pasosoriginal ni timeout. La referencia es secuencia de10eventos reales como máximo, publicación8. Autorización adicional de coordinación para una única corrida3 V2, no campaña. SHA c38623a45ef6be62b43d367e5707b9506cff147f3b0342c341ac53eb35a6cf6e; pendiente resultado.

## Resultado final V2
DesktopQA comunicó resultado verificado:3PASS12.76s (original y ramas responder/omitir), wall13.453s, exit0, timeoutfalse, pico agregado319856640bytes bajo JobObject120s/2GiB, JobObject activo0 al terminar. SHA256 c38623a45ef6be62b43d367e5707b9506cff147f3b0342c341ac53eb35a6cf6e; blobGitRAW d25636f507e34690f75ef85b565a6c816beeae64;14458bytesLF. Logs/checkpoint/manifiesto originales retenidos por DesktopQA en su expediente visualstruct-prediction-v2-20261112.

Las dos ramas verificaron gráfica anterior real frente a publicaciónroot, ayudas ocultas, gráfica posterior solo después de decisión, puntuación exacta y dobleactivación inmediata sin repetir avance. El original conserva el bucle8, práctica on/off, respuesta y reinicio de progreso. No hay cambio de runtime. El V1 fallido se conserva como fallo de preparación, no se presenta como PASS.

Límites:3casos acotados no prueban todas las estructuras, autoplay, replay posterior ni toda la suite. No prueba de despliegue/VPS; no publicación ni cierre CI/RBT. Publicación pendiente revisión de coordinación. Índice de continuidad y guardas son propios de copia y se excluyen del manifiesto publicable.
