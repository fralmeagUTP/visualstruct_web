# Revisión independiente de cambios backend — 2026-10-27

Alcance: diff contra `visualstruct_prueba_local/visualstruct_web-main` de
`base_adapter.py`, diez adapters secuenciales/jerárquicos y los servicios
`structure_service`, `hierarchical_structure_service`, `sorting_structure_service`.
No cambios al producto realizados en esta revisión.

## Hallazgos

1. **Integración UI de rechazo pre-C (requiere corrección):**
   `hierarchical.js` alrededor de 3043 considera cualquier objeto `execution_trace`
   una traza ejecutable. Para inserciones AVL/RN/heap difiere el mensaje real hasta
   el fin de la traza. El nuevo rechazo `AdapterInputError` produce correctamente
   `steps: []`, `execution_started: false`, pero la UI muestra «Inserción preparada:
   resultado pendiente…» y nunca alcanza el fin. Reproducido el contrato de respuesta
   en backend y verificada la rama consumidora estáticamente; falta prueba UI.
   Recomendación: tratar `validation.accepted === false`/`execution_started === false`
   antes de cargar/diferir, mostrando el rechazo y conservando estado previo.
   Secuencial ya retorna pronto para este tipo de rechazo.

2. **Compatibilidad de historiales fuera de int32 (riesgo real, sesiones afectadas no comprobadas):**
   En stack y ABB, `_rebuild_adapter` con entradas de valores
   `[10, 2147483648, 20]` devuelve tres entradas en baseline y dos en reparación.
   `_require_c_int` ahora rechaza la entrada histórica y el replay la omite silenciosamente.
   Rechazar NUEVAS operaciones fuera de int32 es coherente con el TAD C; reutilizar
   sesiones creadas con valores que antes admitía Python requiere política explícita
   de migración/rechazo/aviso, no afirmar preservación universal.

## Comprobaciones independientes satisfactorias

- `AdapterInputError` hereda `ValueError`: los catches existentes conservan compatibilidad.
- Extremos −2147483648 y 2147483647 aceptados; fuera de rango, nulos, vacíos,
  booleanos y decimales rechazados por parser C.
- `_require_int` permanece sin límite int32: `2**80` aceptado.
- Generación aleatoria de grafos y ordenamiento con semilla `2**80` funciona.
- Helper restringido a datos `value`, `parent`, `child`, `priority`, no capacidades ni seeds.
- Rechazo pre-C stack/ABB conserva historial válido y estado y no fabrica pasos.
- Selección de algoritmo de ordenamiento dentro del `try` captura el ValueError
  antes no manejado, sin alterar la ruta de selección válida.
- `import_state`/`export_state` no tienen implementaciones concretas en esta copia;
  siguen heredando `NotImplementedError`. No se introdujeron cambios en sus contratos.
  Reconstrucción sin checkpoint probada; no se afirma prueba de importación inexistente.

Límite: revisión de los cambios enumerados, no certificación global de la app ni
prueba de todas las sesiones históricas. Hallazgos remitidos al lead antes de este informe.

## Corrección posterior autorizada del hallazgo 1

Se añadió rechazo temprano en `executeOperationAndLoadTrace` antes de actualizar
el código, diferir resultados o cargar una traza. Muestra el error real, pausa sin
cambiar el frame, conserva historial y retorna `null` para que el llamador no
reproduzca la traza anterior. El botón Ejecutar solo reinicia cuando recibió datos
aceptados para reproducción, evitando reiniciar la traza previa tras un rechazo.

Prueba focal `node qa/test_hierarchical_validation.js`: 16/16 pasan (cuatro TADs,
modo rápido/paso a paso, cada uno de los dos marcadores de rechazo). Antes del
cambio, los 16 contratos fallaban. Es prueba de función extraída con dependencias
mock, no sustituye QA browser. Logs `hierarchical-validation-{before,after}.log`
en el directorio padre del proyecto. `node --check` correcto.

Hallazgo 2 continúa como decisión de compatibilidad pendiente del lead.

## Corrección posterior autorizada del hallazgo 2

Resuelto sin migrar ni borrar historiales:

- Los diez adapters vuelven al parser entero histórico; Rojo-Negro conserva su
  restricción original de inserción. `_require_c_int` se aplica en la frontera de
  NUEVAS operaciones de los dos servicios, únicamente a argumentos de datos
  declarados (`value`, `parent`, `child`, `priority`).
- Antes de una nueva operación, un historial con datos fuera de int32 provoca un
  rechazo pre-C explícito; respuesta conserva estado/historial y no contiene pasos.
- GET conserva y muestra datos antiguos, con aviso visible. Las trazas preparadas
  secuenciales incompatibles no se exponen al navegador ni se borran de sesión.
- Restablecer sigue siendo la acción explícita del usuario para volver a simular.
- La frontera adicional `compare_structures` valida sus entradas con el mismo
  parser C antes de ejecutar las copias aisladas; no depende del parser legacy.
- Semillas y capacidades no se restringen con este helper.

Pruebas `qa/test_history_validation.py`: 4/4 unittest. Incluyen nueve estructuras
con el historial `[10,2147483648,20]`, preservación de GET y respuesta fallida,
recuperación tras reset, ocultación no destructiva de traza preparada y 16 casos
para las cuatro comparaciones jerárquicas. Los 11 unittest del auditor de trazas
(incluidos sus 48 escenarios de límites) siguen correctos. Compilación Python PASS.
Logs `history-validation.log` y `history-followup-tests.log` en el directorio padre.
No reinicié ningún servidor. QA integrada en browser permanece a cargo del auditor UI.
