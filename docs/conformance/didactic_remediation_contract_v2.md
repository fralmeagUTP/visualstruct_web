# Contratos de remediación didáctica v2

Este documento congela las decisiones previas a la implementación del cambio
`remediate-didactic-c-trace-fidelity`. Cuando la aplicación presenta una operación como C, el C
compilable es el contrato semántico y Python/UI deben reproducirlo.

## Decisiones obligatorias

| Área | Contrato v2 | Compatibilidad |
|---|---|---|
| Grafo | Grafo dirigido como primitiva C; el modo no dirigido compone dos arcos. Insertar un arco crea extremos ausentes y actualiza el costo del arco repetido. El peso es `int` en toda capa. BFS/DFS exponen el orden de visita retornado por el C. Dijkstra rechaza el grafo completo si contiene pesos negativos. Prim/Kruskal sólo aceptan el modo no dirigido y distinguen árbol de bosque. | Historias con peso fraccionario se invalidan con `contract_v2_incompatible`; dirección, extremos auto-creados y pesos enteros se reproducen sin pérdida. |
| Hash | Claves `int`, índice euclidiano determinista y capacidad fija, como el TAD C actual. No hay rehash automático en v2. | Historias con claves de texto o cambio automático de capacidad se rechazan con `contract_v2_incompatible`; las demás se reproducen sin cambio. |
| Cola de prioridad | C conserva orden de llegada y `desencolar`/`frente` seleccionan la prioridad numérica menor con desempate estable por llegada. | La historia de operaciones se conserva; el estado visual deja de asumir que el primer nodo enlazado es el prioritario. |
| Pila y cola | `cima`, `frente` y `final` se respaldan por funciones C declaradas y snippets compilables, con error explícito en vacío. | No cambia la forma de la historia; sólo se corrige la fuente mostrada y su traza. |
| Lista enlazada | Toda operación pública debe existir en el TAD C. Se implementarán las operaciones actualmente sólo-Python antes de mantenerlas expuestas. | Las historias existentes se reproducen con las nuevas transcripciones; si una entrada viola precondiciones C se rechaza en el paso exacto. |
| Sublista | Padres repetidos son nodos distintos con identidad lógica; la serialización usa una lista ordenada y no un diccionario indexado por valor. | El formato antiguo se migra cuando no perdió duplicados; si ya es ambiguo se invalida con `contract_v2_incompatible`. |

## Versiones

- Estado canónico: `canonical-state/v2` para grafo, hash y sublista; el resto conserva campos v1 y
  añade metadata causal compatible.
- Traza: `execution-trace/v2`, con `console_events`, identidad lógica y continuidad obligatoria.
- Sesión: `schema_version: 2` sólo al persistir datos bajo contratos v2.

## Política de migración

La lectura de una sesión v1 realiza validación previa y nunca redondea pesos, cambia claves,
fusiona nodos duplicados ni inventa vértices. Si la transformación es unívoca, produce v2 y
registra `migration: v1_to_v2`; si no lo es, descarta únicamente el registro de la estructura
afectada y devuelve un error accionable. Otras estructuras de la misma sesión se preservan.

La implementación de la migración pertenece a las tareas 1.3 y posteriores; este documento fija
el resultado requerido, no modifica todavía `SESSION_RECORD_VERSION`.

## Estado de compatibilidad y cierre

La implementación v2 fue validada el 2026-08-23. Los 29 casos del inventario conservan su
fixture, prueba de caracterización, oráculo corregido y evidencia individual. Las historias v1
incompatibles se rechazan explícitamente; no se convierten claves de texto, pesos fraccionarios
ni sublistas ambiguas de manera silenciosa.

La matriz normativa y ejecutable es `docs/qa/remediation-regression-matrix-v1.json`. El cierre
global está en `docs/qa/remediation-closure-report-v1.json`; la evidencia por caso se encuentra
en `docs/qa/remediation-evidence/<case_id>.json`.
