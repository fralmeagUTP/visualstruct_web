# Tareas de convergencia
- [x] graph-book-convergence: completar seis etapas y criterios GB01–GB12; no mezclar con checkpoint anterior.
- [x] Etapa1: fijar canon y contrato API, copiar C/H exactos sólo después del gate.
- [x] Etapa2: oráculos nativos y matriz finita independiente, incluido malloc.
- [x] Etapa3: motor restringido y adaptación de integración; errores explícitos.
- [x] Etapa4: trazas fieles y proyección pedagógica con propiedad/memoria.
- [x] Etapa5: main/guías/snippets y compatibilidad/historial explícitos.
- [x] Etapa6: regresiones, revisión independiente, UI5054 y paquete separado.

## Evidencia y pendientes al 2026-10-27 10:21 UTC
- Etapas1–2: `qa_convergence/canonical_manifest.json` y `../qa_independent/ENGINE_CANON_REVIEW.md`; 313 escenarios nativo/motor.
- Etapas3–5 implementadas con QA propia, pendientes de revisión independiente integrada y UI.
- Etapa6: otras12familias34testsPython/25archivosNode PASS; UI5054 y empaquetado aún pendientes.
- Guardas de workflow no equivalen a revisión funcional ni firma humana.

## Revisión técnica independiente — 10:25 UTC
`../qa_independent/INTEGRATION_REVIEW.md`: 19 operaciones en pares normal/paso,
3.788 pasos; 7 grupos HTTP; frontera exacta de captura; 359 llamadas no-grafo sin
discrepancias y 3 pruebas sorting. Proyección de alias retirados: 3 trazas,698pasos,
102referencias históricas comprobadas, sin alterar memoria/eventos/estado reales.
UI aún en curso; el parche de legibilidad de dos nodos no cambia semántica C.

## Cierre finito y empaquetado
UIcerrada10:58UTC. Primera extracción completa55Python/8Node canónicos y
34Python/25Node no-grafo PASS11:03:37UTC; forward/rollback exactos. Se registran
cinco revisiones y se sella el workflow. El artefacto posterior al sello debe
volver a pasar verification.json antes de entrega; no se publica automáticamente.
