# Tareas

## 1. Contrato pedagógico y fidelidad causal

- [x] 1.1 Definir objetivos, conocimientos previos y criterios de dominio para ABB, AVL, rojo-negro y heap.
- [x] 1.2 Publicar un esquema versionado de frame jerárquico con condición, variables, pila, nodos, memoria, ajuste e invariante.
- [x] 1.3 Eliminar inferencias frontend de ramas, rotaciones, recoloreos e intercambios que no procedan de eventos canónicos.
- [x] 1.4 Emitir frames desde la ruta real del intérprete, incluyendo llamadas recursivas y retornos.
- [x] 1.5 Crear golden traces para comparación, descenso, retorno, asignación, reserva, enlace, rotación, recoloreo, intercambio y liberación.

## 2. Organización de la experiencia

- [x] 2.1 Dividir la pantalla en Preparar, Predecir, Ejecutar, Comprender, Relacionar con C, Comparar y Reflexionar.
- [x] 2.2 Mantener visualización y C simultáneos en escritorio y pestañas persistentes en móvil.
- [x] 2.3 Añadir panel redimensionable, índice de funciones y opción para ocultar documentación C extensa.
- [x] 2.4 Separar reinicio de ejecución y restablecimiento del TAD con confirmación.

## 3. Progresión y ejemplos

- [x] 3.1 Implementar niveles Básico, Intermedio y Avanzado sobre una traza única.
- [x] 3.2 Escribir narraciones por TAD, operación, concepto, caso y nivel.
- [x] 3.3 Conservar estructura, operación, entrada, nivel y cursor al cambiar la presentación.
- [x] 3.4 Añadir ejemplos ABB: vacío, búsqueda, degeneración y eliminación de hoja/un hijo/dos hijos.
- [x] 3.5 Añadir ejemplos AVL LL, RR, LR, RL y rebalanceo posterior a eliminación.
- [x] 3.6 Añadir ejemplos rojo-negro de padre negro, tío rojo, tío negro, rotaciones y propagación.
- [x] 3.7 Añadir ejemplos heap de inserción/extracción, empate, ascenso, descenso, único y vacío.

## 4. Recursión, control y memoria C

- [x] 4.1 Mostrar condiciones sustituidas, resultado y rama izquierda/derecha realmente ejecutada.
- [x] 4.2 Mostrar variables con tipo C, significado, valor anterior/actual y cambio.
- [x] 4.3 Mostrar pila recursiva con raíz local, parámetros, retorno y continuación.
- [x] 4.4 Representar `malloc`, validación de `NULL`, inicialización, enlaces y direcciones lógicas estables.
- [x] 4.5 Representar desconexión, sustitución, `free` y ausencia de referencias colgantes.
- [x] 4.6 Mostrar propagación de retornos y reconexión de subárboles.
- [x] 4.7 Garantizar restauración exacta de pila, memoria, árbol/arreglo, consola y visual al retroceder.

## 5. Visualizaciones e invariantes por TAD

- [x] 5.1 ABB: visualizar límites, ruta, caso de eliminación, sucesor y reconexión.
- [x] 5.2 AVL: visualizar altura, FE, nodo crítico, pivote, subárbol transferido y rotaciones LL/RR/LR/RL.
- [x] 5.3 Dividir rotaciones dobles en dos pasos simples causalmente sincronizados.
- [x] 5.4 Rojo-negro: visualizar nodo, padre, abuelo, tío, caso, recoloreo, rotación y propagación.
- [x] 5.5 Mostrar black-height por camino y reglas RN mediante texto y símbolos además del color.
- [x] 5.6 Heap: vincular `A[i]` con nodo, padre/hijos, candidato, intercambio y región ya válida.
- [x] 5.7 Explicar que el heap no es un ABB ni un arreglo totalmente ordenado.
- [x] 5.8 Verificar el invariante específico en cada fase con evidencia por nodo/camino.

## 6. Reproducción y aprendizaje activo

- [x] 6.1 Añadir Preparar, Reproducir, Pausar, Inicio, Anterior, Siguiente, Final y Repetir.
- [x] 6.2 Añadir progreso navegable con paso, función, profundidad, fase y concepto.
- [x] 6.3 Añadir predicciones opcionales de rama, caso de eliminación, rotación, recoloreo e intercambio.
- [x] 6.4 Añadir pistas graduadas, retroalimentación y continuación sin responder.
- [x] 6.5 Guardar progreso conceptual solo durante la sesión y permitir reiniciarlo.
- [x] 6.6 Añadir modo práctica que oculte temporalmente el siguiente estado.

## 7. Comparación conceptual

- [x] 7.1 Ejecutar comparaciones sobre copias aisladas de una entrada inmutable.
- [x] 7.2 Implementar ABB vs AVL con secuencias balanceadas y degeneradas.
- [x] 7.3 Implementar AVL vs rojo-negro y explicar balance estricto frente a reglas de color.
- [x] 7.4 Implementar ABB vs heap y explicar orden de búsqueda frente a prioridad parcial.
- [x] 7.5 Comparar inorden, preorden y postorden con pila recursiva sincronizada.
- [x] 7.6 Generar conclusiones guiadas sobre forma, altura, ajustes, costo e invariante.

## 8. Ayuda, accesibilidad y material docente

- [x] 8.1 Reescribir ayuda por TAD con objetivo, estrategia, invariante, memoria, complejidad y errores frecuentes.
- [x] 8.2 Añadir glosario de raíz, hoja, altura, profundidad, FE, rotación, recoloreo, black-height y heapify.
- [x] 8.3 Añadir guía docente con secuencias de clase, preguntas, ejercicios y rúbrica.
- [x] 8.4 Implementar teclado completo, foco visible, nombres accesibles y anuncios breves.
- [x] 8.5 Verificar contraste, reducción de movimiento y equivalentes textuales de color/animación.
- [x] 8.6 Añadir exportación de captura y resumen de ejecución.

## 9. Verificación y cierre

- [x] 9.1 Ejecutar contratos y golden traces de todos los TAD, operaciones, niveles y casos límite.
- [x] 9.2 Verificar C/backend/traza/historial/consola/visualización frame por frame.
- [x] 9.3 Ejecutar propiedades de ABB, AVL, RN y heap y equivalencia rápido/paso a paso.
- [x] 9.4 Ejecutar Playwright de reproducción, práctica, comparación, teclado y responsividad.
- [x] 9.5 Ejecutar auditoría de accesibilidad y recorrido de usabilidad con tareas de comprensión.
- [x] 9.6 Ejecutar suite completa, cobertura, C17, ASan y UBSan.
- [x] 9.7 Publicar informe antes/después y validar OpenSpec en modo estricto.
