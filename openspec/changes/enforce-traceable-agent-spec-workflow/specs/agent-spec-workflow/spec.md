## ADDED Requirements

### Requirement: R1 Registro y autorización vigente
El flujo SHALL exigir change activo, tarea, asignación vigente, propietario, alcance y referencia a autorización real en los puntos de ejecución controlados; el bootstrap documental SHALL distinguir propuesta de implementación.

#### Scenario: Registro autorizado
- **GIVEN** una tarea técnica registrada con autorización coincidente
- **WHEN** se solicita entrada controlada
- **THEN** permite evaluar el trabajo dentro del alcance, sin autorizar publicación

#### Scenario: Propuesta sin autorización técnica
- **GIVEN** una propuesta válida sin visto bueno
- **WHEN** se intenta ejecutar implementación
- **THEN** rechaza la entrada e identifica aprobación ausente; permite la entrega documental autorizada

#### Scenario: Identidad contradictoria
- **GIVEN** asignación y operación diferentes
- **WHEN** se evalúa entrada
- **THEN** rechaza sin escoger ID histórico ni cambiarlo para eludir cierre

### Requirement: R2 Vínculos de requisitos y rutas
El flujo SHALL vincular cada tarea y ruta tocada a requisitos/escenarios vigentes o a disposición documental justificada, usando base explícita y conjunto de cambios que incluya archivos sin seguimiento.

#### Scenario: Cambio cubierto
- **GIVEN** diff fiable y requisito/escenario exactos
- **WHEN** se verifica trazabilidad
- **THEN** acepta el vínculo y muestra fuente/hash

#### Scenario: Ruta sin vínculo
- **GIVEN** archivo nuevo sin seguimiento fuera del alcance
- **WHEN** se verifica trazabilidad
- **THEN** reporta ruta y rechaza cierre obligatorio

#### Scenario: Base desconocida
- **GIVEN** no hay base fiable de comparación
- **WHEN** se verifica
- **THEN** declara cobertura incompleta y no certifica todo el repositorio

### Requirement: R3 Roles aplicables y revisión genuina
El flujo SHALL reutilizar contratos activables por alcance y registrar transferencia de propiedad; SHALL distinguir roles de agentes/procesos y exigir QA realmente distinta para cierre técnico y activación.

#### Scenario: Documentación pura
- **GIVEN** cambio documental sin UI/código y revisión autorizada
- **WHEN** se determina matriz
- **THEN** no exige navegador ni implementación; justifica roles no aplicables

#### Scenario: Autor revisa su código
- **GIVEN** author y reviewer coinciden
- **WHEN** se solicita cierre técnico
- **THEN** rechaza aun con todos los checks verdes

#### Scenario: Transferencia registrada
- **GIVEN** propietario entrega rutas/contexto y sucesor autorizado acepta
- **WHEN** se solicita entrada
- **THEN** admite un escritor; no afirma reserva global ni lanzamiento de agentes

### Requirement: R4 Evidencia ejecutada y vigente
El flujo SHALL exigir ejecución real, procedencia, resultado, exit_code, UTC y hashes de entradas/entregables para los checks aplicables; SHALL preservar logs previos y declarar límites de autenticación.

#### Scenario: Verificación reproducible
- **GIVEN** log real vigente y check aprobado
- **WHEN** se evalúa verify
- **THEN** acepta exclusivamente el alcance comprobado

#### Scenario: Fuente cambió
- **GIVEN** prueba anterior pasó pero hash actual difiere
- **WHEN** se solicita cierre
- **THEN** rechaza evidencia obsoleta y exige revisión/verificación pertinente nueva

#### Scenario: Check no ejecutado
- **GIVEN** casilla marcada o log histórico reutilizado como nuevo
- **WHEN** se verifica
- **THEN** rechaza la admisión y preserva el registro histórico

### Requirement: R5 Cierre y consolidación separadas
El flujo SHALL separar aceptación técnica, after, consolidación, archivo y publicación; SHALL impedir declarar cierre completo de un cambio funcional sin deltas verificados consolidados y mapa/bindings coherentes.

#### Scenario: Archivo funcional válido
- **GIVEN** implementación aceptada y deltas completos
- **WHEN** se autoriza archivo local
- **THEN** consolida, valida canon y conserva historia; no publica

#### Scenario: Archivo fallido
- **GIVEN** OpenSpec rechaza escenario perdido o conflicto
- **WHEN** se intenta archivar
- **THEN** conserva logs/deltas y declara consolidación pendiente sin PASS ni borrar evidencia

#### Scenario: Propuesta sintácticamente válida
- **GIVEN** solo propuesta y validación strict correcta
- **WHEN** se intenta cerrar implementación
- **THEN** no acepta funcionalidad ni archiva ni actualiza canon

### Requirement: R6 Disposiciones documentales y evolución
El flujo SHALL distinguir cambios documentales, generados, retirados y sustituidos mediante motivos y enlaces a predecesores; SHALL preservar decisiones históricas y no convertir retiros en PASS.

#### Scenario: Archivo documental
- **GIVEN** cambio sin delta funcional justificado y revisado
- **WHEN** se autoriza archivo
- **THEN** permite ruta documental --skip-specs con validación de enlaces, sin delta artificial

#### Scenario: Requisito sustituido
- **GIVEN** decisión aprobada y sucesor de alcance distinto
- **WHEN** se actualizan vínculos
- **THEN** conserva original y referencia vigente sin reabrir implícitamente

#### Scenario: Retiro sin motivo
- **GIVEN** requisito desaparece del delta o retired presentado como passed
- **WHEN** se evalúa cierre
- **THEN** rechaza y exige disposición explícita

### Requirement: R7 Adopción gradual y deuda histórica
El flujo SHALL comenzar en modo observación sin controles nuevos activos, limitarse a cambios/rutas autorizados y pasar a bloqueo solo tras piloto aceptado y autorización separada.

#### Scenario: Deuda intocada
- **GIVEN** archivo histórico fuera del cambio nuevo
- **WHEN** se ejecuta observación
- **THEN** informa deuda separada sin bloquear por migración global

#### Scenario: Piloto aceptado
- **GIVEN** positivos/negativos y QA real documentados
- **WHEN** usuario autoriza superficie obligatoria
- **THEN** activa solo esa superficie y registra límites/rollback

#### Scenario: Bloqueo prematuro
- **GIVEN** no hay aceptación ni permiso de activación
- **WHEN** se solicita modo obligatorio
- **THEN** rechaza activación, conserva propuesta y no modifica CI/hooks

### Requirement: R8 Excepciones acotadas
El flujo SHALL exigir excepción autorizada con ID, motivo/riesgo, control, alcance, propietario, expiración y compensación; SHALL hacerla visible y no permitir excepcionar integridad de originales, evidencia fabricada, permiso de publicación o reapertura no autorizada.

#### Scenario: Excepción vigente
- **GIVEN** revisión documental alternativa autorizada y acotada
- **WHEN** se evalúa gate
- **THEN** registra alcance/compensación sin certificar controles omitidos

#### Scenario: Excepción caducada
- **GIVEN** fecha/tarea de expiración alcanzada
- **WHEN** se pide cierre/publicación
- **THEN** rechaza y solicita renovación o ejecución pendiente

#### Scenario: Excepción inválida
- **GIVEN** se pretende permitir modificar sesiones originales
- **WHEN** se verifica autorización
- **THEN** rechaza la excepción sin tocar originales

### Requirement: R9 Publicación y límites de CI hooks
El flujo SHALL proponer checks CI de trazabilidad/cierre para diff de PR y exigir autorización separada para configurarlos o publicar; SHALL distinguir job, hook optativo y branch protection, sin prometer intercepción universal.

#### Scenario: PR conforme en superficie protegida
- **GIVEN** job requerido configurado por autorización y evidencia válida
- **WHEN** se evalúa merge
- **THEN** la política de plataforma exige resultado; el reporte identifica configuración real

#### Scenario: Check ausente o fallido
- **GIVEN** rama protegida exige job y este no pasa
- **WHEN** se intenta merge
- **THEN** política configurada bloquea; sin protección se informa que job solo no garantiza bloqueo

#### Scenario: Evidencia solo local
- **GIVEN** sesiones/logs no publicables clasificados
- **WHEN** CI valida manifiesto público
- **THEN** no demanda datos privados ni fixtures falsos; declara hechos no verificables y revisión local requerida

### Requirement: R10 Preservación y efectos limitados
El flujo SHALL usar fixtures aisladas y comprobar manifiestos de originales C/sesiones; SHALL mantener preview5051 y cuatro expedientes archivados sin cambios para el piloto, y no ejecutar campañas, lanzar agentes, publicar o restaurar automáticamente por evaluar un gate.

#### Scenario: Evaluación sin efectos
- **GIVEN** fixture aislada y hashes originales registrados
- **WHEN** se evalúan gates positivos/negativos
- **THEN** no cambia producto/sesiones/C/preview ni inicia agentes

#### Scenario: Alteración inesperada
- **GIVEN** hash protegido difiere
- **WHEN** se verifica preservación
- **THEN** suspende el bloque y conserva evidencia sin reset ni borrado automático

#### Scenario: Archivo movido
- **GIVEN** change cerrado pasó al archivo con mapa vigente
- **WHEN** se solicita trabajo con binding antiguo
- **THEN** rechaza continuación; exige asignación nueva legítima sin reabrir historial
