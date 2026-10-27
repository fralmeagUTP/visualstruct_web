## ADDED Requirements

### Requirement: Resaltado persistente y seguro
Los lectores de código DEBEN aplicar la misma clasificación de tokens a la carga inicial y a actualizaciones de todas las familias, sin depender del título.

#### Scenario: Código reemplazado durante el uso
- **GIVEN** una operación, TAD, programa principal o ayuda con código
- **WHEN** cambia el contenido, la operación, el paso, el reset o su contenedor
- **THEN** se conserva el resaltado, el texto exacto, las filas, atributos de navegación y scroll, sin ejecutar markup del código.
