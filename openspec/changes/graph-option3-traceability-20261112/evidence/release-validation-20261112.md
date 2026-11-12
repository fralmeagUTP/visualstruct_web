# Validación integral del release final

Release runtime: `8186a4f4e9b7b5419942bba034f7d9e78dfd958d`. Head documental de PR #8: `c49423d2028d0ca7ca9c80010cd1f3252d9519a6`, runtime idéntico. Imagen exacta: `visualstruct-web:render-8186a4f`, digest `sha256:f84dbcc9818a7e0b3feb552c5365ac156a6023fbb91e2217e19624cfad42db93`.

## Resultados nuevos
- Canario de imagen exacta: 16 casos de fuente/traza PASS en 15,90 s.
- Navegador contra ese canario: 10 casos PASS en 220,79 s, usando runner Chromium previamente disponible. Solo se adaptó transporte del servidor/base URL/fixture y teardown; las 18 assertions y JavaScript del test permanecieron idénticos por comparación AST. Sin instalaciones, puertos públicos ni sesiones de producción.
- Desktop independiente: test original intacto, 26 PASS en 171,96 s; 286 archivos verificados byte por byte contra release, cero diferencias. Incluye diez casos C, diez navegador y seis grafo vacío/inicio ausente.

Posiciones bidireccionales verificadas en canario: BFS 1136, DFS 1146, Dijkstra 922, Bellman-Ford 1110, Prim 906, Kruskal 1110, insertar vértice 106, eliminar vértice 136, insertar arista 226 y eliminar arista 126. Total: 6924.

Se verificaron filtro y auxiliares pertinentes, índice, coordenadas C nativas, todos los pasos adelante/atrás, reset, alternancia de comentarios y selección, ausencia de POST adicionales al navegar y ausencia de errores JavaScript.

## Límites
Es validación finita del grafo/casos de la suite, no certificación de todas las topologías, suite global o CI completo. CI Unit/Coverage y E2E generales presentan fallos y ejecuciones aún sin concluir; esta validación focal no los resuelve. No se integró el PR. Este registro se incluye en el lote de correcciones verificadas, sin redeplegar el runtime.
