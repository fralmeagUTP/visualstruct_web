# Bellman-Ford: opciones pendientes de coordinación

Sin decisión implementada. Baseline de 20 casos: 15 coincidentes y 5 divergencias (empate, infinito INT_MAX, guardas superior/inferior, ciclo omitido en el límite). El caso de dos arcos INT_MIN termina y omite el ciclo alcanzable sin ejecutar suma int desbordada: cada candidata se calcula en long long y la guarda descarta el valor.

| Decisión | Opción A | Opción B | Implicación |
|---|---|---|---|
| Empate | Alinear backend/traza con orden de arcos C y mejora estricta | Cambiar regla C explícitamente | A conserva C docente; no depende del costo final solamente. |
| Distancias y ciclos en límites | Conservar int/INT_MAX y guardas, explicando que puede omitir ciclos | Rediseñar distancias con representación amplia e infinito separado, suma comprobada y detección fiable | A conserva fidelidad pero conserva un defecto matemático; B exige cambiar C/H, backend, trazas, caller y specs con pruebas de límites. No quitar guardas ni saturar silenciosamente. |
| Ciclo detectado | Mantener success=true con bandera y advertencia, reconciliando spec | Publicar error conforme a spec, manteniendo evidencia de detección | B requiere definir HTTP, historial de errores, consola y replay; el backend hoy detecta más ciclos que el C de límite. |
| Pesos | Reconciliar contrato entero representable y validación común | Diseñar soporte decimal en todos los algoritmos | Depende de la decisión abierta de Dijkstra; no truncar ni ejecutar conversiones fuera del rango. |

Recomendación para coordinación: resolver representación primero. Copiar la guarda actual como solución matemática sería incorrecto; para fidelidad puede documentarse su comportamiento, pero el defecto de ciclo debe permanecer abierto. Elegir después estatus de error e historial. La revisión por instrucción de arreglos, pasadas, relajaciones, helpers, alias y memoria necesita un bloque separado acotado; final-state parity no la sustituye.

Evidencia: evidence/visible-graph-bellman-ford-baseline-low. No UB deliberado, ni cambios de algoritmo, contrato decimal o estatus de ciclo.
