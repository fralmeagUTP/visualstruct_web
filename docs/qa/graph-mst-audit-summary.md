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


## Actualización LOW 2026-10-02 sobre D: (historia anterior conservada)
La afirmación histórica de Prim limitado a la componente inicial y clasificación ausente no describe el C/API actuales:Prim reinicia componentes y ambos adapters informan bosque/componentes. Prim17casos:11coincidentes/6divergentes;Kruskal17:15coincidentes/2divergentes por empate yprecondición dirigida. C sinflag de dirección,API no dirigida;no se cambia esa política. Los costos/conjuntos finales normalizados no verifican frames Union-Find/candidatos.

Main no dirigido corregido para arcos simétricos;Prim yKruskal imprimen resultados C,conservan consultas yliberan listas propias. Kruskal:C burbuja estable O(E²+EV+V) conservador,negativos/extremosint admitidos;Prim omite negativos/INT_MAX. C/H algoritmo intacto;no decisión numérica/decimal. Evidencia en openspec/changes/audit-local-quality-and-unified-controls/evidence/visible-graph-{prim,kruskal}-baseline-low. Ambos permanecen abiertos por instrucción ydecisiones;no cierreGRAPH-006global.
