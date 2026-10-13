# Dictamen independiente: siete reparaciones staged

**Adoptables exactamente tres módulos: historial secuencial, rutas Graph y rutas Hash. Retener el módulo MST hasta un reparo puntual de narración Kruskal.** No se recomienda adoptar el paquete entero sin ese reparo. Destinos y SHA exactos en verification-independent.json (evidencia local: `openspec/changes/archive/2026-10-13-review-graph-fused-intern-adoption-quality/evidence/seven-staged-contract-repairs-independent-qa-low/verification-independent.json`); una recomendación no autoriza integración.

## Integridad y evidencia

Paquete SHA `c336672d660eedfee2b51a538ab3dd83fde3eddb9b64a8dc5bcf6a8ee7f261b0`, 46 datos más manifiesto: CRC, SHA, tamaños y originales canónicos D: verificados. Los 999 inputs actuales permanecen intactos. Cuatro copias staged modifican exactamente siete funciones originales; todos los demás cuerpos originales coinciden por AST. XML/runtime/runner conservados acreditan siete IDs PASS, salida 0 y 12.125 s del supervisor sin timeout. El plugin sustituye sólo módulos de tests, conserva nodeids y vincula sus SHA; no sobrescribe producto. Los fallos previos se preservan como evidencia histórica; sus nombres C: de traceback no se usan como certificación del destino actual. Esta revisión no ejecutó pruebas técnicas.

## Tres historiales: aceptar

`session-state/spec.md`, requisito Historial de operaciones por estructura, exige cronología y distingue registro de mutación. Su tabla enumera precisamente frente, buscar_posiciones e hijos_de. Las reparaciones conservan los resultados 10, [4] y [30,31], comprueban la última entrada operation/payload exacta y estado visual sin mutación, ajustando los contadores posteriores. Conservan estabilidad/prioridades y vaciado final. El cambio no extiende consultas a módulos que no las registran ni convierte las consultas en mutaciones. No certifica por sí solo duplicados, resultados vacíos, aislamiento, truncado o ausencia de redispatch: son límites del caso, no cierres globales.

## Dos ayudas: aceptar con alcance explícito

`help-system/spec.md`, Ayuda por estructura enriquecida con código C, exige métodos explicados con snippet y símbolo. Reemplazar el literal editorial Operaciones soportadas por tarjetas con explicación no vacía y cuatro símbolos representativos mantiene una comprobación observable más pertinente; GET/status y encabezados de módulo permanecen. Los símbolos corresponden a las fuentes C Graph/Hash. El regex comprueba presencia de símbolo seguido de paréntesis en el snippet, **no igualdad completa de firmas C** ni todas las tarjetas; el informe del autor no debe interpretarse como certificado de firma/tipos o cobertura completa de ayuda. La estructura HTML actual se acepta como presentación observada, no requisito universal.

## MST: causalidad útil, un reparo requerido

El uso de `expand_graph_trace` es correcto: es el codec oficial, restaura los objetos del transporte y acepta trazas legacy; no inventa etapas. La fuente C de grafo contiene los helpers Find/Union, la condición de raíces y el reinicio Prim observados.

Kruskal conserva costo y fortalece aristas exactas; comprueba seis decisiones con dos aceptaciones/cuatro rechazos, raíces calculadas independientemente sobre padres vivos tipados, dos entradas Union y dos escrituras de padre, además de retorno y correspondencia línea/fuente. Prim conserva dos componentes, dos aristas y costo 3; demuestra u=-1, ausencia de candidatos no visitados, elección válida y costo[u]=0 sobre memoria viva. Son mejoras frente a enums agregados antiguos, no simples renombrados. No certifican fidelidad C universal ni todas las escrituras/órdenes de eventos.

**Reparo obligatorio antes de adoptar `test_graph_pedagogy_phases_7_9.py`:** la versión anterior verificaba que la narración del rechazo explicaba el ciclo. La nueva conserva el rechazo algorítmico pero elimina toda aserción de narración. El compromiso Explicación causal de Kruskal y Union-Find sigue vigente (`commitment-inventory.md:57` y `reconciliation-detailed.md`, REC-0178); probar raíces no prueba la explicación presentada. Recuperar una comprobación didáctica significativa vinculada a decisiones falsas y raíces iguales en la traza decodificada, sin depender de `pedagogy.case=reject_edge` ni exigir una frase editorial exacta. Si la explicación actual no expresa ese hecho, registrar el defecto; no ocultarlo haciendo pasar el test. No afirmo aquí que el producto carezca de esa explicación: el hallazgo es pérdida de su oráculo de regresión.

Como mejora opcional, Prim puede enlazar índices para exigir selección antes de costo[u]=0 y antes de visitar; Kruskal puede contrastar el valor escrito con las raíces del helper. Mover el import nuevo tras el docstring mantiene el docstring del módulo. Estas mejoras no sustituyen el reparo didáctico obligatorio.

## Límites y siguiente paso

La propuesta finita siguiente no está activada. Su clasificación de consumidores y contratos antes de seleccionar nuevos tests es apropiada; candidatos y líneas faltantes no prueban alcanzabilidad ni esfuerzo ni autorizan campaña. La apertura histórica se conserva: global83 FAIL 14512/24147 (60.10%), Sorting raíz85 FAIL 262/417 (62.83%), BFS5s FAIL observación anterior11.156 s. No se ejecutó cobertura ni benchmark ni se repitieron176IDs. QA18 permanece abierto. Las duraciones de tests no son benchmark de producto.

Coordinación puede autorizar los tres módulos exactos aceptados; el cuarto necesita revisión de su nueva identidad tras el reparo. Sin adopción, cambios de producto/C-H/preview, Git, red o instalación. Guardas propias before/after y seguimiento exclusivo preservan la evidencia anterior.
