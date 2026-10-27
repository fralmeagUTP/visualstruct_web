# Diseño propuesto

## Base real y reutilización
Fuentes: AGENTS.md, openspec/AGENTS.md, continuity/README.md y ROLE-WORKFLOW.md; scripts/check_session_continuity.py y role_workflow.py; informe archivado agent-openspec-enforcement-report.md. Continuidad verifica contexto documental; roles evalúan contratos cuando se les pasa configuración. Ambos son de solo lectura, no ejecutan checks ni autentican personas. Los pilotos históricos prueban contratos acotados, no cinco agentes autónomos. El perfil permanente tiene tasks vacío y placeholders; no se activará ni usará como perfil de producto.

Estado funcional preservado: cinco etapas y reproducción manual aprobadas; C1 12/12 finito; inventario 375 original, 369 activo/vinculado, 8 retiros NOT_PASS y 2 añadidos. Sin LSan/universalidad/garantía temporal para todos los grafos. Ninguna de estas brechas se reabre aquí. project.md y notas anteriores de continuidad son fotografías históricas cuando discrepan con las decisiones finales.

## Arquitectura y puntos controlados
1. Registro: un change propuesto con IDs estables, asignación vigente, tareas y referencias exactas a requisitos y escenarios. Bootstrap documental mínimo precede a before; no otorga autorización para código. Requisitos vigentes se enlazan con ruta+título/identificador estable y hash. Cuando no existe delta funcional, se declara por qué.
2. Entrada: un comando explícito reutilizaría check_session_continuity y, solo donde aplique, role_workflow. Comprueba aprobación real referenciada, dependencias y propietario. La coordinación real mantiene escritor único y transferencias. No reserva globalmente archivos.
3. Verificación: futuros controles leerían el conjunto de archivos tocados respecto de una base declarada, incluidos archivos sin seguimiento; cada ruta debe tener tarea/disposición. Sin base fiable se informa alcance incompleto y no se declara cobertura total. Checks ejecutados por runners autorizados producen logs/exit/UTC/hashes; el evaluador los valida, no los fabrica ni los ejecuta automáticamente.
4. Cierre: verifica evidencia vigente, revisión y documentación; separa cierre técnico de archivo. Se exige delta verificado o disposición documental/sin cambio de comportamiento. Captura after antes de mover el change. El cierre local termina con consolidación validada y mapa/retirada de bindings; un fallo deja cierre pendiente de consolidación con evidencia, no falso archivo completado.
5. Publicación: CI sobre el diff de una PR validaría trazabilidad, requisitos, disposición, evidencia publicable y coherencia del canon/archivo. Activación y branch protection requieren aprobación y permisos del repositorio. Sin regla obligatoria en la plataforma, un job/hook por sí solo no impide merge. Push directo o herramientas fuera del comando siguen siendo posibles; solo políticas del servidor en superficies configuradas pueden exigir checks. No hay publicación automática.

## Datos propuestos y fuente única
Reutilizar assignment_source, tasks y los campos de tarea role_workflow (requirements/base/deliverables/documentation/owner/checks/decisions). Un manifiesto complementario, si se necesita, indexa referencias: change, task, capability, requirement, scenario, disposition, touched_paths, approval_ref, review_ref y evidence_ref. No replica contadores de avance ni inventa estados independientes. Su versión/esquema y necesidad se confirman al comenzar fase 1 mediante análisis del código existente. Un artefacto por gate incluye contexto/base, hashes y resultados con procedencia; hash protege integridad, no autenticidad.

Tipos de disposición: comportamiento nuevo/modificado con delta; documental sin cambio funcional; retirado con motivo/impacto; sustituido con predecesor y alcance; generado con fuente/comando; evidencia solo local con clasificación pública verificable. Ningún retired equivale a PASS. Evitar coincidencias de nombres como sustituto de vínculos.

## Roles y revisión
Specifications y documentation aplican a cualquier change. Code aplica a cambios ejecutables/configuración. Visual aplica a impacto de UI/accesibilidad; no exigir navegador a documentación pura. Quality independiente aplica al cierre de controles/producto y al piloto de enforcement. Una misma persona puede ejercer specifications/code/visual secuencialmente con trazabilidad; no afirmar que son agentes separados. QA de cierre debe ser realmente distinta del autor. Si no está disponible, conservar estado pendiente; no inventar revisor. Revisión documental de bajo riesgo puede ser del usuario/coordinador con excepción explícita de QA técnica. Validación sintáctica jamás basta para el cierre de implementación.

## Adopción y excepciones
Fase inicial observa solo cambios nuevos o rutas tocadas, registra faltantes y no bloquea por archivos históricos intocados. Revisar una línea en un archivo histórico no autoriza exigir migración de todo el corpus: delimitar delta y deuda heredada. Después piloto aislado optativo sin app/preview/sesiones; medir falsos positivos y recuperar fallos. Activar bloqueo solo tras aprobación separada y evidencia del piloto. Rollback desactiva la superficie nueva y mantiene reglas manuales existentes/historial; no reescribe casos para obtener verde.

Excepción: ID, control omitido, motivo, riesgo, rutas/requisitos, propietario, autorización real referenciada, expiración por fecha o tarea y checks compensatorios. Debe ser visible en el gate y CI; vencida no permite cierre/publicación. No exceptuar permiso de publicación, integridad de originales, evidencia fabricada ni reapertura sin autorización. Urgencia documentada puede diferir un check de bajo riesgo con aceptación explícita; el cierre queda limitado a ese alcance. Datos/sesiones locales no se suben para satisfacer CI: clasificación y evidencia derivada sin contenido privado; si CI no puede verificar el hecho, reporta límite y exige revisión local genuina.

## Pruebas propuestas, no ejecutadas
Fixtures temporales aisladas para positivos y negativos de cada escenario del delta. Pruebas de integración de continuidad/roles con registros sintéticos legítimos; nunca copiar logs como ejecución nueva. Probar diff/base fiable y desconocida, archivos sin seguimiento, snapshots obsoletos, excepciones, no mutación del evaluador, errores de archivo/consolidación y adopción histórica. Un piloto documental y otro de control técnico autorizados por separado; revisar reporte legible y QA real distinta. Tests de CI/hook se simulan offline antes de cualquier activación remota. Suites del producto solo si una implementación posterior afecta producto y están autorizadas; no son necesarias para esta entrega.

## Protección y recuperación
Manifestar SHA de C originales y de las 3904 sesiones originales sin exponer su contenido. Usar fixtures en temporal y logs fuera del almacenamiento de sesiones; no arrancar/reiniciar preview5051 como piloto. Cualquier alteración inesperada suspende el bloque, conserva evidencia y requiere análisis; no restaurar con reset ni borrar logs automáticamente. Fuentes generadas quedan separadas. Consolidación fallida conserva deltas, outputs y mapa parcial; reintento basado en lectura nueva, no checkpoint obsoleto. Archivo administrativo sin delta usa --skip-specs y validación documental; cambios funcionales jamás usan ese camino para eludir consolidación.

## Decisiones para visto bueno
D1: aprobar este alcance y comenzar fases 1–2 (diseño detallado/observación) después de revisión, sin activar bloqueo inicialmente. Recomendación: sí, previa autorización explícita.
D2: superficie inicial: comandos locales explícitos + piloto; CI de PR después. Hook local optativo, no requisito de seguridad. Recomendada; alternativa comenzar solo con documentación/CLI y diferir CI.
D3: revisión: QA independiente para cambios técnicos/activación; revisión usuario/coordinador para documentación pura con excepción registrada. Confirmar disponibilidad de revisor real.
D4: activación obligatoria en CI/branch protection y repositorio/ramas objetivo: autorización separada en fase 4, con permisos confirmados; no decidir ni activar ahora.
No pedir al usuario elegir detalles internos de esquema/regex ni volver a aprobar decisiones funcionales archivadas. Lanzamiento autónomo de agentes no forma parte de estas decisiones.

## Estimación orientativa
Supuestos: un escritor técnico, reutilización de scripts sin rediseño, Python/OpenSpec local disponibles, revisión independiente en 1–2 días y repositorio remoto con CI/permisos disponibles solo cuando se autorice. Rangos son horas de trabajo, no promesa ni porcentaje de tareas.

| Fase | Entregable y salida | Esfuerzo orientativo |
|---|---|---|
| 1 | Contrato/datos finales, análisis compatibilidad y matriz de aceptación | 4–8 h |
| 2 | Comprobación explícita en modo observación y pruebas aisladas | 8–16 h |
| 3 | Piloto, QA independiente, falsos positivos y recuperación | 6–12 h |
| 4 | Integración CI propuesta, simulación y activación solo aprobada | 6–12 h |
| 5 | Guías, verificación final, consolidación y archivo | 3–6 h |

Total 27–54 h (aprox. 4–8 jornadas técnicas de 7 h), más espera de revisión/permisos. Sin CI, diferir sus 6–12 h. Si exige orquestación automática, firma de evidencia o bloqueo universal, requiere propuesta/estimación independiente. Refinar después de fase 1; las cifras no autorizan ejecución.
