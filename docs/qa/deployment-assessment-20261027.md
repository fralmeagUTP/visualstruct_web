# Dictamen acotado para prueba del usuario en VPS

Candidato remoto observado: `9ad887b2d52db64e198767086fde25a9bfcc3e91`, PR 3 en borrador. No se fusiona main ni se ejecuta un despliegue desde esta tarea.

La entrega es `visualstruct-scroll-codigo-app.zip`, SHA256 `004d35d9a06dcce619a6ff05f24eac6165ec5dd97e79a9e6b79f60567573307b`. Una comparación de 273 archivos entre la entrega y ese commit encontró iguales los contenidos de app, static y C/H, admitiendo exclusivamente CRLF/LF. Sólo difieren `templates/help/manual.html` y `templates/help/_technical_notes.html`, por referencias documentales recuperadas. Los 26 C/H también se comprobaron por bytes exactos.

El Docker local de la entrega sigue healthy y `/healthz` responde ok. Hay evidencia HTTP de páginas, inserción real de vértice y contrato graph-book/v1, y cinco pruebas del lector C. Eso no representa una prueba visual del contenedor local. Los E2E de software se ejecutan en servidores de prueba aislados.

## Dos sospechas de runtime reproducidas y clasificadas

`tests/test_deployment_graph_contracts.py`: **2 passed, 20.43 s**.

- BFS devuelve [1,2,3]. Las únicas funciones vacías corresponden a caller_prepare, caller_receipt y api_publication: C_executed=false, ninguna línea C y rol caller/application. Las instrucciones C sí conservan función y línea exacta. Exigir función C en todos los pasos era una expectativa anterior al contrato actual.
- Bellman-Ford sobre 1→2(1), 2→3(-3), 3→1(1) devuelve HTTP400, GRAFO_CICLO_NEGATIVO y NULL. Conserva todos los datos del grafo, incluidas marcas e identidades. Registra una llamada fallida real en el historial y publica su diagnóstico. Sólo cambian last_operation/last_result; no se reprodujo pérdida de atomicidad. La memoria temporal se libera, no quedan frames y las identidades vivas vuelven al conjunto inicial.

## Validación y límites

C17 y ASan/UBSan pasaron en [40530123995](https://github.com/fralmeagUTP/visualstruct_web/actions/runs/40530123995). Regresiones de entrega pasaron en [40530123863](https://github.com/fralmeagUTP/visualstruct_web/actions/runs/40530123863); E2E principal de algoritmos de grafos pasó en [40530123826](https://github.com/fralmeagUTP/visualstruct_web/actions/runs/40530123826).

El CI global no está aprobado: Chromium0 tiene aserciones y errores de pruebas históricas aún sin diagnóstico completo; unitarias0/1 fueron canceladas aproximadamente a15min (unit0 había registrado1377passed,19failed,10errors). No se atribuyen todos estos resultados a pruebas obsoletas ni a defectos de la aplicación. Algunas correcciones adicionales de pruebas sólo existen en commits locales o archivos bajo validación y no se presentan como ya publicadas.

El hash del informe histórico review.md sigue discrepante: esperado575ce6e9c64cadb19e1e141b1ca8a52f1eea6421e0de9bd1cf1a91a25ff64077. El control estricto lo rechaza. La comprobación aislada registró1failed/9passed; es una referencia documental, no una ejecución fallida de binsort. No se sustituye ni se declara conforme.

No se encontró un defecto bloqueante del runtime en los dos casos sospechosos. El alcance respaldado es una prueba controlada del usuario con respaldo y reversión; no una certificación global de CI. La tarea VPS debe identificar su destino, conservar datos/configuración y verificar la versión y función nueva después del despliegue. Este documento conserva las limitaciones y no modifica gates ni autorizaciones.
