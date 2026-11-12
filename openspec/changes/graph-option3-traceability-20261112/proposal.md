# Opción 3 de Grafos: trazabilidad complementaria

## Por qué
Francisco pide conservar en OpenSpec el requisito de mostrar únicamente la operación seleccionada y sus auxiliares pertinentes, con seguimiento sincronizado, como referencia de interacción Pilas/apilar y Árboles/eliminar. El expediente graph-operation-code-20261111 ya incluye las diez operaciones y una verificación finita; este registro lo complementa, no lo reabre ni reescribe.

## Brechas documentales
- La especificación anterior agrupa diez operaciones en un escenario; faltaba matriz explícita operación→entrada C→evidencia.
- Los estados published=false/deployed=false describen el momento de QA; la publicación posterior tiene expediente separado. No deben interpretarse como estado actual ni corregirse retroactivamente.
- Conviene separar cierre de llamadas estático, instrucciones ejecutadas y limpieza del resultado; no son la misma selección.
- La referencia Pilas/Árboles es un criterio de UX, no evidencia de una comparación automatizada de esos módulos.
- No constaba en el registro inicial una distinción explícita entre evidencia de graph-scope y cambios posteriores de MST/consola.

## Qué
Documentar requisitos precisos, diseño preservado, matriz y límites. No cambiar runtime, pruebas, C/H, semántica de memoria, interpretación ni algoritmos. No consolidar todavía deltas en specs globales ni archivar por mera documentación.
