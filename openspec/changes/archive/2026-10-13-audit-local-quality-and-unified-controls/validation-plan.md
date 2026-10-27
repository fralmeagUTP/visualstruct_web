# Plan de aseguramiento de calidad — tras aprobación

No constituye resultado de pruebas. Cobertura por riesgo e inventario real, sin prometer todas las posibles entradas o garantía absoluta.

| Clase | Alcance y evidencia prevista |
|---|---|
| Unidad | Operaciones/validación de dominio, adapters, estado vacío/unitario/duplicados/límites e invariantes; casos esperados calculados independientemente. |
| Integración | Rutas, contratos JSON, sesión, historial/replay, servicios, selección C y descargas efectivas; aislamiento entre usuarios y comparaciones. |
| Funcional/E2E | Cada control y operación inventariada, preparación de datos, ejecución repetida, toggle, anterior/siguiente, ayudas, manual, exportaciones, resets y aprendizaje. |
| Regresión | Casos históricos y commit base; sin quitar assertions, elevar xfail o bajar gates para obtener verde. |
| Conformidad C | Compilación C17 y warnings, oráculos instrumentados, ramas, eventos, punteros/alias, memoria y recursión; sanitizadores y gcov compatibles si disponibles. |
| Descargas/documentación | Respuestas HTTP C/H, hashes y contenido, includes y compilación del conjunto recibido, Doxygen por símbolo, ejemplos y guía coherentes. |
| UI/visual | Capturas y mediciones de menú/global overflow, Pila y resto de estructuras; mismo orden y controles, ningún dato esencial recortado. |
| Accesibilidad | Teclado, foco visible y orden lógico, nombres accesibles, ocultos fuera de tabulación, errores/live regions, contraste, zoom 200% y movimiento reducido. Herramientas automáticas no equivalen a conformidad total WCAG. |
| Responsive | Viewports acordados y contenido máximo representativo; reflujo, campos y visualizaciones accesibles sin scroll indebido del menú. |
| Navegadores | Chromium primero; Firefox/WebKit si instalables/ejecutables; navegador real Desktop-FM manual si es necesario. Registrar versiones y límites, nunca extrapolar Chromium a todos. |
| Seguridad local | Validación de entradas, allowlist de descargas/path traversal, escape de texto/HTML, sesiones y errores; revisión de configuración y dependencias sin ataques a terceros. Auditoría local no es pentest certificado. |
| Rendimiento | Latencia/crecimiento de trazas y replay, estructuras grandes dentro de límites, tamaño de respuesta y memoria; medidas repetibles con tamaño/entorno, sin límites inventados ni carga productiva. |

## Matriz a entregar
Para sección 2 añadir: instrucción/frame, archivo/función/línea C, evento, estado antes/después, condición/rama/iteración/llamada/retorno, memoria/punteros, consola, significado de resaltado, vista individual/enlazada y dirección adelante/atrás. Identificar cada combinación TAD/operación/vista aplicable; justificar no aplicables.
Columnas: ID, módulo/TAD/operación/opción, spec/requisito, clase de prueba, precondición/datos, pasos, esperado, observado, oráculo, evidencia/ruta/hash, revisión/herramientas, estado, hallazgo y verificación final. Cada opción inventariada tiene al menos una fila; normales/límites/inválidos según dominio y combinaciones justificadas por riesgo. Las pruebas parametrizadas no se cuentan como cobertura funcional si no prueban el comportamiento correspondiente.

## Cierre
Informe con resultados por clase, cobertura técnica comparada, cobertura de opciones, hallazgos y bloqueos. Nuevos defectos graves o ampliaciones ambiguas se presentan para decisión. Suite y controles aplicables se ejecutan sobre la revisión final después de cambios autorizados. No despliegue, merge ni modificación del checkout anterior.
