# Tareas

## 1. Inventario y trazabilidad

- [x] 1.1 Crear recolector que enumere rutas, estructuras, operaciones, algoritmos, fases y controles publicados.
- [x] 1.2 Versionar el manifiesto de cobertura con identificador, fuente, precondiciones, entradas y oráculo por opción.
- [x] 1.3 Fallar la verificación cuando una opción publicada no tenga caso asignado o cuando el manifiesto esté desactualizado.
- [x] 1.4 Documentar ambiente, versiones, navegadores y dependencias reproducibles de la campaña.

## 2. Casos funcionales transversales

- [x] 2.1 Probar inicio, navegación, rutas de módulo, ayuda, assets, health check y respuestas de error.
- [x] 2.2 Probar sesión, historial, replay, reset, aislamiento entre estructuras y límites configurados.
- [x] 2.3 Probar validación de cada tipo de entrada, payload malformado, método no permitido y operación inexistente.
- [x] 2.4 Probar consola, exportación, código C, llamadas, retornos y mensajes de error/`printf` equivalentes.

## 3. Módulo secuencial completo

- [x] 3.1 Cubrir cada operación expuesta por pila, cola y cola de prioridad con vacío, normal, límite e inválido.
- [x] 3.2 Cubrir lista enlazada, circular y sublista, incluidos enlaces, cabecera/cola, circularidad, posiciones y liberación.
- [x] 3.3 Validar invariantes LIFO, FIFO, prioridad, enlaces y reconstrucción por historial en cada frame.
- [x] 3.4 Añadir propiedades y golden traces de casos frontera y regresiones.

## 4. Módulo jerárquico completo

- [x] 4.1 Cubrir todas las operaciones de ABB con raíz, hojas, uno/dos hijos, duplicados, búsqueda y recorridos.
- [x] 4.2 Cubrir AVL y rojo-negro con todos los casos de rotación, recoloreo, inserción y eliminación publicados.
- [x] 4.3 Cubrir montículo binario con inserción, extracción, heapify, empates, vacío y límites.
- [x] 4.4 Validar orden, alturas, balance, colores, enlaces, propiedad heap y trazas recursivas/auxiliares.

## 5. Módulo de grafos completo

- [x] 5.1 Cubrir construcción, edición, reinicio y representación dirigida/no dirigida según las opciones expuestas.
- [x] 5.2 Ejecutar BFS y DFS en componentes, ciclos, vértices aislados y múltiples órdenes relevantes.
- [x] 5.3 Ejecutar Dijkstra y Bellman-Ford en caminos existentes/inexistentes, pesos y restricciones publicadas.
- [x] 5.4 Ejecutar Prim y Kruskal en grafos conectados, desconectados y con empates; validar MST y costos.
- [x] 5.5 Cubrir comparador, fases, tablas auxiliares y equivalencia visual/ruta C.

## 6. Módulo hash completo

- [x] 6.1 Cubrir capacidad, índices positivos/negativos, cero y límites; verificar el cálculo C.
- [x] 6.2 Cubrir inserción, colisiones, actualización, búsqueda/existencia, eliminación por posición, vaciado y destrucción.
- [x] 6.3 Cubrir fallo controlado de memoria, comparación de capacidades y ausencia de referencias colgantes.
- [x] 6.4 Validar buckets, cadenas, punteros, cantidad, memoria, consola y reproducción reversible.

## 7. Módulo de ordenamiento completo

- [x] 7.1 Ejecutar todos los algoritmos registrados con vacío, uno, repetidos, ordenado, inverso, negativos y límites.
- [x] 7.2 Cubrir selección, entrada manual, aleatoria con semilla, ejecución, comparación y reinicio sin mutaciones inesperadas.
- [x] 7.3 Validar comparaciones, intercambios, llamadas auxiliares/recursivas, arreglo parcial/final y estabilidad cuando aplique.
- [x] 7.4 Verificar que modo rápido y reproducción lleguen al mismo resultado y que el código C muestre subrutinas ejecutadas.

## 8. Reproducción, didáctica y UI E2E

- [x] 8.1 Probar Preparar, Reproducir, Pausar, Inicio, Anterior, Siguiente, Final, Repetir, velocidad y progreso en cada módulo.
- [x] 8.2 Verificar frame a frame código activo, ramas, pila de llamadas, temporales, visual, historial y consola.
- [x] 8.3 Cubrir niveles didácticos, ejemplos, predicciones, pistas, práctica y progreso de sesión donde estén disponibles.
- [x] 8.4 Probar diseño de escritorio, móvil y tablet, preservando estado al cambiar paneles o pestañas.

## 9. Calidad no funcional

- [x] 9.1 Ejecutar auditoría de accesibilidad: teclado, foco, nombres, contraste, anuncios, reducción de movimiento y lector de pantalla guiado.
- [x] 9.2 Ejecutar seguridad: validación, límites, sesión, CSRF/headers aplicables, secretos en logs y manejo seguro de errores.
- [x] 9.3 Medir rendimiento de replay, trazas grandes, operaciones masivas y carga de pantallas; fijar presupuestos.
- [x] 9.4 Ejecutar compatibilidad en Chromium y Firefox; registrar explícitamente cualquier cobertura no disponible.

## 10. Cierre y automatización

- [x] 10.1 Ejecutar suites unitarias, integración, propiedades, golden traces, conformidad C17 y sanitizers.
- [x] 10.2 Ejecutar Playwright y publicar capturas/trazas como evidencia de los fallos.
- [x] 10.3 Generar informe completo y backlog priorizado sin aplicar correcciones.
- [x] 10.4 Configurar gates CI y validar la OpenSpec en modo estricto.
