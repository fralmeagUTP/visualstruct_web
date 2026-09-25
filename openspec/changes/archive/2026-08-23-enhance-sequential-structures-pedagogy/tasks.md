# Tareas

## 1. Contrato pedagógico y fidelidad causal

- [x] 1.1 Definir objetivos, conocimientos previos y criterios de dominio para los seis TAD.
- [x] 1.2 Publicar un esquema versionado de frame secuencial con condiciones, variables, punteros, heap y pila.
- [x] 1.3 Eliminar el mapeo visual por proporción y toda inferencia de ramas en el frontend.
- [x] 1.4 Generar frames exclusivamente desde eventos reales del intérprete/backend.
- [x] 1.5 Crear golden traces para llamada, retorno, `malloc`, fallo de reserva, enlace, rama, ciclo y `free`.

## 2. Organización de la experiencia

- [x] 2.1 Dividir la pantalla en Preparar, Predecir, Ejecutar, Comprender, Relacionar con C y Reflexionar.
- [x] 2.2 Mantener visualización y C simultáneos en escritorio y pestañas persistentes en móvil.
- [x] 2.3 Añadir panel redimensionable, índice de funciones y opción para ocultar documentación C extensa.
- [x] 2.4 Separar reinicio de ejecución y restablecimiento del TAD con confirmación cuando corresponda.

## 3. Progresión y ejemplos

- [x] 3.1 Implementar niveles Básico, Intermedio y Avanzado sobre una traza única.
- [x] 3.2 Escribir narraciones por TAD, operación, concepto y nivel.
- [x] 3.3 Conservar TAD, operación, entrada, nivel y cursor al cambiar la presentación.
- [x] 3.4 Añadir ejemplos guiados: vacío, uno, varios, repetidos, inválido, extremos y no encontrado.
- [x] 3.5 Añadir secuencias específicas para LIFO, FIFO, empate de prioridad, circularidad y aislamiento de ramas.

## 4. Control de flujo y memoria C

- [x] 4.1 Mostrar condiciones sustituidas, resultado y consecuencia de la rama ejecutada.
- [x] 4.2 Mostrar tabla de variables con tipo C, significado, valor anterior/actual y cambio.
- [x] 4.3 Mostrar pila de llamadas, parámetros, retorno y punto de continuación.
- [x] 4.4 Representar `malloc`, validación de `NULL`, campos sin inicializar y objeto enlazado.
- [x] 4.5 Representar punteros, alias, enlace anterior/nuevo y direcciones lógicas estables.
- [x] 4.6 Representar desconexión, `free` y prohibir referencias visuales a memoria liberada.
- [x] 4.7 Mostrar iteraciones y criterio real de salida, especialmente en listas circulares.
- [x] 4.8 Garantizar restauración exacta de memoria, punteros, pila y visual al retroceder.

## 5. Visualizaciones e invariantes por TAD

- [x] 5.1 Pila: visualizar `TOP`, auxiliar, enlace, LIFO y liberación al desapilar.
- [x] 5.2 Cola: visualizar `FRONT`, `BACK`, FIFO y transiciones vacío/único/múltiple.
- [x] 5.3 Cola de prioridad: separar orden de llegada, prioridad, candidato, seleccionado y empate estable.
- [x] 5.4 Corregir textos que describen incorrectamente la cola de prioridad como físicamente ordenada.
- [x] 5.5 Lista enlazada: visualizar `HEAD`, `actual`, `anterior`, conectividad y enlace sustituido.
- [x] 5.6 Lista circular: visualizar cierre, último→primero, vuelta al inicio y terminación segura.
- [x] 5.7 Sublista: visualizar propiedad padre-hijo, rama activa y aislamiento de ramas.
- [x] 5.8 Mostrar y verificar el invariante específico en cada fase con texto y símbolos.

## 6. Reproducción y aprendizaje activo

- [x] 6.1 Añadir Preparar, Reproducir, Pausar, Inicio, Anterior, Siguiente, Final y Repetir.
- [x] 6.2 Añadir progreso navegable con paso, función, fase y concepto.
- [x] 6.3 Añadir predicciones opcionales antes de ramas, reasignaciones, cambios de extremos y `free`.
- [x] 6.4 Añadir pistas graduadas, retroalimentación y continuación sin responder.
- [x] 6.5 Guardar progreso conceptual solo durante la sesión y permitir reiniciarlo.
- [x] 6.6 Añadir modo práctica que oculte temporalmente el siguiente estado.

## 7. Comparación conceptual

- [x] 7.1 Ejecutar comparaciones sobre copias aisladas de una secuencia inmutable.
- [x] 7.2 Implementar pila vs cola y explicar LIFO frente a FIFO.
- [x] 7.3 Implementar cola vs prioridad y explicar orden de llegada frente a selección.
- [x] 7.4 Implementar lista lineal vs circular y lista vs sublista.
- [x] 7.5 Sincronizar lado a lado por operación o concepto y generar conclusiones guiadas.

## 8. Ayuda, accesibilidad y material docente

- [x] 8.1 Reescribir ayuda por TAD con objetivo, estrategia, invariante, memoria y errores frecuentes.
- [x] 8.2 Añadir glosario contextual de nodo, enlace, alias, LIFO, FIFO, prioridad, circularidad, `malloc` y `free`.
- [x] 8.3 Añadir guía docente con secuencias de clase, preguntas y actividades evaluables.
- [x] 8.4 Implementar teclado completo, foco visible, nombres accesibles y anuncios breves.
- [x] 8.5 Verificar contraste y que ningún significado dependa solo del color o movimiento.
- [x] 8.6 Añadir exportación de captura y resumen de ejecución.

## 9. Verificación y cierre

- [x] 9.1 Ejecutar contratos y golden traces de todos los TAD, operaciones, niveles y casos límite.
- [x] 9.2 Verificar C/backend/traza/historial/consola/visualización frame por frame.
- [x] 9.3 Ejecutar propiedades de invariantes y equivalencia rápido/paso a paso.
- [x] 9.4 Ejecutar Playwright de reproducción, práctica, comparación, teclado y responsividad.
- [x] 9.5 Ejecutar auditoría de accesibilidad y recorrido de usabilidad con tareas de comprensión.
- [x] 9.6 Ejecutar suite completa, cobertura, C17, ASan y UBSan.
- [x] 9.7 Publicar informe antes/después y validar OpenSpec en modo estricto.
