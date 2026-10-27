# Propuesta: cumplimiento trazable del flujo de agentes y OpenSpec

## Why
Las reglas actuales obligan a registrar cambios y consolidar specs, pero su cumplimiento depende de invocaciones explícitas. La guarda de continuidad y los cinco contratos de roles ya existen; no hay hooks activos ni CI que exija sus vínculos. Una casilla marcada o un OpenSpec sintácticamente válido no demuestra ejecución, revisión independiente ni consolidación funcional. La evidencia concreta está en el informe archivado de agentes del 14 de octubre.

## What Changes
- Proponer un registro verificable de change/tarea/asignación/requisitos, alcance aprobado y propietario, reutilizando continuidad y role_workflow.
- Exigir evaluación en entrada a trabajo controlado, verificación/cierre y publicación; detectar rutas modificadas sin disposición, evidencia obsoleta, revisión ausente y deltas no consolidados.
- Separar aprobación de propuesta, autorización de implementación, aceptación técnica, archivo local y publicación. Ninguna implica las otras.
- Definir matriz de roles aplicables, excepciones acotadas y despliegue gradual: observación, piloto optativo autorizado y bloqueo en superficies expresamente configuradas.
- Tratar documentación, requisitos retirados/sustituidos, evidencia local no publicable y cambios ya archivados sin inventar PASS ni fixtures.
- Preservar originales C/sesiones y decisiones funcionales vigentes. Automatización de lanzamiento de agentes queda fuera.

## Impact
Nueva capacidad propuesta: agent-spec-workflow. Futuras superficies posibles: scripts existentes de continuidad/roles, comando coordinador de comprobación, tests aislados, documentación operativa y un job CI explícitamente aprobado. Un hook local sería ayuda optativa, no autoridad ni mecanismo universal. Ninguno se crea o activa en esta propuesta.

Los cuatro cambios anteriores permanecen archivados. No se modifica openspec/specs, producto, configuración de roles, CI, hooks, sesiones ni C originales. Validación de esta entrega es documental; no aceptación del control futuro.

## Estado y aprobación
PROPOSED / WAITING_FOR_USER_REVIEW. La entrega documental está autorizada; implementar, activar controles, publicar y lanzar agentes no lo están. Véase design.md para decisiones del usuario, límites y estimaciones. Este cambio no se archiva ni consolida por validación sintáctica.
