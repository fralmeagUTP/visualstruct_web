# Revisión AVL/expectativas: bloqueo de continuidad

No se emite todavía dictamen funcional ni recomendación de adopción. La guarda propia before termina exit2: Task binding missing or ambiguous: audit.avl-hint-five-expectations-quality.

La identidad de assignment/operation/task coincide con la orden vigente. El problema está en el enlace de tareas: check_session_continuity.py lee entry.tasks del change, que sigue apuntando a tasks.md de la revisión fused anterior. Ese archivo no contiene el task_prefix nuevo. El tracker separado avl-hint-package-review-tasks.md contiene tres filas con el mismo prefijo; redirigir solamente el puntero tampoco solucionaría la unicidad requerida.

Reparo coordinado concreto: registrar una única fila del task vigente en la tabla que lee realmente la guarda, conservando las filas anteriores, o revisar puntero y bindings de todos los bloques para asegurar coincidencia única. Mantener los IDs vigentes; no elegir otro bloque ni tocar evidencias previas. index.json y tasks.md anterior están fuera de las rutas permitidas a este revisor, por eso no los modifico.

Diagnóstico persistido (evidencia local: `openspec/changes/archive/2026-10-13-review-graph-fused-intern-adoption-quality/evidence/avl-hint-five-expectations-independent-qa-low/binding-blocker.json`). No se ejecutaron pytest, C, navegador, benchmark o cobertura; no se alteraron producto994, paquete ni historia. Los42,79% siguen históricos y QA18 no se acredita. Tras el reparo, continuar desde este estado y ejecutar before con los mismos IDs antes de revisar SHA/AST/respuestas/oráculos.
