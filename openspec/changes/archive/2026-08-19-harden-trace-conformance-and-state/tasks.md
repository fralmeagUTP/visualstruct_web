# Tareas

## 1. Línea base y caracterización

- [x] 1.1 Marcar las pruebas E2E con `pytest.mark.e2e` y documentar comandos de instalación y ejecución de Chromium.
- [x] 1.2 Crear fixtures golden para trazas representativas de las cinco familias.
- [x] 1.3 Registrar una línea base de replay con historiales de 1, 50, 150 y 300 operaciones.
- [x] 1.4 Añadir ADR de decisiones: motor por estrategias, estado canónico y checkpoints.

## 2. Motor modular de trazas

- [x] 2.1 Definir y probar el modelo `TraceStep` y sus invariantes.
- [x] 2.2 Implementar `TraceEngine`, `TraceStrategy` y `TraceStrategyRegistry`.
- [x] 2.3 Extraer la estrategia de estructuras secuenciales y conservar las trazas golden.
- [x] 2.4 Extraer las estrategias de árboles, hash, grafos y ordenamiento.
  - [x] Delegar límites de mutación y estados pre-rotación/pre-fix-up a `TreeTraceStrategy`.
  - [x] Extraer metadatos de recorrido, rebalanceo y fix-up de árboles.
  - [x] Extraer estados y metadatos de hash.
  - [x] Extraer estados y metadatos de grafos.
  - [x] Integrar la estrategia de ordenamiento con el contrato común.
- [x] 2.5 Añadir el adaptador de compatibilidad con el esquema JSON actual.
- [x] 2.6 Eliminar del servicio central las reglas ya migradas y dejarlo como fachada de orquestación.
  - [x] Retirar límites y utilidades migradas de secuenciales, montículo, árboles, grafos y hash.
  - [x] Extraer planificación semántica de control de flujo y algoritmos de grafo.
    - [x] Extraer selección de líneas ejecutables y ramas defensivas a `ControlFlowPlanner`.
    - [x] Extraer evaluación de condiciones y estimación de iteraciones genéricas.
    - [x] Extraer normalización, tamaño de estado y límite determinista de pasos.
    - [x] Extraer expansión genérica de bucles y condicionales.
    - [x] Extraer planificadores de BFS, DFS, Dijkstra, Bellman-Ford y Kruskal.
      - [x] BFS.
      - [x] DFS.
      - [x] Dijkstra.
      - [x] Bellman-Ford.
      - [x] Kruskal.
    - [x] Extraer metadata de depuración y control visual a `GraphTracePlanner`.
  - [x] Reducir `ExecutionTraceService` a una fachada sin reglas específicas de TAD.
    - [x] Extraer planificadores recursivos de inserción y eliminación ABB.
    - [x] Extraer planificador de inserción AVL.
    - [x] Extraer planificador de inserción rojinegra.
    - [x] Extraer recorridos, métricas, extremos y limpieza de árboles.
- [x] 2.7 Verificar que cada archivo nuevo mantenga responsabilidad cohesiva y que ningún nuevo módulo supere 1.000 líneas sin ADR.

## 3. Conformidad C↔Python

- [x] 3.1 Definir el estado canónico y las invariantes de cada TAD.
- [x] 3.2 Crear harnesses C no interactivos para los 13 TAD.
  - [x] Definir protocolo, utilidades seguras y manifiesto de los 13 TAD.
  - [x] Implementar y compilar el harness de pila.
  - [x] Implementar y compilar los harnesses de cola y ordenamiento.
  - [x] Implementar y compilar los harnesses de lista enlazada y lista circular.
  - [x] Implementar y compilar los harnesses de cola de prioridad y sublista.
  - [x] Implementar y compilar los harnesses de montículo binario y ABB.
  - [x] Implementar y compilar los harnesses de AVL y rojinegro.
  - [x] Implementar los harnesses de grafo y tabla hash.
- [x] 3.3 Crear el runner Python que ejecute escenarios equivalentes y normalice resultados.
  - [x] Implementar compilación, ejecución aislada y comparación estructurada.
  - [x] Integrar escenarios equivalentes de pila y cola.
  - [x] Integrar los seis TAD secuenciales.
  - [x] Integrar montículo, ABB, AVL y rojinegro.
  - [x] Registrar traductores para grafo, hash y ordenamiento.
- [x] 3.4 Añadir casos deterministas de éxito, error y límites para cada TAD.
  - [x] Crear catálogo reproducible con las tres categorías para los 13 TAD.
  - [x] Ejecutar casos de éxito y límites válidos mediante el runner diferencial.
  - [x] Comparar bilateralmente los resultados de error C/Python.
- [x] 3.5 Añadir secuencias generadas con semillas reproducibles y reducción del caso fallido.
- [x] 3.6 Integrar compilación C17 con warnings como error en CI.
- [x] 3.7 Integrar AddressSanitizer y UndefinedBehaviorSanitizer en CI Linux.

## 4. Checkpoints y rendimiento

- [x] 4.1 Añadir contrato explícito de exportación/importación de estado en adapters.
- [x] 4.2 Implementar checkpoint versionado, checksum y validación de compatibilidad.
- [x] 4.3 Migrar automáticamente historiales sin checkpoint mediante replay completo inicial.
- [x] 4.4 Añadir configuración del intervalo y feature flag de checkpoints.
- [x] 4.5 Probar corrupción, versión desconocida, truncado y fallback seguro.
- [x] 4.6 Medir y cumplir p95 de reconstrucción menor a 200 ms para 300 operaciones en el entorno de referencia.

## 5. Cobertura y calidad

- [x] 5.1 Elevar a 85% la cobertura de `domain/sorting/tad_ordenamiento.py`.
- [x] 5.2 Elevar a 85% la cobertura de `domain/graph/tad_grafo.py`.
- [x] 5.3 Elevar a 85% la cobertura de `domain/hash/tad_tabla_hash.py` y montículo jerárquico.
- [x] 5.4 Configurar gates por componente sin reducir el umbral global actual.
- [x] 5.5 Ejecutar unitarias/integración, E2E, conformidad y sanitizers como jobs separados.

## 6. Configuración y observabilidad

- [x] 6.1 Introducir `APP_ENV` y validación de configuración de producción.
- [x] 6.2 Rechazar la clave de desarrollo y cookies inseguras en producción.
- [x] 6.3 Hacer explícita la cantidad de proxies confiables antes de aplicar `ProxyFix`.
- [x] 6.4 Añadir métricas y logs estructurados del motor de trazas y reconstrucción.
- [x] 6.5 Actualizar README, guía de despliegue y reporte de pruebas.

## 7. Verificación y cierre

- [x] 7.1 Ejecutar `pytest -q` con Chromium instalado y obtener cero fallos.
- [x] 7.2 Confirmar que la cobertura global no baja de 83% y los componentes críticos alcanzan 85%.
- [x] 7.3 Ejecutar al menos 1.000 secuencias diferenciales por familia sin divergencias no justificadas.
- [x] 7.4 Verificar los 13 TAD con C17, warnings estrictos y sanitizers.
- [x] 7.5 Confirmar compatibilidad de sesiones creadas antes de los checkpoints.
- [x] 7.6 Revisar y archivar la propuesta actualizando las specs base tras el despliegue.
