# QA de la vista de clase v1

Esta revisión modifica sólo presentación compartida y adaptadores de interfaz de las cinco familias. No modifica C/H, Python, contratos, algoritmos ni libros. Parte de la entrega `visualstruct-book-convergence-app.zip` cuyo SHA figura en `../baseline.json` del workspace.

## Criterios de cierre
- Requisitos VC01–VC11: visual y código legibles simultáneamente, superior compacto, zoom/pan persistente, memoria opcional accesible y Resultados claramente distribuidos.
- Pruebas de controladores y renderers: estado/fuentes intactos, copia exacta de C, consola snapshot/events/raw sin alteración, exportación completa independiente de zoom y paneles cerrados.
- QA real independiente en la superficie 1165×757 y casos representativos de las cinco familias. El segundo viewport 1366×768 quedó NOT_RUN por protección autorizada de la pantalla activa del usuario. No equivale a repetir todas las operaciones semánticas auditadas en v0.
- Comparación byte a byte de backend y 26 archivos C/H contra el ZIP entregado.
- Extracción fresca del paquete v1 y restauración exacta de v0 mediante rollback.

## Evidencia y límites
Los informes independientes se conservan en carpetas hermanas `qa_independent` y `qa_ui`; la evidencia de cierre por rol se incorpora al change `cloud-classroom-view-v1-20261027`. Los resultados están en LEAD_FINAL_REVIEW.md y las revisiones por rol. El paquete final debe conservar verification.json posterior al sello. No se certifican todos los navegadores, dispositivos, accesibilidad asistida ni acciones de portapapeles que no hayan sido observadas. El coordinador de IA externa permanece fuera de esta revisión.

## Reproducción en extracción fresca
Extraer app y evidencia en el mismo directorio padre: los fixtures auténticos de copia main y stdout viven en `../qa_frontend_main` y `../qa_trazas`. Ejecutar desde la carpeta de app:
```sh
node --test qa_classroom_v1/test_*.js
python qa_classroom_v1/test_raw_main_compile.py
python qa_classroom_v1/test_templates.py
for f in qa_convergence/test_*.js; do node "$f" || exit; done
sh qa_convergence/run_non_graph_node.sh
```
Requiere Python con dependencias de la app, Node y gcc C17 disponibles. Los scripts Python ejecutan comprobaciones directas, no se cuentan como métodos unittest. Las compilaciones generan ejecutables locales de prueba; no se incluyen binarios ELF en el paquete. Los JPG fallidos anteriores se conservan como evidencia del defecto y no como pruebas aprobadas.
