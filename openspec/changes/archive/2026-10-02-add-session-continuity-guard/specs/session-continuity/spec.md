## ADDED Requirements

### Requirement: Recuperación explícita
El agente SHALL confirmar proyecto/change/operación y leer instrucciones/propuesta/diseño/deltas/tasks/evidencia antes de trabajo dependiente.
#### Scenario: Proyecto o bloque incorrecto
- **WHEN** cwd difiere del proyecto o bloque carece de binding revisado
- **THEN** guarda falla sin inferir siguiente tarea

### Requirement: Estado derivado y checkpoint
La guarda SHALL ser solo lectura sin aplicación; SHALL derivar conteos/cierres desde fuentes con UTC/hashes y detectar cambios/checkpoints obsoletos.
#### Scenario: Fuente modificada
- **WHEN** checkpoint anterior difiere de fuentes vigentes
- **THEN** falla y exige releer/replanificar conservando historial
#### Scenario: Evidencia ausente
- **WHEN** binding refiere archivo inexistente o fuera de raíz
- **THEN** falla sin declarar cierre
#### Scenario: Avance parcial
- **WHEN** operaciones se cierran dentro de tareas globales pendientes
- **THEN** muestra conteo separado de cierres/alcance sin porcentaje de tiempo

### Requirement: Reapertura persistente
Antes de trabajo nuevo, un bloque con cierre declarado SHALL exigir razón/decisión con ID exacto. La fase after SHALL permitir informar cierre sin reabrirlo y SHALL indicar propósito exclusivo de reporte. La guarda SHALL declarar límites de autenticidad y verificación funcional.
#### Scenario: Repetir búsqueda cerrada
- **WHEN** se selecciona bloque cerrado en fase before sin decisión
- **THEN** falla y conserva trabajo registrado
#### Scenario: Regresión nueva documentada
- **GIVEN** decisión contiene ID y motivo exactos
- **WHEN** se solicita reapertura con ambos argumentos
- **THEN** checkpoint incluye decisión/hashes para revisar alcance

### Requirement: Persistencia y consolidación
Solicitudes SHALL quedar en proposal/specs/design/tasks/evidence. Después de verificación/decisión SHALL consolidarse deltas y archivarse contexto. Conflictos SHALL resolverse explícitamente.
#### Scenario: Hash contradictorio
- **WHEN** spec canónica y archivo discrepan
- **THEN** registra diferencia/decisión pendiente sin elegir silenciosamente ni afirmar consolidación completa

### Requirement: Adopción con cambios legítimos
La guarda SHALL comprobar que el change sigue activo y SHALL derivar casillas desde fuente única. SHALL permitir agregar logs sin bloquear trabajo válido: fuentes registradas modificadas requieren releer y emitir fotografía fresca; fuentes nuevas no registradas no invalidan fotografía.
#### Scenario: Finalizar bloque
- **WHEN** evidencia y tareas registran cierre tras implementación
- **THEN** after informa cierre sin autorizar repetición; before exige decisión para reapertura
#### Scenario: Log adicional
- **WHEN** se añade log no referenciado sin cambiar fuentes registradas
- **THEN** checkpoint previo conserva validez documental para sus fuentes
#### Scenario: Log referenciado actualizado
- **WHEN** se amplía evidencia registrada legítimamente
- **THEN** foto anterior se declara obsoleta y lectura/foto fresca permite continuar
#### Scenario: Cambio archivado
- **WHEN** directorio del change activo se traslada al archivo
- **THEN** guarda impide continuar con binding activo anterior

### Requirement: Identidad de asignación vigente
Para cambios con asignación registrada, la guarda SHALL exigir ID actual y coincidencia de change/operación con instrucción persistida antes de evaluar cierre o reapertura. El agente SHALL contrastar mensaje nuevo con registro y SHALL actualizarlo si la instrucción nueva autorizada lo sustituye. Checkpoints históricos SHALL NOT sustituir asignación.
#### Scenario: Eliminar RN frente a búsqueda histórica
- **GIVEN** asignación actual red-black.delete
- **WHEN** se invoca guarda para búsquedas Lista/Circular, incluso con motivo de reapertura
- **THEN** falla por contradicción de asignación e indica seguir instrucción vigente, sin pedir reaprobar instrucción sustituida
#### Scenario: Instrucción nueva
- **WHEN** nuevo registro autorizado cambia ID o alcance
- **THEN** ID/fotografía anteriores fallan; lectura de nuevo registro y checkpoint fresco permite continuar
#### Scenario: Identificador ausente
- **WHEN** existe assignment_source pero invocación omite ID
- **THEN** no lo infiere desde checkpoint ni documentación histórica y falla

### Requirement: Controles recuperables después del archivo
Runtime, bootstrap, índice y asignaciones SHALL usar rutas estables independientes del change activo que los introdujo. Al archivar SHALL consolidarse specs y comprobar enlaces operativos y guardas.
#### Scenario: Archivar el arnés
- **WHEN** el change del arnés se mueve a changes/archive
- **THEN** AGENTS y guarda siguen encontrando índice/asignación/specs, y registros de changes activos siguen operables
#### Scenario: Intento de trabajar el change archivado
- **WHEN** se invoca el ID antiguo como change activo
- **THEN** falla sin reabrirlo implícitamente y conserva historia
