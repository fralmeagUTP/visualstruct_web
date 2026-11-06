# QA de comparaciones completas

## Producto cambiado

- app/services/hierarchical_structure_service.py
- app/routes/hierarchical_routes.py
- templates/hierarchical/structure.html
- static/js/hierarchical.js (solo controlador del panel Comparar)

## Comprobaciones reproducibles

Con el Python existente que incluye las dependencias Flask/pytest:

    python -m pytest tests/test_hierarchical_all_comparisons.py tests/test_hierarchical_pedagogy_closure.py -q
    node --check static/js/hierarchical.js
    node qa_all_comparisons/controller_check.cjs

El script browser_check.cjs utiliza Playwright para Node, Chromium existente y un servidor Flask de prueba efímero con sesión independiente. Variables opcionales: VISUALSTRUCT_PYTHON, PLAYWRIGHT_MODULE y CHROMIUM_EXECUTABLE. La ejecución local en este entorno quedó bloqueada al arrancar Chromium por restricción de socket; el script no se presenta como prueba pasada.

## Revisión visual en navegador habilitado

1. Abrir cada una de /hierarchical/abb, /avl, /red_black y /binary_heap. Abrir Comprender → Comparar con teclado. El selector debe tener 12 parejas, 4 opciones contra todas y recorridos. La pareja inicial de cada página empieza por esa estructura.
2. Ejecutar las tres parejas de cada grupo con 9,3,7. Deben verse exactamente las dos estructuras escogidas, en ese orden; Siguiente y Anterior restauran el mismo estado, sin nuevos POST ni cambios en la operación principal.
3. Ejecutar abb-all, avl-all, red-black-all y heap-all. Deben aparecer cuatro tarjetas distintas con la base primero, todas en el mismo paso/valor insertado. Cada tarjeta tiene forma, altura, tamaño, recorrido/arreglo e invariante. Verificar el tamaño y el diseño en escritorio y móvil (390 px).
4. Probar recorridos (tres recorridos, controles de pasos deshabilitados), un valor (sin siguiente), duplicados (error y sin resultado viejo), cambio de selección/entrada (limpia resultados), y cerrar/abrir panel (conserva comparación).
5. Verificar que no reaparece slider ni se modifica la traza o el historial principal. Probar doble clic mientras espera y cambio de selección durante una respuesta retardada si el navegador permite instrumentarlo.

## Integración

Aplicar implementation.patch a una copia basada en los hashes del manifest. No sobrescribir todo hierarchical.js si otra subtarea lo modificó: el parche afecta solo el bloque Comparar. El índice de continuidad no se incluye porque canonical_project debe corresponder a la copia de integración; integrar el binding nuevo de manifest.json sin perder asignaciones existentes. La evidencia técnica no sustituye QA visual ni autoriza publicar.
