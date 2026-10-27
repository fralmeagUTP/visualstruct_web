# Prioridad limpiar: baseline LOW iniciado, sin cierre funcional

C/H descargados HTTP200 coinciden byte a byte con D:. Compilación C17 estricta y Doxygen C/H sin advertencias. Nueve llamadas C, 153 eventos, 41 condiciones; ocho llamadas API, 140 frames frente a 148 eventos C correspondientes. Ownership nativo: 8 alloc / 8 free / 0 vivos. NULL sólo nativo, sin leer aux/next no inicializados ni punteros retirados.

Cuatro fixtures: vacío, uno, multi FIFO con duplicados/prioridades heterogéneas/valores negativos y reinserción; dos limpiezas por fixture. Las 32 observaciones cotejadas mantienen valores, cantidad y cardinalidad viva. No atribuir defecto de contador ni objetos omitidos: el nodo desconectado está contado, pero pierde identidad original.

16 IDs permanentes: 9 pasan y 7 fallan sin xfail. Rojos: aux anticipado en declaración, next sin alcance/tipo, alias next ausente, nodo desconectado renombrado aux, puntero liberado mostrado utilizable sin máscara/historia, tipo struct Nodo en variables en lugar CPNodo, ocho retornos void omitidos con scope todavía activo. Rear se NULL antes del último free; no intervalo rear inválido como Cola.

Evidencia anterior recuperada, no repetida: priority-instruction-review sólo desencolar/frente, 16 operaciones / 566 eventos, 289→291 observaciones. SHA C antiguo distinto, no oracle cp_vaciar. Log inicial 7 fail/2 pass; posterior after-fix1 8 pass/1 fail; 30 divergencias nativas en after-fix. La suite103 y UI autoconsistente no certifican Prioridad.

Pendiente LOW: navegador ambas vistas ida/vuelta, recarga/historial, main DOM real C17/Doxygen/ownership y fallos simulados, recursos instrumentados. Los tamaños del JSON guardado no son peak/RSS/latencia. No cierre instruccional, no MEDIUM ni cambios de producto, C/H o contratos. Casos inconsistentes de cantidad, ABI, profundidad arbitraria y OOM real fuera de esta evidencia. Cierres previos se conservan; global13/22/docs121/208 no incrementado.

Evidencia: `evidence/visible-priority-queue-limpiar-baseline-low/summary.json`, report.json, native-report.json, regressions.log y protected-check.json.
