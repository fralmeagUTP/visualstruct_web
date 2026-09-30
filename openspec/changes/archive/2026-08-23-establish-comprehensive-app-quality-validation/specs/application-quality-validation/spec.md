# application-quality-validation Specification

## Purpose

Definir una campaña automatizable, completa y trazable que valide cada opción publicada de VisualStruct y su calidad funcional, didáctica y no funcional.

## ADDED Requirements

### Requirement: Inventario exhaustivo y verificable

El sistema de QA MUST generar un manifiesto versionado a partir de los contratos registrados de rutas, adaptadores, algoritmos, fases y controles de interfaz. Cada elemento publicado MUST tener al menos un caso de prueba trazable y un oráculo definido.

#### Scenario: nueva operación publicada

- **GIVEN** un adaptador registra una operación nueva
- **WHEN** se ejecuta la verificación de inventario
- **THEN** la verificación falla hasta que se asigne una prueba con datos y resultado esperado a dicha operación

#### Scenario: control visible sin cobertura E2E

- **GIVEN** un control de reproducción o aprendizaje está presente en la interfaz
- **WHEN** se genera el manifiesto
- **THEN** queda asociado a una prueba Playwright o se informa como cobertura faltante

### Requirement: Cobertura funcional de todos los módulos

La campaña MUST ejecutar todas las estructuras, operaciones, algoritmos, fases, comparadores, reinicios y ayudas expuestos por los módulos secuencial, jerárquico, grafos, hash y ordenamiento. Para cada opción MUST incluir, cuando aplique, estado vacío, normal, límite e inválido.

#### Scenario: algoritmo de ordenamiento registrado

- **GIVEN** un algoritmo incluido en el catálogo de ordenamiento
- **WHEN** se ejecuta la campaña
- **THEN** se prueba con entradas vacía, un elemento, repetidos, ordenada, inversa, negativa y de límite
- **AND** se comprueba que el resultado final está ordenado y coincide entre ejecución rápida y reproducción

#### Scenario: operación de grafo por fase

- **GIVEN** una operación permitida en una fase de grafos
- **WHEN** se ejecuta el caso asociado
- **THEN** la API acepta o rechaza la operación conforme a sus precondiciones
- **AND** la vista y la traza representan el resultado correspondiente

### Requirement: Fidelidad C, estado y traza

Para cada operación evaluada, la campaña MUST contrastar el resultado C o su harness equivalente, el estado de dominio/backend, el historial, la consola, los frames y la visualización. Un frame MUST representar solo una instrucción o rama efectivamente ejecutada.

#### Scenario: reproducción de una operación mutante

- **GIVEN** una operación mutante con traza disponible
- **WHEN** el usuario recorre desde Inicio hasta Final y luego retrocede
- **THEN** cada estado restaurado coincide con el frame correspondiente
- **AND** Final coincide con la ejecución rápida, el historial y la visualización

#### Scenario: llamada auxiliar del código C

- **GIVEN** una instrucción C que invoca una función auxiliar
- **WHEN** esa llamada es ejecutada
- **THEN** la traza identifica llamada, cuerpo ejecutado y retorno conforme al contrato didáctico del módulo

### Requirement: Calidad no funcional y reporte

La campaña MUST ejecutar accesibilidad, seguridad, rendimiento y compatibilidad definidos, y producir resultados reproducibles. Las dependencias ausentes de infraestructura MUST distinguirse de los fallos de producto.

#### Scenario: navegador E2E no instalado

- **GIVEN** un entorno sin navegador de Playwright
- **WHEN** se ejecuta la campaña E2E
- **THEN** el resultado se clasifica como bloqueo de infraestructura con comando de resolución
- **AND** no se clasifica como defecto funcional

#### Scenario: informe de hallazgo

- **GIVEN** una prueba no aprobada
- **WHEN** se publica el informe
- **THEN** incluye operación, entrada, esperado, observado, severidad, causa probable, ubicación y prueba/corrección recomendadas
- **AND** no modifica código de producción como consecuencia del hallazgo
