# Guía breve de operación del arnés cerrado

El mínimo técnico y el piloto documental están aceptados y archivados. Los comandos del piloto antiguo son historia: no usarlos como asignación vigente. [Protocolo](ROLE-WORKFLOW.md), [perfil base](role-workflow.json), [plantilla](role-task-template.json), [mapa de evidencia histórica](role-workflow-archive.json).

## Preparar una operación real nueva
1. Leer AGENTS.md, instrucciones OpenSpec y continuidad; confirmar raíz D:\MisProyectos\Web_VisualEstruct e instrucción vigente.
2. Registrar nuevo change, operación/binding y tarea con rol/owner/alcance/approval/requisitos/base/siguiente paso. Copiar perfil base; sustituir placeholders y task-template. Conservar tareas cerradas pertinentes. Un perfil vacío no autoriza trabajo.
3. Desde raíz usar CLI con los IDs registrados, --workflow-config de ese change, --task actual y --gate before. Añadir --assignment-id sólo si el change tiene assignment_source; comprobar coincidencia con nueva instrucción.
4. Ejecutar trabajo permitido y checks reales. Registrar evidencia UTC/hashes; usar --gate verify. Cierre exige revisor genuino distinto: --gate close. Gate verde no cambia state ni archiva automáticamente.
5. Registrar cierre autorizado; --phase after --gate after informa. Antes de archivo consolidar deltas verificados, separar runtime permanente, conservar fotografías y revisar rutas.

## Recuperación y cambios
CLI recupera objective/role/owner/rutas/dependencias/next_step desde archivos en procesos nuevos; no recupera chats. --checkpoint foto.json rechaza configuración/fuentes cambiadas (Stale checkpoint). Después de cambio legítimo releer/replanificar, repetir verificaciones afectadas y emitir foto fresca, conservando resultados anteriores. before no autoriza rutas adicionales; after no autoriza reapertura. LOW por defecto.

## Historial aceptado y siguiente alcance
El mapa identifica archive_prefix y input_overrides de las guías aprobadas. Evaluar evidencia fechada contra esas copias exactas; no contra guías permanentes reescritas. El checker del piloto se conserva como fuente histórica: contiene IDs/rutas de aquella fase y no es comando actual de adopción tras archivo. El archivo conserva sus resultados reales y QA; no reejecutar scripts de registro de aceptación.

El piloto posterior de requirements/generador/HTML/CSS/teclado/responsive y QA independiente ya se ejecutó y aceptó en su alcance finito. Muestra permanente: examples/local-task; uso práctico: USAGE.md. No existe siguiente tarea asignada ni motor automático por ese cierre. Uso rutinario requiere instrucción y registro nuevos.

No autentica permisos/revisores ni impone aislamiento OS/reserva global entre perfiles. No modificar auditoría activa ni preview5051. Sin agentes reales/API extra, motor autónomo, publicación/merge/despliegue.
