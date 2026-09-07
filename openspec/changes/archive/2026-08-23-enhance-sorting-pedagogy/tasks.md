# Tareas

## 1. Base pedagógica y contratos

- [x] 1.1 Definir objetivos de aprendizaje, conocimientos previos y criterios de dominio para los once algoritmos.
- [x] 1.2 Extender el frame de traza con concepto, fase, condición, variables, pila, invariante y narración multinivel.
- [x] 1.3 Publicar esquema versionado y validadores que rechacen frames incompletos o líneas C inconsistentes.
- [x] 1.4 Crear fixtures golden para llamada, retorno, condición verdadera/falsa, ciclo, recursión y asignación por puntero.

## 2. Nueva organización de pantalla

- [x] 2.1 Separar la pantalla en Preparar, Visualizar, Comprender, Relacionar con C y Reflexionar.
- [x] 2.2 Mantener visualización y código simultáneamente visibles en escritorio y crear pestañas persistentes en móvil.
- [x] 2.3 Añadir panel redimensionable y opción para ocultar comentarios/documentación extensa del C.
- [x] 2.4 Añadir minimapa/índice de funciones con indicador de función activa.
- [x] 2.5 Reducir el tamaño aleatorio recomendado a 6–8 sin retirar el máximo técnico de 80.

## 3. Progresión didáctica

- [x] 3.1 Implementar niveles Básico, Intermedio y Avanzado sin alterar la traza subyacente.
- [x] 3.2 Crear narraciones específicas por nivel para cada concepto y algoritmo.
- [x] 3.3 Mantener nivel, algoritmo, entrada y cursor al cambiar de presentación.
- [x] 3.4 Añadir ejemplos guiados: normal, ordenado, inverso, duplicados, signos y mejor/peor caso.

## 4. Control de flujo y memoria

- [x] 4.1 Mostrar tabla de variables con valor, significado, tipo C y cambios del frame.
- [x] 4.2 Mostrar expresión sustituida, resultado verdadero/falso y consecuencia de cada condición.
- [x] 4.3 Mostrar iteración y límites de cada `for`/`while`, incluidos pasos de salida del ciclo.
- [x] 4.4 Mostrar pila de llamadas, parámetros, retornos y punto de continuación.
- [x] 4.5 Mostrar punteros, `temporal`, auxiliares y estados transitorios de asignaciones.
- [x] 4.6 Garantizar que retroceder restaure exactamente variables, pila, punteros y estado visual.

## 5. Visualizaciones específicas

- [x] 5.1 Implementar eje cero y representación accesible de negativos/positivos.
- [x] 5.2 Implementar mínimo provisional, clave/hueco, frontera de pasada y grupos por `gap`.
- [x] 5.3 Implementar particiones y árbol recursivo de QuickSort.
- [x] 5.4 Implementar árbol de división/fusión y auxiliar de MergeSort.
- [x] 5.5 Implementar vista sincronizada arreglo–árbol para HeapSort.
- [x] 5.6 Implementar frecuencias/urnas para Counting Sort y Binsort.
- [x] 5.7 Implementar dígito activo, signo y buckets 0–9 para Radix Sort.
- [x] 5.8 Añadir leyenda textual y símbolos que no dependan del color.

## 6. Reproducción y navegación

- [x] 6.1 Añadir Preparar, Reproducir, Pausar, Inicio, Anterior, Siguiente, Final y Repetir.
- [x] 6.2 Añadir barra de progreso navegable con número de paso, fase y concepto.
- [x] 6.3 Permitir velocidades pedagógicas y respetar `prefers-reduced-motion`.
- [x] 6.4 Conservar estado exacto al pausar, cambiar nivel, redimensionar o cambiar pestaña.
- [x] 6.5 Separar Reiniciar ejecución de Restablecer datos y solicitar confirmación cuando corresponda.

## 7. Invariantes y análisis

- [x] 7.1 Explicar y resaltar el invariante específico de cada algoritmo en cada fase.
- [x] 7.2 Distinguir métricas observadas de complejidad teórica.
- [x] 7.3 Publicar fichas de complejidad, memoria, estabilidad e in-place para los once métodos.
- [x] 7.4 Explicar casos mejor, promedio y peor con ejemplos reproducibles.

## 8. Aprendizaje activo

- [x] 8.1 Implementar predicciones opcionales antes de ramas, intercambios y cambios de fase.
- [x] 8.2 Añadir pistas graduadas y retroalimentación explicativa inmediata.
- [x] 8.3 Registrar progreso conceptual sólo durante la sesión y permitir reiniciarlo.
- [x] 8.4 Añadir modo práctica que oculte temporalmente el resultado del siguiente paso.

## 9. Comparador de algoritmos

- [x] 9.1 Permitir seleccionar dos algoritmos y una única entrada inmutable.
- [x] 9.2 Implementar reproducción lado a lado sincronizada por paso o concepto.
- [x] 9.3 Comparar métricas observadas y propiedades teóricas sin mezclarlas.
- [x] 9.4 Añadir conclusiones guiadas y advertencias sobre generalización desde una sola entrada.

## 10. Accesibilidad y usabilidad

- [x] 10.1 Implementar navegación completa por teclado, foco visible y atajos documentados.
- [x] 10.2 Añadir roles, nombres accesibles y anuncios breves de cambios relevantes.
- [x] 10.3 Verificar contraste y que ningún estado dependa sólo del color.
- [x] 10.4 Probar escritorio, tableta y móvil sin perder código, cursor ni explicación.
- [x] 10.5 Realizar prueba de usabilidad con tareas de comprensión, no sólo de operación de controles.

## 11. Ayuda y material docente

- [x] 11.1 Reescribir ayuda por algoritmo con objetivo, estrategia, invariante y errores frecuentes.
- [x] 11.2 Añadir guía para docentes con secuencias de clase y preguntas sugeridas.
- [x] 11.3 Añadir glosario contextual de pivote, estabilidad, in-place, heap, bucket y complejidad.
- [x] 11.4 Añadir exportación de captura y resumen de ejecución para discusión en clase.

## 12. Verificación y cierre

- [x] 12.1 Ejecutar contratos y golden traces de los once algoritmos en los tres niveles.
- [x] 12.2 Ejecutar pruebas Playwright de controles, predicciones, comparador y responsividad.
- [x] 12.3 Ejecutar auditoría de accesibilidad automatizada y revisión manual por teclado/lector.
- [x] 12.4 Verificar equivalencia final con C, rápido/paso a paso y comparación lado a lado.
- [x] 12.5 Ejecutar suite completa, C17 y sanitizadores sin reducir cobertura.
- [x] 12.6 Publicar informe pedagógico con evidencia antes/después y validar OpenSpec en modo estricto.
