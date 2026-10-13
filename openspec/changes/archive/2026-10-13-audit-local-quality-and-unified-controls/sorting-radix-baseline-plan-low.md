# Radix: baseline LOW autorizado

La instrucción nueva sorting-binsort-consolidated-review-authorized-low.md autoriza preparar e iniciar este baseline después del cierre justificado y comunicado de Binsort. Binsort10/11 ya cerrado; no reabrir ni repetir los diez métodos.

Operación sorting.radix-baseline-low. Alcance: resultado C/API, eventos nativos por sentencia/control de wrapper y counting_por_digito, guardas y ownership seguros, código fuente realmente entregado, UI cinco secciones/fast-step/replay/historial/reload/main/JSON y C17/Doxygen de callers originales. Ocho entradas: un valor, positivos con varios dígitos, negativos repetidos, mezcla fuera4, ceros, n80ceros, extremos int32 y signos alrededor de cero. Todos UI1..80/int32; no corte de fixtures. Helpers/arrays tipados y fidelidad completa no se inventan desde resultados.

C actual usa uint32_t para magnitudes de INT_MIN y recomposición protegida. Confirmar mediante ejecución definida, sin repetir UB histórica. NULL/n0 y fallos de malloc 1/2/dígito se inyectan en observador nativo aislado; nunca OOMglobal. Medir cada arreglo auxiliar vivo e inicializado; no leer malloc sin escribir. Clasificar conteos de escrituras por destino, sin cambiar silenciosamente unidades de métricas aún no documentadas.

Conservar C/H y hashes de diez métodos; no nueva implementación instruccional compleja ni contrato. Regresiones permanentes de hallazgos quedan rojas sinxfail. LOW puede documentar correcciones rutinarias sólo con causa clara, sin alterar método cerrado; de inicio se recoge el baseline original. Preparar revisión MEDIUM delimitada si los fallos lo justifican. No suites globales, push/merge/deploy, ni reinicio preview ajeno.
