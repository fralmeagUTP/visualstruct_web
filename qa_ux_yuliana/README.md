# Corrección UX local de VisualStruct

Base: 95a46371529677a84fa4c09d5a6f2a747b62326d. Trabajo en copia aislada, sin publicación, sin modificar backend ni fuentes C/H. Las pruebas no certifican producción.

## Comprobaciones reproducibles

Desde la raíz del proyecto, con Python y las dependencias de requirements-test.txt:

```sh
python -m pytest -q tests -m "not e2e"
node --test qa/test_ux_sequential_prediction.js
node tests/qa/ux_hier_unit.cjs
python -m pytest -q tests/test_ux_sorting.py
python scripts/build_app_quality_inventory.py --check
```

La selección explícita `tests` importa: `pytest` sin ruta recoge también carpetas históricas de QA. Algunas dependen de fixtures externos no incluidos o de contratos C anteriores. Sus errores no se eliminan ni se presentan como éxito.

## Integración DOM sin navegador

```sh
npm install --prefix /tmp/visualstruct-ux-dom --cache /tmp/visualstruct-ux-npmcache jsdom@26.1.0
python qa_ux_yuliana/capture_dom_fixtures.py /tmp/visualstruct-ux-fixtures
JSDOM_MODULE=/tmp/visualstruct-ux-dom/node_modules/jsdom node qa_ux_yuliana/test_shared_dom.cjs /tmp/visualstruct-ux-fixtures
```

El generador usa sesiones temporales de Flask, no un servidor. Las 13 páginas inicializan sus scripts reales. Se comprueban errores JS, alternancia reiterada del modo técnico, marcadores de funciones y orden DOM de controles Pila. Los lotes Pila/Cola usan respuestas obtenidas del backend real por test_client y un transporte simulado: selección individual conservada, campo nuevo vacío, tres llamadas y ninguna inserción por doble clic tardío.

JSDOM no calcula disposición visual real, píxeles, tamaño de pantalla, accesibilidad completa ni descargas JPEG. No equivale a Playwright ni a una prueba de navegador.

## Evidencia separada

- sequential-review.md, hierarchical-review.md y sorting-review.md: revisión focal con alcance y límites.
- shared-dom.log: integración DOM final.
- avl-step1-isolated.svg y .png: dibujo aislado del caso AVL auditado, rasterizado con Inkscape. No es captura de la aplicación.
- pytest-tests-only.log: ejecución amplia; consultar el resultado final, no inferir éxito por puntos parciales.
- node/: pruebas Node y reproducciones de fallos históricos sobre la base.

## Límite de navegador

Antes de esta continuación, Chromium fue rechazado por creación de socket tanto normalmente como con escalación revisada. No se repitió ni se eludió esa operación. El navegador cloud tampoco tenía acceso al localhost de esta copia. Queda pendiente un pase autorizado de escritorio y ancho estrecho, incluyendo scroll, foco, contraste, repetición de controles y descarga JPG. No se declara ese pase aprobado.
