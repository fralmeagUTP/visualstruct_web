# Informe de cierre pedagógico del módulo secuencial

## Antes y después

Antes, la pantalla mostraba el estado global y el código, pero no separaba niveles, memoria, variables, condiciones ni comparación conceptual. Los controles principales no cubrían navegación completa y la ayuda no ofrecía una estrategia docente uniforme.

Después, una única traza canónica alimenta tres niveles de explicación, visualización específica por TAD, memoria y punteros, predicciones, práctica, navegación completa, comparación aislada, ayuda estructurada y exportación de evidencia.

## Criterios de aceptación

- El estado visual procede del frame backend y coincide al avanzar, retroceder y ejecutar rápido.
- La cola de prioridad conserva visualmente llegada y señala por separado selección y empate.
- Las comparaciones clonan una secuencia base y no comparten estado mutable.
- Los controles tienen nombres accesibles, foco visible y equivalentes de teclado.
- El progreso conceptual vive únicamente en `sessionStorage`.

## Atajos

- `Alt+→` siguiente; `Alt+←` anterior; `Alt+Home` inicio; `Alt+End` final.
- `Alt+P` pausa; `Alt+R` repetir.

## Evidencia

- Contratos y regresión Python: **828 aprobadas**, 20 excluidas por marcador en la corrida de cobertura.
- Rendimiento: **2 aprobadas**.
- Playwright: **18 aprobadas**, incluyendo reproducción, práctica, comparación, teclado y móvil.
- Matriz pedagógica de cierre: **21 aprobadas**, cubriendo todos los TAD y operaciones registradas.
- Cobertura: compuerta global **≥83%** y cuatro componentes críticos **≥85%**, aprobadas.
- C17: compilación con `-Wall -Wextra -Wpedantic -Werror`, aprobada.
- Memoria C: script oficial `check_c_sanitizers_linux.sh` aprobado con **AddressSanitizer** y **UndefinedBehaviorSanitizer** en `gcc:14`.
- OpenSpec: validación estricta aprobada.

## Auditoría de accesibilidad y usabilidad

- Todos los controles nuevos usan botones, `label` o nombres `aria-label` nativos.
- El foco de teclado tiene contorno visible de 3 px y no depende solo del color.
- Los estados combinan texto y símbolos (`TOP`, `FRONT`, `BACK`, `✓`, `NULL`, `free`).
- `prefers-reduced-motion` elimina animaciones y desplazamiento suave.
- A 390 px, comparación y panel principal se reducen a una columna sin perder controles.
- El recorrido probado permite preparar, predecir, pedir pista, continuar, comparar y exportar sin ratón.
