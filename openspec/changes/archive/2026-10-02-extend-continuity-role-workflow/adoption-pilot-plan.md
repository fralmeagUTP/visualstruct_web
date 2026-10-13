# Piloto real de documentación del arnés

Instrucción vigente: coordinación del hilo 01a0f0a7-80d9-722c-85ae-b3a1660740fc autoriza piloto mínimo real después de aceptación QA de correcciones. Proyecto D:\MisProyectos\Web_VisualEstruct; change extend-continuity-role-workflow; operación workflow.documentation-pilot; tarea documentation-quickstart. LOW.

Objetivo: añadir una guía breve de operación real del arnés con recuperación desde perfil persistido, comandos before/verify/after, resultados esperados, rechazo de evidencia/checkpoint obsoleto y entrega a QA. El documento existente largo obliga a reunir esos pasos; la guía reúne un recorrido verificable. Entregable: openspec/continuity/ROLE-WORKFLOW-QUICKSTART.md. No editar core, aplicación, auditoría, preview o evidencias independientes.

Transferencia secuencial explícita: workflow-minimum se conserva en perfil principal pero pasa active→pending, suspendida; no se cierra ni se pierde historia. implementation-profile-before.json conserva estado exacto anterior. Perfil propio adoption-pilot/workflow.json activa sólo documentation-quickstart y protege perfil principal/core/QA/auditoría. La tarea nueva no repite implementación; sólo crea guía nueva. El código aceptado es base inmutable, no dependencia formal marcada closed: core todavía carece de cierre/adopción, por eso dependencies=[] y no se inventa cierre para eludir un gate. La suspensión/creación es autorización vigente, no checkpoint histórico.

Roles: documentation ejecutado por el implementador actual como autor documental; quality pendiente de revisor independiente existente. specifications omitido porque reutiliza los requisitos actuales del arnés y escenarios definidos abajo, sin nuevo contrato; code omitido porque no modifica implementación; visual omitido porque es Markdown sin producto/UI renderizada ni cambio visual de aplicación. Contratos de esos roles se verificaron en fixtures (68tests), no ejecución real de esos roles en este piloto. No agentes reales ni APIs adicionales.

Criterios de aceptación documental:
- Un operador encuentra comando con IDs/profile explícitos y recupera objetivo/owner/rol/rutas/siguiente paso desde archivos en proceso nuevo.
- Comandos before, verify y after funcionan desde D:; close rechaza mientras falte QA independiente.
- La guía explica que un cambio legítimo invalida checkpoint/evidencia vieja, exige nueva lectura y fotografía, sin borrar historia.
- Enlaces locales válidos y límites explícitos: no autenticación, sandbox ni cierre global.
- Revisor distinto reproduce/inspecciona guía/evidencias/hashes actuales; autor no registra QA ficticia ni cierra tarea/cambio.

Escenarios: recuperación en proceso Python nuevo sin memoria del chat; modificación documental legítima invalida --checkpoint de antes; checkpoint fresco después de releer funciona; close sin QA conserva tarea abierta.
