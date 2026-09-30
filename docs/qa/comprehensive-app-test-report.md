# Informe de QA integral de la aplicación — v1

Fecha de cierre: 2026-08-23.  
Alcance: módulos secuencial, jerárquico, grafos, hash, ordenamiento y controles transversales.

## Resultado ejecutivo

La campaña cubrió el inventario publicado de **357 opciones**: 45 rutas, 13 estructuras, 110 operaciones, 23 algoritmos, 4 fases de grafo y 162 controles identificables de interfaz. La suite funcional no E2E finalizó con **1145 aprobadas, 28 no seleccionadas y 4 xfail**, sin fallos inesperados.

Los `xfail` representan el mismo hallazgo funcional conocido, `QA-ROUTE-HELP-UNKNOWN`: las rutas de ayuda de estructuras desconocidas ofrecen una página de respaldo con HTTP 200, mientras que las pantallas de estructuras responden 404. No se corrigió, conforme al alcance de validación.

## Evidencia de ejecución

| Área | Evidencia | Resultado |
|---|---|---|
| Inventario | `scripts/build_app_quality_inventory.py --check` | Vigente; 357 opciones con caso, capa y oráculo asignados. |
| Unitarias, integración, propiedades y golden traces | `docs/qa/comprehensive-app-unit-results-v1.xml` | 1145 passed, 28 deselected, 4 xfailed; 222.13 s. |
| Conformidad C17 y eventos QA | `python scripts/check_c_conformance.py --qa-events` | Aprobada localmente. |
| Sanitizers locales | `python scripts/check_c_conformance.py --sanitizers --qa-events` | Bloqueado: MinGW no encuentra `-lasan` ni `-lubsan`. El job Ubuntu de CI ejecuta ASan/UBSan. |
| E2E Chromium | Cinco flujos críticos, uno por familia: secuencial, jerárquica, grafo, hash y ordenamiento. | 5 passed. Incluyen reproducción, práctica, navegación, móvil, comparación y exportación. |
| E2E Firefox | `tests/test_playwright_firefox_smoke.py` | 5 skipped: binario Firefox de Playwright ausente; ver registro de compatibilidad. |
| Rendimiento | `docs/qa/comprehensive-app-replay-performance-v1.json` | p95 de replay de 300 operaciones: 1.157–43.321 ms, dentro de 200 ms. |

No hubo fallos E2E que requirieran capturas. Las trazas de reproducción, frames y estados finales quedan cubiertos por las suites API, golden traces y los flujos Chromium; los artefactos JUnit y de rendimiento son la evidencia reproducible de esta ejecución.

## Cobertura evaluada

- Secuenciales: pila, cola, prioridad, lista enlazada, circular y sublista; bajo flujo normal, vacío, inválido y límites enteros.
- Jerárquicas: ABB, AVL, rojo-negro y heap; recorridos, rotaciones, eliminación, recoloreo, heapify e invariantes.
- Grafos: construcción, representación, BFS, DFS, Dijkstra, Bellman-Ford, Prim, Kruskal, comparación y las cuatro fases didácticas.
- Hash: capacidad fija, colisiones, claves negativas, actualización, búsqueda, eliminación, memoria simulada, vaciado, destrucción y comparación.
- Ordenamiento: once algoritmos, entrada manual/aleatoria, semilla, comparación, reproducción rápida/paso a paso, auxiliares y límites.
- Transversal: rutas, sesión, historial, reset, trazas, consola, código C, accesibilidad base, teclado, reducción de movimiento, seguridad de entrada y rendimiento.

## Hallazgos y backlog

| ID | Resultado | Severidad | Descripción y recomendación |
|---|---|---|---|
| QA-ROUTE-HELP-UNKNOWN | Fallido conocido (`xfail`) | Baja | `/help/<módulo>/unknown` devuelve una vista de respaldo HTTP 200. Alinear la semántica con las rutas visuales: validar el identificador mediante el servicio del módulo y responder 404, o documentar explícitamente el fallback como contrato público. Revisar `app/routes/help_routes.py`. |
| QA-INFRA-FIREFOX | Bloqueo de infraestructura | Baja | No está instalado Firefox en Playwright. Ejecutar `.\\.venv\\Scripts\\playwright.exe install firefox` y repetir el smoke test. |
| QA-INFRA-SANITIZERS-WINDOWS | Bloqueo de infraestructura | Media | El MinGW local carece de las librerías ASan/UBSan. Ejecutar el job Ubuntu de CI, o instalar un toolchain con ambos runtimes antes de declarar validación local de memoria. |

## Gates CI

- Unit/integración: incluye `scripts/build_app_quality_inventory.py --check` para impedir que una opción publicada quede fuera del manifiesto.
- E2E: instala Chromium y Firefox; ejecuta la suite E2E principal y el smoke de Firefox.
- C: mantiene jobs separados de C17 y sanitizers en Ubuntu.

## Conclusión

La aplicación supera los gates funcionales locales de la campaña y mantiene la fidelidad de estado/traza evaluada en las pruebas automatizadas. Quedan tres acciones de seguimiento: resolver o formalizar el fallback de ayuda desconocida, instalar Firefox para cobertura local y disponer de un runtime ASan/UBSan local; estas dos últimas no son defectos de producto.
