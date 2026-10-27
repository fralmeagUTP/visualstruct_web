# Trazabilidad del arnés
| Requisito en specs/session-continuity/spec.md | Implementación | Prueba aislada | Evidencia |
|---|---|---|---|
| Recuperación explícita | AGENTS.md; checkpoint identidad/change/operación | wrong_cwd_and_project; unknown_change_and_operation | evidence/verification.md; CLI rejection logs |
| Estado derivado/checkpoint | read_source; checkpoint conteo/manifiestos/relectura | derived_count_and_no_writes; missing_evidence_and_escape; stale_checkpoint_and_identity; changed_source_set; changes_during_second_read_fail | evidence/unit-tests.log; audit-checkpoint.json |
| Reapertura persistente | checkpoint recorded-closed/decision_ref | reopening_requires_persisted_identity_and_reason; unclosed_reopen_is_not_a_bypass | evidence/closed-operation-rejection.log |
| Persistencia/consolidación | AGENTS.md; proposal/design/tasks; reconciliation-decisions.md | OpenSpec strict (estructura); revisión humana del flujo | evidence/openspec-validation.log; consolidation pendiente explícita |

Los nombres de pruebas omiten prefijo test_. Validación estructural no prueba cumplimiento humano ni semántica app. Actualizar bindings cuando cambien títulos de cierre; no otro ledger paralelo. Fuentes de estado/cierres conservan su propietario original.

## Adopción
Requisito Adopción con cambios legítimos → checkpoint directorio activo/context_sources/task_prefix/phase → tests active_change_becomes_archived, task_status_is_derived_not_manual, new_requirement_full_fixture_cycle_and_justified_reopen, new_unregistered_log_does_not_block_valid_checkpoint, appended_registered_log_requires_refresh_not_permanent_block, new_required_evidence_can_be_registered_and_refreshed → evidence/adoption-final/verification.md. Fixtures aislados; no consolidan specs reales.

Identidad de asignación vigente → assignment_source y gate assignment_id/change/operation antes de reapertura; AGENTS cotejo de nuevo prompt → current_assignment_rejects_historical_closed_search_first, old_assignment_or_checkpoint_cannot_replace_new_instruction, missing_assignment_id_does_not_infer_from_checkpoint → evidence/assignment-final/verification.md. No inspección independiente del prompt.
