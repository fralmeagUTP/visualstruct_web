# Informe de cierre pedagógico y QA del módulo de grafos

## Resultado

Las fases 1–9 convierten el módulo en un laboratorio causal: cada cambio visual procede de un frame del backend asociado con la línea C ejecutada. La revisión final cubre construcción, BFS, DFS, Dijkstra, Bellman-Ford, Prim y Kruskal.

## Antes y después

| Área | Antes | Después |
|---|---|---|
| Representación | Dibujo sin explicación completa de adyacencia/memoria | Adyacencia, grados, arcos/aristas y memoria lógica sincronizados |
| Recorridos | Orden final y resaltado general | Cola/pila, descubierto/activo/cerrado, árbol y componente |
| Caminos mínimos | Resultado y ruta | Extracción, tabla, relajación exitosa/fallida, iteraciones y ciclo negativo |
| MST | Aristas finales | Frontera de Prim; orden, `find`, compresión, `union`, aceptación y rechazo de Kruskal |
| Reproducción | Reproducir, anterior y siguiente | Preparar, pausar, inicio, final, repetir, cursor navegable y restauración integral |
| Aprendizaje | Lectura pasiva | Predicción, pistas, práctica oculta y progreso de sesión |
| Comparación | No disponible | BFS/DFS, Dijkstra/Bellman-Ford y Prim/Kruskal sobre copias aisladas |
| Cierre | Sin resumen específico | Captura JPG, resumen JSON, ayuda, glosario, guía docente y teclado |

## Evidencia automatizada

- 80 pruebas focalizadas aprobadas; cobertura focalizada total: 83%.
- 2 recorridos Playwright de contexto móvil y práctica/comparación aprobados.
- Suite completa final: 898 pruebas aprobadas en 5 min 45 s. El único fallo de la primera ejecución fue el umbral de rendimiento BFS, corregido mediante frames compactos para grafos grandes y confirmado en la repetición completa.
- C17 estricto del harness `graph`: aprobado con `-Wall -Wextra -Wpedantic -Werror`.
- ASan/UBSan: ejecución solicitada; el GCC MinGW local no posee `libasan`/`libubsan`. El workflow Linux independiente permanece como gate obligatorio.
- OpenSpec validado en modo estricto.

## Accesibilidad y usabilidad

Se verificaron etiquetas, regiones vivas, estados que no dependen solo del color, foco visible, teclado, diseño móvil y reducción de movimiento. El recorrido recomendado es preparar, predecir, ejecutar, comprender, relacionar con C, comparar y reflexionar.

## Riesgo residual

Los sanitizers deben confirmarse en CI Linux. En grafos mayores de 120 elementos combinados, el frame omite el detalle repetido de adyacencia para conservar el límite de respuesta; el dibujo, tabla algorítmica y estado canónico continúan disponibles.
