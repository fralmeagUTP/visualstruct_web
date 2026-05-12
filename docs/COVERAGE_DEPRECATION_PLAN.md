# Plan de Mejora: Cobertura y Deprecaciones

Fecha base: **12 de mayo de 2026**

## 1. Objetivo

Mantener y mejorar la calidad tecnica mediante:

- control de deprecaciones,
- cobertura automatizada alta,
- menor riesgo de regresiones en el modo interprete C.

## 2. Estado actual

- Suite: `150 passed, 4 skipped`.
- Cobertura global: `89%`.
- Backend de sesion recomendado: `cachelib` (local) o `redis` (produccion).

## 3. Estado por fases

### Fase A - Deprecaciones de sesion

- Migracion desde backend `filesystem` hacia `cachelib` y `redis`: **completada**.
- Configuracion central en `app/config.py`: **completada**.
- Inicializacion robusta en `app/__init__.py`: **completada**.

### Fase B - Cobertura jerarquica

- Cobertura en adapters y dominio jerarquico: **completada**.
- Regresiones AVL/Rojo-Negro verificadas: **completada**.

### Fase C - Cobertura grafos y adapters

- Mejoras fuertes en dominio de grafos y adapters: **completada**.
- Meta global `>=88%`: **cumplida** (`89%`).

### Fase D - Regresiones modo interprete C

- Coherencia historial -> replay -> estado visual: **cubierta**.
- Render esperado en arboles y panel didactico: **cubierto**.

### Fase E - E2E UI (Playwright)

- Pruebas E2E agregadas: **si**.
- Ejecucion automatica en todos los entornos: **pendiente**.

Pendientes operativos:

1. Instalar Playwright y navegador en CI.
2. Agregar job E2E dedicado para PRs principales.
3. Definir politica de ejecucion (por etiqueta o por rama).

## 4. Criterios de aceptacion vigentes

- `pytest` en verde: **cumplido**.
- Cobertura >=88%: **cumplido**.
- Riesgos principales por deprecaciones de sesion: **mitigados**.
- Regresiones criticas del modo interprete C: **cubiertas**.

## 5. Comandos de verificacion

```powershell
.\.venv\Scripts\python.exe -m pytest -q
.\.venv\Scripts\python.exe -m pytest --cov=app --cov-report=term-missing
```

Comandos opcionales E2E:

```powershell
pip install playwright
python -m playwright install chromium
.\.venv\Scripts\python.exe -m pytest tests\test_ui_playwright_e2e.py -q
```
