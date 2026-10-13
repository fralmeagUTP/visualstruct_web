# Diagnóstico Phase8 tamaño/latencia/sesiones LOW

ID: tests/test_phase8_visual_integration.py::test_trace_size_latency_and_session_limits. Diagnóstico solamente, sin ejecutar este ID ni aplicación, C nativo, navegador o campañas. Proyecto canónico D:\MisProyectos\Web_VisualEstruct. Guarda before0; análisis puro de JSON con Job2GiB efectivo y supervisor120s, exit0, 2,516s.

## Fallo demostrado

Log histórico evidence/visible-publish-sorting-followup-oracles-low/unit-terminal.log: 2026-10-07T16:24:04.9213499Z, assert max(item[2] for item in measurements) < 1_000_000; 2111743 < 1000000 falla. El máximo de tiempo <2000ms precede y pasó en esa ejecución, sin timings desglosados. La comprobación de sesión posterior no se alcanzó. El log no atribuye el máximo a una estructura; no identificar retrospectivamente RN sin evidencia.

El test contiene13escenarios/22llamadas. Cronometra execute_scenario completo: servicio, reconstrucción del historial, interpretación Python/traza y dominio. No separa algoritmo de preparación. No ejecuta C nativo ni UI. Detiene timer antes de json.dumps; tamaño es execution_trace expandido serializado UTF8 ensure_ascii=False con separadores predeterminados, no respuesta HTTP completa ni protocolo comprimido. Solo compara configuración SESSION_MAX_HISTORY<=300; no prueba truncado efectivo.

## Estimaciones existentes y límites

JSON guardado de RN10,5,1 (duplicates-final-2-call-12-red_black-insertar-service.json) contiene114pasos y2.119.908bytes con fórmula exacta del test. Esto acredita un escenario actual equivalente por inputs por encima de1MB, no una ejecución nueva del test ni atribución del fallo histórico. Burbuja del parámetro Phase8 original [3,1,2,1], capturada en bubble-consumers-final-traces.json,90pasos y352.489bytes; las otras capturas54/33pasos son fixtures diferentes. Reporte existente de los3consumidores Bubble completos: supervisor2,516s; duplicados con Stack/Sublist/MergeSort/RN: supervisor2,547s (pytest1,52s). Son tiempos de lotes distintos, no latencia aislada ni estimación fiable del agregado13; no sumar ni atribuir tiempo de supervisor a algoritmos. No hay tabla actual de tiempos de los13escenarios, por tanto no se garantiza <2s ni duración exacta del test. Inspección de archivos no reproduce preparación ni reproducción visual.

## Contratos y propuesta mínima

criterion18-sorting-informative-three-layer-decision-low.md retira SLA fijo15s para Sorting, puro y HTTP, sin optimizar algoritmos ni perder instrucciones. Tres capas separadas: algoritmo (C nativo distinto de intérprete), preparación/traza/serialización/reconstrucción y reproducción visual. Esta decisión no autoriza reemplazar2s por15s ni elevar1MB automáticamente, ni retirar presupuestos de otras familias. No se encontró regla2s/1MB en búsqueda puntual de specs vigentes; ello no certifica inexistencia en todo el historial.

openspec/specs/session-state/spec.md exige conservar últimas300entradas y benchmark de reconstrucción con checkpoints300operaciones p95<200ms en entorno de referencia. Este max13escenarios no mide ese benchmark. Mantener requisitos funcionales/fidelidad, límite sesión y guardas de seguridad120s/2GiB.

Propuesta, aún sin implementar: separar el consumidor mixto en comprobaciones funcionales de fidelidad/sesión y un reporte por escenario/capa con tamaño explícito (traza expandida y transporte vigente separados). Sorting: duración informativa, sin algoritmo alterado ni frames omitidos. Para las otras familias conservar presupuesto normativo que corresponda a su capa/entorno. Antes de modificar el umbral1MB, coordinación debe resolver si es requisito del transporte o expectativa histórica incompatible con la traza fiel; si es transporte, medir protocolo actual sin pérdidas, no truncar instrucciones. No elegir nuevo umbral solo para pasar. Truncado de sesiones debe apoyarse en evidencia específica existente o revisión focal posterior, no en la mera configuración. Una futura medición se autoriza por escenario, con límites y reporte; no ejecutar el agregado para descubrir su duración.

No cambios en producto, tests, C/H, umbrales ni algoritmos. Balance conservado:27aceptados,38corregidos pendientesQA,1pendiente (este ID). No aceptación/publicación. Siguiente paso: coordinación decide contrato y alcance mínimo del consumidor; después implementación y revisión independiente acotadas.
