> Implementación autorizada por el usuario el 2026-09-30. La identificación de borrador y el gate siguientes conservan el contexto de revisión inicial; estado actual: auditoría en curso, sin cierre QA.

# Diseño de auditoría y simplificación contextual

**BORRADOR — pendiente de aprobación.** Este documento define el trabajo futuro; no autoriza iniciar servidor, pruebas ni implementación antes de aprobación explícita.

## Fuente, arquitectura y evidencia
Destino autorizado: `D:\MisProyectos\Web_VisualEstruct`, revisión local `ba53ba7c0bcebaf7a4938328ebf4c863f19eadab`. La base citada abajo identifica la inspección inicial del checkout de tarea; las pruebas futuras se ejecutarán sobre el destino y su revisión final registrada.
Base: commit `83c3c96fc17cabed85fddaf95e39b46bb19ff80b` del repositorio VisualStruct Web. Se inventariarán rutas, adapters, algoritmos, templates, JS, ayudas y descargas reales. El C canónico y sus harnesses instrumentados constituyen el oráculo semántico; el estado final no sustituye el contraste causal entre instrucciones, frames, consola y visualización.

Cada caso de la matriz enlazará requisito, datos, esperado/observado, revisión, herramientas y evidencia. Separar observación estática, captura aportada, ejecución automatizada y revisión manual. Registrar limitaciones de browser, compilador, sanitizadores y Doxygen sin convertir tareas bloqueadas en aprobadas.

## Menú común
## Sección 2: Visualizar y ejecutar
Convención propuesta: resaltado significa instrucción JUSTO EJECUTADA y frame posterior; conservar estado previo explícito. Frame inicial indica antes de ejecutar, sin atribuir efecto a una instrucción inexistente. Auditar todas las operaciones/TAD en vista individual y nodos enlazados aplicables, adelante/atrás. Contrastar línea/función/evento, condición/rama/iteración, llamada/retorno, variables, identidad/enlaces, reserva/liberación, antes/después, consola y ambas vistas. Retroceder restaura exactamente el frame anterior sin mutación ni mensajes futuros. Una línea sin cambio estructural conserva el estado y explica su efecto lógico. No inferir frames desde resultado final ni anticipar nodos/enlaces.

## Menú común (criterios)
Reutilizar el menú compartido existente y eliminar excepciones por estructura que generen desplazamiento horizontal o divergencias injustificadas. Usar reflujo natural de enlaces/herramientas a nuevas filas, conservando orden, estilo, foco y acceso. No resolver overflow escondiendo barras ni recortando enlaces. Las capturas del usuario orientan el diseño; sus distintos anchos no demuestran por sí solos una causa de regresión.

## Controles según operación, estado y modo
Pila es la referencia de interacción: preparación del método/datos y cuatro controles visibles contextuales en la captura (Ejecutar operación, Cerrar paso a paso, Paso anterior, Siguiente paso). No hay límite numérico universal. Cada TAD conserva acciones propias necesarias, justificadas por operación/estado/modo y probadas. No se eliminan capacidades por el conteo de elementos en la plantilla.

| Estado | Comportamiento previsto |
|---|---|
| Modo rápido | Ejecutar presenta el resultado final; navegación por pasos oculta y fuera de tabulación. |
| Paso a paso sin traza | Navegación visible pero ambos botones deshabilitados; mensaje que explique que falta ejecutar. |
| Inicio de traza | Anterior deshabilitado; Siguiente disponible si existe otro frame. |
| Frame intermedio | Navegación reversible, estado/línea C sincronizados. |
| Final de traza | Siguiente deshabilitado; Anterior disponible si existe frame previo. |
| Cambio a modo rápido | Muestra el resultado final de la misma ejecución, sin nueva mutación. |
| Nueva ejecución | Exactamente una operación contra estado actual; traza asociada a esa ejecución. |

La decisión sobre posición inicial al reactivar modo y destino de controles secundarios se revisará con el usuario. No modificar contratos de algoritmos o C para satisfacer la presentación.

## Documentación realmente entregada
Descargar C/H por las rutas allowlisted de ayuda; registrar respuesta, nombre, bytes y hash. Compilar el conjunto descargado con dependencias explícitas y generar Doxygen desde esos bytes. Revisar documentación por símbolo, memoria/errores/tipos/retornos y ejemplos, además de advertencias. Contrastar ayudas y manual con el flujo efectivo y el contrato C. Cualquier discrepancia grave del contrato requiere decisión antes de cambiar semántica.

## Reconciliación y fases
Usar `reconciliation.md` para decisiones y `commitment-inventory.md` como catálogo histórico. Revisar obligaciones por escenario; no reabrir automáticamente cambios archivados ni tratar su archivo como evidencia de cumplimiento. Tras aprobación: preview Desktop-FM, línea base, auditoría, correcciones UI/documentales autorizadas, verificación final y entrega. Sin deploy, merge, push, debilitamiento de tests ni cambios ajenos.
