## ADDED Requirements
### Requirement: Extremos presentes al publicar un arco
La inserción de arco DEBE conservar que sus dos extremos existen incluso cuando falla una reserva; una reserva fallida puede conservar vértices nuevos según el contrato parcial existente.
#### Scenario: Falla reserva de un extremo
- **GIVEN** grafo válido sin uno o ambos extremos
- **WHEN** malloc falla al crear un extremo
- **THEN** no se crea un arco con extremo ausente y toda reserva viva permanece alcanzable para limpieza.
#### Scenario: Ruta normal y traza
- **GIVEN** reservas exitosas
- **WHEN** se inserta, actualiza o crea un autobucle
- **THEN** se conserva el resultado normal y la traza ejecuta las comprobaciones reales del nuevo cuerpo C.
