# V3 RN aprobado: validación completa en TAD C/H y aplicación

Nueva delegación del coordinador01a0fe61-3104-743a-b032-bcc289ad80cd,2026-10-03, para registrar contrato y aceptación documental, sin implementar.

Evidencia textual trasladada: asistente «En Rojo-Negro falta decidir qué tan completa será la validación del árbol. Yo recomiendo validar todas sus reglas, incluida la altura negra y los enlaces. Para eso tendría que modificar el validador en C y ajustar visualización, pruebas y documentación. ¿Autorizas esa ampliación del validador?». Usuario «Sí, claro, la idea es que valide las reglas de los árboles rojinegros». Usuario «Sí, eso es ... lo más importante para mí».

Decisión: V3 de la propuesta técnica. Validar las cinco reglas clásicas y orden ABB estricto, padres, ciclos y nodos compartidos sobre objetos vivos. Añadir rbt_validar al TAD C/H y alinear aplicación/traza/main/documentación. Excepción C/H ACOTADA a tad_rojo_negro.c/.h para función pública/helpers/documentación de esa validación; no modificar algoritmos Insertar/Eliminar, otros TAD ni contratos numéricos.

Alcance actual de este autor: documentos/specs de este change y registro propio. Dueño técnico único01a0fc18-c146-7460-b83f-47a215e630cf priorizará implementación RN después del checkpoint actual Encolar; no se cambia asignación/checkpoint del auditor. No función implementada ni prueba funcional nueva.

La conversación se recibe por delegación con citas; no se afirma autenticación independiente. Grafos/Dijkstra permanecen pendientes: esta aprobación no selecciona sus opciones. Decisión producto resuelta, hallazgo funcional no corregido aún. Evidencias anteriores y matriz C1 fechada permanecen intactas.

## Aclaración de aceptación sobre rotaciones

Delegación adicional vigente: usuario confirmó raíz negra/altura negra y preguntó por casos de rotación. Se incorpora aceptación de dos primitivas, LL/LR/RR/RL+recoloreo y cuatro casos clásicos de eliminación con espejos cuando son alcanzables en el algoritmo real. Esto no demuestra defecto previo de rotaciones ni autoriza cambiarlas para ajustarse a una plantilla. Invariantes tras cada operación; reutilizar evidencia cerrada, sin prometer exhaustividad.
