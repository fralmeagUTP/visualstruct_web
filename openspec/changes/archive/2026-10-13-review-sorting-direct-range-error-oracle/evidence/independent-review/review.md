# Revision independiente: rechazo directo de rango Sorting — 2026-10-07

Veredicto: ACEPTADO focalmente. Un archivo, una funcion, dos IDs; no decision A/B ni cierre Sorting global.

34 hashes congelados coinciden con D:. AST independiente confirma solo test_counting_family_rejects_excessive_range_before_auxiliary_allocation cambiado; todas las demas funciones, incluida shared fast/step con source_code vacio, intactas. ABB/RN26 y PQformato32 bindings tambien verificados intactos, sin reabrir aceptaciones.

Semantica aprobada: C/H fija ORDENAMIENTO_RANGO_MAX=1000000 y Counting comprueba rango/capacidad representable antes de calloc y antes de escribir el arreglo. Binsort delega exactamente a Counting y hereda rechazo. Decision resource-bound conserva cap/rechazo; su corte historico del recorder fue superado y NO se usa para declarar fidelidad completa. Para INT_MIN/INT_MAX rango matematico4294967296, mayor al cap; Python usa aritmetica amplia para ese calculo. No se ejecuta C en plataforma32 ni se afirma seguridad de ese caso de cast.

Oraculo fortalece el test: mensaje completo anclado con rango/cap correctos, codigo range-limit, input y interpreter.values sin cambios, sentinel counting_allocator que registra intento y lanza AssertionError (no SortingExecutionError esperada). El camino actual rechaza antes del allocator; solo MemoryError se transforma en fallo de reserva, por lo que el sentinel no puede disfrazarse de rechazo valido. Texto ASCII actual pertenece al error didactico Python; C devuelve enum sin printf. Cambiar acento esperado no cambia contrato de rechazo ni codigo/error semantico. No debilita el test a ausencia de excepcion.

XML mismos dosIDs counting_sort/binsort: baseline2FAIL, final2PASS, worker exit0/1s con membership Job2GiB antes de imports y supervisor120s. Evidencia guardada revisada, no repetida. No reservas amplias ni pruebas largas/producto/native/browser ejecutadas por QA.

Limites: acredita estos rechazos directos, no faultpath de reserva, fidelidad de todo Sorting, propagacion de error por adapter con fuente vacia ni14casos sourceboundary congelados. No cambia decisiones A/B, SLA, C/H, algoritmos, contratos o E2E. Sin publicacion ni edicion de originales/indice. Before/after propios conservados.
