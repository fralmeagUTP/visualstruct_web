# Revision independiente — 2026-10-07

Veredicto: RECHAZADO como demostracion suficiente de frames parciales observados. No publicar este lote hasta corregir y revisar el binding nuevo.

21 entradas SHA-256 coinciden. XML guardado: 21 PASS (16 controles puros y 5 HTTP pequenos: create_graph, insert_vertex, exists_vertex, run_bfs, run_dijkstra). Otros 14 casos HTTP no ejecutados aqui. No se repitieron pruebas HTTP/native/browser. Los checks de decode, continuidad, source y estado final son mejoras validas; False explicito sigue rechazado.

Error material: assert_observed_graph_frame acepta holds=None a partir de una etiqueta phase no vacia y contenedores de memoria con IDs unicos/disjuntos. No acredita que instruction_event sea un evento C observado ni su correspondencia con las memorias. counterexample.json conserva una fixture del propio autor modificada solo con phase="fabricated-with-no-C-event" y memorias vacias (graph={}, frames=[], heap_nodes=[], retired_objects=[]). El oraculo la acepta, aunque falta toda evidencia causal C. Ejecutado solamente el helper puro mediante stdlib, sin importar producto ni ejecutar suites. El contraejemplo demuestra ausencia de prueba, no declara invalido todo estado parcial o una raiz transitoria tras free.

Cambios requeridos: establecer y verificar el contrato real de observation/evento/memorias, incluyendo correspondencia con el evento del step, su procedencia y los campos estructurales aplicables por fase. Agregar controles negativos para evento inventado, memoria sin campos obligatorios y desacoplamiento evento/memoria; preservar estados transitorios legitimos y no convertir None en True. Volver a vincular los archivos y aportar evidencia focal. No infiero contratos RN/Grafos nuevos ni prescribo rechazo indiscriminado de punteros transitorios.

El oraculo final es estructural, no certifica por si mismo rango numeric C ni toda la causalidad del algoritmo. Los 21 PASS actuales no corrigen esta insuficiencia. No cerrar 59 causas, E2E, Sorting ni matriz global.
