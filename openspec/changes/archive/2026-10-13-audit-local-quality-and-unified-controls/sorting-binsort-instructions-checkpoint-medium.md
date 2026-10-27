# Binsort: checkpoint MEDIUM previo al cierre

Los 13 fallos reales del baseline están corregidos en D:\MisProyectos\Web_VisualEstruct. Binsort sigue pendiente de revisión y cierre LOW; los nueve cierres anteriores, el global 13/22 y el ledger 121/208 se conservan.

Asignación: coordination-sorting-binsort-medium-20261002. Operación: sorting.binsort-instructions. Autorización y plan permanecen en este change. Implementé el wrapper por instrucción sobre el núcleo disperso Counting existente, con parámetros suspendidos, alias del mismo arreglo y retiro de scopes en los retornos reales. /step, páginas, recarga y exportación consultan la ejecución guardada sin redispatch. Los errores conservan el estado aceptado, historial y main.

Hay 60 IDs únicos verificados: 32 originales intactos y 28 nuevos, derivados de la unión de logs sin sumar repeticiones. Coinciden completos 4.341 eventos de ocho éxitos y 462 de cuatro errores con C. La UI verifica casos pequeños completos, fronteras del caso grande, errores y simulación NULL rotulada, sin POST de replay ni errores JavaScript. Mantiene las cinco secciones. El caller grande descargado compila en C17, genera Doxygen sin avisos y registra una reserva, una liberación y cero vivos; cuatro callers anteriores se reutilizan por bytes exactos.

El caso de 80 elementos y rango 1.000.000 conserva 3.000.912 pasos lógicos en 1.231 registros físicos: 12.744.946 bytes de contenedores retenidos, respuesta inicial de 134.997 bytes y hasta 64 cubetas en DOM. No hay cutoff de fixtures. C/H, módulos protegidos, runtimes y tests originales conservan SHA.

Límites: C observado con int32/size_t64; oráculos finitos y muestras UI grandes, sin exhaustividad. Los fingerprints nativos reutilizados pueden colisionar. NULL es QA aislada; no ejecuté UB ni agotamiento real. Los bytes contabilizados no son RSS del proceso. El almacén es efímero, con TTL de 900 segundos y presupuesto compartido de 32 trazas/128 MiB.

Evidencia: evidence/visible-sorting-binsort-instructions/README.md, summary.json, unique-test-IDs.json, protected-after.json, preview-final-identity.json y continuity-after.json. La guarda after sólo informa. El preview propio sigue en loopback:5051. No hay prueba activa ni bloqueo técnico. Siguiente paso: consolidación LOW de este checkpoint antes de cerrar Binsort; Radix requiere la siguiente instrucción. No hubo push, merge, commit ni despliegue.
