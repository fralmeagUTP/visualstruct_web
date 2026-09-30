# Entorno reproducible para la campaña integral de QA

## Base verificada

- Sistema operativo: Windows con PowerShell.
- Python: el intérprete del entorno virtual `.venv`.
- Servidor local: `http://127.0.0.1:5050` mediante `start_local.bat` o `start_local.ps1`.
- Navegadores de campaña: Chromium y Firefox a través de Playwright.
- Fuente didáctica: `docs/tads_C/`; compilación C17 con el compilador configurado por `scripts/check_c_conformance.py`.

## Preparación

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\playwright.exe install chromium firefox
```

## Comandos de control

```powershell
.\.venv\Scripts\python.exe scripts\build_app_quality_inventory.py
.\.venv\Scripts\python.exe scripts\build_app_quality_inventory.py --check
.\.venv\Scripts\python.exe -m pytest tests\test_app_quality_inventory.py -q
.\.venv\Scripts\python.exe -m pytest -q
```

Las pruebas E2E, sanitizers o navegadores faltantes se registran como bloqueos de infraestructura, con el comando de preparación correspondiente; no se clasifican como defectos funcionales de la aplicación.

## Evidencia y repetibilidad

- El manifiesto `docs/qa/app-coverage-manifest-v1.json` se regenera antes de ejecutar la campaña y debe permanecer sin cambios al usar `--check`.
- Las pruebas aleatorias deben declarar y conservar su semilla en el caso y reporte.
- Cada fallo incluye navegador, sistema, versión de Python, commit evaluado, datos de entrada, evidencia y fecha.
