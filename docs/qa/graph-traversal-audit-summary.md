# Auditoría de BFS y DFS

Se probaron cadenas, bifurcaciones, ciclos, vértices aislados, inicio inválido y
componentes desconectados. Las ramas principales y las llamadas recursivas se
expanden, pero el valor retornado no conserva la semántica del C.

| Área | Resultado |
|---|---|
| Inicio inexistente y alcance por componente | Aprobado |
| Cola BFS y recursión DFS en la traza | Aprobado parcialmente |
| Aristas destacadas existentes | Aprobado |
| Orden de la lista retornada por C | Fallido (`GRAPH-003`, alta) |

El C antepone nodos y retorna el recorrido invertido; Python muestra el orden de
visita directo. La auditoría distingue explícitamente ambos conceptos.
