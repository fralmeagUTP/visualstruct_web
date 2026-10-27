# Reabrir multiple-input — carrera de continuación, 2026-10-27 12:44 UTC

Al revisar el candidato sellado se identificó un yield de modo normal entre requests. Detener, editar e iniciar otro lote antes de reanudar ese yield podía hacer que la continuación antigua leyera el estado del nuevo lote. La autorización original cubre arreglar y verificar esta carrera de cola frontend, sin ampliar TAD/backend ni publicar.

Se añadió una generación por lote para invalidar continuaciones antiguas; el ajuste local precedió el registro de esta decisión. Se deja explícito, no se presenta el checkpoint anterior como validación del nuevo hash. Reabrir exactamente `multiple-input` para prueba de regresión stop→restart, revisión independiente de nuevo hash y reconstrucción/validación de paquetes. La ayuda congelada no cambia.
