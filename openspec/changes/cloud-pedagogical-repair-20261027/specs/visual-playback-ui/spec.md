<!-- En esta especificación, ejecución C en la aplicación designa reproducción por el intérprete/simulador de instrucciones de la fuente C. La ejecución nativa ocurre sólo en pruebas QA separadas. -->
## ADDED Requirements
### Requirement: Coherencia de reproducción pedagógica
La ejecución DEBE mantener sincronizados código, variables, explicación y estado visual, con navegación reversible y resultado final equivalente al modo normal.
#### Scenario: Repetición y retroceso
- **GIVEN** una operación válida
- **WHEN** se avanza, retrocede, reinicia y repite
- **THEN** se recupera el paso correcto sin duplicar la operación ni perder el estado de sesión.

### Requirement: Comprender contextual y conciso
La ayuda principal DEBE explicar de forma breve, sencilla y por puntos la operación seleccionada y el paso vigente; la referencia extensa permanece accesible separadamente.
#### Scenario: Antes de insertar en ABB
- **GIVEN** ABB vacío con Insertar seleccionado y ninguna ejecución preparada
- **WHEN** se muestra Comprender
- **THEN** se explica la inserción y su regla, sin enumerar todos los otros métodos ni paneles técnicos vacíos.
#### Scenario: Cambio de operación o paso
- **GIVEN** una operación o traza visible
- **WHEN** se selecciona otra operación o se avanza/retrocede
- **THEN** la explicación corresponde al contexto vigente y no conserva detalles de otro método.

### Requirement: Vista estable para clase
En escritorio el código activo y la estructura DEBEN ser legibles simultáneamente. El avance automático no debe desplazar el documento; el seguimiento se limita al contenedor necesario. Las líneas C pueden ajustarse visualmente sin modificar la fuente descargada.
#### Scenario: Entrada y salida de helper
- **GIVEN** código y gráfico visibles
- **WHEN** la traza entra a un helper, modifica nodos y retorna
- **THEN** se conserva el scroll del documento y se ve la instrucción completa y el cambio de estructura.

### Requirement: Resultado y stdout fieles
Los mensajes administrativos y valores retornados DEBEN distinguirse de stdout C. La consola conserva repeticiones y saltos reales según contrato explícito de eventos o snapshots.
#### Scenario: Consulta que no imprime en C
- **GIVEN** búsqueda de posiciones o hijos existentes
- **WHEN** se ejecuta normal
- **THEN** el resultado aparece separado de una consola C sin salida.
#### Scenario: Navegar un resultado
- **GIVEN** una consulta paso a paso
- **WHEN** se llega al retorno final y luego se retrocede
- **THEN** se publica y se vuelve a ocultar el resultado según el paso, sin exponerlo anticipadamente.

### Requirement: Código y memoria utilizados en clase
La fuente descargada y el main del historial DEBEN compilar con sus dependencias declaradas. El renderizado no debe introducir caracteres ajenos a la fuente. La memoria mostrada DEBE distinguir reserva sin inicializar, datos escritos, aliases y liberación; las identidades son simbólicas, no direcciones reales.
#### Scenario: Copiar el main mostrado
- **GIVEN** un historial válido
- **WHEN** se copia literalmente el texto C renderizado y se compila con las fuentes descargadas
- **THEN** compila y ejecuta las operaciones reales, sin consultas reemplazadas por resultados precalculados.
#### Scenario: Mostrar memoria después de liberar
- **GIVEN** un puntero a una reserva liberada
- **WHEN** se muestra el paso posterior
- **THEN** se identifica como no utilizable y no se lee ni inventa contenido de la reserva.

### Requirement: Capacidad pedagógica hash sin pérdida de historia
El visualizador DEBE limitar las solicitudes nuevas a 128 cubetas, como política educativa y de recursos distinta del contrato del TAD C. Un historial que contenga una capacidad superior debe suspenderse explícitamente antes de reconstruir tablas grandes, sin presentarse como vacío ni modificarse automáticamente.
#### Scenario: Abrir un historial superior al límite
- **GIVEN** un historial con creación de 129 cubetas y operaciones confirmadas
- **WHEN** se abre la página o se intenta una nueva operación
- **THEN** no se reconstruye la tabla, se explica la suspensión, se conservan historia/main exportables y no se escribe la sesión; sólo un restablecimiento confirmado permite borrarlos.
#### Scenario: Solicitar una capacidad excesiva
- **GIVEN** una tabla válida existente
- **WHEN** se solicita capacidad 129
- **THEN** se rechaza antes de C y se preservan estado, historial y traza vigente.

### Requirement: Fallo C distinto de rechazo anterior a C
Una respuesta de error de la aplicación DEBE conservar la traza si se reprodujeron instrucciones C en el intérprete/simulador. El estado de transporte HTTP no determina por sí solo si existe ejecución pedagógica.
#### Scenario: Clave hash ausente
- **GIVEN** una tabla válida y una clave ausente
- **WHEN** la búsqueda devuelve false
- **THEN** se puede recorrer la función C y observar que la salida previa del llamador no se escribió, sin presentarla como valor encontrado.
