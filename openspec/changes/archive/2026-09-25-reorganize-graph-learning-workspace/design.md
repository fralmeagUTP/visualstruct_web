# Diseño: experiencia compacta para Grafos

## Flujo común por fase

```
1. Preparar y controlar
   tipo de grafo + operación o algoritmo + entradas + Ejecutar operación + Paso a paso
2. Visualizar y ejecutar       3. Relacionar con código C
   lienzo, aristas, pesos,          funciones arriba y código a ancho completo
   leyenda y estado activo
4. Comprender (plegable)
5. Resultados de la ejecución (plegable)
```

La navegación de Construcción, Recorridos, Camino mínimo y Expansión mínima permanece como contexto curricular. Paso a paso muestra Anterior/Siguiente sólo cuando hay traza y Ejecutar operación completa la traza actual o aplica una operación nueva según el motor.

## Contrato visual por operación

| Grupo | Estado y frames que debe comunicar |
|---|---|
| Construcción | tipo dirigido/no dirigido, altas/bajas, arista/arco, peso y efecto espejo cuando aplique; consultas sin mutación |
| BFS | vértice activo, cola FIFO, descubrimiento, marcado y orden por niveles |
| DFS | rama activa, pila o recursión, marcado y retroceso |
| Dijkstra | distancia tentativa, predecesor, selección mínima y relajación; rechazo explícito de peso negativo |
| Bellman-Ford | pasada de relajación, actualización, ausencia de cambio y ciclo negativo |
| Prim | frontera, arista candidata aceptada y árbol parcial |
| Kruskal | arista ordenada, representantes Union-Find, aceptación o rechazo por ciclo |

Color nunca será la única evidencia: leyenda, rótulos y Comprender expresarán acción, auxiliar e invariante. El lienzo no inventa aristas, caminos o estados que no estén en el frame canónico.

## Código, resultados y responsive

Código C se lee en vertical: checkbox junto al encabezado, funciones en franja superior y bloque C debajo a ancho completo. Resultados pliega/restablece consola, historial, TAD y exportaciones; el TAD no usa `details` propio. En escritorio lienzo y código son legibles en paralelo; en pantalla estrecha el conmutador actual conserva `aria-selected` y la traza. Tablas de distancias o Union-Find se ajustan o desplazan sólo dentro de su tarjeta.
