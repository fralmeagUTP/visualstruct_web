# Integración de la entrega del 27 de octubre de 2026

La entrega incorpora vista de clase, entrada múltiple, ayuda revisada y desplazamiento del lector C, junto con la convergencia de grafos al libro. Los archivos C/H se copian sin modificaciones desde el paquete entregado.

Se conserva la suite histórica del repositorio, las carpetas QA del paquete y sus documentos OpenSpec. Las asignaciones históricas específicas de la máquina, sesiones y configuración privada permanecen locales.

## Reconciliación de CI

Se conservan los cambios locales previos: Doxygen en E2E, pruebas unitarias y cobertura; cuatro particiones deterministas; diagnósticos sin detalles privados; verificación de la unión completa antes de combinar cobertura; resolución portable de herramientas; y los ajustes de pruebas e inputs publicados asociados. El workflow E2E conserva las particiones de Chromium y Firefox de la entrega. Se añade un job pequeño para las regresiones del paquete.

El inventario generado se actualiza a 308 elementos, incluyendo el control nuevo y la exportación del historial de grafos. Esto acredita actualidad del inventario, no cobertura de todos los elementos.

## Validación finita local

- `python -m pytest -q tests/test_publication_followup_preparation.py qa_convergence/test_book_http.py`: 6 pasadas.
- `node qa_scroll/test_code_scroll.js`: 5 pasadas.
- `python scripts/build_app_quality_inventory.py --check`: pasa tras regeneración.
- Los tres workflows son YAML válidos; sus scripts requeridos existen.
- Sintaxis Python de 261 archivos modificados: válida.
- C/H del paquete: igualdad de bytes antes del commit.
- Escaneo de firmas de credenciales sobre candidatos de publicación: sin hallazgos.

La suite histórica completa y la validación visual no se ejecutaron localmente. Los contratos históricos de grafos pueden requerir conciliación con graph-book/v1; los jobs CI conservados deben mostrar sus resultados reales. Este documento no afirma cobertura universal ni certifica CI remoto.

La integración no activa el coordinador IA ni incorpora despliegue remoto. El contenedor local se verifica por separado.
