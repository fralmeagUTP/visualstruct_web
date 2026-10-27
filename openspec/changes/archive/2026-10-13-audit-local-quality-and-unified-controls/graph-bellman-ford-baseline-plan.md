# Bellman-Ford: baseline LOW independiente

Autorizado por coordinación mientras el contrato numérico de Dijkstra sigue pendiente. Operación visible run_bellman_ford, fase /graph/graph/camino-minimo; C real grafo_bellman_ford en docs/tads_C/tad_grafo.c/.h; backend público en app/domain/graph/tad_wrappers.py, adapter y graph_structure_service.

Comparar descargas HTTP C/H compiladas C17, rutas/costos y advertencia stdout con backend. Casos normales pequeños: pesos negativos representables, ciclos negativos alcanzables e inalcanzables, desconectados, empates, vértices negativos, endpoints ausentes, INT_MAX/INT_MIN y sumas descartadas por guarda. Admitir negativos como contrato Bellman-Ford, no tratarlos como rechazo Dijkstra. Registrar equivalencia y divergencias, no deducir instrucciones desde resultados finales.

Revisar historial/repeticiones/fallos/recarga, main real generado, compilación y propiedad. La detección de ciclo negativo actual puede ser success=true con bandera de ciclo; contrastar con spec que pide error antes de elegir otra política. Verificar documentación individual y manual.

No cambiar contrato decimal ni guardas numéricas compartidas. Mantener Dijkstra abierto y BFS/DFS cerrados sin repetir oráculos. Entradas fuera de int, conversiones inseguras y reconstrucciones potencialmente no acotadas no son casos válidos para ejecutar sin protección. Si se estudia saturación/ciclo en el límite, usar diagnóstico de asignación limitada explícitamente separado de los casos normales: no agotar memoria ni inventar un resultado C sin UB.

La revisión por instrucción con arreglos/relajaciones/alias/memoria requiere un bloque separado si resulta difícil. Cualquier cambio de algoritmo C o estatus semántico del ciclo necesita decisión. Global13/22/documentación105/208 al iniciar; conservar5051. Sin push/merge/despliegue.
