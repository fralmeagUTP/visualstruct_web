## ADDED Requirements

### Requirement: Flujo pedagógico de tabla hash
La pantalla SHALL organizarse en Preparar, Predecir, Ejecutar, Comprender, Relacionar con C, Comparar y Reflexionar.

#### Scenario: completar una inserción
- **WHEN** el estudiante prepara y reproduce una inserción
- **THEN** puede predecir el bucket, observar código/tabla, explicar el enlace y reflexionar sobre colisión e invariante

### Requirement: Controles completos
La reproducción SHALL ofrecer Preparar, Reproducir, Pausar, Inicio, Anterior, Siguiente, Final y Repetir, más progreso navegable.

#### Scenario: navegar a un frame
- **WHEN** se mueve el progreso
- **THEN** se restauran paso, función, concepto, bucket, nodo, enlace, consola y visualización

### Requirement: Código y tabla coordinados
En escritorio SHALL permanecer visibles simultáneamente y en móvil SHALL existir pestañas persistentes sin pérdida de contexto.

#### Scenario: cambiar a móvil
- **WHEN** cambia el viewport durante una colisión
- **THEN** cursor, cadena, punteros y nivel permanecen intactos al alternar Tabla/Código

### Requirement: Aprendizaje activo
El módulo SHALL ofrecer predicciones de índice, colisión, comparación, enlace, cantidad, reserva y liberación, con pistas y continuación sin respuesta.

#### Scenario: modo práctica
- **WHEN** está activo antes del siguiente frame
- **THEN** el resultado permanece oculto hasta responder o continuar explícitamente

### Requirement: Progresión por niveles
Básico, Intermedio y Avanzado SHALL usar la misma traza y cambiar únicamente la explicación presentada.

#### Scenario: cambiar de nivel
- **WHEN** se cambia de Básico a Avanzado
- **THEN** se conservan operación, entrada y cursor y aparecen punteros, memoria, expresión C y complejidad

### Requirement: Vista escalable
Las capacidades grandes SHALL ofrecer vista completa, solo ocupados y minimapa sin ocultar el bucket activo.

#### Scenario: capacidad grande
- **WHEN** se activa solo ocupados
- **THEN** se indica cuántos buckets vacíos se omiten y el bucket activo permanece visible

### Requirement: Evidencia exportable y accesible
La pantalla SHALL permitir exportar captura y resumen estructurado, y SHALL ofrecer foco visible, teclado, anuncios, símbolos y movimiento reducido.

#### Scenario: exportar resumen
- **WHEN** termina una búsqueda
- **THEN** el archivo incluye entrada, índice, cadena, comparaciones, resultado, invariante y progreso conceptual
