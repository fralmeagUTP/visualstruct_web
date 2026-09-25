# Diseño pedagógico del módulo de grafos

## Principios

1. Cada frame visual corresponde a una instrucción C realmente ejecutada.
2. El frontend representa eventos canónicos y no reconstruye recorridos, relajaciones ni MST desde el resultado final.
3. Cada frame responde qué elemento se extrajo, qué arista se examinó, qué condición se evaluó, qué cambió y qué invariante se conserva.
4. Cambiar el nivel de explicación no modifica traza, cursor ni estado.
5. Avanzar y retroceder restaura grafo, estructura auxiliar, tablas, código, consola e historial exactamente.
6. Color y movimiento siempre tienen equivalentes textuales y simbólicos.

## Arquitectura de pantalla

- **Preparar:** tipo de grafo, representación, entrada, algoritmo, nivel y ejemplo guiado.
- **Predecir:** próximo vértice, relajación, arista aceptada/rechazada o ciclo esperado.
- **Ejecutar:** grafo, código y controles completos.
- **Comprender:** estructura auxiliar, tabla por vértice, arista activa, condición e invariante.
- **Relacionar con C:** función, variables, índices, punteros, memoria, retornos y `printf`.
- **Comparar:** ejecuciones aisladas sincronizadas por concepto.
- **Reflexionar:** conclusión, historial, errores frecuentes y exportación.

En escritorio el grafo y el código permanecen visibles simultáneamente. En móvil se usan pestañas persistentes sin perder cursor, estructura auxiliar ni tabla.

## Contrato de frame

```json
{
  "schema_version": 1,
  "algorithm": "run_dijkstra",
  "concept": "extract|examine|relax|close|accept|reject|union|return",
  "source": {"line_index": 42, "line_text": "if (dist[u] + peso < dist[v])"},
  "condition": {"substituted": "0 + 4 < INF", "result": true},
  "variables": [{"name": "u", "type": "Vertice *", "value": "A"}],
  "auxiliary": {"kind": "priority_queue", "items": [["B", 4], ["C", 7]]},
  "vertices": [{"id": "B", "status": "frontier", "distance": 4, "predecessor": "A"}],
  "active_edge": {"from": "A", "to": "B", "weight": 4},
  "state_before": {},
  "state_after": {},
  "invariant": {"name": "distancias cerradas definitivas", "holds": true, "evidence": "dist[A]=0"},
  "narration": {"basic": "...", "intermediate": "...", "advanced": "..."}
}
```

## Invariantes por algoritmo

| Algoritmo | Evidencia requerida |
|---|---|
| BFS | cola FIFO, descubierto una vez y nivel no decreciente |
| DFS | pila coherente, activos en la rama actual y finalización tras descendientes |
| Dijkstra | pesos no negativos y distancia definitiva al cerrar un vértice |
| Bellman-Ford | relajación de todas las aristas por iteración y pasada de ciclo negativo |
| Prim | árbol conectado sobre el conjunto incorporado y arista mínima de frontera |
| Kruskal | aristas en orden no decreciente y unión solo de componentes distintas |

## Comparaciones

Las comparaciones emplean copias profundas de un grafo inmutable. BFS/DFS se sincronizan por descubrir/examinar/finalizar; Dijkstra/Bellman-Ford por relajación; Prim/Kruskal por considerar/aceptar/rechazar una arista.

## Estrategia de pruebas

- Golden traces de extracción, descubrimiento, backtracking, relajación, cierre, iteración, ciclo negativo, frontera, `find`, `union`, aceptación y rechazo.
- Propiedades de visitado único, distancias, predecesores, MST/forest y equivalencia de modos.
- Verificación frame a frame entre C, backend, traza, consola, historial y SVG.
- Playwright para reproducción, práctica, comparación, teclado, móvil y movimiento reducido.
- Suite completa, cobertura, C17, AddressSanitizer y UndefinedBehaviorSanitizer.
