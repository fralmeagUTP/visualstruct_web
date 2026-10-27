# Decisión de usuario vigente: máximo15segundos por algoritmo

UTC registrada 2026-10-05T22:33:52.598027+00:00. Fuente: mensaje de coordinación01a0fe61-3104-743a-b032-bcc289ad80cd y transcripción literal preservada; no inferida de una medición ni de la guarda.

Mary por voz: «Lo que sigue bloqueando es BFS: con 30 nodos y 29 aristas está en unos11,73segundos, cuando el máximo permitido es5».
Usuario: «No, Mary, pero mira que yo con esos11segundos no tengo problema, lo puedes dejar así».
Usuario: «Con que no se demore más de... un algoritmo que no se demore más de15segundos, para mí está bien. Listo».
Usuario: «Sí, y en cualquier algoritmo lo».
Usuario: «máximo demora... debe ser15segundos».


Se adopta **duración máxima15s (≤15.0s)**, porque el usuario dijo «máximo» y «no se demore más de15», para cualquier algoritmo ejecutado en el alcance educativo admitido. No restringirlo sólo aBFS; Graph conserva≤30vértices,Sorting conserva su admisión≤80/int32/dominiosvigentes, y no se amplía ni limita silenciosamente otra entrada. Una función auxiliar no registrada conserva su alcance privado, no se crea nueva UI.

Métrica: elapsed monotonic plain del request completo de ejecución, incluyendo replay/reconstrucción necesaria del historial, validación, algoritmo, generación/preparación completa de su traza fiel según protocolo vigente, historial y serialización/materialización de la respuesta. Timer antes del POST y terminado al consumir la respuesta completa; no sólo C/kernel/tracebuild, ni segundos de avanzar manualmente el player. Preparación explícita del fixture fuera del timer como en la pareja30/29 anterior. Sincoverage/tracemalloc/profiler para gateplain. Respuestas paginadas/tapes vigentes preservan TODOS eventos y posibilidad exacta de navegación; no borrar eventos, cambiar codec, memoria, contenido, precisión o liberar antes de tiempo para cumplir latencia. No sumar espera humana entre requests.

Sólo cambia5→15 en presupuesto de algoritmo/request; P95300reconstrucciones<200ms, límites Graph30/legacy/Sorting, cobertura83/85, exactitud/C/estado/ownership/seguridad/semántica permanecen. Specs canónicas aún no se fusionan/archivan: delta activo queda actualizado para QA.

Se cancela la necesidad del segundo prototipoBFS de mapas pedagógicos; no permanece pendiente de respuesta18:44. Ningún prototipoaislado se adopta por este cambio, incluido el que10.493922s ahora queda bajo15; su SHA/fallos/equivalenciafinita y rechazo histórico siguen conservados. Tampoco se reejecuta la pareja.

11.728276199981337s canónico cumple≤15 en la entrada concreta30v/29arcos/unitweights/inicio1. Esto **no acredita todos los algoritmos, formas, estados, historial o tamaños admitidos**, ni convierte enPASS universales los tiempos instrumentados/parciales. Se solicita QA documental18/19 del nuevo contrato y evidencia existente; no cierre global ni nuevascampañas. Sólo si la cobertura finita del nuevo gate requiere una mediciónplain que realmente no existe, informar el escenario exacto antes de cualquier ejecución.

El fallo viejo<5 permanece histórico; la nueva disposición≤15 es derivación documental autorizada de su tiempo bruto, no nuevaejecución ni corrección algorítmica. Scripts/tests históricos de5s quedan intactos en este bloque; sus predicados15s deberán reconciliarse mediante tarea autorizada si se decide ejecutarlos, sin modificar su resultado original para fingirPASS.
