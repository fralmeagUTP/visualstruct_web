## ADDED Requirements

### Requirement: Predicción causal con estado anterior visible
Durante una pregunta pendiente, el sistema MUST conservar visible e inalterado el gráfico del estado anterior al evento objetivo. MUST NOT revelar el resultado del evento hasta responder u omitir. En modo práctica MUST ocultar código, ayudas narrativas, semántica y consola/historial que puedan anticipar el resultado.

#### Scenario: pregunta sobre cambio real
- **GIVEN** una publicación de raíz con estados anterior y posterior diferentes
- **WHEN** se abre la pregunta antes de ese evento
- **THEN** el gráfico y cursor permanecen en el anterior y las ayudas están ocultas

#### Scenario: responder
- **WHEN** se responde la pregunta pendiente
- **THEN** se muestra exactamente el estado posterior y se registra un único intento

#### Scenario: omitir
- **WHEN** se omite la pregunta pendiente
- **THEN** se muestra exactamente el estado posterior sin registrar intento

#### Scenario: activación duplicada inmediata
- **WHEN** responder u omitir recibe dos activaciones inmediatas sobre la misma pregunta
- **THEN** el avance y la puntuación ocurren como máximo una vez
