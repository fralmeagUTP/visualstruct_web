## ADDED Requirements

### Requirement: Progresión didáctica por niveles
El módulo SHALL ofrecer niveles Básico, Intermedio y Avanzado que presenten diferentes grados de
detalle sobre una única ejecución canónica, sin cambiar pasos, ramas ni resultado.

#### Scenario: cambiar de nivel durante una ejecución
- **GIVEN** una ejecución pausada en un frame específico
- **WHEN** el estudiante cambia de Básico a Avanzado
- **THEN** conserva algoritmo, entrada, cursor y estado, y aparecen variables, pila y C completo del mismo frame

### Requirement: Explicación causal de cada frame
Cada frame SHALL identificar concepto, fase, objetivo, acción, consecuencia e invariante; cuando
evalúe una condición SHALL mostrar expresión sustituida, resultado booleano y rama tomada.

#### Scenario: condición verdadera en Burbuja
- **GIVEN** que se evalúa `arreglo[j] > arreglo[j+1]` con valores 8 y 3
- **WHEN** se presenta el frame de condición
- **THEN** muestra `8 > 3 → verdadero`, explica que se llama `intercambiar` y resalta ambos operandos

#### Scenario: condición falsa
- **GIVEN** que la misma condición usa valores 3 y 8
- **WHEN** se presenta el frame
- **THEN** muestra `3 > 8 → falso`, indica que no se llama `intercambiar` y avanza por la rama real

### Requirement: Variables, punteros y pila de llamadas
El módulo SHALL mostrar las variables relevantes, tipos C, valores y cambios, además de la pila de
llamadas con función, parámetros, retorno y punto de continuación. Los estados temporales SHALL
coincidir con las asignaciones reales del C.

#### Scenario: entrar y salir de intercambiar
- **GIVEN** una comparación que requiere intercambio
- **WHEN** el C llama `intercambiar(&arreglo[i], &arreglo[j])`
- **THEN** la pila añade `intercambiar`, muestra `a`, `b` y `temporal`, recorre sus asignaciones y vuelve a la llamada correcta

#### Scenario: recursión QuickSort
- **WHEN** QuickSort crea una llamada recursiva para un subrango
- **THEN** la pila y el árbol recursivo muestran nivel, límites, pivote copiado y retorno sin fusionar identidades

### Requirement: Visualización específica de estrategia e invariante
Cada algoritmo SHALL disponer de una visualización que represente su estrategia y el invariante
garantizado en el frame actual, con explicación textual y símbolos además del color.

#### Scenario: Inserción conserva prefijo ordenado
- **GIVEN** una clave retirada del arreglo
- **WHEN** se desplazan elementos mayores
- **THEN** se visualizan clave, hueco, desplazamientos y prefijo que permanece ordenado

#### Scenario: HeapSort sincroniza dos representaciones
- **WHEN** HeapSort ejecuta `heapify` o extrae la raíz
- **THEN** arreglo y árbol heap muestran las mismas identidades, comparaciones y zona ya ordenada

#### Scenario: Radix muestra buckets
- **WHEN** Radix procesa una potencia decimal
- **THEN** muestra dígito activo, buckets 0–9, orden estable y tratamiento separado del signo

### Requirement: Representación correcta de números con signo
El módulo SHALL representar valores respecto de un eje cero, usando dirección para signo y longitud
para magnitud, y SHALL mantener etiquetas numéricas visibles.

#### Scenario: comparar menos ocho y ocho
- **GIVEN** el arreglo `[-8, 8]`
- **WHEN** se renderiza
- **THEN** `-8` se extiende a la izquierda, `8` a la derecha y ambos conservan su etiqueta

### Requirement: Controles completos y reversibles
El módulo SHALL ofrecer Preparar, Reproducir, Pausar, Inicio, Anterior, Siguiente, Final, Repetir,
Reiniciar ejecución y Restablecer datos, además de una barra de progreso navegable.

#### Scenario: pausa estable
- **GIVEN** una reproducción activa
- **WHEN** el estudiante pulsa Pausar
- **THEN** cursor, variables, pila, código y visualización permanecen en el mismo frame hasta continuar

#### Scenario: navegación arbitraria
- **WHEN** el estudiante mueve la barra a un frame anterior
- **THEN** se restaura exactamente el estado completo de ese frame sin recalcular otra historia

### Requirement: Evaluación formativa opcional
El módulo SHALL poder solicitar predicciones antes de eventos significativos y SHALL proporcionar
pistas y retroalimentación explicativa, sin impedir que el estudiante omita la pregunta.

#### Scenario: predecir un intercambio
- **GIVEN** una comparación aún no revelada
- **WHEN** el estudiante predice si habrá intercambio
- **THEN** el sistema registra la respuesta en la sesión, ejecuta el frame real y explica la diferencia

### Requirement: Comparación de algoritmos
El módulo SHALL permitir comparar dos algoritmos sobre copias idénticas de una entrada, reproducirlos
lado a lado y separar métricas observadas de propiedades teóricas.

#### Scenario: Burbuja frente a Inserción
- **GIVEN** una única entrada seleccionada
- **WHEN** se comparan Burbuja e Inserción
- **THEN** ambos reciben el mismo multiconjunto y se muestran pasos, comparaciones, movimientos, complejidad, estabilidad y memoria claramente diferenciados

### Requirement: Accesibilidad pedagógica
Todos los estados y controles SHALL ser operables por teclado, SHALL tener nombres accesibles y
SHALL comunicar comparación, intercambio, pivote, auxiliar y ordenado sin depender únicamente del color.

#### Scenario: recorrido sin ratón
- **WHEN** un estudiante navega sólo con teclado y reducción de movimiento activa
- **THEN** puede preparar, ejecutar, pausar, avanzar, retroceder y consultar explicaciones con foco visible y sin animación automática

### Requirement: Ayuda orientada a aprendizaje
La ayuda SHALL documentar para cada método objetivo, conocimientos previos, estrategia, invariante,
complejidad, estabilidad, memoria, casos representativos y errores conceptuales frecuentes.

#### Scenario: consultar ayuda de QuickSort
- **WHEN** el estudiante abre la ayuda contextual de QuickSort
- **THEN** encuentra pivote, partición, recursión, complejidades, peor caso y una entrada guiada reproducible
