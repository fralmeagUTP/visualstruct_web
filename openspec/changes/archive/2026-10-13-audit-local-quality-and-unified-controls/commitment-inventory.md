# Reconciliación documental previa

BORRADOR. Clasificación documental; cumplimiento funcional todavía NO verificado.

Se leen íntegramente proposal, design, tasks y deltas de todos los cambios presentes. Se mantiene la semántica vigente; el nuevo patrón sustituye solamente la disposición/visibilidad de controles. Archivo no equivale a evidencia de cumplimiento.

## 2026-08-19-harden-trace-conformance-and-state

Fuente: `openspec/changes/archive/2026-08-19-harden-trace-conformance-and-state`.

MANTENER oráculo C, causalidad, conformidad, cobertura exhaustiva y regresiones; VERIFICAR evidencia contra revisión actual. No reabrir automáticamente remediaciones antiguas.

### Requisitos leídos: specs/application-shell/spec.md

- Configuración por variables de entorno
- Soporte de proxy reverso
- Jobs de calidad independientes
- Métricas y logs operativos sin datos sensibles

### Requisitos leídos: specs/c-code-interpreter/spec.md

- Contrato estable de pasos de traza
- Estrategias de traza por familia
- Conformidad observable entre C y Python
- Verificación de C estándar y memoria
- Compatibilidad durante la migración de trazas

### Requisitos leídos: specs/session-state/spec.md

- Reconstrucción de estado por replay
- Creación periódica de checkpoints
- Presupuesto de reconstrucción

## 2026-08-23-enhance-graph-structures-pedagogy

Fuente: `openspec/changes/archive/2026-08-23-enhance-graph-structures-pedagogy`.

MANTENER contenido didáctico, invariantes, operaciones, visualización causal y comparaciones aisladas; SUSTITUIR disposición incompatible de controles; VERIFICAR accesibilidad, compactación y pendientes sin reabrir todo el diseño.

### Requisitos leídos: specs/c-code-interpreter/spec.md

- Frame causal de grafos
- Ruta de grafos sin inferencia frontend
- Condiciones sustituidas de grafos
- Semántica de memoria de grafos
- Restauración causal completa

### Requisitos leídos: specs/graph-structures/spec.md

- Progresión pedagógica de grafos
- Construcción y representación causal
- Explicación causal de BFS
- Explicación causal de DFS
- Explicación causal de Dijkstra
- Explicación causal de Bellman-Ford
- Explicación causal de Prim
- Explicación causal de Kruskal y Union-Find
- Invariantes verificables de grafos
- Ejemplos guiados de grafos
- Comparaciones aisladas de algoritmos

### Requisitos leídos: specs/help-system/spec.md

- Ayuda pedagógica de grafos
- Glosario contextual de grafos
- Guía docente de grafos

### Requisitos leídos: specs/visual-playback-ui/spec.md

- Reproductor reversible de grafos
- Estructuras auxiliares visibles
- Predicción opcional de grafos
- Presentación adaptable de grafos
- Leyenda y accesibilidad de grafos
- Exportación de evidencia de grafos

## 2026-08-23-enhance-hash-table-pedagogy

Fuente: `openspec/changes/archive/2026-08-23-enhance-hash-table-pedagogy`.

MANTENER contenido didáctico, invariantes, operaciones, visualización causal y comparaciones aisladas; SUSTITUIR disposición incompatible de controles; VERIFICAR accesibilidad, compactación y pendientes sin reabrir todo el diseño.

### Requisitos leídos: specs/c-code-interpreter/spec.md

- Frame causal de tabla hash
- Llamadas auxiliares completas
- Ruta sin inferencia frontend
- Memoria y punteros causales
- Programa principal C17 válido
- Restauración exacta

### Requisitos leídos: specs/hash-table/spec.md

- Contrato fiel de tipos y capacidad
- Explicación de la función hash
- Representación de encadenamiento separado
- Inserción y actualización causales
- Búsqueda causal y costo observado
- Eliminación causal
- Ciclo de vida de la tabla
- Invariantes verificables
- Comparación aislada por capacidad

### Requisitos leídos: specs/help-system/spec.md

- Ayuda fiel de tabla hash
- Glosario y guía docente
- Explicación de complejidad

### Requisitos leídos: specs/visual-playback-ui/spec.md

- Flujo pedagógico de tabla hash
- Controles completos
- Código y tabla coordinados
- Aprendizaje activo
- Progresión por niveles
- Vista escalable
- Evidencia exportable y accesible

## 2026-08-23-enhance-hierarchical-structures-pedagogy

Fuente: `openspec/changes/archive/2026-08-23-enhance-hierarchical-structures-pedagogy`.

MANTENER contenido didáctico, invariantes, operaciones, visualización causal y comparaciones aisladas; SUSTITUIR disposición incompatible de controles; VERIFICAR accesibilidad, compactación y pendientes sin reabrir todo el diseño.

### Requisitos leídos: specs/c-code-interpreter/spec.md

- Frame causal jerárquico
- Ruta jerárquica sin inferencia frontend
- Semántica de memoria jerárquica
- Condiciones y valores derivados

### Requisitos leídos: specs/help-system/spec.md

- Ayuda pedagógica jerárquica
- Glosario jerárquico contextual
- Guía docente jerárquica

### Requisitos leídos: specs/hierarchical-structures/spec.md

- Progresión pedagógica jerárquica
- Invariantes jerárquicos verificables
- Explicación causal de ABB
- Explicación causal de rotaciones AVL
- Explicación causal rojo-negro
- Correspondencia arreglo-árbol del heap
- Ejemplos guiados jerárquicos
- Comparación jerárquica aislada

### Requisitos leídos: specs/visual-playback-ui/spec.md

- Reproductor reversible jerárquico
- Predicción jerárquica opcional
- Presentación adaptable jerárquica
- Accesibilidad de árboles y heap
- Exportación de evidencia jerárquica

## 2026-08-23-enhance-sequential-structures-pedagogy

Fuente: `openspec/changes/archive/2026-08-23-enhance-sequential-structures-pedagogy`.

MANTENER contenido didáctico, invariantes, operaciones, visualización causal y comparaciones aisladas; SUSTITUIR disposición incompatible de controles; VERIFICAR accesibilidad, compactación y pendientes sin reabrir todo el diseño.

### Requisitos leídos: specs/c-code-interpreter/spec.md

- Frame causal de estructura secuencial
- Prohibición de interpolación visual
- Trazabilidad de ciclos circulares

### Requisitos leídos: specs/help-system/spec.md

- Ayuda pedagógica por TAD secuencial
- Material docente secuencial
- Glosario de memoria y enlaces

### Requisitos leídos: specs/sequential-structures/spec.md

- Progresión pedagógica de los TAD secuenciales
- Invariantes secuenciales explícitos
- Semántica correcta de cola de prioridad
- Visualización de memoria y punteros
- Ejemplos guiados por estructura
- Comparación conceptual entre TAD
- Aprendizaje predictivo secuencial

### Requisitos leídos: specs/visual-playback-ui/spec.md

- Reproductor reversible para TAD secuenciales
- Presentación adaptable sin pérdida de contexto
- Accesibilidad de estados secuenciales

## 2026-08-23-enhance-sorting-pedagogy

Fuente: `openspec/changes/archive/2026-08-23-enhance-sorting-pedagogy`.

MANTENER contenido didáctico, invariantes, operaciones, visualización causal y comparaciones aisladas; SUSTITUIR disposición incompatible de controles; VERIFICAR accesibilidad, compactación y pendientes sin reabrir todo el diseño.

### Requisitos leídos: specs/help-system/spec.md

- Material docente del módulo de ordenamiento
- Glosario contextual

### Requisitos leídos: specs/sorting-visualizer/spec.md

- Progresión didáctica por niveles
- Explicación causal de cada frame
- Variables, punteros y pila de llamadas
- Visualización específica de estrategia e invariante
- Representación correcta de números con signo
- Controles completos y reversibles
- Evaluación formativa opcional
- Comparación de algoritmos
- Accesibilidad pedagógica
- Ayuda orientada a aprendizaje

### Requisitos leídos: specs/visual-playback-ui/spec.md

- Reproductor pedagógico con pausa y progreso
- Diseño adaptable sin pérdida de contexto

## 2026-08-23-establish-comprehensive-app-quality-validation

Fuente: `openspec/changes/archive/2026-08-23-establish-comprehensive-app-quality-validation`.

MANTENER oráculo C, causalidad, conformidad, cobertura exhaustiva y regresiones; VERIFICAR evidencia contra revisión actual. No reabrir automáticamente remediaciones antiguas.

### Requisitos leídos: specs/application-quality-validation/spec.md

- Inventario exhaustivo y verificable
- Cobertura funcional de todos los módulos
- Fidelidad C, estado y traza
- Calidad no funcional y reporte

## 2026-08-23-remediate-didactic-c-trace-fidelity

Fuente: `openspec/changes/archive/2026-08-23-remediate-didactic-c-trace-fidelity`.

MANTENER oráculo C, causalidad, conformidad, cobertura exhaustiva y regresiones; VERIFICAR evidencia contra revisión actual. No reabrir automáticamente remediaciones antiguas.

### Requisitos leídos: specs/didactic-conformance-remediation/spec.md

- Un único contrato ejecutable por operación
- Aritmética y memoria definidas en los límites
- Contrato coherente para grafos
- Contrato coherente para hash y secuenciales
- Estado visual causado por eventos C
- Traza continua y fuente verificable
- Consola derivada de ejecución
- Cierre verificable de los hallazgos QA

## 2026-08-23-validate-and-harden-sorting-module

Fuente: `openspec/changes/archive/2026-08-23-validate-and-harden-sorting-module`.

MANTENER oráculo C, causalidad, conformidad, cobertura exhaustiva y regresiones; VERIFICAR evidencia contra revisión actual. No reabrir automáticamente remediaciones antiguas.

### Requisitos leídos: specs/sorting-visualizer/spec.md

- Creación de arreglos
- Selección y ejecución de algoritmos
- Navegación por cursor paso a paso
- Trazas didácticas de ordenamiento

## 2026-09-25-extend-sequential-structural-visualizations

Fuente: `openspec/changes/archive/2026-09-25-extend-sequential-structural-visualizations`.

MANTENER contenido didáctico, invariantes, operaciones, visualización causal y comparaciones aisladas; SUSTITUIR disposición incompatible de controles; VERIFICAR accesibilidad, compactación y pendientes sin reabrir todo el diseño.

### Requisitos leídos: specs/sequential-structural-visualization/spec.md

- Dos modos conservados por estructura secuencial
- Diagrama fiel a cada modelo de enlace
- Animación estructural por operación
- Sublista conserva un carril independiente por padre
- Matriz semántica documentada para operaciones visibles

### Requisitos leídos: specs/sequential-workspace-consistency/spec.md

- Espacio de trabajo secuencial coherente
- Resultados como panel único plegable
- Estructura del TAD siempre abierta dentro de resultados

## 2026-09-25-organize-help-and-download-tad-sources

Fuente: `openspec/changes/archive/2026-09-25-organize-help-and-download-tad-sources`.

MANTENER ayudas y descarga completa de C/H; AMPLIAR auditoría a bytes HTTP, Doxygen y manual efectivo.

### Requisitos leídos: specs/help-system/spec.md

- Descarga de fuente canónica por TAD
- Dependencias transparentes
- Descargas restringidas
- Ayuda coherente con el flujo actual

## 2026-09-25-reorganize-graph-learning-workspace

Fuente: `openspec/changes/archive/2026-09-25-reorganize-graph-learning-workspace`.

MANTENER contenido didáctico, invariantes, operaciones, visualización causal y comparaciones aisladas; SUSTITUIR disposición incompatible de controles; VERIFICAR accesibilidad, compactación y pendientes sin reabrir todo el diseño.

### Requisitos leídos: specs/graph-learning-workspace/spec.md

- Flujo coherente en todas las fases de Grafos
- Visualización fiel del frame de algoritmo
- Código C vertical y correlacionado
- Resultados agrupados y plegables

## 2026-09-25-reorganize-hash-learning-workspace

Fuente: `openspec/changes/archive/2026-09-25-reorganize-hash-learning-workspace`.

MANTENER contenido didáctico, invariantes, operaciones, visualización causal y comparaciones aisladas; SUSTITUIR disposición incompatible de controles; VERIFICAR accesibilidad, compactación y pendientes sin reabrir todo el diseño.

### Requisitos leídos: specs/hash-learning-workspace/spec.md

- Flujo hash unificado y compacto
- Representación fiel del encadenamiento separado
- Código C vertical y resultados agrupados
- Overflow contenido por bucket

## 2026-09-25-reorganize-hierarchical-learning-workspace

Fuente: `openspec/changes/archive/2026-09-25-reorganize-hierarchical-learning-workspace`.

MANTENER contenido didáctico, invariantes, operaciones, visualización causal y comparaciones aisladas; SUSTITUIR disposición incompatible de controles; VERIFICAR accesibilidad, compactación y pendientes sin reabrir todo el diseño.

### Requisitos leídos: specs/hierarchical-learning-workspace/spec.md

- Flujo jerárquico unificado y numerado
- Ejecución reducida a acciones comprensibles
- Código y estado jerárquico correlacionados
- Navegación de funciones C vertical y legible
- Visualización acorde con el tipo jerárquico
- Resultados como una única unidad plegable
- Simplificación sin alterar algoritmos

## 2026-09-25-reorganize-sorting-learning-workspace

Fuente: `openspec/changes/archive/2026-09-25-reorganize-sorting-learning-workspace`.

MANTENER contenido didáctico, invariantes, operaciones, visualización causal y comparaciones aisladas; SUSTITUIR disposición incompatible de controles; VERIFICAR accesibilidad, compactación y pendientes sin reabrir todo el diseño.

### Requisitos leídos: specs/sorting-learning-workspace/spec.md

- Flujo compacto de Ordenamiento
- Controles de ejecución simplificados
- Estado de ordenamiento y código C correlacionados
- Representación específica del algoritmo
- Comprensión y resultados plegables
- Código C sin overflow global
- Simplificación sin eliminar capacidades de servicio

## 2026-09-25-separate-sequential-execution-and-playback

Fuente: `openspec/changes/archive/2026-09-25-separate-sequential-execution-and-playback`.

MANTENER ejecución mutante exactamente una vez y navegación no mutante; SUSTITUIR disposición de botones principales por patrón simplificado.

### Requisitos leídos: specs/sequential-structures/spec.md

- Ejecución explícita por operación secuencial
- Reproducción secuencial sin efectos de dominio
- Trazas asociadas a una ejecución concreta

### Requisitos leídos: specs/visual-playback-ui/spec.md

- Controles separados de ejecutar y reproducir en secuenciales
- Navegación habilitada solo para trazas preparadas
- Estado canónico visible después de ejecutar

## audit-didactic-c-trace-fidelity

Fuente: `openspec/changes/audit-didactic-c-trace-fidelity`.

MANTENER oráculo C, causalidad, conformidad, cobertura exhaustiva y regresiones; VERIFICAR evidencia contra revisión actual. No reabrir automáticamente remediaciones antiguas.

### Requisitos leídos: specs/didactic-conformance-qa/spec.md

- Inventario exhaustivo y trazable
- Código C como oráculo semántico
- Comparación paso a paso entre capas
- Causalidad entre ejecución C y visualización del TAD
- Fidelidad del flujo de control
- Temporales, punteros y consola didáctica
- Invariantes específicos por familia
- Controles reproducibles y equivalencia de modos
- Casos normales, límites e inválidos
- Informe QA estructurado
- Correcciones separadas de la auditoría

### Pendientes documentales: tasks.md

- 2.1 Extender los harnesses de los 13 TAD para emitir eventos por instrucción relevante y estados canónicos intermedios.
- 2.3 Instrumentar identidad lógica, enlaces de punteros, reservas, reasignaciones y liberaciones sin exponer direcciones como contrato.
- 2.4 Capturar `printf`, valores de retorno, errores y estado final con un protocolo JSON reproducible.
- 2.5 Compilar y ejecutar los harnesses con C17 estricto, ASan y UBSan.

## redesign-stack-learning-workspace

Fuente: `openspec/changes/redesign-stack-learning-workspace`.

MANTENER espacio compacto, accesibilidad, estado/C simultáneos y contenido progresivo; SUSTITUIR botones/scroll; VERIFICAR tareas pendientes antes de extender.

### Requisitos leídos: specs/sequential-structures/spec.md

- Piloto visual limitado a Pila

### Requisitos leídos: specs/visual-playback-ui/spec.md

- Laboratorio compacto de Pila
- Divulgación progresiva de detalles de Pila
- Secuencia pedagógica y paneles plegables de Pila

### Pendientes documentales: tasks.md

- 1.1 Medir el recorrido actual de Pila en escritorio, tableta y móvil: insertar, ejecutar, reproducir, desapilar y consultar C.
- 1.3 Establecer los límites de alto, ancho, scroll interno, teclado y contraste para el piloto.
- 3.2 Implementar la composición de tableta sin ocultar la operación ni los controles principales.
- 3.3 Mantener en móvil las pestañas Estado/Código y una zona de control accesible sin superposición.
- 4.1 Probar insertar, duplicar, desapilar, preparar, reproducir, pausar y avanzar paso a paso en Pila.
- 4.2 Confirmar que estado visual y línea C resaltada continúan sincronizados tras el rediseño.
- 4.3 Ejecutar pruebas de teclado, foco, contraste, navegación interna y reducción de movimiento.
- 4.4 Ejecutar Playwright con capturas en escritorio, tableta y móvil; validar que la acción principal no requiere scroll de página.
- 4.5 Presentar el piloto de Pila para aprobación antes de extenderlo a las otras estructuras.
- 4.6 Verificar que abrir o cerrar paneles no altere la traza, el estado de la pila ni la navegación por teclado.

## Specs actuales

Cada requisito actual se incorpora como obligación de verificar, salvo sustituciones explícitas de visual-playback-ui incluidas en el delta.

### application-shell

- Application Factory
- Configuración por variables de entorno
- Soporte de proxy reverso
- Página de inicio
- Health check
- Servido de assets
- Entry points de ejecución
- Jobs de calidad independientes
- Métricas y logs operativos sin datos sensibles

### c-code-interpreter

- Extracción de funciones C desde docs/tads_C
- Mapeo operación → función C por estructura
- Extracción de la estructura del TAD
- Operaciones compuestas y derivadas
- Fallback a pseudocódigo
- Filtrado de líneas ejecutables
- Respeto del flujo de control
- Estados visuales progresivos alineados a la mutación
- Fases visuales de operaciones mutantes
- Pasos de depuración de árboles
- Consola printf e historial técnico
- Coherencia historial–estado final
- Contrato estable de pasos de traza
- Estrategias de traza por familia
- Conformidad observable entre C y Python
- Verificación de C estándar y memoria
- Compatibilidad durante la migración de trazas

### graph-learning-workspace

- Flujo coherente en todas las fases de Grafos
- Visualización fiel del frame de algoritmo
- Código C vertical y correlacionado
- Resultados agrupados y plegables

### graph-structures

- Fases del módulo de grafos
- Operaciones de construcción
- Validación de entradas de grafo
- Estado visual del grafo
- Algoritmos de recorrido
- Algoritmos de camino mínimo
- Árbol de expansión mínima
- Reinicio del grafo

### hash-learning-workspace

- Flujo hash unificado y compacto
- Representación fiel del encadenamiento separado
- Código C vertical y resultados agrupados
- Overflow contenido por bucket

### hash-table

- Endpoints del módulo hash
- Validación de entradas de texto
- Operaciones del TAD
- Resolución de colisiones por encadenamiento
- Rehash por factor de carga
- Estadísticas de la tabla
- Estado visual por buckets

### help-system

- Manual de usuario
- Índices de ayuda por módulo
- Ayuda por estructura enriquecida con código C
- Introducciones y explicaciones didácticas
- Símbolos C en la lista de operaciones
- Cobertura de ayuda para todos los módulos
- Descarga de fuente canónica por TAD
- Dependencias transparentes
- Descargas restringidas
- Ayuda coherente con el flujo actual

### hierarchical-learning-workspace

- Flujo jerárquico unificado y numerado
- Ejecución reducida a acciones comprensibles
- Código y estado jerárquico correlacionados
- Navegación de funciones C vertical y legible
- Visualización acorde con el tipo jerárquico
- Resultados como una única unidad plegable
- Simplificación sin alterar algoritmos

### hierarchical-structures

- Catálogo y endpoints del módulo
- Estado visual de árbol binario
- Estado visual de montículo
- Invariantes de ABB
- Balanceo AVL
- Invariantes Rojo-Negro
- Propiedad de heap
- Recorridos y consultas

### sequential-structural-visualization

- Dos modos conservados por estructura secuencial
- Diagrama fiel a cada modelo de enlace
- Animación estructural por operación
- Sublista conserva un carril independiente por padre
- Matriz semántica documentada para operaciones visibles

### sequential-structures

- Catálogo de estructuras secuenciales
- Página interactiva de estructura
- Ejecución de operaciones
- Validación del cuerpo de la petición
- Validación de entradas enteras
- Errores didácticos de dominio
- Registro de historial solo en mutaciones
- Reinicio de estructura
- Contrato de adapters secuenciales
- Operaciones por estructura
- Ejecución explícita por operación secuencial
- Reproducción secuencial sin efectos de dominio
- Trazas asociadas a una ejecución concreta

### sequential-workspace-consistency

- Espacio de trabajo secuencial coherente
- Resultados como panel único plegable
- Estructura del TAD siempre abierta dentro de resultados

### session-state

- Backend de sesión server-side
- Seguridad de la cookie de sesión
- Historial de operaciones por estructura
- Reconstrucción de estado por replay
- Reinicio de estructura
- Aislamiento entre usuarios
- Creación periódica de checkpoints
- Presupuesto de reconstrucción

### sorting-learning-workspace

- Flujo compacto de Ordenamiento
- Controles de ejecución simplificados
- Estado de ordenamiento y código C correlacionados
- Representación específica del algoritmo
- Comprensión y resultados plegables
- Código C sin overflow global
- Simplificación sin eliminar capacidades de servicio

### sorting-visualizer

- Páginas del módulo
- Creación de arreglos
- Selección y ejecución de algoritmos
- Navegación por cursor paso a paso
- Consulta y reinicio de estado
- Contrato de errores del API
- Trazas didácticas de ordenamiento

### visual-playback-ui

- Modo intérprete conmutado
- Disposición de controles de simulación
- Resaltado sincronizado código–animación
- Clasificación de la acción actual en grafos
- Estado final limpio en secuenciales
- Equivalencia de modo rápido en grafos
- Visibilidad de detalles técnicos
- Paneles didácticos por operación
- Exportación de la vista como JPG
- Renderizado de estructuras
- Consola printf y deduplicación visual
- Escape de contenido dinámico
- Controles separados de ejecutar y reproducir en secuenciales
- Navegación habilitada solo para trazas preparadas
- Estado canónico visible después de ejecutar
