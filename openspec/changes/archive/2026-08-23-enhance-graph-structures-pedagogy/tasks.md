# Tareas

## 1. Contrato pedagógico y fidelidad causal

- [x] 1.1 Definir objetivos, conocimientos previos y criterios de dominio para construcción, BFS, DFS, Dijkstra, Bellman-Ford, Prim y Kruskal.
- [x] 1.2 Publicar un esquema versionado de frame con condición, variables, estructura auxiliar, vértices, aristas, tablas, estado e invariante.
- [x] 1.3 Eliminar inferencias frontend de recorrido, relajación, camino y MST que no procedan de eventos canónicos.
- [x] 1.4 Emitir frames desde la ruta real del intérprete, incluyendo llamadas auxiliares, ciclos, retornos y ramas no tomadas como ausencia.
- [x] 1.5 Crear golden traces de descubrimiento, extracción, examen, backtracking, relajación, cierre, ciclo negativo, frontera, `find`, `union`, aceptación y rechazo.

## 2. Organización de la experiencia

- [x] 2.1 Dividir la pantalla en Preparar, Predecir, Ejecutar, Comprender, Relacionar con C, Comparar y Reflexionar.
- [x] 2.2 Mantener grafo y C simultáneos en escritorio y pestañas persistentes en móvil.
- [x] 2.3 Añadir panel redimensionable, índice de funciones y opción para ocultar documentación C extensa.
- [x] 2.4 Separar reinicio de ejecución y restablecimiento del grafo con confirmación.
- [x] 2.5 Añadir leyenda permanente para no descubierto, frontera, activo, cerrado, MST, aceptado y rechazado.

## 3. Progresión y ejemplos

- [x] 3.1 Implementar niveles Básico, Intermedio y Avanzado sobre una única traza.
- [x] 3.2 Escribir narraciones por algoritmo, concepto, caso y nivel.
- [x] 3.3 Conservar grafo, algoritmo, entrada, nivel, fase y cursor al cambiar presentación.
- [x] 3.4 Añadir ejemplos de vacío, único, aislado, desconectado, ciclo, DAG y grafo completo pequeño.
- [x] 3.5 Añadir ejemplos ponderados de empate, destino inalcanzable, ruta indirecta barata y peso negativo.
- [x] 3.6 Añadir ciclo negativo alcanzable/no alcanzable y varios MST de igual peso.
- [x] 3.7 Documentar y probar la política de lazos, aristas paralelas y orden de vecinos.

## 4. Construcción y representación del grafo

- [x] 4.1 Mostrar lista de adyacencia sincronizada con el dibujo y con las reservas/enlaces del C.
- [x] 4.2 Diferenciar arista no dirigida y arco dirigido mediante texto, símbolos y accesibilidad.
- [x] 4.3 Mostrar grado, grado de entrada y grado de salida cuando corresponda.
- [x] 4.4 Explicar inserción/eliminación de vértices y todas las aristas incidentes afectadas.
- [x] 4.5 Garantizar que la generación aleatoria produzca una entrada inmutable hasta que el usuario solicite otra.
- [x] 4.6 Representar `malloc`, validación de `NULL`, enlaces, desconexión y `free` con direcciones lógicas estables.

## 5. Recorridos BFS y DFS

- [x] 5.1 BFS: visualizar cola FIFO, extracción, descubrimiento, vecinos, niveles y árbol de predecesores.
- [x] 5.2 Explicar que BFS minimiza número de aristas solo en grafos no ponderados o de peso uniforme.
- [x] 5.3 DFS: visualizar pila explícita/recursiva, entrada, descenso, backtracking y finalización.
- [x] 5.4 Diferenciar descubierto, activo y finalizado sin depender únicamente del color.
- [x] 5.5 Mostrar bosque de recorrido y reinicio por componente en grafos desconectados cuando aplique.
- [x] 5.6 Verificar visitado único, coherencia de cola/pila y árbol de recorrido en cada fase.

## 6. Caminos mínimos

- [x] 6.1 Mostrar tabla sincronizada de vértice, estado, distancia, predecesor e iteración.
- [x] 6.2 Dijkstra: visualizar cola de prioridad, extracción mínima, examen, relajación y cierre definitivo.
- [x] 6.3 Mostrar relajaciones exitosas y fallidas con expresión sustituida y efecto real.
- [x] 6.4 Rechazar Dijkstra con pesos negativos y explicar el contraejemplo.
- [x] 6.5 Bellman-Ford: visualizar las `V-1` iteraciones, orden de aristas, cambios y terminación anticipada.
- [x] 6.6 Visualizar la pasada adicional y diferenciar ciclo negativo alcanzable de destino inalcanzable.
- [x] 6.7 Reconstruir el camino desde predecesores y demostrar su costo arista por arista.

## 7. Árbol de expansión mínima

- [x] 7.1 Prim: mostrar conjunto incorporado, frontera, claves, padres, candidato y peso acumulado.
- [x] 7.2 Kruskal: mostrar aristas ordenadas, candidata, aceptada/rechazada y peso acumulado.
- [x] 7.3 Visualizar Union-Find con padre, rango/tamaño, `find`, compresión y `union`.
- [x] 7.4 Explicar por qué una arista rechazada formaría ciclo.
- [x] 7.5 Validar grafo no dirigido y distinguir MST de bosque de expansión en grafos desconectados.
- [x] 7.6 Verificar aciclicidad, cobertura, número de aristas y peso total en cada resultado.

## 8. Reproducción y aprendizaje activo

- [x] 8.1 Añadir Preparar, Reproducir, Pausar, Inicio, Anterior, Siguiente, Final y Repetir.
- [x] 8.2 Añadir progreso navegable con paso, función, fase, concepto, vértice y arista.
- [x] 8.3 Añadir predicciones de extracción, vecino, relajación, predecesor, arista MST y ciclo.
- [x] 8.4 Añadir pistas graduadas, retroalimentación y continuación sin responder.
- [x] 8.5 Guardar progreso conceptual solo durante la sesión y permitir reiniciarlo.
- [x] 8.6 Añadir modo práctica que oculte temporalmente el siguiente estado.
- [x] 8.7 Garantizar restauración exacta de grafo, auxiliares, tablas, consola y visual al retroceder.

## 9. Comparación, ayuda y cierre QA

- [x] 9.1 Comparar BFS/DFS, Dijkstra/Bellman-Ford y Prim/Kruskal sobre copias aisladas de una entrada inmutable.
- [x] 9.2 Sincronizar comparaciones por concepto y generar conclusiones sobre estado auxiliar, costo, restricción e invariante.
- [x] 9.3 Reescribir ayuda con objetivo, estrategia, invariante, memoria, complejidad, aplicaciones y errores frecuentes.
- [x] 9.4 Añadir glosario, guía docente, teclado completo, foco visible, anuncios y movimiento reducido.
- [x] 9.5 Añadir exportación de captura y resumen estructurado de ejecución/aprendizaje.
- [x] 9.6 Ejecutar contratos, golden traces, propiedades y equivalencia rápido/paso a paso.
- [x] 9.7 Ejecutar Playwright de reproducción, práctica, comparación, teclado y responsividad.
- [x] 9.8 Ejecutar auditoría de accesibilidad, recorrido de usabilidad, suite completa, cobertura, C17, ASan y UBSan.
- [x] 9.9 Publicar informe antes/después y validar OpenSpec en modo estricto.
