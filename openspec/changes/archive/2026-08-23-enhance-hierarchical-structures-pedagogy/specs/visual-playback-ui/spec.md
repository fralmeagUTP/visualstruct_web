## ADDED Requirements

### Requirement: Reproductor reversible jerárquico
El reproductor SHALL ofrecer preparar, reproducir, pausar, inicio, anterior, siguiente, final y repetir, con progreso navegable por función, profundidad, fase y concepto.

#### Scenario: retroceder una rotación
- **GIVEN** un frame posterior a una rotación
- **WHEN** el estudiante retrocede
- **THEN** restaura exactamente enlaces, alturas, factores, pila, código, consola y árbol anteriores

### Requirement: Predicción jerárquica opcional
El estudiante SHALL poder predecir rama, caso de eliminación, rotación, recoloreo o intercambio, solicitar pistas y continuar sin responder.

#### Scenario: predecir rotación AVL
- **GIVEN** alturas y ruta suficientes
- **WHEN** el siguiente frame clasifica el desequilibrio
- **THEN** el modo práctica oculta el ajuste hasta responder o continuar y luego explica el caso

### Requirement: Presentación adaptable jerárquica
La interfaz SHALL mantener visual y C simultáneamente visibles en escritorio y pestañas persistentes en móvil sin perder contexto.

#### Scenario: alternar árbol y C en móvil
- **GIVEN** una recursión pausada
- **WHEN** se cambia de pestaña
- **THEN** conserva cursor, frame, pila, nodo activo e invariante

### Requirement: Accesibilidad de árboles y heap
Nodos, rutas, colores, factores, rotaciones e intercambios SHALL comunicarse mediante texto o símbolos además de color y movimiento.

#### Scenario: recoloreo con lector de pantalla
- **WHEN** un nodo cambia de rojo a negro
- **THEN** una región accesible anuncia nodo, color anterior/nuevo, motivo y regla restaurada

### Requirement: Exportación de evidencia jerárquica
El módulo SHALL exportar captura y resumen estructurado con TAD, operación, entrada, cursor, frame, invariante, estado y progreso de sesión.

#### Scenario: exportar una rotación
- **WHEN** se exporta durante una rotación AVL
- **THEN** la evidencia incluye caso, pivote, enlaces antes/después y verificación del balance
