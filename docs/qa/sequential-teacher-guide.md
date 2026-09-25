# Guía docente: estructuras secuenciales en C

## Propósito

Usar la visualización como evidencia de la ejecución real del C, no como sustituto del razonamiento sobre punteros. Cada actividad comienza con una predicción, continúa con inspección frame a frame y termina explicando el invariante.

## Secuencia de clase sugerida (90 minutos)

1. **Activación (10 min):** comparar pila y cola con `10, 20, 30`; pedir el siguiente valor antes de ejecutar.
2. **Modelado (20 min):** apilar y desapilar un elemento, siguiendo `malloc`, inicialización, enlace, reasignación de `TOP`, desconexión y `free`.
3. **Práctica guiada (20 min):** transición de cola única a vacía; justificar por qué cambian `FRONT` y `BACK`.
4. **Contraste (15 min):** cola frente a prioridad con empate; distinguir cadena de llegada y candidato seleccionado.
5. **Recorridos (15 min):** contrastar terminación lineal en `NULL` con vuelta a `HEAD` en lista circular.
6. **Cierre (10 min):** exportar el resumen y redactar qué invariante se conservó y qué error de memoria se evitó.

## Preguntas de comprensión

- ¿Qué puntero conserva el acceso al resto de la estructura antes de `free`?
- ¿Qué cambia cuando una cola pasa de un nodo a cero?
- ¿Por qué dos valores iguales pueden tener direcciones lógicas distintas?
- ¿Cómo termina un recorrido circular si nunca alcanza `NULL`?
- ¿Qué rama de una sublista debe permanecer idéntica después de modificar otra?

## Actividades evaluables

- Predecir cinco ramas y justificar al menos cuatro usando valores sustituidos.
- Reconstruir en papel los estados anterior y posterior de una reasignación.
- Detectar una referencia colgante en un ejemplo incorrecto y proponer el orden seguro.
- Comparar dos TAD con la misma entrada y formular una conclusión LIFO/FIFO, llegada/prioridad o lineal/circular.

## Rúbrica breve

- **4:** relaciona línea C, memoria, visual e invariante sin contradicciones.
- **3:** obtiene el estado correcto y explica la mayoría de los punteros.
- **2:** reconoce el resultado, pero omite pasos de memoria o control.
- **1:** describe solo la animación sin conectarla con el código C.
