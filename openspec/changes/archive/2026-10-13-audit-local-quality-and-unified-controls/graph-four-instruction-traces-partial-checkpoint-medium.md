# Checkpoint parcial de trazas Graph MEDIUM

Asignación vigente: coordination-graph-four-instruction-traces-medium-20261004. Operación abierta graph.bellman-prim-integer-cycle-approved-medium. Proyecto canónico D:\MisProyectos\Web_VisualEstruct. Este checkpoint publica resultados parciales; no cierra algoritmos ni tareas globales.

| Algoritmo | Verificación independiente C17 -O2 | Integración API | Pendiente |
|---|---|---|---|
| Bellman-Ford | 20 fixtures: eventos, condiciones, operandos, escrituras, llamadas, retornos, salida y vida coinciden | Ciclo realmente ejecutado, stdout al printf, resultado fallido sin query exitosa; humo integrado anterior | DOM final, adelante/atrás/seek, recarga, caller y regresión permanente |
| Prim | 17 fixtures C reales coinciden; dirigido API tratado separadamente | Humo integrado y arrays candidatos/alcanzabilidad | DOM final, recarga, caller y regresión permanente |
| Dijkstra | 16 fixtures C reales coinciden; no cambiar kernel protegido | Humo integrado; API negativo rechaza con cero C; destino ausente sigue no-ruta y arrays reflejan retorno C temprano | DOM final, recarga, caller y regresión permanente |
| Kruskal | 17 fixtures C reales coinciden | Humo integrado, union-find y orden bruto | DOM final, recarga, caller y regresión permanente |

Evidencia: native-*/report.json; current-model-preserved-native-recheck.json vuelve a comparar el modelo actual con eventos C preservados sin repetir oráculos. API-rejections-no-C.json registra seis rechazos con cero eventos C e historial intacto. api-first-smoke-resources.json corresponde a la primera integración, anterior a ajustes finales de metadatos, no prueba navegador final.

Corrección observador Kruskal: todos los eventos distintos de preparación de call son iguales antes/después; el observador usa thunks tipados para no separar prefijos de llamadas. C no fija orden de operandos de !=; se contrasta una secuencia válida observada de GCC, no portabilidad universal izquierda-primero.

Límite abierto: las trazas completas con snapshots para tres vértices han medido 9.8–24.2 MB de JSON y 72–170 MB de pico Python antes de los últimos metadatos. No hay prueba general de recursos para 200 vértices ni se ha introducido muestreo/corte/dominio nuevo. Malloc fallido todavía no contrastado en este bloque. No ASan/UBSan disponible según evidencia anterior; no nueva instalación.

La validación funcional previa permanece en graph-integer-cycle-functional-milestone-checkpoint-medium.md y su evidencia inmutable. C/H canónico no modificado por esta fase. BFS/DFS y otros cierres no se repiten. Preview5051 permanece con generación funcional anterior hasta reinicio identificado propio.

Siguiente: pruebas reales de los cuatro players y callers DOM descargables, sólo regresiones afectadas, checkpoint final por algoritmo y guarda after. QA independiente y consolidación LOW posteriores.
