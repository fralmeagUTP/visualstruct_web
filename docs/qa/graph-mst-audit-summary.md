# Auditoría de Prim y Kruskal

Se evaluaron candidatos, pesos repetidos, union-find, componentes desconectados,
orientación y costo acumulado.

| Área | Resultado |
|---|---|
| Selección y costo final en grafo conectado | Aprobado |
| Prevención de ciclos mediante union-find | Aprobado en resultado final |
| Contrato para grafos dirigidos | Divergencia (`GRAPH-006`, alta) |
| Clasificación de resultados desconectados | Fallido (`GRAPH-006`, alta) |
| Candidatos y estado union-find frame a frame | Fallido (`GRAPH-006`, alta) |

Prim produce el árbol de la componente inicial y Kruskal un bosque, pero la API
no informa que el resultado no es un árbol de expansión de todos los vértices.
