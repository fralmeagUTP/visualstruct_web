# Reapertura autorizada: ocho pruebas de cobertura actual

Operación audit.remaining-coverage-smaller-blocks; tarea remaining-coverage-smaller-blocks; assignment coordination-resume-repair-failures-r2-low-20261011.

Motivo exacto: Cobertura actual de ocho fixtures cp_inicializar/cp_vacia con versiones del comparador y recursos nativos fijadas antes de ejecutar.

Usuario Sentinel_bf49a9a5f57881919a04799164586085,2026-10-11 22:57UTC; coordinación01a0fe61-3104-743a-b032-bcc289ad80cd aporta la autorización explícita: «Autorizo reabrir y ejecutar esas 8 pruebas en un único bloque de máximo 120 segundos y 2 GiB. Si se agota el límite, detener sin reintentar ni ampliar recursos.»

Estos ocho PASS históricos se reabren únicamente para obtener cobertura actual con hashes completos del comparador y sus fixtures/eventos. No revalida universalmente los oráculos nativos; tests leen datos existentes, sin compilación. Mantener resultados anteriores. Una ejecución conjunta, máximo120s y2GiB por proceso y Job. Timeout: terminarJob, conservarparcial, detener sin retry/ampliación. Reservas/230bloqueados/Bellman900/JPEG no autorizados; ningún algoritmo/contrato/C/UI/gate/exclusion/commit/push/despliegue modificado.

IDs exactos:

- `tests/test_priority_queue_five_helpers_instructions_medium.py::test_typed_statement_memory_scope_buffer_matches_native[PQ5I-cp_inicializar-fresh-uninitialized]`
- `tests/test_priority_queue_five_helpers_instructions_medium.py::test_typed_statement_memory_scope_buffer_matches_native[PQ5I-cp_inicializar-NULL]`
- `tests/test_priority_queue_five_helpers_instructions_medium.py::test_typed_statement_memory_scope_buffer_matches_native[PQ5I-cp_inicializar-initialized-empty]`
- `tests/test_priority_queue_five_helpers_instructions_medium.py::test_typed_statement_memory_scope_buffer_matches_native[PQ5I-cp_inicializar-borrowed-reset-private]`
- `tests/test_priority_queue_five_helpers_instructions_medium.py::test_typed_statement_memory_scope_buffer_matches_native[PQ5I-cp_vacia-empty]`
- `tests/test_priority_queue_five_helpers_instructions_medium.py::test_typed_statement_memory_scope_buffer_matches_native[PQ5I-cp_vacia-single]`
- `tests/test_priority_queue_five_helpers_instructions_medium.py::test_typed_statement_memory_scope_buffer_matches_native[PQ5I-cp_vacia-multi]`
- `tests/test_priority_queue_five_helpers_instructions_medium.py::test_typed_statement_memory_scope_buffer_matches_native[PQ5I-cp_vacia-duplicate]`

La operación registrada amplia sigue not-signed-off, no se cambia deID. La guarda solo permite --reopen-reason/--decision-ref si esa operación está recorded-closed; rechaza ambos flags para operación abierta. Esta decisión autentica la excepción exacta de ocho IDs dentro del scope activo y queda vinculada en context_sources. Before/after ordinarios validan el mismo assignment; no se modifica la guarda ni se simula un cierre.
