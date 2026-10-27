# Revisión independiente: consumidores legacy de memoria Apilar

Dictamen: RECHAZO focal por dos huecos relacionados en la frontera de entrada del oráculo. Fecha2026-10-07; proyecto D:\MisProyectos\Web_VisualEstruct; change review-stack-push-legacy-memory-consumers; operación qa.stack-push-legacy-memory-consumers; assignment coordination-stack-push-legacy-memory-consumers-independent-qa-low-20261007; task stack-push-legacy-memory-consumers-independent-qa.

## Defectos concretos y cambio requerido

1. assert_empty_stack_push_memory no valida el primer state_snapshot. Cambiarlo por una pila con items=[{value:123}],size1,emptyFalse es aceptado, mientras entry.state_after ya queda vacío. Eso admite desaparición de un nodo sin store, publicación, pop ni free, en un fixture expresamente vacío→9.
2. El helper comprueba tipo/valor de valor, pero no initialized/valid; tampoco esos flags y scope de todos los parámetros. Marcar valor initialized=False,valid=False en el frame de entrada y sincronizar las tres representaciones variables/push_memory/scopes es aceptado. En C el parámetro int valor está inicializado al entrar y después se lee en aux->nro=valor.

Ambas admisiones se reprodujeron sólo con el fixture escrito a mano y helper stdlib, sin importar producto, ejecutar algoritmos o suites. El fixture sano pasa. Véase contraejemplos (evidencia local: `openspec/changes/archive/2026-10-13-review-stack-push-legacy-memory-consumers/evidence/independent-review/isolated-boundary-counterexamples.json`). No son defectos demostrados del producto actual, sino expectativas del consumidor capaces de ocultar esos errores.

Corrección imprescindible dentro del mismo helper: exigir el estado inicial vacío conocido y continuidad también desde ese estado hacia entry; exigir tipo, valor, scope, initialized=True y valid=True de p y valor durante su alcance C, además del caller. Añadir negativos coordinados para los dos casos reproducidos, manteniendo el positivo existente. No cambiar producto/C, reabrir stack.apilar.instructions ni ejecutar campañas cerradas.

## Comprobaciones satisfactorias

El contrato C y cierre finito respaldan la sustitución de state_after.temporaries por pedagogy.push_memory. El helper distingue allocator_enter, allocator_success_return y aux_allocated sobre la misma línea malloc; conserva identidad temporal, campo nro inválido antes de store, máscaras0→1→3, sgte NULL válido después del store, publicación sólo en*p=aux, alias aux vivo hasta retorno y retiro de callee. No fabrica printf/free ni convierte metadata final del motor en prueba de esas escrituras. Las expectativas antiguas de allocated/value/next se reemplazan por comprobaciones físicas más precisas; STACK-002.json histórico y su assert failed se conservan.

Los41inputs congelados coinciden. Sólo dos funciones históricas y sus imports cambian, más helper/controles nuevos; las otras funciones AST permanecen. Motor stack_push_instruction.py y tad_pila.c son byteidénticos a las copias anteriores. Las respuestas completas antes/después son iguales. Los28inputs del delta jerárquico aceptado también siguen coincidentes; los lotes previos y sus dictámenes no se sobrescriben. Véase preservación/resultados (evidencia local: `openspec/changes/archive/2026-10-13-review-stack-push-legacy-memory-consumers/evidence/independent-review/preservation-results.json`), hashes (evidencia local: `openspec/changes/archive/2026-10-13-review-stack-push-legacy-memory-consumers/evidence/independent-review/hash-check.json`).

XML guardados: dos consumidores2FAIL antes; después19IDs únicosPASS0FAIL =2rutas+17controles puros. No se suman repeticiones ni se recalcula resto66FAIL. Los dieciséis negativos existentes no cubren las falsificaciones de frontera anteriores. No se repitió campaña ni se ejecutó C/browser. La revisión no reabre implementación Apilar cerrada y no certifica Pila/global.

## Continuidad y límites

Se registró únicamente la identidad independiente propuesta y autorizada por el handoff; originales técnicos y evidencia anterior intactos. Guardas propias before/after. Sin publicación, despliegue, commit/push/reintento/ruta alternativa, cambios al producto, campañas globales/E2E o nuevos frentes. No hubo denegación de herramienta durante esta revisión. El pendiente es corregir estos dos checks de entrada y demostrar sus negativos dentro del lote actual.
