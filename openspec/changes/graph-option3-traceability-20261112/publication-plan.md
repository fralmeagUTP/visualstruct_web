# Persistencia documental

Este commit publica el expediente aprobado en el PR #8 como cambio exclusivamente documental, descendiente del head 8186a4f4e9b7b5419942bba034f7d9e78dfd958d revalidado. Incluye únicamente seis archivos nuevos bajo openspec/changes/graph-option3-traceability-20261112/: proposal.md, design.md, tasks.md, specs/graph-code/spec.md, evidence/traceability.md y este plan.

No sobrescribe expedientes existentes ni publica índices/asignaciones locales, guards con rutas del ejecutor o evidencia operativa privada. El runtime queda idéntico al head anterior; no requiere redespliegue. La revisión documental no constituye QA nueva de las diez operaciones ni aprobación global de CI.

La publicación usa el head esperado para evitar carreras. El SHA remoto confirmado y las comprobaciones de alcance se conservan en evidencia local posterior al envío, fuera de este commit para evitar una cadena de commits autorreferenciales. Las ejecuciones CI nuevas se observan por separado, sin reruns manuales ni asumir aprobación previa. La comprobación de opción 3 sobre el release final continúa pendiente, como indica tasks.md.
