# Auditoría de caminos mínimos

Se revisaron rutas alcanzables, destinos inalcanzables, pesos negativos, ciclo
negativo, límites enteros y reconstrucción de predecesores.

| Área | Resultado |
|---|---|
| Ruta y costo final con pesos no negativos | Aprobado |
| Destino inalcanzable | Aprobado |
| Detección Bellman-Ford de ciclo negativo | Aprobado en estado final |
| Política Dijkstra para pesos negativos | Divergencia (`GRAPH-004`, alta) |
| Tablas temporales y relajaciones visuales | Fallido (`GRAPH-005`, alta) |

La animación actual deriva una ruta final; no interpreta los vectores que el C
modifica durante cada pasada.
