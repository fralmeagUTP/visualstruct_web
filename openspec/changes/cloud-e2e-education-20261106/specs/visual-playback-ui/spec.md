# Reconciliación educativa, 2026-11-06

## MODIFIED Requirements

### Requirement: Predicción futura con navegación manual
ABB, AVL, RedBlack y BinaryHeap MUST predecir la siguiente condición C realmente evaluada posterior al cursor. Las opciones MUST ser Verdadero/Falso conforme al resultado booleano registrado. Responder u omitir MUST revelar evidencia rotulada con el paso objetivo futuro, sin mover el cursor, cambiar el estado visible, mutar la traza ni volver a ejecutar la operación. La misma condición MUST permanecer marcada como resuelta hasta avanzar manualmente. Los intentos MUST contarse como máximo una vez por objetivo de la misma traza; volver atrás, reabrir el panel, repetir u omitir no vuelve a puntuar. Reiniciar métricas no rehabilita puntos del mismo objetivo.

#### Scenario: ayudas progresivas conservadas
- GIVEN una condición futura disponible
- WHEN se solicitan pistas sucesivas
- THEN se conservan tres pistas diferentes y progresivas, sin navegar ni puntuar
- AND la cuarta solicitud conserva la tercera pista
- AND un objetivo diferente o una traza nueva reinicia la progresión de pistas

#### Scenario: responder sin avanzar
- GIVEN un estado previo y una condición futura aún no ejecutada
- WHEN se responde o se omite
- THEN se revela la evidencia registrada del paso futuro con identificación explícita
- AND el estado actual, el cursor y el código activo permanecen iguales
- AND no se dispara un POST de la operación principal

### Requirement: Práctica antes de la condición
Práctica MUST conservar visible el estado previo y detener Siguiente y ArrowRight inmediatamente antes de una condición pendiente. Resolver u omitir esa condición MUST permitir avanzar manualmente una sola instrucción, sin desbloquear otras condiciones. No se usa máscara global ni avance automático. ArrowRight MUST navegar sólo una traza ya disponible, sin iniciar preparación ni POST.

### Requirement: Nivel explicativo en Relacionar con código
Se conserva la ubicación canónica del nivel y sus guías en Relacionar con código. MUST existir un solo control, con etiqueta y referencias ARIA válidas, cuyo valor y funcionamiento sobrevivan a navegación, reapertura y cambios de vista. Los ejemplos siguen en Preparar; Predecir y Comparar permanecen en disclosures nativos de Comprender. Las cinco etapas se conservan.

#### Scenario: explicación completa accesible
- GIVEN un frame disponible
- WHEN se selecciona Básico, Intermedio o Avanzado
- THEN la guía y narración corresponden al nivel y al frame
- AND el resumen conciso puede usar detalles nativos para conservar la explicación completa
- AND no cambian cursor, estado, código activo ni número de POST

## Procedencia y límites

La spec canónica visual-playback-ui:259–265 fija ubicación/capacidades y ausencia de ejecución accidental. VS-21/UI018, del change cloud-pedagogical-repair-20261027, fija siguiente evento relevante, evidencia y no doble puntuación. La decisión técnica de 2026-11-06 conserva tres pistas y cursor quieto, confirma estado previo visible con bloqueo manual y restituye ubicación Nivel. No se atribuye aceptación retroactiva a dos pistas/seek. La validación de screenshots escritorio/estrecho queda pendiente de CI; JSDOM no constituye revisión visual.
