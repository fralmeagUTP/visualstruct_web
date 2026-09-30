# Tareas

## 1. Contrato semántico y correcciones críticas

- [x] 1.1 Documentar y probar que la capacidad es fija; retirar toda afirmación o evento de resize/rehash inexistente.
- [x] 1.2 Alinear entrada, wrapper y TAD C para almacenar claves y valores enteros reales.
- [x] 1.3 Eliminar la sustitución oculta de claves y demostrar que claves distintas que colisionan conservan su identidad.
- [x] 1.4 Generar llamadas e historial `main` C17 compilables para entradas válidas.
- [x] 1.5 Definir objetivos, prerrequisitos y criterios de dominio para hashing, colisión, búsqueda, eliminación y memoria.

## 2. Contrato de frames e invariantes

- [x] 2.1 Publicar un esquema versionado de frame hash con fuente, fórmula, condición, variables, punteros, cadena, costo, memoria, estados e invariante.
- [x] 2.2 Emitir frames desde la ruta real del intérprete, incluyendo llamadas a `th_indice` y retornos.
- [x] 2.3 Eliminar inferencias frontend de bucket, búsqueda, comparación y enlaces.
- [x] 2.4 Validar ubicación, unicidad, cantidad, aciclicidad y ausencia de punteros colgantes en cada frame.
- [x] 2.5 Crear golden traces de índice, normalización, colisión, actualización, búsqueda, unlink, `free`, vaciado y destrucción.

## 3. Organización y progresión

- [x] 3.1 Dividir la pantalla en Preparar, Predecir, Ejecutar, Comprender, Relacionar con C, Comparar y Reflexionar.
- [x] 3.2 Mantener tabla y C simultáneos en escritorio y pestañas persistentes en móvil.
- [x] 3.3 Añadir panel redimensionable, índice de funciones y ocultación de documentación extensa.
- [x] 3.4 Implementar niveles Básico, Intermedio y Avanzado sobre una única traza.
- [x] 3.5 Conservar tabla, operación, entrada, nivel, fase y cursor al cambiar presentación.
- [x] 3.6 Separar reinicio de ejecución, vaciado y destrucción con confirmaciones apropiadas.

## 4. Función hash y representación

- [x] 4.1 Mostrar clave, capacidad, residuo C, normalización y bucket final.
- [x] 4.2 Representar arreglo de buckets, cabeceras, nodos, campos y `NULL` con direcciones lógicas estables.
- [x] 4.3 Mostrar ocupación, factor de carga, colisiones y longitud de cadenas con fórmulas explicadas.
- [x] 4.4 Añadir vista completa, solo ocupados y minimapa para capacidades grandes.
- [x] 4.5 Verificar claves cero, negativas, `INT_MIN` e `INT_MAX` sin divergencia C/Python.

## 5. Inserción y actualización

- [x] 5.1 Visualizar cálculo, bucket, recorrido para duplicados y comparaciones ejecutadas.
- [x] 5.2 Inserción nueva: mostrar `malloc`, comprobación de `NULL`, inicialización y enlace a cabecera.
- [x] 5.3 Colisión: mostrar cadena anterior/posterior y explicar por qué dos claves comparten bucket.
- [x] 5.4 Actualización: demostrar que no reserva nodo ni cambia cantidad, dirección o colisiones.
- [x] 5.5 Simular fallo de `malloc` de manera controlada y comprobar estado sin cambios.

## 6. Búsqueda, existencia y costo

- [x] 6.1 Mostrar cada valor de `actual`, comparación sustituida y avance por `siguiente`.
- [x] 6.2 Diferenciar búsqueda en cabecera, intermedia, final y ausente.
- [x] 6.3 Mostrar retorno, valor de salida y equivalencia de `contains` con `th_buscar`.
- [x] 6.4 Medir evaluaciones hash, comparaciones y nodos visitados sin confundirlas con tiempo real.
- [x] 6.5 Explicar mejor/promedio/peor caso y dependencia de distribución/factor de carga.

## 7. Eliminación y ciclo de vida

- [x] 7.1 Mostrar `actual` y `anterior` durante la búsqueda del nodo.
- [x] 7.2 Diferenciar eliminación de cabecera, nodo intermedio y clave ausente.
- [x] 7.3 Visualizar enlace sustituido, `free(actual)` y decremento de cantidad en orden causal.
- [x] 7.4 `th_vaciar`: liberar todos los nodos conservando arreglo y capacidad.
- [x] 7.5 `th_destruir`: liberar nodos y buckets, asignar `NULL` y dejar capacidad/cantidad en cero.
- [x] 7.6 Verificar que no se use ni muestre memoria liberada al avanzar o retroceder.

## 8. Ejemplos y aprendizaje activo

- [x] 8.1 Añadir ejemplos de vacío, capacidad 1, sin colisión y colisión múltiple.
- [x] 8.2 Añadir actualización, búsquedas por posición, ausente y eliminaciones por caso.
- [x] 8.3 Añadir clave cero, negativas, límites enteros, factor bajo/alto y fallo de memoria.
- [x] 8.4 Añadir predicciones de bucket, colisión, comparación, enlace, cantidad, `malloc` y `free`.
- [x] 8.5 Añadir pistas graduadas, retroalimentación, continuación sin responder y modo práctica.
- [x] 8.6 Guardar progreso conceptual solo durante la sesión y permitir reiniciarlo.

## 9. Reproducción

- [x] 9.1 Añadir Preparar, Reproducir, Pausar, Inicio, Anterior, Siguiente, Final y Repetir.
- [x] 9.2 Añadir progreso navegable con paso, función, fase, concepto, bucket, nodo y enlace.
- [x] 9.3 Sincronizar resaltado C, variables, punteros, tabla, consola e historial.
- [x] 9.4 Restaurar exactamente estado, cadena, memoria y salidas al retroceder.
- [x] 9.5 Garantizar equivalencia entre modo rápido y último frame paso a paso.

## 10. Comparación y métricas

- [x] 10.1 Comparar la misma entrada inmutable en capacidades 3, 7 y 17 sobre copias aisladas.
- [x] 10.2 Sincronizar por inserción y mostrar distribución, ocupación, colisiones y longitudes.
- [x] 10.3 Comparar costo observado de búsquedas exitosas y fallidas.
- [x] 10.4 Explicar que una muestra no demuestra complejidad promedio universal.

## 11. Ayuda, accesibilidad y exportación

- [x] 11.1 Reescribir ayuda con objetivo, estrategia, invariantes, memoria, complejidad, aplicaciones y errores frecuentes.
- [x] 11.2 Añadir glosario, guía docente y explicación explícita de capacidad fija.
- [x] 11.3 Añadir teclado completo, foco visible, anuncios, símbolos y movimiento reducido.
- [x] 11.4 Añadir exportación de captura y resumen estructurado de ejecución/aprendizaje.

## 12. Cierre QA

- [x] 12.1 Ejecutar contratos, golden traces, propiedades y equivalencia rápido/paso a paso.
- [x] 12.2 Compilar y ejecutar el `main` generado y el harness C17 con warnings como errores.
- [x] 12.3 Ejecutar Playwright de reproducción, práctica, comparación, teclado y responsividad.
- [x] 12.4 Ejecutar auditoría de accesibilidad, recorrido de usabilidad, suite completa y cobertura.
- [x] 12.5 Ejecutar ASan y UBSan para inserción, eliminación, vaciado y destrucción.
- [x] 12.6 Publicar informe antes/después, guía docente y validar OpenSpec en modo estricto.
