# Diagnóstico de portabilidad del commit effda1c

Commit remoto actual: effda1c349637d3131e24fb655b486ea4bb1ee10. Este diagnóstico NO implementa enforce-traceable-agent-spec-workflow ni activa sus controles. No se cambian históricos, assertions, gates o configuración activa CI. No hay SHA corregido publicado porque la corrección completa requiere una decisión material de CI descrita abajo.

## Resultados reales
Unit/integration: 34 errores de recolección; 332 deselected; 9.10s; exit2. No llegaron a ejecutarse tests seleccionados. Coverage: los mismos34 y un error adicional de identidad de módulo test_example. C17 y sanitizers: PASS. E2E: consultar evidencia fechada ci-e2e-final.json cuando concluya; un job pendiente no es PASS.

## Causas exactas
19 ModuleNotFoundError por playwright; 2 por PIL (Pillow); 12 FileNotFoundError a11 archivos únicos excluidos de Git; 1 KeyError por CANDIDATE_OUT. Algunas cadenas de importación impiden conocer todos los faltantes diferidos hasta resolver la primera dependencia. Los11 archivos existen en el proyecto canónico: aproximadamente3.67MB en total, con SHA y procedencia en evidence/ci-missing-inputs-provenance.json. No son evidencia inventada. Otros fixtures se leen durante la ejecución y no están cubiertos por esa primera lista.

Coverage recoge también archivo histórico y ejemplo permanente llamados checks/test_example.py; pytest prepend importa ambos como test_example y rechaza identidad. No alterar el ejemplo archivado para resolverlo.

## Listado completo de34 errores

| # | Archivo | Causa inicial |
|---|---|---|
| 1 | `tests/test_allocation_fast_error_supplement.py` | Playwright ausente |
| 2 | `tests/test_allocation_transport_fix.py` | Playwright ausente |
| 3 | `tests/test_bellman_http_consumer_oracle_controls.py` | Fixture/source histórico excluido; ver JSON de procedencia |
| 4 | `tests/test_circular_intermediate_residual_focal.py` | Playwright ausente |
| 5 | `tests/test_controls40_real_flows.py` | Playwright ausente |
| 6 | `tests/test_dynamic_control_supplement.py` | Playwright ausente |
| 7 | `tests/test_dynamic_deferred_window_supplement.py` | Playwright ausente |
| 8 | `tests/test_graph_avl_golden_consumer_oracle_controls.py` | Fixture/source histórico excluido; ver JSON de procedencia |
| 9 | `tests/test_graph_bfs_revision_cache_regression.py` | Fixture/source histórico excluido; ver JSON de procedencia |
| 10 | `tests/test_graph_boundary_equivalence_regression.py` | Fixture/source histórico excluido; ver JSON de procedencia |
| 11 | `tests/test_graph_delete_kruskal_consumer_oracle_controls.py` | Fixture/source histórico excluido; ver JSON de procedencia |
| 12 | `tests/test_graph_main_actual_activation.py` | Playwright ausente |
| 13 | `tests/test_graph_prim_main_symmetry.py` | Playwright ausente |
| 14 | `tests/test_graph_validation_copy_regression.py` | Fixture/source histórico excluido; ver JSON de procedencia |
| 15 | `tests/test_hidden_linked_positional_instruction_e2e.py` | Playwright ausente |
| 16 | `tests/test_hidden_list_terminal_instruction_e2e.py` | Playwright ausente |
| 17 | `tests/test_hidden_list_terminal_instruction_regression.py` | Fixture/source histórico excluido; ver JSON de procedencia |
| 18 | `tests/test_hierarchical_education_restored_focal.py` | Playwright ausente |
| 19 | `tests/test_js_deferred_export_flows.py` | Playwright ausente |
| 20 | `tests/test_linked_intermediate_residual_focal.py` | Playwright ausente |
| 21 | `tests/test_priority_intermediate_residual_focal.py` | Playwright ausente |
| 22 | `tests/test_priority_queue_five_helpers_baseline_low.py` | Fixture/source histórico excluido; ver JSON de procedencia |
| 23 | `tests/test_priority_queue_five_helpers_instructions_medium.py` | Fixture/source histórico excluido; ver JSON de procedencia |
| 24 | `tests/test_qa_three_repairs_candidate.py` | CANDIDATE_OUT obligatorio al importar |
| 25 | `tests/test_queue_intermediate_residual_focal.py` | Playwright ausente |
| 26 | `tests/test_residual97_navigation.py` | Playwright ausente |
| 27 | `tests/test_review122_named_widgets.py` | Pillow ausente |
| 28 | `tests/test_review17_current_presentation.py` | Playwright ausente |
| 29 | `tests/test_rn_console_consumer_oracle_controls.py` | Fixture/source histórico excluido; ver JSON de procedencia |
| 30 | `tests/test_sequential_acceptance_criteria_focal.py` | Playwright ausente |
| 31 | `tests/test_sorting_binsort_baseline_low.py` | Fixture/source histórico excluido; ver JSON de procedencia |
| 32 | `tests/test_sorting_empty_jpeg_regression.py` | Pillow ausente |
| 33 | `tests/test_stack_queue_show_baseline_low.py` | Fixture/source histórico excluido; ver JSON de procedencia |
| 34 | `tests/test_sublist_intermediate_residual_focal.py` | Playwright ausente |

## Corrección mínima propuesta
1. Empaquetar únicamente inputs de prueba necesarios en tests/fixtures, revisados por privacidad y con fuente/SHA/contenido exacto o extracción declarada. Cambiar lectores hacia esas copias; conservar originals y resultados históricos. No añadir indiscriminadamente evidence ni inventar fixture fallback. Revisar dependencias transitivas: builders Graph previos, eventos nativos, nominal allocation responses, Doxygen/XML consumido y snapshots JS.
2. Separar imports de helpers de fixtures navegador; marcar como e2e SOLO las funciones que realmente usan navegador. Mantener funciones API/nativas de módulos mixtos en unit/integration. Lazy imports dentro de fixtures/browser functions para que recolección unitaria no exija Playwright. No importorskip ni saltos nuevos para pasar CI.
3. Proveer Pillow y Playwright como dependencias de testing en el job correcto, con versiones compatibles observadas en el entorno auditado, no una versión arbitraria. Chromium instalado por el mecanismo existente antes de tests navegador. La dependencia Python sola NO instala el browser.
4. Hacer CANDIDATE_OUT optativo mediante fixture tmp_path con configuración de sesión aislada explícita; conservar override cuando se suministre y assertions. No apuntar al cache original ni fijar un directorio del autor. Revisar que este test candidato todavía corresponda al contrato vigente antes de ejecutar; no forzar PASS de asserts históricos.
5. Resolver colisión del ejemplo permanente con nombre módulo único y actualizar enlaces de ese ejemplo (mantener archivo histórico intacto), o usar selección/importación pytest compatible que mantenga ambos juegos de tests. No excluir carpeta histórica de cobertura silenciosamente.
6. Añadir los tests browser publicados a una partición E2E explícita: los jobs actuales ejecutan solo tests/test_ui_playwright_e2e.py y tests/test_playwright_firefox_smoke.py. Clasificarlos e2e y dejarlos fuera de esos targets los desactivaría efectivamente; no es aceptable. Mantener partición Graph/performance y gates actuales. Esto exige modificar .github/workflows/e2e-playwright.yml y posiblemente el empaquetado de dependencias para tests; está fuera de la autorización actual de NO modificar CI activo.
7. Hacer portable el caso JPEG que hoy exige JPEG_FOCAL_URL: un servidor privado de fixture equivalente, sin nuevos skips ni usar preview5051. Recolectar en checkout limpio y publicar un nuevo commit solo cuando el paquete sea coherente. Checks de recolección son distintos de campaña funcional.

## Decisión material necesaria
Autorizar una modificación acotada de la selección E2E/dependencias CI para que ejecute los tests browser existentes recién publicados, sin bajar gates ni implementar el nuevo OpenSpec. Autorizar la ejecución remota resultante de esos casos y un preflight aislado de recolección (120s/2GiB), sin repetir las campañas originales. Alternativa: conservar SHA publicado con CI fallido y mantener VPS pendiente. No se propone desactivar pruebas, saltarlas ni afirmar validación global.

## Límite de esta entrega
Se prepararon11 copias SHA idénticas solo en temporal. Se añadió openspec/continuity/examples/local-task/checks/__init__.py para resolver identidad de colección sin modificar los12tests ni el ejemplo archivado: recolección12/12 exit0 en0.07s, cero tests ejecutados. Cambio local aún no publicado. No se modificaron producto, CI/security, requisitos funcionales o la propuesta de controles. La evidencia JSON enumera errores iniciales reales; no promete que al resolverlos no aparezcan fallos de assertions, plataforma, dependencias nativas o performance. Esos resultados deben verificarse por el flujo autorizado posterior. Originales C/sesiones y recuperación permanecen preservados.

## Correcciones locales preparadas durante diagnóstico
- Identidad de paquete del ejemplo permanente: ambos módulos recogidos,12tests en0.07s; histórico sin cambios.
- tests/test_qa_three_repairs_candidate.py: salida por tmp_path cuando CANDIDATE_OUT no está definido; override explícito conservado; clase de configuración con sesiones en salida privada y header C exacto copiado al directorio del observer. Assertions existentes conservadas. Recolección10tests en0.26s sin variable externa. No se ejecutaron sus casos nativos/API ni campañas.
-11inputs iniciales preparados en temporal con SHA exacto; no añadidos aún a tests/fixtures porque falta resolver el paquete transitorio completo y su enrutamiento CI.
Estas correcciones todavía son locales y NO vuelven verde el SHA publicado. CI/browser sigue sujeto a autorización material; los archivos de producto y configuración activa CI no cambian.

## E2E Chromium general: oráculos heredados
Diagnósticos sanitizados confirman dosfallos de assertion: test_playwright_hierarchical_guided_level_and_mobile_context y test_playwright_hierarchical_comparison_practice_keyboard_and_accessibility. Loslogs no exportan traceback completo por protección de secretos. Fuente de ambos tests exigía count==0 decontroles educativos restaurados por requisito vigente Educación jerárquica en cinco etapas. Cuatro assertions locales pasan a count==1; navegación/teclado/responsive permanecen. Dosnodos recogidos sin ejecutar tests; verificación remota de corrección pendiente. Firefox PASS. Grafos aún pendiente.

## Checkpoint solicitado por coordinación
Estado fechado en evidence/ci-portability-checkpoint.json. Operación sigue abierta: grafos pendiente y autorización material de CI pendiente. No marcar tarea como completada ni inventar SHA corregido/CI verde. Reanudar misma operación registrada; no lanzar ejecución duplicada.
