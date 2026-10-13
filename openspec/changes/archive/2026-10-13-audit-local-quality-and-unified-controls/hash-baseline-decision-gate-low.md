# Hash baseline: contract decision still pending

Read-only inspection, not fresh native instruction verification. No application/spec canonical rewrite or new Hash baseline executed.

Observed sources: docs/tads_C/tad_tabla_hash.h declares int key/value, fixed buckets/capacity and no rehash API. app/adapters/hash_table_adapter.py _require_key/_require_value enforce signed-int inputs and metadata capacity_policy=fixed. app/services/hash_structure_service.py describes fixed capacity and isolated comparisons. Archived2026-08-23-enhance-hash-table-pedagogy requires integer/fixed capacity, normalized C modulo and no resize.

Conflicting canonical source: openspec/specs/hash-table/spec.md requires nonempty text (ana/90), text-valued get and resize at0.75. Audit reconciliation.md and add-session-continuity-guard/reconciliation-options.md retain the disagreement. Runtime being identifiable does not authorize choosing its contract as the approved target.

Condition for a new normative baseline is not met until the existing H1/H2/H3 decision is answered. H1: integer/fixed capacity as target, technically verify then reconcile deltas/compatibility. H2: text/rehash redesign under a separate approved change, not a silent audit fix. H3: defer with explicit conflict. No assumption of approval or changed canonical truth.

After decision: record the exact assignment/binding for hash.instructions, use actual HTTP C/H bytes and an independent native observer; cover collision insertion/update, successful/absent queries, signed extrema/negative modulo, front/interior/back unlink/free, clear versus destroy and fixed-capacity stats (or the newly approved redesigned contract). Compare per-instruction identities/scopes/heap/conditions/console in both views/replay; separate previous final-state comparisons from instructional proof. This is a deferred worklist, not a pass claim.


## H1 supera la espera histórica de decisión

H1 aprobado en openspec/changes/archive/2026-10-02-reconcile-hash-integer-fixed-capacity/decision.md y canon openspec/specs/hash-table/spec.md. El bloqueo textual anterior es histórico y no exige nueva reconciliación. Ver audit-next-pending-map-after-radix.md:baselineHashtécnico pendiente, no ejecutado por este mapa.
