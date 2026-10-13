## ADDED Requirements

### Requirement: Hash H1 creation and insertion statement fidelity
La traza MUST seguir th_inicializar/th_insertar/th_indice conservando enteros/capacidad fija, memoria indeterminada, parámetros/variables/pila y solo ramas ejecutadas. Recreación MUST distinguir cleanup del caller del kernel.

#### Scenario: Successful create with capacity3
- GIVEN instancia anterior de capacidad17
- WHEN se recrea con capacidad3
- THEN el caller libera la instancia previa y el kernel inicializa3 celdas sin ejecutar la rama de error de reserva ni conservar capacidad pedagógica17.

#### Scenario: Collision/update/failure
- GIVEN tabla de capacidad3 con colisiones
- WHEN se inserta, actualiza o simula mallocNULL de nodo
- THEN los campos se inicializan antes de publicar, cantidad++ se observa después; actualización no reserva; fallo conserva contenido; carga mayor que1 no cambia capacidad.

### Requirement: Hash execution replay and checked caller
La UI MUST conservar una traza para navegar/reabrir/recargar sin redispatch y descargar caller C17 con resultados reales y cleanup de éxito/error desde historial mutante confirmado.

#### Scenario: Repeated identical confirmed insertions
- GIVEN dos inserciones iguales consecutivas
- WHEN se recarga o descarga main.c
- THEN ambas llamadas permanecen; navegación/mode/reload no envía otra operación; caller verifica retorno y libera sus objetos incluso si una reserva real falla.
