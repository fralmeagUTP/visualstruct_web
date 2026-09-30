## ADDED Requirements

### Requirement: Ayuda fiel de tabla hash
La ayuda SHALL describir capacidad fija, tipos enteros, función hash, normalización, encadenamiento, memoria, complejidad, aplicaciones y errores frecuentes sin anunciar rehash inexistente.

#### Scenario: consultar política de capacidad
- **WHEN** el estudiante abre la ayuda
- **THEN** se explica que superar un factor de carga no cambia la capacidad en esta versión

### Requirement: Glosario y guía docente
La ayuda SHALL incluir glosario y una guía docente con predicciones, contraejemplos y criterios de evaluación.

#### Scenario: enseñar una colisión
- **WHEN** el docente usa claves congruentes módulo capacidad
- **THEN** la guía propone predecir índice, recorrer comparaciones y justificar el enlace final

### Requirement: Explicación de complejidad
La ayuda SHALL distinguir costo esperado de hashing, peor caso lineal y mediciones observadas en una cadena concreta.

#### Scenario: cadena larga
- **WHEN** varias claves colisionan
- **THEN** se explica que la búsqueda puede degradarse a O(n) y que una sola muestra no demuestra el promedio universal
