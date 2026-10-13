## ADDED Requirements
### Requirement: Ejemplo local de contexto persistido
El ejemplo SHALL generar HTML desde un perfil y task explícitos, mostrando objetivo, rol, propietario, rutas y siguiente paso como fotografía sin certificar aprobación ni ejecutar herramientas.
#### Scenario: recuperar tarea real
- **WHEN** se genera el ejemplo con perfil/task registrados
- **THEN** los valores visibles coinciden con esa tarea persistida
#### Scenario: contenido con etiquetas
- **WHEN** una tarea contiene texto HTML o un cierre de script
- **THEN** se muestra como texto sin ejecutar contenido inyectado
#### Scenario: tarea desconocida
- **WHEN** el ID no existe en el perfil
- **THEN** el generador falla antes de producir una entrega válida
### Requirement: Lectura accesible sin red
La muestra SHALL funcionar sólo con archivos locales, conservar lectura sin overflow horizontal a 390 y 1280 píxeles y ofrecer foco visible, enlace de salto y control operable por teclado para mostrar JSON.
#### Scenario: lector con teclado
- **WHEN** usa Tab y Enter en el control JSON
- **THEN** el foco es visible, aria-expanded cambia y el contenido se puede consultar
#### Scenario: viewport estrecho
- **WHEN** abre la muestra a 390 píxeles
- **THEN** los textos/rutas se ajustan sin perder contenido ni necesitar scroll horizontal de página
#### Scenario: fuera de línea
- **WHEN** se abre el HTML file:// con red externa bloqueada
- **THEN** texto, estilo y control funcionan sin petición HTTP/HTTPS
