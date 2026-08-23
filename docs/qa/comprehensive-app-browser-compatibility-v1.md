# Compatibilidad de navegadores — campaña integral QA v1

Fecha de ejecución: 2026-08-23.

| Navegador | Cobertura | Resultado | Evidencia / acción |
|---|---|---|---|
| Chromium (Playwright) | Reproducción, práctica, niveles, navegación, responsividad y exportación en secuenciales, jerárquicas, grafos, hash y ordenamiento. | Ejecutada mediante `tests/test_ui_playwright_e2e.py`. | La suite constituye la evidencia E2E primaria de esta campaña. |
| Firefox (Playwright) | Carga de las cinco pantallas didácticas y foco por teclado. | Bloqueada por infraestructura: 5 pruebas omitidas. | Falta `C:\\Users\\fralm\\AppData\\Local\\ms-playwright\\firefox-1511\\firefox\\firefox.exe`. Ejecutar `.\\.venv\\Scripts\\playwright.exe install firefox` y repetir `python -m pytest tests/test_playwright_firefox_smoke.py -q`. |

La ausencia del binario Firefox no se clasifica como defecto funcional. La prueba queda automatizada y se ejecutará cuando el navegador esté instalado.
